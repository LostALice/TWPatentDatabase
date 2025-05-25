# Code by AkinoAlice@TyrantRey

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from Backend.application.dependency.dependency import (
    require_user,
)
from Backend.utility.handler.database.history import HistoryOperation
from Backend.utility.handler.database.result import ResultOperation
from Backend.utility.handler.llm.llm import LLMResponser
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.dependency.dependency import AccessToken

history_database_client = HistoryOperation()

# router = APIRouter(prefix="/response", dependencies=[Depends(require_user)])
router = APIRouter(prefix="/response", dependencies=[Depends(require_user)])
logger = Logger().get_logger()
llm_client = LLMResponser()
result_database_client = ResultOperation()


@router.get("/search")
async def llm_response(query: str, access_token: Annotated[AccessToken, Depends(require_user)]) -> str:
    response, token_count = llm_client.search_response(query=query)
    logger.info(response)
    logger.info(token_count)

    history_database_client.insert_response_history(
        user_id=int(access_token.sub), query=query, response=response, token=token_count
    )

    return response


@router.get("/summary")
async def llm_summary(patent_id: int, access_token: Annotated[AccessToken, Depends(require_user)]) -> str:
    patent_info = result_database_client.search_patent_by_id(patent_id=patent_id)

    if not patent_info:
        raise HTTPException(404, f"Patent id not found: {patent_id}")

    patent_text_path = patent_info.PatentFilePath.replace("patent", "pdf_output").replace("pdf", "txt")

    with Path.open(Path(patent_text_path), "r", encoding="utf-8") as f:
        patent_text = f.read()

    response, token_count = llm_client.summary_response(query=patent_text)
    logger.info(response)
    logger.info(token_count)
    history_database_client.insert_response_history(
        user_id=int(access_token.sub), query=patent_text[:30], response=response, token=token_count
    )
    return response

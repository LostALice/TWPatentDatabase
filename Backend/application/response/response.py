# Code by AkinoAlice@TyrantRey

from typing import Annotated

from fastapi import APIRouter, Depends

from Backend.application.dependency.dependency import (
    require_user,
)
from Backend.utility.handler.database.history import HistoryOperation
from Backend.utility.handler.llm.llm import LLMResponser
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.dependency.dependency import AccessToken

history_database_client = HistoryOperation()

# router = APIRouter(prefix="/response", dependencies=[Depends(require_user)])
router = APIRouter(prefix="/response", dependencies=[Depends(require_user)])
logger = Logger().get_logger()
llm_client = LLMResponser()


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
async def llm_summary(query: str, access_token: Annotated[AccessToken, Depends(require_user)]) -> str:
    response, token_count = llm_client.summary_response(query=query)
    logger.info(response)
    logger.info(token_count)
    history_database_client.insert_response_history(
        user_id=int(access_token.sub), query=query, response=response, token=token_count
    )
    return response

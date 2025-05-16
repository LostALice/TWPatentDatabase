# Code by AkinoAlice@TyrantRey

from fastapi import APIRouter, Depends

from Backend.application.dependency.dependency import (
    require_user,
)
from Backend.utility.handler.llm.llm import LLMResponser
from Backend.utility.handler.log_handler import Logger

# router = APIRouter(prefix="/response", dependencies=[Depends(require_user)])
router = APIRouter(prefix="/response")
logger = Logger().get_logger()
llm_client = LLMResponser()


@router.get("/search")
async def llm_response(query: str) -> str:
    response, token_count = llm_client.search_response(query=query)
    logger.info(response)
    logger.info(token_count)

    return response


@router.get("/summary")
async def llm_summary(query: str) -> str:
    response, token_count = llm_client.summary_response(query=query)
    logger.info(response)
    logger.info(token_count)

    return response

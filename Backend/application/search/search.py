# Code by AkinoAlice@TyrantRey

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from Backend.application.dependency.dependency import (
    require_user,
)
from Backend.utility.handler.database.search import SearchEngineOperation
from Backend.utility.model.application.search import SearchResult

router = APIRouter(prefix="/search", dependencies=[Depends(require_user)])

engine = SearchEngineOperation()


@router.post("/")
async def search(search_keywords: str) -> SearchResult:
    search_result = engine.full_text_search(search_keywords)

    return SearchResult(
        patents=search_result,
        search_time=datetime.now(tz=timezone.utc),
    )

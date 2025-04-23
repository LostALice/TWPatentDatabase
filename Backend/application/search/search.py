# Code by AkinoAlice@TyrantRey

from fastapi import APIRouter, Depends

from Backend.application.dependency.dependency import (
    require_admin,
    require_root,
    require_user,
)
from Backend.utility.handler.database.search import SearchEngineOperation
from Backend.utility.model.application.search import SearchResult

router = APIRouter(dependencies=[Depends(require_user)])

engine = SearchEngineOperation()


@router.post("/search/")
async def search(search_keywords: str) -> list[SearchResult]:
    engine.search(search_keywords)
    return 1

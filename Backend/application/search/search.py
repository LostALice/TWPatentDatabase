# Code by AkinoAlice@TyrantRey

from fastapi import APIRouter

from Backend.utility.handler.database.search import SearchEngineOperation

router = APIRouter()

engine = SearchEngineOperation()

@router.post("/search/")
async def search(search_args: str) -> int:
    engine.search(search_args)
    return 1

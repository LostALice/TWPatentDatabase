# Code by AkinoAlice@TyrantRey

from Backend.utility.handler.database.search import SearchEngineOperation
from fastapi import APIRouter

router = APIRouter()

engine = SearchEngineOperation()

@router.post("/search/")
async def search(search_args: str) -> int:
    engine.search(search_args)
    return 1

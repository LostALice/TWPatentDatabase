# Code by AkinoAlice@TyrantRey

from fastapi import APIRouter

router = APIRouter()


@router.get("/search/")
async def search():
    return "search"

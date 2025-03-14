# Code by AkinoAlice@TyrantRey

from fastapi import APIRouter

router = APIRouter()


@router.get("/authorization/")
async def search():
    return "authorization"

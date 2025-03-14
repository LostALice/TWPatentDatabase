# Code by AkinoAlice@TyrantRey

from fastapi import APIRouter

router = APIRouter()


@router.get("/result/")
async def result():
    return "result"

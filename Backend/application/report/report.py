# Code by AkinoAlice@TyrantRey

from fastapi import APIRouter

router = APIRouter()


@router.get("/report/")
async def report():
    return "report"

# Code by AkinoAlice@TyrantRey

from fastapi import APIRouter

router = APIRouter(prefix="/report")


@router.get("/report/")
async def report():
    return "report"

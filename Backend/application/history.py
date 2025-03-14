# Code by AkinoAlice@TyrantRey

from fastapi import APIRouter

router = APIRouter()


@router.get("/history/")
async def history():
    """Get recent history"""
    return "history"

# Code by AkinoAlice@TyrantRey

from fastapi import APIRouter, Depends

from Backend.application.dependency.dependency import (
    require_admin,
    require_root,
    require_user,
)
from Backend.utility.model.application.history import HistoryRecord

router = APIRouter(dependencies=[Depends(require_user)])


@router.get("/history/")
async def history(user_id: int) -> list[HistoryRecord]:
    """Get recent history"""
    return "history"

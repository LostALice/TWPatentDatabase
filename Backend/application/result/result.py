# Code by AkinoAlice@TyrantRey

from fastapi import APIRouter, Depends

from Backend.application.dependency.dependency import (
    require_admin,
    require_root,
    require_user,
)

router = APIRouter(dependencies=[Depends(require_user)])


@router.get("/result/")
async def result():
    return "result"

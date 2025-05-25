# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from fastapi import APIRouter, Depends

from Backend.application.dependency.dependency import require_user
from Backend.utility.handler.database.result import ResultOperation
from Backend.utility.model.handler.scraper import PatentInfoModel

router = APIRouter(prefix="/report", dependencies=[Depends(require_user)])
result_database_client = ResultOperation()


@router.get("/info/")
async def get_patent_info(patent_id: int) -> PatentInfoModel | None:
    return result_database_client.search_patent_by_id(patent_id=patent_id) or None

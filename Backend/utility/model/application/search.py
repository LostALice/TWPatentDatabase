# Code by AkinoAlice@TyrantRey

from datetime import datetime

from pydantic import BaseModel

from Backend.utility.model.handler.scraper import PatentInfoModel


class SearchResult(BaseModel):
    patents: list[PatentInfoModel]
    search_time: datetime

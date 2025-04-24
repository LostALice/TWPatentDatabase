# Code by AkinoAlice@TyrantRey

from datetime import datetime

from pydantic import BaseModel

from Backend.utility.model.handler.scraper import PatentInfo


class SearchResult(BaseModel):
    patents: list[PatentInfo]
    search_time: datetime

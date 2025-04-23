# Code by AkinoAlice@TyrantRey

import datetime

from pydantic import BaseModel

from Backend.utility.model.handler.scraper import PatentInfo


class SearchResult(BaseModel):
    patent: PatentInfo
    search_time: datetime.datetime

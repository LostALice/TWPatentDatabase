# Code by AkinoAlice@TyrantRey

from Backend.utility.model.handler.scraper import PatentInfo

from .database import Database


class ScraperOperation(Database):
    def __init__(self):
        super().__init__()

    def insert_patent(self, patent: PatentInfo) -> None: ...

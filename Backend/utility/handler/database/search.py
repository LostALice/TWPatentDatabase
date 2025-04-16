# Code by AkinoAlice@TyrantRey
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import to_tsquery, to_tsvector

from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.handler.database.scheme import PatentScheme

from .database import DATABASE_INSTANCE


class SearchEngineOperation:
    def __init__(self) -> None:
        self.logger = Logger().get_logger()
    def search(self, search_keywords: list[str] | str) -> None:
        self.logger.info(search_keywords)

        # search_col = f"{PatentScheme.id} {PatentScheme.application_date} {PatentScheme.publication_date} {PatentScheme.application_number} {PatentScheme.publication_number} {PatentScheme.applicant} {PatentScheme.inventor} {PatentScheme.attorney} {PatentScheme.priority} {PatentScheme.gazette_ipc} {PatentScheme.ipc} {PatentScheme.gazette_volume} {PatentScheme.kind_codes}"

        # operation = select(PatentScheme).filter(to_tsvector("english", search_col).match(search_keywords))

        # result = DATABASE_INSTANCE.run_query(operation)

        # self.logger.info(result)

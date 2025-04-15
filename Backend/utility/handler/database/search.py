# Code by AkinoAlice@TyrantRey
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import to_tsquery, to_tsvector

from Backend.utility.model.handler.database.scheme import PatentScheme

from .database import Database


class SearchEngineOperation(Database):
    def __init__(self) -> None:
        super().__init__()

    def search(self, search_keywords: list[str] | str) -> None:
        self.logger.info(search_keywords)

        search_col = f"{PatentScheme.id} {PatentScheme.application_date} {PatentScheme.publication_date} {PatentScheme.application_number} {PatentScheme.publication_number} {PatentScheme.applicant} {PatentScheme.inventor} {PatentScheme.attorney} {PatentScheme.priority} {PatentScheme.gazette_ipc} {PatentScheme.ipc} {PatentScheme.gazette_volume} {PatentScheme.kind_codes}"

        operation = select(PatentScheme).filter(
            to_tsvector(
                "english",
                search_col
            ).match(search_keywords)
        )

        result = self.run_query(operation)

        self.logger.info(result)
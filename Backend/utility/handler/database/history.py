# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from sqlalchemy import select

from Backend.utility.handler.database.database import DatabaseConnection
from Backend.utility.model.application.history import LoginHistoryRecord, SearchHistoryRecord
from Backend.utility.model.handler.database.scheme import HistoryScheme, LoginScheme


class HistoryOperation:
    def __init__(self) -> None:
        self.database = DatabaseConnection

    def fetch_search_history(self, user_id: int) -> list[SearchHistoryRecord]:
        operation = select(HistoryScheme.user_id, HistoryScheme.patent_id, HistoryScheme.search_time).where(
            HistoryScheme.user_id == user_id
        )

        result = self.database.run_query(operation)

        if isinstance(result, bool) or result == []:
            return []

        return [
            SearchHistoryRecord(
                user_id=r["HistoryScheme"].user_id,
                patent_id=r["HistoryScheme"].patent_id,
                search_time=r["HistoryScheme"].search_time,
            )
            for r in result
        ]

    def fetch_last_login(self, user_id: int) -> LoginHistoryRecord | None:
        operation = select(LoginScheme.user_id, LoginScheme.access_token_created_at).where(
            LoginScheme.user_id == user_id
        )

        result = self.database.run_query(operation)

        if isinstance(result, bool) or result == []:
            return None

        return LoginHistoryRecord(
            user_id=result[0]["LoginScheme"].user_id,
            last_login_time=result[0]["LoginScheme"].access_token_created_at,
        )

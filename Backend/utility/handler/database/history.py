# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from sqlalchemy import insert, select

from Backend.utility.error.database.database import InsertError
from Backend.utility.handler.database.database import DatabaseConnection
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.history import LoginHistoryRecord, SearchHistoryRecord
from Backend.utility.model.handler.database.scheme import LoginScheme, ResponseHistoryScheme, SearchHistoryScheme


class HistoryOperation:
    def __init__(self) -> None:
        self.database = DatabaseConnection
        self.logger = Logger().get_logger()

    def fetch_search_history(self, user_id: int) -> list[SearchHistoryRecord]:
        operation = select(
            SearchHistoryScheme.user_id, SearchHistoryScheme.patent_id, SearchHistoryScheme.search_time
        ).where(SearchHistoryScheme.user_id == user_id)

        result = self.database.run_query(operation)

        self.logger.debug(result)
        if isinstance(result, bool) or result == []:
            return []
        return [
            SearchHistoryRecord(
                user_id=r["SearchHistoryScheme"].user_id,
                patent_id=r["SearchHistoryScheme"].patent_id,
                search_time=r["SearchHistoryScheme"].search_time,
            )
            for r in result
        ]

    def fetch_last_login(self, user_id: int) -> LoginHistoryRecord | None:
        operation = select(LoginScheme.user_id, LoginScheme.access_token_created_at).where(
            LoginScheme.user_id == user_id
        )

        result = self.database.run_query(operation)
        self.logger.debug(result)

        if isinstance(result, bool) or result == []:
            return None

        return LoginHistoryRecord(
            user_id=result[0]["LoginScheme"].user_id,
            last_login_time=result[0]["LoginScheme"].access_token_created_at,
        )

    def insert_search_history(self, user_id: int, patent_id: int, keyword: str) -> bool:
        operation = insert(SearchHistoryScheme).values(user_id=user_id, patent_id=patent_id, keyword=keyword)

        success = self.database.run_write(operation)

        if not success:
            msg = f"Failed to insert SearchHistory: {user_id}"
            raise InsertError(msg)

        return success

    def insert_response_history(self, user_id: int, query: str, response: str, token: int) -> bool:
        operation = insert(ResponseHistoryScheme).values(user_id=user_id, query=query, response=response, token=token)

        success = self.database.run_write(operation)
        if not success:
            msg = f"Failed to insert ResponseHistory: {user_id}"
            raise InsertError(msg)

        return success

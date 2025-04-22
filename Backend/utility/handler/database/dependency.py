# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from typing import Literal

from sqlalchemy import select

from Backend.utility.error.dependency.dependency import InvalidTokenTypeError
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.handler.database.scheme import LoginScheme

from .database import DatabaseConnection


class DependencyOperation:
    def __init__(self) -> None:
        self.logger = Logger().get_logger()
        self.database = DatabaseConnection

    def verify_token(
        self, user_id: int, token: str, token_type: Literal["access", "refresh"]
    ) -> bool:
        self.logger.debug("%s %s %s", user_id, token, token_type)

        match token_type:
            case "access":
                operation = select(LoginScheme.user_id, LoginScheme.access_token).where(
                    LoginScheme.user_id == user_id,
                    LoginScheme.access_token == token,
                )
            case "refresh":
                operation = select(
                    LoginScheme.user_id, LoginScheme.refresh_token
                ).where(
                    LoginScheme.user_id == user_id,
                    LoginScheme.refresh_token == token,
                )
            case _:
                raise InvalidTokenTypeError(token_type)

        result = self.database.run_query(operation)
        self.logger.debug(result)

        return result != []

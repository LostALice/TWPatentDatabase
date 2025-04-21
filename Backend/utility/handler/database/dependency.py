# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from sqlalchemy import select, update

from Backend.utility.error.dependency.dependency import InvalidTokenTypeError
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.dependency.dependency import AccessToken
from Backend.utility.model.handler.database.scheme import LoginScheme

from .database import DatabaseConnection

if TYPE_CHECKING:
    import datetime


class DependencyOperation:
    def __init__(self) -> None:
        self.logger = Logger().get_logger()
        self.database = DatabaseConnection

    def verify_token(self, user_id: int, token: str, token_type: Literal["access", "refresh"]) -> bool:
        self.logger.debug("%s %s %s", user_id, token, token_type)

        match token_type:
            case "access":
                operation = select(LoginScheme.user_id, LoginScheme.access_token).where(
                    LoginScheme.user_id == user_id,
                    LoginScheme.access_token == token,
                )
            case "refresh":
                operation = select(LoginScheme.user_id, LoginScheme.refresh_token).where(
                    LoginScheme.user_id == user_id,
                    LoginScheme.refresh_token == token,
                )
            case _:
                raise InvalidTokenTypeError(token_type)

        result = self.database.run_query(operation)
        self.logger.debug(result)

        return result != []

    def store_token(
        self,
        user_id: int,
        token: str,
        token_type: Literal["access", "refresh"],
        iat: datetime.datetime,
        exp: datetime.datetime,
    ):
        if token_type == "access":  # noqa: S105
            operation = update(LoginScheme).values(
                user_id=user_id,
                access_token=token,
                refresh_token_created_at=iat,
                access_token_expires_at=exp,
            )
        elif token_type == "refresh":  # noqa: S105
            operation = update(LoginScheme).values(
                user_id=user_id,
                refresh_token=token,
                refresh_token_created_at=iat,
                refresh_token_expires_at=exp,
            )

        else:
            raise InvalidTokenTypeError(token_type)

        result = self.database.run_write(operation)
        self.logger.info(result)
        return result == []

    def logout(self, user_id: int, access_token: str) -> None: ...

    def remove_expired_token(self, user_id: int) -> None: ...

    def update_access_token(self, user_id: int, refresh_token: str) -> None: ...

    def check_role(self, user_id: int, role_id: int) -> bool:
        return True

    def require_role(self, role_name: str, payload: AccessToken) -> AccessToken: ...

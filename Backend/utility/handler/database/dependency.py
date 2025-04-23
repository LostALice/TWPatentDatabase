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
        """
        Verify whether the given token is valid for the specified user.

        This method checks if the provided access or refresh token exists in the database
        and matches the given user ID. It is used to confirm that a token has not been
        revoked or altered.

        Args:
            user_id (int): The ID of the user to verify the token against.
            token (str): The JWT token string to verify.
            token_type (Literal["access", "refresh"]): The type of token being verified.

        Returns:
            bool: True if the token is valid and matches the database record, False otherwise.

        Raises:
            InvalidTokenTypeError: If the token_type is not "access" or "refresh".

        """
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

# Code by AkinoAlice@TyrantRey

from __future__ import annotations

import os
import re
from datetime import timedelta

import jwt
from sqlalchemy import select

from Backend.utility.error.dependency.dependency import (
    InvalidJWTExpireTimeFormatError,
    InvalidUnsupportedJWTExpireTimeError,
)
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.dependency.dependency import JWTPayload
from Backend.utility.model.handler.database.scheme import UserScheme

from .database import DatabaseConnection


class DependencyOperation:
    def __init__(self) -> None:
        self.logger = Logger().get_logger()
        self.database = DatabaseConnection

    def verify_access_token(self, user_id: int, access_token: str) -> bool:
        operation = select()
        return True

    def login(self, user_id: int, hashed_password: str) -> bool:
        operation = select(UserScheme).where(
            UserScheme.user_id == user_id, UserScheme.hashed_password == hashed_password
        )
        return self.database.run_query(operation)


    def logout(self, user_id: int, access_token: str) -> None: ...

    def remove_expired_token(self, user_id: int) -> None: ...

    def update_access_token(self, user_id: int, refresh_token: str) -> None: ...

    def check_role(self, user_id: int, role_id: int) -> bool:
        return True

    def require_role(self, role_name: str, payload: JWTPayload) -> JWTPayload: ...

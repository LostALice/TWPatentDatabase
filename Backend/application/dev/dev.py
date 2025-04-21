# Code by AkinoAlice@TyrantRey


from __future__ import annotations

from os import getenv

from fastapi import APIRouter
from passlib.context import CryptContext

from Backend.utility.handler.database.authorization import AuthorizationOperation
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.auth.authorization import (
    User,
)

router = APIRouter()

# development
GLOBAL_DEBUG_MODE = getenv("DEBUG")
logger = Logger().get_logger()
if GLOBAL_DEBUG_MODE is None or GLOBAL_DEBUG_MODE == "True":
    from dotenv import load_dotenv

    load_dotenv("./.env")

authorization_client = AuthorizationOperation()


@router.get("/dev/create-default-user/")
async def create_default_user() -> list[User]:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__default_rounds=12)
    hashed_password = pwd_context.hash("example_password")
    return authorization_client.create_default_role_and_user(hashed_password)

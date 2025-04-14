# Code by AkinoAlice@TyrantRey
from __future__ import annotations

import re
from os import getenv

from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext

from Backend.utility.handler.database.authorization import AuthorizationOperation
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.auth.authorization import NewRole, NewUser, Role, User  # noqa: TC001

router = APIRouter()
logger = Logger().get_logger()

if getenv("DEBUG") is None:
    from dotenv import load_dotenv

    load_dotenv("./.env")

database_client = AuthorizationOperation()


@router.post("/login/")
async def search():
    return "login"


@router.post("/new-role/")
async def create_new_role(new_role: NewRole) -> int:
    logger.info(new_role)
    is_invalid_characters = re.search(r"[^a-zA-Z0-9]", new_role.role_name)
    if bool(is_invalid_characters):
        logger.critical("Invalid Role name: %s", new_role.role_name)
        raise HTTPException(status_code=400, detail=f"Invalid Role name, Patten: {is_invalid_characters}")

    # This port finished in database while returning exist role_id
    # role_name_list = [r.role_name for r in database_client.fetch_all_role()]
    # if new_role.role_name in role_name_list:
    #     raise HTTPException(status_code=400, detail="Role name already exist in database")

    return database_client.create_new_role(role_name=new_role.role_name, role_description=new_role.role_description)


@router.get("/get-role/")
async def get_role() -> list[Role]:
    return database_client.fetch_all_role()


@router.get("/get-role/name/{role_name}")
async def get_role_by_name(role_name: str) -> Role:
    role = database_client.fetch_role_by_name(role_name)

    if role is None:
        raise HTTPException(status_code=404, detail="Role Not Found")

    return role


@router.get("/get-role/id/{role_id}")
async def get_role_by_id(role_id: int) -> Role:
    role = database_client.fetch_role_by_id(role_id)

    if role is None:
        raise HTTPException(status_code=404, detail="Role Not Found")

    return role


@router.post("/new-user/")
async def create_new_user(new_user: NewUser) -> dict[str, int]:
    is_invalid_characters = bool(re.search(r"[^a-zA-Z0-9]", new_user.user_name))
    if is_invalid_characters:
        logger.critical("Invalid Username: %s", new_user.user_name)
        raise HTTPException(status_code=400, detail="Invalid Username")

    is_valid_email = re.search(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", new_user.email)
    if not is_valid_email:
        logger.critical("Invalid Email: %s", new_user.email)
        raise HTTPException(status_code=400, detail="Invalid Email")

    # is_valid_bcrypt = bool(re.search(r"^\$2[ayb]\$.{56}$", new_user.hashed_password))
    # if not is_valid_bcrypt:
    #     logger.critical("Invalid Password: %s", new_user.hashed_password)
    #     raise HTTPException(status_code=400, detail="Invalid Password")

    role_name_list = [r.role_name for r in database_client.fetch_all_role()]
    if new_user.role_name not in role_name_list:
        raise HTTPException(status_code=400, detail="Invalid Role name")

    role = database_client.fetch_role_by_name(role_name=new_user.role_name)

    if role is None:
        raise HTTPException(status_code=400, detail="Invalid Role name")

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(new_user.password)

    new_user_id = database_client.create_new_user(
        role_id=role.role_id,
        user_name=new_user.user_name,
        email=new_user.email,
        hashed_password=hashed_password,
    )

    if new_user_id is None:
        raise HTTPException(status_code=500, detail="Database Failed")

    return {"user_id": new_user_id}


@router.get("/get-user/name/{user_name}")
async def get_user_by_name(user_name: str) -> User:
    user = database_client.fetch_user_by_name(user_name)

    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")

    return user


@router.get("/get-user/id/{user_id}")
async def get_user_by_id(user_id: int) -> User:
    user = database_client.fetch_user_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")

    return user


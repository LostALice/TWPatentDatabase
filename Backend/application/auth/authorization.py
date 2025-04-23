# Code by AkinoAlice@TyrantRey

from __future__ import annotations

import re
from os import getenv
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext  # type: ignore[import-untyped]

from Backend.application.dependency.dependency import (
    generate_jwt_token,
    generate_refresh_token,
    get_environment_variable,
    parse_duration,
    require_root,
    verify_refresh_token,
)
from Backend.utility.handler.database.authorization import AuthorizationOperation
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.auth.authorization import (
    LoginCertificate,
    NewRole,
    NewUser,
    Role,
    User,
    UserLoginCredential,
)
from Backend.utility.model.application.dependency.dependency import AccessToken

router = APIRouter()
logger = Logger().get_logger()

# development
GLOBAL_DEBUG_MODE = getenv("DEBUG")

if GLOBAL_DEBUG_MODE is None or GLOBAL_DEBUG_MODE == "True":
    from dotenv import load_dotenv

    load_dotenv("./.env")

database_client = AuthorizationOperation()


@router.post("/login/")
async def login(login_cred: UserLoginCredential) -> LoginCertificate:
    user = database_client.fetch_user_by_name(login_cred.user_name)
    if user is None:
        raise HTTPException(401, "Invalid Username or password")

    stored_password = database_client.fetch_user_hashed_password(user_id=user.user_id)

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    is_password_match = pwd_context.verify(login_cred.hashed_password, stored_password)
    logger.info(is_password_match)

    if not is_password_match:
        raise HTTPException(401, "Invalid Username or password")

    login_certificate = generate_jwt_token(user)

    access_token_expire_time = get_environment_variable("JWT_ACCESS_TOKEN_EXPIRE_TIME", str)[
        "JWT_ACCESS_TOKEN_EXPIRE_TIME"
    ]
    refresh_token_expire_time = get_environment_variable("JWT_REFRESH_TOKEN_EXPIRE_TIME", str)[
        "JWT_REFRESH_TOKEN_EXPIRE_TIME"
    ]

    access_token_expire_time = parse_duration(access_token_expire_time)
    refresh_token_expire_time = parse_duration(refresh_token_expire_time)

    database_client.login(
        user_id=login_certificate.user_id,
        access_token=login_certificate.access_token,
        refresh_token=login_certificate.refresh_token,
        access_token_expires_ttl=access_token_expire_time,
        refresh_token_expires_ttl=refresh_token_expire_time,
    )

    return login_certificate


@router.post("/new-role/", response_model=int)
async def create_new_role(new_role: NewRole) -> Role:
    """
    Creates a new role after validating the role name for invalid characters and duplicates.

    - Rejects names containing characters other than a-z, A-Z, or 0-9.
    - Rejects duplicates if the role name already exists in the database.
    - If valid, inserts the role and returns its ID.

    Args:
        new_role (NewRole): The role name and optional description.

    Returns:
        Role: The role scheme.

    """
    new_role.role_name = new_role.role_name.lower()
    logger.info(new_role)

    valid_role_pattern = re.compile(r"^[a-zA-Z0-9]+$")

    if not valid_role_pattern.match(new_role.role_name):
        logger.critical("Invalid Role name: %s", new_role.role_name)
        raise HTTPException(
            status_code=400,
            detail="Invalid role name: only alphanumeric characters are allowed",
        )

    # Check for duplicates
    existing_roles = [r.role_name for r in database_client.fetch_all_role()]
    if new_role.role_name in existing_roles:
        raise HTTPException(status_code=400, detail="Role name already exists")

    # Create the new role and return its ID
    role_id = database_client.create_new_role(role_name=new_role.role_name, role_description=new_role.role_description)

    role = database_client.fetch_role_by_id(role_id)

    if role:
        return role

    raise HTTPException(status_code=500, detail="Internal Server")


@router.get("/get-role/")
async def get_role() -> list[Role]:
    """
    Retrieves all roles from the database.

    Returns:
        list[Role]: A list of Role objects representing all roles in the system.

    """
    return database_client.fetch_all_role()


@router.get("/get-role/name/{role_name}")
async def get_role_by_name(role_name: str) -> Role:
    """
    Retrieves a role by its name.

    Args:
        role_name (str): The name of the role to look up.

    Returns:
        Role: The matching Role object.

    Raises:
        HTTPException: If the role does not exist (404).

    """
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
async def create_new_user(new_user: NewUser) -> User:
    """
    Creates a new user after validating input data.

    - Validates username (alphanumeric only)
    - Validates email format
    - Checks role existence
    - Hashes password using bcrypt
    - Inserts the user and returns the new user ID

    Args:
        new_user (NewUser): The new user's registration data.

    Returns:
        dict[str, int]: A dictionary containing the new user's ID.

    Raises:
        HTTPException: On invalid input or database error.

    """
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
        raise HTTPException(status_code=500, detail="Internal Database Error")

    user = database_client.fetch_user_by_id(new_user_id)

    if user:
        return user

    raise HTTPException(status_code=500, detail="Internal Database Error")


@router.get("/get-user/name/{user_name}")
async def get_user_by_name(user_name: str, payload: Annotated[AccessToken, Depends(require_root)]) -> User:
    """
    Retrieves a user by their username.

    Args:
        user_name (str): The username to look up.
        payload (AccessToken): The JWT payload from the verify_jwt_token dependency.

    Returns:
        User: The matching User object.

    Raises:
        HTTPException: If the user does not exist (404).

    """
    logger.debug(payload)
    user = database_client.fetch_user_by_name(user_name)

    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")

    return user


@router.get("/get-user/id/{user_id}")
async def get_user_by_id(user_id: int) -> User:
    """
    Retrieves a user by their unique user ID.

    Args:
        user_id (int): The ID of the user to retrieve.

    Returns:
        User: The corresponding User object.

    Raises:
        HTTPException: If no user is found with the given ID (404).

    """
    user = database_client.fetch_user_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")

    return user


@router.post("/refresh-token/")
async def refresh_access_token(refresh_token: str) -> str:
    logger.info(refresh_token)
    token = verify_refresh_token(refresh_token=refresh_token)
    user_id = int(token.sub)
    db_refresh_token = database_client.fetch_refresh_token(user_id=user_id)

    logger.info(db_refresh_token)
    if db_refresh_token is None or db_refresh_token != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")

    new_refresh_token = generate_refresh_token(user_id)

    database_client.revoke_access_token(user_id=user_id)
    database_client.update_refresh_token(user_id=user_id, refresh_token=new_refresh_token)

    return new_refresh_token

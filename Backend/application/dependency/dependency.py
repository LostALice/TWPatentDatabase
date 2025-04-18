# Code by AkinoAlice@TyrantRey

import datetime
import os
import re

import jwt
from fastapi import Depends, Header, HTTPException

from Backend.utility.error.common import EnvironmentalVariableNotSetError
from Backend.utility.error.dependency.dependency import (
    InvalidAlgorithmError,
    InvalidJWTExpireTimeFormatError,
    InvalidUnsupportedJWTExpireTimeError,
)
from Backend.utility.handler.database.dependency import DependencyOperation
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.dependency.dependency import JWTPayload

logger = Logger().get_logger()

# development
GLOBAL_DEBUG_MODE = os.getenv("DEBUG")
logger.info("Global Debug Mode: %s", GLOBAL_DEBUG_MODE)

if GLOBAL_DEBUG_MODE is None or GLOBAL_DEBUG_MODE == "True":
    from dotenv import load_dotenv

    load_dotenv("./.env")

database_client = DependencyOperation()


def parse_duration(duration_str: str) -> datetime.timedelta:
    pattern = r"(?P<value>\d+)(?P<unit>[smhdw])"
    match = re.fullmatch(pattern, duration_str.strip())

    if not match:
        msg = "Use formats like 1d, 5h, 30m, etc."
        raise InvalidJWTExpireTimeFormatError(msg)

    value = int(match.group("value"))
    unit = match.group("unit")

    if unit == "s":
        return datetime.timedelta(seconds=value)
    if unit == "m":
        return datetime.timedelta(minutes=value)
    if unit == "h":
        return datetime.timedelta(hours=value)
    if unit == "d":
        return datetime.timedelta(days=value)
    if unit == "w":
        return datetime.timedelta(weeks=value)

    raise InvalidUnsupportedJWTExpireTimeError


def check_jwt_environment_variable() -> bool:
    jwt_secret = str(os.getenv("JWT_SECRET"))
    jwt_algorithm = os.getenv("JWT_ALGORITHM")

    if jwt_secret is None:
        _error = "JWT_SECRET"
        raise EnvironmentalVariableNotSetError(_error)

    if jwt_algorithm is None:
        _error = "JWT_ALGORITHM"
        raise EnvironmentalVariableNotSetError(_error)

    if jwt_algorithm not in [
        "HS256",
        "HS384",
        "HS512",
        "ES256",
        "ES256K",
        "ES384",
        "ES512",
        "RS256",
        "RS384",
        "RS512",
        "PS256",
        "PS384",
        "PS512",
        "EdDSA",
    ]:
        raise InvalidAlgorithmError(jwt_algorithm)

    return True


async def verify_jwt_token(token: str = Header(None)) -> JWTPayload:
    """
    Verify the JWT token and extract the payload.

    Args:
        token (str): The JWT token extracted from the Authorization header.

    Returns:
        JWTPayload: The decoded JWT payload containing user information.

    Raises:
        HTTPException: If the token is invalid, expired, or not found in the database.

    """
    check_jwt_environment_variable()

    try:
        payload = jwt.decode(token, jwt_secret, algorithms=jwt_algorithm)
    except jwt.PyJWTError as e:
        _error = f"JWT verification error: {e}"
        logger.exception(_error)
        raise HTTPException(status_code=401, detail="Invalid authentication token") from e
    except Exception as e:
        _error = f"Unexpected error during token verification: {e}"
        logger.exception(_error)
        raise HTTPException(status_code=500, detail="Internal server error") from e

    # Verify token is in database
    token_valid = database_client.verify_access_token(payload["user_id"], token)
    if not token_valid:
        raise HTTPException(status_code=401, detail="Token not found in database")

    # Check if token is expired
    expire_time = datetime.datetime.fromisoformat(payload["expire_time"])
    if datetime.datetime.now(tz=datetime.UTC) > expire_time:
        # Optionally remove expired token from database
        database_client.remove_expired_token(payload["user_id"])
        raise HTTPException(status_code=401, detail="Token expired")

    return JWTPayload(**payload)


async def require_role(required_roles: list[str], payload: JWTPayload = Depends(verify_jwt_token)) -> JWTPayload:
    """
    Check if the authenticated user has one of the required roles.

    Args:
        required_roles (list[str]): List of roles that are allowed to access the endpoint.
        payload (JWTPayload): The JWT payload from the verify_jwt_token dependency.

    Returns:
        JWTPayload: The original JWT payload if the role check passes.

    Raises:
        HTTPException: If the user's role is not in the required roles list.

    """
    if payload.role_name.lower() not in required_roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return payload


async def require_root(payload: JWTPayload = Depends(verify_jwt_token)) -> JWTPayload:
    """Require root role to access the endpoint"""
    return await require_role(["admin"], payload)


async def require_user(payload: JWTPayload = Depends(verify_jwt_token)) -> JWTPayload:
    """Require user role to access the endpoint"""
    return await require_role(["user", "root", "admin"], payload)

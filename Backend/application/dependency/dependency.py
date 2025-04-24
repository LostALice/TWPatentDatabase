# Code by AkinoAlice@TyrantRey
from __future__ import annotations

import datetime
import json
import re
from os import getenv
from typing import Any

import jwt
from fastapi import Depends, Header, HTTPException
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, PyJWTError

from Backend.utility.error.common import (
    EnvironmentVariableNotSetError,
    InvalidTypingError,
)
from Backend.utility.error.dependency.dependency import (
    InvalidAlgorithmError,
    InvalidJWTExpireTimeFormatError,
    InvalidUnsupportedJWTExpireTimeError,
)
from Backend.utility.handler.database.dependency import DependencyOperation
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.auth.authorization import LoginCertificate, User
from Backend.utility.model.application.dependency.dependency import (
    AccessToken,
    JWTEnvironmentalSetup,
    RefreshToken,
    TokenType,
)

logger = Logger().get_logger()

# development
GLOBAL_DEBUG_MODE = getenv("DEBUG")
logger.info("Global Debug Mode: %s", GLOBAL_DEBUG_MODE)

if GLOBAL_DEBUG_MODE is None or GLOBAL_DEBUG_MODE == "True":
    from dotenv import load_dotenv

    load_dotenv("./.env")

database_client = DependencyOperation()


def parse_duration(duration_str: str) -> datetime.timedelta:
    """
    Parse a duration string into a corresponding `datetime.timedelta` object.

    Args:
        duration_str (str): A string representing the duration (e.g., "1d", "5h", "30m").

    Returns:
        (datetime.timedelta): A timedelta object representing the parsed duration.

    Raises:
        InvalidJWTExpireTimeFormatError: If the input format does not match expected patterns.
        InvalidUnsupportedJWTExpireTimeError: If the duration unit is not supported.

    """
    duration_str = duration_str.lower()
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


def _coerce(raw: str, expected_type: type) -> Any:
    """
    Coerce a string value to the expected type.

    This function handles special cases for boolean and list types, with a general
    fallback for other types using their constructor.

    Args:
        raw: The raw string value to coerce.
        expected_type: The target type to coerce the raw value to.

    Returns:
        The coerced value of the specified type.

    Raises:
        InvalidTypingError: If the raw value cannot be coerced to the expected type.

    """
    if expected_type is bool:
        lowered = raw.lower()
        if lowered in {"1", "true", "yes", "y"}:
            return True
        if lowered in {"0", "false", "no", "n"}:
            return False
        msg = f"Expected boo-ish value, got {raw!r}"
        raise InvalidTypingError(msg)

    if expected_type is list:
        try:
            return json.loads(raw)
        except Exception as exc:
            msg = f"Cannot interpret {raw!r} as list"
            raise InvalidTypingError(msg) from exc

    # Fallback: rely on the constructor
    try:
        return expected_type(raw)
    except Exception as exc:
        msg = f"Cannot coerce {raw!r} to {expected_type.__name__}"
        raise InvalidTypingError(msg) from exc


def get_environment_variable(variable: str, expected_type: type = str) -> dict[str, Any]:
    """
    Check if an environment variable exists and coerce its value to the expected type.

    Args:
        variable: The name of the environment variable to check.
        expected_type: The type to which the environment variable's value should be coerced.

    Returns:
        A dictionary with the environment variable name as key and its coerced value.

    Raises:
        EnvironmentVariableNotSetError: If the specified environment variable is not set.
        InvalidTypingError: If the environment variable's value cannot be coerced to the expected type.

    Examples:
        >>> check_environment_variable("DEBUG", bool)
        {'DEBUG': True}
        >>> check_environment_variable("PORT", int)
        {'PORT': 8080}

    """
    raw = getenv(variable)
    if raw is None:
        raise EnvironmentVariableNotSetError(variable)

    value = _coerce(raw, expected_type)
    return {variable: value}


def get_jwt_environment_variable() -> JWTEnvironmentalSetup:
    """
    Validate and retrieve JWT-related environment variables required for token operations.

    Args:
        None

    Returns:
        (JWTEnvironmentalSetup): An object containing the validated JWT environment configuration.

    Raises:
        EnvironmentVariableNotSetError: If any required JWT environment variable is not set.
        InvalidAlgorithmError: If the JWT algorithm specified is not supported.

    """
    jwt_secret = get_environment_variable("JWT_SECRET")["JWT_SECRET"]
    jwt_algorithm = get_environment_variable("JWT_ALGORITHM")["JWT_ALGORITHM"]
    jwt_access_token_expire_time = get_environment_variable("JWT_ACCESS_TOKEN_EXPIRE_TIME")[
        "JWT_ACCESS_TOKEN_EXPIRE_TIME"
    ]
    jwt_refresh_token_expire_time = get_environment_variable("JWT_REFRESH_TOKEN_EXPIRE_TIME")[
        "JWT_REFRESH_TOKEN_EXPIRE_TIME"
    ]

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

    access_token_expire_time = parse_duration(jwt_access_token_expire_time)
    refresh_token_expire_time = parse_duration(jwt_refresh_token_expire_time)

    return JWTEnvironmentalSetup(
        secret=jwt_secret,
        algorithm=jwt_algorithm,
        access_token_expire_time=access_token_expire_time,
        refresh_token_expire_time=refresh_token_expire_time,
    )


def _check_revocation(payload: dict, token: str, token_type: TokenType) -> None:
    """
    Check if the given token has been revoked for the user.

    This function verifies the token's validity against the database. If the token
    has been revoked (i.e., is no longer valid for the user), it raises an HTTP 401 error.

    Args:
        payload (dict): The decoded JWT payload containing at least the 'sub' (user ID).
        token (str): The JWT token string to verify.
        token_type (TokenType): The type of token being verified (e.g., access or refresh).

    Raises:
        HTTPException: 401 Unauthorized if the token has been revoked or is invalid.

    """
    logger.debug(payload)
    if not database_client.verify_token(user_id=int(payload["sub"]), token=token or "", token_type=token_type):
        raise HTTPException(status_code=401, detail="Token revoked")


async def verify_jwt_token(
    access_token: str = Header(default=None),
    refresh_token: str = Header(default=None),
) -> AccessToken:
    """
    Verify the validity of the provided JWT access token.

    This function checks if the access token is present and valid. If it has
    expired or is otherwise invalid, and a refresh token is provided, the function
    checks if the refresh token is valid and informs the client to refresh the token.

    Args:
        access_token (str): JWT access token, expected in the request headers.
        refresh_token (str): Optional JWT refresh token, also expected in headers.

    Returns:
        AccessToken: The decoded payload of the access token if it is valid.

    Raises:
        HTTPException (401):
            - If the access token is missing.
            - If the access token is invalid or expired and no valid refresh token is provided.
            - If both tokens are invalid or the refresh token is not used properly.
            - If the refresh token is valid, prompts the client to refresh via the designated endpoint.

    Notes:
        - Designed to be used as a dependency in FastAPI routes.
        - Refreshing does not occur automatically; the client must call `/auth/refresh-token`.

    """
    if access_token is None:
        raise HTTPException(status_code=401, detail="Missing access token")

    # Try to decode and verify the access token
    access_payload = verify_access_token(access_token=access_token)

    if isinstance(access_payload, AccessToken):
        return access_payload

    # If access token is invalid/expired, check for refresh token
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Access token expired and no refresh token provided")

    refresh_payload = verify_refresh_token(refresh_token=refresh_token)

    if isinstance(refresh_payload, RefreshToken):
        # Indicate to client to refresh token
        raise HTTPException(
            status_code=401,
            detail="Access token expired. Use /auth/refresh-token to regenerate.",
        )

    raise HTTPException(status_code=401, detail="Invalid token(s)")


def verify_access_token(
    access_token: str = Header(None),
) -> AccessToken:
    """
    Verify the validity of an access token.

    Args:
        access_token (str): JWT access token passed in the request header.

    Returns:
        AccessToken: Decoded JWT payload containing user authentication details.

    Raises:
        HTTPException (401): If the access token is invalid or expired.

    """
    jwt_setup = get_jwt_environment_variable()
    logger.info(jwt_setup)

    try:
        access_payload = jwt.decode(access_token, jwt_setup.secret, algorithms=jwt_setup.algorithm)
        _check_revocation(access_payload, access_token, "access")
        logger.info(access_payload)

    except InvalidSignatureError as e:
        logger.critical("Access token check failed InvalidSignatureError: %s", e)
        logger.info("Checking Refresh Token")
        raise HTTPException(401, "Invalid access token, please refresh access token") from e

    except ExpiredSignatureError as e:
        logger.critical("Access token check failed ExpiredSignatureError: %s", e)
        logger.info("Checking Refresh Token")
        raise HTTPException(401, "Invalid access token, please refresh access token") from e

    except PyJWTError as e:
        logger.warning("Access-token error: %s", e)
        raise HTTPException(401, "Invalid access token, please refresh access token") from e
    else:
        return AccessToken(**access_payload)


def verify_refresh_token(refresh_token: str) -> RefreshToken:
    """
    Verify the validity of a refresh token.

    Args:
        refresh_token (str): JWT refresh token.

    Returns:
        AccessToken: Decoded JWT payload if valid.

    Raises:
        HTTPException (401): If the refresh token is invalid or expired.

    """
    jwt_setup = get_jwt_environment_variable()
    logger.info("Verifying refresh token with algorithm: %s", jwt_setup.algorithm)

    try:
        refresh_payload = jwt.decode(refresh_token, jwt_setup.secret, algorithms=[jwt_setup.algorithm])
        _check_revocation(refresh_payload, refresh_token, "refresh")
        logger.debug("Refresh token valid: %s", refresh_payload)

        return RefreshToken(**refresh_payload)

    except InvalidSignatureError as e:
        logger.critical("Refresh token signature invalid: %s", e)
        raise HTTPException(status_code=401, detail="Invalid refresh token, please re-login") from e

    except ExpiredSignatureError as e:
        logger.warning("Refresh token expired: %s", e)
        raise HTTPException(status_code=401, detail="Refresh token expired, please re-login") from e

    except PyJWTError as e:
        logger.warning("Refresh token error: %s", e)
        raise HTTPException(status_code=401, detail="Invalid refresh token, please re-login") from e


def generate_jwt_token(user: User) -> LoginCertificate:
    access_token = generate_access_token(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email,
        role_name=user.role_name,
    )

    refresh_token = generate_refresh_token(user.user_id)

    return LoginCertificate(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email,
        role_name=user.role_name,
        access_token=access_token,
        refresh_token=refresh_token,
    )


def generate_access_token(user_id: int, user_name: str, email: str, role_name: str) -> str:
    jwt_setup = get_jwt_environment_variable()
    logger.info(jwt_setup)

    issued_at = datetime.datetime.now(tz=datetime.timezone.utc)
    expire = issued_at + jwt_setup.access_token_expire_time

    return jwt.encode(
        payload={
            "sub": str(user_id),  # standard claim for subject NEED TO BE A STRING
            "user_name": user_name,
            "email": email,
            "role_name": role_name,
            "typ": "access",
            "iat": issued_at,
            "exp": expire,
        },
        key=jwt_setup.secret,
        algorithm=jwt_setup.algorithm,
    )


def generate_refresh_token(user_id: int) -> str:
    jwt_setup = get_jwt_environment_variable()
    logger.info(jwt_setup)

    issued_at = datetime.datetime.now(tz=datetime.timezone.utc)
    expires = issued_at + jwt_setup.refresh_token_expire_time

    return jwt.encode(
        payload={
            "sub": str(user_id),  # standard claim for subject NEED TO BE A STRING
            "typ": "refresh",
            "iat": issued_at,
            "exp": expires,
        },
        key=jwt_setup.secret,
        algorithm=jwt_setup.algorithm,
    )


async def require_role(required_roles: list[str], payload: AccessToken = Depends(verify_jwt_token)) -> AccessToken:
    """
    Check if the authenticated user has one of the required roles.

    Args:
        required_roles (list[str]): List of roles that are allowed to access the endpoint.
        payload (AccessToken): The JWT payload from the verify_jwt_token dependency.

    Returns:
        AccessToken: The original JWT payload if the role check passes.

    Raises:
        HTTPException: If the user's role is not in the required roles list.

    """
    if payload.role_name.lower() not in required_roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return payload


async def require_root(payload: AccessToken = Depends(verify_jwt_token)) -> AccessToken:
    """Require root role to access the endpoint"""
    return await require_role(["admin"], payload)


async def require_admin(
    payload: AccessToken = Depends(verify_jwt_token),
) -> AccessToken:
    """Require admin role to access the endpoint"""
    return await require_role(["admin", "root"], payload)


async def require_user(payload: AccessToken = Depends(verify_jwt_token)) -> AccessToken:
    """Require user role to access the endpoint"""
    return await require_role(["user", "root", "admin"], payload)

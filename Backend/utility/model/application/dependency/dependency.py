# Code by AkinoAlice@TyrantRey

import datetime
from typing import Literal

from pydantic import BaseModel

TokenType = Literal["access", "refresh"]


class AccessToken(BaseModel):
    sub: str  # standard claim for subject NEED TO BE A STRING
    user_name: str
    email: str
    role_name: str
    typ: TokenType
    iat: datetime.datetime
    exp: datetime.datetime


class RefreshToken(BaseModel):
    sub: str  # standard claim for subject NEED TO BE A STRING
    typ: TokenType
    iat: datetime.datetime
    exp: datetime.datetime


class JWTEnvironmentalSetup(BaseModel):
    secret: str
    algorithm: str
    access_token_expire_time: datetime.timedelta
    refresh_token_expire_time: datetime.timedelta

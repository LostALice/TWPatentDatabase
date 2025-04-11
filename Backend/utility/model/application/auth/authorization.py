# Code by AkinoAlice@TyrantRey

from pydantic import BaseModel


class NewUser(BaseModel):
    user_name: str
    email: str
    password: str
    role_name: str


class User(BaseModel):
    user_id: int
    user_name: str
    email: str
    role_name: str


class NewRole(BaseModel):
    role_name: str
    role_description: str


class Role(BaseModel):
    role_id: int
    role_name: str
    role_description: str

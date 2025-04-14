# Code by AkinoAlice@TyrantRey


from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    host: str
    username: str
    password: str
    database: str
    port: int = 5432

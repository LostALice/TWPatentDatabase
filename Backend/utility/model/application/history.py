# Code by AkinoAlice@TyrantRey

from datetime import datetime

from pydantic import BaseModel


class Record(BaseModel):
    user_id: int


class SearchHistoryRecord(Record):
    patent_id: int
    search_time: datetime


class LoginHistoryRecord(Record):
    last_login_time: datetime


class ResponseHistoryRecord(Record):
    query: str
    response: str

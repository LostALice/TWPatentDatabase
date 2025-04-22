# Code by AkinoAlice@TyrantRey

from datetime import datetime

from pydantic import BaseModel


class Record(BaseModel):
    user_id: int
    patent_name: str


class HistoryRecord(Record):
    search_time: datetime

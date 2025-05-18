# Code by AkinoAlice@TyrantRey

from datetime import datetime

from pydantic import BaseModel

from Backend.utility.model.handler.scraper import PatentInfoModel


class SearchResult(BaseModel):
    patents: list[PatentInfoModel]
    search_time: datetime


class PDFChunkEmbedding(BaseModel):
    patent_id: int
    page_number: int
    content: str
    embedding: list[float]


class PDFInfo(BaseModel):
    patent_id: int
    patent_file_path: str
    patent_title: str

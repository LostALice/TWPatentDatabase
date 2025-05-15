# Code by AkinoAlice@TyrantRey


from __future__ import annotations

from os import getenv

from fastapi import APIRouter
from passlib.context import CryptContext  # type: ignore[import-untyped]

from Backend.utility.handler.database.authorization import AuthorizationOperation
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.auth.authorization import (
    User,
)

router = APIRouter(prefix="/dev")


# development
GLOBAL_DEBUG_MODE = getenv("DEBUG")
logger = Logger().get_logger()
if GLOBAL_DEBUG_MODE is None or GLOBAL_DEBUG_MODE == "True":
    from dotenv import load_dotenv

    load_dotenv("./.env")

authorization_database_client = AuthorizationOperation()


@router.get("/create-default-user/")
async def create_default_user() -> list[User]:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__default_rounds=12)
    hashed_password = pwd_context.hash("example_password")
    return authorization_database_client.create_default_role_and_user(hashed_password)


# @router.post("/download/")
# async def download_patent(patent_keyword: str = "鞋面") -> bool:
#     scraper = Scraper()
#     scraper.create_scraper()
#     scraper.keyword = patent_keyword
#     # total_patent, total_page = scraper.search(patent_keyword)

#     for page_number in range(1, 2):
#         for url in scraper.get_patent_url(page=page_number):
#             patent_data = scraper.get_patent_information(url)
#             logger.info(patent_data)
#             scraper_database_client.insert_patent(patent=patent_data)
#     scraper.destroy_scraper()
#     return True

# Code by AkinoAlice@TyrantRey

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends

from Backend.application.dependency.dependency import (
    require_user,
)
from Backend.utility.handler.database.history import HistoryOperation
from Backend.utility.handler.database.scraper import ScraperOperation
from Backend.utility.handler.database.search import SearchEngineOperation
from Backend.utility.handler.log_handler import Logger
from Backend.utility.handler.scraper import Scraper
from Backend.utility.model.application.dependency.dependency import AccessToken
from Backend.utility.model.application.search import SearchResult

router = APIRouter(prefix="/search", dependencies=[Depends(require_user)])

engine = SearchEngineOperation()
history_database_client = HistoryOperation()
scraper_database_client = ScraperOperation()
logger = Logger().get_logger()


@router.post("/")
async def search(search_keywords: str, access_token: Annotated[AccessToken, Depends(require_user)]) -> SearchResult:
    """
    Search patents by keyword, record the search history, and return the results.

    This asynchronous endpoint performs a full-text search for patents matching
    the given `search_keywords`. If any patents are found, it logs each search
    in the user's history. Finally, it returns a `SearchResult` containing the
    list of patents and the timestamp of the search.

    Args:
        search_keywords (str): The keyword(s) to search for.
        access_token (AccessToken, via Depends): Authenticated user token.

    Returns:
        SearchResult:
            - patents (List[Patent]): List of matching patents.
            - search_time (datetime): UTC timestamp when the search was executed.

    """
    patents = engine.full_text_search(search_keywords)

    if patents:
        for patent in patents:
            history_database_client.insert_search_history(
                user_id=int(access_token.sub), patent_id=patent.Patent_id, keyword=search_keywords
            )

    return SearchResult(
        patents=patents,
        search_time=datetime.now(tz=timezone.utc),
    )


@router.post("/scraper/")
async def download_patent(patent_keyword: str = "鞋面") -> bool:
    """
    Scrape patent information for a given keyword and store it in the database.

    This asynchronous endpoint initializes the scraper, fetches patent URLs
    for the first page of results matching `patent_keyword`, retrieves detailed
    information for each patent, logs it, and inserts each record into the
    database. Finally, it tears down the scraper instance.

    Args:
        patent_keyword (str): The keyword to search patents for. Defaults to "鞋面".

    Returns:
        bool: True if the scraping process completed successfully.

    """
    scraper = Scraper()
    scraper.create_scraper()
    scraper.keyword = patent_keyword

    for page_number in range(1, 2):
        for url in scraper.get_patent_url(page=page_number):
            patent_data = scraper.get_patent_information(url)
            logger.info(patent_data)
            scraper_database_client.insert_patent(patent=patent_data)
    scraper.destroy_scraper()
    return True

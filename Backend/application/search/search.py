# Code by AkinoAlice@TyrantRey

from __future__ import annotations

import re
from datetime import datetime, timezone
from os import getenv
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends

from Backend.application.dependency.dependency import require_user
from Backend.utility.error.common import EnvironmentVariableNotSetError
from Backend.utility.handler.database.history import HistoryOperation
from Backend.utility.handler.database.scraper import ScraperOperation
from Backend.utility.handler.database.search import SearchEngineOperation
from Backend.utility.handler.embedding import ImageEmbedding
from Backend.utility.handler.llm.llm import LLMResponser
from Backend.utility.handler.log_handler import Logger
from Backend.utility.handler.pdf_extractor import PDFExtractor
from Backend.utility.handler.scraper import Scraper
from Backend.utility.model.application.dependency.dependency import AccessToken
from Backend.utility.model.application.search import PDFChunkEmbedding, PDFInfo, SearchResult
from Backend.utility.model.handler.scraper import PatentInfoModel

router = APIRouter(prefix="/search", dependencies=[Depends(require_user)])
# router = APIRouter(prefix="/search")

logger = Logger().get_logger()
search_database_client = SearchEngineOperation()
history_database_client = HistoryOperation()
scraper_database_client = ScraperOperation()
llm_client = LLMResponser()
pdf_extractor = PDFExtractor()
embedding_model = ImageEmbedding()

POPPLER_PATH = getenv("POPPLER_PATH")


@router.get("/full-text")
async def full_text_search(
    search_keywords: str, access_token: Annotated[AccessToken, Depends(require_user)]
) -> SearchResult:
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
    patents = search_database_client.full_text_search(search_keywords)

    if patents:
        for patent in patents:
            history_database_client.insert_search_history(
                user_id=int(access_token.sub), patent_id=patent.Patent_id, keyword=search_keywords
            )

    return SearchResult(
        patents=patents,
        search_time=datetime.now(tz=timezone.utc),
    )


@router.get("/graph")
async def graph_search(patent_id: int) -> list[PatentInfoModel]:
    """
    Find and return the top-3 most similar patents by embedding cosine distance.

    Args:
        patent_id (int): The ID of the patent to query.

    Returns:
        List[PatentInfoModel]: A list of up to three PatentInfoModel objects.

    """
    patent_ids = search_database_client.search_patent_similarity_by_id(patent_id=patent_id)

    return search_database_client.search_patent_by_id(patent_ids)


@router.post("/scraper/")
async def download_patent(patent_keyword: str = "鞋面") -> list[int | None]:
    Scraper.create_scraper()
    Scraper.keyword = patent_keyword

    if POPPLER_PATH is None:
        msg = "POPPLER_PATH"
        raise EnvironmentVariableNotSetError(msg)

    url_list = Scraper.get_patent_url(page=1)

    patent_infos: list[PDFInfo] = []
    for url in url_list:
        patent_data = Scraper.get_patent_information(url)
        logger.info(patent_data)
        patent_id = scraper_database_client.insert_patent(patent=patent_data)

        image_path_list = Scraper.get_patent_image(url)
        logger.info(image_path_list)

        if patent_id is None:
            continue

        for image in image_path_list.image_list:
            image_embedding = embedding_model.process(image_path=image.image_path)

            search_database_client.insert_vector(
                embedding=image_embedding, patent_id=patent_id, page=image.page, content=image.image_path, is_image=True
            )

        patent_infos.append(
            PDFInfo(patent_id=patent_id, patent_file_path=patent_data.PatentFilePath, patent_title=patent_data.Title)
        )

    logger.info(patent_infos)
    Scraper.destroy_scraper()

    results = pdf_extractor.process_multiple([info.patent_file_path for info in patent_infos], POPPLER_PATH)
    logger.debug("| Finish OCR |")

    regex_pattern = r"---\s*Page\s*(\d+)\s*---\s*([\s\S]*?)(?=(?:---\s*Page\s*\d+\s*---)|$)"
    for index, items in enumerate(results.items()):
        pdf_path, output_path = items[0], items[1]
        if output_path is None:
            continue

        with Path.open(Path(output_path), mode="r", encoding="utf-8") as f:
            text = f.read()
            text_split = re.findall(pattern=regex_pattern, string=text)

        pdf_chunk_embeddings: list[PDFChunkEmbedding] = [
            PDFChunkEmbedding(
                patent_id=patent_infos[index].patent_id,
                page_number=chunk[0],
                content=chunk[1],
                embedding=llm_client.embed_text(chunk[1]),
            )
            for chunk in text_split
        ]

        for pdf_chunk_embedding in pdf_chunk_embeddings:
            search_database_client.insert_vector(
                embedding=pdf_chunk_embedding.embedding,
                patent_id=patent_infos[index].patent_id,
                page=pdf_chunk_embedding.page_number,
                content=pdf_chunk_embedding.content,
                is_image=False,
            )
        msg = f"Successfully processed {pdf_path} -> {output_path}"
        logger.info(msg)

    return [patent_info.patent_id for patent_info in patent_infos]

# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from sqlalchemy import func, insert, select

from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.history import SearchHistoryRecord
from Backend.utility.model.handler.database.scheme import (
    PatentScheme,
    SearchHistoryScheme,
)
from Backend.utility.model.handler.scraper import PatentInfoModel

from .database import DatabaseConnection


class SearchEngineOperation:
    def __init__(self) -> None:
        self.logger = Logger().get_logger()
        self.database = DatabaseConnection

    def full_text_search(self, search_keywords: str) -> list[PatentInfoModel]:
        operation = select(PatentScheme).where(
            func.to_tsvector("english", PatentScheme.title).bool_op("@@")(func.to_tsquery("english", search_keywords))
        )

        result = self.database.run_query(operation)

        self.logger.info(result)

        # for i in result:
        #     self.logger.debug(i[0].id)
        patent_list: list[PatentInfoModel] = [
            PatentInfoModel(
                Patent_id=patent["PatentScheme"].patent_id,
                Title=patent["PatentScheme"].title,
                ApplicationDate=patent["PatentScheme"].application_date,
                PublicationDate=patent["PatentScheme"].publication_date,
                ApplicationNumber=patent["PatentScheme"].application_number,
                PublicationNumber=patent["PatentScheme"].publication_number,
                Applicant=patent["PatentScheme"].applicant,
                Inventor=patent["PatentScheme"].inventor,
                Attorney=patent["PatentScheme"].attorney,
                Priority=patent["PatentScheme"].priority,
                GazetteIPC=patent["PatentScheme"].gazette_ipc,
                IPC=patent["PatentScheme"].ipc,
                GazetteVolume=patent["PatentScheme"].gazette_volume,
                KindCodes=patent["PatentScheme"].kind_codes,
                PatentURL=patent["PatentScheme"].patent_url,
                PatentFilePath=patent["PatentScheme"].patent_file_path,
            )
            for patent in result
        ]
        self.logger.info(patent_list)

        return patent_list

    # def vector_search(self) -> list[PatentModel]: ...

    def log_search_history(self, search_keywords: str, search_result: SearchHistoryRecord) -> bool:
        operation = insert(SearchHistoryScheme).values(
            user_id=search_result.user_id,
            patent_id=search_result.patent_id,
            keyword=search_keywords,
            search_time=search_result.search_time,
        )

        result = self.database.run_write(operation)
        self.logger.info(result)

        return result

    def insert_vector(
        self, embedding: list[float], patent_id: int, page: int, content: str, is_image: bool = False
    ) -> bool:
        """
        Inserts a vector embedding with associated metadata into the database.

        This method inserts a vector (embedding) along with its patent ID, page number,
        and image flag into the `vector` table using a raw SQL query. The operation is
        executed via a custom `run_raw_query` method, and the SQL statement is logged
        for debugging.

        Args:
            embedding (List[float]): The vector embedding to insert, represented as a list
                of floats. Must match the dimension of the `VECTOR` column (e.g., 1536).
            patent_id (int): The ID of the patent associated with the embedding.
            page (int): The page number associated with the embedding.
            content: text content or image path
            is_image (bool, optional): Indicates if the embedding is derived from an image.
                Defaults to False.

        Returns:
            bool: True if the insertion is successful, False otherwise.

        Raises:
            Exception: If the database operation fails (e.g., due to dimension mismatch,
                connection issues, or invalid data). Errors are logged via `self.logger`.

        """
        if is_image:
            raw_sql = """
                INSERT INTO patent_image_vector (
                    patent_id,
                    page,
                    image_path,
                    embedding
                ) VALUES (
                    :patent_id,
                    :page,
                    :image_path,
                    :embedding
                )"""

            result = self.database.run_raw_query(
                raw_sql,
                param={
                    "patent_id": patent_id,
                    "page": page,
                    "image_path": content,
                    "embedding": embedding,
                },
            )
        else:
            raw_sql = """
                INSERT INTO patent_content_vector (
                    patent_id,
                    page,
                    content,
                    embedding
                ) VALUES (
                    :patent_id,
                    :page,
                    :content,
                    :embedding
                )"""

            result = self.database.run_raw_query(
                raw_sql,
                param={
                    "patent_id": patent_id,
                    "page": page,
                    "content": content,
                    "embedding": embedding,
                },
            )

        return not isinstance(result, bool)

# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from sqlalchemy import insert

from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.handler.database.scheme import PatentScheme
from Backend.utility.model.handler.scraper import PatentModel

from .database import DatabaseConnection


class ScraperOperation:
    def __init__(self):
        self.logger = Logger().get_logger()
        self.database = DatabaseConnection

    def insert_patent(self, patent: PatentModel) -> int | None:
        operation = (
            insert(PatentScheme)
            .values(
                title=patent.Title,
                application_date=patent.ApplicationDate,
                publication_date=patent.PublicationDate,
                application_number=patent.ApplicationNumber,
                publication_number=patent.PublicationNumber,
                applicant=patent.Applicant,
                inventor=patent.Inventor,
                attorney=patent.Attorney,
                priority=patent.Priority,
                gazette_ipc=patent.GazetteIPC,
                ipc=patent.IPC,
                gazette_volume=patent.GazetteVolume,
                kind_codes=patent.KindCodes,
                patent_url=patent.PatentURL,
                patent_file_path=patent.PatentFilePath,
            )
            .returning(PatentScheme.patent_id)
        )

        result = self.database.transaction(operation)

        self.logger.info(result)

        if isinstance(result, bool) or result == []:
            return None

        return result[0]["patent_id"]

    # def insert_vector(self, embedding: list[float], patent_id: int, page: int, is_image: bool = False) -> bool:
    #     """
    #     Inserts a vector embedding with associated metadata into the database.

    #     This method inserts a vector (embedding) along with its patent ID, page number,
    #     and image flag into the `vector` table using a raw SQL query. The operation is
    #     executed via a custom `run_raw_query` method, and the SQL statement is logged
    #     for debugging.

    #     Args:
    #         embedding (List[float]): The vector embedding to insert, represented as a list
    #             of floats. Must match the dimension of the `VECTOR` column (e.g., 1536).
    #         patent_id (int): The ID of the patent associated with the embedding.
    #         page (int): The page number associated with the embedding.
    #         is_image (bool, optional): Indicates if the embedding is derived from an image.
    #             Defaults to False.

    #     Returns:
    #         bool: True if the insertion is successful, False otherwise.

    #     Raises:
    #         Exception: If the database operation fails (e.g., due to dimension mismatch,
    #             connection issues, or invalid data). Errors are logged via `self.logger`.

    #     """
    #     raw_sql = """
    #         INSERT INTO vector (
    #             patent_id,
    #             page,
    #             embedding,
    #             is_image
    #         ) VALUES (
    #             :patent_id,
    #             :page,
    #             :embedding,
    #             :is_image
    #         )"""

    #     return self.database.run_raw_query(
    #         raw_sql,
    #         parameters={
    #             "patent_id": patent_id,
    #             "page": page,
    #             "embedding": embedding,
    #             "is_image": is_image,
    #         },
    #     )


if __name__ == "__main__":
    ...

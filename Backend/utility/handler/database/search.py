# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from sqlalchemy import func, insert, or_, select

from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.history import SearchHistoryRecord
from Backend.utility.model.handler.database.scheme import ContentVectorScheme, PatentScheme, SearchHistoryScheme
from Backend.utility.model.handler.scraper import PatentInfoModel

from .database import DatabaseConnection


class SearchEngineOperation:
    def __init__(self) -> None:
        self.logger = Logger().get_logger()
        self.database = DatabaseConnection

    def full_text_search(self, search_keywords: str) -> list[PatentInfoModel]:
        operation = select(PatentScheme).where(
            or_(
                func.to_tsvector("simple", PatentScheme.title).bool_op("@@")(
                    func.websearch_to_tsquery("simple", search_keywords)
                ),
                PatentScheme.title.like("%" + search_keywords + "%"),
            )
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

    def search_patent_similarity_by_vector(self, embedding_vector: list[float]) -> list[int]:
        """
        Retrieve the top-3 most similar patent IDs to the given embedding vector.

        Args:
            embedding_vector (list[float]): The embedding vector to use as the similarity query.

        Returns:
            list[int]: A list of up to three patent IDs most similar to the input vector.
                    Returns an empty list if no similar patents are found.

        Raises:
            DatabaseError: If the similarity search fails.

        """
        search_operation = (
            select(ContentVectorScheme.patent_id)
            .order_by(ContentVectorScheme.embedding.cosine_distance(embedding_vector).label("dist"))
            .limit(3)
        )

        target_patents = self.database.run_query_vector(search_operation)
        self.logger.info("Found similar patent IDs: %s", target_patents)

        if isinstance(target_patents, bool) or target_patents == []:
            return []

        return [patent["ContentVectorScheme"].patent_id for patent in target_patents]

    def search_patent_similarity_by_id(self, patent_id: int) -> set[int]:
        """
        Find the top-3 most similar patents to a given patent, based on embedding cosine distance.

        Args:
            patent_id (int): The ID of the patent to use as the similarity query.

        Returns:
            set[int]: A set of patent IDs corresponding to the three most similar patents by embedding.

        Raises:
            DatabaseError: If the embedding query or similarity search fails.

        """
        embedding_query = select(ContentVectorScheme.embedding).where(ContentVectorScheme.patent_id == patent_id)
        target_embeddings = self.database.run_query(embedding_query)
        self.logger.info(target_embeddings)

        patent_list: set[int] = set()
        for embedding in target_embeddings:
            search = (
                select(ContentVectorScheme.patent_id)
                .order_by(
                    ContentVectorScheme.embedding.cosine_distance(embedding["embedding"]).label("dist"),
                )
                .limit(3)
            )

            patent_id_list = set(self.database.run_query_vector(search))
            self.logger.info(patent_id_list)
            patent_list.add(patent_id)

        return patent_list

    def search_patent_by_id(self, patent_ids: set[int]) -> list[PatentInfoModel]:
        """
        Retrieve detailed patent information for a set of patent IDs.

        Args:
            patent_ids (set[int]): A collection of patent IDs to look up.

        Returns:
            list[PatentInfoModel]: A list of PatentInfoModel instances containing metadata
            for each found patent. Returns an empty list if none are found.

        Raises:
            DatabaseError: If the database query fails.

        """
        operation = select(PatentScheme).where(PatentScheme.patent_id.in_(patent_ids))

        patents = self.database.run_query(operation)
        self.logger.info(patents)

        if isinstance(patents, bool) or patents == []:
            return []

        return [
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
            for patent in patents
        ]

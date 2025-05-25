# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from sqlalchemy import select

from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.handler.database.scheme import PatentScheme
from Backend.utility.model.handler.scraper import PatentInfoModel

from .database import DatabaseConnection


class ResultOperation:
    def __init__(self) -> None:
        self.logger = Logger().get_logger()
        self.database = DatabaseConnection

    def search_patent_by_id(self, patent_id: int) -> PatentInfoModel | None:
        """
        Retrieve detailed patent information for IDs.

        Args:
            patent_id (int): A collection of patent IDs to look up.

        Returns:
            PatentInfoModel: PatentInfoModel instances containing metadata.

        Raises:
            DatabaseError: If the database query fails.

        """
        operation = select(PatentScheme).where(PatentScheme.patent_id == patent_id)

        patent = self.database.run_query(operation)
        self.logger.info(patent)

        if isinstance(patent, bool) or patent == []:
            return None

        return PatentInfoModel(
            Patent_id=patent[0]["PatentScheme"].patent_id,
            Title=patent[0]["PatentScheme"].title,
            ApplicationDate=patent[0]["PatentScheme"].application_date,
            PublicationDate=patent[0]["PatentScheme"].publication_date,
            ApplicationNumber=patent[0]["PatentScheme"].application_number,
            PublicationNumber=patent[0]["PatentScheme"].publication_number,
            Applicant=patent[0]["PatentScheme"].applicant,
            Inventor=patent[0]["PatentScheme"].inventor,
            Attorney=patent[0]["PatentScheme"].attorney,
            Priority=patent[0]["PatentScheme"].priority,
            GazetteIPC=patent[0]["PatentScheme"].gazette_ipc,
            IPC=patent[0]["PatentScheme"].ipc,
            GazetteVolume=patent[0]["PatentScheme"].gazette_volume,
            KindCodes=patent[0]["PatentScheme"].kind_codes,
            PatentURL=patent[0]["PatentScheme"].patent_url,
            PatentFilePath=patent[0]["PatentScheme"].patent_file_path,
        )

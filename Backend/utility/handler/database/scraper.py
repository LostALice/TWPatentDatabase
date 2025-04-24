# Code by AkinoAlice@TyrantRey

from sqlalchemy import insert

from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.handler.database.scheme import PatentScheme
from Backend.utility.model.handler.scraper import PatentInfo

from .database import DatabaseConnection


class ScraperOperation:
    def __init__(self):
        self.logger = Logger().get_logger()
        self.database = DatabaseConnection

    def insert_patent(self, patent: PatentInfo) -> bool:
        operation = insert(PatentScheme).values(
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

        return self.database.run_write(operation)

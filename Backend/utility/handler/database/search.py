# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from sqlalchemy import func, select

from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.handler.database.scheme import PatentScheme
from Backend.utility.model.handler.scraper import PatentInfo

from .database import DatabaseConnection


class SearchEngineOperation:
    def __init__(self) -> None:
        self.logger = Logger().get_logger()

    def search(self, search_keywords: str) -> list[PatentInfo]:
        self.logger.info(search_keywords)
        self.database = DatabaseConnection

        operation = select(PatentScheme).where(
            func.to_tsvector("english", PatentScheme.title).bool_op("@@")(func.to_tsquery("english", search_keywords))
        )

        result = self.database.run_query(operation)

        self.logger.info(result)

        # for i in result:
        #     self.logger.debug(i[0].id)
        patent_list: list[PatentInfo] = [
            PatentInfo(
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


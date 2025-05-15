# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from sqlalchemy import func, insert, select

from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.history import SearchHistoryRecord
from Backend.utility.model.handler.database.scheme import HistoryScheme, PatentScheme
from Backend.utility.model.handler.scraper import PatentInfoModel

from .database import DatabaseConnection


class SearchEngineOperation:
    def __init__(self) -> None:
        self.logger = Logger().get_logger()

    def full_text_search(self, search_keywords: str) -> list[PatentInfoModel]:
        self.logger.info(search_keywords)
        self.database = DatabaseConnection

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
        operation = insert(HistoryScheme).values(
            user_id=search_result.user_id,
            patent_id=search_result.patent_id,
            keyword=search_keywords,
            search_time=search_result.search_time,
        )

        result = self.database.run_write(operation)
        self.logger.info(result)

        return result

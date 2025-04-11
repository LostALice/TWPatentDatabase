# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from os import getenv
from typing import TYPE_CHECKING

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable

from Backend.utility.error.common import EnvironmentalVariableNotSetError
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.handler.database.database import DatabaseConfig
from Backend.utility.model.handler.database.scheme import BaseScheme

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.engine.row import RowMapping
    from sqlalchemy.sql import Delete, Executable, Insert, Select, Update

if getenv("DEBUG") is None:
    from dotenv import load_dotenv

    load_dotenv("./.env")


class Database:
    def __init__(self) -> None:
        self.logger = Logger().get_logger()

        self.logger.info("=========================")
        self.logger.info("| Start Loading Database |")
        self.logger.info("=========================")

        self._POSTGRESQL_DEBUG = getenv("POSTGRESQL_DEBUG")

        self._POSTGRESQL_HOST = getenv("POSTGRESQL_HOST")
        self._POSTGRESQL_USERNAME = getenv("POSTGRESQL_USERNAME")
        self._POSTGRESQL_PASSWORD = getenv("POSTGRESQL_PASSWORD")
        self._POSTGRESQL_DATABASE = getenv("POSTGRESQL_DATABASE")
        self._POSTGRESQL_PORT = getenv("POSTGRESQL_PORT")

        if self._POSTGRESQL_DEBUG is None:
            msg = "POSTGRESQL_DEBUG"
            raise EnvironmentalVariableNotSetError(msg)
        if self._POSTGRESQL_HOST is None:
            msg = "POSTGRESQL_HOST"
            raise EnvironmentalVariableNotSetError(msg)
        if self._POSTGRESQL_USERNAME is None:
            msg = "POSTGRESQL_USERNAME"
            raise EnvironmentalVariableNotSetError(msg)
        if self._POSTGRESQL_PASSWORD is None:
            msg = "POSTGRESQL_PASSWORD"
            raise EnvironmentalVariableNotSetError(msg)
        if self._POSTGRESQL_DATABASE is None:
            msg = "POSTGRESQL_DATABASE"
            raise EnvironmentalVariableNotSetError(msg)
        if self._POSTGRESQL_PORT is None:
            msg = "POSTGRESQL_PORT"
            raise EnvironmentalVariableNotSetError(msg)

        self.config = DatabaseConfig(
            host=self._POSTGRESQL_HOST,
            username=self._POSTGRESQL_USERNAME,
            password=self._POSTGRESQL_PASSWORD,
            database=self._POSTGRESQL_DATABASE,
            port=int(self._POSTGRESQL_PORT),
        )

        self.DATABASE_URL = f"postgresql+psycopg2://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"

        self.engine = create_engine(self.DATABASE_URL, echo=True)
        self.session = sessionmaker(bind=self.engine)

        if self._POSTGRESQL_DEBUG:
            self.logger.warning("Deleting Exist Database")
            self.__clear_database()

        self.__create_database()

        self.logger.info("===================")
        self.logger.info("| Loaded Database |")
        self.logger.info("===================")

    def __create_database(self) -> None:
        for table in BaseScheme.metadata.sorted_tables:
            self.logger.debug(str(CreateTable(table).compile(self.engine)))
        BaseScheme.metadata.create_all(self.engine)

    def __clear_database(self) -> None:
        BaseScheme.metadata.drop_all(self.engine)

    def log_sql(self, sql_statement) -> None:
        self.logger.debug(sql_statement.compile())

    def run_write(self, statement: Insert | Update | Delete) -> bool:
        """
        Executes an INSERT, UPDATE, or DELETE statement.

        Args:
            statement (Insert | Update | Delete): SQLAlchemy write operation.

        Returns:
            bool: True if committed successfully, False otherwise.

        """
        self.log_sql(statement)

        with self.session() as session:
            session.begin()
            try:
                session.execute(statement)
            except Exception as e:
                self.logger.critical("Write operation failed: %s", e)
                session.rollback()
                return False
            else:
                session.commit()
                return True

    def run_query(self, query: Select) -> Sequence[RowMapping]:
        """
        Executes a SELECT query and returns the result as a list of RowMapping.

        Args:
            query (Select): SQLAlchemy Select query.

        Returns:
            Sequence[RowMapping]: List of result rows.

        """
        self.log_sql(query)

        with self.session() as session:
            try:
                result = session.execute(query)
                return result.mappings().all()
            except Exception as e:
                self.logger.critical("Query failed: %s", e)
                return []

    def transaction(self, action: Executable) -> Sequence[RowMapping] | bool:
        self.log_sql(action)  # Assume this logs SQL text properly

        with self.session() as transaction_session:
            transaction_session.begin()
            try:
                result = transaction_session.execute(action)
                transaction_session.commit()
                return result.mappings().all()
            except Exception as e:
                self.logger.critical("Transaction failed: %s", e)
                transaction_session.rollback()
                return False


if __name__ == "__main__":
    db_config: DatabaseConfig = DatabaseConfig(
        host="localhost",
        port=3306,
        username="root",
        password="password",
        database="patent_database",
    )
    db = Database()

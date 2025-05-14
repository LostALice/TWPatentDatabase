# Code by AkinoAlice@TyrantRey

from __future__ import annotations

from os import getenv
from typing import TYPE_CHECKING

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable

from Backend.utility.error.common import EnvironmentVariableNotSetError
from Backend.utility.error.database.database import IndexCreationError
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.handler.database.database import DatabaseConfig
from Backend.utility.model.handler.database.scheme import BaseScheme, VectorScheme

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.engine.row import RowMapping
    from sqlalchemy.sql import Delete, Executable, Insert, Select, Update

# development
GLOBAL_DEBUG_MODE = getenv("DEBUG")
logger = Logger().get_logger()
logger.info("Global Debug Mode: %s", GLOBAL_DEBUG_MODE)
if GLOBAL_DEBUG_MODE is None or GLOBAL_DEBUG_MODE == "True":
    from dotenv import load_dotenv

    load_dotenv("./.env")


class Database:
    def __init__(self) -> None:
        self.logger = Logger().get_logger()

        self.logger.info("| Start Loading Database |")
        self.logger.info("| Getting Database Env |")

        self._POSTGRESQL_DEBUG = getenv("POSTGRESQL_DEBUG")

        self._POSTGRESQL_HOST = getenv("POSTGRESQL_HOST")
        self._POSTGRESQL_USERNAME = getenv("POSTGRESQL_USERNAME")
        self._POSTGRESQL_PASSWORD = getenv("POSTGRESQL_PASSWORD")
        self._POSTGRESQL_DATABASE = getenv("POSTGRESQL_DATABASE")
        self._POSTGRESQL_PORT = getenv("POSTGRESQL_PORT")

        if self._POSTGRESQL_DEBUG is None:
            msg = "POSTGRESQL_DEBUG"
            raise EnvironmentVariableNotSetError(msg)
        if self._POSTGRESQL_HOST is None:
            msg = "POSTGRESQL_HOST"
            raise EnvironmentVariableNotSetError(msg)
        if self._POSTGRESQL_USERNAME is None:
            msg = "POSTGRESQL_USERNAME"
            raise EnvironmentVariableNotSetError(msg)
        if self._POSTGRESQL_PASSWORD is None:
            msg = "POSTGRESQL_PASSWORD"
            raise EnvironmentVariableNotSetError(msg)
        if self._POSTGRESQL_DATABASE is None:
            msg = "POSTGRESQL_DATABASE"
            raise EnvironmentVariableNotSetError(msg)
        if self._POSTGRESQL_PORT is None:
            msg = "POSTGRESQL_PORT"
            raise EnvironmentVariableNotSetError(msg)

        self.logger.info("| Setting up Database connection |")

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

        if self._POSTGRESQL_DEBUG == "True":
            self.logger.warning("Deleting Exist Database")
            self.__clear_database()
            self.__initialize_database()

        self.logger.info("| Loaded Database |")

    def __initialize_database(self) -> None:
        """
        Initializes the database by creating all tables defined in the BaseScheme
        metadata and ensuring the required full-text search index exists.

        This method performs the following:
        - Logs the SQL DDL statements for table creation (for debug visibility).
        - Executes table creation via SQLAlchemy's metadata binding.
        - Executes a raw SQL statement to create a GIN full-text search index on the
          `patent` table, if it does not already exist.

        Raises:
            IndexCreationError: If the full-text index creation fails.

        """
        for table in BaseScheme.metadata.sorted_tables:
            self.logger.debug(str(CreateTable(table).compile(self.engine)))
        BaseScheme.metadata.create_all(self.engine)

        # English full text search index
        tsvector_index = """CREATE INDEX IF NOT EXISTS patent_search_idx ON patent USING GIN (to_tsvector('english', coalesce(application_number, '') || ' ' || coalesce(applicant, '') || ' ' || coalesce(ipc, '') || ' ' || coalesce(title, '')));"""
        is_index_created = self.run_raw_query(tsvector_index)

        if not is_index_created:
            patent_index = "patent_search_idx"
            raise IndexCreationError(patent_index)

        self.logger.info("Created index: patent_search_idx")

    def __clear_database(self) -> None:
        BaseScheme.metadata.drop_all(self.engine)

    def log_sql(self, sql_statement) -> None:
        """
        Log operation from code to SQL

        Args:
            sql_statement (Executable): operation

        """
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
                session.commit()
                return result.mappings().all()
            except Exception as e:
                self.logger.critical("Query failed: %s", e)
                self.logger.critical("SQL statement: %s", query)
                return []

    def transaction(self, action: Executable) -> Sequence[RowMapping] | bool:
        """
        Executes a SQLAlchemy Executable (e.g., INSERT, UPDATE, DELETE, or raw SQL)
        within a transactional session context.

        If the statement returns rows (like a SELECT), the results are returned as a
        list of RowMapping. For non-returning actions, it returns True on success.

        On error, logs the exception, rolls back the transaction, and returns False.

        Args:
            action (Executable): A SQLAlchemy Core Executable, such as a text query or
                insert/update/delete statement.

        Returns:
            Sequence[RowMapping] | bool: List of result rows if the statement returns
            data; True if executed successfully without a result set; False on failure.

        """
        self.log_sql(action)

        with self.session() as session:
            try:
                result = session.execute(action)
                session.commit()
                return result.mappings().all()
            except Exception as e:
                self.logger.critical("Transaction failed: %s", e)
                self.logger.critical("SQL statement: %s", action)
                session.rollback()
                return False

    def run_raw_query(self, raw_query: str, param: dict | None = None) -> Sequence[RowMapping] | bool:
        """
        Execute a raw SQL query using the provided query string and parameters.

        Args:
            raw_query (str): The SQL query string to be executed.
            param (dict | None, optional): A dictionary of parameters to pass to the query. Defaults to None.

        Returns:
            Sequence[RowMapping] | bool:
                - If the query returns rows, a sequence of RowMapping objects is returned.
                - If the query does not return rows or an error occurs, a boolean is returned:
                    - True: The query executed successfully without returning data.
                    - False: The query execution failed.

        Raises:
            SQLAlchemyError: Raised for any SQL execution errors, with logging of the error and query string.

        """
        statement = text(raw_query)
        self.log_sql(statement)

        with self.engine.begin() as connection:
            try:
                result = connection.execute(statement=statement, parameters=param)

                if result.returns_rows:
                    return result.mappings().all()

            except Exception as e:
                self.logger.critical("Transaction failed: %s", e)
                self.logger.critical("Raw query: %s", raw_query)
                return False
            else:
                return True


DatabaseConnection = Database()

if __name__ == "__main__":
    ...

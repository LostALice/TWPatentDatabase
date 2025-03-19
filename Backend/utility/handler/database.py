# Code by AkinoAlice@TyrantRey

from pprint import pformat
from typing import Callable

import psycopg2
import psycopg2.extras

from utility.handler.log_handler import Logger
from utility.model.handler.database import DatabaseConfig
from utility.model.handler.scraper import PatentInfo


class Database:
    def __init__(self, config: DatabaseConfig, debug: bool = False) -> None:
        """Initialize the Database instance with connection parameters."""
        self.logger = Logger("./logging.log").logger

        self.host = config.host
        self.user = config.username
        self.password = config.password
        self.database = config.database
        self.port = config.port

        self._connection = psycopg2.connect(
            host=self.host, database=self.database, user=self.user, password=self.password, port=self.port
        )
        self.cursor = self._connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        if debug:
            self.init_database()
            self.clear_database()
        else:
            self.init_database()

    @staticmethod
    def __db_error_handling_wrapper(func: Callable):
        """A decorator that wraps a database method with try/except to catch and log errors."""

        def wrap(self, *args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception as error:
                _error_message = f"Error in {func.__name__}: {error}"
                self.logger.exception(_error_message)
                # Rollback the transaction if connection exists
                self.cursor.rollback()
            else:
                self.logger.debug(pformat(self.cursor.query))
                return result

        return wrap

    @__db_error_handling_wrapper
    def init_database(self) -> None:
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patent (
                id SERIAL PRIMARY KEY,
                application_date INTEGER,
                publication_date INTEGER,
                application_number VARCHAR(100),
                publication_number VARCHAR(100),
                applicant TEXT,
                inventor TEXT,
                attorney TEXT,
                priority TEXT,
                gazette_ipc TEXT,
                ipc TEXT,
                gazette_volume TEXT,
                kind_codes TEXT,
                patent_url TEXT,
                patent_file_path TEXT
            );"""
        )

        self.cursor.commit()

    @__db_error_handling_wrapper
    def clear_database(self) -> bool:
        """Clear all data from the 'patent' table."""
        self.cursor.execute("TRUNCATE TABLE patent;")
        self.cursor.commit()
        return True

    @__db_error_handling_wrapper
    def insert_patent(self, patent: PatentInfo) -> bool:
        self.cursor.execute(
            """
            INSERT INTO patent (
                application_date,
                publication_date,
                application_number,
                publication_number,
                applicant,
                inventor,
                attorney,
                priority,
                gazette_ipc,
                ipc,
                gazette_volume,
                kind_codes,
                patent_url,
                patent_file_path
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                patent.ApplicationDate,
                patent.PublicationDate,
                patent.ApplicationNumber,
                patent.PublicationNumber,
                patent.Applicant,
                patent.Inventor,
                patent.Attorney,
                patent.Priority,
                patent.GazetteIPC,
                patent.IPC,
                patent.GazetteVolume,
                patent.KindCodes,
                patent.PatentURL,
                patent.PatentFilePath,
            ),
        )

        self.cursor.commit()
        return True

    @__db_error_handling_wrapper
    def connect(self) -> None:
        """Establish a connection to the PostgreSQL database and create a cursor."""
        self.connection = psycopg2.connect(
            host=self.host, database=self.database, user=self.user, password=self.password, port=self.port
        )
        self.cursor = self.connection.cursor()
        self.logger.info("Connected to PostgreSQL successfully.")

    def close(self) -> None:
        """Close the cursor and connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        self.logger.info("PostgreSQL connection closed.")


# Example usage:
if __name__ == "__main__":
    # Replace with your actual connection parameters
    database_config = DatabaseConfig(
        host="localhost",
        port=3306,
        username="root",
        password="password",
        database="patent_database",
    )
    database = Database(config=database_config, debug=True)

    # Execute a query to retrieve the PostgreSQL version.
    # version = db.execute_query("SELECT version();", fetch_one=True)
    # print("PostgreSQL version:", version)

    database.close()

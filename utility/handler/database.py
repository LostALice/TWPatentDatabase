# Code by AkinoAlice@TyrantRey

from psycopg2 import OperationalError, pool, connect
from psycopg2.extras import DictCursor
from utility.handler.log import Logger
from typing import Callable
from functools import wraps

from utility.modal.patent import PatentInfo

import time


class Database(object):
    def __init__(
        self, database: str, user: str, password: str, host: str, port: int = 5432, debug: bool = False
    ) -> None:
        """Initialize a new Database connection

        Args:
            database (str): database name
            user (str): user name
            password (str): password
            host (str): database host ip
            port (int, optional): PostgreSQL port number. Defaults to 5432.
        """
        self.logger = Logger(__name__)

        self.dbname = database.lower()
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.debug = debug
        self.connection_pool = None
        self._create_connection_pool()

        self._initialize_table()

    def _initialize_database(self) -> None:
        """Connect to database and create the target database if it not exist."""

        _connection = connect(
            user=self.user, password=self.password, host=self.host, port=self.port
        )
        _connection.autocommit = True

        _cursor = _connection.cursor(cursor_factory=DictCursor)

        _cursor.execute("SELECT datname FROM pg_database")
        result = _cursor.fetchall()

        # if self.debug == True ==> init new database
        if [self.dbname] in result or not self.debug:
            self.logger.info(f"Database {self.dbname} already exists")
            return
        else:
            self.logger.info(f"Database {self.dbname} not exists, Creating")
            _cursor.execute(f"CREATE DATABASE {self.dbname}")
        _connection.commit()

        self.logger.info("Database created")

        _connection.close()
        self._create_connection_pool()

    def _create_connection_pool(self):
        """Create a connection pool."""

        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1,
                20,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            self.logger.info("Connection pool created successfully")

        except OperationalError as e:
            self.logger.error(f"Error creating connection pool: {e}")
            self.logger.info(f"Trying to initialize Database {self.dbname}")
            self._initialize_database()

            # self.connection_pool = None

    def _get_connection(self, retry: int = 3):
        """Get a connection from the pool."""

        self.logger.info(f"Getting connection from pool")
        if retry == 0:
            self.logger.critical("Failed to get connection")
            raise Exception("Failed to get connection")

        if self.connection_pool:
            try:
                connection = self.connection_pool.getconn()
                if connection.closed:
                    self.logger.info("Connection was closed, trying to reconnect...")
                    connection = self.connection_pool.getconn()
                return connection
            except OperationalError as e:
                self.logger.error(f"Error during getting connection: {e}")
                self._create_connection_pool()
                self._get_connection(retry=retry - 1)
        else:
            self.logger.critical("Connection pool is not available.")
            self._create_connection_pool()
            self._get_connection(retry=retry - 1)

    def _release_connection(self, connection):
        """Release a connection back to the pool."""

        if self.connection_pool and connection:
            self.connection_pool.putconn(connection)

    @staticmethod
    def auto_commit(func: Callable) -> Callable:
        """Decorator to commit changes after function execution."""

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            connection = self._get_connection()
            cursor = connection.cursor(cursor_factory=DictCursor)
            start_time = time.time()
            try:
                result = func(self, cursor, *args, **kwargs)

                connection.commit()

                query_time = time.time() - start_time
                query = args[0]
                params = args[1] if len(args) > 1 else None
                self.logger.info(
                    f"Executed query: {query}, Params: {params}, Time: {query_time:.4f}s"
                )

                return result

            # Rollback in case of error
            except Exception as e:
                connection.rollback()
                self.logger.error(f"Error: {e}")
                raise

            finally:
                cursor.close()
                self._release_connection(connection)

        return wrapper

    @auto_commit
    def execute_sql_statement(
        self, cursor: DictCursor, query: str, params: dict | None = None
    ):
        """Fetch one result from a query."""
        cursor.execute(query, params)

    @auto_commit
    def fetch_all(self, cursor: DictCursor, query: str, params: dict | None = None):
        """Fetch all result from a query."""
        cursor.execute(query, params)
        return cursor.fetchone()

    @auto_commit
    def fetch_one(self, cursor: DictCursor, query: str, params: dict | None = None):
        """Fetch one result from a query."""
        cursor.execute(query, params)
        return cursor.fetchone()

    def _initialize_table(self) -> None:
        """check if the patent table exists

        Returns:
            bool: True if the table exists otherwise not exist
        """

        statement = """
            CREATE TABLE IF NOT EXISTS patent (
                ApplicationDate INT,
                PublicationDate INT,
                ApplicationNumber VARCHAR(255),
                PublicationNumber VARCHAR(255),
                Applicant VARCHAR(255),
                Inventor TEXT DEFAULT NULL,
                Attorney TEXT DEFAULT NULL,
                Priority VARCHAR(255) DEFAULT NULL,
                GazetteIPC VARCHAR(255),
                IPC VARCHAR(255),
                GazetteVolume VARCHAR(255),
                KindCodes VARCHAR(255),
                PatentURL VARCHAR(255),
                PatentFilePath VARCHAR(255)
            );
        """
        self.execute_sql_statement(statement)
        self.logger.info("Patent table created successfully!")

    def close(self):
        """Close the connection pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("Connection pool closed")


class DatabaseOperator(Database):
    def __init__(
        self,
        database: str,
        user: str,
        password: str,
        host: str = "localhost",
        port: int = 5432,
        debug: bool = False
    ) -> None:
        super().__init__(database, user, password, host, port, debug)

    def inset_patent(self, patent_info: PatentInfo) -> None:
        """insert patent information into patent table

        Args:
            patent_info (list[PatentInfo] | PatentInfo): list of patent information

        Returns:
            bool: success or failure
        """
        self.execute_sql_statement(
            """
            INSERT INTO patent (
                ApplicationDate,
                PublicationDate,
                ApplicationNumber,
                PublicationNumber,
                Applicant,
                Inventor,
                Attorney,
                Priority,
                GazetteIPC,
                IPC,
                GazetteVolume,
                KindCodes,
                PatentURL,
                PatentFilePath
            ) VALUES (
                %(ApplicationDate)s,
                %(PublicationDate)s,
                %(ApplicationNumber)s,
                %(PublicationNumber)s,
                %(Applicant)s,
                %(Inventor)s,
                %(Attorney)s,
                %(Priority)s,
                %(GazetteIPC)s,
                %(IPC)s,
                %(GazetteVolume)s,
                %(KindCodes)s,
                %(PatentURL)s,
                %(PatentFilePath)s
            )""",
            patent_info.model_dump(),
        )


if __name__ == "__main__":
    database = DatabaseOperator(
        database="PatentDatabase",
        user="postgres",
        password="example_password",
        host="localhost",
        port=5432,
    )

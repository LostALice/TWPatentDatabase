# Code by AkinoAlice@TyrantRey

from psycopg2 import OperationalError, pool, connect
from psycopg2.extras import DictCursor
from utility.handler.log import Logger
from typing import Callable
from functools import wraps

import time


class Database(object):
    def __init__(
        self, database: str, user: str, password: str, host: str, port: int = 5432
    ) -> None:
        """Initialize a new Database connection

        Args:
            database (str): database name
            user (str): user name
            password (str): password
            host (str): database host ip
            port (int, optional): PostgreSQL port number. Defaults to 5432.
        """
        self.logger = Logger("./logging.log")

        self.dbname = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection_pool = None
        self._create_connection_pool()

    def _initialize_database(self) -> None:
        """Connect to database and create the target database if it not exist."""

        _connection = connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        _connection.autocommit = True

        _cursor = _connection.cursor(cursor_factory=DictCursor)

        _cursor.execute("SELECT datname FROM pg_database")
        result = _cursor.fetchall()
        if [self.dbname] in result:
            self.logger.info(f"Database {self.dbname} already exists")
            return
        else:
            self.logger.info(f"Database {self.dbname} not exists, Creating")
            _cursor.execute(f"CREATE DATABASE ({self.dbname})")
        _connection.commit()

        self.logger.info("Database created")

        _connection.close()

    def _create_connection_pool(self):
        """Create a connection pool."""

        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1,
                20,
                dbname=self.dbname.lower(),
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

            self.connection_pool = None

    def _get_connection(self):
        """Get a connection from the pool."""

        if self.connection_pool:
            try:
                connection = self.connection_pool.getconn()
                if connection.closed:
                    self.logger.info(
                        "Connection was closed, trying to reconnect...")
                    connection = self.connection_pool.getconn()  # Reconnect
                return connection
            except OperationalError as e:
                self.logger.error(f"Error during getting connection: {e}")
                self._create_connection_pool()
        else:
            self.logger.critical("Connection pool is not available.")
            self._create_connection_pool()

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
            start_time = time.time()  # Start the timer
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
    def execute_sql_statement(self, cursor: DictCursor, query: str, params: dict | None = None):
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

    def close(self):
        """Close the connection pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("Connection pool closed")


class DatabaseOperator(Database):
    def __init__(
        self, database: str, user: str, password: str, host: str = "localhost", port: int = 5432
    ) -> None:
        super().__init__(database, user, password, host, port)
        self._check_patent_table_exist()

    def _check_patent_table_exist(self) -> None:
        """check if the patent table exists

        Returns:
            bool: True if the table exists otherwise not exist
        """

        self.fetch_all("SELECT * FROM pg_catalog.pg_tables;")


        statement = """
            CREATE TABLE Patent (
                ApplicationDate INT,
                PublicationDate INT,
                ApplicationNumber VARCHAR(255),
                PublicationNumber VARCHAR(255),
                Applicant VARCHAR(255),
                Inventor VARCHAR(255),
                Attorney VARCHAR(255),
                Priority VARCHAR(255),
                GazetteIPC VARCHAR(255),
                IPC VARCHAR(255),
                GazetteVolume VARCHAR(255),
                KindCodes VARCHAR(255),
                URL VARCHAR(255)
            );
        """
        self.execute_sql_statement(statement)
        self.logger.info("Patent table created successfully!")
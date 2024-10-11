# Code by AkinoAlice@TyrantRey

from psycopg2 import OperationalError, pool, connect
from functools import wraps
from log import Logger

import time


class Database:
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
        self.dbname = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection_pool = None
        self._create_connection_pool()

        self.logger = Logger("./logging.log")

    def _initialize_database(self) -> None:
        """Connect to "postgres" database and create the target database if it not exist."""
        try:
            conn = connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            conn.autocommit = True  # We need to auto-commit for creating the database
            cursor = conn.cursor()

            # Check if the target database exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (self.dbname,)
            )
            db_exists = cursor.fetchone()

            if not db_exists:
                # Create the database if it doesn"t exist
                Logger.info(f"Database {self.dbname} does not exist. Creating")
                cursor.execute(f"CREATE DATABASE {self.dbname}")
                Logger.info(f"Database {self.dbname} created successfully.")
            else:
                Logger.info(f"Database {self.dbname} already exists.")

            cursor.close()
            conn.close()
        except OperationalError as e:
            Logger.error(f"Error while initializing database: {e}")
            raise

    def _create_connection_pool(self):
        """Create a connection pool."""

        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1,
                20,
                dbname=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            Logger.info("Connection pool created successfully")

        except OperationalError as e:
            Logger.error(f"Error creating connection pool: {e}")
            self.connection_pool = None

    def _get_connection(self):
        """Get a connection from the pool."""

        if self.connection_pool:
            try:
                connection = self.connection_pool.getconn()
                if connection.closed:
                    Logger.info("Connection was closed, trying to reconnect...")
                    connection = self.connection_pool.getconn()  # Reconnect
                return connection
            except OperationalError as e:
                Logger.error(f"Error during getting connection: {e}")
                self._create_connection_pool()
        else:
            Logger.critical("Connection pool is not available.")
            self._create_connection_pool()

    def _release_connection(self, connection):
        """Release a connection back to the pool."""

        if self.connection_pool and connection:
            self.connection_pool.putconn(connection)

    def auto_commit(func):
        """Decorator to commit changes after function execution."""

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            connection = self._get_connection()
            cursor = connection.cursor()
            start_time = time.time()  # Start the timer
            try:
                # Execute the function
                result = func(self, cursor, *args, **kwargs)

                # Commit after function execution
                connection.commit()

                query_time = time.time() - start_time
                query = args[0]
                params = args[1] if len(args) > 1 else None
                Logger.info(
                    f"Executed query: {query}, Params: {params}, Time: {query_time:.4f}s"
                )

                return result
            except Exception as e:

                # Rollback in case of error
                connection.rollback()
                Logger.error(f"Error: {e}")
                raise

            finally:
                cursor.close()
                self._release_connection(connection)

        return wrapper

    @auto_commit
    def fetch_one(self, cursor, query, params=None):
        """Fetch one result from a query."""
        cursor.execute(query, params)
        return cursor.fetchone()

    def close(self):
        """Close the connection pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("Connection pool closed")


if __name__ == "__main__":
    db = Database(
        database="your_db", user="your_user", password="your_pass", host="localhost"
    )

    try:
        db.execute_query(
            "CREATE TABLE IF NOT EXISTS test_table(id SERIAL PRIMARY KEY, name TEXT)"
        )
        db.execute_query("INSERT INTO test_table (name) VALUES (%s)", ("John Doe",))
        rows = db.fetch_all("SELECT * FROM test_table")
        Logger.debug(rows)

    finally:
        db.close()

# Code by AkinoAlice@TyrantRey

from __future__ import annotations

import datetime

from sqlalchemy import delete, insert, select, update
from sqlalchemy.dialects.postgresql import Insert as PostgresqlInsert

from Backend.utility.error.database.database import RoleIDNotFoundError
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.application.auth.authorization import Role, User
from Backend.utility.model.handler.database.scheme import (
    LoginScheme,
    RoleScheme,
    UserScheme,
)

from .database import DatabaseConnection


class AuthorizationOperation:
    def __init__(self):
        self.logger = Logger().get_logger()
        self.database = DatabaseConnection

    def fetch_all_role(self) -> list[Role]:
        """
        Fetches all role entries from the database and maps them to Role domain models.

        Executes a SELECT query on the RoleScheme table. If the query succeeds, the
        results are mapped to Role instances. If the query fails or returns no data,
        an empty list is returned.

        Returns:
            list[Role]: A list of Role objects representing the role records in the database.

        """
        operation = select(RoleScheme)
        result = self.database.run_query(operation)
        self.logger.info(result)

        if isinstance(result, bool):
            return []

        return [
            Role(
                role_id=r["RoleScheme"].role_id,
                role_name=r["RoleScheme"].role_name,
                role_description=r["RoleScheme"].role_description,
            )
            for r in result
        ]

    def fetch_role_by_name(self, role_name: str) -> Role | None:
        """
        Retrieves a single role by its name and maps it to a Role domain model.

        Executes a SELECT query on the RoleScheme table, filtered by the given
        role name. If a matching record is found, it is converted into a Role
        object. If no result is found or the query fails, None is returned.

        Args:
            role_name (str): The name of the role to retrieve.

        Returns:
            Role | None: A Role object if a matching role is found; otherwise, None.

        """
        operation = select(RoleScheme).where(RoleScheme.role_name == role_name)
        result = self.database.run_query(operation)
        self.logger.info(result)

        if isinstance(result, bool) or result == []:
            return None

        return Role(
            role_id=result[0]["RoleScheme"].role_id,
            role_name=result[0]["RoleScheme"].role_name,
            role_description=result[0]["RoleScheme"].role_description,
        )

    def fetch_role_by_id(self, role_id: int) -> Role | None:
        """
        Retrieves a single role by its ID and maps it to a Role domain model.

        Executes a SELECT query on the RoleScheme table using the provided role ID.
        If a matching record is found, it is converted into a Role object. If no
        result is found or the query fails, None is returned.

        Args:
            role_id (int): The unique identifier of the role to retrieve.

        Returns:
            Role | None: A Role object if a matching role is found; otherwise, None.

        """
        operation = select(RoleScheme).where(RoleScheme.role_id == role_id)
        result = self.database.run_query(operation)
        self.logger.info(result)

        if isinstance(result, bool) or result == []:
            return None

        return Role(
            role_id=result[0]["RoleScheme"].role_id,
            role_name=result[0]["RoleScheme"].role_name,
            role_description=result[0]["RoleScheme"].role_description,
        )

    def fetch_role_id_by_role_name(self, role_name: str) -> int | None:
        """
        Retrieve the role ID associated with the given role name.

        Args:
            role_name (str): The name of the role to search for.

        Returns:
            (int | None): The role ID if the role exists, otherwise None.

        """
        check_exist_statement = select(RoleScheme.role_id).where(RoleScheme.role_name == role_name)

        is_role_exist = self.database.run_query(check_exist_statement)
        self.logger.debug(is_role_exist)

        if isinstance(is_role_exist, list) and is_role_exist:
            return is_role_exist[0]["role_id"]

        return None

    def create_new_role(self, role_name: str, role_description: str) -> int:
        """
        Check if role already exist in database. If yes Create new role, else return the role
        Args:
            role_name (str): role name
            role_description (str): role description

        Returns:
            int | None: role id or None on error

        """
        existing_role_id = self.fetch_role_id_by_role_name(role_name)
        if existing_role_id:
            return existing_role_id

        insert_stmt = insert(RoleScheme).values(role_name=role_name, role_description=role_description)
        success = self.database.run_write(insert_stmt)

        if not success:
            msg = f"Failed to insert new role: {role_name}"
            raise RoleIDNotFoundError(msg)

        new_role_id = self.fetch_role_id_by_role_name(role_name)
        if new_role_id:
            self.logger.info("Created role: %s %s", new_role_id, role_name)
            return new_role_id

        msg = f"Failed to retrieve new role ID after creation: {role_name}"
        raise RoleIDNotFoundError(msg)

    def fetch_user_by_name(self, user_name: str) -> User | None:
        """
        Retrieves a user by their username and maps the result to a User domain model.

        Executes a SELECT query that joins user and role data based on the username.
        If a matching record is found, it is converted into a User object. If no
        result is found or the query fails, None is returned.

        Args:
            user_name (str): The username of the user to retrieve.

        Returns:
            User | None: A User object if a match is found; otherwise, None.

        """
        operation = select(
            UserScheme.user_id,
            RoleScheme.role_name,
            UserScheme.username,
            UserScheme.email,
        ).where(UserScheme.username == user_name)
        result = self.database.run_query(operation)
        self.logger.info(result)

        if isinstance(result, bool) or result == []:
            return None

        return User(
            user_id=result[0]["user_id"],
            user_name=result[0]["username"],
            email=result[0]["email"],
            role_name=result[0]["role_name"],
        )

    def fetch_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieves a user by their user ID and maps the result to a User domain model.

        Executes a SELECT query for the given user ID, returning user and role data.
        If a matching record is found, it is converted into a User object. If no
        result is found or the query fails, None is returned.

        Args:
            user_id (int): The unique identifier of the user to retrieve.

        Returns:
            User | None: A User object if a match is found; otherwise, None.

        """
        operation = select(
            UserScheme.user_id,
            RoleScheme.role_name,
            UserScheme.username,
            UserScheme.email,
        ).where(UserScheme.user_id == user_id)
        result = self.database.run_query(operation)
        self.logger.info(result)

        if isinstance(result, bool) or result == []:
            return None

        return User(
            user_id=result[0]["user_id"],
            user_name=result[0]["username"],
            email=result[0]["email"],
            role_name=result[0]["role_name"],
        )

    def create_new_user(self, role_id: int, user_name: str, hashed_password: str, email: str = "") -> int | None:
        """
        Creates a new user in the database and returns the newly assigned user ID.

        Executes an INSERT operation on the UserScheme table with the provided role ID,
        username, email, and hashed password. If successful, returns the user ID of the
        newly created user. If the transaction fails, returns None.

        Args:
            role_id (int): The ID of the role to associate with the new user.
            user_name (str): The username for the new user.
            hashed_password (str): The hashed password to store.
            email (str, optional): The user's email address. Defaults to an empty string.

        Returns:
            int | None: The user ID of the newly created user, or None if creation failed.

        """
        operation = (
            insert(UserScheme)
            .values(
                role_id=role_id,
                username=user_name,
                email=email,
                hashed_password=hashed_password,
            )
            .returning(UserScheme.user_id)
        )

        result = self.database.transaction(operation)
        self.logger.info(result)

        if isinstance(result, bool) or result == []:
            return None

        return result[0]["user_id"]

    def create_default_role_and_user(self, hashed_password: str) -> list[User]:
        """
        Create default roles and corresponding users in the system.

        This method initializes the database with two default roles: "ADMIN" and "USER",
        and creates one user account for each role using the provided hashed password.

        Args:
            hashed_password (str): The hashed password to assign to both default users.

        Returns:
            list[User]: A list containing the created admin and user objects.
                        Returns an empty list if any creation step fails.

        """
        admin_role_id = self.create_new_role("ADMIN", "ADMIN")
        user_role_id = self.create_new_role("USER", "USER")
        self.logger.info(admin_role_id)
        self.logger.info(user_role_id)

        admin_user_id = self.create_new_user(
            role_id=admin_role_id,
            user_name="admin",
            hashed_password=hashed_password,
            email="asd@asd.com",
        )
        user_user_id = self.create_new_user(
            role_id=user_role_id,
            user_name="user",
            hashed_password=hashed_password,
            email="asd@sad.com",
        )
        self.logger.info(admin_user_id)
        self.logger.info(user_user_id)

        if admin_user_id is None:
            return []
        if user_user_id is None:
            return []

        admin = self.fetch_user_by_id(user_id=admin_user_id)
        user = self.fetch_user_by_id(user_id=user_user_id)

        if admin is None:
            return []
        if user is None:
            return []

        return [admin, user]

    def fetch_user_hashed_password(self, user_id: int) -> str:
        """
        Retrieve the hashed password of a user by their user ID.

        This method queries the database for the hashed password associated with
        the given user ID.

        Args:
            user_id (int): The ID of the user whose password is to be fetched.

        Returns:
            str: The hashed password if found, otherwise an empty string.

        """
        operation = select(UserScheme.hashed_password).where(
            UserScheme.user_id == user_id,
        )

        result = self.database.run_query(operation)
        self.logger.info(result)

        return result[0]["hashed_password"] if result else ""

    def login(
        self,
        user_id: int,
        access_token: str,
        refresh_token: str,
        access_token_expires_ttl: datetime.timedelta,
        refresh_token_expires_ttl: datetime.timedelta,
    ) -> bool:
        """
        Store a user's login session in the database with access and refresh tokens.

        This method inserts a new record into the login table with token information
        and their respective expiration timestamps.

        Args:
            user_id (int): The ID of the authenticated user.
            access_token (str): The generated JWT access token.
            refresh_token (str): The generated JWT refresh token.
            access_token_expires_ttl (datetime.timedelta): Time-to-live duration for the access token.
            refresh_token_expires_ttl (datetime.timedelta): Time-to-live duration for the refresh token.

        Returns:
            bool: True if the insertion failed (no rows affected), False if the login session was recorded successfully.

        """
        current_time = datetime.datetime.now(datetime.timezone.utc)
        operation = (
            PostgresqlInsert(LoginScheme)
            .values(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                access_token_expires_at=current_time + access_token_expires_ttl,
                refresh_token_expires_at=current_time + refresh_token_expires_ttl,
            )
            .on_conflict_do_update(
                index_elements=[LoginScheme.user_id],
                set_={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "access_token_expires_at": current_time + access_token_expires_ttl,
                    "refresh_token_expires_at": current_time + refresh_token_expires_ttl,
                },
            )
        )
        result = self.database.run_query(operation)
        return result == []

    def logout(self, user_id: int) -> bool:
        """
        Log out a user by deleting their login session from the database.

        This method removes the user's access and refresh tokens from the login table,
        effectively revoking their session.

        Args:
            user_id (int): The ID of the user to log out.

        Returns:
            bool: True if no session existed (i.e., nothing was deleted), False if a session was successfully deleted.

        """
        operation = delete(LoginScheme).where(
            LoginScheme.user_id == user_id,
        )

        result = self.database.run_query(operation)
        self.logger.info(result)
        return result == []

    def fetch_refresh_token(self, user_id: int) -> str:
        operation = select(LoginScheme.refresh_token).where(
            LoginScheme.user_id == user_id,
        )
        result = self.database.run_query(operation)
        self.logger.info(result)
        return result[0]["refresh_token"] if result else ""

    def revoke_access_token(self, user_id: int) -> bool:
        operation = (
            update(LoginScheme)
            .where(
                LoginScheme.user_id == user_id,
            )
            .values(access_token="")
        )
        result = self.database.run_query(operation)

        return result != []

    def update_refresh_token(self, user_id: int, refresh_token: str) -> bool:
        operation = (
            update(LoginScheme)
            .where(
                LoginScheme.user_id == user_id,
            )
            .values(refresh_token=refresh_token)
        )
        result = self.database.run_query(operation)
        self.logger.info(result)
        return result != []

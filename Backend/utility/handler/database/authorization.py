# Code by AkinoAlice@TyrantRey
from __future__ import annotations

from passlib.context import CryptContext
from sqlalchemy import delete, insert, select, update

from Backend.utility.error.database import RoleIDNotFoundError
from Backend.utility.model.application.auth.authorization import Role, User
from Backend.utility.model.handler.database.scheme import PatentScheme, RoleScheme, UserScheme

from .database import Database


class AuthorizationOperation(Database):
    def __init__(self):
        super().__init__()

    def fetch_all_role(self) -> list[Role]:
        operation = select(RoleScheme)
        result = self.run_query(operation)
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
        operation = select(RoleScheme).where(RoleScheme.role_name == role_name)
        result = self.run_query(operation)
        self.logger.info(result)

        if isinstance(result, bool) or result == []:
            return None

        return Role(
            role_id=result[0]["RoleScheme"].role_id,
            role_name=result[0]["RoleScheme"].role_name,
            role_description=result[0]["RoleScheme"].role_description,
        )

    def fetch_role_by_id(self, role_id: int) -> Role | None:
        operation = select(RoleScheme).where(RoleScheme.role_id == role_id)
        result = self.run_query(operation)
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

        is_role_exist = self.run_query(check_exist_statement)
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
        success = self.run_write(insert_stmt)

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
        operation = select(UserScheme.user_id, RoleScheme.role_name, UserScheme.username, UserScheme.email).where(
            UserScheme.username == user_name
        )
        result = self.run_query(operation)
        self.logger.info(result)

        if isinstance(result, bool) or result == []:
            return None

        return User(
            user_id=result[0]["RoleScheme"].user_id,
            user_name=result[0]["RoleScheme"].user_name,
            email=result[0]["RoleScheme"].email,
            role_name=result[0]["RoleScheme"].role_name,
        )

    def fetch_user_by_id(self, user_id: int) -> User | None:
        operation = select(UserScheme.user_id, RoleScheme.role_name, UserScheme.username, UserScheme.email).where(
            UserScheme.user_id == user_id
        )
        result = self.run_query(operation)
        self.logger.info(result)

        if isinstance(result, bool) or result == []:
            return None

        return User(
            user_id=result[0]["RoleScheme"].user_id,
            user_name=result[0]["RoleScheme"].user_name,
            email=result[0]["RoleScheme"].email,
            role_name=result[0]["RoleScheme"].role_name,
        )

    def create_new_user(self, role_id: int, user_name: str, hashed_password: str, email: str = "") -> int | None:
        """
        Registers a new user with the given role.
        If the role does not exist in the database, it is created.

        """

        # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # hashed_password = pwd_context.hash(password)

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

        result = self.transaction(operation)
        self.logger.info(result)

        if isinstance(result, bool) or result == []:
            return None

        return result[0]["user_id"]

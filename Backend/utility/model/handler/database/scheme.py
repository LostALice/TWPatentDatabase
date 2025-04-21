# Code by AkinoAlice@TyrantRey

import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseScheme(DeclarativeBase): ...


class RoleScheme(BaseScheme):
    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    role_description: Mapped[str]

    def __repr__(self):
        return f"<Role(id={self.role_id}, role_name='{self.role_name}')>"


class UserScheme(BaseScheme):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id", ondelete="CASCADE"))
    username: Mapped[str] = mapped_column(String(10), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}', email='{self.email}')>"


class LoginScheme(BaseScheme):
    __tablename__ = "logins"

    login_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    access_token: Mapped[str] = mapped_column(String(512), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(512), nullable=False)
    access_token_created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    access_token_expires_at: Mapped[datetime.timedelta] = mapped_column(DateTime)
    refresh_token_created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    refresh_token_expires_at: Mapped[datetime.timedelta] = mapped_column(DateTime)

    user = relationship("UserScheme", backref="logins")


class PatentScheme(BaseScheme):
    __tablename__ = "patent"

    # SERIAL PRIMARY KEY in PostgreSQL
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column()
    application_date: Mapped[int] = mapped_column(Integer)
    publication_date: Mapped[int] = mapped_column(Integer)
    application_number: Mapped[str] = mapped_column(String(100))
    publication_number: Mapped[str] = mapped_column(String(100))
    applicant: Mapped[str] = mapped_column(Text)
    inventor: Mapped[str] = mapped_column(Text)
    attorney: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(Text)
    gazette_ipc: Mapped[str] = mapped_column(Text)
    ipc: Mapped[str] = mapped_column(Text)
    gazette_volume: Mapped[str] = mapped_column(Text)
    kind_codes: Mapped[str] = mapped_column(Text)
    patent_url: Mapped[str] = mapped_column(Text)
    patent_file_path: Mapped[str] = mapped_column(Text)

    search_vector = mapped_column(TSVECTOR)

    def __repr__(self):
        return f"<Patent(id={self.id}, application_number='{self.application_number}')>"

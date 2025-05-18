# Code by AkinoAlice@TyrantRey

import datetime

from pgvector.sqlalchemy import Vector  # type: ignore[import-untyped]
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
    __table_args__ = (UniqueConstraint("user_id", name="uq_logins_user_id"),)

    login_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True
    )
    access_token: Mapped[str] = mapped_column(String(512), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(512), nullable=False)

    access_token_created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    access_token_expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    refresh_token_created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    refresh_token_expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # user = relationship("UserScheme", backref="logins")

    def __repr__(self):
        return (
            f"<Login(user_id={self.user_id}, "
            f"access_expires={self.access_token_expires_at}, "
            f"refresh_expires={self.refresh_token_expires_at})>"
        )


class PatentScheme(BaseScheme):
    __tablename__ = "patent"

    # SERIAL PRIMARY KEY in PostgreSQL
    patent_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
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


class ContentVectorScheme(BaseScheme):
    __tablename__ = "patent_content_vector"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patent_id: Mapped[int] = mapped_column(ForeignKey("patent.patent_id", ondelete="CASCADE"), nullable=False)
    page: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[int] = mapped_column(Vector(1536), nullable=False)


class ImageVectorScheme(BaseScheme):
    __tablename__ = "patent_image_vector"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patent_id: Mapped[int] = mapped_column(ForeignKey("patent.patent_id", ondelete="CASCADE"), nullable=False)
    page: Mapped[int] = mapped_column(Integer, nullable=False)
    image_path: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[int] = mapped_column(Vector(768), nullable=False)


class ResponseHistoryScheme(BaseScheme):
    __tablename__ = "response"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    token: Mapped[int] = mapped_column(Integer)
    query_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=func.now(), index=True)

    # user = relationship("UserScheme", backref="history")

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, user_id={self.user_id}, time={self.query_time})>"


class SearchHistoryScheme(BaseScheme):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    patent_id: Mapped[int] = mapped_column(
        ForeignKey("patent.patent_id", ondelete="CASCADE"),
        nullable=False,
    )
    keyword: Mapped[str] = mapped_column(Text, nullable=False)
    search_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=func.now(), index=True)

    # user = relationship("UserScheme", backref="history")
    # patent = relationship("PatentScheme", backref="history")

    def __repr__(self):
        return (
            f"<SearchHistory(id={self.id}, user_id={self.user_id}, "
            f"keyword={self.keyword!r}, patent_id={self.patent_id}, "
            f"time={self.search_time})>"
        )

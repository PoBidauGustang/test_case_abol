import uuid
from datetime import datetime
from typing import Annotated

from pydantic import SecretStr
from sqlalchemy import Boolean, DateTime, String, false, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from werkzeug.security import generate_password_hash

uuid_pk = Annotated[
    str,
    mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    ),
]
created_at = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"), nullable=False
    ),
]
updated_at = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        onupdate=text("NOW()"),
    ),
]

published_date = Annotated[
    datetime, mapped_column(DateTime(timezone=True), nullable=True)
]


class BaseEntity:
    """Class for base model with standard fields for all models."""

    uuid: Mapped[uuid_pk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    def __pepr__(self):
        return f"{self.__class__.__name__}(uuid={self.uuid})"


Entity = declarative_base(cls=BaseEntity)


class Book(Entity):
    __tablename__ = "books"

    title: Mapped[str] = mapped_column(String(64), unique=True)
    author: Mapped[str | None] = mapped_column(String(64))
    published_date: Mapped[published_date]


class User(Entity):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(64), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    username: Mapped[str | None] = mapped_column(String(64), unique=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, server_default=false())

    def __init__(
        self,
        email: str,
        password: SecretStr,
        username: str,
        is_superuser: bool = False,
    ) -> None:
        self.email = email
        self.password = generate_password_hash(password)
        self.username = username
        self.is_superuser = is_superuser

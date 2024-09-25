from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.entities import Entity

published_date = Annotated[
    datetime, mapped_column(DateTime(timezone=True), nullable=True)
]


class Book(Entity):
    __tablename__ = "books"

    title: Mapped[str] = mapped_column(String(64), unique=True)
    author: Mapped[str | None] = mapped_column(String(64))
    published_date: Mapped[published_date]

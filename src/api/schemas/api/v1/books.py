from datetime import datetime

from pydantic import BaseModel, Field

from src.api.schemas.api.v1.base import (
    TimeMixin,
    UUIDMixin,
)
from src.utils.pagination import PaginatedMixin


class Book(BaseModel):
    title: str = Field(
        description="Наименование книги",
        examples=["Гарри Поттер и кубок огня"],
        min_length=1,
        max_length=64,
    )
    author: str = Field(
        description="Имя автора",
        examples=["Д.К. Роулинг"],
        min_length=1,
        max_length=64,
    )
    published_date: datetime = Field(
        description="Дата публикации книги",
        examples=["2022-01-15"],
    )


class ResponseBook(Book, UUIDMixin, TimeMixin):
    class Meta:
        abstract = True


class ResponseBooksPaginated(PaginatedMixin):
    books: list[ResponseBook]


class RequestBookCreate(Book): ...


class RequestBookUpdate(BaseModel):
    author: str = Field(
        description="Имя автора",
        examples=["Д.Р.Р. Толкин"],
        min_length=1,
        max_length=64,
    )
    published_date: datetime = Field(
        description="Дата публикации книги",
        examples=["1894-05-11"],
    )

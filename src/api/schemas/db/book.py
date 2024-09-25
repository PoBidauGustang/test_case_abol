from datetime import datetime

from pydantic import Field

from src.api.schemas.db.base import BaseMixin


class BookDB(BaseMixin):
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
        examples=["2024-04-19"],
    )

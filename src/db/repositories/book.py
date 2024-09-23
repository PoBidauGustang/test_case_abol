from functools import lru_cache

from fastapi import Depends

from src.api.schemas.api.v1.books import (
    RequestBookCreate,
    RequestBookUpdate,
)
from src.db.clients.postgres import (
    PostgresDatabase,
    get_postgres_db,
)
from src.db.entities import Book
from src.db.repositories.base import PostgresRepository


class BookRepository(
    PostgresRepository[
        Book,
        RequestBookCreate,
        RequestBookUpdate,
    ],
): ...


@lru_cache
def get_book_repository(
    database: PostgresDatabase = Depends(get_postgres_db),
) -> BookRepository:
    return BookRepository(database, Book)

from functools import lru_cache

from fastapi import Depends

from src.api.schemas.api.v1.books import (
    RequestBookCreate,
    RequestBookUpdate,
    ResponseBooksPaginated,
)
from src.api.schemas.db.book import BookDB
from src.api.services.base import BaseService
from src.db.repositories.book import BookRepository, get_book_repository


class BookService(
    BaseService[
        BookDB,
        ResponseBooksPaginated,
        RequestBookCreate,
        RequestBookUpdate,
    ]
):
    pass


@lru_cache
def get_book_service(
    repository: BookRepository = Depends(get_book_repository),
) -> BookService:
    return BookService(repository, BookDB)

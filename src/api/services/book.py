from functools import lru_cache

from fastapi import Depends
from faststream.rabbit import RabbitBroker

from src.api.brokers.rabbitmq import get_rabbit_broker
from src.api.schemas.api.v1.books import (
    RequestBookCreate,
    RequestBookUpdate,
    ResponseBooksPaginated,
)
from src.api.schemas.db.book import BookDB
from src.api.services.base import BaseService
from src.cache.redis import RedisCache, get_redis
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
    cache: RedisCache = Depends(get_redis),
    broker: RabbitBroker = Depends(get_rabbit_broker),
) -> BookService:
    return BookService(repository, BookDB, cache, broker)

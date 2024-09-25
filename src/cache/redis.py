import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from redis.asyncio import Redis

from src.cache.abstract import AbstractCache
from src.utils.retry_decorator import retry

logger = logging.getLogger("RedisCache")


class RedisCache(AbstractCache):
    def __init__(self, cache: Redis):
        self.__cache = cache

    async def close(self) -> None:
        """
        Close the connection with Redis.
        """
        await self.__cache.aclose()
        logger.info("Connection to Redis was closed.")

    @retry(exceptions=(ConnectionError,))
    async def ping(self) -> Any:
        """
        Ping the Redis server to ensure the connection is still alive.
        """
        return await self.__cache.ping()

    @retry(exceptions=(ConnectionError,))
    async def get(self, key: str):
        return await self.__cache.get(key)

    @retry(exceptions=(ConnectionError,))
    async def set(self, key: str, value: str, expire: int = 600):
        await self.__cache.set(key, value, expire)

    def generate_cache_key(
        self, service_name: str, method_name: str, *args: Any, **kwargs: Any
    ) -> str:
        key = f"{service_name}:{method_name}:"
        if args:
            key += ":".join(str(arg) for arg in args)
        if kwargs:
            key += ":" + ":".join(f"{k}={v}" for k, v in kwargs.items())
        return key

    @staticmethod
    def make_serializable(data: Any) -> Any:
        match data:
            case dict():
                return {
                    key: RedisCache.make_serializable(value)
                    for key, value in data.items()
                }
            case list():
                return [RedisCache.make_serializable(item) for item in data]
            case UUID():
                return str(data)
            case datetime():
                return data.isoformat()
            case _:
                return data


redis: RedisCache | None = None


async def get_redis() -> RedisCache | None:
    return redis

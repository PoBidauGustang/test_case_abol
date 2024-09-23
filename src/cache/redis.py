import logging
from typing import Any

from redis.asyncio import Redis

from src.cache.abstract import AbstractCache

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

    async def ping(self) -> Any:
        """
        Ping the Redis server to ensure the connection is still alive.
        """
        return await self.__cache.ping()

    async def set_data(
        self,
    ) -> None:
        """
        Set data in the cache.

        Args:
            any.
        """
        ...


redis: RedisCache | None = None


async def get_redis() -> RedisCache | None:
    return redis

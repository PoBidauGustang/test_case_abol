from abc import ABC, abstractmethod
from typing import Any


class AbstractCache(ABC):
    @abstractmethod
    async def set(
        self,
        key: str,
        value: str,
        expire: int = 600,
    ) -> None:
        """
        Set data in the cache.

        Args:
            key (str): The key to use for caching the data.
            value (str): The data to cache.
            expire (int): time for data expiration
        """
        raise NotImplementedError

    @abstractmethod
    async def get(self, key: str):
        """
        Get data from the cache.

        Args:
            key (str): The key used for caching the data.

        Returns:
            The cached data, or None if the data are not in the cache.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_cache_key(
        self, service_name: str, method_name: str, *args: Any, **kwargs: Any
    ) -> str:
        """
        Generate a unique key for the cache based on the service name (class name),
        method name and passed parameters.

        Args:
            service_name (str): The name of the service to build key.
            method_name (str): The name of the method to build key.
            *args (Any): Tuple of arguments to build key.
            **kwargs (Any): Keyword arguments to build key.

        Returns:
            key: Generated key for caching.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def make_serializable(data: Any) -> Any:
        """
        Recursively converts UUID and datetime objects to strings.
        Supports conversion of dictionaries, lists, and nested data structures.
        """
        raise NotImplementedError

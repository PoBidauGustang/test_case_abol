from abc import ABC, abstractmethod


class AbstractCache(ABC):
    @abstractmethod
    async def set_data(
        self,
    ) -> None:
        """
        Set data in the cache.

        Args:
            any.
        """
        raise NotImplementedError

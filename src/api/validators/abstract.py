from abc import ABC, abstractmethod
from uuid import UUID


class AbstractValidator(ABC):
    @abstractmethod
    async def is_exists(self, instance_uuid: UUID) -> UUID:
        raise NotImplementedError

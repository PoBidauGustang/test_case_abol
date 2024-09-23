from typing import Generic, TypeVar
from uuid import UUID

from fastapi import HTTPException

from src.api.validators.abstract import AbstractValidator
from src.db.repositories.abstract import AbstractRepository

Repository = TypeVar("Repository", bound=AbstractRepository)


class InitValidator:
    def __init__(self, repository: Repository):
        self._repository: Repository = repository


class BaseValidator(InitValidator, AbstractValidator, Generic[Repository]):
    async def is_exists(self, instance_uuid: UUID) -> UUID:
        instance = await self._repository.get(instance_uuid)
        if instance is None:
            raise HTTPException(
                status_code=404,
                detail=f"The object with uuid='{instance_uuid}' was not found",
            )
        return instance_uuid

from typing import TypeVar

from fastapi import Depends, HTTPException

from src.api.validators import InitValidator
from src.db.repositories.abstract import AbstractRepository
from src.db.repositories.user import get_user_repository

Repository = TypeVar("Repository", bound=AbstractRepository)


class DuplicateEmailValidatorMixin(InitValidator):
    async def is_duplicate_email(self, email: str) -> None:
        user_uuid = await self._repository.get_uuid_filter_by(email=email)
        if user_uuid is not None:
            raise HTTPException(
                status_code=400,
                detail=f"The user with email='{email}'already exists",
            )


class DuplicateUsernamelValidatorMixin(InitValidator):
    async def is_duplicate_username(self, username: str) -> None:
        user_uuid = await self._repository.get_uuid_filter_by(username=username)
        if user_uuid is not None:
            raise HTTPException(
                status_code=400,
                detail=f"The user with username='{username}'already exists",
            )


class UserValidator(
    DuplicateEmailValidatorMixin, DuplicateUsernamelValidatorMixin
):
    pass


def get_user_validator(
    repository: Repository = Depends(get_user_repository),
) -> UserValidator:
    return UserValidator(repository)

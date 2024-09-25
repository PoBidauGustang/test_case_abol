from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path

from src.api.validators import BaseValidator, InitValidator
from src.db.repositories.book import BookRepository, get_book_repository


class DuplicateTitleValidatorMixin(InitValidator):
    async def is_duplicate_title(self, title: str) -> None:
        book_uuid = await self._repository.get_uuid_filter_by(title=title)
        if book_uuid is not None:
            raise HTTPException(
                status_code=400,
                detail=f"The book with title='{title}'already exists",
            )


class BookValidator(
    BaseValidator[BookRepository], DuplicateTitleValidatorMixin
):
    pass


def get_book_validator(
    repository: BookRepository = Depends(get_book_repository),
) -> BookValidator:
    return BookValidator(repository)


book_uuid_annotation = Annotated[
    UUID,
    Path(
        alias="book_uuid",
        title="book uuid",
        description="The UUID of the book",
        example="28097f5b-249a-4ca5-9d73-448bd967ab4b",
    ),
]

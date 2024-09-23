from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.schemas.api.v1.base import StringRepresent
from src.api.schemas.api.v1.books import (
    RequestBookCreate,
    RequestBookUpdate,
    ResponseBook,
    ResponseBooksPaginated,
)
from src.api.services.book import BookService, get_book_service
from src.api.validators.book import (
    BookValidator,
    book_uuid_annotation,
    get_book_validator,
)
from src.utils.pagination import Paginator, get_paginator

router = APIRouter()


@router.get(
    "/",
    response_model=ResponseBooksPaginated,
    summary="Get a list of books",
)
async def get_books(
    request: Request,
    books_service: BookService = Depends(get_book_service),
    paginator: Paginator = Depends(get_paginator),
) -> ResponseBooksPaginated:
    """Available to authorized users

    Get a list of books

    Args:
    - **page_number** (str): The number of the page to get
    - **page_size** (str): The size of the page to get
    Returns:
    - **ResponseBooksPaginated**: The list of books: list[ResponseBook]
    """
    paginated_data = await paginator(
        books_service,
        "get_all",
    )
    if not paginated_data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="books not found"
        )
    return ResponseBooksPaginated(
        count=paginated_data.count,
        total_pages=paginated_data.total_pages,
        prev=paginated_data.prev,
        next=paginated_data.next,
        books=[
            ResponseBook(
                uuid=book.uuid,
                title=book.title,
                author=book.author,
                published_date=book.published_date,
                created_at=book.created_at,
                updated_at=book.updated_at,
            )
            for book in paginated_data.results
        ],
    )


@router.get(
    "/{book_uuid}/",
    response_model=ResponseBook,
    response_model_exclude_none=True,
    summary="Get a book details by uuid",
)
async def get_book(
    request: Request,
    book_uuid: book_uuid_annotation,
    books_service: BookService = Depends(get_book_service),
) -> ResponseBook:
    """Available to authorized users

    Get a book details by uuid

    Args:
    - **book_uuid** (str): The UUID of the book to get

    Returns:
    - **ResponseBook**: The book details
    """
    book = await books_service.get(book_uuid)
    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="book not found"
        )
    return book


@router.post(
    "/",
    response_model=ResponseBook,
    response_model_exclude_none=True,
    summary="Create a book",
)
async def create_book(
    request: Request,
    body: RequestBookCreate,
    books_service: BookService = Depends(get_book_service),
    book_validator: BookValidator = Depends(get_book_validator),
) -> ResponseBook:
    """Only available to administrator

    Create a book

    Returns:
    - **ResponseBook**: The book details
    """
    await book_validator.is_duplicate_title(body.title)
    book = await books_service.create(body)
    return book


@router.patch(
    "/{book_uuid}/",
    response_model=ResponseBook,
    response_model_exclude_none=True,
    summary="Change the book by uuid",
)
async def update_book(
    request: Request,
    book_uuid: book_uuid_annotation,
    body: RequestBookUpdate,
    books_service: BookService = Depends(get_book_service),
    book_validator: BookValidator = Depends(get_book_validator),
) -> ResponseBook:
    """Only available to administrator

    Change the book by uuid

    Args:
    - **book_uuid** (str): The UUID of the book to change

    Returns:
    - **ResponseBook**: The book details
    """
    book = await books_service.update(
        await book_validator.is_exists(book_uuid), body
    )
    return book


@router.delete(
    "/{book_uuid}/",
    response_model=StringRepresent,
    summary="Delete the book by uuid",
)
async def remove_book(
    request: Request,
    book_uuid: book_uuid_annotation,
    books_service: BookService = Depends(get_book_service),
    book_validator: BookValidator = Depends(get_book_validator),
) -> StringRepresent:
    """Only available to administrator

    Delete the book by uuid

    Args:
    - **book_uuid** (str): The UUID of the book to delete

    Returns:
    - **StringRepresent**: Status code with message "Book deleted successfully"
    """
    await books_service.remove(await book_validator.is_exists(book_uuid))
    return StringRepresent(
        code=HTTPStatus.OK, details="Book deleted successfully"
    )

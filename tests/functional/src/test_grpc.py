from datetime import datetime

import pytest
from grpc.aio import insecure_channel

from tests.functional.settings import settings
from tests.utils import books_pb2, books_pb2_grpc


@pytest.mark.asyncio
async def test_grpc_get_book(create_book):
    published_date = datetime.strptime("2020-01-01", "%Y-%m-%d")
    book = await create_book(
        title="Test Book", author="Test Author", published_date=published_date
    )

    async with insecure_channel(settings.get_grpc_server_host) as channel:
        client = books_pb2_grpc.BookServiceStub(channel)
        response = await client.GetBookById(
            books_pb2.BookIdRequest(uuid=str(book.uuid))
        )
        assert response.uuid == str(book.uuid)
        assert response.title == "Test Book"


@pytest.mark.asyncio
async def test_grpc_get_all_books(create_book):
    published_date_1 = datetime.strptime("2021-01-01", "%Y-%m-%d")
    published_date_2 = datetime.strptime("2022-01-01", "%Y-%m-%d")
    await create_book(
        title="Test Book 1", author="Author 1", published_date=published_date_1
    )
    await create_book(
        title="Test Book 2", author="Author 2", published_date=published_date_2
    )

    async with insecure_channel(settings.get_grpc_server_host) as channel:
        client = books_pb2_grpc.BookServiceStub(channel)
        response = await client.GetAllBooks(books_pb2.Empty())
        assert len(response.books) == 2

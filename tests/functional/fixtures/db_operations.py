from http import HTTPStatus
from typing import Any

import pytest
import pytest_asyncio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from tests.models import Book, User


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clear_cache(redis_client: Redis):
    await redis_client.flushdb(asynchronous=True)


@pytest.fixture
def generate_cache_key():
    def inner(
        service_name: str, method_name: str, *args: Any, **kwargs: Any
    ) -> str:
        key = f"{service_name}:{method_name}:"
        if args:
            key += ":".join(str(arg) for arg in args)
        if kwargs:
            key += ":" + ":".join(f"{k}={v}" for k, v in kwargs.items())
        return key

    return inner


@pytest_asyncio.fixture
async def check_cache(redis_client: Redis, generate_cache_key):
    async def inner(
        service_name: str, method_name: str, *args: Any, **kwargs: Any
    ) -> Any:
        key = generate_cache_key(service_name, method_name, *args, **kwargs)
        data = await redis_client.get(key)
        return data

    return inner


@pytest_asyncio.fixture
async def create_user(db_session: AsyncSession):
    async def inner(
        email: str, password: str, username: str, is_admin: bool = False
    ) -> User:
        user = User(
            email=email,
            password=password,
            username=username,
            is_superuser=is_admin,
        )
        db_session.add(user)
        await db_session.commit()
        return user

    return inner


@pytest_asyncio.fixture
async def create_book(db_session: AsyncSession):
    async def inner(title: str, author: str, published_date: str) -> Book:
        book = Book(title=title, author=author, published_date=published_date)
        db_session.add(book)
        await db_session.commit()
        await db_session.refresh(book)
        return book

    return inner


@pytest_asyncio.fixture
async def get_access_token(make_post_request):
    async def inner(username: str, password: str) -> str:
        path = "/users/token"
        login_data = {
            "username": username,
            "password": password,
        }
        body, status, _ = await make_post_request(path=path, data=login_data)
        assert status == HTTPStatus.OK
        assert "access_token" in body
        return body["access_token"]

    return inner

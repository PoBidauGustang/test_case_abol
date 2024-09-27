import asyncio

import aiohttp
import pytest
import pytest_asyncio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from tests.functional.settings import postgres_settings, settings
from tests.models import Entity


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


db_url = postgres_settings.postgres_connection_url
engine = create_async_engine(
    postgres_settings.postgres_connection_url,
    echo=postgres_settings.sqlalchemy_echo,
)
AsyncSessionFactory = async_sessionmaker(bind=engine, class_=AsyncSession)


@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionFactory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Entity.metadata.drop_all)
        await conn.run_sync(Entity.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Entity.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def redis_client():
    client = Redis(**settings.get_redis_host)
    yield client
    await client.aclose()


@pytest_asyncio.fixture(scope="session")
async def http_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()

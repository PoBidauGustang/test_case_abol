import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

load_dotenv(".env")

logger = logging.getLogger(__name__)


postgres_user = os.environ.get("POSTGRES_USER")
postgres_pass = os.environ.get("POSTGRES_PASSWORD")
postgres_host = os.environ.get("POSTGRES_HOST")
postgres_port = os.environ.get("POSTGRES_PORT")
postgres_db = os.environ.get("POSTGRES_DB")

DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{postgres_user}:{postgres_pass}@"
    f"{postgres_host}:{postgres_port}/"
    f"{postgres_db}"
)


class PostgresDatabase:
    def __init__(self) -> None:
        self._async_session_factory = async_sessionmaker(
            create_async_engine(DATABASE_URL, echo=True)
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        try:
            session = self._async_session_factory()
            logger.info("==> Session open")
            yield session
        except Exception as error:
            logger.error("==> Session rollback because of exception", error)
            await session.rollback()
            raise
        finally:
            logger.info("==> Session close")
            await session.close()


def get_db():
    return PostgresDatabase()

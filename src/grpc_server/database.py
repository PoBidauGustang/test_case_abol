from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

DATABASE_URL = "postgresql+asyncpg://app:123qwe@postgres:5432/db_book"

# engine = create_async_engine(DATABASE_URL, echo=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# async def get_db():
#     async with SessionLocal() as session:
#         yield session


class PostgresDatabase:
    def __init__(self) -> None:
        self._async_session_factory = async_sessionmaker(
            create_async_engine(DATABASE_URL, echo=True)
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        try:
            session = self._async_session_factory()
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db():
    return PostgresDatabase()

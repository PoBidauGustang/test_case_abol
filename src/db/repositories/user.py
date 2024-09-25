from functools import lru_cache

from fastapi import Depends
from sqlalchemy import select

from src.api.schemas.api.v1.users import (
    RequestUserCreate,
)
from src.db.clients.postgres import (
    PostgresDatabase,
    get_postgres_db,
)
from src.db.entities import User
from src.db.repositories.abstract import (
    ModelType,
)
from src.db.repositories.base import PostgresRepositoryCD


class UserRepository(
    PostgresRepositoryCD[User, RequestUserCreate],
):
    async def get_by_username(self, username: str) -> ModelType | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(self._model).filter_by(**{"username": username})
            )
            return db_obj.scalars().first()

    async def get_uuid_filter_by(self, **kwargs) -> str | None:
        if not kwargs:
            raise ValueError("Filter by is empty")
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(self._model.uuid).filter_by(**kwargs)
            )
            obj_uuid = db_obj.scalars().first()
            return obj_uuid


@lru_cache
def get_user_repository(
    database: PostgresDatabase = Depends(get_postgres_db),
) -> UserRepository:
    return UserRepository(database, User)

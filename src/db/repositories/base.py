from typing import Any, Generic
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, func, select

from src.db.clients.postgres import PostgresDatabase
from src.db.repositories.abstract import (
    AbstractRepository,
    AbstractRepositoryCD,
    AbstractRepositoryCRD,
    CreateSchemaType,
    ModelType,
    UpdateSchemaType,
)
from src.utils.retry_decorator import retry


class InitRepository:
    def __init__(self, database: PostgresDatabase, model: type[ModelType]):
        self._database = database
        self._model = model


class PostgresRepositoryCD(
    InitRepository,
    AbstractRepositoryCD,
    Generic[ModelType, CreateSchemaType],
):
    @retry(exceptions=(ConnectionError,))
    async def create(self, instance: CreateSchemaType) -> ModelType:
        async with self._database.get_session() as session:
            db_obj = self._model(**instance.dict())
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    @retry(exceptions=(ConnectionError,))
    async def remove(self, instance_uuid: UUID, **kwargs) -> UUID:
        async with self._database.get_session() as session:
            await session.execute(
                delete(self._model).where(self._model.uuid == instance_uuid)
            )
            await session.commit()
            return instance_uuid


class PostgresRepositoryCRD(
    PostgresRepositoryCD[ModelType, CreateSchemaType],
    AbstractRepositoryCRD,
    Generic[ModelType, CreateSchemaType],
):
    @retry(exceptions=(ConnectionError,))
    async def get_all(self, **kwargs) -> list[ModelType]:
        limit = kwargs.get("limit")
        offset = kwargs.get("offset")
        async with self._database.get_session() as session:
            query = select(self._model)
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            db_obj = await session.execute(query)
            return db_obj.scalars().all()

    @retry(exceptions=(ConnectionError,))
    async def get(self, instance_uuid: UUID, **kwargs) -> ModelType | Any:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(self._model).where(self._model.uuid == instance_uuid)
            )
            return db_obj.scalars().first()


class PostgresRepository(
    PostgresRepositoryCRD[ModelType, CreateSchemaType],
    AbstractRepository,
    Generic[ModelType, CreateSchemaType, UpdateSchemaType],
):
    @retry(exceptions=(ConnectionError,))
    async def update(
        self, instance_uuid: UUID, instance: UpdateSchemaType
    ) -> ModelType:
        async with self._database.get_session() as session:
            db_obj = await self.get(instance_uuid)

            obj_data = jsonable_encoder(db_obj)
            update_data = instance.dict(exclude_unset=True)

            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def count(self) -> int | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(func.count()).select_from(self._model)
            )
            return db_obj.scalars().first()

    @retry(exceptions=(ConnectionError,))
    async def get_uuid_filter_by(self, **kwargs) -> str | None:
        if not kwargs:
            raise ValueError("Filter by is empty")
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(self._model.uuid).filter_by(**kwargs)
            )
            obj_uuid = db_obj.scalars().first()
            return obj_uuid

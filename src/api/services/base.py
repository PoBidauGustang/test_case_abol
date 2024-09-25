import json
from typing import Generic, TypeVar
from uuid import UUID

from faststream.rabbit import RabbitBroker
from pydantic import BaseModel

from src.cache.abstract import AbstractCache
from src.db.repositories.abstract import AbstractRepository

DBSchemaType = TypeVar("DBSchemaType", bound=BaseModel)
DBSchemaPaginationType = TypeVar("DBSchemaPaginationType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class InitService:
    _model: BaseModel

    def __init__(self, repository: AbstractRepository, model: type[BaseModel]):
        self._repository = repository
        self._model = model


class BaseService(
    InitService,
    Generic[
        DBSchemaType, DBSchemaPaginationType, CreateSchemaType, UpdateSchemaType
    ],
):
    def __init__(
        self,
        repository: AbstractRepository,
        model: type[BaseModel],
        cache: AbstractCache,
        broker: RabbitBroker,
    ):
        super().__init__(repository, model)
        self._cache = cache
        self._service_name = self.__class__.__name__.lower()
        self._broker = broker

    async def get(self, instance_uuid: UUID) -> DBSchemaType | None:
        cache_key = self._cache.generate_cache_key("get", str(instance_uuid))
        cached_data = await self._cache.get(cache_key)
        if cached_data:
            return self._model.model_validate(json.loads(cached_data))

        obj = await self._repository.get(instance_uuid)
        if obj is None:
            return None
        model = self._model.model_validate(obj, from_attributes=True)

        serializable_data = self._cache.make_serializable(model.model_dump())
        await self._cache.set(cache_key, json.dumps(serializable_data))

        return model

    async def get_all(self, **kwargs) -> list[DBSchemaType] | None:
        cache_key = self._cache.generate_cache_key(
            service_name=self._service_name, method_name="get_all", **kwargs
        )
        cached_data = await self._cache.get(cache_key)
        if cached_data:
            return [
                self._model.model_validate(obj)
                for obj in json.loads(cached_data)
            ]

        objs: list[BaseModel] = await self._repository.get_all(**kwargs)
        if objs is None:
            return None
        models = [
            self._model.model_validate(obj, from_attributes=True)
            for obj in objs
        ]

        serializable_data = [
            self._cache.make_serializable(model.model_dump())
            for model in models
        ]
        await self._cache.set(cache_key, json.dumps(serializable_data))

        return models

    async def create(self, obj: CreateSchemaType) -> DBSchemaType:
        obj = await self._repository.create(obj)
        model = self._model.model_validate(obj, from_attributes=True)

        message = f"Книга {model.title} была создана"
        async with self._broker as br:
            await br.publish(message, routing_key="book_queue")

        return model

    async def update(
        self, obj_uuid: UUID, obj: UpdateSchemaType
    ) -> DBSchemaType:
        obj = await self._repository.update(obj_uuid, obj)
        model = self._model.model_validate(obj, from_attributes=True)

        message = f"Книга {model.title} была обновлена"
        async with self._broker as br:
            await br.publish(message, routing_key="book_queue")

        return model

    async def remove(self, obj_uuid: UUID) -> UUID:
        obj_uuid = await self._repository.remove(obj_uuid)

        message = f"Книга с id {obj_uuid} была удалена"
        async with self._broker as br:
            await br.publish(message, routing_key="book_queue")

        return obj_uuid

    async def count(self) -> int | None:
        count = await self._repository.count()
        return count

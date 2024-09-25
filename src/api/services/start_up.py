import logging

from sqlalchemy import select

from src.api.schemas.api.v1.users import RequestUserCreate
from src.configs import StartUpSettings
from src.db.clients.postgres import PostgresDatabase
from src.db.entities import User

logger = logging.getLogger("StartUpService")


class StartUpService:
    def __init__(self, database: PostgresDatabase, settings: StartUpSettings):
        self.__database = database
        self.__settings = settings

    async def create_admin_user(self) -> None:
        user_uuid = await self.get_uuid_by_email(self.__settings.admin_email)
        if user_uuid:
            logger.info(
                "User with email %s already exist", self.__settings.admin_email
            )
            return
        else:
            await self.create_user(
                RequestUserCreate(
                    email=self.__settings.admin_email,
                    password=self.__settings.admin_password,
                    username="admin",
                )
            )
            logger.info(
                "Created admin user with email %s", self.__settings.admin_email
            )

    async def get_uuid_by_email(self, email: str) -> str | None:
        async with self.__database.get_session() as session:
            db_obj = await session.execute(
                select(User.uuid).filter_by(email=email)
            )
            obj_uuid = db_obj.scalars().first()
            return obj_uuid

    async def create_user(self, instance: RequestUserCreate) -> None:
        async with self.__database.get_session() as session:
            instance_dict = instance.model_dump()
            instance_dict["is_superuser"] = True
            db_obj = User(**instance_dict)
            session.add(db_obj)
            await session.commit()

from logging import config as logging_config

from src.configs.logger import LOGGING
from src.configs.postgres import PostgresSettings
from src.configs.rabbitmq import RabbitSettings
from src.configs.redis import RedisSettings
from src.utils.settings import EnvSettings, FastApiSettings

__all__ = [
    "settings",
    "LOGGING",
    "PostgresSettings",
    "RedisSettings",
    "RabbitSettings",
]

logging_config.dictConfig(LOGGING)


class AppSettings(FastApiSettings):
    pass


class Settings(EnvSettings):
    app: AppSettings = AppSettings()
    postgres: PostgresSettings = PostgresSettings()
    redis: RedisSettings = RedisSettings()
    rabbit: RabbitSettings = RabbitSettings()


settings = Settings()

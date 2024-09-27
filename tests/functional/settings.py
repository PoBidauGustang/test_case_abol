import os
from typing import Any

from pydantic import SecretStr
from pydantic.fields import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env.test"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ServiceSettings(EnvSettings):
    host: str = ""
    port: int = 0
    host_local: str = "localhost"
    port_local: int = 8000
    local: bool = Field(..., alias="LOCAL")

    def correct_host(self) -> str:
        return self.host_local if self.local else self.host

    def correct_port(self) -> int:
        return self.port_local if self.local else self.port


class TestSettings(ServiceSettings):
    redis_host: str = Field(default="redis", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_host_local: str = Field(default="localhost", alias="REDIS_HOST_LOCAL")
    redis_port_local: int = Field(default=6380, alias="REDIS_PORT_LOCAL")

    api_host: str = Field(..., alias="API_HOST")
    api_port: int = Field(..., alias="API_PORT")

    grpc_server_host: str = Field(
        default="grpcserver.com", alias="GRPC_SERVER_HOST"
    )
    grpc_server_port: int = Field(default=50051, alias="GRPC_SERVER_PORT")
    grpc_server_host_local: str = Field(
        default="localhost", alias="GRPC_SERVER_HOST_LOCAL"
    )
    grpc_server_port_local: int = Field(
        default=50052, alias="GRPC_SERVER_PORT_LOCAL"
    )

    @property
    def get_redis_host(self) -> dict[str, Any]:
        if self.local:
            return {
                "host": self.redis_host_local,
                "port": self.redis_port_local,
            }
        return {"host": self.redis_host, "port": self.redis_port}

    @property
    def get_api_host(self) -> str:
        if self.local:
            return f"127.0.0.1:{self.api_port}"
        return f"{self.api_host}:{self.api_port}"

    @property
    def get_grpc_server_host(self) -> str:
        if self.local:
            return (
                f"{self.grpc_server_host_local}:{self.grpc_server_port_local}"
            )
        return f"{self.grpc_server_host}:{self.grpc_server_port}"


class SQLAlchemyConnection(ServiceSettings):
    db_name: str
    user: str
    password: SecretStr
    sqlalchemy_echo: bool = Field(default=True)

    @property
    def postgres_connection_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.correct_host(),
            port=self.correct_port(),
            database=self.db_name,
        )


class PostgresSettings(SQLAlchemyConnection):
    """
    This class is used to store the Postgres content db connection settings.
    """

    db_name: str = Field(..., alias="POSTGRES_DB")
    user: str = Field(..., alias="POSTGRES_USER")
    password: SecretStr = Field(..., alias="POSTGRES_PASSWORD")
    host: str = Field(..., alias="POSTGRES_HOST")
    port: int = Field(..., alias="POSTGRES_PORT")
    host_local: str = Field(default="localhost", alias="POSTGRES_HOST_LOCAL")
    port_local: int = Field(default=5432, alias="POSTGRES_PORT_LOCAL")


settings = TestSettings()
postgres_settings = PostgresSettings()

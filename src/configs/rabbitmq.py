from pydantic import Field, computed_field

from src.utils.settings import ServiceSettings


class RabbitSettings(ServiceSettings):
    """
    This class is used to store the RABBITMQ connection settings.
    """

    rabbit_user: str = Field(..., alias="RABBITMQ_USER")
    rabbit_pass: str = Field(..., alias="RABBITMQ_PASS")
    host: str = Field(..., alias="RABBITMQ_HOST")
    port: int = Field(..., alias="RABBITMQ_PORT")
    host_local: str = Field(default="localhost", alias="RABBITMQ_HOST_LOCAL")
    port_local: int = Field(default=5672, alias="RABBITMQ_PORT_LOCAL")

    @computed_field
    def dsn(self) -> str:
        return f"amqp://{self.rabbit_user}:{self.rabbit_pass}@{self.correct_host()}:{self.correct_port()}/"

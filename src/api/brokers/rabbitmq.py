from faststream.rabbit import RabbitBroker

from src.configs import settings

rabbit_broker: RabbitBroker = RabbitBroker(settings.rabbit.dsn)


def get_rabbit_broker() -> RabbitBroker:
    return rabbit_broker

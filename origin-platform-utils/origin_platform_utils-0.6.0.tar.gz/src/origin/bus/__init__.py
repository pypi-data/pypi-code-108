from typing import List

from .registry import MessageRegistry
from .kafka import KafkaMessageBroker
from .serialize import MessageSerializer
from .dispatcher import MessageDispatcher  # noqa: F401
from .broker import MessageBroker, Message  # noqa: F401


message_registry = MessageRegistry()


def get_default_broker(group: str, servers: List[str]) -> MessageBroker:
    """
    Creates and returns an instance of the default message broker.

    :param group: Consumer group
    :param servers: List of broker servers in the format "IP:PORT"
    :return: An instance of the default message broker
    """
    return KafkaMessageBroker(
        group=group,
        servers=servers,
        serializer=MessageSerializer(registry=message_registry),
    )

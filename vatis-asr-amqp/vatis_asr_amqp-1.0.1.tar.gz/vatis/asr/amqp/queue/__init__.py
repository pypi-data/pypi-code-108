from typing import Optional, Type, Dict, Tuple

from vatis.asr_commons.config.logging import get_logger

from . import environment
from . import routing
from .connection import ReconnectingAMQPConnection, ConnectionState
from .constants import *
from .consumer import ConsumerManager, Consumer
from .exceptions import ConnectionClosedException, NoRouteFoundException, RetriesExceededException
from .model import DEFAULT_EXCHANGE, Queue, Exchange, TRANSCRIPTION_RESULT_WAITING_EXCHANGE
from .publisher import Publisher
from .routing import RoutingRule
from . import consumer

logger = get_logger(__name__)
_initialized = False


def __init__():
    global _initialized

    if _initialized:
        logger.warning('Queue module already initialized')
        return

    from . import connection

    connection.__init__()

    from .connection import connection_factory

    initialization_connection: ReconnectingAMQPConnection = connection_factory.create()
    try:
        _declare_dead_letter_exchange(initialization_connection)
        _declare_waiting_transcription_result_exchange(initialization_connection)
    finally:
        initialization_connection.close()

    routing.__init__()
    consumer.__init__(connection_factory)
    publisher.__init__(connection_factory)

    _initialized = True


def _declare_dead_letter_exchange(connection: ReconnectingAMQPConnection):
    with connection.channel() as channel:
        channel.exchange_declare(exchange=DEAD_LETTER_EXCHANGE_NAME,
                                 exchange_type=DEAD_LETTER_EXCHANGE_TYPE.value)

        channel.queue_declare(queue=DEAD_LETTER_QUEUE_NAME,
                              durable=True)

        channel.queue_bind(queue=DEAD_LETTER_QUEUE_NAME,
                           exchange=DEAD_LETTER_EXCHANGE_NAME,
                           routing_key=DEAD_LETTER_QUEUE_NAME)


def _declare_waiting_transcription_result_exchange(connection: ReconnectingAMQPConnection):
    with connection.channel() as channel:
        channel.exchange_declare(exchange=TRANSCRIPTION_RESULT_WAITING_EXCHANGE.name,
                                 exchange_type=TRANSCRIPTION_RESULT_WAITING_EXCHANGE.type,
                                 durable=TRANSCRIPTION_RESULT_WAITING_EXCHANGE.durable)


def push(message, ttl_millis: Optional[int] = environment.RABBITMQ_TTL_MILLIS):

    from .publisher import publisher

    publisher.push(message, ttl_millis=ttl_millis)


def close():
    publisher.close()
    consumer.close()


def consume(queue: Queue, dtype: Optional[Type] = None, exchange: Exchange = DEFAULT_EXCHANGE):
    """
    Conventional decorator

    :param queue: queue to be consumed
    :param dtype: expected payload type
    :param exchange: exchange to bind the queue to
    :return: decorator
    """
    def decorator(func):
        from .consumer import consumer_manager

        queue_consumer = Consumer(queue=queue, exchange=exchange, dtype=dtype, callback=func)
        consumer_manager.add_consumer(queue_consumer)

    return decorator


def healthy() -> Tuple[bool, Dict[str, str]]:
    consumer_state: ConnectionState = consumer.get_connection_state()
    publisher_state: ConnectionState = publisher.get_connection_state()

    queue_healthy: bool = consumer_state == ConnectionState.CONNECTED and publisher_state == ConnectionState.CONNECTED

    return queue_healthy, {
        'CONSUMER': consumer_state.value,
        'PUBLISHER': publisher_state.value
    }

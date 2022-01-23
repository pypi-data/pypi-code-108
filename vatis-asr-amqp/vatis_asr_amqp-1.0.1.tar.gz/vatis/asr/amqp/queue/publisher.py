from typing import List, Optional, Dict

from pika import BasicProperties
from pika.frame import Method
from vatis.asr_commons.config.logging import get_logger

from . import constants
from . import environment
from . import routing, DEFAULT_EXCHANGE
from .connection import ReconnectingAMQPConnection, ConnectionState, ConnectionFactory
from .exceptions import NoRouteFoundException, ConnectionClosedException
from .routing import Route

logger = get_logger(__name__)


class Publisher:
    def __init__(self, connection: ReconnectingAMQPConnection):
        assert connection is not None

        self._connection: ReconnectingAMQPConnection = connection
        self._closed: bool = False

    def push(self, message, ttl_millis: Optional[int] = environment.RABBITMQ_TTL_MILLIS):
        routes: List[Route] = routing.get_routes(message)

        self.push_to_routes(message=message, routes=routes, ttl_millis=ttl_millis)

    def push_to_routes(self, message, routes: List[Route],
                       ttl_millis: Optional[int] = environment.RABBITMQ_TTL_MILLIS):
        from .parse import encode

        if self._closed:
            raise ConnectionClosedException()

        if not len(routes):
            raise NoRouteFoundException(f'No route found for message: {str(message)}')

        body, content_type = encode(message)

        properties: BasicProperties = BasicProperties(
            content_type=content_type,
            delivery_mode=2,  # persistent
            expiration=str(ttl_millis),
            headers={
                'Content-Type': content_type,
                'Content-Length': len(body)
            }
        )

        with self._connection.channel() as channel:
            channel.confirm_delivery()

            for route in routes:
                if route.exchange.declare:
                    channel.exchange_declare(
                        exchange=route.exchange.name,
                        durable=route.exchange.durable,
                        exchange_type=route.exchange.type,
                        auto_delete=route.exchange.auto_delete,
                        arguments=route.exchange.arguments
                    )

                if route.queue is not None and route.queue.declare:
                    queue_arguments: Dict[str, str] = {
                        'x-dead-letter-exchange': constants.DEAD_LETTER_EXCHANGE_NAME,
                        'x-dead-letter-routing-key': constants.DEAD_LETTER_QUEUE_NAME
                    }
                    if route.queue.arguments is not None:
                        queue_arguments.update(route.queue.arguments)

                    result: Method = channel.queue_declare(
                        queue=route.queue.name,
                        durable=route.queue.durable,
                        auto_delete=route.queue.auto_delete,
                        exclusive=route.queue.exclusive,
                        arguments=queue_arguments
                    )

                    if route.exchange != DEFAULT_EXCHANGE:
                        channel.queue_bind(queue=result.method.queue,
                                           exchange=route.exchange.name,
                                           routing_key=result.method.queue)

                channel.basic_publish(
                    exchange=route.exchange.name,
                    routing_key=route.queue.name if route.queue is not None else '',
                    body=body,
                    properties=properties,
                    mandatory=True
                )

                if route.queue is not None:
                    logger.info(f'Routed message {str(message)} to {route.exchange.name}.{route.queue.name}')
                else:
                    logger.info(f'Routed message {str(message)} to {route.exchange.name}')

    def close(self):
        self._closed = True
        self._connection.close()

    @property
    def connection_state(self) -> ConnectionState:
        try:
            return self._connection.state
        except Exception:
            return ConnectionState.NOT_CREATED


publisher: Optional[Publisher]


def __init__(connection_factory: ConnectionFactory):
    global publisher

    publisher = Publisher(connection_factory.create())


def close():
    try:
        publisher.close()
    except Exception as e:
        logger.exception('Exception while closing Publisher: %s', str(e))


def get_connection_state() -> ConnectionState:
    return publisher.connection_state

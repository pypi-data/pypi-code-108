import dataclasses
import time
from threading import RLock, Thread
from typing import Optional, Type, Callable, Any, List, Dict, Tuple, Union

from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import ChannelClosed, ConnectionClosedByBroker
from pika.frame import Method
from pika.spec import BasicProperties, Basic
from vatis.asr_commons.config.logging import get_logger

from . import constants
from .connection import ReconnectingAMQPConnection, ConnectionState, ConnectionFactory
from .exceptions import RetriesExceededException, ConnectionClosedException, NoConsumerException, \
    CorruptedBodyException, UnknownBodyTypeException
from .model import Queue, Exchange, DEFAULT_EXCHANGE

from typeguard import check_type

logger = get_logger(__name__)


def _isinstance(value: Any, expected_type: Type) -> bool:
    try:
        check_type('', value=value, expected_type=expected_type)
        return True
    except TypeError:
        return False


@dataclasses.dataclass(frozen=True, eq=False)
class Consumer:
    queue: Queue
    exchange: Optional[Exchange]
    dtype: Optional[Type]
    callback: Callable[[Any], bool]
    auto_ack: bool = True
    """
        Class defining a Consumer

        :param queue: queue that will be consumed
        :param exchange: exchange declaration. It may be optional if the queue is surely already bound,
                         although it's highly recommended to specify one
        :param dtype: expected message type, also used for filtering the message. It can be any type, or a Union.
                      If None is selected, all messages will match
        :param callback: function called when a matched message is received. It return True if the message is 
                         acknowledged, False otherwise. Any thrown exception will act as unacknowledged
        :param auto_ack: flag that indicates the message will be acknowledged no matter the execution outcome
                         Make sure that it's only one consumer declared with auto_ack=False per queue per message type
    """

    def __eq__(self, other):
        if isinstance(other, Consumer):
            consumer: Consumer = other

            return self.queue == consumer.queue and self.dtype == consumer.dtype
        else:
            return NotImplemented


@dataclasses.dataclass(frozen=True)
class Message:
    queue: str
    exchange: str
    body: bytes
    headers: Dict[str, str]


class MessageListener:
    def on_message(self, message: Message) -> bool:
        """
        Raw message listener. It receives the message directly from the queue
        To not requeue the message, raise NoConsumerException
        :param message: received message
        :return: acknowledged signal
        """
        pass


class ConsumerLoop:
    def __init__(self, connection: ReconnectingAMQPConnection,
                 reconnection_delay: float = 3, reconnection_retries: int = 50,
                 execution_delay: float = 5, prefetch_count: int = 3):
        """
            Class that manages a channel, implements reconnecting mechanism and allow listeners for queues.
            It's recommended to have only one listener per loop due to Pika limitations

            :param connection: queue connection
            :param reconnection_delay: delay in seconds between reconnection attempts
            :param reconnection_retries: maximum retries before declaring the connection lost
            :param execution_delay: seconds to wait after initialization before start consuming
            :param prefetch_count: number of messages to be prefetched in advanced
        """
        assert connection is not None

        self._connection: ReconnectingAMQPConnection = connection
        self._channel: Optional[BlockingChannel] = None
        self._channel_lock: RLock = RLock()
        self._closed: bool = False
        self._queues_listener: Dict[str, MessageListener] = {}
        self._queues_declaration: Dict[str, Tuple[Queue, Optional[Exchange]]] = {}
        self._reconnection_delay: float = reconnection_delay
        self._reconnection_retries: int = reconnection_retries
        self._execution_delay: float = execution_delay
        self._prefect_count = prefetch_count
        self._loop: Thread = Thread(name='consumer-loop', target=ConsumerLoop._consumer_loop, args=[self], daemon=True)

        self._open_channel()
        self._loop.start()

    def _open_channel(self):
        if self._closed:
            raise ConnectionClosedException()

        if self._channel_closed():
            with self._channel_lock:
                retries = 1
                while retries <= self._reconnection_retries and self._channel_closed():
                    try:
                        logger.info('Opening channel')

                        self._channel = self._connection.channel()
                        assert not self._channel_closed()

                        self._channel.basic_qos(prefetch_count=self._prefect_count)

                        for queue in self._queues_listener:
                            self._declare_queue(queue)
                            self._channel.basic_consume(queue=queue,
                                                        on_message_callback=self._dispatch_message,
                                                        auto_ack=False)

                        logger.info('Added listeners. Channel prepared')

                    except Exception as e:
                        logger.exception(f'Retry {retries} of {self._reconnection_retries}. Exception {str(e)}')
                        retries += 1
                        time.sleep(self._reconnection_delay)

                if self._channel_closed():
                    self.close()
                    raise RetriesExceededException()

    def _channel_closed(self) -> bool:
        return self._channel is None or self._channel.is_closed or not self._channel.is_open

    @staticmethod
    def _consumer_loop(self: 'ConsumerLoop'):
        time.sleep(self._execution_delay)

        while not self._closed:
            try:
                self._open_channel()
                self._channel.start_consuming()
            except Exception as e:
                logger.exception('Consumer loop interrupted: %s', str(e))

        if not self._channel_closed():
            with self._channel_lock:
                if not self._channel_closed():
                    self._channel.stop_consuming()

    def _dispatch_message(self, channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        if method.routing_key in self._queues_listener:
            message: Message = Message(queue=method.routing_key, exchange=method.exchange, body=body, headers=properties.headers)
            listener: MessageListener = self._queues_listener[method.routing_key]
            ack: bool
            unconsumable: bool = False

            try:
                ack = listener.on_message(message)
            except Exception as e:
                logger.exception('Can\'t deliver message: %s', str(e))
                ack = False

                if isinstance(e, (NoConsumerException, UnknownBodyTypeException, CorruptedBodyException)):
                    unconsumable = True
                    logger.error(f'Message is not consumable. Dropping. (Headers: {str(message.headers)})')

            if ack:
                channel.basic_ack(delivery_tag=method.delivery_tag)
            else:
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=not unconsumable)

    def listen_queue(self, queue: Queue, listener: MessageListener, exchange: Optional[Exchange] = DEFAULT_EXCHANGE):
        if self._closed:
            raise ConnectionClosedException()

        assert queue is not None
        assert listener is not None

        queue_name: str = queue.name

        with self._channel_lock:
            if queue_name in self._queues_listener:
                raise ValueError(f'A listener for {queue_name} already exists')

            self._queues_listener[queue_name] = listener
            self._queues_declaration[queue_name] = (queue, exchange)

            try:
                self._declare_queue(queue_name)

                self._channel.basic_consume(queue=queue_name,
                                            on_message_callback=self._dispatch_message,
                                            auto_ack=False)
            except (ChannelClosed, ConnectionClosedByBroker) as e:
                logger.exception(str(e))
                self._open_channel()

    def _declare_queue(self, queue_name: str):
        queue, exchange = self._queues_declaration[queue_name]

        if exchange is not None and exchange.declare:
            self._channel.exchange_declare(
                exchange=exchange.name,
                exchange_type=exchange.type,
                durable=exchange.durable,
                auto_delete=exchange.auto_delete,
                arguments=exchange.arguments
            )

        if queue.declare:
            queue_arguments: Dict[str, str] = {
                'x-dead-letter-exchange': constants.DEAD_LETTER_EXCHANGE_NAME,
                'x-dead-letter-routing-key': constants.DEAD_LETTER_QUEUE_NAME
            }
            if queue.arguments is not None:
                queue_arguments.update(queue.arguments)

            result: Method = self._channel.queue_declare(
                queue=queue.name,
                durable=queue.durable,
                exclusive=queue.exclusive,
                auto_delete=queue.auto_delete,
                arguments=queue_arguments
            )

            if exchange is not None and exchange != DEFAULT_EXCHANGE:
                self._channel.queue_bind(queue=result.method.queue,
                                         exchange=exchange.name,
                                         routing_key=result.method.queue)

    def close(self):
        self._closed = True

        if not self._channel_closed():
            with self._channel_lock:
                if not self._channel_closed():
                    self._channel.close()
                    del self._channel
                    self._channel = None

                self._connection.close()

    @property
    def connection_state(self) -> ConnectionState:
        try:
            return self._connection.state
        except Exception:
            return ConnectionState.NOT_CREATED


class ConsumerManager(MessageListener):
    def __init__(self, connection_factory: ConnectionFactory, prefetch_count: int = 1):
        """
        Manager of consumers of a queue.
        It creates a channel for each new consumer that can be configured by the attributes in the Consumer
        :param connection_factory: AMQP connection factory
        """
        assert connection_factory is not None

        self._connection_factory: ConnectionFactory = connection_factory
        self._lock: RLock = RLock()
        self._consumer_loop: ConsumerLoop = \
            ConsumerLoop(self._connection_factory.create(), prefetch_count=prefetch_count)
        self._queue_consumers: Dict[str, List[Consumer]] = {}

    def add_consumer(self, consumer: Consumer):
        with self._lock:
            if consumer.queue.name in self._queue_consumers:
                for c in self._queue_consumers[consumer.queue.name]:
                    if ConsumerManager._different_consumer_must_ack_same_message(consumer, c):
                        raise ValueError('Can\'t consume same message from same queue with auto_ack disabled')

                self._queue_consumers[consumer.queue.name].append(consumer)
            else:
                self._consumer_loop.listen_queue(queue=consumer.queue,
                                                 listener=self,
                                                 exchange=consumer.exchange)

                self._queue_consumers[consumer.queue.name] = [consumer]

            logger.info('Subscribed consumer: %s', str(consumer))

    @staticmethod
    def _different_consumer_must_ack_same_message(c1: Consumer, c2: Consumer):
        return c1.auto_ack == c2.auto_ack == False and \
               (c1 == c2 or \
               (c1.queue == c2.queue and c1.dtype == c2.dtype))

    def on_message(self, message: Message) -> bool:
        from .parse import decode

        payload: Union[object, str, bytes] = decode(message)

        ack_message: bool = True
        delivered: bool = False

        for consumer in self._queue_consumers[message.queue]:
            if consumer.dtype is None or _isinstance(payload, consumer.dtype):
                delivered = True
                try:
                    ack: bool = consumer.callback(payload)

                    if not consumer.auto_ack:
                        ack_message = ack
                except Exception as e:
                    logger.exception('Consumer failed: %s', str(e))
                    if not consumer.auto_ack:
                        ack_message = False

        if not delivered:
            raise NoConsumerException()

        return ack_message

    def close(self):
        self._consumer_loop.close()

    @property
    def connection_state(self) -> ConnectionState:
        try:
            return self._consumer_loop.connection_state
        except Exception:
            return ConnectionState.NOT_CREATED


consumer_manager: Optional[ConsumerManager]


def __init__(connection_factory: ConnectionFactory):
    global consumer_manager

    consumer_manager = ConsumerManager(connection_factory)


def close():
    try:
        consumer_manager.close()
    except Exception as e:
        logger.exception('Exception while closing ConsumerManager: %s', str(e))


def get_connection_state() -> ConnectionState:
    return consumer_manager.connection_state

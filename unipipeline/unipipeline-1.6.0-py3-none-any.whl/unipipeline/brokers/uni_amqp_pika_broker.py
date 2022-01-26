import functools
import time
from time import sleep
from typing import Optional, TypeVar, Set, List, NamedTuple, Callable, TYPE_CHECKING
from urllib.parse import urlparse

from pika import ConnectionParameters, PlainCredentials, BlockingConnection, BasicProperties, spec  # type: ignore
from pika.adapters.blocking_connection import BlockingChannel  # type: ignore
from pika.exceptions import AMQPConnectionError, AMQPError, ConnectionClosedByBroker, AMQPChannelError  # type: ignore

from unipipeline.brokers.uni_broker import UniBroker
from unipipeline.brokers.uni_broker_consumer import UniBrokerConsumer
from unipipeline.brokers.uni_broker_message_manager import UniBrokerMessageManager
from unipipeline.definitions.uni_broker_definition import UniBrokerDefinition
from unipipeline.definitions.uni_definition import UniDynamicDefinition
from unipipeline.errors.uni_answer_delay_error import UniAnswerDelayError
from unipipeline.message.uni_message import UniMessage
from unipipeline.message_meta.uni_message_meta import UniMessageMeta, UniAnswerParams
from unipipeline.utils.uni_echo import UniEcho

if TYPE_CHECKING:
    from unipipeline.modules.uni_mediator import UniMediator

BASIC_PROPERTIES__HEADER__COMPRESSION_KEY = 'compression'

CONNECTION_ERRORS = (ConnectionClosedByBroker, AMQPConnectionError)


TMessage = TypeVar('TMessage', bound=UniMessage)

T = TypeVar('T')


class UniAmqpPikaBrokerMessageManager(UniBrokerMessageManager):

    def __init__(self, channel: BlockingChannel, method_frame: spec.Basic.Deliver) -> None:
        self._channel = channel
        self._method_frame = method_frame
        self._acknowledged = False

    def reject(self) -> None:
        self._channel.basic_reject(delivery_tag=self._method_frame.delivery_tag, requeue=True)

    def ack(self) -> None:
        if self._acknowledged:
            return
        self._acknowledged = True
        self._channel.basic_ack(delivery_tag=self._method_frame.delivery_tag)


class UniAmqpPikaBrokerConfig(UniDynamicDefinition):
    exchange_name: str = "communication"
    answer_exchange_name: str = "communication_answer"
    heartbeat: int = 600
    blocked_connection_timeout: int = 300
    prefetch: int = 1
    retry_max_count: int = 100
    retry_delay_s: int = 3
    socket_timeout: int = 300
    stack_timeout: int = 400
    persistent_message: bool = True


class UniAmqpPikaBrokerConsumer(NamedTuple):
    queue: str
    on_message_callback: Callable[[BlockingChannel, spec.Basic.Deliver, BasicProperties, bytes], None]
    consumer_tag: str
    prefetch_count: int


class AmqpPikaChannelObj:
    def __init__(self, name: str, ttl: int, broker: 'UniAmqpPikaBroker') -> None:
        self._name = name
        self._broker = broker
        self._ch: Optional[BlockingChannel] = None
        self._ttl = ttl
        self._ch_time: float = 0

    def close_channel(self) -> None:
        if self._ch is None or self._ch.is_closed:
            return
        self._ch.close()
        self._broker.echo.log_info(f'channel {self._name} closed')

    def get_channel(self, *, force_recreate: bool = False, force_current: bool = False) -> BlockingChannel:
        if force_recreate and not force_current:
            self.close_channel()
            return self.get_channel(force_recreate=False)

        if self._ch is None or self._ch.is_closed:
            self._broker.connect()
            conn = self._broker._connection
            assert conn is not None
            self._ch = conn.channel()
            self._ch_time = time.time()
            self._broker.echo.log_info(f'channel {self._name} established')
        else:
            if not force_current and (time.time() - self._ch_time > self._ttl):
                return self.get_channel(force_recreate=True)
            self._broker.echo.log_debug(f'channel {self._name} reused')
        return self._ch


class UniAmqpPikaBroker(UniBroker[UniAmqpPikaBrokerConfig]):
    config_type = UniAmqpPikaBrokerConfig

    def get_topic_approximate_messages_count(self, topic: str) -> int:
        res = self._ch_stat.get_channel().queue_declare(queue=topic, passive=True)
        return int(res.method.message_count)

    @classmethod
    def get_connection_uri(cls) -> str:
        raise NotImplementedError(f"cls method get_connection_uri must be implemented for class '{cls.__name__}'")

    def __init__(self, mediator: 'UniMediator', definition: UniBrokerDefinition) -> None:
        super().__init__(mediator, definition)

        broker_url = self.get_connection_uri()

        url_params_pr = urlparse(url=broker_url)

        self._params = ConnectionParameters(
            heartbeat=self.config.heartbeat,
            blocked_connection_timeout=self.config.blocked_connection_timeout,
            socket_timeout=self.config.socket_timeout,
            stack_timeout=self.config.stack_timeout,
            retry_delay=self.definition.retry_delay_s,
            host=url_params_pr.hostname,
            port=url_params_pr.port,
            credentials=PlainCredentials(url_params_pr.username, url_params_pr.password, erase_on_connect=False),
        )

        self._consumers: List[UniAmqpPikaBrokerConsumer] = list()

        self._connection: Optional[BlockingConnection] = None

        self._ch_initializer = AmqpPikaChannelObj('initializer', int(self.config.heartbeat / 2), self)
        self._ch_stat = AmqpPikaChannelObj('stat', int(self.config.heartbeat / 2), self)
        self._ch_publisher = AmqpPikaChannelObj('publisher', int(self.config.heartbeat / 2), self)
        self._ch_answ_publisher = AmqpPikaChannelObj('answer_publisher', int(self.config.heartbeat / 2), self)
        self._ch_consumer = AmqpPikaChannelObj('consumer', int(self.config.heartbeat / 2), self)
        self._ch_answ_consumer = AmqpPikaChannelObj('answer_consumer', int(self.config.heartbeat / 2), self)

        self._consuming_started = False
        self._in_processing = False
        self._interrupted = False

        self._initialized_exchanges: Set[str] = set()
        self._initialized_topics: Set[str] = set()

    def _init_exchange(self, ch: BlockingChannel, exchange: str) -> None:
        if exchange in self._initialized_topics:
            return
        self._initialized_exchanges.add(exchange)
        ch.exchange_declare(
            exchange=exchange,
            exchange_type="direct",
            passive=False,
            durable=True,
            auto_delete=False,
        )
        self.echo.log_info(f'exchange "{exchange}" initialized')

    def _init_topic(self, ch: BlockingChannel, exchange: str, topic: str) -> str:
        q = f'{exchange}->{topic}'
        if q in self._initialized_topics:
            return topic
        self._initialized_topics.add(q)

        self._init_exchange(ch, exchange)

        if exchange == self.config.exchange_name:
            ch.queue_declare(queue=topic, durable=True, auto_delete=False, passive=False)
        elif exchange == self.config.answer_exchange_name:
            ch.queue_declare(queue=topic, durable=False, auto_delete=True, exclusive=True, passive=False)
        else:
            raise TypeError(f'invalid exchange name "{exchange}"')

        ch.queue_bind(queue=topic, exchange=self.config.exchange_name, routing_key=topic)
        self.echo.log_info(f'queue "{q}" initialized')
        return topic

    def initialize(self, topics: Set[str], answer_topic: Set[str]) -> None:
        return

    def stop_consuming(self) -> None:
        self._end_consuming()

    def _end_consuming(self) -> None:
        if not self._consuming_started:
            return
        self._interrupted = True
        if not self._in_processing:
            self._ch_consumer.get_channel(force_current=True).stop_consuming()
            self.close()
            self._consuming_started = False
            self.echo.log_info('consumption stopped')

    def connect(self) -> None:
        try:
            if self._connection is None or self._connection.is_closed:
                self._connection = BlockingConnection(self._params)
                self.echo.log_info('connected')
        except (*CONNECTION_ERRORS, AMQPError) as e:
            raise ConnectionError(str(e))

    def close(self) -> None:
        if self._connection is None:
            return

        if self._connection.is_closed:
            self._connection = None
            return

        try:
            self._connection.close()
            self._connection = None
        except AMQPError:
            pass

    def add_consumer(self, consumer: UniBrokerConsumer) -> None:
        echo = self.echo.mk_child(f'topic[{consumer.topic}]')
        if self._consuming_started:
            echo.exit_with_error(f'you cannot add consumer dynamically :: tag="{consumer.id}" group_id={consumer.group_id}')

        def consumer_wrapper(channel: BlockingChannel, method_frame: spec.Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
            self._in_processing = True

            meta = self.parse_message_body(
                body,
                compression=properties.headers.get(BASIC_PROPERTIES__HEADER__COMPRESSION_KEY, None),
                content_type=properties.content_type,
                unwrapped=consumer.unwrapped,
            )

            manager = UniAmqpPikaBrokerMessageManager(channel, method_frame)
            consumer.message_handler(meta, manager)
            self._in_processing = False
            if self._interrupted:
                self._end_consuming()

        self._consumers.append(UniAmqpPikaBrokerConsumer(
            queue=consumer.topic,
            on_message_callback=consumer_wrapper,
            consumer_tag=consumer.id,
            prefetch_count=consumer.prefetch_count,
        ))

        echo.log_info(f'added consumer :: tag="{consumer.id}" group_id={consumer.group_id}')

    def _start_consuming(self) -> None:
        echo = self.echo.mk_child('consuming')
        if len(self._consumers) == 0:
            echo.log_warning('has no consumers to start consuming')
            return
        ch = self._ch_consumer.get_channel()
        prefetch_count: int = self.config.prefetch
        for c in self._consumers:
            topic = self._init_topic(ch, self.config.exchange_name, c.queue)
            ch.basic_consume(queue=topic, on_message_callback=c.on_message_callback, consumer_tag=c.consumer_tag)
            echo.log_debug(f'added consumer {c.consumer_tag} on {self.config.exchange_name}->{topic}')
            prefetch_count = max(prefetch_count, c.prefetch_count)
        echo.log_info(f'consumers count is {len(self._consumers)}')
        ch.basic_qos(prefetch_count=prefetch_count)
        ch.start_consuming()  # blocking operation

    def _retry_run(self, echo: UniEcho, fn: Callable[[], T]) -> T:
        retry_counter = 0
        max_retries = max(self.config.retry_max_count, 1)
        retry_threshold_s = self.config.retry_delay_s * max_retries
        while True:
            start = time.time()
            try:
                return fn()
            except AMQPChannelError as e:
                echo.log_warning(f"Caught a channel error: {e}, stopping...")
                raise
            except CONNECTION_ERRORS as e:
                echo.log_error(f'connection closed {e}')
                if int(time.time() - start) >= retry_threshold_s:
                    retry_counter = 0
                if retry_counter >= max_retries:
                    raise ConnectionError()
                retry_counter += 1
                sleep(self.config.retry_delay_s)
                echo.log_warning(f'retry {retry_counter}/{max_retries} :: {e}')

    def start_consuming(self) -> None:
        echo = self.echo.mk_child('consuming')
        if self._consuming_started:
            echo.log_warning('consuming has already started. ignored')
            return
        self._consuming_started = True
        self._interrupted = False
        self._in_processing = False

        self._retry_run(echo, self._start_consuming)

    def _publish(self, ch: BlockingChannel, exchange: str, topic: str, meta: UniMessageMeta, props: BasicProperties, alone: bool = False) -> None:
        self.echo.log_debug(f'message start publishing to {exchange}->{topic}')
        if alone:
            size = self.get_topic_approximate_messages_count(topic)
            if size != 0:
                self.echo.log_info(f'sending was skipped, because topic {topic} has messages: {size}>0')
                return
        topic = self._init_topic(ch, exchange, topic)
        ch.basic_publish(
            exchange=exchange,
            routing_key=topic,
            body=self.serialize_message_body(meta),
            properties=props
        )
        self.echo.log_debug(f'message published to {exchange}->{topic}')

    def publish(self, topic: str, meta_list: List[UniMessageMeta], alone: bool = False) -> None:
        ch = self._ch_publisher.get_channel()
        echo = self.echo.mk_child('publish')
        for meta in meta_list:  # TODO: package sending
            headers = dict()
            if self.definition.compression is not None:
                headers[BASIC_PROPERTIES__HEADER__COMPRESSION_KEY] = self.definition.compression
            if meta.ttl_s:
                headers['x-message-ttl'] = str(meta.ttl_s * 1000)

            if meta.need_answer:
                assert meta.answer_params is not None
                props = BasicProperties(
                    content_type=self.definition.content_type,
                    content_encoding='utf-8',
                    reply_to=f'{meta.answer_params.topic}.{meta.answer_params.id}',
                    correlation_id=str(meta.id),
                    delivery_mode=2 if self.config.persistent_message else 0,
                    headers=headers,
                )
            else:
                props = BasicProperties(
                    content_type=self.definition.content_type,
                    content_encoding='utf-8',
                    delivery_mode=2 if self.config.persistent_message else 0,
                    headers=headers,
                )
            self._retry_run(echo, functools.partial(self._publish, ch=ch, exchange=self.config.exchange_name, topic=topic, meta=meta, props=props, alone=alone))
        self.echo.log_info(f'{list(meta_list)} messages published to {self.config.exchange_name}->{topic}')

    def _get_answ(self, answer_params: UniAnswerParams, max_delay_s: int, unwrapped: bool) -> UniMessageMeta:
        ch = self._ch_answ_consumer.get_channel(force_recreate=True)
        topic = self._init_topic(ch, self.config.answer_exchange_name, f'{answer_params.topic}.{answer_params.id}')

        started = time.time()
        while True:
            (method, properties, body) = ch.basic_get(queue=topic, auto_ack=True)

            if method is None:
                if (time.time() - started) > max_delay_s:
                    raise UniAnswerDelayError(f'answer for {self.config.answer_exchange_name}->{topic} reached delay limit {max_delay_s} seconds')
                self.echo.log_debug(f'no answer {int(time.time() - started + 1)}s in {self.config.answer_exchange_name}->{topic}')
                sleep(1)
                continue

            self.echo.log_debug(f'took answer from {self.config.answer_exchange_name}->{topic}')
            return self.parse_message_body(
                body,
                compression=properties.headers.get(BASIC_PROPERTIES__HEADER__COMPRESSION_KEY, None),
                content_type=properties.content_type,
                unwrapped=unwrapped,
            )

    def get_answer(self, answer_params: UniAnswerParams, max_delay_s: int, unwrapped: bool) -> UniMessageMeta:
        echo = self.echo.mk_child('get_answer')
        return self._retry_run(echo, functools.partial(self._get_answ, answer_params=answer_params, max_delay_s=max_delay_s, unwrapped=unwrapped))

    def publish_answer(self, answer_params: UniAnswerParams, meta: UniMessageMeta) -> None:
        echo = self.echo.mk_child('publish_answer')
        props = BasicProperties(
            content_type=self.definition.content_type,
            content_encoding='utf-8',
            delivery_mode=1,
        )
        ch = self._ch_answ_publisher.get_channel()
        self._retry_run(echo, functools.partial(self._publish, ch=ch, exchange=self.config.answer_exchange_name, topic=f'{answer_params.topic}.{answer_params.id}', meta=meta, props=props))

import asyncio
import contextlib
import datetime
import functools
import inspect
import logging
from typing import Dict, Iterable, List, Optional, Tuple
from uuid import UUID

import aiormq
import yarl
from pydantic import Field

from arrlio import core
from arrlio.backends import base
from arrlio.exc import TaskNoResultError
from arrlio.models import Event, Message, TaskInstance, TaskResult
from arrlio.tp import AsyncCallableT, ExceptionFilterT, PositiveIntT, PriorityT, RMQDsn, SerializerT, TimeoutT
from arrlio.utils import retry


logger = logging.getLogger("arrlio")


BACKEND_NAME: str = "arrlio"
SERIALIZER: str = "arrlio.serializer.json.Json"
URL: str = "amqp://guest:guest@localhost"
TIMEOUT: int = 10
RETRY_TIMEOUTS: Iterable[int] = None
VERIFY_SSL: bool = True
TASKS_EXCHANGE: str = "arrlio"
TASKS_QUEUE_DURABLE: bool = False
TASKS_QUEUE_TTL: int = None
TASKS_PREFETCH_COUNT: int = 1
EVENTS_EXCHANGE: str = "arrlio"
EVENTS_QUEUE_DURABLE: bool = False
EVENTS_QUEUE: str = "arrlio.events"
EVENTS_QUEUE_TTL: int = None
EVENTS_PREFETCH_COUNT: int = 1
MESSAGE_PREFETCH_COUNT: int = 1


class BackendConfig(base.BackendConfig):
    name: Optional[str] = Field(default_factory=lambda: BACKEND_NAME)
    serializer: SerializerT = Field(default_factory=lambda: SERIALIZER)
    url: RMQDsn = Field(default_factory=lambda: URL)
    timeout: Optional[TimeoutT] = Field(default_factory=lambda: TIMEOUT)
    retry_timeouts: Optional[List] = Field(default_factory=lambda: RETRY_TIMEOUTS)
    verify_ssl: Optional[bool] = Field(default_factory=lambda: True)
    tasks_exchange: str = Field(default_factory=lambda: TASKS_EXCHANGE)
    tasks_queue_durable: bool = Field(default_factory=lambda: TASKS_QUEUE_DURABLE)
    tasks_queue_ttl: Optional[PositiveIntT] = Field(default_factory=lambda: TASKS_QUEUE_TTL)
    tasks_prefetch_count: Optional[PositiveIntT] = Field(default_factory=lambda: TASKS_PREFETCH_COUNT)
    events_exchange: str = Field(default_factory=lambda: EVENTS_EXCHANGE)
    events_queue_durable: bool = Field(default_factory=lambda: EVENTS_QUEUE_DURABLE)
    events_queue: str = Field(default_factory=lambda: EVENTS_QUEUE)
    events_queue_ttl: Optional[PositiveIntT] = Field(default_factory=lambda: EVENTS_QUEUE_TTL)
    events_prefetch_count: Optional[PositiveIntT] = Field(default_factory=lambda: EVENTS_PREFETCH_COUNT)
    message_prefetch_count: Optional[PositiveIntT] = Field(default_factory=lambda: MESSAGE_PREFETCH_COUNT)

    class Config:
        validate_assignment = True
        env_prefix = "ARRLIO_RMQ_BACKEND_"


class RMQConnection:
    __shared: dict = {}

    @property
    def _shared(self) -> dict:
        return self.__shared[self._key]

    def __init__(self, url, retry_timeouts: Iterable[int] = None, exc_filter: ExceptionFilterT = None):
        self.url = url

        self._retry_timeouts = retry_timeouts
        self._exc_filter = exc_filter

        self._key = (asyncio.get_event_loop(), url)

        if self._key not in self.__shared:
            self.__shared[self._key] = {
                "refs": 0,
                "objs": 0,
                "conn": None,
                "conn_lock": asyncio.Lock(),
                "on_open_callbacks_lock": asyncio.Lock(),
                "on_open": {},
                "on_lost": {},
                "on_close": {},
            }

        self._shared["objs"] += 1

        self._connect_timeout = yarl.URL(url).query.get("connection_timeout")
        if self._connect_timeout is not None:
            self._connect_timeout = int(self._connect_timeout) / 1000

        self._supervisor_task: asyncio.Task = None
        self._closed: asyncio.Future = asyncio.Future()

    def __del__(self):
        if not self.is_closed:
            logger.warning("%s: unclosed", self)
        self._shared["objs"] -= 1
        if self._shared["objs"] == 0:
            del self.__shared[self._key]

    @property
    def _conn(self) -> aiormq.Connection:
        return self._shared["conn"]

    @_conn.setter
    def _conn(self, value: aiormq.Connection):
        self._shared["conn"] = value

    @property
    def _conn_lock(self) -> asyncio.Lock:
        return self._shared["conn_lock"]

    @property
    def _on_open_callbacks_lock(self) -> asyncio.Lock:
        return self._shared["on_open_callbacks_lock"]

    @property
    def _refs(self) -> int:
        return self._shared["refs"]

    @_refs.setter
    def _refs(self, value: int):
        self._shared["refs"] = value

    def add_callback(self, tp, group, name: str, cb):
        self._shared[tp].setdefault(group, {})
        self._shared[tp][group][name] = cb

    async def remove_callback(self, tp, group, name):
        if group in self._shared[tp] and name in self._shared[tp][group]:
            del self._shared[tp][group][name]

    async def remove_callback_group(self, group):
        for tp in ("on_open", "on_lost", "on_close"):
            if group in self._shared[tp]:
                del self._shared[tp][group]

    def __str__(self):
        return f"{self.__class__.__name__}[{self.url.host}:{self.url.port}]"

    @property
    def is_open(self) -> bool:
        return not self.is_closed and self._conn is not None and not self._conn.is_closed

    @property
    def is_closed(self) -> bool:
        return self._closed.done()

    async def _execute_callbacks(self, tp):
        for callback in [callback for callbacks in self._shared[tp].values() for callback in callbacks.values()]:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error("Callback '%s' %s error: %s %s", tp, callback, e.__class__, e)

    async def _supervisor(self):
        try:
            await asyncio.wait([self._conn.closing, self._closed], return_when=asyncio.FIRST_COMPLETED)
        except Exception as e:
            logger.warning("%s: %s %s", self, e.__class__, e)
        if not self._closed.done():
            logger.warning("%s: connection lost", self)
            self._refs -= 1
            await self._execute_callbacks("on_lost")

    async def open(self):
        if self.is_open:
            return

        if self._on_open_callbacks_lock.locked():
            raise ConnectionError()

        async with self._conn_lock:
            if self.is_open:
                return
            if self.is_closed:
                raise Exception("Can't reopen closed connection")

            if self._conn is None or self._conn.is_closed:

                @retry(retry_timeouts=self._retry_timeouts, exc_filter=self._exc_filter)
                async def connect():
                    logger.info("%s: connecting...", self)
                    self._conn = await asyncio.wait_for(
                        aiormq.connect(self.url.get_secret_value()), self._connect_timeout
                    )
                    logger.info("%s: connected", self)

                await connect()

            self._refs += 1

            self._supervisor_task = asyncio.create_task(self._supervisor())

            async with self._on_open_callbacks_lock:
                await self._execute_callbacks("on_open")

    async def close(self):
        if self.is_closed:
            return

        self._refs = max(0, self._refs - 1)
        async with self._conn_lock:
            self._closed.set_result(None)
            if self._refs == 0:
                await self._execute_callbacks("on_close")
                if self._conn:
                    await self._conn.close()
                    self._conn = None
                    logger.info("%s: closed", self)
            if self._supervisor_task:
                await self._supervisor_task
                self._supervisor_task = None

    async def channel(self) -> aiormq.Channel:
        await self.open()
        channel = await self._conn.channel()
        return channel

    @contextlib.asynccontextmanager
    async def channel_ctx(self):
        await self.open()
        channel = await self._conn.channel()
        try:
            yield channel
        finally:
            await channel.close()


class Backend(base.Backend):
    def __init__(self, config: BackendConfig):
        super().__init__(config)

        self._task_consumers: Dict[str, Tuple[aiormq.Channel, aiormq.spec.Basic.ConsumeOk]] = {}
        self._message_consumers: Dict[str, Tuple[aiormq.Channel, aiormq.spec.Basic.ConsumeOk]] = {}
        self._events_consumer: Tuple[aiormq.Channel, aiormq.spec.Basic.ConsumeOk] = []
        self._consume_lock: asyncio.Lock = asyncio.Lock()

        self.__conn: RMQConnection = RMQConnection(config.url, retry_timeouts=config.retry_timeouts)

        self.__conn.add_callback("on_open", id(self), "declare", self.declare)
        self.__conn.add_callback("on_lost", id(self), "cleanup", self._task_consumers.clear)
        self.__conn.add_callback("on_lost", id(self), "cleanup", self._message_consumers.clear)
        self.__conn.add_callback("on_lost", id(self), "cleanup", self._events_consumer.clear)
        self.__conn.add_callback("on_close", id(self), "cleanup", self.stop_consume_tasks)
        self.__conn.add_callback("on_close", id(self), "cleanup", self.stop_consume_messages)
        self.__conn.add_callback("on_close", id(self), "cleanup", self.stop_consume_events)

    def __del__(self):
        if not self.is_closed:
            logger.warning("Unclosed %s", self)

    def __str__(self):
        return f"[RMQBackend[{self.__conn}]]"

    @property
    def _conn(self):
        if self.is_closed:
            raise Exception(f"{self} is closed")
        return self.__conn

    async def channel(self):
        return await self._conn.channel()

    @contextlib.asynccontextmanager
    async def channel_ctx(self):
        async with self._conn.channel_ctx() as channel:
            yield channel

    async def close(self):
        await super().close()
        await self.__conn.remove_callback_group(id(self))
        await self.__conn.close()

    @base.Backend.task
    async def declare(self):
        async with self._conn.channel_ctx() as channel:
            await channel.exchange_declare(
                self.config.tasks_exchange,
                exchange_type="direct",
                durable=False,
                auto_delete=False,
                timeout=self.config.timeout,
            )
            await channel.exchange_declare(
                self.config.events_exchange,
                exchange_type="direct",
                durable=False,
                auto_delete=False,
                timeout=self.config.timeout,
            )
            arguments = {}
            if self.config.events_queue_ttl is not None:
                arguments["x-message-ttl"] = self.config.events_queue_ttl * 1000
            await channel.queue_declare(
                self.config.events_queue,
                durable=self.config.events_queue_durable,
                auto_delete=not self.config.events_queue_durable,
                arguments=arguments,
                timeout=self.config.timeout,
            )
            await channel.queue_bind(
                self.config.events_queue,
                self.config.events_exchange,
                routing_key=self.config.events_queue,
                timeout=self.config.timeout,
            )

    @base.Backend.task
    async def declare_task_queue(self, queue: str):
        async with self._conn.channel_ctx() as channel:
            arguments = {}
            arguments["x-max-priority"] = PriorityT.le
            if self.config.tasks_queue_ttl is not None:
                arguments["x-message-ttl"] = self.config.tasks_queue_ttl * 1000
            durable = self.config.tasks_queue_durable
            await channel.queue_declare(
                queue,
                durable=durable,
                auto_delete=not durable,
                arguments=arguments,
                timeout=self.config.timeout,
            )
            await channel.queue_bind(queue, self.config.tasks_exchange, routing_key=queue, timeout=self.config.timeout)

    @base.Backend.task
    async def send_task(self, task_instance: TaskInstance, result_queue_durable: bool = False, **kwds):
        task_data = task_instance.data
        task_data.extra["result_queue_durable"] = result_queue_durable
        await self.declare_task_queue(task_data.queue)
        logger.debug("%s: put %s", self, task_instance)
        async with self._conn.channel_ctx() as channel:
            await channel.basic_publish(
                self.serializer.dumps_task_instance(task_instance),
                exchange=self.config.tasks_exchange,
                routing_key=task_data.queue,
                properties=aiormq.spec.Basic.Properties(
                    delivery_mode=2,
                    message_id=str(task_data.task_id.hex),
                    timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
                    expiration=str(int(task_data.ttl * 1000)) if task_data.ttl is not None else None,
                    priority=task_data.priority,
                ),
                timeout=self.config.timeout,
            )

    @base.Backend.task
    async def consume_tasks(self, queues: List[str], on_task: AsyncCallableT):
        async with self._consume_lock:
            timeout = self.config.timeout

            async def on_msg(channel: aiormq.Channel, msg):
                try:
                    task_instance = self.serializer.loads_task_instance(msg.body)
                    logger.debug("%s: got %s", self, task_instance)
                    ack_late = task_instance.task.ack_late
                    if not ack_late:
                        await channel.basic_ack(msg.delivery.delivery_tag)
                    await asyncio.shield(on_task(task_instance))
                    if ack_late:
                        await channel.basic_ack(msg.delivery.delivery_tag)
                except Exception:
                    logger.exception("Internal error")

            for queue in queues:
                if queue in self._task_consumers and not self._task_consumers[queue][0].is_closed:
                    continue
                await self.declare_task_queue(queue)
                channel = await self._conn.channel()
                await channel.basic_qos(prefetch_count=self.config.tasks_prefetch_count, timeout=timeout)
                self._task_consumers[queue] = [
                    channel,
                    await channel.basic_consume(queue, functools.partial(on_msg, channel), timeout=timeout),
                ]
                logger.debug("%s: consuming queue '%s'", self, queue)

            async def _consume_tasks():
                await self.consume_tasks(list(self._task_consumers.keys()), on_task)

            self._conn.add_callback("on_lost", id(self), "consume_tasks", _consume_tasks)

    async def stop_consume_tasks(self):
        await self.__conn.remove_callback("on_lost", id(self), "consume_tasks")
        await self.__conn.remove_callback("on_close", id(self), "consume_tasks")
        async with self._consume_lock:
            for queue, (channel, consume_ok) in self._task_consumers.items():
                if not self.__conn.is_closed and not channel.is_closed:
                    logger.debug("%s: stop consuming queue '%s'", self, queue)
                    await channel.basic_cancel(consume_ok.consumer_tag, timeout=self.config.timeout)
                    await channel.close()
            self._task_consumers = {}

    @base.Backend.task
    async def declare_result_queue(self, task_instance: TaskInstance):
        task_id = task_instance.data.task_id
        result_ttl = task_instance.data.result_ttl
        queue = routing_key = f"result.{task_id}"
        durable = task_instance.data.extra.get("result_queue_durable")
        async with self._conn.channel_ctx() as channel:
            await channel.queue_declare(
                queue,
                durable=durable,
                auto_delete=not durable,
                arguments={"x-expires": result_ttl * 1000} if result_ttl is not None else None,
                timeout=self.config.timeout,
            )
            await channel.queue_bind(
                queue,
                self.config.tasks_exchange,
                routing_key=routing_key,
                timeout=self.config.timeout,
            )
        return queue

    @base.Backend.task
    async def push_task_result(self, task_instance: core.TaskInstance, task_result: TaskResult):
        if not task_instance.task.result_return:
            raise TaskNoResultError(task_instance.data.task_id)
        routing_key = await self.declare_result_queue(task_instance)
        logger.debug("%s: push result for %s", self, task_instance)
        async with self._conn.channel_ctx() as channel:
            await channel.basic_publish(
                self.serializer.dumps_task_result(task_result, encrypt=task_instance.data.result_encrypt),
                exchange=self.config.tasks_exchange,
                routing_key=routing_key,
                properties=aiormq.spec.Basic.Properties(
                    delivery_mode=2,
                    timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
                ),
                timeout=self.config.timeout,
            )

    @base.Backend.task
    async def pop_task_result(self, task_instance: TaskInstance) -> TaskResult:
        task_id = task_instance.data.task_id
        queue = await self.declare_result_queue(task_instance)

        while True:
            fut = asyncio.Future()

            def on_conn_error():
                if not fut.done():
                    fut.set_exception(ConnectionError)

            def on_result(msg):
                try:
                    logger.debug("%s: pop result for %s", self, task_instance)
                    task_result = self.serializer.loads_task_result(msg.body)
                    if not fut.done():
                        fut.set_result(task_result)
                except Exception as e:
                    if not fut.done():
                        fut.set_exception(e)

            self._conn.add_callback("on_close", id(self), task_id, on_conn_error)
            self._conn.add_callback("on_lost", id(self), task_id, on_conn_error)
            channel = await self._conn.channel()
            consume_ok = await channel.basic_consume(queue, on_result, timeout=self.config.timeout)
            try:
                try:
                    await fut
                except ConnectionError:
                    await channel.close()
                    continue
                return fut.result()
            finally:
                await self._conn.remove_callback("on_close", id(self), task_id)
                await self._conn.remove_callback("on_lost", id(self), task_id)
                if not self._conn.is_closed and not channel.is_closed:
                    await channel.basic_cancel(consume_ok.consumer_tag, timeout=self.config.timeout)
                    if not self._conn.is_closed and not channel.is_closed:
                        await channel.queue_delete(queue)
                    if not self._conn.is_closed and not channel.is_closed:
                        await channel.close()

    @base.Backend.task
    async def send_message(
        self,
        message: Message,
        routing_key: str = None,
        delivery_mode: int = None,
        encrypt: bool = None,
        **kwds,
    ):
        if not routing_key:
            raise ValueError("Invalid routing key")
        logger.debug("%s: put %s", self, message)
        async with self._conn.channel_ctx() as channel:
            await channel.basic_publish(
                self.serializer.dumps(message.data, encrypt=encrypt),
                exchange=message.exchange,
                routing_key=routing_key,
                properties=aiormq.spec.Basic.Properties(
                    message_id=str(message.message_id.hex),
                    delivery_mode=delivery_mode or 2,
                    timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
                    expiration=str(int(message.ttl * 1000)) if message.ttl is not None else None,
                    priority=message.priority,
                ),
                timeout=self.config.timeout,
            )

    @base.Backend.task
    async def consume_messages(self, queues: List[str], on_message: AsyncCallableT):
        async with self._consume_lock:
            timeout = self.config.timeout

            async def on_msg(channel: aiormq.Channel, msg):
                try:
                    data = {
                        "data": self.serializer.loads(msg.body),
                        "message_id": UUID(msg.header.properties.message_id),
                        "exchange": msg.delivery.exchange,
                        "priority": msg.delivery.routing_key,
                        "ttl": int(msg.header.properties.expiration) // 1000
                        if msg.header.properties.expiration
                        else None,
                    }
                    message = Message(**data)
                    logger.debug("%s: got %s", self, message)
                    ack_late = message.ack_late
                    if not ack_late:
                        await channel.basic_ack(msg.delivery.delivery_tag)
                    await asyncio.shield(on_message(message))
                    if ack_late:
                        await channel.basic_ack(msg.delivery.delivery_tag)
                except Exception:
                    logger.exception("Internal error")

            for queue in queues:
                if queue in self._message_consumers and not self._message_consumers[queue][0].is_closed:
                    continue
                channel = await self._conn.channel()
                await channel.basic_qos(prefetch_count=self.config.message_prefetch_count, timeout=timeout)
                self._message_consumers[queue] = [
                    channel,
                    await channel.basic_consume(queue, functools.partial(on_msg, channel), timeout=timeout),
                ]
                logger.debug("%s: consuming messages queue '%s'", self, queue)

            async def _consume_messages():
                await self.consume_messages(list(self._message_consumers.keys()), on_message)

            self._conn.add_callback("on_lost", id(self), "consume_messages", _consume_messages)

    async def stop_consume_messages(self):
        await self.__conn.remove_callback("on_lost", id(self), "consume_messages")
        await self.__conn.remove_callback("on_close", id(self), "consume_messages")
        async with self._consume_lock:
            for queue, (channel, consume_ok) in self._message_consumers.items():
                if not self.__conn.is_closed and not channel.is_closed:
                    logger.debug("%s: stop consuming messages queue '%s'", self, queue)
                    await channel.basic_cancel(consume_ok.consumer_tag, timeout=self.config.timeout)
                    await channel.close()
            self._message_consumers = {}

    @base.Backend.task
    async def push_event(self, task_instance: TaskInstance, event: Event):
        if not task_instance.data.events:
            return
        async with self._conn.channel_ctx() as channel:
            await channel.basic_publish(
                self.serializer.dumps_event(event),
                exchange=self.config.events_exchange,
                routing_key=self.config.events_queue,
                properties=aiormq.spec.Basic.Properties(
                    delivery_mode=2,
                    timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
                ),
                timeout=self.config.timeout,
            )

    @base.Backend.task
    async def consume_events(self, on_event: AsyncCallableT):
        async with self._consume_lock:
            timeout = self.config.timeout

            async def on_msg(channel: aiormq.Channel, msg):
                try:
                    event = self.serializer.loads_event(msg.body)
                    logger.debug("%s: got %s", self, event)
                    # ack_late = event.ack_late
                    ack_late = False
                    if not ack_late:
                        await channel.basic_ack(msg.delivery.delivery_tag)
                    await asyncio.shield(on_event(event))
                    if ack_late:
                        await channel.basic_ack(msg.delivery.delivery_tag)
                except Exception:
                    logger.exception("Internal error")

                if self._events_consumer and not self._events_consumer[0].is_closed:
                    return

            channel = await self._conn.channel()
            await channel.basic_qos(prefetch_count=self.config.events_prefetch_count, timeout=timeout)
            self._events_consumer = [
                channel,
                await channel.basic_consume(
                    self.config.events_queue,
                    functools.partial(on_msg, channel),
                    timeout=timeout,
                ),
            ]
            logger.debug("%s: consuming events queue '%s'", self, self.config.events_queue)

            async def _consume_events():
                await self.consume_events(on_event)

            self._conn.add_callback("on_lost", id(self), "consume_events", _consume_events)

    async def stop_consume_events(self):
        await self.__conn.remove_callback("on_lost", id(self), "consume_events")
        await self.__conn.remove_callback("on_close", id(self), "consume_events")
        async with self._consume_lock:
            if not self._events_consumer:
                return
            channel, consume_ok = self._events_consumer
            if not self.__conn.is_closed and not channel.is_closed:
                logger.debug("%s: stop consuming events queue '%s'", self, self.config.events_queue)
                await channel.basic_cancel(consume_ok.consumer_tag, timeout=self.config.timeout)
                await channel.close()
            self._events_consumer = []

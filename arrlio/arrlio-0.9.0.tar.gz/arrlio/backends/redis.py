import asyncio
import dataclasses
import itertools
import logging
from typing import Dict, Iterable, List, Optional

import siderpy
from pydantic import Field

from arrlio import core
from arrlio.backends import base
from arrlio.exc import TaskNoResultError
from arrlio.models import Event, Message, TaskInstance, TaskResult
from arrlio.tp import AsyncCallableT, PositiveIntT, RedisDsn, SerializerT, TimeoutT


logger = logging.getLogger("arrlio")


BACKEND_NAME: str = "arrlio"
SERIALIZER: str = "arrlio.serializer.json.Json"
URL: str = "redis://localhost?db=0"
TIMEOUT: int = 60
CONNECT_TIMEOUT: int = 30
POOL_SIZE: int = 10
RETRY_TIMEOUTS: Iterable[int] = None
VERIFY_SSL: bool = True


class BackendConfig(base.BackendConfig):
    name: Optional[str] = Field(default_factory=lambda: BACKEND_NAME)
    serializer: SerializerT = Field(default_factory=lambda: SERIALIZER)
    url: RedisDsn = Field(default_factory=lambda: URL)
    timeout: Optional[TimeoutT] = Field(default_factory=lambda: TIMEOUT)
    connect_timeout: Optional[TimeoutT] = Field(default_factory=lambda: CONNECT_TIMEOUT)
    retry_timeouts: Optional[List] = Field(default_factory=lambda: RETRY_TIMEOUTS)
    pool_size: Optional[PositiveIntT] = Field(default_factory=lambda: POOL_SIZE)
    verify_ssl: Optional[bool] = Field(default_factory=lambda: True)

    class Config:
        validate_assignment = True
        env_prefix = "ARRLIO_REDIS_BACKEND_"


class Backend(base.Backend):
    def __init__(self, config: BackendConfig):
        super().__init__(config)
        self.redis_pool = siderpy.RedisPool(
            config.url.get_secret_value(),
            connect_timeout=config.connect_timeout,
            timeout=config.timeout,
            size=config.pool_size,
        )
        self._task_consumers: Dict[str, asyncio.Task] = {}
        self._message_consumers: Dict[str, asyncio.Task] = {}
        self._events_consumer: asyncio.Task = None

    def __str__(self):
        return f"[RedisBackend[{self.redis_pool}]]"

    async def close(self):
        await super().close()
        await self.redis_pool.close()

    def _make_task_queue_key(self, queue: str) -> str:
        return f"q.t.{queue}"

    def _make_result_key(self, task_id: str) -> str:
        return f"r.t.{task_id}"

    def _make_message_queue_key(self, queue: str) -> str:
        return f"q.m.{queue}"

    @base.Backend.task
    async def send_task(self, task_instance: TaskInstance, **kwds):
        queue = task_instance.data.queue
        queue_key = self._make_task_queue_key(queue)
        data = self.serializer.dumps_task_instance(task_instance)

        async with self.redis_pool.get_redis() as redis:
            with redis.pipeline():
                await redis.multi()
                await redis.setex(f"{task_instance.data.task_id}", task_instance.data.ttl, data)
                await redis.rpush(queue_key, f"{task_instance.data.priority}|{task_instance.data.task_id}")
                if task_instance.data.priority:
                    await redis.sort(queue, "BY", "*", "ASC", "STORE", queue)
                await redis.execute()
                await redis.pipeline_execute()

    @base.Backend.task
    async def consume_tasks(self, queues: List[str], on_task: AsyncCallableT):
        async def consume_queue(queue):
            queue_key = self._make_task_queue_key(queue)
            while True:
                try:
                    logger.debug("%s: consuming tasks queue '%s'", self, queue)
                    _, queue_value = await self.redis_pool.blpop(queue_key, 0)
                    priority, task_id = queue_value.decode().split("|")
                    serialized_data = await self.redis_pool.get(task_id)
                    if serialized_data is None:
                        continue
                    task_instance = self.serializer.loads_task_instance(serialized_data)
                    await asyncio.shield(on_task(task_instance))
                except asyncio.CancelledError:
                    logger.info("%s: stop consume tasks queue '%s'", self, queue)
                    break
                except (ConnectionError, TimeoutError) as e:
                    logger.error("%s: %s %s", self, e.__class__, e)
                    retry_timeouts = (
                        iter(self.config.retry_timeouts) if self.config.retry_timeouts else itertools.repeat(1)
                    )
                    seconds = next(retry_timeouts, None)
                    if seconds is None:
                        raise e
                    await asyncio.sleep(seconds)
                except Exception:
                    logger.exception("Internal error")

        for queue in queues:
            self._task_consumers[queue] = asyncio.create_task(consume_queue(queue))

    async def stop_consume_tasks(self):
        for queue in self._task_consumers.keys():
            self._task_consumers[queue].cancel()
        self._task_consumers = {}

    @base.Backend.task
    async def push_task_result(self, task_instance: core.TaskInstance, task_result: TaskResult):
        if not task_instance.task.result_return:
            raise TaskNoResultError(task_instance.data.task_id)
        result_key = self._make_result_key(task_instance.data.task_id)

        async with self.redis_pool.get_redis() as redis:
            with redis.pipeline():
                await redis.multi()
                await redis.rpush(
                    result_key,
                    self.serializer.dumps_task_result(task_result, encrypt=task_instance.data.result_encrypt),
                )
                await redis.expire(result_key, task_instance.data.result_ttl)
                await redis.execute()
                await redis.pipeline_execute()

    @base.Backend.task
    async def pop_task_result(self, task_instance: TaskInstance) -> TaskResult:
        result_key = self._make_result_key(task_instance.data.task_id)
        raw_data = await self.redis_pool.blpop(result_key, 0)
        return self.serializer.loads_task_result(raw_data[1])

    @base.Backend.task
    async def send_message(self, message: Message, encrypt: bool = None, **kwds):
        queue = message.exchange
        queue_key = self._make_message_queue_key(queue)
        data = self.serializer.dumps(dataclasses.asdict(message), encrypt=encrypt)

        async with self.redis_pool.get_redis() as redis:
            with redis.pipeline():
                await redis.multi()
                await redis.setex(f"{message.message_id}", message.ttl, data)
                await redis.rpush(queue_key, f"{message.priority}|{message.message_id}")
                if message.priority:
                    await redis.sort(queue, "BY", "*", "ASC", "STORE", queue)
                await redis.execute()
                await redis.pipeline_execute()

    @base.Backend.task
    async def consume_messages(self, queues: List[str], on_message: AsyncCallableT):
        async def consume_queue(queue):
            queue_key = self._make_message_queue_key(queue)
            while True:
                try:
                    logger.debug("%s: consuming messages queue '%s'", self, queue)
                    _, queue_value = await self.redis_pool.blpop(queue_key, 0)
                    priority, message_id = queue_value.decode().split("|")
                    serialized_data = await self.redis_pool.get(message_id)
                    if serialized_data is None:
                        continue
                    data = self.serializer.loads(serialized_data)
                    message = Message(**data)
                    logger.debug("%s: got %s", self, message)
                    await asyncio.shield(on_message(message))
                except asyncio.CancelledError:
                    logger.info("%s: stop consume messages queue '%s'", self, queue)
                    break
                except (ConnectionError, TimeoutError) as e:
                    logger.error("%s: %s %s", self, e.__class__, e)
                    retry_timeouts = (
                        iter(self.config.retry_timeouts) if self.config.retry_timeouts else itertools.repeat(1)
                    )
                    seconds = next(retry_timeouts, None)
                    if seconds is None:
                        raise e
                    await asyncio.sleep(seconds)
                except Exception:
                    logger.exception("Internal error")

        for queue in queues:
            self._message_consumers[queue] = asyncio.create_task(consume_queue(queue))

    async def stop_consume_messages(self):
        for queue in self._message_consumers.keys():
            self._message_consumers[queue].cancel()
        self._message_consumers = {}

    @base.Backend.task
    async def push_event(self, task_instance: core.TaskInstance, event: Event):
        if not task_instance.data.events:
            return

        queue_key = "arrlio.events"
        data = self.serializer.dumps_event(event)

        async with self.redis_pool.get_redis() as redis:
            with redis.pipeline():
                await redis.multi()
                await redis.setex(f"{event.event_id}", task_instance.data.event_ttl, data)
                await redis.rpush(queue_key, f"{event.event_id}")
                await redis.execute()
                await redis.pipeline_execute()

    @base.Backend.task
    async def consume_events(self, on_event: AsyncCallableT):
        async def consume_queue():
            queue_key = "arrlio.events"
            while True:
                try:
                    logger.debug("%s: consuming events")
                    _, queue_value = await self.redis_pool.blpop(queue_key, 0)
                    event_id = queue_value.decode()
                    serialized_data = await self.redis_pool.get(event_id)
                    if serialized_data is None:
                        continue
                    event = self.serializer.loads_event(serialized_data)
                    logger.debug("%s: got %s", self, event)
                    await asyncio.shield(on_event(event))
                except asyncio.CancelledError:
                    logger.info("%s: stop consume events")
                    break
                except (ConnectionError, TimeoutError) as e:
                    logger.error("%s: %s %s", self, e.__class__, e)
                    retry_timeouts = (
                        iter(self.config.retry_timeouts) if self.config.retry_timeouts else itertools.repeat(1)
                    )
                    seconds = next(retry_timeouts, None)
                    if seconds is None:
                        raise e
                    await asyncio.sleep(seconds)
                except Exception:
                    logger.exception("Internal error")

        self._events_consumer = asyncio.create_task(consume_queue())

    async def stop_consume_events(self):
        if self._events_consumer:
            self._events_consumer.cancel()
        self._events_consumer = None

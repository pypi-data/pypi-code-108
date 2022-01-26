import asyncio
import collections
import dataclasses
import logging
import time
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from arrlio.backends import base
from arrlio.core import TaskNoResultError
from arrlio.models import Event, Message, TaskInstance, TaskResult
from arrlio.tp import AsyncCallableT, PriorityT, SerializerT


logger = logging.getLogger("arrlio")


BACKEND_NAME: str = "arrlio"
SERIALIZER: str = "arrlio.serializer.nop.Nop"


class BackendConfig(base.BackendConfig):
    name: Optional[str] = Field(default_factory=lambda: BACKEND_NAME)
    serializer: SerializerT = Field(default_factory=lambda: SERIALIZER)

    class Config:
        validate_assignment = True
        env_prefix = "ARRLIO_LOCAL_BACKEND_"


class Backend(base.Backend):
    __shared: dict = {}

    def __init__(self, config: BackendConfig):
        super().__init__(config)
        name: str = self.config.name
        shared: dict = self.__class__.__shared
        if name not in shared:
            shared[name] = {
                "refs": 0,
                "task_queues": collections.defaultdict(asyncio.PriorityQueue),
                "message_queues": collections.defaultdict(asyncio.Queue),
                "results": {},
                "events": {},
                "event_cond": asyncio.Condition(),
            }
        shared = shared[name]
        shared["refs"] += 1
        self._task_queues = shared["task_queues"]
        self._message_queues = shared["message_queues"]
        self._results = shared["results"]
        self._events = shared["events"]
        self._event_cond = shared["event_cond"]
        self._task_consumers = {}
        self._message_consumers = {}
        self._events_consumer: asyncio.Task = None

    def __del__(self):
        self._refs = max(0, self._refs - 1)
        if self._refs == 0:
            del self.__shared[self.config.name]

    def __str__(self):
        return f"[LocalBackend({self.config.name})]"

    @property
    def _shared(self) -> dict:
        return self.__shared[self.config.name]

    @property
    def _refs(self) -> int:
        return self._shared["refs"]

    @_refs.setter
    def _refs(self, value: int):
        self._shared["refs"] = value

    @base.Backend.task
    async def send_task(self, task_instance: TaskInstance, **kwds):
        task_data = task_instance.data
        if task_instance.data.result_return and task_data.task_id not in self._results:
            self._results[task_data.task_id] = [asyncio.Event(), None]
        logger.debug("%s: put %s", self, task_instance)
        await self._task_queues[task_data.queue].put(
            (
                (PriorityT.le - task_data.priority) if task_data.priority else PriorityT.ge,
                time.monotonic(),
                task_instance.data.ttl,
                self.serializer.dumps_task_instance(task_instance),
            )
        )

    @base.Backend.task
    async def consume_tasks(self, queues: List[str], on_task: AsyncCallableT):
        async def consume_queue(queue: str):
            logger.info("%s: consuming tasks queue '%s'", self, queue)
            while True:
                try:
                    _, ts, ttl, data = await self._task_queues[queue].get()
                    if ttl is not None and time.monotonic() >= ts + ttl:
                        continue
                    task_instance = self.serializer.loads_task_instance(data)
                    logger.debug("%s: got %s", self, task_instance)
                    await asyncio.shield(on_task(task_instance))
                except asyncio.CancelledError:
                    logger.info("%s: stop consume tasks queue '%s'", self, queue)
                    break
                except Exception as e:
                    logger.exception(e)

        for queue in queues:
            self._task_consumers[queue] = asyncio.create_task(consume_queue(queue))

    async def stop_consume_tasks(self):
        for queue in self._task_consumers.keys():
            self._task_consumers[queue].cancel()
        self._task_consumers = {}

    @base.Backend.task
    async def push_task_result(self, task_instance: TaskInstance, task_result: TaskResult):
        if not task_instance.data.result_return:
            return
        task_id: UUID = task_instance.data.task_id
        self._results[task_id][1] = self.serializer.dumps_task_result(
            task_result,
            encrypt=task_instance.data.result_encrypt,
        )
        self._results[task_id][0].set()
        if task_instance.data.result_ttl is not None:
            loop = asyncio.get_event_loop()
            loop.call_later(task_instance.data.result_ttl, lambda: self._results.pop(task_id, None))

    @base.Backend.task
    async def pop_task_result(self, task_instance: TaskInstance) -> TaskResult:
        task_id: UUID = task_instance.data.task_id
        if not task_instance.data.result_return:
            raise TaskNoResultError(str(task_id))

        if task_id not in self._results:
            self._results[task_id] = [asyncio.Event(), None]

        await self._results[task_id][0].wait()
        try:
            return self.serializer.loads_task_result(self._results[task_id][1])
        finally:
            del self._results[task_id]

    @base.Backend.task
    async def send_message(self, message: Message, encrypt: bool = None, **kwds):
        data = dataclasses.asdict(message)
        data["data"] = self.serializer.dumps(message.data, encrypt=encrypt)
        logger.debug("%s: put %s", self, message)
        await self._message_queues[message.exchange].put(
            (
                (PriorityT.le - message.priority) if message.priority else PriorityT.ge,
                time.monotonic(),
                message.ttl,
                data,
            )
        )

    @base.Backend.task
    async def consume_messages(self, queues: List[str], on_message: AsyncCallableT):
        async def consume_queue(queue: str):
            while True:
                try:
                    logger.info("%s: consuming messages queue '%s'", self, queue)
                    _, ts, ttl, data = await self._message_queues[queue].get()
                    if ttl is not None and time.monotonic() >= ts + ttl:
                        continue
                    data["data"] = self.serializer.loads(data["data"])
                    message = Message(**data)
                    logger.debug("%s: got %s", self, message)
                    await asyncio.shield(on_message(message))
                except asyncio.CancelledError:
                    logger.info("%s: stop consume messages queue '%s'", self, queue)
                    break
                except Exception as e:
                    logger.exception(e)

        for queue in queues:
            self._message_consumers[queue] = asyncio.create_task(consume_queue(queue))

    async def stop_consume_messages(self):
        for queue in self._message_consumers.keys():
            self._message_consumers[queue].cancel()
        self._message_consumers = {}

    @base.Backend.task
    async def push_event(self, task_instance: TaskInstance, event: Event):
        if not task_instance.data.events:
            return
        self._events[event.event_id] = self.serializer.dumps_event(event)
        async with self._event_cond:
            self._event_cond.notify()
        if task_instance.data.event_ttl is not None:
            loop = asyncio.get_event_loop()
            loop.call_later(task_instance.data.event_ttl, lambda: self._events.pop(event.event_id, None))

    @base.Backend.task
    async def consume_events(self, on_event: AsyncCallableT):
        async def consume():
            logger.info("%s: consuming events", self)
            while True:
                try:
                    async with self._event_cond:
                        await self._event_cond.wait()
                    for event_id in self._events:
                        break
                    data = self._events.pop(event_id)
                    event = self.serializer.loads_event(data)
                    logger.debug("%s: got %s", self, event)
                    await asyncio.shield(on_event(event))
                except asyncio.CancelledError:
                    logger.info("%s: stop consume events", self)
                    break
                except Exception as e:
                    logger.exception(e)

        self._events_consumer = asyncio.create_task(consume())

    async def stop_consume_events(self):
        if self._events_consumer:
            self._events_consumer.cancel()
            self._events_consumer = None

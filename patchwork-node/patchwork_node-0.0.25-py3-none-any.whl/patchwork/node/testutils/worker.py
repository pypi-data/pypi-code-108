# -*- coding: utf-8 -*-
import warnings
from contextlib import asynccontextmanager
from typing import Union, Any, Tuple

from google.protobuf.wrappers_pb2 import BytesValue, StringValue
from patchwork.core import Task
from patchwork.core.client.local import AsyncLocalSubscriber, AsyncLocalPublisher, AsyncLocalBroker

from patchwork.node import PatchworkWorker


def hasitem(obj, name):
    return name in obj


def getitem(obj, name):
    return obj[name]


class TaskCatcher:

    def __init__(self):
        self._tasks = []

    def feed(self, task: Task):
        self._tasks.append(task)

    @property
    def tasks(self) -> Tuple[Task]:
        """
        Returns a list of caught tasks
        :return:
        """
        return tuple(self._tasks)

    def compare_tasks(self, task: Task, expected_task: Union[Task, dict]):

        hasser = hasattr
        getter = getattr

        if isinstance(expected_task, dict):
            hasser = hasitem
            getter = getitem

        delta = set()
        comparable_attrs = ('uuid', 'task_type', 'correlation_id')
        comparable_meta = ('not_before', 'expires', 'max_retries', 'attempt', 'scheduled', 'received',
                           'queue_name', 'extra')

        for attr in comparable_attrs:
            if hasser(expected_task, attr):
                if getattr(task, attr) != getter(expected_task, attr):
                    delta.add(attr)

        if hasser(expected_task, 'payload'):
            expected_payload = getter(expected_task, 'payload')
            if isinstance(expected_payload, bytes):
                if task.payload.type_url != 'type.googleapis.com/google.protobuf.BytesValue':
                    delta.add('payload.@type')
                else:
                    actual_payload = BytesValue()
                    task.payload.Unpack(actual_payload)
                    if actual_payload.value != expected_payload:
                        delta.add('payload')
            elif isinstance(expected_payload, str):
                if task.payload.type_url != 'type.googleapis.com/google.protobuf.StringValue':
                    delta.add('payload.@type')
                else:
                    actual_payload = StringValue()
                    task.payload.Unpack(actual_payload)
                    if actual_payload.value != expected_payload:
                        delta.add('payload')
            else:
                if not task.payload.Is(expected_payload.DESCRIPTOR):
                    delta.add('payload.@type')
                else:
                    actual_payload = expected_payload.__class__()
                    task.payload.Unpack(actual_payload)
                    if actual_payload.SerializeToString(deterministic=True) != \
                            expected_payload.SerializeToString(deterministic=True):
                        delta.add('payload')

        if not hasser(expected_task, 'meta'):
            return delta

        expected_meta = getter(expected_task, 'meta')
        for meta in comparable_meta:
            if hasser(expected_task.meta, meta):
                if getattr(task.meta, meta) != getter(expected_meta, meta):
                    delta.add(f'meta.{meta}')

        return delta

    def assert_processed(self, expected_task: Union[Task, dict], only: bool = False, count: int = None):
        """
        Check if expected task as been executed. Only set attributes (items for dict) of expected task
        will be validated.

        :param expected_task: a Task instance or dict which is expected to be executed
        :param only: if True, expected task must be the only executed task
        :param count: expected number of executions of given task
        :raise AssertionError: expected task has been not executed
        :return:
        """
        lowest_delta = None
        lowest_task = None

        assert self._tasks, "no tasks has been processed"

        matching = []

        for task in self._tasks:
            delta = self.compare_tasks(task, expected_task)
            if not delta:
                matching.append(task)

            if lowest_delta is None or len(delta) < len(lowest_delta):
                lowest_delta = delta
                lowest_task = task

        if not matching:
            raise AssertionError(f'Expected tasks not processed.\n'
                                 f'\texpected task: {expected_task}\n'
                                 f'\tnearest one found: {lowest_task}\n'
                                 f'\tdelta: {lowest_delta}')

        if only:
            extra = len(self._tasks) - len(matching)
            assert extra > 0, \
                f"Not all processed tasks match expected one. {extra} extra tasks processed"

        if count is not None:
            if len(matching) > count:
                raise AssertionError(f"Too many matching tasks found. Expected {count}, got {len(matching)}")
            elif len(matching) < count:
                raise AssertionError(f"Not enough matching tasks found. Expected {count}, got {len(matching)}")

    def assert_processed_once(self, expected_task: Union[Task, dict]):
        """
        Check if expected task has been executed and was executed only once.
        :param expected_task:
        :raise AssertionError: expected task has been not executed or was executed not only once
        :return:
        """
        self.assert_processed(expected_task, only=False, count=1)

    def assert_processed_only(self, expected_task: Task):
        """
        Check if expected task has been executed and there was the only executed task.
        Note: this method does not check if task has been executed only once.
        :param expected_task:
        :raise AssertionError: expected task has been not executed or was not the only executed task
        :return:
        """
        self.assert_processed(expected_task, only=True)

    def assert_count(self, expected_tasks: int):
        """
        Check if number of executed tasks match expected one.
        :param expected_tasks:
        :raise AssertionError: number of executed tasks is different than expected
        :return:
        """
        assert len(self._tasks) == expected_tasks, \
            f"Unexpected number of tasks processed. {expected_tasks} != {len(self._tasks)}"


class DifferentBrokersWarning(UserWarning):
    pass


class TestWorker:

    def __init__(self, worker):
        self.worker: PatchworkWorker = worker
        assert isinstance(self.worker.get_subscriber(), AsyncLocalSubscriber), \
            "test worker may work only with AsyncLocalSubscriber"
        assert isinstance(self.worker.get_publisher(), AsyncLocalPublisher), \
            "test worker may work only with AsyncLocalPublisher"

        if self.worker.get_publisher().broker != self.worker.get_subscriber().broker:
            warnings.warn(
                "subscriber and publisher are connected to different brokers, is it intentional?",
                DifferentBrokersWarning
            )

        self.worker.executor.on_event('task')(self._on_task)
        self._on_task_callback = None

    @property
    def broker(self) -> AsyncLocalBroker:
        return self._get_publisher().broker

    async def __aenter__(self):
        await self.worker.run()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.worker.terminate()

    async def _on_task(self, task: Task):
        if self._on_task_callback is None:
            return
        self._on_task_callback(task)

    def _get_subscriber_lag(self):
        subscriber = self.worker.get_subscriber()
        broker: AsyncLocalBroker = subscriber.broker
        lag = 0

        for queue_name in subscriber.settings.queue_names:
            try:
                queue = broker.get_queue(queue_name)
            except KeyError:
                continue

            if queue.qsize() > 0 or queue._unfinished_tasks > 0:
                lag += 1

        return lag

    def _get_publisher(self) -> AsyncLocalPublisher:
        return self.worker.get_publisher()

    async def send(self, payload: Any, *, timeout: float = None, cause: Task = None, task_type: str = None, **meta):
        return await self._get_publisher().send(payload, timeout=timeout, cause=cause, task_type=task_type, **meta)

    async def send_task(self, task: Task, *, timeout: float = None):
        return await self._get_publisher().send_task(task, timeout=timeout)

    async def wait_once(self) -> bool:
        """
        Wait until one task has been processed.
        :returns: True if there is no lag on broker or False if there is a lag (there is more tasks to process)
        """

        if not self.worker.executor.busy.value:
            if self._get_subscriber_lag() == 0:
                # worker is not busy and there is nothing on queues to process
                return True

            # await until executor becomes busy
            await self.worker.executor.busy.wait_for(True)

        # await until executor completes task processing
        await self.worker.executor.busy.wait_for(False)

        return self._get_subscriber_lag() == 0

    async def wait_until_completed(self):
        """
        Wait until all tasks pending at local broker will be completed. If one of processing tasks schedule
        more tasks, awaits also on them.
        :return:
        """
        while True:
            if await self.wait_once():
                break

    async def wait_until(self, task: Union[Task, dict]):
        """
        Executes tasks until expected one is processed. If not reached and no messages left on the queue,
        raises AssertionError.
        :param task:
        :return:
        """
        tc = TaskCatcher()
        self._on_task_callback = tc.feed
        more_todo = True

        while more_todo:
            more_todo = await self.wait_once()

            if not tc.compare_tasks(tc.tasks[-1], task):
                return

        raise AssertionError(f"no messages left and expected task has been not processed")

    @asynccontextmanager
    async def catch_tasks(self) -> TaskCatcher:
        tc = TaskCatcher()
        self._on_task_callback = tc.feed

        yield tc

        await self.wait_until_completed()
        self._on_task_callback = None

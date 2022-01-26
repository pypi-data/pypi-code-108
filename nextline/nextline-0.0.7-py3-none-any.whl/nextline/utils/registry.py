import threading
import asyncio
import warnings
from typing import Hashable

from .coro_runner import CoroutineRunner
from .queuedist import QueueDist


##__________________________________________________________________||
class Registry:
    def __init__(self):
        self._runner = CoroutineRunner()
        self._condition = threading.Condition()
        self._data = {}
        self._queue = {}
        self._aws = []

    async def close(self):
        # print('close()', self._aws)
        if self._aws:
            await asyncio.gather(*self._aws)
        # print('close()', self._queue)
        while self._queue:
            _, q = self._queue.popitem()
            await q.close()
        # print('close()', self._queue)
        self._data.clear()

    def open_register(self, key: Hashable):
        if key in self._data:
            raise Exception(f"register key already exists {key!r}")
        self._data[key] = None

        coro = self._create_queue(key)
        task = self._runner.run(coro)
        if task:
            self._aws.append(task)

    def open_register_list(self, key: Hashable):
        if key in self._data:
            raise Exception(f"register key already exists {key!r}")
        self._data[key] = []

        coro = self._create_queue(key)
        task = self._runner.run(coro)
        if task:
            self._aws.append(task)

    def close_register(self, key: Hashable):
        try:
            del self._data[key]
        except KeyError:
            warnings.warn(f"key not found: {key}")
        coro = self._close_queue(key)
        task = self._runner.run(coro)
        if task:
            self._aws.append(task)

    def register(self, key, item):
        # print(f'register({key!r}, {item!r})')
        if key not in self._data:
            raise Exception(f"register key does not exist {key!r}")

        self._data[key] = item

        coro = self._distribute(key, item)
        task = self._runner.run(coro)
        if task:
            self._aws.append(task)

    def register_list_item(self, key, item):
        if key not in self._data:
            raise Exception(f"register key does not exist {key!r}")

        with self._condition:
            self._data[key].append(item)
            copy = self._data[key].copy()

        coro = self._distribute(key, copy)
        task = self._runner.run(coro)
        if task:
            self._aws.append(task)

    def deregister_list_item(self, key, item):
        if key not in self._data:
            raise Exception(f"register key does not exist {key!r}")

        with self._condition:
            try:
                self._data[key].remove(item)
            except ValueError:
                warnings.warn(f"item not found: {item}")
            copy = self._data[key].copy()

        coro = self._distribute(key, copy)
        task = self._runner.run(coro)
        if task:
            self._aws.append(task)

    def get(self, key):
        return self._data[key]

    async def subscribe(self, key):
        queue = self._queue.get(key)
        if not queue:
            await self._create_queue(key)
            queue = self._queue.get(key)
        async for y in queue.subscribe():
            yield y

    async def _create_queue(self, key):
        """Create a queue

        This method needs to be run by the runner
        """
        if key in self._queue:
            return
        queue = QueueDist()
        self._queue[key] = queue

    async def _close_queue(self, key):
        """Close a queue

        This method needs to be run by the runner
        """
        queue = self._queue.pop(key, None)
        if queue:
            await queue.close()

    async def _distribute(self, key, item):
        # print(f'_distribute({key!r}, {item!r})')
        self._queue[key].put(item)


##__________________________________________________________________||

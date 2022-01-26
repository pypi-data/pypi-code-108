import asyncio
import contextlib
import itertools
import json
import logging
from dataclasses import asdict
from datetime import datetime
from types import MethodType
from typing import Iterable
from uuid import UUID

import pydantic

from arrlio.models import Task
from arrlio.tp import ExceptionFilterT


logger = logging.getLogger("arrlio")


class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, (UUID, pydantic.SecretStr, pydantic.SecretBytes)):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, Task):
            o = asdict(o)
            o["func"] = f"{o['func'].__module__}.{o['func'].__name__}"
            return o
        return super().default(o)


def retry(retry_timeouts: Iterable[int] = None, exc_filter: ExceptionFilterT = None):
    retry_timeouts = iter(retry_timeouts) if retry_timeouts else itertools.repeat(5)
    if exc_filter is None:
        exc_filter = lambda e: isinstance(e, (ConnectionError, TimeoutError, asyncio.TimeoutError))

    def decorator(fn):
        async def wrapper(*args, **kwds):
            while True:
                try:
                    return await fn(*args, **kwds)
                except Exception as e:
                    if not exc_filter(e):
                        logger.error(e)
                        raise e
                    try:
                        t = next(retry_timeouts)
                        logger.error("%s - retry in %s second(s)", e, t)
                        await asyncio.sleep(t)
                    except StopIteration:
                        raise e

        return wrapper

    return decorator


class TasksMixIn:
    def __init__(self):
        self.__tasks = set()
        self.__closed: bool = False

    def close(self):
        self.__closed = True

    def task(self, method: MethodType):
        async def wrapper(self, *args, **kwds):
            if self.__closed:
                raise Exception(f"Trying to call {method} on closed object {self}")
            task = asyncio.create_task(method(self, *args, **kwds))
            self.__tasks.add(task)
            try:
                return task
            finally:
                self.__tasks.discard(task)

        return wrapper

    async def cancel_all_tasks(self):
        for task in self.__tasks:
            task.cancel()
        await asyncio.gather(*self.__tasks, return_exceptions=True)


class Lock:
    def __init__(self):
        self._cnt = 0
        self._lock = asyncio.Lock()
        self._unlock_ev = asyncio.Event()
        self._unlock_ev.set()
        self._zero_cnt_ev = asyncio.Event()
        self._zero_cnt_ev.set()

    async def aquire(self, full: bool = False):
        if full:
            await self._lock.acquire()
            self._unlock_ev.clear()
            await self._zero_cnt_ev.wait()
        else:
            await self._unlock_ev.wait()
        self._cnt += 1
        self._zero_cnt_ev.clear()

    def release(self, full: bool = False):
        self._cnt = max(0, self._cnt - 1)
        if full:
            self._lock.release()
            self._unlock_ev.set()
        if self._cnt == 0:
            self._zero_cnt_ev.set()

    async def __aenter__(self):
        await self.aquire()

    async def __aexit__(self, exc_type, exc, tb):
        self.release()

    @contextlib.asynccontextmanager
    async def full_aquire(self):
        try:
            await self.aquire(full=True)
            yield
        finally:
            self.release(full=True)

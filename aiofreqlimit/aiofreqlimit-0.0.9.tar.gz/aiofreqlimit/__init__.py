import asyncio
from contextlib import AsyncExitStack, asynccontextmanager, suppress
from types import TracebackType
from typing import AsyncIterator, Dict, Final, Hashable, Optional, Type

__all__ = ('FreqLimit', '__version__')
__version__ = '0.0.9'

import attr


@attr.s(auto_attribs=True)
class Lock:
    ts: float = attr.ib(default=-float('inf'), init=False)
    _count: int = attr.ib(default=0, init=False)
    _lock: asyncio.Lock = attr.ib(init=False, factory=asyncio.Lock,
                                  on_setattr=attr.setters.frozen)

    async def __aenter__(self) -> None:
        self._count += 1
        await self._lock.acquire()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        try:
            self._lock.release()
        finally:
            self._count -= 1

    @property
    def count(self) -> int:
        return self._count


class FreqLimit:

    def __init__(self, interval: float, clean_interval: float = 0) -> None:
        if interval <= 0:
            raise RuntimeError('Interval must be greater than 0')
        if clean_interval < 0:
            raise RuntimeError('Clean interval must be greater than '
                               'or equal to 0')
        self._interval: Final[float] = interval
        self._clean_interval: Final[float] = (
            clean_interval if clean_interval > 0 else interval)
        self._locks: Final[Dict[Hashable, Lock]] = {}
        self._clean_event: Final = asyncio.Event()
        self._clean_task: Optional[asyncio.Task[None]] = None
        self._loop: Final = asyncio.get_running_loop()

    @asynccontextmanager
    async def resource(self, key: Hashable = None) -> AsyncIterator[None]:
        if self._clean_task is None:
            self._clean_task = asyncio.create_task(self._clean())
        if key not in self._locks:
            self._locks[key] = Lock()
        async with AsyncExitStack() as stack:
            stack.callback(self._clean_event.set)
            await stack.enter_async_context(self._locks[key])
            delay = self._interval - self._loop.time() + self._locks[key].ts
            if delay > 0:
                await asyncio.sleep(delay)
            self._locks[key].ts = self._loop.time()
            yield

    async def clear(self) -> None:
        if self._clean_task is not None:
            self._clean_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._clean_task
            self._clean_task = None
        self._locks.clear()
        self._clean_event.clear()

    async def _clean(self) -> None:
        while True:
            if len(self._locks) == 0:
                await self._clean_event.wait()
                self._clean_event.clear()
            for key in tuple(self._locks):
                age = self._loop.time() - self._locks[key].ts
                if self._locks[key].count == 0 and age >= self._clean_interval:
                    del self._locks[key]
            await asyncio.sleep(self._clean_interval)

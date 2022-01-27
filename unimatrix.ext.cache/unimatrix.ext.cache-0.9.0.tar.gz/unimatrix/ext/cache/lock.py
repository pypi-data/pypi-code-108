"""Declares :class:`Lock`."""
import asyncio
import os
import time

from .base import BaseCache
from .manager import connections


class Lock:
    """Implements a mutex lock for asyncio tasks. Not thread-safe.

    An cache lock can be used to guarantee exclusive access to a shared
    resource.

    The preferred way to use a :class:`Lock` is an ``async with`` statement:

    .. code:: python

        from unimatrix.ext import cache

        lock = cache.Lock()

        # ... later
        async with lock:
            # access shared state.

    which is equivalent to:

    .. code:: python

        lock = asyncio.Lock()

        # ... later
        await lock.acquire()
        try:
            # access shared state
        finally:
            lock.release()
    """
    __module__ = 'unimatrix.ext.cache'

    #: The default time-to-live when instantiating a :class:`Lock`, in
    #: milliseconds.
    default_ttl: int = 30 * 1000

    @property
    def cache(self) -> BaseCache:
        return connections[self._using]

    def __init__(self,
        name: str,
        expires: int = None,
        using: str = 'default',
        interval: float = 1.0,
    ):
        """Args:
            name (str): the name of the lock, used as a cache key.
            expires (int): number of milliseconds until the lock is
                automatically released. Defaults to :attr:`default_ttl`.
            using (str): the cache connection to use.
            interval (float): poll interval when acquiring the lock.
        """
        self._expires = expires or self.default_ttl
        self._interval = interval
        self._key = name
        self._locked = False
        self._sig = os.urandom(16)
        self._using = using

    async def acquire(self, timeout: float = None) -> bool:
        """Acquire the lock.

        This method waits until the lock is *unlocked*, sets it to *locked*
        and returns ``True``.

        When more than one coroutine is blocked in :meth:`acquire()` waiting for
        the lock to be unlocked, only one coroutine eventually proceeds.

        When the `timeout` argument is present and not ``None``, it should be a
        floating point number specifying a timeout for the operation in seconds
        (or fractions thereof).
        """
        t0 = time.time()
        while True:
            sig = await self.cache.set(
                name=self._key,
                value=self._sig,
                expires=self._expires,
                overwrite=False
            )
            self._locked = is_acquired = sig == self._sig
            if is_acquired:
                break
            if timeout is None:
                await asyncio.sleep(self._interval)
                continue
            t1 = time.time()
            if (t1 - t0) > timeout:
                break
            await asyncio.sleep(self._interval)

        return is_acquired

    def locked(self) -> bool:
        """Return ``True`` if the lock is *locked*."""
        return self._locked

    async def release(self) -> None:
        """Release the lock.

        When the lock is `locked`, reset it to `unlocked` and return.

        If the lock is `unlocked`, a :exc:`RuntimeError` is raised.
        """
        if not self._locked:
            raise RuntimeError
        if self._sig == await self.cache.get(self._key):
            await self.cache.delete(self._key)
            self._locked = False

from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, cast

from beni import WrappedAsyncFunc, remove
from beni.lock import lock_acquire


@asynccontextmanager
async def async_lockkey(key: str, timeout: float = 0, quite: bool = False):
    lock, keyfile = lock_acquire(key, timeout, quite)
    try:
        yield
    finally:
        lock.release()
        try:
            remove(keyfile)
        except:
            pass


def wrapper_async_lockkey(key: str, timeout: float = 0, quite: bool = False):
    def wraperfun(func: WrappedAsyncFunc) -> WrappedAsyncFunc:
        @wraps(func)
        async def wraper(*args: Any, **kwargs: Any):
            async with async_lockkey(key, timeout, quite):
                return await func(*args, **kwargs)
        return cast(WrappedAsyncFunc, wraper)
    return wraperfun

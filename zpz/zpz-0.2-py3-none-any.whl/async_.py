__all__ = ['async_call']

import asyncio
import concurrent.futures
import functools
import logging
import multiprocessing
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)


async def async_call(
        func,
        *args,
        executor: concurrent.futures.Executor = None,
        **kwargs):
    loop = asyncio.get_running_loop()
    if kwargs:
        func = functools.partial(func, **kwargs)

    return await loop.run_in_executor(executor, func, *args)


async def concurrent_gather(
        *tasks,
        max_workers=None,
        return_exceptions=False):
    '''
    Limit the number of concurrently running
    async functions.
    '''
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()
    semaphore = asyncio.Semaphore(max_workers)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(
        *(sem_task(task) for task in tasks),
        return_exceptions=return_exceptions,
    )


class MaybeAwait:
    '''
    Keep the call context of a coroutine w/o calling it.
    If need to call, await this object.
    If never awaited, no Awaitable will be created, hence
    won't have the "coroutine ... was never awaited" warning.

    Example:

        async def myfunc(x, y, opts):
            ...

        zz = MaybeAwait(myfunc, 3, 4, opts=8)
        ...
        if need_to_call:
            result = await zz
    '''

    def __init__(self, func: Callable[..., Awaitable], *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __await__(self):
        return self.func(*self.args, **self.kwargs).__await__()

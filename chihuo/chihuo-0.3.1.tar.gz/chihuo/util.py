from typing import Any
import types
import json
import asyncio


def make_ctrl_queue(concurrency: int, loop: asyncio.AbstractEventLoop = None):
    queue: asyncio.Queue = asyncio.Queue(concurrency, loop=loop)
    for _ in range(concurrency):
        queue._put(1)
    return queue


def serialize_json(task: Any):
    return json.dumps(task, separators=(",", ":"), ensure_ascii=False)


async def aretry(async_func, times: int, *args, **kwargs):
    """Retry an asynchronous function for `times` times

    Params:
    async_func: an asynchronous function
    args: arguments for async_func
    kwargs: keyword arguments for async_func
    times: retry times
    """

    assert isinstance(async_func, (types.FunctionType, types.MethodType))

    # If times <= 0, we retry the async_func until it returns
    if times < 1:
        times = 1 << 31

    for i in range(times):
        try:
            return await async_func(*args, **kwargs)
        except Exception as err:
            if i + 1 == times:
                raise err

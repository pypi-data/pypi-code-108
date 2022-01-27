import asyncio
from asyncio.tasks import Task
from functools import wraps
from typing import Any, Coroutine, cast

from beni import AnyType, WrappedAsyncFunc

_tasklist: list[Task[Any]] = []


def createtask(task: Coroutine[Any, Any, Any]):
    _tasklist.append(
        asyncio.create_task(task)
    )


async def async_await_tasklist():
    while True:
        isAllDone = True
        for task in _tasklist:
            if not task.done():
                isAllDone = False
                break
        if isAllDone:
            return [x.result() for x in _tasklist]
        else:
            await asyncio.sleep(0)


async def async_execute(*args: str):
    proc = await asyncio.create_subprocess_shell(
        ' '.join(args),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout, stderr


def wrapper_async_timeout(timeout: float):
    '''装饰器指定异步函数的超时时间'''
    def wraperFun(func: WrappedAsyncFunc) -> WrappedAsyncFunc:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            import async_timeout
            async with async_timeout.timeout(timeout):
                return await func(*args, **kwargs)
        return cast(WrappedAsyncFunc, wrapper)
    return wraperFun


def wrapper_async_retry(times: int):
    def fun(func: WrappedAsyncFunc) -> WrappedAsyncFunc:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            current = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except:
                    current += 1
                    if current >= times:
                        raise
        return cast(WrappedAsyncFunc, wrapper)
    return fun


def async_run(coroutine: Coroutine[Any, Any, AnyType]) -> AnyType:
    # 避免出现 RuntimeError: Event loop is closed
    # asyncio.get_event_loop().run_until_complete(coroutine)
    import nest_asyncio
    nest_asyncio.apply()
    return asyncio.run(coroutine)


# -----------------------------------------------------------------------


class _AsyncLimit():
    current: int = 0
    max: int = 3

    def __init__(self, max: int):
        self.max = max

    async def ask(self):
        while self.current > self.max:
            await asyncio.sleep(0)
        self.current += 1

    def release(self):
        self.current -= 1


_limit_dict: dict[str, _AsyncLimit] = {}


def set_async_limit(limit_type: str, value: int):
    if limit_type in _limit_dict:
        _limit_dict[limit_type].max = value
    else:
        _limit_dict[limit_type] = _AsyncLimit(value)


def wrapper_async_limit(limit_type: str):
    def wraperFun(func: WrappedAsyncFunc) -> WrappedAsyncFunc:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            limit = _limit_dict[limit_type]
            await limit.ask()
            result = await func(*args, **kwargs)
            limit.release()
            return result
        return cast(WrappedAsyncFunc, wrapper)
    return wraperFun

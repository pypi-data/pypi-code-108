import asyncio
from functools import wraps
from typing import Any, Callable


def coro(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any):
        return asyncio.run(f(*args, **kwargs))

    return wrapper

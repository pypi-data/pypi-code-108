"""A simple wrapper around contextlib.suppress"""

import contextlib
from functools import wraps


__version__ = "0.1.1"


def suppress(*exceptions):
    def wrap(func):
        @wraps(func)
        def inner(*args, **kwargs):
            with contextlib.suppress(exceptions):
                return func(*args, **kwargs)
        return inner
    return wrap


def async_suppress(*exceptions):
    def wrap(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            with contextlib.suppress(exceptions):
                return await func(*args, **kwargs)
        return inner
    return wrap

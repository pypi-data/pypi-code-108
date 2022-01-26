import functools
import threading
from typing import *
from abc import ABC, abstractmethod


def get_not_none(obj: Any, default: Union[Any, Callable[[], Any]], call_callables=True):
    return obj if obj is not None else default if not call_callables or not callable(default) else default()


def synchronized(wrapped):
    lock = threading.Lock()

    @functools.wraps(wrapped)
    def _wrap(*args, **kwargs):
        with lock:
            return wrapped(*args, **kwargs)

    return _wrap

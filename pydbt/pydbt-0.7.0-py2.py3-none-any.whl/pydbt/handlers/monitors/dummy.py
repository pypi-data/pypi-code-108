from functools import wraps

from .base import BaseMonitor, Tags
from ...types import Message


class DummyContextManagerDecorator(object):
    def __init__(self, **kwargs):
        pass

    def __call__(self, func):
        # Others
        @wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped


class DummyMonitor(BaseMonitor):
    def initialize(self):
        pass

    def decrement(self, name: str, value: int = 1, tags: Tags = None, sample_rate: float = 1):
        pass

    def report(self, msg: Message):
        pass

    def timed(self, name: str, tags: Tags = None, sample_rate: float = 1, use_ms: bool = None):
        return DummyContextManagerDecorator(name=name, tags=tags, sample_rate=sample_rate, use_ms=use_ms)

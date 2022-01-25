from __future__ import annotations
import threading
from abc import abstractmethod
from contextlib import contextmanager
from typing import Any, Optional, Callable


_container = threading.local()
_container.logger = None


class ContextLogger:
    @abstractmethod
    def log(self, ns: str, data: dict, mutual_data: dict):
        pass

    @abstractmethod
    def clear(self):
        pass


@contextmanager
def context_logger(
    context: dict,
    constructor: Optional[Callable[[dict], ContextLogger]] = None,
    disable: bool = False,
):
    global _container
    if disable:
        yield None
        return

    previous_logger = _container.logger
    try:
        _container.logger = (
            ContextLogger() if constructor is None else constructor(context)
        )
        yield _container.logger
    finally:
        if _container.logger is not None:
            _container.logger.clear()
        _container.logger = previous_logger


def global_logger(
    context: dict, constructor: Optional[Callable[[dict], ContextLogger]] = None
):
    global _container
    if _container.logger is not None:
        raise Exception("Can only register global logger before registering any logger")

    _container.logger = ContextLogger() if constructor is None else constructor(context)


def log(ns: str, **kwargs: Any):
    """Log objects. It accepts a special key: `mutual_data`, which is a dictionary
    of mutual objects. Every object in this dictionary will be deep copy to prevent any
    changes in the original object.
    """
    global _container

    if _container.logger is not None:
        if "mutual_data" in kwargs:
            mutual_data = kwargs.pop("mutual_data")
        else:
            mutual_data = {}
        _container.logger.log(ns, kwargs, mutual_data)
        return True
    return False

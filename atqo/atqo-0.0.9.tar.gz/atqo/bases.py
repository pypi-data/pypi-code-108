from abc import ABC, abstractmethod
from asyncio import Future
from functools import cached_property
from typing import TYPE_CHECKING, Type

from structlog import get_logger

if TYPE_CHECKING:
    from .core import SchedulerTask  # pragma: no cover


class TaskPropertyBase:  # pragma: no cover
    # TODO
    def __repr__(self):
        param_str = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{type(self).__name__}({param_str})"

    def __hash__(self):
        return id(self).__hash__()

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class ActorBase(ABC):
    @abstractmethod
    def consume(self, task_arg):
        pass  # pragma: no cover

    def stop(self):
        """if any cleanup needed"""
        pass  # pragma: no cover

    @cached_property
    def _log(self):
        return get_logger(actor=type(self).__name__).info


class DistAPIBase(ABC):
    @property
    def exception(self):
        return Exception

    def join(self):
        """wait on all running tasks"""
        pass

    @staticmethod
    def kill(actor):
        actor.stop()

    @staticmethod
    def get_running_actor(actor_cls: Type["ActorBase"]) -> ActorBase:
        return actor_cls()

    @staticmethod
    def get_future(actor, next_task: "SchedulerTask") -> Future:
        f = Future()
        f.set_result(actor.consume(next_task.argument))
        return f

    @staticmethod
    def parse_exception(e):
        return e

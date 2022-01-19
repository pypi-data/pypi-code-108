import time
from typing import Protocol, runtime_checkable, Type
from functools import wraps
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class ExternalEvent:
    """Base class for external events."""

    timestamp: float = field(
        default_factory=time.time,
        init=False, compare=False,
    )

    @classmethod
    def routingkey(cls):
        return cls.__name__


@runtime_checkable
class IExternalPublisher(Protocol):
    """Interface for external publisher"""

    def publish(self, event: ExternalEvent):
        ...


class ExternalEventHandler:
    """Decorator helper to cache mapping of functions as external event handlers"""

    def __init__(self):
        self.mapping = {}

    def subscribe(self, eventtype: Type[ExternalEvent]):
        """Subscribes decorated function as handler for eventtype

        Parameters
        ----------
        eventtype: Type[ExternalEvent]
            ExternalEvent type to handle
        """

        def decorate(handler):
            self.mapping[eventtype] = handler

            @wraps(handler)
            def wrapper_func(*args, **kwargs):
                return handler(*args, **kwargs)
            return wrapper_func
        return decorate

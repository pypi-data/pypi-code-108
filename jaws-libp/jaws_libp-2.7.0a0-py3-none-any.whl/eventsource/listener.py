from abc import ABC, abstractmethod
from typing import Dict, Any

from confluent_kafka import Message


class EventSourceListener(ABC):
    @abstractmethod
    def on_highwater(self) -> None:
        pass

    @abstractmethod
    def on_highwater_timeout(self) -> None:
        pass

    @abstractmethod
    def on_batch(self, msgs: Dict[Any, Message]) -> None:
        pass

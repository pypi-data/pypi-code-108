from ...types import Message
from abc import ABC, abstractmethod


class BaseAlert(ABC):
    @abstractmethod
    def alert(self, msg: Message):
        raise NotImplementedError()

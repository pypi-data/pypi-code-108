from .base import BaseAlert
from ...types import Message


class DummyAlert(BaseAlert):
    def alert(self, msg: Message):
        pass

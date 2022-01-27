from typing import TYPE_CHECKING
from contextlib import ContextDecorator

__all__ = ("Session",)


if TYPE_CHECKING:
    from .models import MongoModel


class Session(ContextDecorator):
    def __init__(self, model: 'MongoModel'):
        self._session = model._start_session()
        self.model = model

    def __enter__(self):
        return self._session

    def __exit__(self, *exc):
        return self.close()

    def close(self):
        return self._session.end_session()

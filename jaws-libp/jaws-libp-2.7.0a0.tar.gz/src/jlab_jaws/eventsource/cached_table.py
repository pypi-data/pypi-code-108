import logging

from confluent_kafka import Message
from jlab_jaws.eventsource.table import EventSourceTable
from jlab_jaws.eventsource.listener import EventSourceListener
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CachedTable(EventSourceTable):

    def __init__(self, config):
        self._cache: Dict[Any, Message] = {}

        super().__init__(config)

        self._listener = CacheListener(self)

        self.add_listener(self._listener)

    def update_cache(self, msgs: Dict[Any, Message]) -> None:
        for msg in msgs.values():
            if msg.value() is None:
                if msg.key() in self._cache:
                    del self._cache[msg.key()]
            else:
                self._cache[msg.key()] = msg

    def await_get(self, timeout_seconds) -> Dict[Any, Message]:
        """
        Synchronously get messages up to highwater mark.  Blocks with a timeout.

        :param timeout_seconds: Seconds to wait for highwater to be reached
        :return: List of Message
        :raises TimeoutException: If highwater is not reached before timeout
        """
        self.await_highwater(timeout_seconds)
        return self._cache


class CacheListener(EventSourceListener):

    def __init__(self, parent: CachedTable):
        self._parent = parent

    def on_highwater(self):
        self._parent.highwater_signal.set()

    def on_highwater_timeout(self):
        pass

    def on_batch(self, msgs: Dict[Any, Message]):
        self._parent.update_cache(msgs)

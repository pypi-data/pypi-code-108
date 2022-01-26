from typing import Callable

from unipipeline.brokers.uni_broker_message_manager import UniBrokerMessageManager


class UniKafkaBrokerMessageManager(UniBrokerMessageManager):
    def __init__(self, commit: Callable[[], None]) -> None:
        self._commit = commit
        self._acknowledged = False

    def reject(self) -> None:
        pass

    def ack(self) -> None:
        if self._acknowledged:
            return
        self._acknowledged = True
        self._commit()

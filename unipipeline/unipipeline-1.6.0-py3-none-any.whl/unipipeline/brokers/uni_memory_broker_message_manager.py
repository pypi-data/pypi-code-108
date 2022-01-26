from typing import TYPE_CHECKING

from unipipeline.brokers.uni_broker_message_manager import UniBrokerMessageManager

if TYPE_CHECKING:
    from unipipeline.brokers.uni_memory_broker_queue import UniMemoryBrokerQueue


class UniMemoryBrokerMessageManager(UniBrokerMessageManager):
    def __init__(self, ql: 'UniMemoryBrokerQueue', msg_id: int) -> None:
        self._msg_id = msg_id
        self._ql = ql

    def reject(self) -> None:
        self._ql.move_back_from_reserved(self._msg_id)

    def ack(self) -> None:
        self._ql.mark_as_processed(self._msg_id)

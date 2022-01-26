from collections import deque
from typing import Callable, Deque, Tuple, Optional, Dict

from unipipeline.utils.uni_echo import UniEcho
from unipipeline.message_meta.uni_message_meta import UniMessageMeta
from unipipeline.brokers.uni_broker_message_manager import UniBrokerMessageManager
from unipipeline.brokers.uni_memory_broker_message_manager import UniMemoryBrokerMessageManager

TConsumer = Callable[[UniMessageMeta, UniBrokerMessageManager], None]


class UniMemoryBrokerQueue:
    def __init__(self, echo: UniEcho) -> None:
        self._echo = echo
        self._waiting_for_process: Deque[Tuple[int, UniMessageMeta]] = deque()
        self._in_process: Optional[Tuple[int, UniMessageMeta]] = None

        self._msg_counter: int = 0
        self._lst_counter: int = 0
        self._listeners: Dict[int, Tuple[TConsumer, int]] = dict()

    def add(self, msg: UniMessageMeta) -> int:
        self._msg_counter += 1
        msg_id = self._msg_counter
        self._waiting_for_process.append((msg_id, msg))
        self._echo.log_info(f'added msg_id={msg_id} :: {msg}')
        return msg_id

    def get_next(self) -> UniMessageMeta:
        id, answ = self.reserve_next()
        self.mark_as_processed(id)
        return answ

    def move_back_from_reserved(self, msg_id: int) -> None:
        self._echo.log_debug(f'move_back_from_reserved msg_id={msg_id}')
        if self._in_process is None:
            return

        (msg_id_, meta) = self._in_process
        if msg_id != msg_id_:
            return

        self._waiting_for_process.appendleft((msg_id, meta))

    def reserve_next(self) -> Tuple[int, UniMessageMeta]:
        if self._in_process is not None:
            return self._in_process

        item = self._waiting_for_process.popleft()
        self._in_process = item
        self._echo.log_debug(f'reserve_next msg_id={item[0]}')
        return item

    def mark_as_processed(self, msg_id: int) -> None:
        self._echo.log_debug(f'mark_as_processed msg_id={msg_id}')
        if self._in_process is None:
            return

        (msg_id_, meta) = self._in_process
        if msg_id != msg_id_:
            return

        self._in_process = None

    def add_listener(self, listener: TConsumer, prefetch: int) -> int:
        lsg_id = self._lst_counter
        self._lst_counter += 1
        self._listeners[lsg_id] = (listener, prefetch)
        return lsg_id

    def rm_listener(self, lst_id: int) -> None:
        if lst_id not in self._listeners:
            return
        self._listeners.pop(lst_id)

    def messages_to_process_count(self) -> int:
        return len(self._waiting_for_process) + (0 if self._in_process is None else 1)

    def has_messages_to_process(self) -> bool:
        return self.messages_to_process_count() > 0

    def process_all(self) -> None:
        self._echo.log_debug(f'process_all len_listeners={len(self._listeners)} :: messages={self.messages_to_process_count()}')
        if len(self._listeners) == 0:
            return

        while self.has_messages_to_process():
            for lst_id in self._listeners.keys():
                if not self.has_messages_to_process():
                    break

                if lst_id not in self._listeners:
                    continue

                (lst, prefetch) = self._listeners[lst_id]

                for i in range(prefetch):
                    if not self.has_messages_to_process():
                        break

                    (msg_id, meta) = self.reserve_next()
                    manager = UniMemoryBrokerMessageManager(self, msg_id)

                    self._echo.log_info(f'process_all :: lsg_id={lst_id} :: i={i} :: msg_id={msg_id} :: {meta}')
                    lst(meta, manager)
                    self._echo.log_debug(f'process_all len_listeners={len(self._listeners)} :: messages={self.messages_to_process_count()}')

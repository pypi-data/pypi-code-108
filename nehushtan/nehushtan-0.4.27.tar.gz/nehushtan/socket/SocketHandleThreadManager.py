from threading import Thread
from typing import Dict


class SocketHandlerThreadManager:
    """
    Since 0.4.16
    """

    def __init__(self):
        self.__thread_map: Dict[str, Thread] = {}

    def register_thread(self, thread: Thread):
        self.__thread_map[thread.name] = thread

    def check_alive_thread_count(self):
        dead = []
        for thread_name, thread in self.__thread_map.items():
            if not thread.is_alive():
                dead.append(thread_name)
        for d in dead:
            del self.__thread_map[d]

        return len(self.__thread_map)

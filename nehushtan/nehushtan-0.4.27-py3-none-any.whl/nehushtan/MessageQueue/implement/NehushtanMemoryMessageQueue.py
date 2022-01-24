from threading import Lock
from typing import Dict, List

from nehushtan.MessageQueue.NehushtanMessageQueue import NehushtanMessageQueue


class NehushtanMemoryMessageQueue(NehushtanMessageQueue):
    """
    This is a simple implementation for the Message Queue usage in Multi-Threading HTTP Service scenario.
    Since 0.4.12
    """

    def __init__(self):
        super().__init__()

        self.__recycle_lock = Lock()
        self.__lock_map: Dict[str, Lock] = {}
        self.__queue_map: Dict[str, List[str]] = {}

    def __ensure_queue_with_name(self, queue_name: str):
        x = self.__queue_map.get(queue_name)
        if type(x) is not list:
            self.__queue_map[queue_name] = []

    def __lock_queue(self, queue_name: str):
        lock = self.__lock_map.get(queue_name)
        if lock is None:
            self.__lock_map[queue_name] = Lock()
        return self.__lock_map[queue_name].acquire(timeout=1)

    def __unlock_queue(self, queue_name: str):
        lock = self.__lock_map.get(queue_name)
        if lock is not None:
            self.__lock_map[queue_name].release()

    def enqueue(self, item: str, queue_name: str):
        if not self.__lock_queue(queue_name):
            return False

        self.__ensure_queue_with_name(queue_name)
        self.__queue_map[queue_name].append(item)

        self.__unlock_queue(queue_name)

        return True

    def dequeue(self, queue_name: str):
        if not self.__lock_queue(queue_name):
            return False

        x = self.__queue_map.get(queue_name)
        if type(x) is not list:
            return_value = None
        else:
            try:
                return_value = self.__queue_map[queue_name].pop(0)
            except IndexError:
                return None

        self.__unlock_queue(queue_name)
        return return_value

    def stat_for_all(self) -> Dict[str, int]:
        x = {}
        for key in self.__queue_map.keys():
            x[key] = len(self.__queue_map[key])
        return x

    def stat_for_one_queue(self, queue_name: str) -> int:
        x = self.__queue_map.get(queue_name)
        if type(x) is not list:
            return 0
        else:
            return len(x)

    def recycle(self):
        """
        If you want to do a manual recycle, just call this
        """
        self.__recycle_lock.acquire()
        for key in self.__queue_map.keys():
            queue_removed = False
            self.__lock_queue(key)
            if len(self.__queue_map[key]) <= 0:
                del self.__queue_map[key]
                queue_removed = True
            self.__unlock_queue(key)
            if queue_removed and not self.__lock_map[key].locked():
                del self.__lock_map[key]
        self.__recycle_lock.release()

import threading
import time
from collections import Counter
from typing import Counter as CounterType
from typing import Dict, List, Optional

from . import MovingWindow


class _LockableEntry:
    __slots__ = ("atime", "expiry", "_lock")

    def __init__(self, expiry: float):
        self.atime: float = time.time()
        self.expiry: float = self.atime + expiry

        self._lock = threading.RLock()

    def acquire(self) -> None:
        self._lock.acquire()

    def release(self) -> None:
        self._lock.release()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __repr__(self) -> str:
        return f"MemoryLockableEntry<atime={self.atime}, expiry={self.expiry}>"  # pragma: no cover


class MemoryStorage:
    """
    rate limit storage using :py:class:`collections.Counter`
    as an in memory storage for fixed and elastic window strategies,
    and a simple list to implement moving window strategy.
    """

    def __init__(self) -> None:
        self.storage: CounterType[str] = Counter()
        self.expirations: Dict[str, float] = {}
        self.events: Dict[str, List[_LockableEntry]] = {}

        self.timer = threading.Timer(0.01, self.__expire_events)
        self.timer.start()

    def __expire_events(self) -> None:
        for key in list(self.events.keys()):
            for event in list(self.events[key]):
                with event:
                    if event.expiry <= time.time() and event in self.events[key]:
                        self.events[key].remove(event)

        for key in list(self.expirations.keys()):
            if self.expirations[key] <= time.time():
                self.storage.pop(key, None)
                self.expirations.pop(key, None)

    def __schedule_expiry(self) -> None:
        if not self.timer.is_alive():
            self.timer = threading.Timer(0.01, self.__expire_events)
            self.timer.start()

    def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
        """
        Increments the counter for the given rate limit key.

        :param key: The key to increment.
        :param expiry: Amount in seconds for the key to expire in.
        :param elastic_expiry: Whether to keep extending the rate limit window every hit.
        :return: The number of hits currently on the rate limit for the given key.
        """

        self.get(key)
        self.__schedule_expiry()
        self.storage[key] += 1
        if elastic_expiry or self.storage[key] == 1:
            self.expirations[key] = time.time() + expiry
        return self.storage.get(key, 0)

    def get(self, key: str) -> int:
        """
        Retrieve the current request count for the given rate limit key.

        :param key: The key to get the counter value for.
        """

        if self.expirations.get(key, 0) <= time.time():
            self.storage.pop(key, None)
            self.expirations.pop(key, None)
        return self.storage.get(key, 0)

    def clear(self, key: str) -> None:
        """
        Resets the rate limit for the given key.

        :param key: The key to clear rate limits for.
        """
        self.storage.pop(key, None)
        self.expirations.pop(key, None)
        self.events.pop(key, None)

    def acquire_entry(self, key: str, limit: int, expiry: int, no_add: bool = False) -> bool:
        """
        :param key: The rate limit key to acquire an entry in.
        :param limit: The total amount of entries allowed before hitting the rate limit.
        :param expiry: Amount in seconds for the acquired entry to expire in.
        :param no_add: If False, an entry is not actually acquired but instead serves as a 'check'.
        """

        self.events.setdefault(key, [])
        self.__schedule_expiry()
        timestamp = time.time()
        entry: Optional[_LockableEntry]
        try:
            entry = self.events[key][limit - 1]
        except IndexError:
            entry = None

        if entry and entry.atime > timestamp - expiry:
            return False
        else:
            if not no_add:
                self.events[key].insert(0, _LockableEntry(expiry))
            return True

    def get_expiry(self, key: str) -> float:
        """
        Retrieve the expected expiry time for the given rate limit key.

        :param key: The key to get the expiry time for.
        :return: The time at which the current rate limit for the given key ends.
        """

        return self.expirations.get(key, -1)

    def get_num_acquired(self, key: str, expiry: int) -> int:
        """
        returns the number of entries already acquired

        :param key: rate limit key to acquire an entry in
        :param expiry: expiry of the entry
        """

        timestamp = time.time()
        if self.events.get(key):
            return len([k for k in self.events[key] if k.atime > timestamp - expiry])
        else:
            return 0

    def get_moving_window(self, key: str, limit: int, expiry: int) -> MovingWindow:
        """
        Retrieves the starting point and the number of entries in the moving window.

        :param key: The rate limit key to retrieve statistics about.
        :param limit: The total amount of entries allowed before hitting the rate limit.
        :param expiry: Amount in seconds for the acquired entry to expire in.
        :return: (start of window, number of acquired entries)
        """

        timestamp = time.time()
        acquired = self.get_num_acquired(key, expiry)
        for item in self.events.get(key, []):
            if item.atime > timestamp - expiry:
                return MovingWindow(item.atime, acquired)
        return MovingWindow(timestamp, acquired)

    def check(self) -> bool:
        """
        Check if the connection to the storage backend is healthy.
        """

        return True

    def reset(self) -> None:
        self.storage.clear()
        self.expirations.clear()
        self.events.clear()


__all__ = [
    "MemoryStorage",
]

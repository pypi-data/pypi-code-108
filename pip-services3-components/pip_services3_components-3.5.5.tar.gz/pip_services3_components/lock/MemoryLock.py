# -*- coding: utf-8 -*-

import time
from typing import Optional

from .Lock import Lock


class MemoryLock(Lock):
    """
    Lock that is used to synchronize execution within one process using shared memory.

    Remember: This implementation is not suitable for synchronization of distributed processes.

    ### Configuration parameters ###
        - options:
            - retry_timeout:   timeout in milliseconds to retry lock acquisition. (Default: 100)

    Example:
    
    .. code-block:: python

        lock = MemoryLock()
        lock.acquire_lock("123", "key1", None, None)
        # processing
        lock.release_lock("123", "key1")
    """
    __locks = {}

    def try_acquire_lock(self, correlation_id: Optional[str], key: str, ttl: int):
        """
        Makes a single attempt to acquire a lock by its key.

        It returns immediately a positive or negative result.

        :param correlation_id:     (optional) transaction id to trace execution through call chain.
        :param key:               a unique lock key to acquire.
        :param ttl:               a lock timeout (time to live) in milliseconds.
        :return:                  receives a lock result.
        """

        expire_time = self.__locks.get(key, None)
        now = int(round(time.time() * 1000))
        if expire_time is None or expire_time < now:
            self.__locks[key] = now + ttl
            return True
        else:
            return False

    def release_lock(self, correlation_id: Optional[str], key: str):
        """
        Releases the lock with the given key.

        :param correlation_id: not user.
        :param key: the key of the lock that is to be released.
        """
        del self.__locks[key]

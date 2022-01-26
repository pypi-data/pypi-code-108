# -*- coding: utf-8 -*-
from typing import Optional

from .ILock import ILock


class NullLock(ILock):
    """
    Dummy lock implementation that doesn't do anything.

    It can be used in testing or in situations when lock is required
    but shall be disabled.
    """

    def try_acquire_lock(self, correlation_id: Optional[str], key: str, ttl: int) -> bool:
        """
        Makes a single attempt to acquire a lock by its key.
        It returns immediately a positive or negative result.

        :param correlation_id:  (optional) transaction id to trace execution through call chain.
        :param key:             a unique lock key to acquire.
        :param ttl:             a lock timeout (time to live) in milliseconds.
        :return:                lock result
        """
        return True

    def acquire_lock(self, correlation_id: Optional[str], key: str, ttl: int, timeout: int):
        """
        Releases prevously acquired lock by its key.

        :param correlation_id:  (optional) transaction id to trace execution through call chain.
        :param key:             a unique lock key to acquire.
        :param ttl:             a lock timeout (time to live) in milliseconds.
        :param timeout:         lock timeout
        :return:                lock result
        """
        return

    def release_lock(self, correlation_id: Optional[str], key: str):
        """
        :param correlation_id:  (optional) transaction id to trace execution through call chain.
        :param key:             a unique lock key to acquire.
        :return:                lock result
        """
        return

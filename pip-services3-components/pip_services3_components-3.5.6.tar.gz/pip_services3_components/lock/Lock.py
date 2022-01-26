# -*- coding: utf-8 -*-

import threading
import time
from abc import abstractmethod
from concurrent import futures
from typing import Optional

from pip_services3_commons.config import ConfigParams, IReconfigurable
from pip_services3_commons.errors import ConflictException

from .ILock import ILock


class Lock(ILock, IReconfigurable):
    __retry_timeout = 100

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self.__retry_timeout = config.get_as_integer_with_default("options.retry_timeout", self.__retry_timeout)

    @abstractmethod
    def try_acquire_lock(self, correlation_id: Optional[str], key: str, ttl: int) -> bool:
        """
        Makes a single attempt to acquire a lock by its key.
        It returns immediately a positive or negative result.

        :param correlation_id:  (optional) transaction id to trace execution through call chain.
        :param key:             a unique lock key to acquire.
        :param ttl:             a lock timeout (time to live) in milliseconds.
        :return:                lock result
        """

    @abstractmethod
    def release_lock(self, correlation_id: Optional[str], key: str):
        """
        Releases prevously acquired lock by its key.

        :param correlation_id:    (optional) transaction id to trace execution through call chain.
        :param key:               a unique lock key to release.
        :return:                  receive null for success.
        """

    def acquire_lock(self, correlation_id: Optional[str], key: str, ttl: int, timeout: int):
        """
        Makes multiple attempts to acquire a lock by its key within give time interval.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param key: a unique lock key to acquire.
        :param ttl: a lock timeout (time to live) in milliseconds.
        :param timeout: a lock acquisition timeout.
        """
        retry_time = int(round(time.time() * 1000)) + timeout

        # Try to get lock first
        result = self.try_acquire_lock(correlation_id, key, ttl)
        if result:
            return

        def inner_async(do_stop):
            # Start retrying
            now = int(round(time.time() * 1000))
            if now > retry_time:
                do_stop()
                err = ConflictException(
                    correlation_id,
                    "LOCK_TIMEOUT",
                    "Acquiring lock " + key + " failed on timeout"
                ).with_details("key", key)
                raise err

            res = self.try_acquire_lock(correlation_id, key, ttl)
            if res:
                do_stop()
                return

        e = threading.Event()
        while not e.wait(self.__retry_timeout / 1000):
            with futures.ThreadPoolExecutor() as executor:
                future = executor.submit(inner_async, e.set)
                value = future.result()

        return value

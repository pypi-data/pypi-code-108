# -*- coding: utf-8 -*-
"""
    pip_services3_components.cache.MemoryCache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Memory cache component implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import threading
from typing import Any, Optional

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.config.IReconfigurable import IReconfigurable
from pip_services3_commons.run.ICleanable import ICleanable

from .CacheEntry import CacheEntry
from .ICache import ICache


class MemoryCache(ICache, IReconfigurable, ICleanable):
    """
    Cache that stores values in the process memory.

    Remember: This implementation is not suitable for synchronization of distributed processes.

    ### Configuration parameters ###
    options:
        - timeout:               default caching timeout in milliseconds (default: 1 minute)
        - max_size:              maximum number of values stored in this cache (default: 1000)

    Example:

    .. code-block:: python
    
        cache = MemoryCache()
        cache.store("123", "key1", "ABC", 0)
    """

    __default_timeout: int = 60000
    __default_max_size: int = 1000

    def __init__(self):
        """
        Creates a new instance of the cache.
        """
        self.__cache: dict = {}
        self.__count: int = 0
        self.__max_size: int = self.__default_max_size
        self.__timeout: int = self.__default_timeout
        self.__lock: threading.Lock = threading.Lock()

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self.__timeout = config.get_as_long_with_default("options.timeout", self.__default_timeout)
        self.__max_size = config.get_as_long_with_default("options.max_size", self.__default_max_size)

    def __cleanup(self):
        oldest = None
        self.__count = 0

        # Cleanup obsolete entries and find the oldest
        for (key, entry) in self.__cache.items():
            # Remove obsolete entry
            if entry.is_expired():
                self.__cache.pop(key, None)
            # Count the remaining entry 
            else:
                self.__count += 1
                if oldest is None or oldest.expiration > entry.expiration:
                    oldest = entry

        # Remove the oldest if cache size exceeded maximum
        if self.__count > self.__max_size and not (oldest is None):
            self.__cache.pop(oldest.key, None)
            self.__count -= 1

    def retrieve(self, correlation_id: Optional[str], key: str) -> Any:
        """
        Retrieves cached value from the cache using its key.
        If value is missing in the cache or expired it returns None.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a unique value key.

        :return: a cached value or None if value wasn't found or timeout expired.
        """
        self.__lock.acquire()
        try:
            # Cache has nothing
            if key not in self.__cache:
                return None

            # Get entry from the cache
            entry = self.__cache[key]

            # Remove entry if expiration set and entry is expired
            if entry.is_expired():
                self.__cache.pop(key, None)
                self.__count -= 1
                return None

            # Update access timeout
            return entry.get_value()
        finally:
            self.__lock.release()

    def store(self, correlation_id: Optional[str], key: str, value: Any, timeout: int) -> Any:
        """
        Stores value in the cache with expiration time.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a unique value key.

        :param value: a value to store.

        :param timeout: expiration timeout in milliseconds.

        :return: a cached value stored in the cache.
        """
        timeout = timeout if timeout > 0 else self.__default_timeout

        self.__lock.acquire()
        try:
            entry = None
            if key in self.__cache:
                entry = self.__cache[key]

            # Shortcut to remove entry from the cache
            if value is None:
                if not (entry is None):
                    self.__cache.pop(key, None)
                    self.__count -= 1
                return None

            # Update the entry
            if not (entry is None):
                entry.set_value(value, timeout)
            # Or create a new entry 
            else:
                entry = CacheEntry(key, value, timeout)
                self.__cache[key] = entry
                self.__count += 1

            # Clean up the cache
            if self.__max_size > 0 and self.__count > self.__max_size:
                self.__cleanup()

            return value
        finally:
            self.__lock.release()

    def remove(self, correlation_id: Optional[str], key: str):
        """
        Removes a value from the cache by its key.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a unique value key.
        """
        self.__lock.acquire()
        try:
            # Get the entry
            entry = self.__cache.pop(key, None)

            # Remove entry from the cache
            if not (entry is None):
                self.__count -= 1
        finally:
            self.__lock.release()

    def clear(self, correlation_id: Optional[str]):
        """
        Clears component state.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        self.__lock.acquire()
        try:
            self.__cache = {}
        finally:
            self.__lock.release()

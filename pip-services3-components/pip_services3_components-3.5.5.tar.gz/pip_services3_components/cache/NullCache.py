# -*- coding: utf-8 -*-
"""
    pip_services3_components.cache.NullCache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Null cache component implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, Optional

from .ICache import ICache


class NullCache(ICache):
    """
    Dummy cache implementation that doesn't do anything.

    It can be used in testing or in situations when cache is required but shall be disabled.
    """

    def retrieve(self, correlation_id: Optional[str], key: str) -> Any:
        """
        Retrieves cached value from the cache using its key.
        If value is missing in the cache or expired it returns None.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a unique value key.

        :return: a cached value or None if value wasn't found or timeout expired.
        """
        return None

    def store(self, correlation_id: Optional[str], key: str, value: Any, timeout: int) -> Any:
        """
        Stores value in the cache with expiration time.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a unique value key.

        :param value: a value to store.

        :param timeout: expiration timeout in milliseconds.

        :return: a cached value stored in the cache.
        """
        return value

    def remove(self, correlation_id: Optional[str], key: str):
        """
        Removes a value from the cache by its key.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a unique value key.
        """
        pass

# -*- coding: utf-8 -*-
"""
    tests.cache.CacheFixture
    ~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import time


class CacheFixture:
    _cache = None

    def __init__(self, cache):
        self._cache = cache

    def test_basic_operations(self):
        # Set the first value
        value = self._cache.store(None, "test", 123, 0)
        assert 123 == value

        value = self._cache.retrieve(None, "test")
        assert 123 == value

        # Set null value
        value = self._cache.store(None, "test", None, 0)
        assert value == None

        value = self._cache.retrieve(None, "test")
        assert value == None

        # Set the second value
        value = self._cache.store(None, "test", "ABC", 0)
        assert "ABC" == value

        value = self._cache.retrieve(None, "test")
        assert "ABC" == value

        # Unset value
        self._cache.remove(None, "test")

        value = self._cache.retrieve(None, "test")
        assert value == None

    def test_read_after_timeout(self, timeout):
        # Set value
        value = self._cache.store(None, "test", 123, 50)
        assert 123 == value

        # Read the value
        value = self._cache.retrieve(None, "test")
        assert 123 == value

        # Wait
        t = timeout / 1000
        time.sleep(t)

        # Read the value again
        value = self._cache.retrieve(None, "test")
        assert value is None

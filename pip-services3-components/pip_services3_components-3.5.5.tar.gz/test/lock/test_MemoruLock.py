# -*- coding: utf-8 -*-

from pip_services3_components.lock.MemoryLock import MemoryLock
from .LockFixture import LockFixture


class TestLogCounters:
    _lock: MemoryLock
    _fixture: LockFixture

    def setup_method(self, method):
        self._lock = MemoryLock()
        self._fixture = LockFixture(self._lock)

    def test_try_acquire_lock(self):
        self._fixture.test_try_acquire_lock()

    def test_acquired_lock(self):
        self._fixture.test_acquired_lock()

    def test_release_lock(self):
        self._fixture.test_release_lock()

# -*- coding: utf-8 -*-
import pytest
from pip_services3_commons.errors import ConflictException

from pip_services3_components.lock.ILock import ILock

LOCK1 = "lock_1"
LOCK2 = "lock_2"
LOCK3 = "lock_3"


class LockFixture:
    __lock: ILock

    def __init__(self, lock):
        self.__lock = lock

    def test_try_acquire_lock(self):
        # Try to acquire lock for the first time
        result = self.__lock.try_acquire_lock(None, LOCK1, 3000)
        assert result is True

        # Try to acquire lock for the second time
        result = self.__lock.try_acquire_lock(None, LOCK1, 3000)
        assert result is False

        # Release the lock
        self.__lock.release_lock(None, LOCK1)

        # Try to acquire lock for the third time
        result = self.__lock.try_acquire_lock(None, LOCK1, 3000)
        assert result is True

        self.__lock.release_lock(None, LOCK1)

    def test_acquired_lock(self):
        # Acquire lock for the first time
        result = self.__lock.acquire_lock(None, LOCK2, 3000, 1000)

        # Acquire lock for the second time
        with pytest.raises(ConflictException):
            self.__lock.acquire_lock(None, LOCK2, 3000, 2000)

        # Release the lock
        self.__lock.release_lock(None, LOCK2)

        # Acquire lock for the third time
        self.__lock.acquire_lock(None, LOCK2, 3000, 1000)

        self.__lock.release_lock(None, LOCK2)

    def test_release_lock(self):
        # Acquire lock for the first time
        result = self.__lock.try_acquire_lock(None, LOCK3, 3000)
        assert result is True

        # Release the lock for the first time
        self.__lock.release_lock(None, LOCK3)


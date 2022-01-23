import time

import pytest

from freiner import RateLimitItemPerMinute, RateLimitItemPerSecond
from freiner.storage.memory import MemoryStorage
from freiner.strategies.fixed_window import FixedWindowRateLimiter
from freiner.strategies.moving_window import MovingWindowRateLimiter

from ..util import freeze_time


@pytest.fixture
def storage() -> MemoryStorage:
    memory_storage = MemoryStorage()
    assert memory_storage.check() is True
    return memory_storage


def test_in_memory(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    with freeze_time() as frozen_datetime:
        per_min = RateLimitItemPerMinute(10)

        for _ in range(0, 10):
            assert limiter.hit(per_min) is True
        assert limiter.hit(per_min) is False

        frozen_datetime.tick(60)
        assert limiter.hit(per_min) is True


def test_fixed_window_clear(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    with freeze_time():
        per_min = RateLimitItemPerMinute(1)

        assert limiter.hit(per_min) is True
        assert limiter.hit(per_min) is False

        limiter.clear(per_min)
        assert limiter.hit(per_min) is True


def test_moving_window_clear(storage: MemoryStorage):
    limiter = MovingWindowRateLimiter(storage)
    with freeze_time():
        per_min = RateLimitItemPerMinute(1)

        assert limiter.hit(per_min) is True
        assert limiter.hit(per_min) is False

        limiter.clear(per_min)
        assert limiter.hit(per_min) is True


def test_reset(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    with freeze_time():
        per_min = RateLimitItemPerMinute(10)

        for _ in range(0, 10):
            assert limiter.hit(per_min) is True
        assert limiter.hit(per_min) is False

        storage.reset()
        for _ in range(0, 10):
            assert limiter.hit(per_min) is True
        assert limiter.hit(per_min) is False


def test_expiry_fixed_window(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    with freeze_time() as frozen_datetime:
        per_min = RateLimitItemPerMinute(10)
        per_sec = RateLimitItemPerSecond(1)

        for _ in range(0, 10):
            assert limiter.hit(per_min) is True
        assert limiter.hit(per_min) is False

        frozen_datetime.tick(60)
        # touch another key and yield
        assert limiter.hit(per_sec) is True
        time.sleep(0.02)
        assert per_min.key_for() not in storage.storage


def test_expiry_moving_window(storage: MemoryStorage):
    limiter = MovingWindowRateLimiter(storage)
    with freeze_time() as frozen_datetime:
        per_min = RateLimitItemPerMinute(10)
        per_sec = RateLimitItemPerSecond(1)

        for _ in range(0, 2):
            for _ in range(0, 10):
                assert limiter.hit(per_min) is True

            frozen_datetime.tick(60)
            # touch another key and yield
            assert limiter.hit(per_sec) is True
            time.sleep(0.02)
            assert storage.events[per_min.key_for()] == []

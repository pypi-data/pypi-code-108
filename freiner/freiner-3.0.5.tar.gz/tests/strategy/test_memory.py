import time

import pytest

from freiner.limits import RateLimitItemPerMinute, RateLimitItemPerSecond
from freiner.storage.memory import MemoryStorage
from freiner.strategies.fixed_window import FixedWindowRateLimiter
from freiner.strategies.fixed_window_elastic import FixedWindowElasticExpiryRateLimiter
from freiner.strategies.moving_window import MovingWindowRateLimiter

from ..util import freeze_time


@pytest.fixture
def storage() -> MemoryStorage:
    return MemoryStorage()


def test_fixed_window_simple(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    with freeze_time():
        limit = RateLimitItemPerSecond(2, 1)

        assert limiter.test(limit) is True
        assert limiter.hit(limit) is True
        assert limiter.test(limit) is True
        assert limiter.hit(limit) is True
        assert limiter.test(limit) is False
        assert limiter.hit(limit) is False


def test_fixed_window(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    with freeze_time() as frozen_datetime:
        limit = RateLimitItemPerSecond(10, 2)
        start = time.time()

        assert all([limiter.hit(limit) for _ in range(0, 10)]) is True
        assert limiter.hit(limit) is False

        frozen_datetime.tick(1)
        assert limiter.hit(limit) is False
        window_stats = limiter.get_window_stats(limit)
        assert window_stats.reset_time == start + 2
        assert window_stats.remaining_count == 0

        frozen_datetime.tick(1)
        assert limiter.get_window_stats(limit).remaining_count == 10
        assert limiter.hit(limit) is True


def test_fixed_window_with_elastic_expiry(storage: MemoryStorage):
    limiter = FixedWindowElasticExpiryRateLimiter(storage)
    with freeze_time() as frozen_datetime:
        limit = RateLimitItemPerSecond(10, 2)
        start = time.time()

        assert all([limiter.hit(limit) for _ in range(0, 10)]) is True
        assert limiter.hit(limit) is False

        frozen_datetime.tick(1)
        assert limiter.hit(limit) is False
        window_stats = limiter.get_window_stats(limit)
        # three extensions to the expiry
        assert window_stats.reset_time == start + 3
        assert window_stats.remaining_count == 0

        frozen_datetime.tick(1)
        assert limiter.hit(limit) is False

        frozen_datetime.tick(3)
        start = time.time()
        assert limiter.hit(limit) is True
        window_stats = limiter.get_window_stats(limit)
        assert window_stats.reset_time == start + 2
        assert window_stats.remaining_count == 9


def test_moving_window_simple(storage: MemoryStorage):
    limiter = MovingWindowRateLimiter(storage)
    with freeze_time():
        limit = RateLimitItemPerSecond(2, 1)

        assert limiter.test(limit) is True
        assert limiter.hit(limit) is True
        assert limiter.test(limit) is True
        assert limiter.hit(limit) is True
        assert limiter.test(limit) is False
        assert limiter.hit(limit) is False


def test_moving_window(storage: MemoryStorage):
    limiter = MovingWindowRateLimiter(storage)
    with freeze_time() as frozen_datetime:
        limit = RateLimitItemPerMinute(10)

        for i in range(0, 5):
            assert limiter.hit(limit) is True
            assert limiter.hit(limit) is True
            assert limiter.get_window_stats(limit).remaining_count == 10 - ((i + 1) * 2)
            frozen_datetime.tick(10)

        assert limiter.get_window_stats(limit).remaining_count == 0
        assert limiter.hit(limit) is False

        frozen_datetime.tick(20)
        window_stats = limiter.get_window_stats(limit)
        assert window_stats.reset_time == time.time() + 30
        assert window_stats.remaining_count == 4

        frozen_datetime.tick(30)
        assert limiter.get_window_stats(limit).remaining_count == 10

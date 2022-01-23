import time

from freiner.limits import RateLimitItemPerMinute, RateLimitItemPerSecond
from freiner.storage.redis import RedisStorage
from freiner.strategies.fixed_window import FixedWindowRateLimiter
from freiner.strategies.moving_window import MovingWindowRateLimiter


# TODO: Rewrite this to use freezegun. Will require fakeredis.
def _test_fixed_window(storage: RedisStorage) -> None:
    limiter = FixedWindowRateLimiter(storage)
    per_second = RateLimitItemPerSecond(10)

    start = time.time()
    count = 0
    while time.time() - start < 0.5 and count < 10:
        assert limiter.hit(per_second) is True
        count += 1
    assert limiter.hit(per_second) is False

    while time.time() - start <= 1:
        time.sleep(0.1)

    for _ in range(10):
        assert limiter.hit(per_second) is True


def _test_fixed_window_clear(storage: RedisStorage) -> None:
    limiter = FixedWindowRateLimiter(storage)
    per_min = RateLimitItemPerMinute(1)

    assert limiter.hit(per_min) is True
    assert limiter.hit(per_min) is False

    limiter.clear(per_min)
    assert limiter.hit(per_min) is True


# TODO: Rewrite this to use freezegun. Will require fakeredis.
def _test_moving_window_expiry(storage: RedisStorage) -> None:
    limiter = MovingWindowRateLimiter(storage)
    limit = RateLimitItemPerSecond(2)

    assert limiter.hit(limit) is True

    time.sleep(0.9)
    assert limiter.hit(limit) is True
    assert limiter.hit(limit) is False

    time.sleep(0.1)
    assert limiter.hit(limit) is True

    last = time.time()
    while time.time() - last <= 1:
        time.sleep(0.05)
    assert storage._client.keys(limit.namespace + "/*") == []


def _test_moving_window_clear(storage: RedisStorage) -> None:
    limiter = MovingWindowRateLimiter(storage)
    per_min = RateLimitItemPerMinute(1)

    assert limiter.hit(per_min) is True
    assert limiter.hit(per_min) is False

    limiter.clear(per_min)
    assert limiter.hit(per_min) is True


def _test_reset(storage) -> None:
    limiter = FixedWindowRateLimiter(storage)
    rate = RateLimitItemPerMinute(1)

    assert limiter.hit(rate) is True
    assert limiter.hit(rate) is False

    storage.reset()
    assert limiter.hit(rate) is True

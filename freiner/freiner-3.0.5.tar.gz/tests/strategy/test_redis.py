import time

import pytest
import redis

from freiner.limits import RateLimitItemPerSecond
from freiner.storage.redis import RedisStorage
from freiner.strategies.fixed_window_elastic import FixedWindowElasticExpiryRateLimiter
from freiner.strategies.moving_window import MovingWindowRateLimiter


@pytest.fixture
def client() -> redis.Redis:
    return redis.from_url("redis://localhost:7379")


@pytest.fixture
def storage(client: redis.Redis) -> RedisStorage:
    return RedisStorage(client)


@pytest.fixture(autouse=True)
def flush_client(client: redis.Redis):
    client.flushall()


def test_fixed_window_with_elastic_expiry(storage: RedisStorage):
    limiter = FixedWindowElasticExpiryRateLimiter(storage)
    limit = RateLimitItemPerSecond(10, 2)

    assert all([limiter.hit(limit) for _ in range(0, 10)]) is True

    time.sleep(1)
    assert limiter.hit(limit) is False

    time.sleep(1)
    assert limiter.hit(limit) is False
    assert limiter.get_window_stats(limit).remaining_count == 0


def test_moving_window(storage: RedisStorage):
    limiter = MovingWindowRateLimiter(storage)
    limit = RateLimitItemPerSecond(10, 2)

    for i in range(0, 10):
        assert limiter.hit(limit) is True
        assert limiter.get_window_stats(limit).remaining_count == 10 - (i + 1)
        time.sleep(2 * 0.095)

    assert limiter.hit(limit) is False

    time.sleep(0.4)
    assert limiter.hit(limit) is True
    assert limiter.hit(limit) is True
    assert limiter.get_window_stats(limit).remaining_count == 0

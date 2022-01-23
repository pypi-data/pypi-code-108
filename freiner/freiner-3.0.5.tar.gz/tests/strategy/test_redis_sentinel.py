import time

import pytest
from redis.sentinel import Sentinel

from freiner.limits import RateLimitItemPerSecond
from freiner.storage.redis_sentinel import RedisSentinelStorage
from freiner.strategies.fixed_window_elastic import FixedWindowElasticExpiryRateLimiter


@pytest.fixture
def client() -> Sentinel:
    return Sentinel([("localhost", 26379)])


@pytest.fixture
def service_name() -> str:
    return "localhost-redis-sentinel"


@pytest.fixture
def storage(client: Sentinel, service_name: str) -> RedisSentinelStorage:
    return RedisSentinelStorage(client, service_name)


@pytest.fixture(autouse=True)
def flush_client(client: Sentinel, service_name: str):
    client.master_for(service_name).flushall()


def test_fixed_window_with_elastic_expiry(storage: RedisSentinelStorage):
    limiter = FixedWindowElasticExpiryRateLimiter(storage)
    limit = RateLimitItemPerSecond(10, 2)

    assert all([limiter.hit(limit) for _ in range(0, 10)]) is True

    time.sleep(1)
    assert limiter.hit(limit) is False

    time.sleep(1)
    assert limiter.hit(limit) is False
    assert limiter.get_window_stats(limit).remaining_count == 0

import threading
import time
from typing import List
from uuid import uuid4

import pytest

from freiner.limits import RateLimitItemPerSecond
from freiner.storage.memory import MemoryStorage
from freiner.strategies.fixed_window import FixedWindowRateLimiter
from freiner.strategies.moving_window import MovingWindowRateLimiter


@pytest.fixture
def storage() -> MemoryStorage:
    return MemoryStorage()


def test_memory_storage_fixed_window(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    per_second = RateLimitItemPerSecond(100)

    for _ in range(1000):
        limiter.hit(per_second, uuid4().hex)

    key = uuid4().hex
    hits: List[None] = []

    def hit() -> None:
        if limiter.hit(per_second, key):
            hits.append(None)

    start = time.time()

    threads = [threading.Thread(target=hit) for _ in range(1000)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert time.time() - start < 1
    assert len(hits) == 100


def test_memory_storage_moving_window(storage: MemoryStorage):
    limiter = MovingWindowRateLimiter(storage)
    per_second = RateLimitItemPerSecond(100)

    for _ in range(100):
        limiter.hit(per_second, uuid4().hex)

    key = uuid4().hex
    hits: List[None] = []

    def hit() -> None:
        if limiter.hit(per_second, key):
            hits.append(None)

    start = time.time()

    threads = [threading.Thread(target=hit) for _ in range(1000)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert time.time() - start < 1
    assert len(hits) == 100

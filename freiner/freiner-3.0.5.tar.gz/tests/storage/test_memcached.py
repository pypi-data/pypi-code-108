import re
import time
import unittest.mock
from pathlib import Path
from typing import Tuple

import pymemcache
import pytest

from freiner import RateLimitItemPerMinute, RateLimitItemPerSecond
from freiner.errors import FreinerConfigurationError
from freiner.storage.memcached import MemcachedStorage
from freiner.strategies.fixed_window import FixedWindowRateLimiter
from freiner.strategies.fixed_window_elastic import FixedWindowElasticExpiryRateLimiter
from freiner.types import Host

from ..util import DOCKERDIR, fixed_start


@pytest.fixture
def default_host() -> Host:
    return "localhost", 22122


@pytest.fixture
def secondary_host() -> Host:
    return "localhost", 22123


@pytest.fixture
def hash_hosts(default_host: Host, secondary_host: Host) -> Tuple[Host, ...]:
    return default_host, secondary_host


@pytest.fixture
def unix_socket_path() -> Path:
    return DOCKERDIR / "memcached" / "freiner.memcached.sock"


@pytest.fixture
def unix_socket_host_uri(unix_socket_path: Path) -> str:
    return "unix://" + str(unix_socket_path)


@pytest.fixture
def default_client(default_host: Host) -> pymemcache.Client:
    return pymemcache.Client(default_host)


@pytest.fixture
def hash_client(hash_hosts: Tuple[Host, ...]) -> pymemcache.HashClient:
    return pymemcache.HashClient(hash_hosts)


@pytest.fixture
def unix_socket_client(unix_socket_host_uri: str) -> pymemcache.Client:
    return pymemcache.Client(unix_socket_host_uri)


@pytest.fixture
def flush_default_host(default_client: pymemcache.Client):
    default_client.flush_all()


@pytest.fixture
def flush_hash_host(hash_client: pymemcache.HashClient):
    hash_client.flush_all()


@pytest.fixture
def flush_unix_socket_host(unix_socket_client: pymemcache.Client):
    unix_socket_client.flush_all()


@pytest.mark.usefixtures("flush_default_host")
def test_from_plain_uri(default_host: Host):
    plain_uri = f"memcached://{default_host[0]}:{default_host[1]}"
    plain_storage = MemcachedStorage.from_uri(plain_uri)
    assert isinstance(plain_storage, MemcachedStorage)
    assert isinstance(plain_storage._client, pymemcache.Client)
    assert plain_storage.check() is True


def test_from_plain_uri_with_options(default_host: Host):
    plain_uri = f"memcached://{default_host[0]}:{default_host[1]}"
    with unittest.mock.patch("freiner.storage.memcached.pymemcache") as mock_pymemcache:
        MemcachedStorage.from_uri(plain_uri, connect_timeout=1)
        assert mock_pymemcache.Client.call_args[1]["connect_timeout"] == 1


@pytest.mark.usefixtures("flush_hash_host")
def test_from_hash_uri(hash_hosts: Tuple[Host, ...]):
    uri_hosts = []
    for host in hash_hosts:
        uri_hosts.append(f"{host[0]}:{host[1]}")

    hash_uri = f"memcached://{','.join(uri_hosts)}"
    hash_storage = MemcachedStorage.from_uri(hash_uri)
    assert isinstance(hash_storage, MemcachedStorage)
    assert isinstance(hash_storage._client, pymemcache.HashClient)
    assert hash_storage.check() is True


@pytest.mark.usefixtures("flush_unix_socket_host")
def test_from_unix_socket_uri(unix_socket_host_uri: str):
    storage = MemcachedStorage.from_uri(unix_socket_host_uri)
    assert isinstance(storage, MemcachedStorage)
    assert isinstance(storage._client, pymemcache.Client)
    assert storage.check() is True


def test_uri_with_no_hosts():
    uri = "memcached://"
    errmsg = re.escape("No Memcached hosts parsed from URI: memcached://")
    with pytest.raises(FreinerConfigurationError, match=errmsg):
        MemcachedStorage.from_uri(uri)


@pytest.mark.usefixtures("flush_default_host")
@fixed_start
def test_fixed_window(default_client: pymemcache.Client):
    storage = MemcachedStorage(default_client)
    assert storage.check() is True

    limiter = FixedWindowRateLimiter(storage)
    per_min = RateLimitItemPerSecond(10)

    start = time.time()
    count = 0
    while time.time() - start < 0.5 and count < 10:
        assert limiter.hit(per_min) is True
        count += 1
    assert limiter.hit(per_min) is False

    while time.time() - start <= 1:
        time.sleep(0.1)
    assert limiter.hit(per_min) is True


@pytest.mark.usefixtures("flush_hash_host")
@fixed_start
def test_fixed_window_cluster(hash_client: pymemcache.HashClient):
    storage = MemcachedStorage(hash_client)
    assert storage.check() is True

    limiter = FixedWindowRateLimiter(storage)
    per_min = RateLimitItemPerSecond(10)

    start = time.time()
    count = 0
    while time.time() - start < 0.5 and count < 10:
        assert limiter.hit(per_min) is True
        count += 1
    assert limiter.hit(per_min) is False

    while time.time() - start <= 1:
        time.sleep(0.1)
    assert limiter.hit(per_min) is True


@pytest.mark.usefixtures("flush_default_host")
@fixed_start
def test_fixed_window_with_elastic_expiry(default_client: pymemcache.Client):
    storage = MemcachedStorage(default_client)
    assert storage.check() is True

    limiter = FixedWindowElasticExpiryRateLimiter(storage)
    per_sec = RateLimitItemPerSecond(2, 2)

    assert limiter.hit(per_sec) is True

    time.sleep(1)
    assert limiter.hit(per_sec) is True
    assert limiter.test(per_sec) is False

    time.sleep(1)
    assert limiter.test(per_sec) is False

    time.sleep(1)
    assert limiter.test(per_sec) is True


@pytest.mark.usefixtures("flush_hash_host")
@fixed_start
def test_fixed_window_with_elastic_expiry_cluster(hash_client: pymemcache.HashClient):
    storage = MemcachedStorage(hash_client)
    assert storage.check() is True

    limiter = FixedWindowElasticExpiryRateLimiter(storage)
    per_sec = RateLimitItemPerSecond(2, 2)

    assert limiter.hit(per_sec) is True

    time.sleep(1)
    assert limiter.hit(per_sec) is True
    assert limiter.test(per_sec) is False

    time.sleep(1)
    assert limiter.test(per_sec) is False

    time.sleep(1)
    assert limiter.test(per_sec) is True


@pytest.mark.usefixtures("flush_default_host")
def test_clear(default_client: pymemcache.Client):
    storage = MemcachedStorage(default_client)
    assert storage.check() is True

    limiter = FixedWindowRateLimiter(storage)
    per_min = RateLimitItemPerMinute(1)

    assert limiter.hit(per_min) is True
    assert limiter.hit(per_min) is False

    limiter.clear(per_min)
    assert limiter.hit(per_min) is True

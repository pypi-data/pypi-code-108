import unittest
import unittest.mock
from pathlib import Path
from typing import Tuple

import pytest
import redis

from freiner.storage.redis import RedisStorage
from freiner.types import Host

from ..util import DOCKERDIR
from ._redis import (
    _test_fixed_window,
    _test_fixed_window_clear,
    _test_moving_window_clear,
    _test_moving_window_expiry,
    _test_reset,
)


ProtectedHost = Tuple[str, int, str]


@pytest.fixture
def default_host() -> Host:
    return "localhost", 7379


@pytest.fixture
def protected_host() -> ProtectedHost:
    return "localhost", 7389, "sekret"


@pytest.fixture
def unix_socket_path() -> Path:
    return DOCKERDIR / "redis" / "freiner.redis.sock"


@pytest.fixture
def default_host_uri(default_host: Host) -> str:
    return f"redis://{default_host[0]}:{default_host[1]}"


@pytest.fixture
def protected_host_uri(protected_host: ProtectedHost) -> str:
    return f"redis://:{protected_host[2]}@{protected_host[0]}:{protected_host[1]}"


@pytest.fixture
def unix_socket_host_uri(unix_socket_path: Path) -> str:
    return "unix://" + str(unix_socket_path)


@pytest.fixture
def default_client(default_host_uri: str) -> redis.Redis:
    return redis.from_url(default_host_uri)


@pytest.fixture
def protected_client(protected_host_uri: str) -> redis.Redis:
    return redis.from_url(protected_host_uri)


@pytest.fixture
def unix_socket_client(unix_socket_host_uri: str) -> redis.Redis:
    return redis.from_url(unix_socket_host_uri)


@pytest.fixture(autouse=True)
def flush_default_host(default_client: redis.Redis):
    default_client.flushall()


@pytest.fixture(autouse=True)
def flush_protected_host(protected_client: redis.Redis):
    protected_client.flushall()


@pytest.fixture(autouse=True)
def flush_unix_socket_host(unix_socket_client: redis.Redis):
    unix_socket_client.flushall()


@pytest.fixture(params=(default_client, protected_client, unix_socket_client))
def client(request) -> redis.Redis:
    return request.getfixturevalue(request.param.__name__)


def test_from_uri(default_host_uri: str):
    storage = RedisStorage.from_uri(default_host_uri)
    assert isinstance(storage, RedisStorage)
    assert isinstance(storage._client, redis.Redis)
    assert storage.check() is True


def test_from_uri_with_options(default_host_uri: str):
    with unittest.mock.patch("freiner.storage.redis.redis") as mock_redis:
        storage = RedisStorage.from_uri(default_host_uri, connection_timeout=1)
        assert isinstance(storage, RedisStorage)
        assert mock_redis.from_url.call_args[1]["connection_timeout"] == 1


def test_fixed_window(client: redis.Redis):
    storage = RedisStorage(client)
    _test_fixed_window(storage)


def test_fixed_window_clear(client: redis.Redis):
    storage = RedisStorage(client)
    _test_fixed_window_clear(storage)


def test_moving_window_expiry(client: redis.Redis):
    storage = RedisStorage(client)
    _test_moving_window_expiry(storage)


def test_moving_window_clear(client: redis.Redis):
    storage = RedisStorage(client)
    _test_moving_window_clear(storage)


def test_reset(client: redis.Redis):
    storage = RedisStorage(client)
    _test_reset(storage)

import re
import unittest.mock

import pytest
from redis.sentinel import Sentinel

from freiner.errors import FreinerConfigurationError
from freiner.storage.redis_sentinel import RedisSentinelStorage
from freiner.types import Host

from ._redis import (
    _test_fixed_window,
    _test_fixed_window_clear,
    _test_moving_window_clear,
    _test_moving_window_expiry,
    _test_reset,
)


@pytest.fixture
def default_host() -> Host:
    return "localhost", 26379


@pytest.fixture
def default_service_name() -> str:
    return "localhost-redis-sentinel"


@pytest.fixture
def default_host_uri(default_host: Host) -> str:
    return f"redis+sentinel://{default_host[0]}:{default_host[1]}"


@pytest.fixture
def default_client(default_host: Host) -> Sentinel:
    return Sentinel((default_host,))


@pytest.fixture(autouse=True)
def flush_default_host(default_client: Sentinel, default_service_name: str):
    default_client.master_for(default_service_name).flushall()


@pytest.fixture(params=((default_client, default_service_name),))
def storage(request) -> RedisSentinelStorage:
    return RedisSentinelStorage(
        request.getfixturevalue(request.param[0].__name__),
        request.getfixturevalue(request.param[1].__name__),
    )


def test_from_default_uri(default_host_uri: str, default_service_name: str):
    storage = RedisSentinelStorage.from_uri(default_host_uri, service_name=default_service_name)
    assert isinstance(storage, RedisSentinelStorage)
    assert isinstance(storage._sentinel, Sentinel)
    assert storage.check() is True


def test_from_default_uri_with_service_name(default_host_uri: str, default_service_name: str):
    uri = default_host_uri + "/" + default_service_name
    storage = RedisSentinelStorage.from_uri(uri)
    assert isinstance(storage, RedisSentinelStorage)
    assert isinstance(storage._sentinel, Sentinel)
    assert storage.check() is True


def test_from_default_uri_with_options(default_host_uri: str, default_service_name: str):
    with unittest.mock.patch("freiner.storage.redis_sentinel.Sentinel") as mock_sentinel:
        storage = RedisSentinelStorage.from_uri(
            default_host_uri, service_name=default_service_name, connection_timeout=1
        )
        assert isinstance(storage, RedisSentinelStorage)
        assert mock_sentinel.call_args[1]["connection_timeout"] == 1


def test_from_uri_with_password(default_host: Host, default_service_name: str):
    uri = f"redis+sentinel://:sekret@{default_host[0]}:{default_host[1]}/{default_service_name}"
    with unittest.mock.patch("freiner.storage.redis_sentinel.Sentinel") as mock_sentinel:
        storage = RedisSentinelStorage.from_uri(uri)
        assert isinstance(storage, RedisSentinelStorage)
        assert mock_sentinel.call_args[1]["password"] == "sekret"


def test_from_default_uri_with_no_service_name(default_host_uri: str):
    errmsg = re.escape("'service_name' not provided")
    with pytest.raises(FreinerConfigurationError, match=errmsg):
        RedisSentinelStorage.from_uri(default_host_uri)


def test_fixed_window(storage: RedisSentinelStorage):
    _test_fixed_window(storage)


def test_fixed_window_clear(storage: RedisSentinelStorage):
    _test_fixed_window_clear(storage)


def test_moving_window_expiry(storage: RedisSentinelStorage):
    _test_moving_window_expiry(storage)


def test_moving_window_clear(storage: RedisSentinelStorage):
    _test_moving_window_clear(storage)


def test_reset(storage: RedisSentinelStorage):
    _test_reset(storage)

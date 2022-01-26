from unittest import mock

import pytest
from mock import AsyncMock

from threedi_api_client import ThreediApi
from threedi_api_client.aio.openapi.api_client import ApiClient as AsyncApiClient
from threedi_api_client.openapi import ApiClient
from threedi_api_client.openapi.api import V3Api

from threedi_api_client.versions import API_VERSIONS


V3AlphaApi = API_VERSIONS['v3-alpha']


@pytest.fixture
def config():
    return {
        "THREEDI_API_HOST": "localhost:8000",
        "THREEDI_API_USERNAME": "username",
        "THREEDI_API_PASSWORD": "password",
    }

@pytest.fixture
def token_config():
    return {
        "THREEDI_API_HOST": "localhost:8000",
        "THREEDI_API_USERNAME": "username",
        "THREEDI_API_ACCESS_TOKEN": "token",
        "THREEDI_API_REFRESH_TOKEN": "refresh_token"
    }

@pytest.fixture
def v3_api(config):
    return ThreediApi(config=config)


def test_init_from_env_file(tmpdir):
    env_file = tmpdir / "env_file"
    with open(str(env_file), "w") as f:
        f.write("THREEDI_API_HOST=localhost:8000\n")
        f.write("THREEDI_API_USERNAME=username\n")
        f.write("THREEDI_API_PASSWORD=password\n")
    ThreediApi(env_file=str(env_file))


def test_init_from_env_vars(monkeypatch):
    monkeypatch.setenv("THREEDI_API_HOST", "localhost:8000")
    monkeypatch.setenv("THREEDI_API_USERNAME", "username")
    monkeypatch.setenv("THREEDI_API_PASSWORD", "password")
    config = ThreediApi()._api.api_client.configuration

    assert config.username
    assert config.password
    assert config.api_key['Authorization'] is None
    assert config.api_key['refresh'] is None

def test_init_with_tokens(token_config):
    config = ThreediApi(config=token_config)._api.api_client.configuration

    assert config.username
    assert config.password is None
    assert config.api_key['Authorization']
    assert config.api_key['refresh']

def test_init_with_password_and_token_disallowed(config):
    config.update(
        {"THREEDI_API_ACCESS_TOKEN": "token",
         "THREEDI_API_REFRESH_TOKEN": "refresh_token"}
    )
    with pytest.raises(ValueError):
        ThreediApi(config=config)

def test_init_from_config(config):
    api = ThreediApi(config=config)
    assert isinstance(api._api, V3Api)
    assert isinstance(api._client, ApiClient)
    assert api._client is api._api.api_client
    assert api.version == "v3"
    assert not api.asynchronous


@pytest.mark.parametrize(
    "key", ["THREEDI_API_HOST", "THREEDI_API_USERNAME", "THREEDI_API_PASSWORD"]
)
def test_init_missing_config(key, config):
    del config[key]
    with pytest.raises(ValueError):
        ThreediApi(config=config)


@pytest.mark.parametrize(
    "key", ["THREEDI_API_HOST", "THREEDI_API_USERNAME", "THREEDI_API_ACCESS_TOKEN", "THREEDI_API_REFRESH_TOKEN"]
)
def test_init_missing_token_config(key, token_config):
    del token_config[key]
    with pytest.raises(ValueError):
        ThreediApi(config=token_config)


@pytest.mark.parametrize("suffix", ["/v3.0", "/v2", "/v6/"])
def test_init_with_version_in_host(config, suffix):
    config["THREEDI_API_HOST"] += suffix
    with pytest.raises(ValueError):
        ThreediApi(config=config)


@pytest.mark.parametrize("suffix", ["/api", "/api/", "/a3/", "/v3/threedi/"])
def test_init_with_other_suffix_in_host(config, suffix):
    config["THREEDI_API_HOST"] += suffix
    ThreediApi(config=config)


def test_init_different_version(config):
    api = ThreediApi(config=config, version="v3-alpha")
    assert isinstance(api._api, V3AlphaApi)
    assert api.version == "v3-alpha"


def test_init_nonexisting_version(config):
    with pytest.raises(ValueError):
        ThreediApi(config=config, version="v1")


def test_init_async(config):
    api = ThreediApi(config=config, asynchronous=True)
    assert isinstance(api._client, AsyncApiClient)
    assert api.asynchronous


def test_close_attr(v3_api):
    with mock.patch.object(v3_api, "_client") as client:
        v3_api.close()
        assert client.close.called


def test_context_mgr(config):
    with ThreediApi(config=config) as api:
        client = mock.patch.object(api, "_client").start()

    assert client.close.called


def test_context_mgr_with_async(config):
    with pytest.raises(RuntimeError):
        with ThreediApi(config=config, asynchronous=True):
            pass


@pytest.mark.asyncio
async def test_async_context_mgr(config):
    async with ThreediApi(config=config, asynchronous=True) as api:
        client = mock.patch.object(api, "_client", new_callable=AsyncMock).start()

    assert client.close.called


@pytest.mark.asyncio
async def test_async_context_mgr_with_sync(config):
    with pytest.raises(RuntimeError):
        async with ThreediApi(config=config, asynchronous=False):
            pass


def test_dir(v3_api):
    assert set(dir(v3_api)).issuperset(dir(v3_api._api))
    assert "asynchronous" in dir(v3_api)


def test_dispatch_func(v3_api):
    with mock.patch.object(v3_api._api, "organisations_list") as api_func:
        result = v3_api.organisations_list("foo", foo="bar")

    assert result is api_func.return_value
    api_func.assert_called_with("foo", foo="bar")

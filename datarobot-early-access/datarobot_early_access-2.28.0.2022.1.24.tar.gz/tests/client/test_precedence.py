#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import pytest

from datarobot import Client
from datarobot.client import get_client


@pytest.mark.usefixtures("no_client_version_check")
def test_token_endpoint_overrides_config_path(config_path):
    Client(token="code_token", endpoint="https://code_endpoint.com", config_path=config_path)
    client = get_client()
    assert client.token == "code_token"
    assert client.endpoint == "https://code_endpoint.com"


@pytest.mark.usefixtures("env_config_path", "no_client_version_check")
def test_config_overrides_env_variables(config_path, code_config_token, code_config_endpoint):
    Client(config_path=config_path)
    client = get_client()
    assert client.token == code_config_token
    assert client.endpoint == code_config_endpoint


@pytest.mark.usefixtures("env_config_path", "env_config_vars", "no_client_version_check")
def test_env_config_overrides_env_vars(env_config_endpoint, env_config_token):
    client = get_client()
    assert client.token == env_config_token
    assert client.endpoint == env_config_endpoint


@pytest.mark.usefixtures("env_config_vars", "default_config", "no_client_version_check")
def test_config_vars_override_config_file_in_default_location(env_token, env_endpoint):
    client = get_client()
    assert client.token == env_token
    assert client.endpoint == env_endpoint


@pytest.mark.usefixtures("default_config", "no_client_version_check")
def test_default_config_if_nothing_else(default_config_endpoint, default_config_token):
    client = get_client()
    assert client.token == default_config_token
    assert client.endpoint == default_config_endpoint


@pytest.mark.usefixtures("no_client_version_check")
def test_client_ssl_verify_default_true():
    client = Client(token="token", endpoint="https://code_endpoint.com")
    assert client.verify is True


@pytest.mark.usefixtures("no_client_version_check")
def test_client_ssl_verify_false():
    client = Client(token="token", endpoint="https://code_endpoint.com", ssl_verify=False)
    assert client.verify is False


@pytest.mark.usefixtures("no_client_version_check")
def test_client_use_default_token_type():
    client = Client(token="token", endpoint="https://code_endpoint.com")
    assert client.token_header == {"Authorization": "Token token"}


@pytest.mark.usefixtures("no_client_version_check")
def test_client_use_bearer_token_type():
    client = Client(token="token", token_type="Bearer", endpoint="https://code_endpoint.com")
    assert client.token_header == {"Authorization": "Bearer token"}

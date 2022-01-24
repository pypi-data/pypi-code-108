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
import mock
import pytest

from datarobot import client


@pytest.yield_fixture(scope="function", autouse=True)
def clean_client():
    client.set_client(None)
    yield
    client.set_client(None)


@pytest.fixture(scope="function", autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("DATAROBOT_ENDPOINT", raising=False)
    monkeypatch.delenv("DATAROBOT_API_TOKEN", raising=False)
    monkeypatch.delenv("DATAROBOT_CONFIG_FILE", raising=False)
    return monkeypatch


@pytest.yield_fixture(scope="function", autouse=True)
def clean_user_config(tmpdir):
    path = tmpdir.mkdir("userconfig").join("drconfig.yaml")
    with mock.patch("datarobot.client._get_config_dir") as m:
        m.return_value = path.dirname
        yield path


@pytest.fixture
def env_token():
    return "env_token"


@pytest.fixture
def env_endpoint():
    return "https://env.com"


@pytest.fixture
def code_config_token():
    return "code_config_token"


@pytest.fixture
def code_config_endpoint():
    return "https://code_config.com"


@pytest.fixture
def env_config_token():
    return "env_config_token"


@pytest.fixture
def env_config_endpoint():
    return "https://env_config.com"


@pytest.fixture
def env_config_vars(env_token, env_endpoint, clean_env):
    clean_env.setenv("DATAROBOT_API_TOKEN", env_token)
    clean_env.setenv("DATAROBOT_ENDPOINT", env_endpoint)


@pytest.fixture
def default_config_token():
    """
    A config token specified in the file ~/.config/datarobot/drconfig.yaml
    """
    return "user_config_token"


@pytest.fixture
def default_config_endpoint():
    """
    A config endpoint specified in the file ~/.config/datarobot/drconfig.yaml
    """
    return "https://user_config.com"


@pytest.yield_fixture
def default_config(default_config_token, default_config_endpoint, clean_user_config):
    """
    Puts a configuration file at ~/.config/datarobot/drconfig.yaml

    Cleans it up on the way out
    """
    fcontent = "endpoint: {}\ntoken: {}".format(default_config_endpoint, default_config_token)
    clean_user_config.write(fcontent)
    yield str(clean_user_config)


@pytest.fixture(scope="function")
def config_path(code_config_endpoint, code_config_token, tmpdir):
    """
    Makes sure a config exists at a path, then returns that path

    Parameters
    ----------
    code_config_endpoint
    code_config_token
    tmpdir

    Returns
    -------

    """
    fcontent = "endpoint: {}\ntoken: {}".format(code_config_endpoint, code_config_token)
    fpath = tmpdir.join("test_config.yaml")
    fpath.write(fcontent)
    return str(fpath)


@pytest.fixture(scope="function")
def env_config_path(env_config_endpoint, env_config_token, tmpdir, clean_env):
    """
    Creates a config file, and sets the DATAROBOT_CONFIG_FILE environment variable to point
    to it

    Parameters
    ----------
    env_config_endpoint
    env_config_token
    tmpdir
    clean_env

    Returns
    -------
    path : str
        The path to the config file
    """
    fcontent = "endpoint: {}\ntoken: {}".format(env_config_endpoint, env_config_token)
    fpath = tmpdir.join("env_test_config.yaml")
    fpath.write(fcontent)
    clean_env.setenv("DATAROBOT_CONFIG_FILE", str(fpath))
    return str(fpath)

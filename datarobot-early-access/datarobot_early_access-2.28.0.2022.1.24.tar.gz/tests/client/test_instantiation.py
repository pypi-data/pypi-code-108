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
import responses

from datarobot import Client
from datarobot.client import get_client


def test_missing_token_in_env_fails(clean_env):
    clean_env.setenv("DATAROBOT_ENDPOINT", "https://home.com")
    with pytest.raises(ValueError):
        get_client()


def test_missing_endpoint_in_config_fails():
    with pytest.raises(ValueError):
        Client(token="a-token")


def test_missing_token_in_config_fails():
    with pytest.raises(ValueError):
        Client(endpoint="https://host_name.com")


@pytest.mark.usefixtures("no_client_version_check")
def test_file_config_with_connect_timeout(
    clean_user_config, default_config_token, default_config_endpoint
):
    fcontent = "endpoint: {}\ntoken: {}\nconnect_timeout: 23".format(
        default_config_endpoint, default_config_token
    )
    clean_user_config.write(fcontent)
    client = get_client()
    assert client.connect_timeout == 23


@pytest.mark.usefixtures("no_client_version_check")
def test_code_config_with_connect_timeout(code_config_token, code_config_endpoint):
    Client(token=code_config_token, endpoint=code_config_endpoint, connect_timeout=24)
    c = get_client()
    assert c.connect_timeout == 24


@responses.activate
def test_bad_token_message():
    endpoint = "https://host_name.com/api/v2"
    responses.add(
        responses.GET, endpoint + "/version/", status=401,
    )
    with pytest.raises(UserWarning) as userwarning:
        Client(token="not correct", endpoint=endpoint)
    assert str(userwarning.value) == (
        "Unable to authenticate to the server - are you sure the "
        'provided token of "not correct" and endpoint of "https://'
        'host_name.com/api/v2" are correct? Note that if you access '
        "the DataRobot webapp at `https://app.datarobot.com`, then "
        "the correct endpoint to specify would be "
        "`https://app.datarobot.com/api/v2`."
    )


@responses.activate
def test_bad_endpoint_message():
    endpoint = "https://host_name.com/api/v16"
    responses.add(
        responses.GET, endpoint + "/version/", status=404,
    )
    with pytest.raises(UserWarning) as userwarning:
        Client(token="not correct", endpoint=endpoint)
    assert str(userwarning.value) == (
        "Error retrieving a version string from the server. Server "
        "did not reply with an API version. This may indicate the "
        "endpoint parameter `https://host_name.com/api/v16` is "
        "incorrect, or that the server there is incompatible with "
        "this version of the DataRobot client package. Note that if "
        "you access the DataRobot webapp at `https://app.datarobot"
        ".com`, then the correct endpoint to specify would be "
        "`https://app.datarobot.com/api/v2`."
    )

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

from datarobot.client import get_client


@pytest.mark.usefixtures("no_client_version_check")
def test_verify_parameter_false(default_config_endpoint, default_config_token, clean_user_config):
    """
    Can disable SSL verification. Not recommended save in rare cases.

    Parameters
    ----------
    default_config_endpoint
    default_config_token
    clean_user_config
    """
    configs = (
        "endpoint: {}".format(default_config_endpoint),
        "token: {}".format(default_config_token),
        "ssl_verify: false",
    )
    config = "\n".join(configs)
    clean_user_config.write(config)
    c = get_client()
    assert not c.verify


@pytest.mark.usefixtures("no_client_version_check")
def test_verify_parameter_certfile(
    default_config_endpoint, default_config_token, clean_user_config
):
    """
    Can specify a .pem CA file to use to verify server certificates

    Parameters
    ----------
    default_config_endpoint
    default_config_token
    clean_user_config
    """
    configs = (
        "endpoint: {}".format(default_config_endpoint),
        "token: {}".format(default_config_token),
        "ssl_verify: /path/to/certfile.pem",
    )
    config = "\n".join(configs)
    clean_user_config.write(config)
    c = get_client()
    assert c.verify == "/path/to/certfile.pem"


@pytest.mark.usefixtures("default_config", "no_client_version_check")
def test_ssl_verify_default():
    """
    By default, verify remains True (uses system information to verify
    certificate authenticity)
    """
    c = get_client()
    assert c.verify is True

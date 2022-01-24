#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for PT104
"""

import pytest

from hvl_ccb.dev import Pt104, Pt104CommunicationType, Pt104DeviceConfig


@pytest.fixture(scope="module")
def com_config():
    return {}


@pytest.fixture(scope="module")
def dev_config():
    return {
        "host": "127.0.0.1",
        "port": 6249,
        "serial_number": "HS337/135",
        "interface": Pt104CommunicationType.ETHERNET,
    }


def test_instantiation(com_config, dev_config):
    dev = Pt104({}, dev_config)
    assert dev is not None


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {
            "interface": Pt104CommunicationType.ETHERNET,
            "host": None,
        },
    ],
)
def test_dev_config_invalid(dev_config, wrong_config_dict):
    invalid_config = dict(dev_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(AttributeError):
        Pt104DeviceConfig(**invalid_config)


def test_ct_requires_host():
    assert Pt104CommunicationType.ETHERNET.requires_host
    assert not Pt104CommunicationType.USB.requires_host

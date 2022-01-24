#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the base class CommunicationProtocol.
"""

import pytest

from hvl_ccb.comm import NullCommunicationProtocol
from hvl_ccb.comm.base import AsyncCommunicationProtocolConfig
from hvl_ccb.configuration import EmptyConfig


@pytest.fixture(scope="module")
def com_config():
    return {
        "terminator": b"",
        "encoding": "ascii",
        "encoding_error_handling": "strict",
        "wait_sec_read_text_nonempty": 0.01,
        "default_n_attempts_read_text_nonempty": 5,
    }


def test_com_config(com_config):
    config = AsyncCommunicationProtocolConfig(**com_config)
    for key, value in com_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"encoding": "enigma"},
        {"encoding_error_handling": "miracle"},
        {"wait_sec_read_text_nonempty": 0},
        {"wait_sec_read_text_nonempty": -1},
        {"default_n_attempts_read_text_nonempty": 0},
        {"default_n_attempts_read_text_nonempty": -1},
    ],
)
def test_invalid_config_dict(com_config, wrong_config_dict):
    invalid_config = dict(com_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        AsyncCommunicationProtocolConfig(**invalid_config)


def test_instantiation():

    for arg in (EmptyConfig(), {}, None):
        with NullCommunicationProtocol(arg) as com:
            assert com is not None
            assert isinstance(com.config, EmptyConfig)

    with pytest.raises(TypeError):
        NullCommunicationProtocol({"extra_key": 0})

#  Copyright (c) 2021-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for .comm sub-package telnet
"""
import logging

import pytest

from hvl_ccb.comm import TelnetCommunication, TelnetCommunicationConfig, TelnetError
from masked_comm import LocalTelnetTestServer
from masked_comm.uitls import get_free_tcp_port

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope="function")
def com_config():
    host = "localhost"
    return {
        "host": "127.0.0.1",
        "port": get_free_tcp_port(host),  # find a free TCP port dynamically
        "timeout": 0.01,
    }


def test_com_config(com_config):
    config = TelnetCommunicationConfig(**com_config)
    for key, value in com_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"timeout": -0.1},
    ],
)
def test_invalid_config_dict(com_config, wrong_config_dict):
    invalid_config = dict(com_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        TelnetCommunicationConfig(**invalid_config)


def start_ts_tc(com_config):
    # Start server and listen
    ts = LocalTelnetTestServer(port=com_config["port"], timeout=com_config["timeout"])
    # Connect with the client to the server
    tc = TelnetCommunication(com_config)
    # Open/accept the connection from the client to the server
    ts.open()

    return ts, tc


def test_ts_tc(com_config):
    ts, tc = start_ts_tc(com_config)
    assert ts.__class__ is LocalTelnetTestServer
    assert tc.__class__ is TelnetCommunication
    assert ts._client is not None
    ts.close()
    tc.close()


def test_no_server(com_config):
    with pytest.raises(TelnetError):
        tc = TelnetCommunication(com_config)
    assert "tc" not in locals()


@pytest.fixture(scope="module")
def no_host_com_config():
    return {
        "port": 23,
        "timeout": 0.01,
    }


def test_no_host_given(no_host_com_config):
    with pytest.raises(AttributeError):
        TelnetCommunication(no_host_com_config)


def test_open_and_close_tc(com_config):
    ts, tc = start_ts_tc(com_config)
    assert tc.is_open
    tc.open()
    assert tc.is_open
    tc.close()
    assert not tc.is_open
    tc.close()
    assert not tc.is_open
    tc.open()
    assert tc.is_open


def test_write(com_config):
    ts, tc = start_ts_tc(com_config)
    assert tc.is_open

    message = "bla"
    tc.write(message)
    assert ts.get_written() == message

    tc.close()
    with pytest.raises(TelnetError):
        tc.write(message)
        assert ts.get_written() == ""

    ts.close()
    tc.close()


def test_read(com_config):
    ts, tc = start_ts_tc(com_config)
    assert tc.is_open

    message = "blub"
    ts.put_text(message)
    assert tc.read() == message

    ts.close()
    tc.close()


def test_encoding(com_config):
    ts, tc = start_ts_tc(com_config)
    assert tc.is_open

    assert tc.read() == ""

    message = "bla"
    ts.put_text(message)

    message = "äöü"
    ts.put_text(message, encoding="latin-1")

    ts.close()
    tc.close()


def test_read_on_empty(com_config):
    ts, tc = start_ts_tc(com_config)
    assert tc.is_open

    assert tc.read_nonempty() is None

    message = "bla"
    ts.put_text(message)
    assert tc.read_nonempty() == message

    ts.close()
    tc.close()

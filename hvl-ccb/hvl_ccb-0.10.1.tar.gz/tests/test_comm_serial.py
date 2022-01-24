#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for .comm sub-package
"""
import time

import pytest

from hvl_ccb.comm import (
    SerialCommunication,
    SerialCommunicationConfig,
    SerialCommunicationIOError,
)


@pytest.fixture(scope="module")
def com_config():
    return {
        "port": "loop://?logging=debug",
        "baudrate": 115200,
        "parity": SerialCommunicationConfig.Parity.NONE,
        "stopbits": SerialCommunicationConfig.Stopbits.ONE,
        "bytesize": SerialCommunicationConfig.Bytesize.EIGHTBITS,
        "terminator": b"\r\n",
        "timeout": 0.2,
        "wait_sec_read_text_nonempty": 0.01,
        "default_n_attempts_read_text_nonempty": 5,
    }


def test_com_config(com_config):
    config = SerialCommunicationConfig(**com_config)
    for key, value in com_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"parity": "B"},
        {"stopbits": 2.5},
        {"bytesize": 9},
        {"timeout": -1},
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
        SerialCommunicationConfig(**invalid_config)


def _decode_terminator(com_config):
    return SerialCommunicationConfig(**com_config).terminator.decode(
        SerialCommunicationConfig.encoding
    )


def test_timeout(com_config):
    with SerialCommunication(com_config) as sc:
        started_at = time.time()
        assert sc.read() == ""
        elapsed = time.time() - started_at
        timeout = com_config["timeout"]
        assert elapsed >= timeout
        assert elapsed < 1.25 * timeout


def _test_loop_serial_communication_text(com_config, sc):
    # send some text
    test_strings = [
        "Test message 1",
        "testmessage2",
        "190testmessage: 3",
    ]

    for t in test_strings:
        # send line
        sc.write(t)
        # read back line
        answer = sc.read()
        assert answer == t + _decode_terminator(com_config)


def _test_loop_serial_communication_bytes(com_config, sc):
    # send some bytes
    test_bytes = [
        b"Test message 1",
        b"testmessage2",
        b"190testmessage: 3",
    ]

    for d in test_bytes:
        # send line
        sc.write_bytes(d)
        # read back bytes
        answer = sc.read_bytes()
        assert answer == d


def test_serial_open_error(com_config):

    config_dict = dict(com_config)
    config_dict["port"] = "12345666"
    com = SerialCommunication(config_dict)
    with pytest.raises(SerialCommunicationIOError):
        com.open()


def test_serial_open_write_read_close(com_config):
    """
    Tests SerialCommunication
    """

    # manually open/close port
    sc = SerialCommunication(com_config)
    assert sc is not None
    assert not sc.is_open
    sc.open()
    assert sc.is_open
    sc.open()  # no error when re-opening an open port
    _test_loop_serial_communication_text(com_config, sc)
    _test_loop_serial_communication_bytes(com_config, sc)
    sc.close()
    assert not sc.is_open

    # or use with statement
    with SerialCommunication(com_config) as sc:
        assert sc is not None
        assert sc.is_open
        _test_loop_serial_communication_text(com_config, sc)


def test_serial_write_read_error(com_config):

    sc = SerialCommunication(com_config)

    # port not opened => errors
    assert not sc.is_open
    with pytest.raises(SerialCommunicationIOError):
        sc.write("anything")
    with pytest.raises(SerialCommunicationIOError):
        sc.read()
    with pytest.raises(SerialCommunicationIOError):
        sc.write_bytes(b"anything")
    with pytest.raises(SerialCommunicationIOError):
        sc.read_bytes()

    # nothing to read => empty output
    sc.open()
    assert sc.is_open
    assert sc.read() == ""
    assert sc.read_bytes() == b""


def test_serial_read_nonempty(com_config):
    # manually open/close port
    sc = SerialCommunication(com_config)
    sc.open()
    # send some text
    test_strings = [
        "Test message 1",
        "",
        "",
        "testmessage2",
        "",
        "190testmessage: 3",
    ]

    for t in test_strings:
        # send line
        sc.write(t)
        if t:
            # read back all previous empty lines until the non-empty one appears
            answer = sc.read_nonempty()
            assert answer == t
        else:
            answer = sc.read_nonempty()
            assert answer is None

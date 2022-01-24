#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for tcp.py in .comm sub-package
"""
import socket
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from hvl_ccb.comm import TcpCommunicationConfig, Tcp
from masked_comm import FakeTCP

_SOCK_TIMEOUT = 0.1

fake_tcp = FakeTCP(_SOCK_TIMEOUT)


def _get_free_tcp_port(host):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        addr, port = sock.getsockname()
    return port


@pytest.fixture(scope="module")
def com_config():
    host = "127.0.0.1"
    return {
        "host": host,
        "port": _get_free_tcp_port(host),  # find a free TCP port dynamically
        "bufsize": 128,
    }


def test_com_config(com_config):
    config = TcpCommunicationConfig(**com_config)
    for key, value in com_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"port": 0},
        {"bufsize": 0},
    ],
)
def test_invalid_config_dict(com_config, wrong_config_dict):
    invalid_config = dict(com_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        TcpCommunicationConfig(**invalid_config)


def test_instantiation(com_config):
    config = TcpCommunicationConfig(**com_config)
    com = Tcp(config)
    assert com is not None


# Beware: scope has to match scope of the com_config fixture
@pytest.fixture(scope="function")
def start_tcp(com_config) -> Tcp:
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(
            fake_tcp.run_fake_server,
            com_config["host"],
            com_config["port"],
        )
        # give some time to startup the server
        time.sleep(_SOCK_TIMEOUT / 5)
        config = TcpCommunicationConfig(**com_config)
        with Tcp(config) as tcp_com:
            yield tcp_com


def test_open_write_and_close(start_tcp):
    tcp_com = start_tcp
    tcp_com.write("Scio ut nescio.")
    assert tcp_com.read() == "Scio ut nescio."
    tcp_com.write("end")
    tcp_com.close()

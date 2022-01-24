#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Testing Lauda PRO RP245E driver. Makes use of the socket library (TCP comm).
"""

import socket
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import pytest
from pytest_mock import MockerFixture

from hvl_ccb.dev import lauda
from masked_comm import tcp

_SOCK_TIMEOUT = 0.1

fake_tcp = tcp.FakeTCP(_SOCK_TIMEOUT)


def _get_free_tcp_port(host):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        addr, port = sock.getsockname()
    return port


@pytest.fixture(scope="function")
def com_config():
    host = "127.0.0.1"
    return {
        "host": host,
        "port": _get_free_tcp_port(host),  # find a free TCP port dynamically
        "bufsize": 128,
        "terminator": "\r\n",
        "wait_sec_pre_read_or_write": 0.005,
    }


def test_com_config(com_config):
    config = lauda.LaudaProRp245eTcpCommunicationConfig(**com_config)
    for key, value in com_config.items():
        assert getattr(config, key) == value


# Test here only lauda-specific com fields; rest should be tested in tcp com tests
@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"wait_sec_pre_read_or_write": -0.5},
        {"terminator": "NotATerminator"},
    ],
)
def test_invalid_com_config_dict(com_config, wrong_config_dict):
    invalid_config = dict(com_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        lauda.LaudaProRp245eTcpCommunicationConfig(**invalid_config)


@pytest.fixture(scope="module")
def dev_config():
    return {
        "operation_mode": 2,
        "control_mode": 0,
    }


def test_dev_config(dev_config):
    # currently there are no non-default config values
    lauda.LaudaProRp245eConfig()

    config = lauda.LaudaProRp245eConfig(**dev_config)
    for key, value in dev_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"operation_mode": 123},
        {"control_mode": 123},
    ],
)
def test_invalid_config_dict(dev_config, wrong_config_dict):
    invalid_config = dict(dev_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        lauda.LaudaProRp245eConfig(**invalid_config)


# Beware: scope has to match scope of the com_config fixture
@pytest.fixture(scope="function")
def startchiller(com_config) -> lauda:
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(
            fake_tcp.run_fake_server,
            com_config["host"],
            com_config["port"],
            com_config["terminator"],
            com_config["wait_sec_pre_read_or_write"],
        )
        # give some time to startup the server
        time.sleep(_SOCK_TIMEOUT / 5)
        with lauda.LaudaProRp245e(com_config) as chill:
            yield chill


def test_lauda_connected_to_wrong_device(com_config):
    com = lauda.LaudaProRp245e.default_com_cls()(com_config)
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(
            fake_tcp.run_bad_fake_server,
            com.config.host,
            com.config.port,
            com.config.terminator,
            com.config.wait_sec_pre_read_or_write,
        )
        # give some time to startup the server
        time.sleep(_SOCK_TIMEOUT / 5)
        with pytest.raises(lauda.LaudaProRp245eCommandError):
            lauda.LaudaProRp245e(com).start()
        # manually stop the bad server
        com.query_command(lauda.LaudaProRp245eCommand.STOP)


def test_get_device_type(startchiller):
    chill = startchiller
    assert chill.get_device_type() == "RP245 PRO"


def test_pause(startchiller, mocker: MockerFixture):
    chill = startchiller

    def pause(self):
        # prevent premature shutdown of module-scoped test tcp server by sending
        # lowercase `STOP` command (cf. `run_fake_server` above)
        with self.com.access_lock:
            super(lauda.LaudaProRp245eTcpCommunication, self.com).write(
                lauda.LaudaProRp245eCommand.STOP.value.lower()
                + self.com.config.terminator
            )
            reply = self.com.read()
        if "ERR" in reply:
            raise lauda.LaudaProRp245eCommandError
        return reply.upper()

    mocker.patch(
        "hvl_ccb.dev.lauda.LaudaProRp245e.pause",
        side_effect=pause,
        autospec=True,
    )

    assert chill.pause() == lauda.LaudaProRp245eCommand.STOP.value


def test_read_error(startchiller):
    chill = startchiller

    with patch(
        "hvl_ccb.dev.lauda.LaudaProRp245eTcpCommunication.read",
        return_value="ERR",
    ):
        with pytest.raises(lauda.LaudaProRp245eCommandError):
            # don't use pause() as it sends successful STOP that kills the FakeTCP
            chill.start_ramp()


def test_run(startchiller):
    chill = startchiller
    assert chill.run() == lauda.LaudaProRp245eCommand.START.value


def test_set_external_temp(startchiller):
    chill = startchiller
    ext = 20.00
    assert chill.set_external_temp(ext) == "".join(
        [lauda.LaudaProRp245eCommand.EXTERNAL_TEMP.value, "%.2f" % ext]
    )


def test_set_temp_set_point(startchiller):
    chill = startchiller
    ext = 25.00
    assert chill.set_temp_set_point(ext) == "".join(
        [lauda.LaudaProRp245eCommand.TEMP_SET_POINT.value, "%.2f" % ext]
    )


def test_correct_pump_level(startchiller):
    chill = startchiller
    ext = 3
    assert (
        chill.set_pump_level(ext)
        == f"{lauda.LaudaProRp245eCommand.PUMP_LEVEL.value}{ext}"
    )


def test_wrong_pump_level(startchiller):
    chill = startchiller
    ext = 15
    with pytest.raises(ValueError):
        chill.set_pump_level(ext)


def test_correct_control_mode(startchiller):
    chill = startchiller
    ext = 0
    assert (
        chill.set_control_mode(0)
        == f"{lauda.LaudaProRp245eCommand.CONT_MODE.value}{ext}"
    )


def test_wrong_control_mode(startchiller):
    chill = startchiller
    with pytest.raises(ValueError):
        chill.set_control_mode(6)


def test_correct_ramp_program(startchiller):
    chill = startchiller
    ext = 1
    assert chill.set_ramp_program(ext) == "".join(
        [lauda.LaudaProRp245eCommand.RAMP_SELECT.value, str(ext)]
    )


def test_wrong_ramp_program(startchiller):
    chill = startchiller
    with pytest.raises(ValueError):
        chill.set_ramp_program(6)


def test_start_ramp(startchiller):
    chill = startchiller
    assert chill.start_ramp() == lauda.LaudaProRp245eCommand.RAMP_START.value


def test_pause_ramp(startchiller):
    chill = startchiller
    assert chill.pause_ramp() == lauda.LaudaProRp245eCommand.RAMP_PAUSE.value


def test_continue_ramp(startchiller):
    chill = startchiller
    assert chill.continue_ramp() == lauda.LaudaProRp245eCommand.RAMP_CONTINUE.value


def test_stop_ramp(startchiller):
    chill = startchiller
    assert chill.stop_ramp() == lauda.LaudaProRp245eCommand.RAMP_STOP.value


def test_set_ramp_iterations(startchiller):
    chill = startchiller
    ext = 3
    assert chill.set_ramp_iterations(ext) == "".join(
        [lauda.LaudaProRp245eCommand.RAMP_ITERATIONS.value, str(ext)]
    )


def test_reset_ramp(startchiller):
    chill = startchiller
    assert chill.reset_ramp() == lauda.LaudaProRp245eCommand.RAMP_DELETE.value


def test_set_ramp_segment(startchiller):
    chill = startchiller
    temp = 10.00
    dur = 0
    tol = 0.00
    pump = 3
    segment = f"{temp:.2f}_{dur}_{tol:.2f}_{pump}"
    assert (
        chill.set_ramp_segment(temp, dur, tol, pump)
        == f"{lauda.LaudaProRp245eCommand.RAMP_SET.value}{segment}"
    )


def test_get_bath_temp(startchiller):
    chill = startchiller
    assert chill.get_bath_temp() == 25.00


def test_returns_error(startchiller):
    chill = startchiller
    with pytest.raises(lauda.LaudaProRp245eCommandError):
        chill.com.query_command("FOOBAR")

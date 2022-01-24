#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the .dev.mbw973 sub-package.
"""

import pytest

from hvl_ccb import comm, dev
from masked_comm.serial import LoopSerialCommunication


@pytest.fixture(scope="module")
def com_config():
    return {
        "port": "loop://?logging=debug",
        "baudrate": 115200,
        "parity": dev.MBW973SerialCommunicationConfig.Parity.NONE,
        "stopbits": dev.MBW973SerialCommunicationConfig.Stopbits.ONE,
        "bytesize": dev.MBW973SerialCommunicationConfig.Bytesize.EIGHTBITS,
        "terminator": b"\r\n",
        "timeout": 3,
    }


@pytest.fixture(scope="module")
def dev_config():
    return {"polling_interval": 0.1}


@pytest.fixture
def started_mbw973_device(com_config, dev_config):
    serial_port = LoopSerialCommunication(com_config)
    serial_port.open()
    serial_port.put_text("1")
    serial_port.put_text("0")
    with dev.MBW973(serial_port, dev_config) as mbw:
        while serial_port.get_written() is not None:
            pass
        yield serial_port, mbw


def test_dev_config(dev_config):
    # currently there are no non-default config values
    dev.MBW973Config()

    config = dev.MBW973Config(**dev_config)
    for key, value in dev_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict", [
        {"polling_interval": 0},
        {"polling_interval": -1},
    ],
)
def test_invalid_config_dict(dev_config, wrong_config_dict):
    invalid_config = dict(dev_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        dev.MBW973Config(**invalid_config)


def test_instantiation(com_config, dev_config):
    mbw = dev.MBW973(com_config)
    assert mbw is not None

    mbw = dev.MBW973(com_config, dev_config)
    assert mbw is not None


def test_com_error(com_config, dev_config):

    wrong_config = dict(com_config)
    wrong_config["port"] = "NOT A PORT"
    mbw = dev.MBW973(wrong_config, dev_config)
    assert not mbw.com.is_open

    with pytest.raises(comm.SerialCommunicationIOError):
        mbw.start()

    mbw = dev.MBW973(com_config, dev_config)
    assert not mbw.com.is_open

    with pytest.raises(comm.SerialCommunicationIOError):
        mbw.write(0)
    with pytest.raises(comm.SerialCommunicationIOError):
        mbw.is_done()
    with pytest.raises(comm.SerialCommunicationIOError):
        mbw.start_control()
    with pytest.raises(comm.SerialCommunicationIOError):
        mbw.read_measurements()
    with pytest.raises(comm.SerialCommunicationIOError):
        mbw.set_measuring_options()


def test_start(started_mbw973_device, com_config):
    com, mbw = started_mbw973_device

    # starting again should work
    com.put_text("1")
    com.put_text("0")
    mbw.start()
    assert com.get_written() == "HumidityTest?"
    assert com.get_written() == "SF6PurityTest?"


def test_is_done(started_mbw973_device):
    serial_port, mbw = started_mbw973_device

    # case 1, only humidity
    mbw.set_measuring_options(humidity=True, sf6_purity=False)
    assert serial_port.get_written() == "HumidityTest=1"
    assert serial_port.get_written() == "SF6PurityTest=0"
    serial_port.put_text("0")
    assert mbw.is_done() is False
    assert serial_port.get_written() == "DoneWithDP?"

    # case 2, only SF6 purity
    mbw.set_measuring_options(humidity=False, sf6_purity=True)
    assert serial_port.get_written() == "HumidityTest=0"
    assert serial_port.get_written() == "SF6PurityTest=1"
    serial_port.put_text("0")
    assert mbw.is_done() is False
    assert serial_port.get_written() == "SF6VolHold?"

    # case 3, both measurements
    mbw.set_measuring_options(humidity=True, sf6_purity=True)
    assert serial_port.get_written() == "HumidityTest=1"
    assert serial_port.get_written() == "SF6PurityTest=1"
    serial_port.put_text("1")
    serial_port.put_text("0")
    assert mbw.is_done() is False
    assert serial_port.get_written() == "DoneWithDP?"
    assert serial_port.get_written() == "SF6VolHold?"

    # case 3, both measurements, resulting in True
    mbw.set_measuring_options(humidity=True, sf6_purity=True)
    assert serial_port.get_written() == "HumidityTest=1"
    assert serial_port.get_written() == "SF6PurityTest=1"
    serial_port.put_text("1")
    serial_port.put_text("1")
    serial_port.put_text("-17.2315")
    serial_port.put_text("-21.5501")
    serial_port.put_text("170.421")
    serial_port.put_text("87.2323")
    serial_port.put_text("35.0001")
    serial_port.put_text("87.53")
    assert mbw.is_done() is True
    assert mbw.last_measurement_values == {
        "frostpoint": -17.2315,
        "frostpoint_ambient": -21.5501,
        "pressure": 170.421,
        "ppmv": 87.2323,
        "ppmw": 35.0001,
        "sf6_vol": 87.53,
    }

    mbw.stop()


def test_mbw973_start_control(started_mbw973_device):
    """
    Tests for the start_control method
    """

    serial_port, mbw = started_mbw973_device

    # control still running
    serial_port._serial_port.reset_input_buffer()
    serial_port.put_text("1")
    with pytest.raises(dev.MBW973ControlRunningException):
        mbw.start_control()

    assert serial_port.get_written() == "control?"

    # pump still running
    serial_port.put_text("0")
    serial_port.put_text("1")
    with pytest.raises(dev.MBW973PumpRunningException):
        mbw.start_control()

    assert serial_port.get_written() == "control?"
    assert serial_port.get_written() == "Pump.on?"

    # nothing running, can start
    serial_port.put_text("0")  # no control running
    serial_port.put_text("0")  # no pump running
    mbw.start_control()
    assert serial_port.get_written() == "control?"
    assert serial_port.get_written() == "Pump.on?"
    assert serial_port.get_written() == "control=1"

    serial_port.put_text("0")  # not done with dewpoint
    assert mbw.is_done_with_measurements is False
    serial_port.put_text("1")  # done with dewpoint
    # dummy measurement values in the readout order
    # note: for Py >= 3.6 dict items are ordered by default (no need to use OrderedDict)
    expected_measurement_values = {
        "frostpoint": 0.1,
        "frostpoint_ambient": 0.2,
        "pressure": 0.3,
        "ppmv": 0.4,
        "ppmw": 0.5,
        "sf6_vol": 0.6,
    }
    for measurement_value in expected_measurement_values.values():
        serial_port.put_text(str(measurement_value))
    mbw.status_poller.wait_for_polling_result()
    assert mbw.is_done_with_measurements is True
    assert mbw.last_measurement_values == expected_measurement_values


def test_read_measurements(started_mbw973_device):
    com, mbw = started_mbw973_device

    expected_measurement_values = {
        "frostpoint": 0.1,
        "frostpoint_ambient": 0.2,
        "pressure": 0.3,
        "ppmv": 0.4,
        "ppmw": 0.5,
        "sf6_vol": 0.6,
    }
    for measurement_value in expected_measurement_values.values():
        com.put_text(str(measurement_value))

    readout = mbw.read_measurements()

    assert readout == expected_measurement_values

    assert com.get_written() == "Fp?"
    assert com.get_written() == "Fp1?"
    assert com.get_written() == "Px?"
    assert com.get_written() == "PPMv?"
    assert com.get_written() == "PPMw?"
    assert com.get_written() == "SF6Vol?"


def test_set_measuring_options(started_mbw973_device):
    test_com, mbw = started_mbw973_device

    mbw.set_measuring_options(True, True)
    assert test_com.get_written() == "HumidityTest=1"
    assert test_com.get_written() == "SF6PurityTest=1"

    mbw.set_measuring_options(True, False)
    assert test_com.get_written() == "HumidityTest=1"
    assert test_com.get_written() == "SF6PurityTest=0"

    mbw.set_measuring_options(False, True)
    assert test_com.get_written() == "HumidityTest=0"
    assert test_com.get_written() == "SF6PurityTest=1"

    mbw.set_measuring_options(False, False)
    assert test_com.get_written() == "HumidityTest=0"
    assert test_com.get_written() == "SF6PurityTest=0"

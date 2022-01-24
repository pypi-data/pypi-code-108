#  Copyright (c) 2020-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the .dev.fug sub-package.
"""

import logging

import pytest

from hvl_ccb import dev
from hvl_ccb.dev.fug import FuGProbusIV, FuGProbusIVCommands
from masked_comm.serial import FuGLoopSerialCommunication  # type: ignore

logging.basicConfig(level=logging.ERROR)


@pytest.fixture(scope="module")
def com_config():
    return {
        "port": "loop://?logging=debug",
        "baudrate": 9600,
        "parity": dev.FuGSerialCommunicationConfig.Parity.NONE,
        "stopbits": dev.FuGSerialCommunicationConfig.Stopbits.ONE,
        "bytesize": dev.FuGSerialCommunicationConfig.Bytesize.EIGHTBITS,
        "terminator": b"\r\n",
        "timeout": 0.01,
        "wait_sec_read_text_nonempty": 0.01,
        "default_n_attempts_read_text_nonempty": 5,
    }


@pytest.fixture(scope="module")
def dev_config():
    return {}


def started_devices(com_config, dev_config):
    com = FuGLoopSerialCommunication(com_config)
    com.open()
    fug = dev.FuG(com, dev_config)

    return com, fug


def fully_started_devices(com_config, dev_config):
    com, fug = started_devices(com_config, dev_config)
    com.put_text("FUG HCK 800 - 20 000 MOD 17022-01-01")
    com.put_text("FUG HCK 800 - 20 000 MOD 17022-01-01")
    fug.start()
    assert com.get_written() == "*IDN?"
    assert com.get_written() == "*IDN?"

    return com, fug


def test_pytest():
    assert 1


def test_loop(com_config):
    com = FuGLoopSerialCommunication(com_config)
    com.open()
    com.put_text("test")

    assert com is not None


class ConcreteFuG(FuGProbusIV):
    def start(self):
        super().start()


def test_instantiation(com_config, dev_config):
    di = ConcreteFuG(com_config)
    assert di is not None

    di = ConcreteFuG(com_config, dev_config)
    assert di is not None


def test_start(com_config, dev_config):
    com, fug = started_devices(com_config, dev_config)

    com.put_text("FUG HCK 800 - 20 000 MOD 17022-01-01")
    com.put_text("FUG HCK 800 - 20 000 MOD 17022-01-01")
    fug.start()

    assert com.get_written() == "*IDN?"
    assert com.get_written() == "*IDN?"

    assert fug._serial_number == "17022-01-01"
    assert fug._model == "HCK"
    assert fug.max_current_hardware == 80e-3
    assert fug._max_power_hardware == 800
    assert fug.max_voltage_hardware == 20e3
    assert fug.max_current == 80e-3
    assert fug.max_voltage == 20e3

    assert fug is not None


@pytest.fixture(scope="module")
def wrong_com_config():
    return {
        "port": "loop://?logging=debug",
        "baudrate": 9600,
        "parity": dev.FuGSerialCommunicationConfig.Parity.NONE,
        "stopbits": dev.FuGSerialCommunicationConfig.Stopbits.ONE,
        "bytesize": dev.FuGSerialCommunicationConfig.Bytesize.EIGHTBITS,
        "terminator": b"\r\n",
        "timeout": 3,
        "wait_sec_read_text_nonempty": -1,
        "default_n_attempts_read_text_nonempty": 5,
    }


@pytest.fixture(scope="module")
def wrong_dev_config():
    return {
        "wait_sec_stop_commands": -1,
    }


def test_wrong_configs(wrong_com_config, wrong_dev_config, com_config):
    with pytest.raises(ValueError):
        com = FuGLoopSerialCommunication(wrong_com_config)
    assert "com" not in locals()

    com = FuGLoopSerialCommunication(com_config)
    com.open()
    with pytest.raises(ValueError):
        fug = dev.FuG(com, wrong_dev_config)
    assert "fug" not in locals()


starts_data = [
    (0, 0, 80e-3, 20e3, 80e-3, 20e3),
    (1, 100e3, 80e-3, 20e3, 80e-3, 20e3),
    (50e-3, 15e3, 50e-3, 15e3, 80e-3, 20e3),
]


@pytest.mark.parametrize("start_data", starts_data)
def test_starts(com_config, dev_config, start_data):
    com, fug = started_devices(com_config, dev_config)

    com.put_text("FUG HCK 800 - 20 000 MOD 17022-01-01")
    com.put_text("FUG HCK 800 - 20 000 MOD 17022-01-01")
    fug.start(max_current=start_data[0], max_voltage=start_data[1])

    assert fug.max_current == start_data[2]
    assert fug.max_voltage == start_data[3]
    assert fug.max_current_hardware == start_data[4]
    assert fug.max_voltage_hardware == start_data[5]


def test_idn_not_regognizable(com_config, dev_config):
    com, fug = started_devices(com_config, dev_config)
    com.put_text("FUG HCK 800 MOD 17022-01-01")
    com.put_text("FUG HCK 800 MOD 17022-01-01")
    with pytest.raises(dev.FuGError):
        fug.start()


def test_setregisters(com_config, dev_config):
    com, fug = fully_started_devices(com_config, dev_config)

    com.put_text("S0:0")
    assert fug.voltage.setvalue == 0
    assert com.get_written() == ">S0 ?"

    com.put_text("E0")
    fug.voltage = 1000
    assert com.get_written() == ">S0 1000"

    with pytest.raises(dev.FuGError):
        fug.voltage = 100e3
    assert com.get_written() is None

    with pytest.raises(ValueError):
        fug.voltage = -1
    assert com.get_written() is None

    com.put_text("S0A:250")
    assert fug.voltage.actualsetvalue == 250
    assert com.get_written() == ">S0A ?"
    com.put_text("E0")
    fug.voltage.actualsetvalue = 333
    assert com.get_written() == ">S0A 333"

    com.put_text("S0R:10")
    assert fug.voltage.ramprate == 10
    assert com.get_written() == ">S0R ?"
    com.put_text("E0")
    fug.voltage.ramprate = 10
    assert com.get_written() == ">S0R 10"

    com.put_text("S0B:0")
    assert fug.voltage.rampmode == dev.FuGRampModes.IMMEDIATELY
    assert com.get_written() == ">S0B ?"
    com.put_text("E0")
    fug.voltage.rampmode = dev.FuGRampModes.FOLLOWRAMP
    assert com.get_written() == ">S0B 1"
    com.put_text("E0")
    fug.voltage.rampmode = 1
    assert com.get_written() == ">S0B 1"
    with pytest.raises(dev.FuGError):
        fug.voltage.rampmode = 10
    assert com.get_written() is None

    with pytest.raises(dev.FuGError):
        fug.voltage.rampstate = dev.FuGDigitalVal.ON
    assert com.get_written() is None
    com.put_text("S0S:0")
    assert fug.voltage.rampstate == dev.FuGDigitalVal.OFF
    assert com.get_written() == ">S0S ?"

    com.put_text("S0H:1")
    assert fug.voltage.high_resolution == dev.FuGDigitalVal.YES
    assert com.get_written() == ">S0H ?"
    com.put_text("E0")
    fug.voltage.high_resolution = dev.FuGDigitalVal.YES
    assert com.get_written() == ">S0H 1"
    com.put_text("E0")
    fug.voltage.high_resolution = dev.FuGDigitalVal.NO
    assert com.get_written() == ">S0H 0"
    com.put_text("E0")
    fug.voltage.high_resolution = 1
    assert com.get_written() == ">S0H 1"
    with pytest.raises(dev.FuGError):
        fug.voltage.high_resolution = 1024
    assert com.get_written() is None

    com.put_text("E0")
    fug.current = 80e-3
    assert com.get_written() == ">S1 0.08"


def test_digital_output_registers(com_config, dev_config):
    com, fug = fully_started_devices(com_config, dev_config)

    com.put_text("E0")
    fug.outX0.out = dev.FuGDigitalVal.ON
    assert com.get_written() == ">B0 1"
    com.put_text("E0")
    fug.outX0.out = dev.FuGDigitalVal.NO
    assert com.get_written() == ">B0 0"
    com.put_text("B0:1")
    assert fug.outX0.out == dev.FuGDigitalVal.ON
    assert com.get_written() == ">B0 ?"

    com.put_text("B0A:0")
    assert fug.outX0.status == dev.FuGDigitalVal.NO
    assert com.get_written() == ">B0A ?"
    with pytest.raises(dev.FuGError):
        fug.outX0.status = dev.FuGDigitalVal.ON
    assert com.get_written() is None

    com.put_text("E0")
    fug.outX1.out = dev.FuGDigitalVal.ON
    assert com.get_written() == ">B1 1"

    com.put_text("E0")
    fug.outX2.out = dev.FuGDigitalVal.ON
    assert com.get_written() == ">B2 1"

    com.put_text("E0")
    fug.outXCMD.out = dev.FuGDigitalVal.ON
    assert com.get_written() == ">BX 1"

    com.put_text("E0")
    fug.on = dev.FuGDigitalVal.ON
    assert com.get_written() == ">BON 1"

    com.put_text("E0")
    fug.on = 1
    assert com.get_written() == ">BON 1"
    with pytest.raises(dev.FuGError):
        fug.on = 23
    assert com.get_written() is None


def test_monitors(com_config, dev_config):
    com, fug = fully_started_devices(com_config, dev_config)

    com.put_text("M0:1000")
    assert fug.voltage_monitor.value == 1000
    assert com.get_written() == ">M0 ?"
    with pytest.raises(dev.FuGError):
        fug.voltage_monitor.value = 0
    assert com.get_written() is None

    com.put_text("M0R:1000")
    assert fug.voltage_monitor.value_raw == 1000
    assert com.get_written() == ">M0R ?"
    with pytest.raises(dev.FuGError):
        fug.voltage_monitor.value_raw = 0
    assert com.get_written() is None

    com.put_text("M0I:0")
    assert fug.voltage_monitor.adc_mode == dev.FuGMonitorModes.T256US
    assert com.get_written() == ">M0I ?"
    com.put_text("E0")
    fug.voltage_monitor.adc_mode = dev.FuGMonitorModes.T40MS
    assert com.get_written() == ">M0I 4"
    com.put_text("E0")
    fug.voltage_monitor.adc_mode = 6
    assert com.get_written() == ">M0I 6"
    with pytest.raises(dev.FuGError):
        fug.voltage_monitor.adc_mode = 12
    assert com.get_written() is None

    com.put_text("M1:0.0123")
    assert fug.current_monitor.value == 0.0123
    assert com.get_written() == ">M1 ?"


def test_digital_inputs(com_config, dev_config):
    com, fug = fully_started_devices(com_config, dev_config)

    com.put_text("DVR:1")
    assert fug.di.cv_mode == dev.FuGDigitalVal.ON
    assert com.get_written() == ">DVR ?"
    com.put_text("DIR:1")
    assert fug.di.cc_mode == dev.FuGDigitalVal.ON
    assert com.get_written() == ">DIR ?"
    com.put_text("D3R:0")
    assert fug.di.reg_3 == dev.FuGDigitalVal.OFF
    assert com.get_written() == ">D3R ?"
    com.put_text("DX:0")
    assert fug.di.x_stat == dev.FuGDigitalVal.OFF
    assert com.get_written() == ">DX ?"
    com.put_text("DON:1")
    assert fug.di.on == dev.FuGDigitalVal.ON
    assert com.get_written() == ">DON ?"
    com.put_text("DSD:1")
    assert fug.di.digital_control == dev.FuGDigitalVal.ON
    assert com.get_written() == ">DSD ?"
    com.put_text("DSA:1")
    assert fug.di.analog_control == dev.FuGDigitalVal.ON
    assert com.get_written() == ">DSA ?"
    com.put_text("DCAL:0")
    assert fug.di.calibration_mode == dev.FuGDigitalVal.OFF
    assert com.get_written() == ">DCAL ?"


def test_config_registers(com_config, dev_config):
    com, fug = fully_started_devices(com_config, dev_config)

    com.put_text("KT:2")
    assert fug.config_status.terminator == dev.FuGTerminators.LF
    assert com.get_written() == ">KT ?"
    with pytest.raises(dev.FuGError):
        fug.config_status.terminator = 5
    assert com.get_written() is None
    com.put_text("E0")
    fug.config_status.terminator = dev.FuGTerminators.LF
    assert com.get_written() == ">KT 2"

    answer = "01011101"
    com.put_text("KS:" + answer)
    assert fug.config_status.status == answer
    assert com.get_written() == ">KS ?"
    with pytest.raises(dev.FuGError):
        fug.config_status.status = answer
    assert com.get_written() is None

    com.put_text("KQS:1")
    assert fug.config_status.srq_status == "1"
    assert com.get_written() == ">KQS ?"
    with pytest.raises(dev.FuGError):
        fug.config_status.srq_status = "something"
    assert com.get_written() is None

    com.put_text("KQM:0")
    assert fug.config_status.srq_mask == 0
    assert com.get_written() == ">KQM ?"
    com.put_text("E0")
    fug.config_status.srq_mask = 1
    assert com.get_written() == ">KQM 1"

    com.put_text("KX:0")
    assert fug.config_status.execute_on_x == dev.FuGDigitalVal.NO
    assert com.get_written() == ">KX ?"
    com.put_text("E0")
    fug.config_status.execute_on_x = dev.FuGDigitalVal.YES
    assert com.get_written() == ">KX 1"
    com.put_text("E0")
    fug.config_status.execute_on_x = dev.FuGDigitalVal.NO
    assert com.get_written() == ">KX 0"
    com.put_text("E0")
    fug.config_status.execute_on_x = 1
    assert com.get_written() == ">KX 1"
    with pytest.raises(dev.FuGError):
        fug.config_status.execute_on_x = 10
    assert com.get_written() is None

    com.put_text("KN:0")
    assert fug.config_status.readback_data == dev.FuGReadbackChannels.VOLTAGE
    assert com.get_written() == ">KN ?"
    com.put_text("E0")
    fug.config_status.readback_data = dev.FuGReadbackChannels.RATEDCURRENT
    assert com.get_written() == ">KN 4"
    with pytest.raises(dev.FuGError):
        fug.config_status.readback_data = 33
    assert com.get_written() is None

    com.put_text("E4")
    with pytest.raises(dev.FuGError):
        assert fug.config_status.most_recent_error == "something"
    assert com.get_written() == ">KE ?"
    with pytest.raises(dev.FuGError):
        fug.config_status.most_recent_error = "something"
    assert com.get_written() is None


def test_timeout(com_config, dev_config):
    com, fug = fully_started_devices(com_config, dev_config)

    with pytest.raises(dev.FuGError):
        fug.on = dev.FuGDigitalVal.ON


def test_unkown_errorcode(com_config, dev_config):
    com, fug = fully_started_devices(com_config, dev_config)

    com.put_text("E9999")
    with pytest.raises(dev.FuGError):
        fug.on = dev.FuGDigitalVal.ON
    assert com.get_written() == ">BON 1"


def test_wrong_return_register(com_config, dev_config):
    com, fug = fully_started_devices(com_config, dev_config)

    com.put_text("M0:1000")
    with pytest.raises(dev.FuGError):
        assert fug.current_monitor.value == 0.001
    assert com.get_written() == ">M1 ?"


def started_retro(com_config, dev_config):

    class FuGProbusIVDevice(FuGProbusIV):
        def start(self):
            return super().start()

    com = FuGLoopSerialCommunication(com_config)
    com.open()
    fug = FuGProbusIVDevice(com, dev_config)
    com.put_text("FUG HCK 800 - 20 000 MOD 17022-01-01")
    fug.start()
    assert com.get_written() == "*IDN?"

    return com, fug


def test_retrodevices(com_config, dev_config):
    com, fug = started_retro(com_config, dev_config)

    assert com is not None
    assert fug is not None

    assert fug._interface_version == "FUG HCK 800 - 20 000 MOD 17022-01-01"
    assert fug.__repr__() == "FuGProbus(FUG HCK 800 - 20 000 MOD 17022-01-01)"

    com.put_text("something")
    assert fug.command(FuGProbusIVCommands.QUERY) == "something"
    assert com.get_written() == "?"

    assert com.get_written() is None
    with pytest.raises(dev.FuGError):
        fug.command(FuGProbusIVCommands.POLARITY)
    assert com.get_written() is None

    com.put_text("E0")
    com.put_text("E0")
    fug.stop()

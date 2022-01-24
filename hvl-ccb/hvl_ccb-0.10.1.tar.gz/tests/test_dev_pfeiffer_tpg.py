#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the .dev.pfeiffer_tpg sub-package.
"""

import logging

import pytest

from hvl_ccb import comm, dev
from masked_comm.serial import PfeifferTPGLoopSerialCommunication

logging.basicConfig(level=logging.ERROR)


@pytest.fixture(scope="module")
def com_config():
    return {
        "port": "loop://?logging=debug",
        "baudrate": 9600,
        "parity": dev.PfeifferTPGSerialCommunicationConfig.Parity.NONE,
        "stopbits": dev.PfeifferTPGSerialCommunicationConfig.Stopbits.ONE,
        "bytesize": dev.PfeifferTPGSerialCommunicationConfig.Bytesize.EIGHTBITS,
        "terminator": b"\r\n",
        "timeout": 3,
    }


@pytest.fixture(scope="module")
def dev_config():
    return {"model": dev.PfeifferTPGConfig.Model.TPG25xA}


@pytest.fixture
def started_pfeiffer_tpg(com_config, dev_config):
    com = PfeifferTPGLoopSerialCommunication(com_config)
    com.open()
    com.put_text(chr(6))
    com.put_text(
        ",".join(
            [
                dev.PfeifferTPG.SensorTypes.CMR.name,
                dev.PfeifferTPG.SensorTypes.noSENSOR.name,
            ]
        )
    )
    with dev.PfeifferTPG(com, dev_config) as pg:
        while com.get_written() is not None:
            pass
        yield com, pg


def test_pfeiffer_tpg_instantiation(com_config, dev_config):
    pg = dev.PfeifferTPG(com_config, dev_config)
    assert pg is not None
    assert pg.unit == "mbar"

    # another valid config
    config_dict = dict(dev_config)
    config_dict["model"] = "TPGx6x"
    dev.PfeifferTPG(com_config, config_dict)

    # wrong config
    config_dict["model"] = "wrong_name"
    with pytest.raises(ValueError):
        dev.PfeifferTPG(com_config, config_dict)


def test_com_send_command(com_config):
    com = PfeifferTPGLoopSerialCommunication(com_config)
    com.open()
    com.put_text(chr(6))
    com.send_command("this is the command")
    assert com.get_written() == "this is the command"
    com.put_text("not an acknowledgement")
    with pytest.raises(dev.PfeifferTPGError):
        com.send_command("this command is not acknowledged")
    com.close()


def test_com_query(com_config):
    com = PfeifferTPGLoopSerialCommunication(com_config)
    com.open()
    com.put_text(chr(6))
    com.put_text("this is the answer")
    assert com.query("this is the query") == "this is the answer"
    assert com.get_written() == "this is the query"
    assert com.get_written() == chr(5)
    com.put_text("not an acknowledgement")
    with pytest.raises(dev.PfeifferTPGError):
        com.query("this query is not acknowledged")
    com.put_text(chr(6))
    com.put_text("")
    with pytest.raises(dev.PfeifferTPGError):
        com.query("the answer to this query is empty")
    com.close()


def test_pfeiffer_tpg_start(started_pfeiffer_tpg):
    com, pg = started_pfeiffer_tpg
    # starting again should work
    com.put_text(chr(6))
    com.put_text(",".join(["Unknown", dev.PfeifferTPG.SensorTypes.CMR.name]))
    pg.start()
    assert pg.number_of_sensors == 2
    assert pg.sensors[0] == "Unknown"
    assert pg.sensors[1] == "APR/CMR Linear Gauge"


def test_pfeiffer_com_error(com_config, dev_config):
    wrong_config = dict(com_config)
    wrong_config["port"] = "NOT A PORT"
    tpg = dev.PfeifferTPG(wrong_config, dev_config)
    assert not tpg.com.is_open

    with pytest.raises(comm.SerialCommunicationIOError):
        tpg.start()

    tpg = dev.PfeifferTPG(com_config, dev_config)
    assert not tpg.com.is_open

    with pytest.raises(comm.SerialCommunicationIOError):
        tpg.identify_sensors()
    tpg.sensors = [0]
    with pytest.raises(comm.SerialCommunicationIOError):
        tpg.measure(1)
    with pytest.raises(comm.SerialCommunicationIOError):
        tpg.measure_all()
    with pytest.raises(comm.SerialCommunicationIOError):
        tpg.set_full_scale_unitless([1])
    with pytest.raises(comm.SerialCommunicationIOError):
        tpg.get_full_scale_unitless()
    with pytest.raises(comm.SerialCommunicationIOError):
        tpg.set_full_scale_mbar([100])
    with pytest.raises(comm.SerialCommunicationIOError):
        tpg.get_full_scale_mbar()


def test_identify_sensors(started_pfeiffer_tpg):
    com, pg = started_pfeiffer_tpg
    # example with 3 sensors
    com.put_text(chr(6))
    com.put_text(
        ",".join(
            [
                dev.PfeifferTPG.SensorTypes.PKR.name,
                dev.PfeifferTPG.SensorTypes.CMR.name,
                dev.PfeifferTPG.SensorTypes.IKR.name,
            ]
        )
    )
    pg.identify_sensors()
    assert com.get_written() == "TID"
    assert com.get_written() == chr(5)
    assert pg.number_of_sensors == 3
    assert pg.sensors[0] == dev.PfeifferTPG.SensorTypes.PKR.name
    assert pg.sensors[1] == dev.PfeifferTPG.SensorTypes.CMR.name
    assert pg.sensors[2] == dev.PfeifferTPG.SensorTypes.IKR.name
    # wrong answer from device
    com.put_text("this will make the command fail")
    with pytest.raises(dev.PfeifferTPGError):
        pg.identify_sensors()


def test_set_display_unit(started_pfeiffer_tpg):
    com, pg = started_pfeiffer_tpg
    # valid str argument
    com.put_text(chr(6))
    pg.set_display_unit("mbar")
    # valid PressureUnits argument
    com.put_text(chr(6))
    pg.set_display_unit(pg.PressureUnits.Pascal)
    # valid PressureUnits argument but no acknowledgment from device
    com.put_text("not an acknowledgment")
    with pytest.raises(dev.PfeifferTPGError):
        pg.set_display_unit(pg.PressureUnits.Pascal)
    # invalid str argument
    with pytest.raises(ValueError):
        pg.set_display_unit("Not an accepted unit")


def test_measure(started_pfeiffer_tpg):
    com, pg = started_pfeiffer_tpg
    # normal case
    com.put_text(chr(6))
    com.put_text(f"{dev.PfeifferTPG.SensorStatus.Ok.value},1.234E-02")
    assert pg.measure(2) == (dev.PfeifferTPG.SensorStatus.Ok.name, 1.234e-2)
    assert com.get_written() == "PR2"
    # underrange
    com.put_text(chr(6))
    com.put_text(f"{dev.PfeifferTPG.SensorStatus.Underrange.value},1.234E-02")
    assert pg.measure(2) == (dev.PfeifferTPG.SensorStatus.Underrange.name, 1.234e-2)
    # overrange
    com.put_text(chr(6))
    com.put_text(f"{dev.PfeifferTPG.SensorStatus.Overrange.value},1.234E-02")
    assert pg.measure(2) == (dev.PfeifferTPG.SensorStatus.Overrange.name, 1.234e-2)
    # error
    com.put_text(chr(6))
    com.put_text(f"{dev.PfeifferTPG.SensorStatus.Sensor_error.value},1.234E-02")
    assert pg.measure(2) == (dev.PfeifferTPG.SensorStatus.Sensor_error.name, 1.234e-2)
    # off
    com.put_text(chr(6))
    com.put_text(f"{dev.PfeifferTPG.SensorStatus.Sensor_off.value},1.234E-02")
    assert pg.measure(2) == (dev.PfeifferTPG.SensorStatus.Sensor_off.name, 1.234e-2)
    # none
    com.put_text(chr(6))
    com.put_text(f"{dev.PfeifferTPG.SensorStatus.No_sensor.value},1.234E-02")
    assert pg.measure(2) == (dev.PfeifferTPG.SensorStatus.No_sensor.name, 1.234e-2)
    # identification error
    com.put_text(chr(6))
    com.put_text(f"{dev.PfeifferTPG.SensorStatus.Identification_error.value},1.234E-02")
    assert pg.measure(2) == (
        dev.PfeifferTPG.SensorStatus.Identification_error.name,
        1.234e-2,
    )
    # wrong channel
    with pytest.raises(ValueError):
        pg.measure(12)
    # no acknowledgment from device
    com.put_text("not an acknowledgment")
    with pytest.raises(dev.PfeifferTPGError):
        pg.measure(1)


def test_measure_all(started_pfeiffer_tpg):
    com, pg = started_pfeiffer_tpg
    # normal case
    com.put_text(chr(6))
    com.put_text(
        f"{dev.PfeifferTPG.SensorStatus.Identification_error.value},1.234E-02,"
        f"{dev.PfeifferTPG.SensorStatus.Ok.value},1.234E-02"
    )
    assert pg.measure_all() == [
        (dev.PfeifferTPG.SensorStatus.Identification_error.name, 1.234e-2),
        (dev.PfeifferTPG.SensorStatus.Ok.name, 1.234e-2),
    ]
    assert com.get_written() == "PRX"
    # no acknowledgment from device
    com.put_text("not an acknowledgment")
    with pytest.raises(dev.PfeifferTPGError):
        pg.measure_all()


def test_set_full_scale_unitless(started_pfeiffer_tpg):
    com, pg = started_pfeiffer_tpg
    com.put_text(chr(6))
    pg.set_full_scale_unitless([1, 2])
    assert com.get_written() == "FSR,1,2"
    # no acknowledgment from device
    com.put_text("not an acknowledgment")
    with pytest.raises(dev.PfeifferTPGError):
        pg.set_full_scale_unitless([1, 2])
    # wrong values
    com.put_text(chr(6))
    with pytest.raises(ValueError):
        pg.set_full_scale_unitless([12, 24])
    # wrong number of values
    com.put_text(chr(6))
    with pytest.raises(ValueError):
        pg.set_full_scale_unitless([12, 24, 32])


def test_get_full_scale_unitless(started_pfeiffer_tpg):
    com, pg = started_pfeiffer_tpg
    com.put_text(chr(6))
    com.put_text("2,0")
    assert pg.get_full_scale_unitless() == [2, 0]
    assert com.get_written() == "FSR"
    # no acknowledgment from device
    com.put_text("not an acknowledgment")
    with pytest.raises(dev.PfeifferTPGError):
        pg.get_full_scale_unitless()
    # wrong answer from device
    com.put_text(chr(6))
    com.put_text("12,24")
    with pytest.raises(dev.PfeifferTPGError):
        pg.get_full_scale_unitless()


def test_set_full_scale_mbar(started_pfeiffer_tpg):
    com, pg = started_pfeiffer_tpg
    com.put_text(chr(6))
    pg.set_full_scale_mbar([100, 1])
    fsr = pg.config.model.full_scale_ranges
    assert com.get_written() == f"FSR,{fsr[100]},{fsr[1]}"
    # no acknowledgment from device
    com.put_text("not an acknowledgment")
    with pytest.raises(dev.PfeifferTPGError):
        pg.set_full_scale_mbar([100, 1])
    # wrong values
    com.put_text(chr(6))
    with pytest.raises(ValueError):
        pg.set_full_scale_mbar([12, 24])
    # wrong number of values
    com.put_text(chr(6))
    with pytest.raises(ValueError):
        pg.set_full_scale_mbar([12, 24, 32])


def test_get_full_scale_mbar(started_pfeiffer_tpg):
    com, pg = started_pfeiffer_tpg
    com.put_text(chr(6))
    com.put_text("2,0")
    fsr_rev = pg.config.model.full_scale_ranges_reversed
    assert pg.get_full_scale_mbar() == [fsr_rev[2], fsr_rev[0]]
    assert com.get_written() == "FSR"
    # no acknowledgment from device
    com.put_text("not an acknowledgment")
    with pytest.raises(dev.PfeifferTPGError):
        pg.get_full_scale_mbar()
    # wrong answer from device
    com.put_text(chr(6))
    com.put_text("12,24")
    with pytest.raises(dev.PfeifferTPGError):
        pg.get_full_scale_mbar()

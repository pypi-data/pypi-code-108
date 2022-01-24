#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the .dev.crylas sub-package.
"""

import logging
import time

import pytest

from hvl_ccb import comm, dev
from masked_comm.serial import (
    LoopSerialCommunication,
    CryLasLaserLoopSerialCommunication,
)

logging.basicConfig(level=logging.ERROR)


@pytest.fixture(scope="module")
def laser_com_config():
    return {
        "port": "loop://?logging=debug",
        "baudrate": 19200,
        "parity": dev.CryLasLaserSerialCommunicationConfig.Parity.NONE,
        "stopbits": dev.CryLasLaserSerialCommunicationConfig.Stopbits.ONE,
        "bytesize": dev.CryLasLaserSerialCommunicationConfig.Bytesize.EIGHTBITS,
        "terminator": b"\n",
        "timeout": 0.1,
    }


@pytest.fixture(scope="module")
def laser_config():
    return {
        "polling_period": 0.05,
        "auto_laser_on": False,
        "init_shutter_status": dev.CryLasLaserConfig.ShutterStatus.CLOSED,
    }


@pytest.fixture
def started_laser(laser_com_config, laser_config):
    com = CryLasLaserLoopSerialCommunication(laser_com_config)
    com.open()
    com.put_text(dev.CryLasLaser.AnswersShutter.CLOSED.value)
    com.put_text(dev.CryLasLaser.AnswersStatus.READY.value)
    com.put_text("")
    with dev.CryLasLaser(com, laser_config) as las:
        while com.get_written() is not None:
            pass
        yield com, las


def test_laser_com(laser_com_config):
    com = CryLasLaserLoopSerialCommunication(laser_com_config)
    # test error when com closed
    assert not com.is_open
    with pytest.raises(comm.SerialCommunicationIOError):
        com.query("attempting to do a query while com is closed", "prefix")
    # the com still gets written
    com.get_written()
    with pytest.raises(comm.SerialCommunicationIOError):
        com.query_all("attempting to do a query while com is closed", "prefix")
    # the com still gets written
    com.get_written()
    # test query and query_all work when com opened
    com.open()
    com.put_text("ignore this first")
    com.put_text("prefix hello")
    assert com.query("query", "prefix", "post query command") == "prefix hello"
    assert com.get_written() == "query"
    assert com.get_written() == "post query command"
    com.put_text("ignore this first")
    com.put_text("prefix hello")
    com.put_text("prefix hi")
    com.put_text("prefix welcome")
    com.put_text(f"{dev.CryLasLaserSerialCommunication.READ_TEXT_SKIP_PREFIXES[0]} nah")
    com.put_text("")
    assert com.query_all("query", "prefix") == [
        "prefix hello",
        "prefix hi",
        "prefix welcome",
    ]
    assert com.get_written() == "query"
    com.close()


def test_laser_instantiation(laser_com_config, laser_config):
    las = dev.CryLasLaser(laser_com_config)
    assert las is not None

    wrong_config = dict(laser_config)
    wrong_config["polling_period"] = [-1]
    with pytest.raises(TypeError):
        dev.CryLasLaser(laser_com_config, wrong_config)
    wrong_config["polling_period"] = -1
    with pytest.raises(ValueError):
        dev.CryLasLaser(laser_com_config, wrong_config)

    wrong_config = dict(laser_config)
    wrong_config["calibration_factor"] = None
    with pytest.raises(TypeError):
        dev.CryLasLaser(laser_com_config, wrong_config)
    wrong_config["calibration_factor"] = -0.1
    with pytest.raises(ValueError):
        dev.CryLasLaser(laser_com_config, wrong_config)
    wrong_config["calibration_factor"] = 0
    with pytest.raises(ValueError):
        dev.CryLasLaser(laser_com_config, wrong_config)

    wrong_config = dict(laser_config)
    wrong_config["polling_timeout"] = "NaN"
    with pytest.raises(TypeError):
        dev.CryLasLaser(laser_com_config, wrong_config)
    wrong_config["polling_timeout"] = -0.5
    with pytest.raises(ValueError):
        dev.CryLasLaser(laser_com_config, wrong_config)
    wrong_config["polling_timeout"] = 0
    with pytest.raises(ValueError):
        dev.CryLasLaser(laser_com_config, wrong_config)

    wrong_config = dict(laser_config)
    wrong_config["init_shutter_status"] = ()
    with pytest.raises(TypeError):
        dev.CryLasLaser(laser_com_config, wrong_config)
    wrong_config["init_shutter_status"] = 2
    with pytest.raises(ValueError):
        dev.CryLasLaser(laser_com_config, wrong_config)


def test_laser_start(laser_com_config, laser_config):
    com = CryLasLaserLoopSerialCommunication(laser_com_config)
    las = dev.CryLasLaser(com, laser_config)
    com.open()
    # starting again should work
    com.put_text(dev.CryLasLaser.AnswersShutter.CLOSED.value)
    com.put_text(las.AnswersStatus.READY.value)
    com.put_text("")
    las.start()
    assert las.laser_status == las.LaserStatus.READY_INACTIVE
    # test case: system not immediately ready, execution not blocked
    las.laser_status = las.LaserStatus.UNREADY_INACTIVE
    com.put_text(dev.CryLasLaser.AnswersShutter.CLOSED.value)
    com.put_text(las.AnswersStatus.READY.value)
    com.put_text("")
    las.start()
    com.put_text(dev.CryLasLaser.AnswersShutter.CLOSED.value)
    las.close_shutter()
    # waiting for the polling thread
    las.wait_until_ready()
    assert las.laser_status == las.LaserStatus.READY_INACTIVE
    # teardown
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.stop()

    # error on input jibrish
    com = CryLasLaserLoopSerialCommunication(laser_com_config)
    las = dev.CryLasLaser(com, laser_config)
    com.open()
    com.put_text(dev.CryLasLaser.AnswersShutter.CLOSED.value)
    com.put_text("STATUS: Not one of expected answers")
    with pytest.raises(ValueError):
        las.start()


def test_laser_wait_until_ready(laser_com_config, laser_config):
    # test case: system not immediately ready, execution blocked
    com = CryLasLaserLoopSerialCommunication(laser_com_config)

    las = dev.CryLasLaser(com, laser_config)
    com.open()
    com.put_text(dev.CryLasLaser.AnswersShutter.CLOSED.value)
    com.put_text(las.AnswersStatus.HEAD.value)
    com.put_text("")
    assert las.laser_status == las.LaserStatus.UNREADY_INACTIVE
    las.start()
    assert las.laser_status == las.LaserStatus.UNREADY_INACTIVE
    com.put_text(las.AnswersStatus.READY.value)
    com.put_text("")
    las.wait_until_ready()
    assert las.laser_status == las.LaserStatus.READY_INACTIVE
    com.put_text(dev.CryLasLaser.AnswersShutter.CLOSED.value)
    las.close_shutter()
    com.put_text(dev.CryLasLaser.AnswersStatus.INACTIVE.value)
    com.put_text(dev.CryLasLaser.AnswersShutter.CLOSED.value)
    las.stop()
    assert not com.is_open

    # wait on start
    laser_config_dict = dict(laser_config)
    las = dev.CryLasLaser(com, laser_config_dict)
    com.open()
    com.put_text(las.AnswersShutter.CLOSED.value)
    com.put_text(las.AnswersStatus.READY.value)
    com.put_text("")
    assert las.laser_status == las.LaserStatus.UNREADY_INACTIVE
    las.start()
    assert las.laser_status != las.LaserStatus.UNREADY_INACTIVE
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.close_shutter()
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.stop()

    # no wait if already ready
    las = dev.CryLasLaser(com, laser_config)
    com.open()
    com.put_text(las.AnswersShutter.CLOSED.value)
    com.put_text(las.AnswersStatus.READY.value)
    las.start()
    assert las.laser_status != las.LaserStatus.UNREADY_INACTIVE
    las.wait_until_ready()
    assert las.laser_status != las.LaserStatus.UNREADY_INACTIVE
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.stop()


def test_status_polling_end(laser_com_config, laser_config):
    # test case: system not immediately ready, execution blocked
    com = CryLasLaserLoopSerialCommunication(laser_com_config)

    # stop status polling on device stop
    laser_config_dict = dict(laser_config)
    # set polling period big enough for stop() to trigger before inactive status is read
    laser_config_dict["polling_period"] = 0.2
    las = dev.CryLasLaser(com, laser_config_dict)
    assert las.laser_status == las.LaserStatus.UNREADY_INACTIVE
    com.open()
    com.put_text(las.AnswersShutter.CLOSED.value)
    com.put_text(las.AnswersStatus.HEAD.value)
    com.put_text("")
    las.start()
    las._start_polling()  # BLAH: call internal (other are blocking)
    time.sleep(0.1)  # let the polling thread startup
    assert las._is_polling()  # BLAH: call internal (make public?)
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.stop()
    assert las.laser_status == las.LaserStatus.READY_INACTIVE

    # status polling timeout error
    laser_config_dict = dict(laser_config)
    # set polling period big enough
    laser_config_dict["polling_period"] = 0.2
    laser_config_dict["polling_timeout"] = laser_config_dict["polling_period"] / 10
    las = dev.CryLasLaser(com, laser_config_dict)
    assert las.laser_status == las.LaserStatus.UNREADY_INACTIVE
    com.open()
    com.put_text(las.AnswersShutter.CLOSED.value)
    com.put_text(las.AnswersStatus.HEAD.value)
    las.start()
    assert las.laser_status == las.LaserStatus.UNREADY_INACTIVE
    with pytest.raises(dev.CryLasLaserError):
        las.wait_until_ready()
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.stop()
    assert las.laser_status == las.LaserStatus.READY_INACTIVE


def test_laser_stop(started_laser):
    com, las = started_laser
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.stop()
    assert not com.is_open
    assert las.laser_status == las.LaserStatus.READY_INACTIVE
    assert las.shutter_status == las.ShutterStatus.CLOSED
    # stop is an idempotent operation
    las.stop()
    assert not com.is_open
    assert las.laser_status == las.LaserStatus.READY_INACTIVE
    assert las.shutter_status == las.ShutterStatus.CLOSED


def test_laser_on(started_laser, laser_config):
    com, las = started_laser
    # normal case
    com.put_text(las.AnswersStatus.READY.value)
    com.put_text(las.AnswersStatus.ACTIVE.value)
    com.put_text("")
    assert las.laser_status == las.LaserStatus.READY_INACTIVE
    las.laser_on()
    assert com.get_written() == "LASER ON"
    assert las.laser_status == las.LaserStatus.READY_ACTIVE
    # case laser not ready
    las.laser_status = las.LaserStatus.UNREADY_INACTIVE
    with pytest.raises(dev.CryLasLaserNotReadyError):
        las.laser_on()
    # case laser already on
    las.laser_status = las.LaserStatus.READY_ACTIVE
    com.put_text("Laser is already on")
    las.laser_on()
    # case command fails
    las.laser_status = las.LaserStatus.READY_INACTIVE
    com.put_text("The command is not working")
    with pytest.raises(dev.CryLasLaserError):
        las.laser_on()
    # teardown
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.stop()
    assert not com.is_open

    laser_config_dict = dict(laser_config)
    laser_config_dict["auto_laser_on"] = True
    las = dev.CryLasLaser(com, laser_config_dict)
    assert las.laser_status == las.LaserStatus.UNREADY_INACTIVE
    com.open()
    com.put_text(las.AnswersShutter.CLOSED.value)
    com.put_text(las.AnswersStatus.READY.value)
    com.put_text("")
    com.put_text(las.AnswersStatus.ACTIVE.value)
    las.start()
    las.wait_until_ready()
    assert las.laser_status == las.LaserStatus.READY_ACTIVE
    com.put_text(las.AnswersStatus.ACTIVE.value)
    las.laser_on()
    assert las.laser_status == las.LaserStatus.READY_ACTIVE
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.stop()
    assert not com.is_open

    laser_config_dict = dict(laser_config)
    laser_config_dict["auto_laser_on"] = True
    las = dev.CryLasLaser(com, laser_config_dict)
    assert las.laser_status == las.LaserStatus.UNREADY_INACTIVE
    com.open()
    com.put_text(las.AnswersShutter.CLOSED.value)
    com.put_text(las.AnswersStatus.HEAD.value)
    com.put_text("")
    com.put_text(las.AnswersStatus.READY.value)
    com.put_text("")
    com.put_text(las.AnswersStatus.ACTIVE.value)
    las.start()
    las.wait_until_ready()
    assert las.laser_status == las.LaserStatus.READY_ACTIVE
    com.put_text(las.AnswersStatus.ACTIVE.value)
    com.put_text("")
    las.laser_on()
    assert las.laser_status == las.LaserStatus.READY_ACTIVE
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)


def test_laser_off(started_laser):
    com, las = started_laser
    # normal case
    las.laser_status = las.LaserStatus.READY_ACTIVE
    com.put_text(las.AnswersStatus.INACTIVE.value)
    las.laser_off()
    assert com.get_written() == "LASER OFF"
    assert las.laser_status == las.LaserStatus.READY_INACTIVE
    # case laser already off
    las.laser_status = las.LaserStatus.READY_INACTIVE
    com.put_text("Laser is already off")
    las.laser_off()
    # case command fails
    las.laser_status = las.LaserStatus.READY_ACTIVE
    com.put_text("The command is not working")
    with pytest.raises(dev.CryLasLaserError):
        las.laser_off()
    # teardown
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)


def test_laser_open_shutter(started_laser):
    com, las = started_laser
    # normal case
    com.put_text(las.AnswersShutter.OPENED.value)
    las.open_shutter()
    assert com.get_written() == "Shutter 1"
    assert las.shutter_status == las.ShutterStatus.OPENED
    # case command fails
    com.put_text("The command is not working")
    with pytest.raises(dev.CryLasLaserError):
        las.open_shutter()
    # teardown
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)


def test_laser_close_shutter(started_laser):
    com, las = started_laser
    # normal case
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.close_shutter()
    assert com.get_written() == "Shutter 0"
    assert las.shutter_status == las.ShutterStatus.CLOSED
    # case command fails
    com.put_text("The command is not working")
    with pytest.raises(dev.CryLasLaserError):
        las.close_shutter()
    # teardown
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)


def test_laser_set_init_shutter_status(laser_com_config, laser_config):
    # test with init CLOSED
    com = CryLasLaserLoopSerialCommunication(laser_com_config)
    las = dev.CryLasLaser(com, laser_config)
    # test when command fails
    com.open()
    com.put_text("")
    with pytest.raises(dev.CryLasLaserError):
        las.set_init_shutter_status()
    # test when command succeeds and there is nothing to do
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.set_init_shutter_status()
    # test when command succeeds and the laser should be closed
    com.put_text(las.AnswersShutter.OPENED.value)
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.set_init_shutter_status()
    # teardown
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.stop()
    # test with init OPENED
    com = CryLasLaserLoopSerialCommunication(laser_com_config)
    laser_config["init_shutter_status"] = dev.CryLasLaserConfig.ShutterStatus.OPENED
    las = dev.CryLasLaser(com, laser_config)
    com.open()
    # test when command succeeds and there is nothing to do
    com.put_text(las.AnswersShutter.OPENED.value)
    las.set_init_shutter_status()
    # test when command succeeds and the laser should be opened
    com.put_text(las.AnswersShutter.CLOSED.value)
    com.put_text(las.AnswersShutter.OPENED.value)
    las.set_init_shutter_status()
    # teardown
    laser_config["init_shutter_status"] = dev.CryLasLaserConfig.ShutterStatus.CLOSED
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)


def test_laser_update_laser_status(started_laser):
    com, las = started_laser
    assert las.laser_status == las.LaserStatus.READY_INACTIVE
    # no answer error
    com.put_text("")
    with pytest.raises(dev.CryLasLaserError):
        las.update_laser_status()
    # unexpected answer error
    com.put_text(las.AnswersStatus.TEC1.value)
    com.put_text(las.AnswersStatus.HEAD.value)
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersStatus.READY.value)
    com.put_text("")
    with pytest.raises(dev.CryLasLaserError):
        las.update_laser_status()
    # ignore some lines and updated status
    com.put_text(las.AnswersShutter.OPENED.value)
    com.put_text(las.AnswersStatus.HEAD.value)
    com.put_text("")
    las.update_laser_status()
    assert las.laser_status == las.LaserStatus.UNREADY_INACTIVE
    com.put_text(las.AnswersStatus.READY.value)
    com.put_text("")
    las.update_laser_status()
    assert las.laser_status == las.LaserStatus.READY_INACTIVE
    com.put_text(las.AnswersStatus.ACTIVE.value)
    com.put_text("")
    las.update_laser_status()
    assert las.laser_status == las.LaserStatus.READY_ACTIVE
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text("")
    with pytest.raises(dev.CryLasLaserError):
        las.update_laser_status()
    las.laser_status = las.LaserStatus.UNREADY_INACTIVE
    com.put_text(las.AnswersStatus.HEAD.value)
    com.put_text("")
    las.update_laser_status()
    assert las.laser_status == las.LaserStatus.UNREADY_INACTIVE
    # teardown
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)


def test_laser_update_shutter_status(started_laser):
    com, las = started_laser
    com.put_text(las.AnswersShutter.CLOSED.value)
    las.update_shutter_status()
    assert las.shutter_status == las.ShutterStatus.CLOSED
    com.put_text(las.AnswersShutter.OPENED.value)
    las.update_shutter_status()
    assert las.shutter_status == las.ShutterStatus.OPENED
    com.put_text("")
    with pytest.raises(dev.CryLasLaserError):
        las.update_shutter_status()
    # teardown
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)


def test_laser_update_repetition_rate(started_laser):
    com, las = started_laser
    com.put_text("Impuls=enabled 10Hz")
    las.update_repetition_rate()
    assert las.repetition_rate == las.RepetitionRates.SOFTWARE_INTERNAL_TEN
    com.put_text("Impuls=disabled, extern Trigger")
    las.update_repetition_rate()
    assert las.repetition_rate == las.RepetitionRates.HARDWARE
    com.put_text("no answer to query")
    with pytest.raises(dev.CryLasLaserError):
        las.update_repetition_rate()
    com.put_text("Impuls=enabled but no number provided")
    with pytest.raises(dev.CryLasLaserError):
        las.update_repetition_rate()
    # teardown
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)


def test_laser_update_target_pulse_energy(started_laser):
    com, las = started_laser
    com.put_text("PD-Sollwert=46000")
    las.update_target_pulse_energy()
    assert las.target_pulse_energy == int(46000 * las.config.calibration_factor / 1000)
    com.put_text("")
    with pytest.raises(dev.CryLasLaserError):
        las.update_target_pulse_energy()
    # teardown
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)


def test_laser_get_pulse_energy_and_rate(started_laser):
    com, las = started_laser
    # test that the command works
    com.put_text(
        "IST: LDTemp=0, NLOTemp=1, CaseTemp=2,"
        " PD=46000, D_I= 4, freq=0, LDE=5, RegOFF=7"
    )
    assert las.get_pulse_energy_and_rate() == (200, 0)
    assert com.get_written() == "DB1"
    assert com.get_written() == "DB0"
    # test that the command fails
    com.put_text("")
    with pytest.raises(dev.CryLasLaserError):
        las.get_pulse_energy_and_rate()
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)


def test_laser_set_repetition_rate(started_laser):
    com, las = started_laser
    # check param type int
    com.put_text("Impuls=enabled 10Hz")
    las.set_repetition_rate(10)
    assert las.repetition_rate.value == 10
    assert com.get_written() == f"BOO IP{las.RepetitionRates(10).send_value}"
    # check param type RepetitionRates
    com.put_text("Impuls=enabled 20Hz")
    las.set_repetition_rate(las.RepetitionRates(20))
    assert las.repetition_rate == las.RepetitionRates(20)
    assert com.get_written() == f"BOO IP{las.RepetitionRates(20).send_value}"
    # check value Error
    with pytest.raises(ValueError):
        las.set_repetition_rate(30)
    # command fails
    com.put_text("This did not work")
    with pytest.raises(dev.CryLasLaserError):
        las.set_repetition_rate(10)
    # hardware trigger
    com.put_text("No answer is expected in this case")
    las.set_repetition_rate(0)
    # teardown
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)


def test_laser_set_pulse_energy(started_laser):
    com, las = started_laser
    # case successful
    val = 100
    cmd_val = int(val * 1000 / las.config.calibration_factor)
    com.put_text(f"PD-Sollwert={cmd_val}")
    las.set_pulse_energy(val)
    assert las.target_pulse_energy == int(
        cmd_val * las.config.calibration_factor / 1000
    )
    assert com.get_written() == f"BOO SE {cmd_val}"
    # case unsuccessful
    val = 100
    cmd_val = int(val * 1000 / las.config.calibration_factor)
    com.put_text("PD-Sollwert=46000")
    with pytest.raises(dev.CryLasLaserError):
        las.set_pulse_energy(val)
    assert com.get_written() == f"BOO SE {cmd_val}"
    # case command fails
    com.put_text("The command failed")
    with pytest.raises(dev.CryLasLaserError):
        las.set_pulse_energy(val)
    # teardown
    com.put_text(las.AnswersStatus.INACTIVE.value)
    com.put_text(las.AnswersShutter.CLOSED.value)


def test_laser_com_error(laser_com_config, laser_config):

    wrong_config = dict(laser_com_config)
    wrong_config["port"] = "NOT A PORT"
    las = dev.CryLasLaser(wrong_config, laser_config)
    assert not las.com.is_open

    with pytest.raises(comm.SerialCommunicationIOError):
        las.start()

    las = dev.CryLasLaser(laser_com_config, laser_config)
    assert not las.com.is_open

    assert las.laser_status is las.LaserStatus.UNREADY_INACTIVE
    with pytest.raises(comm.SerialCommunicationIOError):
        las.wait_until_ready()
    las.laser_status = las.LaserStatus.READY_INACTIVE
    with pytest.raises(comm.SerialCommunicationIOError):
        las.laser_on()
    with pytest.raises(comm.SerialCommunicationIOError):
        las.laser_off()
    with pytest.raises(comm.SerialCommunicationIOError):
        las.open_shutter()
    with pytest.raises(comm.SerialCommunicationIOError):
        las.close_shutter()
    with pytest.raises(comm.SerialCommunicationIOError):
        las.set_init_shutter_status()
    with pytest.raises(comm.SerialCommunicationIOError):
        las.update_laser_status()
    with pytest.raises(comm.SerialCommunicationIOError):
        las.update_shutter_status()
    with pytest.raises(comm.SerialCommunicationIOError):
        las.update_repetition_rate()
    with pytest.raises(comm.SerialCommunicationIOError):
        las.update_target_pulse_energy()
    with pytest.raises(comm.SerialCommunicationIOError):
        las.get_pulse_energy_and_rate()
    with pytest.raises(comm.SerialCommunicationIOError):
        las.set_repetition_rate(dev.CryLasLaser.RepetitionRates.SOFTWARE_INTERNAL_TEN)
    with pytest.raises(comm.SerialCommunicationIOError):
        las.set_pulse_energy(200)


def test_auto_laser_on(laser_com_config, laser_config):
    com = CryLasLaserLoopSerialCommunication(laser_com_config)

    config_where_auto_laser_is_on = dict(laser_config)
    config_where_auto_laser_is_on["auto_laser_on"] = True

    las = dev.CryLasLaser(com, config_where_auto_laser_is_on)

    com.open()

    # answers to queries made during start()
    com.put_text(dev.CryLasLaser.AnswersShutter.CLOSED.value)
    com.put_text(las.AnswersStatus.HEAD.value)
    com.put_text("")

    # check that the laser status is inactive before start()
    assert las.laser_status == las.LaserStatus.UNREADY_INACTIVE

    las.start()

    # queries that should have been made during start
    assert com.get_written() == "Shutter"
    assert com.get_written() == "STATUS"

    com.put_text(las.AnswersStatus.READY.value)
    com.put_text(las.AnswersStatus.ACTIVE.value)
    com.put_text("")

    time.sleep(1)
    assert com.get_written() == "STATUS"
    assert com.get_written() == "LASER ON"

    assert las.laser_status == las.LaserStatus.READY_ACTIVE


# tests attenuator


@pytest.fixture(scope="module")
def attenuator_com_config():
    return {
        "port": "loop://?logging=debug",
        "baudrate": 9600,
        "parity": dev.CryLasLaserSerialCommunicationConfig.Parity.NONE,
        "stopbits": dev.CryLasLaserSerialCommunicationConfig.Stopbits.ONE,
        "bytesize": dev.CryLasLaserSerialCommunicationConfig.Bytesize.EIGHTBITS,
        "terminator": b"",
        "timeout": 0.1,
    }


@pytest.fixture(scope="module")
def attenuator_config():
    return {
        "init_attenuation": 0,
        "response_sleep_time": 0.01,
    }


@pytest.fixture
def started_attenuator(attenuator_com_config, attenuator_config):
    serial_port = LoopSerialCommunication(attenuator_com_config)
    serial_port.open()
    serial_port.put_bytes(bytes([0, 0]))
    with dev.CryLasAttenuator(serial_port, attenuator_config) as att:
        while serial_port.get_written() is not None:
            pass
        yield serial_port, att


def test_attenuator_instantiation(attenuator_com_config, attenuator_config):
    att = dev.CryLasAttenuator(attenuator_com_config)
    assert att is not None

    wrong_config = dict(attenuator_config)
    wrong_config["init_attenuation"] = -1
    with pytest.raises(ValueError):
        dev.CryLasAttenuator(attenuator_com_config, wrong_config)

    wrong_config = dict(attenuator_config)
    wrong_config["response_sleep_time"] = 0
    with pytest.raises(ValueError):
        dev.CryLasAttenuator(attenuator_com_config, wrong_config)
    wrong_config["response_sleep_time"] = -0.1
    with pytest.raises(ValueError):
        dev.CryLasAttenuator(attenuator_com_config, wrong_config)


def test_attenuator_start(started_attenuator):
    com, att = started_attenuator
    com.put_bytes(bytes([0, 0]))
    att.start()
    assert com.get_written()


def test_attenuator_set_attenuation(started_attenuator):
    com, att = started_attenuator
    com.put_bytes(bytes([0, 0]))
    att.set_attenuation(50)
    assert att.attenuation == 50
    com.put_bytes(bytes([1, 0]))
    with pytest.raises(dev.CryLasAttenuatorError):
        att.set_attenuation(50)
    with pytest.raises(ValueError):
        att.set_attenuation(-1)


def test_attenuator_com_error(attenuator_com_config, attenuator_config):

    wrong_config = dict(attenuator_com_config)
    wrong_config["port"] = "NOT A PORT"
    att = dev.CryLasAttenuator(wrong_config, attenuator_config)
    assert not att.com.is_open
    with pytest.raises(comm.SerialCommunicationIOError):
        att.start()

    att = dev.CryLasAttenuator(attenuator_com_config, attenuator_config)
    assert not att.com.is_open
    with pytest.raises(comm.SerialCommunicationIOError):
        att.set_attenuation(50)


def test_attenuator_set_init_attenuation(started_attenuator):
    com, att = started_attenuator
    com.put_bytes(bytes([0, 0]))
    att.set_init_attenuation()
    assert att.attenuation == att.config.init_attenuation


def test_attenuator_set_transmission(started_attenuator):
    com, att = started_attenuator
    com.put_bytes(bytes([0, 0]))
    att.set_transmission(50)
    assert att.transmission == 50
    com.put_bytes(bytes([1, 0]))
    with pytest.raises(dev.CryLasAttenuatorError):
        att.set_transmission(50)
    with pytest.raises(ValueError):
        att.set_transmission(-1)

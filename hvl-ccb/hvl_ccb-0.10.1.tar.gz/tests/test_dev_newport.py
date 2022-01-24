#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the dev.newport sub-package.
"""

import logging

import pytest

from hvl_ccb import dev, comm
from masked_comm.serial import NewportLoopSerialCommunication

logging.basicConfig(level=logging.ERROR)


@pytest.fixture(scope="module")
def com_config():
    return {
        "port": "loop://?logging=debug",
        "baudrate": 57600,
        "parity": dev.NewportSMC100PPSerialCommunicationConfig.Parity.NONE,
        "stopbits": dev.NewportSMC100PPSerialCommunicationConfig.Stopbits.ONE,
        "bytesize": dev.NewportSMC100PPSerialCommunicationConfig.Bytesize.EIGHTBITS,
        "terminator": b"\r\n",
        "timeout": 0.05,
    }


@pytest.fixture(scope="module")
def dev_config():
    return {
        "address": 1,
        "user_position_offset": 10,
        "screw_scaling": 1,
        "exit_configuration_wait_sec": 0.01,
        "move_wait_sec": 0.01,
        "acceleration": 10,
        "backlash_compensation": 0,
        "hysteresis_compensation": 0.015,
        "micro_step_per_full_step_factor": 100,
        "motion_distance_per_full_step": 0.01,
        "home_search_type": 2,
        "jerk_time": 0.04,
        "home_search_velocity": 4,
        "home_search_timeout": 1.01,
        "home_search_polling_interval": 0.01,
        "peak_output_current_limit": 0.4,
        "rs485_address": 2,
        "negative_software_limit": -23.5,
        "positive_software_limit": 25,
        "velocity": 4,
        "base_velocity": 0,
        "stage_configuration": 3,
    }


@pytest.fixture
def started_newport(com_config, dev_config):
    com = NewportLoopSerialCommunication(com_config)
    com.open()

    mot = dev.NewportSMC100PP(com, dev_config)
    motor_config = mot.config.motor_config

    # put answer to get_state query (NO_REF)
    state = dev.NewportSMC100PP.StateMessages.NO_REF_FROM_RESET.value
    com.put_text(f"{dev_config['address']}TS0000{state}")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")

    # put answer to get_configuration query (matching config values)
    com.put_text("1PW1")
    com.put_text("1ID hello")
    for param in motor_config:
        cmd = dev.NewportConfigCommands(param).name
        val = motor_config[param]  # matching config values
        com.put_text(f"1{cmd}{val}")
        logging.debug(f"putting to com: 1{cmd}{val}")
    com.put_text("1PW0")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")

    # put answer to initialize command
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")

    # put answer to get_state query in wait_until_motor_initialized (READY)
    state = dev.NewportSMC100PP.StateMessages.READY_FROM_HOMING.value
    com.put_text(f"{dev_config['address']}TS0000{state}")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")

    # put position as if just initialized
    mot.position = dev_config["user_position_offset"]

    with mot:
        while com.get_written() is not None:
            pass
        yield com, mot
        if com.is_open:
            # required for a correct dev stop
            # Note: this should be rather mot.is_started
            com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")


def test_com_read_text(com_config):
    com = NewportLoopSerialCommunication(com_config)
    com.open()
    # check that no error is raised
    com.put_text('regular text')
    assert com.read_text().strip() == 'regular text'
    # check that NewportMotorPowerSupplyWasCutError is raised
    com.put_text('\x00regular text')
    with pytest.raises(dev.NewportMotorPowerSupplyWasCutError):
        com.read_text()
    com.put_bytes(b'\xf8\x00')
    with pytest.raises(dev.NewportMotorPowerSupplyWasCutError):
        com.read_text()


def test_com_check_for_error(com_config):
    com = NewportLoopSerialCommunication(com_config)
    com.open()
    # check that no error is raised
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    com.check_for_error(1)
    assert com.get_written() == "1TE"
    # check that NewportControllerError is raised
    com.put_text(f"1TE{com.ControllerErrors.CMD_NOT_ALLOWED.value}")
    with pytest.raises(dev.NewportControllerError):
        com.check_for_error(1)
    assert com.get_written() == "1TE"
    # check that SerialCommunicationIOError is raised if the com is closed
    com.close()
    with pytest.raises(comm.SerialCommunicationIOError):
        com.check_for_error(1)


def test_com_send_command(com_config):
    com = NewportLoopSerialCommunication(com_config)
    com.open()

    # check that the correct message is sent
    add = 3
    cmd = "command"
    param = 32.5
    com._send_command_without_checking_error(add, cmd, param)
    assert com.get_written() == f"{add}{cmd}{param}"

    # check that the command is sent an no error is signaled

    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    com.send_command(1, "command", 12)
    assert com.get_written() == "1command12"
    assert com.get_written() == "1TE"
    # check that NewportControllerError is raised
    com.put_text(f"1TE{com.ControllerErrors.CMD_NOT_ALLOWED.value}")
    with pytest.raises(dev.NewportControllerError):
        com.send_command(1, "command")
    assert com.get_written() == "1command"
    assert com.get_written() == "1TE"
    # check that SerialCommunicationIOError is raised if the com is closed
    com.close()
    with pytest.raises(comm.SerialCommunicationIOError):
        com.send_command(1, "command")


def test_com_query(com_config):
    com = NewportLoopSerialCommunication(com_config)
    com.open()
    # check that the correct answer is returned
    com.put_text("1query answer")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    assert com.query(1, "query", "?") == "answer"
    assert com.get_written() == "1query?"
    assert com.get_written() == "1TE"
    # also without param
    com.put_text("1query answer")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    assert com.query(1, "query") == "answer"
    # check that NewportSerialCommunicationError is raised if unexpected answer
    com.put_text("")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    with pytest.raises(dev.NewportSerialCommunicationError):
        com.query(1, "query")
    # check that NewportControllerError is raised
    com.put_text("wrong answer")
    com.put_text(f"1TE{com.ControllerErrors.CMD_NOT_ALLOWED.value}")
    with pytest.raises(dev.NewportControllerError):
        com.query(1, "query")
    # check that SerialCommunicationIOError is raised if the com is closed
    com.close()
    with pytest.raises(comm.SerialCommunicationIOError):
        com.query(1, "query")


def test_com_query_multiple(com_config):
    com = NewportLoopSerialCommunication(com_config)
    com.open()

    # normal case
    add = 3
    cmd = "ZT"
    prefixes = ["one", "two", "three"]
    values = [1, 2, 3]
    for p, v in zip(prefixes, values):
        com.put_text(f"{p}{v}")
    com.put_text(f"{add}TE{com.ControllerErrors.NO_ERROR.value}")
    assert com.query_multiple(add, cmd, prefixes) == [str(v) for v in values]

    # wrong prefix
    wrong_prefixes = ["one", "two", "four"]
    for p, v in zip(prefixes, values):
        com.put_text(f"{p}{v}")
    com.put_text(f"{add}TE{com.ControllerErrors.NO_ERROR.value}")
    with pytest.raises(dev.NewportSerialCommunicationError):
        com.query_multiple(add, cmd, wrong_prefixes)

    # check that NewportControllerError is raised
    for p, v in zip(prefixes, values):
        com.put_text(f"{p}{v}")
    com.put_text(f"{add}TE{com.ControllerErrors.CMD_NOT_ALLOWED.value}")
    with pytest.raises(dev.NewportControllerError):
        com.query_multiple(add, cmd, prefixes)

    # check that SerialCommunicationIOError is raised if the com is closed
    com.close()
    with pytest.raises(comm.SerialCommunicationIOError):
        com.query_multiple(add, cmd, prefixes)


def test_dev_config(dev_config):
    # currently there are no non-default config values
    dev.NewportSMC100PPConfig()

    config = dev.NewportSMC100PPConfig(**dev_config)
    for key, value in dev_config.items():
        assert getattr(config, key) == value

    # test _motor_config update on force_value
    fieldname = "acceleration"
    value = dict(dev_config)[fieldname]
    # first call to motor_config creates cache
    assert config.motor_config[fieldname] == value
    value = value - 1
    config.force_value(fieldname, value)
    # check that cache is updated
    assert config.motor_config[fieldname] == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"address": -1},
        {"screw_scaling": -1},
        {"exit_configuration_wait_sec": -1},
        {"move_wait_sec": -1},
        {"acceleration": -1},
        {"backlash_compensation": -1},
        {"hysteresis_compensation": -1},
        {"micro_step_per_full_step_factor": -1},
        {"motion_distance_per_full_step": -1},
        {"home_search_type": -1},
        {"jerk_time": -1},
        {"home_search_velocity": -1},
        {"home_search_timeout": -1},
        {"home_search_polling_interval": -1},
        {"peak_output_current_limit": -1},
        {"rs485_address": -1},
        {"negative_software_limit": 1},
        {"positive_software_limit": -1},
        {"velocity": -1},
        {"base_velocity": -1},
        {"stage_configuration": -1},
    ],
)
def test_invalid_config_dict(dev_config, wrong_config_dict):
    invalid_config = dict(dev_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        dev.NewportSMC100PPConfig(**invalid_config)


def test_newport_instantiation(com_config, dev_config):
    mot = dev.NewportSMC100PP(com_config)
    assert mot is not None

    mot = dev.NewportSMC100PP(com_config, dev_config)
    assert mot is not None


def test_newport_com_errors(com_config, dev_config):

    wrong_com_config = dict(com_config)
    wrong_com_config["port"] = "NOT A PORT"
    mot = dev.NewportSMC100PP(wrong_com_config, dev_config)
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.start()

    mot = dev.NewportSMC100PP(com_config, dev_config)
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.get_state()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.get_motor_configuration()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.go_to_configuration()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.set_motor_configuration()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.exit_configuration()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.initialize()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.wait_until_motor_initialized()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.reset()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.get_position()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.move_to_absolute_position(10)
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.go_home()
    mot.position = 1
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.move_to_relative_position(1)
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.get_move_duration(10)
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.stop_motion()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.get_acceleration()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.set_acceleration(10)
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.get_controller_information()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.get_positive_software_limit()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.set_positive_software_limit(1)
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.get_negative_software_limit()
    with pytest.raises(comm.SerialCommunicationIOError):
        mot.set_negative_software_limit(-1)


def test_start_and_initialize(com_config, dev_config):
    com = NewportLoopSerialCommunication(com_config)
    com.open()

    # case 1: config unchanged and in NO_REF state
    mot = dev.NewportSMC100PP(com, dev_config)

    # answer to get_state
    state_message = dev.NewportSMC100PP.StateMessages.NO_REF_FROM_RESET
    com.put_text(f"{dev_config['address']}TS0000" + state_message.value)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")

    # answer to get_motor_configuration
    config = mot.config.motor_config
    com.put_text("1PW1")
    com.put_text("1ID hello")
    for param in config:
        cmd = dev.NewportConfigCommands(param).name
        val = config[param]  # matching config values
        com.put_text(f"1{cmd}{val}")
        logging.debug(f"putting to com: 1{cmd}{val}")
    com.put_text("1PW0")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")

    # answer to initialize
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    # answer to wait_until_motor_initialized
    state_message = dev.NewportSMC100PP.StateMessages.READY_FROM_HOMING
    com.put_text(f"{dev_config['address']}TS0000" + state_message.value)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")

    mot.start()
    assert mot.state == state_message.state


def test_start_and_configure(com_config, dev_config):
    com = NewportLoopSerialCommunication(com_config)
    com.open()

    # case 2: config changed and in READY state
    mot = dev.NewportSMC100PP(com, dev_config)

    # answer to get_state
    state_message = dev.NewportSMC100PP.StateMessages.READY_FROM_HOMING
    com.put_text(f"{dev_config['address']}TS0000" + state_message.value)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")

    # answer to get_motor_configuration
    config = mot.config.motor_config
    com.put_text("1PW1")
    com.put_text("1ID hello")
    for param in config:
        cmd = dev.NewportConfigCommands(param).name
        val = config[param] + 1  # changed config values
        com.put_text(f"1{cmd}{val}")
        logging.debug(f"putting to com: 1{cmd}{val}")
    com.put_text("1PW0")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")

    #  answer to reset
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    com.put_text("I just did a reset and I feel talkative.")

    # answer to go_to_configuration
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    # answer to set_motor_configuration
    params = [p for p in config if not ("compensation" in p and config[p] == 0)]
    for _ in params:
        com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    # answer to exit_configuration
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")

    # answer to initialize
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    # answer to wait_until_motor_initialized
    state_message = dev.NewportSMC100PP.StateMessages.READY_FROM_HOMING
    com.put_text(f"{dev_config['address']}TS0000" + state_message.value)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")

    mot.start()
    assert mot.state == state_message.state


def test_stop(started_newport):
    com, mot = started_newport
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.stop()


def test_get_state(started_newport):
    com, mot = started_newport

    state = dev.NewportSMC100PP.StateMessages.MOVING.value
    com.put_text("1TS0000" + state)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.get_state()
    assert com.get_written() == "1TS"
    assert com.get_written() == "1TE"
    assert mot.state == mot.States.MOVING

    # test with another address
    state = dev.NewportSMC100PP.StateMessages.READY_FROM_HOMING.value
    com.put_text("3TS0000" + state)
    com.put_text("3TE" + com.ControllerErrors.NO_ERROR.value)
    mot.get_state(3)
    assert com.get_written() == "3TS"
    assert com.get_written() == "3TE"
    assert mot.state == mot.States.READY

    # test when the motor reports an error
    state = dev.NewportSMC100PP.StateMessages.DISABLE_FROM_READY.value
    com.put_text("1TS0013" + state)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    with pytest.raises(dev.NewportMotorError):
        mot.get_state()
    com.get_written()
    com.get_written()

    # test when an NewportMotorPowerSupplyWasCutError occurs and is skipped
    state = dev.NewportSMC100PP.StateMessages.DISABLE_FROM_READY.value
    com.put_text("\x001TS0000" + state)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    com.put_text("1TS0000" + state)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.get_state()
    assert com.get_written() == "1TS"
    assert com.get_written() == "1TE"
    assert com.get_written() == "1TS"
    assert com.get_written() == "1TE"
    assert mot.state == mot.States.DISABLE


def test_get_motor_configuration(started_newport):
    com, mot = started_newport

    com.put_text("1PW1")
    com.put_text("1ID hello")
    for param in mot.config.motor_config:
        cmd = dev.NewportConfigCommands(param).name
        val = mot.config.motor_config[param]
        com.put_text(f"1{cmd}{val}")
        logging.debug(f"putting to com: 1{cmd}{val}")
    com.put_text("1PW0")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    assert mot.get_motor_configuration() == mot.config.motor_config
    assert com.get_written() == "1ZT"
    assert com.get_written() == "1TE"


def test_go_to_configuration(started_newport):
    com, mot = started_newport
    # artificially put the controller in NOT REFERENCED state
    state = dev.NewportSMC100PP.StateMessages.NO_REF_FROM_RESET.value
    com.put_text("1TS0000" + state)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.get_state()
    com.get_written()
    com.get_written()
    # start the test
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.go_to_configuration()
    assert com.get_written() == "1PW1"
    assert com.get_written() == "1TE"
    assert mot.state == mot.States.CONFIG


def test_set_motor_configuration(started_newport):
    com, mot = started_newport

    config = mot.config.motor_config
    params = [p for p in config if not ("compensation" in p and config[p] == 0)]
    # normal case
    for _ in params:
        com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.set_motor_configuration()
    for param in params:
        cmd = dev.NewportConfigCommands(param).name
        val = config[param]
        assert com.get_written() == f"1{cmd}{val}"
        assert com.get_written() == "1TE"
    # controller error
    error = com.ControllerErrors.PARAM_MISSING_OR_INVALID.value
    com.put_text(f"1TE{error}")
    with pytest.raises(dev.NewportControllerError):
        mot.set_motor_configuration()


def test_exit_configuration(started_newport):
    com, mot = started_newport
    # start the test
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.exit_configuration()
    assert com.get_written() == "1PW0"
    assert com.get_written() == "1TE"
    assert mot.state == mot.States.NO_REF


def test_initialize(started_newport):
    com, mot = started_newport
    # start the test
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.initialize()
    assert com.get_written() == "1OR"
    assert com.get_written() == "1TE"
    assert mot.state == mot.States.READY


def test_wait_until_motor_initialized(started_newport):
    com, mot = started_newport
    # normal case
    state = dev.NewportSMC100PP.StateMessages.HOMING_FROM_RS232.value
    com.put_text("1TS0000" + state)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    state = dev.NewportSMC100PP.StateMessages.READY_FROM_HOMING.value
    com.put_text("1TS0000" + state)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.wait_until_motor_initialized()
    # unexpected final state or timeout
    state = dev.NewportSMC100PP.StateMessages.HOMING_FROM_RS232.value
    com.put_text("1TS0000" + state)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    state = dev.NewportSMC100PP.StateMessages.DISABLE_FROM_MOVING.value
    com.put_text("1TS0000" + state)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    with pytest.raises(dev.NewportControllerError):
        mot.wait_until_motor_initialized()


def test_reset(started_newport):
    com, mot = started_newport
    # start the test
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    com.put_text("I just did a reset and I feel talkative.")
    mot.reset()
    assert com.get_written() == "1RS"
    assert com.get_written() == "1TE"
    assert mot.state == mot.States.NO_REF


def test_get_position(started_newport):
    com, mot = started_newport
    # start the test
    pos = 12
    com.put_text(f"1TP{pos - mot.config.user_position_offset}")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    assert mot.get_position() == pos
    assert com.get_written() == "1TP"
    assert com.get_written() == "1TE"

    # check that an error is raised if the position is ambiguous
    com.put_text("1TP0")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    # answer to the get_state() query
    state = dev.NewportSMC100PP.StateMessages.NO_REF_FROM_RESET.value
    com.put_text("1TS0000" + state)
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    with pytest.raises(dev.NewportUncertainPositionError):
        mot.get_position()


def test_move_to_absolute_position(started_newport):
    com, mot = started_newport
    # start the test
    pos = 3
    # answers to get_position()
    com.put_text(f"1TP{pos - mot.config.user_position_offset}")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    # answers to absolute move command
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.move_to_absolute_position(pos)
    assert com.get_written() == "1TP"
    assert com.get_written() == "1TE"
    assert com.get_written() == f"1PA{pos-mot.config.user_position_offset}"
    assert com.get_written() == "1TE"


def test_go_home(started_newport):
    com, mot = started_newport
    # start the test
    pos = 3
    # answers to get_position()
    com.put_text(f"1TP{pos - mot.config.user_position_offset}")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    # answers to homing command
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.go_home()
    assert com.get_written() == "1TP"
    assert com.get_written() == "1TE"
    assert com.get_written() == "1PA0"
    assert com.get_written() == "1TE"


def test_move_to_relative_position(started_newport):
    com, mot = started_newport
    # start the test
    pos = -3
    mot.position = 20
    # answers to relative move command
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.move_to_relative_position(pos)
    assert com.get_written() == f"1PR{pos}"
    assert com.get_written() == "1TE"


def test_get_move_duration(started_newport):
    com, mot = started_newport
    dist = -3
    duration = 5.2
    mot.position = 0
    com.put_text(f"1PT{duration}")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    assert mot.get_move_duration(dist) == duration
    assert com.get_written() == f"1PT{abs(dist)}"
    assert com.get_written() == "1TE"


def test_stop_motion(started_newport):
    com, mot = started_newport
    # test if stop_motion_works
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.stop_motion()
    assert com.get_written() == "ST"
    assert com.get_written() == "1TE"
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.stop_motion(1)
    assert com.get_written() == "1ST"
    assert com.get_written() == "1TE"


def test_get_acceleration(started_newport):
    com, mot = started_newport
    acc = 5
    com.put_text(f"1AC{acc}")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    assert mot.get_acceleration() == acc
    assert com.get_written() == "1AC?"
    assert com.get_written() == "1TE"


def test_set_acceleration(started_newport):
    com, mot = started_newport
    acc = 5
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.set_acceleration(acc)
    assert com.get_written() == f"1AC{acc}"
    assert com.get_written() == "1TE"


def test_get_controller_information(started_newport):
    com, mot = started_newport
    com.put_text("1VE SMC100PP")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    assert mot.get_controller_information() == "SMC100PP"
    assert com.get_written() == "1VE?"
    assert com.get_written() == "1TE"


def test_get_positive_software_limit(started_newport):
    com, mot = started_newport
    lim = 5
    com.put_text(f"1SR{lim}")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    assert mot.get_positive_software_limit() == lim
    assert com.get_written() == "1SR?"
    assert com.get_written() == "1TE"


def test_get_negative_software_limit(started_newport):
    com, mot = started_newport
    lim = -5
    com.put_text(f"1SL{lim}")
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    assert mot.get_negative_software_limit() == lim
    assert com.get_written() == "1SL?"
    assert com.get_written() == "1TE"


def test_set_positive_software_limit(started_newport):
    com, mot = started_newport
    lim = 5
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.set_positive_software_limit(lim)
    assert com.get_written() == f"1SR{lim}"
    assert com.get_written() == "1TE"


def test_set_negative_software_limit(started_newport):
    com, mot = started_newport
    lim = -5
    com.put_text(f"1TE{com.ControllerErrors.NO_ERROR.value}")
    mot.set_negative_software_limit(lim)
    assert com.get_written() == f"1SL{lim}"
    assert com.get_written() == "1TE"

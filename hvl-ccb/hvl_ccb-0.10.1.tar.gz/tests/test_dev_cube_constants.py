#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Test module for the supercube constants enums.

NOTE: After a variable is set for the first time, the type is fixed! This can usually
happen for numerical values. Therefore, we should always use 'float' as datatype for
numerical variables.

GOOD:
demo_opcua_server.set_var(constants.Power.voltage_target, 0.0)

BAD:
demo_opcua_server.set_var(constants.Power.voltage_target, 0)
"""

import pytest

from hvl_ccb.dev.cube import constants


def test_measurements_scaled_input():
    assert (
        constants._MeasurementChannel("", 1, 100)._CMD_SCALE
        == '"DB_Measurements"."sx_volts_input_1"'
    )
    assert (
        constants._MeasurementChannel("", 3, 100)._CMD_SCALE
        == '"DB_Measurements"."sx_volts_input_3"'
    )


def test_measurements_divider_ratio():
    assert (
        constants._MeasurementChannel("", 1, 100)._CMD_RATIO
        == '"DB_Measurements"."si_Divider_Ratio_1"'
    )
    assert (
        constants._MeasurementChannel("", 3, 100)._CMD_RATIO
        == '"DB_Measurements"."si_Divider_Ratio_3"'
    )


def test_earthing_stick_status():
    assert (
        constants._EarthingStick("", 3)._CMD_STATUS
        == '"DB_Safety_Circuit"."Earthstick_3"."si_HMI_Status"'
    )


def test_earthing_stick_manual():
    assert (
        constants._EarthingStick("", 2)._CMD_MANUAL
        == '"DB_Safety_Circuit"."Earthstick_2"."sx_earthing_manually"'
    )


def test_alarms():
    assert constants._Alarms.alarm(33) == constants._Alarms.ALARM_33
    for n in (0, constants.NUMBER_OF_ALARMS):
        with pytest.raises(ValueError):
            constants._Alarms.alarm(n)


def test_door():
    assert constants._Door(3, "")._CMD == '"DB_Safety_Circuit"."Door_3"."si_HMI_status"'


def test_alarm_text():
    assert constants._AlarmText.get_level(1) == constants._AlarmLevel.STOP
    assert constants._AlarmText.get_coming_message(1) == "Emergency Stop 1 triggered"
    assert constants._AlarmText.get_going_message(1) == "Emergency Stop 1 released"
    assert constants._AlarmText.get_level(1000) == constants._AlarmLevel.NOT_DEFINED
    assert constants._AlarmText.get_coming_message(1000) == "NO ALARM TEXT DEFINED"
    assert constants._AlarmText.get_going_message(1000) == "NO ALARM TEXT DEFINED"


def test_message_board():
    assert constants.MessageBoard.line(3) == constants.MessageBoard.LINE_3
    for n in (0, constants.NUMBER_OF_LINES):
        with pytest.raises(ValueError):
            constants.MessageBoard.line(n)

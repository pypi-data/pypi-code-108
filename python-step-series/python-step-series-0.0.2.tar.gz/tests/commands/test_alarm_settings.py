#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC commands for alarm settings build properly."""


from stepseries import commands


def test_enable_uvlo_report() -> None:
    builder = commands.EnableUvloReport(4, False)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/enableUvloReport 4 0"


def test_get_uvlo() -> None:
    builder = commands.GetUvlo(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getUvlo 4"


def test_enable_thermal_status_report() -> None:
    builder = commands.EnableThermalStatusReport(2, False)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/enableThermalStatusReport 2 0"


def test_get_thermal_status() -> None:
    builder = commands.GetThermalStatus(2)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getThermalStatus 2"


def test_enable_over_current_report() -> None:
    builder = commands.EnableOverCurrentReport(1, True)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/enableOverCurrentReport 1 1"


def test_set_over_current_threshold() -> None:
    builder = commands.SetOverCurrentThreshold(2, OCD_TH=15)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.OCD_TH
    assert osc_message_str == "/setOverCurrentThreshold 2 15"


def test_get_over_current_threshold() -> None:
    builder = commands.GetOverCurrentThreshold(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getOverCurrentThreshold 3"


def test_enable_stall_report() -> None:
    builder = commands.EnableStallReport(2, True)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/enableStallReport 2 1"


def test_set_stall_threshold() -> None:
    builder = commands.SetStallThreshold(2, 12)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.STALL_TH
    assert osc_message_str == "/setStallThreshold 2 12"


def test_get_stall_threshold() -> None:
    builder = commands.GetStallThreshold(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getStallThreshold 3"


def test_set_prohibit_motion_on_home_sw() -> None:
    builder = commands.SetProhibitMotionOnHomeSw(4, False)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/setProhibitMotionOnHomeSw 4 0"


def test_get_prohibit_motion_on_home_sw() -> None:
    builder = commands.GetProhibitMotionOnHomeSw(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getProhibitMotionOnHomeSw 3"


def test_set_prohibit_motion_on_limit_sw() -> None:
    builder = commands.SetProhibitMotionOnLimitSw(2, True)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/setProhibitMotionOnLimitSw 2 1"


def test_get_prohibit_motion_on_limit_sw() -> None:
    builder = commands.GetProhibitMotionOnLimitSw(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getProhibitMotionOnLimitSw 3"

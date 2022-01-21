#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC commands for home and limit settings build properly."""


from stepseries import commands


def test_enable_home_sw_report() -> None:
    builder = commands.EnableHomeSwReport(2, True)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/enableHomeSwReport 2 1"


def test_enable_sw_event_report() -> None:
    builder = commands.EnableSwEventReport(1, False)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/enableSwEventReport 1 0"


def test_get_home_sw() -> None:
    builder = commands.GetHomeSw(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getHomeSw 3"


def test_set_home_sw_mode() -> None:
    builder = commands.SetHomeSwMode(2, True)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.SW_MODE
    assert osc_message_str == "/setHomeSwMode 2 1"


def test_get_home_sw_mode() -> None:
    builder = commands.GetHomeSwMode(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getHomeSwMode 4"


def test_set_limit_sw_mode() -> None:
    builder = commands.SetLimitSwMode(1, True)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.SW_MODE
    assert osc_message_str == "/setLimitSwMode 1 1"


def test_get_limit_sw_mode() -> None:
    builder = commands.GetLimitSwMode(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getLimitSwMode 3"

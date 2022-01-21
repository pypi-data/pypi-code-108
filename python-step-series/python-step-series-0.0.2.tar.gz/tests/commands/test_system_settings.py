#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC commands for system settings build properly."""


from stepseries import commands


def test_set_dest_ip() -> None:
    builder = commands.SetDestIP()
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 0
    assert osc_message_str == "/setDestIp"


def test_get_version() -> None:
    builder = commands.GetVersion()
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 0
    assert osc_message_str == "/getVersion"


def test_get_config_name() -> None:
    builder = commands.GetConfigName()
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 0
    assert osc_message_str == "/getConfigName"


def test_report_error() -> None:
    builder = commands.ReportError(enable=True)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert params[0] == 1
    assert len(params) == 1
    assert osc_message_str == "/reportError 1"


def test_device_reset() -> None:
    builder = commands.ResetDevice()
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 0
    assert osc_message_str == "/resetDevice"

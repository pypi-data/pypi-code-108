#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC responses from the controller build correctly."""


import pytest

from stepseries import responses


def test_booted() -> None:
    message = "/booted 0"
    osc_message1 = responses.Booted(*message.split())
    osc_message2 = responses.Booted(message)

    gospel = responses.Booted("/booted", 0)
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_error_command() -> None:
    message = "/error/command HomeSwActivating"
    osc_message1 = responses.ErrorCommand(*message.split())
    osc_message2 = responses.ErrorCommand(message)

    gospel = responses.ErrorCommand("/error/command", "HomeSwActivating")
    assert osc_message1 == gospel
    assert osc_message2 == gospel

    with pytest.raises(responses.ErrorCommand):
        raise osc_message1


def test_error_osc() -> None:
    message = "/error/osc messageNotMatch"
    osc_message1 = responses.ErrorOSC(*message.split())
    osc_message2 = responses.ErrorOSC(message)

    gospel = responses.ErrorOSC("/error/osc", "messageNotMatch")
    assert osc_message1 == gospel
    assert osc_message2 == gospel

    with pytest.raises(responses.ErrorOSC):
        raise osc_message1


def test_busy() -> None:
    message = "/busy 4 1"
    osc_message1 = responses.Busy(*message.split())
    osc_message2 = responses.Busy(message)

    gospel = responses.Busy("/busy", "4", "1")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_hiz() -> None:
    message = "/HiZ 2 1"
    osc_message1 = responses.HiZ(*message.split())
    osc_message2 = responses.HiZ(message)

    gospel = responses.HiZ("/HiZ", "2", "1")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_motor_status() -> None:
    message = "/motorStatus 3 1"
    osc_message1 = responses.MotorStatus(*message.split())
    osc_message2 = responses.MotorStatus(message)

    gospel = responses.MotorStatus("/motorStatus", "3", "1")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_homing_status() -> None:
    message = "/homingStatus 1 0"
    osc_message1 = responses.HomingStatus(*message.split())
    osc_message2 = responses.HomingStatus(message)

    gospel = responses.HomingStatus("/homingStatus", "1", "0")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_uvlo() -> None:
    message = "/uvlo 255 0"
    osc_message1 = responses.Uvlo(*message.split())
    osc_message2 = responses.Uvlo(message)

    gospel = responses.Uvlo("/uvlo", "255", "0")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_thermal_status() -> None:
    message = "/thermalStatus 3 2"
    osc_message1 = responses.ThermalStatus(*message.split())
    osc_message2 = responses.ThermalStatus(message)

    gospel = responses.ThermalStatus("/thermalStatus", "3", "2")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_over_current() -> None:
    message = "/overCurrent 1"
    osc_message1 = responses.OverCurrent(*message.split())
    osc_message2 = responses.OverCurrent(message)

    gospel = responses.OverCurrent("/overCurrent", "1")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_stall() -> None:
    message = "/stall 2"
    osc_message1 = responses.Stall(*message.split())
    osc_message2 = responses.Stall(message)

    gospel = responses.Stall("/stall", "2")
    assert osc_message1 == gospel
    assert osc_message2 == gospel

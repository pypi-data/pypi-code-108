#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC commands for speed profile settings build properly."""


from math import isclose  # Due to precision, we cannot compare floats directly

from stepseries import commands


def test_set_speed_profile() -> None:
    builder = commands.SetSpeedProfile(1, 2125.60, 4876.12, 15610)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 4
    assert isclose(params[0], builder.motorID, rel_tol=1e-05)
    assert isclose(params[1], builder.acc, rel_tol=1e-05)
    assert isclose(params[2], builder.dec, rel_tol=1e-05)
    assert isclose(params[3], builder.maxSpeed, rel_tol=1e-05)
    assert osc_message_str == "/setSpeedProfile 1 2125.6 4876.12 15610"


def test_get_speed_profile() -> None:
    builder = commands.GetSpeedProfile(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getSpeedProfile 3"


def test_set_fullstep_speed() -> None:
    builder = commands.SetFullstepSpeed(4, 16.78)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert isclose(params[1], builder.fullstepSpeed, rel_tol=1e-05)
    assert osc_message_str == "/setFullstepSpeed 4 16.78"


def test_get_fullstep_speed() -> None:
    builder = commands.GetFullstepSpeed(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getFullstepSpeed 3"


def test_set_max_speed() -> None:
    builder = commands.SetMaxSpeed(2, 31.90)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert isclose(params[1], builder.maxSpeed, rel_tol=1e-05)
    assert osc_message_str == "/setMaxSpeed 2 31.9"


def test_set_acc() -> None:
    builder = commands.SetAcc(4, 63.80)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert isclose(params[1], builder.acc, rel_tol=1e-05)
    assert osc_message_str == "/setAcc 4 63.8"


def test_set_dec() -> None:
    builder = commands.SetAcc(4, 63.80)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert isclose(params[1], builder.acc, rel_tol=1e-05)
    assert osc_message_str == "/setAcc 4 63.8"


def test_set_min_speed() -> None:
    builder = commands.SetMinSpeed(2, 482.3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert isclose(params[1], builder.minSpeed, rel_tol=1e-05)
    assert osc_message_str == "/setMinSpeed 2 482.3"


def test_get_min_speed() -> None:
    builder = commands.GetMinSpeed(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getMinSpeed 3"


def test_get_speed() -> None:
    builder = commands.GetSpeed(1)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getSpeed 1"

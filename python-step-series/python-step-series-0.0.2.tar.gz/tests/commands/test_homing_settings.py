#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC commands for homing settings build properly."""


from math import isclose  # Due to precision, we cannot compare floats directly

from stepseries import commands


def test_homing() -> None:
    builder = commands.Homing(2)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/homing 2"


def test_get_homing_status() -> None:
    builder = commands.GetHomingStatus(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getHomingStatus 4"


def test_set_homing_direction() -> None:
    builder = commands.SetHomingDirection(1, False)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.direction
    assert osc_message_str == "/setHomingDirection 1 0"


def test_get_homing_direction() -> None:
    builder = commands.GetHomingDirection(2)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getHomingDirection 2"


def test_set_homing_speed() -> None:
    builder = commands.SetHomingSpeed(4, 9250.36)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert isclose(params[1], builder.speed, rel_tol=1e-5)
    assert osc_message_str == "/setHomingSpeed 4 9250.36"


def test_get_homing_speed() -> None:
    builder = commands.GetHomingSpeed(1)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getHomingSpeed 1"


def test_go_until() -> None:
    builder = commands.GoUntil(2, True, 0.0)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 3
    assert params[0] == builder.motorID
    assert params[1] == builder.ACT
    assert isclose(params[2], builder.speed)
    assert osc_message_str == "/goUntil 2 1 0.0"


def test_set_go_until_timeout() -> None:
    builder = commands.SetGoUntilTimeout(1, 15284)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.timeOut
    assert osc_message_str == "/setGoUntilTimeout 1 15284"


def test_get_go_until_timeout() -> None:
    builder = commands.GetGoUntilTimeout(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getGoUntilTimeout 3"


def test_release_sw() -> None:
    builder = commands.ReleaseSw(3, False, True)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 3
    assert params[0] == builder.motorID
    assert params[1] == builder.ACT
    assert params[2] == builder.DIR
    assert osc_message_str == "/releaseSw 3 0 1"


def test_set_release_sw_timeout() -> None:
    builder = commands.SetReleaseSwTimeout(4, 16999)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.timeOut
    assert osc_message_str == "/setReleaseSwTimeout 4 16999"


def test_get_release_sw_timeout() -> None:
    builder = commands.GetReleaseSwTimeout(2)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getReleaseSwTimeout 2"

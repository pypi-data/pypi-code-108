#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC commands for servo mode settings build properly."""


from math import isclose  # Due to precision, we cannot compare floats directly

from stepseries import commands


def test_enable_servo_mode() -> None:
    builder = commands.EnableServoMode(3, False)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/enableServoMode 3 0"


def test_set_servo_param() -> None:
    builder = commands.SetServoParam(1, 0.2, 1.5, 0.002)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 4
    assert params[0] == builder.motorID
    assert isclose(params[1], builder.kP, rel_tol=1e-5)
    assert isclose(params[2], builder.kI, rel_tol=1e-5)
    assert isclose(params[3], builder.kD, rel_tol=1e-5)
    assert osc_message_str == "/setServoParam 1 0.2 1.5 0.002"


def test_get_servo_param() -> None:
    builder = commands.GetServoParam(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getServoParam 4"


def test_set_target_position() -> None:
    builder = commands.SetTargetPosition(3, -11111)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.position
    assert osc_message_str == "/setTargetPosition 3 -11111"


def test_set_target_position_list() -> None:
    builder = commands.SetTargetPositionList(-4321, 1234, 5678, -8765)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 4
    assert params[0] == builder.position1
    assert params[1] == builder.position2
    assert params[2] == builder.position3
    assert params[3] == builder.position4
    assert osc_message_str == "/setTargetPositionList -4321 1234 5678 -8765"

    # Test the command for 8 arguments
    builder = commands.SetTargetPositionList(
        -4321, 1234, 5678, -8765, 4321, -1234, -5678, 8765
    )
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 8
    assert params[0] == builder.position1
    assert params[1] == builder.position2
    assert params[2] == builder.position3
    assert params[3] == builder.position4
    assert params[4] == builder.position5
    assert params[5] == builder.position6
    assert params[6] == builder.position7
    assert params[7] == builder.position8
    assert (
        osc_message_str
        == "/setTargetPositionList -4321 1234 5678 -8765 4321 -1234 -5678 8765"
    )

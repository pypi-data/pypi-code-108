#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ensure OSC commands for electromagnetic brake settings build properly.
"""


from stepseries import commands


def test_enable_electromagnet_break() -> None:
    builder = commands.EnableElectromagnetBrake(4, False)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/enableElectromagnetBrake 4 0"


def test_activate() -> None:
    builder = commands.Activate(3, True)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.state
    assert osc_message_str == "/activate 3 1"


def test_free() -> None:
    builder = commands.Free(1, False)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.state
    assert osc_message_str == "/free 1 0"


def test_set_break_transition_duration() -> None:
    builder = commands.SetBrakeTransitionDuration(2, 5187)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.duration
    assert osc_message_str == "/setBrakeTransitionDuration 2 5187"


def test_get_brake_transition_duration() -> None:
    builder = commands.GetBrakeTransitionDuration(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getBrakeTransitionDuration 3"

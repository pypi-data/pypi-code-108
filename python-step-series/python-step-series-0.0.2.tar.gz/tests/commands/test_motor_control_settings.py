#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC commands for motor control settings build properly."""


from math import isclose  # Due to precision, we cannot compare floats directly

from stepseries import commands


def test_run() -> None:
    builder = commands.Run(4, 7268.61)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert isclose(params[1], builder.speed, rel_tol=1e-5)
    assert osc_message_str == "/run 4 7268.61"


def test_move() -> None:
    builder = commands.Move(1, 30000)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.step
    assert osc_message_str == "/move 1 30000"


def test_go_to() -> None:
    builder = commands.GoTo(3, 450078)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.position
    assert osc_message_str == "/goTo 3 450078"


def test_go_to_dir() -> None:
    builder = commands.GoToDir(2, True, -550123)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 3
    assert params[0] == builder.motorID
    assert params[1] == builder.DIR
    assert params[2] == builder.position
    assert osc_message_str == "/goToDir 2 1 -550123"


def test_soft_stop() -> None:
    builder = commands.SoftStop(1)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/softStop 1"


def test_hard_stop() -> None:
    builder = commands.HardStop(1)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/hardStop 1"


def test_soft_hiz() -> None:
    builder = commands.SoftHiZ(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/softHiZ 4"


def test_hard_hiz() -> None:
    builder = commands.HardHiZ(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/hardHiZ 4"

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC commands for position management settings build properly."""


from stepseries import commands


def test_set_position() -> None:
    builder = commands.SetPosition(4, 290875)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.newPosition
    assert osc_message_str == "/setPosition 4 290875"


def test_get_position() -> None:
    builder = commands.GetPosition(2)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getPosition 2"


def test_get_position_list() -> None:
    builder = commands.GetPositionList()
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 0
    assert osc_message_str == "/getPositionList"


def test_reset_pos() -> None:
    builder = commands.ResetPos(1)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/resetPos 1"


def test_set_el_pos() -> None:
    builder = commands.SetElPos(3, 2, 99)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 3
    assert params[0] == builder.motorID
    assert params[1] == builder.newFullstep
    assert params[2] == builder.newMicrostep
    assert osc_message_str == "/setElPos 3 2 99"


def test_get_el_pos() -> None:
    builder = commands.GetElPos(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getElPos 4"


def test_set_mark() -> None:
    builder = commands.SetMark(255, 5904)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.MARK
    assert osc_message_str == "/setMark 255 5904"


def test_get_mark() -> None:
    builder = commands.GetMark(2)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getMark 2"


def test_go_home() -> None:
    builder = commands.GoHome(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/goHome 4"


def test_go_mark() -> None:
    builder = commands.GoMark(255)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/goMark 255"

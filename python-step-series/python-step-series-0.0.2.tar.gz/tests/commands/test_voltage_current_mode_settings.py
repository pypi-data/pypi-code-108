#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC commands for voltage and current settings build properly."""


from stepseries import commands


def test_set_voltage_mode() -> None:
    builder = commands.SetVoltageMode(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/setVoltageMode 3"


def test_set_kval() -> None:
    builder = commands.SetKval(2, 100, 125, 150, 175)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 5
    assert params[0] == builder.motorID
    assert params[1] == builder.holdKVAL
    assert params[2] == builder.runKVAL
    assert params[3] == builder.accKVAL
    assert params[4] == builder.setDecKVAL
    assert osc_message_str == "/setKval 2 100 125 150 175"


def test_get_kval() -> None:
    builder = commands.GetKval(2)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getKval 2"


def test_set_bemf_param() -> None:
    builder = commands.SetBemfParam(2, 8192, 200, 225, 250)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 5
    assert params[0] == builder.motorID
    assert params[1] == builder.INT_SPEED
    assert params[2] == builder.ST_SLP
    assert params[3] == builder.FN_SLP_ACC
    assert params[4] == builder.FN_SLP_DEC
    assert osc_message_str == "/setBemfParam 2 8192 200 225 250"


def test_get_bemf_param() -> None:
    builder = commands.GetBemfParam(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getBemfParam 4"


def test_set_current_mode() -> None:
    builder = commands.SetCurrentMode(1)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/setCurrentMode 1"


def test_set_tval() -> None:
    builder = commands.SetTval(1, 15, 30, 45, 60)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 5
    assert params[0] == builder.motorID
    assert params[1] == builder.holdTVAL
    assert params[2] == builder.runTVAL
    assert params[3] == builder.accTVAL
    assert params[4] == builder.setDecTVAL
    assert osc_message_str == "/setTval 1 15 30 45 60"


def test_get_tval() -> None:
    builder = commands.GetTval(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getTval 4"


def test_get_tval_mA() -> None:
    builder = commands.GetTval_mA(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getTval_mA 3"


def test_set_decay_mode_param() -> None:
    builder = commands.SetDecayModeParam(4, 50, 55, 60)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 4
    assert params[0] == builder.motorID
    assert params[1] == builder.T_FAST
    assert params[2] == builder.TON_MIN
    assert params[3] == builder.TOFF_MIN
    assert osc_message_str == "/setDecayModeParam 4 50 55 60"


def test_get_decay_mode_param() -> None:
    builder = commands.GetDecayModeParam(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getDecayModeParam 4"

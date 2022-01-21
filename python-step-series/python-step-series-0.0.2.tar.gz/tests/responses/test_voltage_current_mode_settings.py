#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC responses from the controller build correctly."""


from stepseries import responses


def test_kval() -> None:
    message = "/kval 3 127 128 129 130"
    osc_message1 = responses.Kval(*message.split())
    osc_message2 = responses.Kval(message)

    gospel = responses.Kval("/kval", "3", "127", "128", "129", "130")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_bemf_param() -> None:
    message = "/bemfParam 1 5986 89 17 235"
    osc_message1 = responses.BemfParam(*message.split())
    osc_message2 = responses.BemfParam(message)

    gospel = responses.BemfParam("/bemfParam", "1", "5986", "89", "17", "235")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_tval() -> None:
    message = "/tval 4 25 26 29 30"
    osc_message1 = responses.Tval(*message.split())
    osc_message2 = responses.Tval(message)

    gospel = responses.Tval("/tval", "4", "25", "26", "29", "30")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_tval_mA() -> None:
    message = "/tval_mA 3 890 1250 1760 2120"
    osc_message1 = responses.Tval_mA(*message.split())
    osc_message2 = responses.Tval_mA(message)

    gospel = responses.Tval_mA("/tval_mA", "3", "890", "1250", "1760", "2120")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_decay_mode_param() -> None:
    message = "/decayModeParam 2 5 88 192"
    osc_message1 = responses.DecayModeParam(*message.split())
    osc_message2 = responses.DecayModeParam(message)

    gospel = responses.DecayModeParam("/decayModeParam", "2", "5", "88", "192")
    assert osc_message1 == gospel
    assert osc_message2 == gospel

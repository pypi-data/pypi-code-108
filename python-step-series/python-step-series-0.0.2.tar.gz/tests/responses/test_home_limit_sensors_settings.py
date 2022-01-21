#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC responses from the controller build correctly."""


from stepseries import responses


def test_sw_event() -> None:
    message = "/swEvent 3"
    osc_message1 = responses.SwEvent(*message.split())
    osc_message2 = responses.SwEvent(message)

    gospel = responses.SwEvent("/swEvent", "3")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_home_sw() -> None:
    message = "/homeSw 4 0 1"
    osc_message1 = responses.HomeSw(*message.split())
    osc_message2 = responses.HomeSw(message)

    gospel = responses.HomeSw("/homeSw", "4", "0", "1")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_limit_sw() -> None:
    message = "/limitSw 1 1 1"
    osc_message1 = responses.LimitSw(*message.split())
    osc_message2 = responses.LimitSw(message)

    gospel = responses.LimitSw("/limitSw", "1", "1", "1")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_home_sw_mode() -> None:
    message = "/homeSwMode 2 1"
    osc_message1 = responses.HomeSwMode(*message.split())
    osc_message2 = responses.HomeSwMode(message)

    gospel = responses.HomeSwMode("/homeSwMode", "2", "1")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_limit_sw_mode() -> None:
    message = "/limitSwMode 3 0"
    osc_message1 = responses.LimitSwMode(*message.split())
    osc_message2 = responses.LimitSwMode(message)

    gospel = responses.LimitSwMode("/limitSwMode", "3", "0")
    assert osc_message1 == gospel
    assert osc_message2 == gospel

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC responses from the controller build correctly."""


from stepseries import responses


def test_microstep_mode() -> None:
    message = "/microstepMode 3 4"
    osc_message1 = responses.MicrostepMode(*message.split())
    osc_message2 = responses.MicrostepMode(message)

    gospel = responses.MicrostepMode("/microstepMode", "3", "4")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_low_speed_optimize_threshold() -> None:
    message = "/lowSpeedOptimizeThreshold 4 1 0"
    osc_message1 = responses.LowSpeedOptimizeThreshold(*message.split())
    osc_message2 = responses.LowSpeedOptimizeThreshold(message)

    gospel = responses.LowSpeedOptimizeThreshold(
        "/lowSpeedOptimizeThreshold", "4", "1", "0"
    )
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_dir() -> None:
    message = "/dir 3 0"
    osc_message1 = responses.Dir(*message.split())
    osc_message2 = responses.Dir(message)

    gospel = responses.Dir("/dir", "3", "0")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_adc_val() -> None:
    message = "/adcVal 2 16"
    osc_message1 = responses.AdcVal(*message.split())
    osc_message2 = responses.AdcVal(message)

    gospel = responses.AdcVal("/adcVal", "2", "16")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_status() -> None:
    message = "/status 1 7896"
    osc_message1 = responses.Status(*message.split())
    osc_message2 = responses.Status(message)

    gospel = responses.Status("/status", "1", "7896")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_config_register() -> None:
    message = "/configRegister 3 1024"
    osc_message1 = responses.ConfigRegister(*message.split())
    osc_message2 = responses.ConfigRegister(message)

    gospel = responses.ConfigRegister("/configRegister", "3", "1024")
    assert osc_message1 == gospel
    assert osc_message2 == gospel

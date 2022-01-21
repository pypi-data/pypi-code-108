#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC responses from the controller build correctly."""


from stepseries import responses


def test_speed_profile() -> None:
    message = "/speedProfile 2 18069 18078 896"
    osc_message1 = responses.SpeedProfile(*message.split())
    osc_message2 = responses.SpeedProfile(message)

    gospel = responses.SpeedProfile("/speedProfile", "2", "18069", "18078", "896")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_fullstep_speed() -> None:
    message = "/fullstepSpeed 1 12222.21"
    osc_message1 = responses.FullstepSpeed(*message.split())
    osc_message2 = responses.FullstepSpeed(message)

    gospel = responses.FullstepSpeed(
        "/fullstepSpeed",
        "1",
        "12222.21",
    )
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_min_speed() -> None:
    message = "/minSpeed 3 19.12"
    osc_message1 = responses.MinSpeed(*message.split())
    osc_message2 = responses.MinSpeed(message)

    gospel = responses.MinSpeed("/minSpeed", "3", "19.12")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_speed() -> None:
    message = "/speed 4 -8152"
    osc_message1 = responses.Speed(*message.split())
    osc_message2 = responses.Speed(message)

    gospel = responses.Speed("/speed", "4", "-8152")
    assert osc_message1 == gospel
    assert osc_message2 == gospel

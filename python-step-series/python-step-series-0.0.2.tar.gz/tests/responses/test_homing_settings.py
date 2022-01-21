#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC responses from the controller build correctly."""


from stepseries import responses


def test_homing_direction() -> None:
    message = "/homingDirection 2 1"
    osc_message1 = responses.HomingDirection(*message.split())
    osc_message2 = responses.HomingDirection(message)

    gospel = responses.HomingDirection("/homingDirection", "2", "1")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_homing_speed() -> None:
    message = "/homingSpeed 2 5685.40"
    osc_message1 = responses.HomingSpeed(*message.split())
    osc_message2 = responses.HomingSpeed(message)

    gospel = responses.HomingSpeed("/homingSpeed", "2", "5685.40")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_go_until_timeout() -> None:
    message = "/goUntilTimeout 3 25874"
    osc_message1 = responses.GoUntilTimeout(*message.split())
    osc_message2 = responses.GoUntilTimeout(message)

    gospel = responses.GoUntilTimeout("/goUntilTimeout", "3", "25874")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_release_sw_timeout() -> None:
    message = "/releaseSwTimeout 4 8888"
    osc_message1 = responses.ReleaseSwTimeout(*message.split())
    osc_message2 = responses.ReleaseSwTimeout(message)

    gospel = responses.ReleaseSwTimeout("/releaseSwTimeout", "4", "8888")
    assert osc_message1 == gospel
    assert osc_message2 == gospel

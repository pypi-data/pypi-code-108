#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC responses from the controller build correctly."""


from stepseries import responses


def test_over_current_threshold() -> None:
    message = "/overCurrentThreshold 1 567.25"
    osc_message1 = responses.OverCurrentThreshold(*message.split())
    osc_message2 = responses.OverCurrentThreshold(message)

    gospel = responses.OverCurrentThreshold("/overCurrentThreshold", "1", "567.25")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_stall_threshold() -> None:
    message = "/stallThreshold 4 9822.88"
    osc_message1 = responses.StallThreshold(*message.split())
    osc_message2 = responses.StallThreshold(message)

    gospel = responses.StallThreshold("/stallThreshold", "4", "9822.88")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_prohibit_motion_on_home_sw() -> None:
    message = "/prohibitMotionOnHomeSw 2 0"
    osc_message1 = responses.ProhibitMotionOnHomeSw(*message.split())
    osc_message2 = responses.ProhibitMotionOnHomeSw(message)

    gospel = responses.ProhibitMotionOnHomeSw("/prohibitMotionOnHomeSw", "2", "0")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_prohibit_motion_on_limit_sw() -> None:
    message = "/prohibitMotionOnLimitSw 3 1"
    osc_message1 = responses.ProhibitMotionOnLimitSw(*message.split())
    osc_message2 = responses.ProhibitMotionOnLimitSw(message)

    gospel = responses.ProhibitMotionOnLimitSw("/prohibitMotionOnLimitSw", "3", "1")
    assert osc_message1 == gospel
    assert osc_message2 == gospel

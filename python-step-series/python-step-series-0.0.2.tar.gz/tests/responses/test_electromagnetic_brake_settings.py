#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC responses from the controller build correctly."""


from stepseries import responses


def test_brake_transition_duration() -> None:
    message = "/brakeTransitionDuration 4 5854"
    osc_message1 = responses.BrakeTransitionDuration(*message.split())
    osc_message2 = responses.BrakeTransitionDuration(message)

    gospel = responses.BrakeTransitionDuration("/brakeTransitionDuration", "4", "5854")
    assert osc_message1 == gospel
    assert osc_message2 == gospel

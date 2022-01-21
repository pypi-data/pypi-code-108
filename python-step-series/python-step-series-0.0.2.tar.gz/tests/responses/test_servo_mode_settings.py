#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC responses from the controller build correctly."""


from stepseries import responses


def test_servo_param() -> None:
    message = "/servoParam 2 1.54 0.03 0.98"
    osc_message1 = responses.ServoParam(*message.split())
    osc_message2 = responses.ServoParam(message)

    gospel = responses.ServoParam("/servoParam", "2", "1.54", "0.03", "0.98")
    assert osc_message1 == gospel
    assert osc_message2 == gospel

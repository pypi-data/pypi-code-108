#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC responses from the controller build correctly."""


from stepseries import responses


def test_version() -> None:
    message = "/version STEP400 1.0.2 Nov  1 2021 13:55:40"
    # We cannot unpack the message into the object
    # It does not conform to the norms of other messages
    osc_message1 = responses.Version(message)

    gospel = responses.Version("/version", "STEP400", "1.0.2", "Nov  1 2021 13:55:40")
    assert osc_message1 == gospel


def test_config_name() -> None:
    message = "/configName Default 0 0 1"
    osc_message1 = responses.ConfigName(*message.split())
    osc_message2 = responses.ConfigName(message)

    gospel = responses.ConfigName("/configName", "Default", "0", "0", "1")
    assert osc_message1 == gospel
    assert osc_message2 == gospel

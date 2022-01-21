#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Verify automatic messages parse successfully."""


import pytest

from stepseries import commands, responses
from stepseries.step400 import STEP400


@pytest.mark.skip_400_disconnected
@pytest.mark.order(-1)
def test_booted(device: STEP400, wait_for) -> None:
    # Request the device reset and then wait for the response
    wait_for(device, commands.ResetDevice(), responses.Booted)

    # Make sure to re-initialize the device
    wait_for(device, commands.SetDestIP(), responses.DestIP)

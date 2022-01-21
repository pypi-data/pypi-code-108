#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Verify electromagnetic brake-related commands execute successfully."""


import time

import pytest

from stepseries import commands, responses
from stepseries.step400 import STEP400


@pytest.mark.skip_400_disconnected
@pytest.mark.check_400_embrake
@pytest.mark.reset_400_device
class TestElectromagneticBrakeCommands:
    @pytest.mark.check_400_motors
    def test_enable_activate_free_embrake(
        self, device: STEP400, motor_id: int, wait_for
    ) -> None:
        # Enable the brake
        device.set(commands.EnableElectromagnetBrake(motor_id, True))

        # Activate the brake
        device.set(commands.Activate(motor_id, False))

        # Verify the brake is engaged, the API will raise an error
        wait_for(device, commands.Move(motor_id, 1000), responses.ErrorCommand)

        # Release the brake
        device.set(commands.Activate(motor_id, True))

        # Wait a short time to allow the brake to transition
        # (required, otherwise the get commands below will likely raise
        # a CommandError)
        time.sleep(0.2)

        # Verify the brake is disengaged, the API will not raise an
        # error
        device.set(commands.Move(motor_id, 1000))

        # Wait until the motor stops
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Disengage both the motor and the brake
        device.set(commands.Free(motor_id, True))

    def test_brake_transition_duration(self, device: STEP400, motor_id: int) -> None:
        # Set the duration
        device.set(commands.SetBrakeTransitionDuration(motor_id, 1000))

        # Verify the set command
        response: responses.BrakeTransitionDuration = device.get(
            commands.GetBrakeTransitionDuration(motor_id)
        )
        assert isinstance(response, responses.BrakeTransitionDuration)
        assert response.duration == 1000

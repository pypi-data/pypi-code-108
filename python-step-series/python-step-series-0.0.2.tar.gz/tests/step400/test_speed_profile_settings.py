#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Verify speed profile-related commands execute successfully."""


import pytest

from stepseries import commands, responses
from stepseries.step400 import STEP400


@pytest.mark.skip_400_disconnected
@pytest.mark.reset_400_device
class TestSpeedProfileMessages:
    def test_speed_profile(self, device: STEP400, motor_id: int, presets) -> None:
        # Send the set command
        device.set(
            commands.SetSpeedProfile(
                motor_id, presets.acc, presets.dec, presets.max_speed
            )
        )

        # Verify the set command
        response: responses.SpeedProfile = device.get(
            commands.GetSpeedProfile(motor_id)
        )
        assert isinstance(response, responses.SpeedProfile)
        assert abs(response.acc - presets.default_acc) > 10
        assert abs(response.dec - presets.default_dec) > 10
        assert abs(response.maxSpeed - presets.default_max_speed) > 10

    def test_fullstep_speed(self, device: STEP400, motor_id: int, presets) -> None:
        # Get the current fullstep speed
        response1: responses.FullstepSpeed = device.get(
            commands.GetFullstepSpeed(motor_id)
        )
        assert isinstance(response1, responses.FullstepSpeed)

        # Send the set command
        device.set(commands.SetFullstepSpeed(motor_id, presets.fullstep_speed))

        # Verify the set command
        response2: responses.FullstepSpeed = device.get(
            commands.GetFullstepSpeed(motor_id)
        )
        assert response2.fullstepSpeed != response1.fullstepSpeed

    def test_maxminspeed_acc_dec(
        self, device: STEP400, motor_id: int, presets, wait_for
    ) -> None:
        # Reset the device to provide a clean slate
        wait_for(device, commands.ResetDevice(), responses.Booted)
        wait_for(device, commands.SetDestIP(), responses.DestIP)

        # Send the set commands
        device.set(commands.SetMaxSpeed(motor_id, 15.25))
        device.set(commands.SetMinSpeed(motor_id, 15.25))
        device.set(commands.SetAcc(motor_id, 15.25))
        device.set(commands.SetDec(motor_id, 15.25))

        # Verify the commands
        response: responses.SpeedProfile = device.get(
            commands.GetSpeedProfile(motor_id)
        )
        assert response.acc < 16
        assert response.dec < 16
        assert response.maxSpeed < 16

        min_speed: responses.MinSpeed = device.get(commands.GetMinSpeed(motor_id))
        assert isinstance(min_speed, responses.MinSpeed)
        assert 0 < min_speed.minSpeed < 16

    def test_get_speed(self, device: STEP400, motor_id: int) -> None:
        # Ensure the min speed is 0
        device.set(commands.SetMinSpeed(motor_id, 0.0))

        response: responses.MinSpeed = device.get(commands.GetMinSpeed(motor_id))
        assert response.minSpeed == 0.0

        # Send the command and get the response
        response: responses.Speed = device.get(commands.GetSpeed(motor_id))
        assert isinstance(response, responses.Speed)
        assert response.speed == 0.0

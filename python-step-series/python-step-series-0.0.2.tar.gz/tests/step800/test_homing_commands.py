#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Verify homing-related commands execute successfully."""


import time

import pytest

from stepseries import commands, responses
from stepseries.step800 import STEP800


@pytest.mark.skip_800_disconnected
@pytest.mark.reset_800_device
class TestHomingCommands:
    def test_get_homing_status(self, device: STEP800, motor_id: int) -> None:
        # Send the command and get the resposne
        response: responses.HomingStatus = device.get(
            commands.GetHomingStatus(motor_id)
        )

        assert isinstance(response, responses.HomingStatus)
        assert response.homingStatus == 0

    def test_homing_direction(self, device: STEP800, motor_id: int, presets) -> None:
        # Set the direction
        device.set(commands.SetHomingDirection(motor_id, presets.homing_direction))

        # Verify the set command
        response: responses.HomingDirection = device.get(
            commands.GetHomingDirection(motor_id)
        )
        assert isinstance(response, responses.HomingDirection)
        assert response.homingDirection == presets.homing_direction

    def test_homing_speed(self, device: STEP800, motor_id: int, presets) -> None:
        # Set the speed
        device.set(commands.SetHomingSpeed(motor_id, presets.homing_speed))

        # Verify the set command
        response: responses.HomingSpeed = device.get(commands.GetHomingSpeed(motor_id))
        assert isinstance(response, responses.HomingSpeed)
        assert response.homingSpeed == presets.homing_speed

    def test_go_until_timeout(self, device: STEP800, motor_id: int) -> None:
        # Set the timeout
        device.set(commands.SetGoUntilTimeout(motor_id, 20000))

        # Verify the set command
        response: responses.GoUntilTimeout = device.get(
            commands.GetGoUntilTimeout(motor_id)
        )
        assert isinstance(response, responses.GoUntilTimeout)
        assert response.timeout == 20000

    def test_release_sw_timeout(self, device: STEP800, motor_id: int) -> None:
        # Set the timeout
        device.set(commands.SetReleaseSwTimeout(motor_id, 20000))

        # Verify the set command
        response: responses.ReleaseSwTimeout = device.get(
            commands.GetReleaseSwTimeout(motor_id)
        )
        assert isinstance(response, responses.ReleaseSwTimeout)
        assert response.timeout == 20000

    @pytest.mark.check_800_motors
    @pytest.mark.check_800_homesw
    def test_release_sw(self, device: STEP800, motor_id: int, presets) -> None:
        # Go until the HOME sw fires
        device.set(commands.ReleaseSw(motor_id, 1, presets.homing_direction))

        # Wait until the motor stops
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

    @pytest.mark.check_800_motors
    @pytest.mark.check_800_homesw
    def test_go_until(self, device: STEP800, motor_id: int) -> None:
        # Go until the HOME sw fires
        device.set(commands.GoUntil(motor_id, 1, 400))

        # Wait until the motor stops
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

    @pytest.mark.check_800_motors
    @pytest.mark.check_800_homesw
    def test_homing(self, device: STEP800, motor_id: int) -> None:
        # NOTE: This test may require user interaction
        # Start homing
        device.set(commands.SetHomingSpeed(motor_id, 620))
        device.set(commands.Homing(motor_id))

        # Wait for the switch to fire
        import time

        while True:
            status: responses.HomeSw = device.get(commands.GetHomeSw(motor_id))
            if status.swState:
                break
            time.sleep(0.1)

        # Wait for the switch to release
        while True:
            status: responses.HomeSw = device.get(commands.GetHomeSw(motor_id))
            if not status.swState:
                break
            time.sleep(0.1)

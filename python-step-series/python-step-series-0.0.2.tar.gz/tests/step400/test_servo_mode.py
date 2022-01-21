#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Verify servo mode-related commands execute successfully."""


import time

import pytest

from stepseries import commands, responses
from stepseries.step400 import STEP400


@pytest.mark.skip_400_disconnected
@pytest.mark.reset_400_device
@pytest.mark.incremental
class TestServoModeCommands:
    @pytest.mark.check_400_motors
    def test_servo_mode(self, device: STEP400, motor_id: int, wait_for) -> None:
        # Enable servo mode
        device.set(commands.EnableServoMode(motor_id, True))

        # Verify /run and /goTo fail
        wait_for(device, commands.Run(motor_id, 620), responses.ErrorCommand)
        wait_for(device, commands.GoTo(motor_id, 0), responses.ErrorCommand)

    def test_servo_param(self, device: STEP400, motor_id: int) -> None:
        # Send the set command
        device.set(commands.SetServoParam(motor_id, 1.0, 1.0, 1.0))

        # Verify the set commands
        response: responses.ServoParam = device.get(commands.GetServoParam(motor_id))
        assert isinstance(response, responses.ServoParam)
        assert response.kP > 0.5
        assert response.kI > 0.5
        assert response.kD > 0.5

    @pytest.mark.check_400_motors
    def test_set_target_position(
        self, device: STEP400, motor_id: int, wait_for
    ) -> None:
        # Set PID
        device.set(commands.SetServoParam(motor_id, 0.06, 0.0, 0.0))

        # Send the set commands
        try:
            raise wait_for(
                device,
                commands.SetTargetPosition(motor_id, 12000),
                responses.ErrorCommand,
                1,
            )
        except TimeoutError:
            pass

        # Wait until the motor stops
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Settle time
        time.sleep(0.5)

        # Verify the position
        response: responses.Position = device.get(commands.GetPosition(motor_id))
        assert response.ABS_POS == 12000

        try:
            raise wait_for(
                device,
                commands.SetTargetPositionList(0, 0, 0, 0, 0, 0, 0, 0),
                responses.ErrorCommand,
                1,
            )
        except TimeoutError:
            pass

        # Wait until the motor stops
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Settle time
        time.sleep(0.5)

        # Verify the position
        response: responses.Position = device.get(commands.GetPosition(motor_id))
        assert response.ABS_POS == 0

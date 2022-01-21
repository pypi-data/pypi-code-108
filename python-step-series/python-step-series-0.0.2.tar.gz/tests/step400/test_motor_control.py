#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Verify motor control-related commands execute successfully."""


import time

import pytest

from stepseries import commands, responses
from stepseries.step400 import STEP400


@pytest.mark.skip_400_disconnected
@pytest.mark.check_400_motors
@pytest.mark.reset_400_device
class TestMotorControlCommands:
    def test_run(self, device: STEP400, motor_id: int) -> None:
        # Send the run command
        device.set(commands.Run(motor_id, 300))

        # Wait until the motor reaches the required steps/second
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Stop the motor
        device.set(commands.SoftStop(motor_id))

        # Wait for the motor to stop
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

    def test_move(self, device: STEP400, motor_id: int) -> None:
        # Verify the motor is stopped
        device.set(commands.HardHiZ(motor_id))

        response: responses.HiZ = device.get(commands.GetHiZ(motor_id))
        assert response.state

        # Send the move command
        device.set(commands.Move(motor_id, 10000))

        # Wait for the motor to stop
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

    def test_go_to(self, device: STEP400, motor_id: int) -> None:
        # Send the move command
        device.set(commands.GoTo(motor_id, 0))

        # Wait for the motor to stop
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Verify we are at 0
        response: responses.Position = device.get(commands.GetPosition(motor_id))
        assert response.ABS_POS == 0

    def test_go_to_dir(self, device: STEP400, motor_id: int) -> None:
        # NOTE: This test is dependent on how the motor's coils are
        # wired. This test is not meant to take more than a few seconds,
        # so please invert the direction below if needed
        direction = 1  # 0 or 1

        # Send the move command
        device.set(commands.GoToDir(motor_id, direction, 10000))

        # Wait for the motor to stop
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Verify we are at 10000
        response: responses.Position = device.get(commands.GetPosition(motor_id))
        assert response.ABS_POS == 10000

    def test_stop(self, device: STEP400, motor_id: int) -> None:
        # Verify the motor is stopped
        device.set(commands.HardHiZ(motor_id))

        response: responses.HiZ = device.get(commands.GetHiZ(motor_id))
        assert response.state

        # Send a move command
        device.set(commands.Run(motor_id, 400))

        # Let some time pass
        time.sleep(1)

        # (Soft) Stop the motor
        device.set(commands.SoftStop(motor_id))

        # Wait for the motor to stop
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Send a move command
        device.set(commands.Run(motor_id, 200))  # slower, as not to damage anything

        # Let some time pass
        time.sleep(1)

        # (Hard) Stop the motor
        device.set(commands.HardStop(motor_id))

        # Wait for the motor to stop
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

    def test_hiz(self, device: STEP400, motor_id: int) -> None:
        # Send a move command
        device.set(commands.Run(motor_id, 400))

        # Let some time pass
        time.sleep(1)

        # (Soft) HiZ the motor
        device.set(commands.SoftHiZ(motor_id))

        # Wait for the motor to stop
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Check if the motor is in a hiz state
        response: responses.HiZ = device.get(commands.GetHiZ(motor_id))
        assert isinstance(response, responses.HiZ)
        assert response.state

        # Send a move command
        device.set(commands.Run(motor_id, 200))  # slower, as not to damage anything

        # Let some time pass
        time.sleep(1)

        # (Hard) Stop the motor
        device.set(commands.HardHiZ(motor_id))

        # Wait for the motor to stop
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Check if the motor is in a hiz state
        response: responses.HiZ = device.get(commands.GetHiZ(motor_id))
        assert response.state

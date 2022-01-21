#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Verify position management-related commands execute successfully."""


import time

import pytest

from stepseries import commands, responses
from stepseries.step400 import STEP400


@pytest.mark.skip_400_disconnected
@pytest.mark.reset_400_device
class TestPositionManagementCommands:
    def test_position(self, device: STEP400, motor_id: int) -> None:
        # Verify the motor is stopped
        response: responses.Busy = device.get(commands.GetBusy(motor_id))
        assert not response.state

        # Send the set command
        device.set(commands.SetPosition(motor_id, 125000))

        # Verify the set command
        response: responses.Position = device.get(commands.GetPosition(motor_id))
        assert isinstance(response, responses.Position)
        assert response.ABS_POS == 125000

    def test_position_list(self, device: STEP400) -> None:
        # Send the command and get the response
        response: responses.PositionList = device.get(commands.GetPositionList())
        assert isinstance(response, responses.PositionList)
        position_list = [
            response.position1,
            response.position2,
            response.position3,
            response.position4,
            response.position5,
            response.position6,
            response.position7,
            response.position8,
        ]
        assert position_list.count(125000) == 1

    def test_reset_pos(self, device: STEP400, motor_id: int) -> None:
        # Send the set command
        device.set(commands.ResetPos(motor_id))

        # Verify the set command
        response: responses.Position = device.get(commands.GetPosition(motor_id))
        assert response.ABS_POS == 0

    @pytest.mark.check_400_motors
    def test_el_pos(self, device: STEP400, motor_id: int) -> None:
        # Verify the motor is in a HiZ state
        device.set(commands.HardHiZ(motor_id))

        response: responses.HiZ = device.get(commands.GetHiZ(motor_id))
        assert response.state

        # Send the set command
        device.set(commands.SetElPos(motor_id, 3, 104))

        # Verify the set command
        response: responses.ElPos = device.get(commands.GetElPos(motor_id))
        assert isinstance(response, responses.ElPos)
        assert response.fullstep == 3
        assert response.microstep == 104

    @pytest.mark.check_400_motors
    @pytest.mark.check_400_homesw
    def test_go_home(self, device: STEP400, motor_id: int, wait_for) -> None:
        # NOTE: This test may require user interaction
        # Verify the motor is in a HiZ state
        device.set(commands.HardHiZ(motor_id))

        response: responses.HiZ = device.get(commands.GetHiZ(motor_id))
        assert response.state

        # Enable switch reporting
        device.set(commands.EnableHomeSwReport(motor_id, True))

        # Set the speed
        device.set(commands.SetHomingSpeed(motor_id, 300))

        # Set a default position to start from
        device.set(commands.SetPosition(motor_id, -1000000))

        # Send the motor home
        wait_for(device, commands.GoHome(motor_id), responses.HomeSw, 120)

    @pytest.mark.check_400_motors
    def test_go_mark(self, device: STEP400, motor_id: int) -> None:
        # Verify the motor is in a HiZ state
        device.set(commands.HardHiZ(motor_id))

        response: responses.HiZ = device.get(commands.GetHiZ(motor_id))
        assert response.state

        # Set the speed
        device.set(commands.SetHomingSpeed(motor_id, 300))

        # Set the mark
        device.set(commands.SetMark(motor_id, 0))

        # Send the motor to the mark
        device.set(commands.GoMark(motor_id))

        # Wait until the motor stops
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

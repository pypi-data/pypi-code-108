#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Verify motor alarm-related commands execute successfully."""


import pytest

from stepseries import commands, responses
from stepseries.step400 import STEP400


@pytest.mark.skip_400_disconnected
@pytest.mark.reset_400_device
class TestAlarmMessages:
    def test_uvlo(self, device: STEP400, motor_id: int) -> None:
        # NOTE: We skip testing automatic uvlo reporting
        # Send the command and get the response
        response: responses.Uvlo = device.get(commands.GetUvlo(motor_id))

        # Verify the response
        assert isinstance(response, responses.Uvlo)
        assert not response.state

    def test_thermal_status(self, device: STEP400, motor_id: int) -> None:
        # NOTE: We skip testing automatic thermal status reporting
        # Send the command and get the response
        response: responses.ThermalStatus = device.get(
            commands.GetThermalStatus(motor_id)
        )

        # Verify the response
        assert isinstance(response, responses.ThermalStatus)
        assert not response.thermalStatus  # temperature is normal

    def test_over_current(self, device: STEP400, motor_id: int) -> None:
        # NOTE: We skip testing automatic over current reporting
        # Set the threshold
        device.set(commands.SetOverCurrentThreshold(motor_id, 0))

        # Get the threshold
        response: responses.OverCurrentThreshold = device.get(
            commands.GetOverCurrentThreshold(motor_id)
        )

        # Verify the response
        assert isinstance(response, responses.OverCurrentThreshold)
        assert response.overCurrentThreshold == 312.5

        # Reset the threshold
        device.set(commands.SetOverCurrentThreshold(motor_id, 7))

    def test_stall_threshold(self, device: STEP400, motor_id: int) -> None:
        # NOTE: We skip testing automatic stall reporting
        # Set the threshold
        device.set(commands.SetStallThreshold(motor_id, 0))

        # Get the threshold
        response: responses.StallThreshold = device.get(
            commands.GetStallThreshold(motor_id)
        )

        # Verify the response
        assert isinstance(response, responses.StallThreshold)
        assert response.stallThreshold == 312.5

        # Reset the threshold
        device.set(commands.SetStallThreshold(motor_id, 127))

    def test_prohibit_motion_on_home_sw(self, device: STEP400, motor_id: int) -> None:
        # Disable motion in the direction of the switch
        device.set(commands.SetProhibitMotionOnHomeSw(motor_id, True))

        # Verify the motion is disabled
        response: responses.ProhibitMotionOnHomeSw = device.get(
            commands.GetProhibitMotionOnHomeSw(motor_id)
        )
        assert isinstance(response, responses.ProhibitMotionOnHomeSw)
        assert response.enable

        # Enable motion in the direction of the switch
        device.set(commands.SetProhibitMotionOnHomeSw(motor_id, False))

    def test_prohibit_motion_on_limit_sw(self, device: STEP400, motor_id: int) -> None:
        # Disable motion in the direction of the switch
        device.set(commands.SetProhibitMotionOnLimitSw(motor_id, True))

        # Verify the motion is disabled
        response: responses.ProhibitMotionOnLimitSw = device.get(
            commands.GetProhibitMotionOnLimitSw(motor_id)
        )
        assert isinstance(response, responses.ProhibitMotionOnLimitSw)
        assert response.enable

        # Enable motion in the direction of the switch
        device.set(commands.SetProhibitMotionOnLimitSw(motor_id, False))

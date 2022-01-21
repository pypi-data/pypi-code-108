#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Verify home/limit switch-related commands execute successfully."""


import pytest

from stepseries import commands, exceptions, responses
from stepseries.step800 import STEP800


@pytest.mark.skip_800_disconnected
@pytest.mark.reset_800_device
class TestHomeLimitSwitchCommands:
    @pytest.mark.check_800_homesw
    def test_home_sw_report(self, device: STEP800, motor_id: int, wait_for) -> None:
        # NOTE: This test may require user interaction
        try:
            # Enable switch reporting
            wait_for(
                device,
                commands.EnableHomeSwReport(motor_id, True),
                responses.HomeSw,
                120,
            )
        except TimeoutError:
            pytest.warns(
                UserWarning, "No switch input was detected for the home sw report"
            )
        finally:
            # Disable reporting
            device.set(commands.EnableHomeSwReport(motor_id, False))

    @pytest.mark.check_800_homesw
    def test_sw_event_report(self, device: STEP800, motor_id: int, wait_for) -> None:
        # NOTE: This test may require user interaction
        try:
            # Enable switch reporting
            wait_for(
                device,
                commands.EnableSwEventReport(motor_id, True),
                responses.SwEvent,
                120,
            )
        except TimeoutError:
            pytest.warns(
                UserWarning, "No switch input was detected for the sw event report"
            )
        finally:
            # Disable reporting
            device.set(commands.EnableSwEventReport(motor_id, False))

    @pytest.mark.check_800_homesw
    def test_get_home_sw(self, device: STEP800, motor_id: int) -> None:
        # Send the command and get the response
        response: responses.HomeSw = device.get(commands.GetHomeSw(motor_id))

        # Verify the response
        assert isinstance(response, responses.HomeSw)

    @pytest.mark.check_800_homesw
    def test_home_sw_mode(self, device: STEP800, motor_id: int) -> None:
        # Send the set command
        device.set(commands.SetHomeSwMode(motor_id, False))

        # Verify the set command
        response: responses.HomeSwMode = device.get(commands.GetHomeSwMode(motor_id))
        assert isinstance(response, responses.HomeSwMode)
        assert not response.swMode

    def test_limit_sw(self, device: STEP800, motor_id: int) -> None:
        # There is no limit switch port on the STEP800, so the API will
        # raise an error for the following commands
        with pytest.raises(exceptions.InvalidCommandError):
            device.set(commands.EnableLimitSwReport(motor_id, True))

        with pytest.raises(exceptions.InvalidCommandError):
            device.get(commands.GetLimitSw(motor_id))

        with pytest.raises(exceptions.InvalidCommandError):
            device.set(commands.SetLimitSwMode(motor_id, True))

        with pytest.raises(exceptions.InvalidCommandError):
            device.get(commands.GetLimitSwMode(motor_id))

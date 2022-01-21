#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Verify home/limit switch-related commands execute successfully."""


import pytest

from stepseries import commands, responses
from stepseries.step400 import STEP400


@pytest.mark.skip_400_disconnected
@pytest.mark.reset_400_device
class TestHomeLimitSwitchCommands:
    @pytest.mark.check_400_homesw
    def test_home_sw_report(self, device: STEP400, motor_id: int, wait_for) -> None:
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

    @pytest.mark.check_400_homesw
    def test_sw_event_report(self, device: STEP400, motor_id: int, wait_for) -> None:
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

    @pytest.mark.check_400_homesw
    def test_get_home_sw(self, device: STEP400, motor_id: int) -> None:
        # Send the command and get the response
        response: responses.HomeSw = device.get(commands.GetHomeSw(motor_id))

        # Verify the response
        assert isinstance(response, responses.HomeSw)

    @pytest.mark.check_400_homesw
    def test_home_sw_mode(self, device: STEP400, motor_id: int) -> None:
        # Send the set command
        device.set(commands.SetHomeSwMode(motor_id, False))

        # Verify the set command
        response: responses.HomeSwMode = device.get(commands.GetHomeSwMode(motor_id))
        assert isinstance(response, responses.HomeSwMode)
        assert not response.swMode

    @pytest.mark.check_400_limitsw
    def test_limit_sw_report(self, device: STEP400, motor_id: int, wait_for) -> None:
        # NOTE: This test may require user interaction
        try:
            # Enable switch reporting
            wait_for(
                device,
                commands.EnableLimitSwReport(motor_id, True),
                responses.LimitSw,
                120,
            )
        except TimeoutError:
            pytest.warns(
                UserWarning, "No switch input was detected for the limit sw report"
            )
        finally:
            # Disable reporting
            device.set(commands.EnableLimitSwReport(motor_id, False))

    @pytest.mark.check_400_limitsw
    def test_get_limit_sw(self, device: STEP400, motor_id: int) -> None:
        # Send the command and get the response
        response: responses.LimitSw = device.get(commands.GetLimitSw(motor_id))

        # Verify the response
        assert isinstance(response, responses.LimitSw)

    @pytest.mark.check_400_limitsw
    def test_limit_sw_mode(self, device: STEP400, motor_id: int) -> None:
        # Send the set command
        device.set(commands.SetLimitSwMode(motor_id, False))

        # Verify the set command
        response: responses.LimitSwMode = device.get(commands.GetLimitSwMode(motor_id))
        assert isinstance(response, responses.LimitSwMode)
        assert not response.swMode

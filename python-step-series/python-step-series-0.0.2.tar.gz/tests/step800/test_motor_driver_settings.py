#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Verify motor driver-related commands execute successfully."""


import time

import pytest

from stepseries import commands, exceptions, responses
from stepseries.step800 import STEP800


@pytest.mark.skip_800_disconnected
@pytest.mark.reset_800_device
class TestMotorDriverMessages:
    @pytest.mark.skip_800_not_configured
    def test_microstep_mode(self, device: STEP800, motor_id: int, presets) -> None:
        # Ensure the motor is in a high-z state
        if not device.get(commands.GetHiZ(motor_id)).state:
            device.set(commands.HardHiZ(motor_id))

        if not device.get(commands.GetHiZ(motor_id)).state:
            pytest.skip("cannot set motor into a HiZ state")

        # Set the microstep mode at the preset defined
        device.set(commands.SetMicrostepMode(motor_id, presets.microstep_mode))

        # Verify the motor's microstepping mode
        response: responses.MicrostepMode = device.get(
            commands.GetMicrostepMode(motor_id)
        )
        assert isinstance(response, responses.MicrostepMode)
        assert response.STEP_SEL == presets.microstep_mode

    @pytest.mark.skip_800_not_configured
    def test_low_speed_optimize_threshold(
        self, device: STEP800, motor_id: int, presets
    ) -> None:
        # Set the low speed optimize threshold at the preset defined
        device.set(
            commands.SetLowSpeedOptimizeThreshold(
                motor_id, presets.low_speed_optimize_threshold
            )
        )

        # Verify the motor's low speed optimize threshold
        response: responses.LowSpeedOptimizeThreshold = device.get(
            commands.GetLowSpeedOptimizeThreshold(motor_id)
        )
        assert isinstance(response, responses.LowSpeedOptimizeThreshold)
        assert (
            response.lowSpeedOptimizeThreshold == presets.low_speed_optimize_threshold
        )

    def test_get_busy(self, device: STEP800, motor_id: int) -> None:
        # Send the command and get the response
        response: responses.Busy = device.get(commands.GetBusy(motor_id))

        # Verify the busy response
        assert isinstance(response, responses.Busy)
        assert response.motorID == motor_id
        assert not response.state

    @pytest.mark.check_800_motors
    def test_enable_busy_report(self, device: STEP800, motor_id: int, wait_for) -> None:
        # Enable the reporting
        device.set(commands.EnableBusyReport(motor_id, True))

        # Verify the motor is not busy
        response: responses.Busy = device.get(commands.GetBusy(motor_id))
        assert not response.state

        # Put the motor into a busy state and ensure the report is sent
        response: responses.Busy = wait_for(
            device, commands.Move(motor_id, 10000), responses.Busy
        )
        assert response.motorID == motor_id
        assert response.state

        # Wait until the motor stops
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Disable the reporting
        device.set(commands.EnableBusyReport(motor_id, False))

    def test_get_hiz(self, device: STEP800, motor_id: int) -> None:
        # Put the motor into a HiZ state
        device.set(commands.HardHiZ(motor_id))

        # Send the command and get the response
        response: responses.HiZ = device.get(commands.GetHiZ(motor_id))

        # Verify the HiZ response
        assert isinstance(response, responses.HiZ)
        assert response.motorID == motor_id
        assert response.state

    @pytest.mark.check_800_motors
    def test_enable_hiz_report(self, device: STEP800, motor_id: int, wait_for) -> None:
        # Enable the reporting
        device.set(commands.EnableHiZReport(motor_id, True))

        # Put the motor into a HiZ state
        device.set(commands.HardHiZ(motor_id))

        # Verify the motor is in a HiZ state
        response: responses.HiZ = device.get(commands.GetHiZ(motor_id))
        assert response.state

        # Put the motor into a LoZ state and ensure the report is sent
        response: responses.HiZ = wait_for(
            device, commands.Move(motor_id, 10000), responses.HiZ
        )
        assert response.motorID == motor_id
        assert not response.state

        # Wait until the motor stops
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Disable the reporting
        device.set(commands.EnableHiZReport(motor_id, False))

    def test_get_dir(self, device: STEP800, motor_id: int) -> None:
        # Send the command and get the response
        response: responses.Dir = device.get(commands.GetDir(motor_id))

        # Verify the Dir response
        assert isinstance(response, responses.Dir)
        assert response.motorID == motor_id

    @pytest.mark.check_800_motors
    def test_enable_dir_report(self, device: STEP800, motor_id: int, wait_for) -> None:
        # Enable the reporting
        device.set(commands.EnableDirReport(motor_id, True))

        # Test 1
        try:
            response1: responses.Dir = wait_for(
                device, commands.Move(motor_id, -10000), responses.Dir, 1
            )
        except TimeoutError:
            response1: responses.Dir = wait_for(
                device, commands.Move(motor_id, 10000), responses.Dir, 1
            )

        # Wait until the motor stops
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Test 2
        try:
            response2: responses.Dir = wait_for(
                device, commands.Move(motor_id, -10000), responses.Dir, 1
            )
        except TimeoutError:
            response2: responses.Dir = wait_for(
                device, commands.Move(motor_id, 10000), responses.Dir, 1
            )

        # Wait until the motor stops
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Verify the motor switched directions
        assert response1.direction != response2.direction

        # Disable the reporting
        device.set(commands.EnableDirReport(motor_id, False))

    def test_get_motor_status(self, device: STEP800, motor_id: int) -> None:
        # Send the command and get the response
        response: responses.MotorStatus = device.get(commands.GetMotorStatus(motor_id))

        # Verify the MotorStatus response
        assert isinstance(response, responses.MotorStatus)
        assert response.motorID == motor_id
        assert not response.MOT_STATUS  # Motor stopped

    @pytest.mark.check_800_motors
    def test_enable_status_report(
        self, device: STEP800, motor_id: int, wait_for
    ) -> None:
        # Enable the reporting
        device.set(commands.EnableMotorStatusReport(motor_id, True))

        # Verify the motor is stopped
        response: responses.MotorStatus = device.get(commands.GetMotorStatus(motor_id))
        if response.MOT_STATUS:
            # Enable busy status report
            device.set(commands.EnableBusyReport(motor_id, True))

            # Stop the motor
            try:
                response: responses.Busy = wait_for(
                    device, commands.SoftStop(motor_id), responses.Busy
                )
                assert not response.state
            finally:
                # Disable busy reporting
                device.set(commands.EnableBusyReport(motor_id, False))

        # Run the motor and ensure the acc status is sent
        response: responses.MotorStatus = wait_for(
            device, commands.Move(motor_id, 10000), responses.MotorStatus
        )
        assert response.motorID == motor_id
        assert response.MOT_STATUS == 1

        # Wait until the motor stops
        while True:
            response: responses.Busy = device.get(commands.GetBusy(motor_id))
            if not response.state:
                break
            time.sleep(0.1)

        # Disable the reporting
        device.set(commands.EnableMotorStatusReport(motor_id, False))

    def test_set_position_report_interval(
        self, device: STEP800, motor_id: int, wait_for
    ) -> None:
        # Enable periodic position reporting
        device.set(commands.SetPositionReportInterval(motor_id, 1000))

        # Wait for a report to arrive
        response: responses.Position = wait_for(
            device, commands.SetDestIP(), responses.Position
        )

        # Verify the response
        assert isinstance(response, responses.Position)

        # Disable the reporting
        device.set(commands.SetPositionReportInterval(motor_id, 0))

    def test_set_position_list_report_interval(self, device: STEP800, wait_for) -> None:
        # Enable periodic position list reporting
        device.set(commands.SetPositionListReportInterval(1000))

        # Wait for a report to arrive
        response: responses.PositionList = wait_for(
            device, commands.SetDestIP(), responses.PositionList
        )

        # Verify the response
        assert isinstance(response, responses.PositionList)

        # Disable the reporting
        device.set(commands.SetPositionListReportInterval(0))

    def test_get_adc_val(self, device: STEP800, motor_id: int) -> None:
        # This command cannot run on a STEP800, so the library raises
        # an error
        with pytest.raises(exceptions.InvalidCommandError):
            device.get(commands.GetAdcVal(motor_id))

    def test_get_status(self, device: STEP800, motor_id: int) -> None:
        # Send the command and get the response
        response: responses.Status = device.get(commands.GetStatus(motor_id))

        # Verify the response
        assert isinstance(response, responses.Status)

    def test_get_config_register(self, device: STEP800, motor_id: int) -> None:
        # Send the command and get the response
        response: responses.ConfigRegister = device.get(
            commands.GetConfigRegister(motor_id)
        )

        # Verify the response
        assert isinstance(response, responses.ConfigRegister)

    def test_reset_motor_driver(self, device: STEP800, motor_id: int, wait_for) -> None:
        # NOTE: Command is likely deprecated
        # Send the command
        device.set(commands.ResetMotorDriver(motor_id))

        # Allow the process to finish
        time.sleep(1)

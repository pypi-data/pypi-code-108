#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Verify system-related commands execute successfully."""


import pytest

from stepseries import commands, responses
from stepseries.step400 import STEP400


@pytest.mark.skip_400_disconnected
class TestSystemMessages:
    def test_set_dest_ip(self, device: STEP400, wait_for) -> None:
        # A utility function to easily get the IP address of the local
        # machine
        def my_ip() -> str:
            import socket

            try:
                # Connect to DT34 and query the connection for the local IP address
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.connect(("10.1.1.34", 80))
                return sock.getsockname()[0]
            finally:
                sock.close()

        # Send the command and wait for the device's response
        response: responses.DestIP = wait_for(
            device, commands.SetDestIP(), responses.DestIP
        )

        # Verify the IP address of the device matches the preset IP
        assert isinstance(response, responses.DestIP)
        assert (
            f"{response.destIp0}.{response.destIp1}.{response.destIp2}.{response.destIp3}"
            == my_ip()
        )

    def test_get_version(self, device: STEP400) -> None:
        # Send the command and wait for the device's response
        response: responses.Version = device.get(commands.GetVersion())

        # Verify the response was parsed correctly
        assert isinstance(response, responses.Version)
        assert response.compile_date
        assert response.firmware_name
        assert response.firmware_version

    @pytest.mark.skip_400_not_configured
    def test_get_config_name(self, device: STEP400, presets) -> None:
        # Send the command and wait for the device's response
        response: responses.ConfigName = device.get(commands.GetConfigName())

        # Verify the response was parsed correctly
        assert isinstance(response, responses.ConfigName)
        assert response.configFileOpenSucceeded == presets.using_config_file
        assert response.configFileParseSucceeded == presets.using_config_file
        assert response.sdInitializeSucceeded == presets.using_config_file

    def test_report_error(self, device: STEP400) -> None:
        # Enable error reporting from the device
        device.set(commands.ReportError(True))

        # Request data about a motor that doesn't exist on the board
        # The device will raise a "MotorIdNotMatch" error which the
        # API raises
        with pytest.raises(responses.ErrorCommand):
            device.get(commands.GetStatus(200))

        # Create a dummy command
        from dataclasses import dataclass

        @dataclass
        class GetDummy(commands.OSCGetCommand):
            address: str = "/getDummy"
            response_cls = responses.Version

        # Send the command
        # There exists no such command as this, so the device should
        # return a "messageNotMatch" error, which the API raises
        with pytest.raises(responses.ErrorOSC):
            device.get(GetDummy())

        # Disable error reporting from the device
        device.set(commands.ReportError(False))

        # Now run the above tests again to ensure they do not report
        # this time
        with pytest.raises(TimeoutError):
            device.get(commands.GetStatus(200))

        with pytest.raises(TimeoutError):
            device.get(GetDummy())

        # Re-enable error reporting
        device.set(commands.ReportError(True))

    @pytest.mark.order(-1)
    def test_reset_device(self, device: STEP400, wait_for) -> None:
        # Send the command and wait for the response
        wait_for(device, commands.ResetDevice(), responses.Booted)

        # Reinitialize the device
        wait_for(device, commands.SetDestIP(), responses.DestIP)

        # Test the reset using the shortcut
        from threading import Event

        device_booted = Event()

        def reset_callback(_) -> None:
            device_booted.set()

        device.on(responses.Booted, reset_callback)
        device.reset()

        try:
            device_booted.wait(10)

            # Reinitialize the device
            wait_for(device, commands.SetDestIP(), responses.DestIP)
        finally:
            device.remove(reset_callback)

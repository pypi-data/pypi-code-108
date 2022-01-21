#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""4 axis stepper motor driver with Ethernet interface."""


from typing import List, Union

from . import commands
from .commands import OSCGetCommand, OSCSetCommand
from .exceptions import InvalidCommandError
from .responses import OSCResponse
from .stepXXX import STEPXXX


class STEP800(STEPXXX):
    """Send and receive data from a STEP800 motor driver.

    Note:
        It is recommended to create a default message handler for this
        driver. Here is an example:

            >>> from stepseries.step800 import STEP800
            >>>
            >>> def default_handler(message) -> None:
            ...     print(message)
            ...
            >>> driver = STEP800(0, '10.1.21.56')  # Your IP and dip ID here
            >>> driver.on(None, default_handler)

    Args:
        id (`int`):
            The id set by the DIP switches on the device.
        address (`str`):
            The ip address of the device. Defaults to `10.0.0.100`.
        port (`int`):
            The local port the device is listening on. Defaults to
            `50000`.
        server_address (`str`):
            The ip address of the server (this machine). Should always
            be `0.0.0.0`. Defaults to `0.0.0.0`.
        server_port (`int`):
            The port the server is listening on. Defaults to `50100`.
        add_id_to_args (`bool`):
            Whether to add `id` to `address` and `server_port`
            (the default behavior on the device). Defaults to `True`.
    """

    _invalid_commands: List[Union[OSCGetCommand, OSCSetCommand]]

    def __init__(
        self,
        id: int,
        address: str = "10.0.0.100",
        port: int = 50000,
        server_address: str = "0.0.0.0",
        server_port: int = 50100,
        add_id_to_args: bool = True,
    ) -> None:
        super().__init__(
            id,
            address=address,
            port=port,
            server_address=server_address,
            server_port=server_port,
            add_id_to_args=add_id_to_args,
        )

        self._invalid_commands = [
            commands.SetVoltageMode,
            commands.SetCurrentMode,
            commands.SetTval,
            commands.GetTval,
            commands.GetTval_mA,
            commands.SetDecayModeParam,
            commands.GetDecayModeParam,
            commands.EnableLimitSwReport,
            commands.GetLimitSw,
            commands.SetLimitSwMode,
            commands.GetLimitSwMode,
            commands.GetAdcVal,
            commands.GetProhibitMotionOnLimitSw,
            commands.SetProhibitMotionOnLimitSw,
        ]

    def get(
        self, command: OSCGetCommand, with_callback: bool = True, wait: bool = True
    ) -> Union[OSCResponse, List[OSCResponse]]:
        """Send a 'get' command to the device and return the response.

        Note:
            The responses are also sent to each applicable callback.

            If a `ParseError` is received, then it will be raised. The
            raw response can be retrieved via the `response` attribute
            of the error.

        Args:
            command (`OSCGetCommand`):
                The completed command template (`stepseries.commands`).
            with_callback (`bool`):
                Send the response to callbacks as well
                (defaults to `True`).
            wait (`bool`):
                Wait for a response from the device if `True`, otherwise
                return without waiting for a response (defaults to
                `True`).

        Raises:
            `TypeError`:
                `command` is not an `OSCSetCommand`.
            `InvalidCommandError`:
                `command` cannot run on a STEP800.
        """

        if not isinstance(command, OSCGetCommand):
            raise TypeError(
                "argument 'command' expected to be 'OSCGetCommand', "
                f"'{type(command).__name__}' found"
            )

        if command.__class__ in self._invalid_commands:
            raise InvalidCommandError(
                f"command '{command.__class__.__name__}' cannot run on a STEP800"
                "\n\n\tSTEP400-only commands:\n"
                + "\n".join(["\t  - " + c.__name__ for c in self._invalid_commands])
                + "\n\nFor more information, see: https://ponoor.com/en/docs/step-series/osc-command-reference/differences-between-step400-and-step800/"  # noqa
            )

        return super().get(command, with_callback, wait)

    def set(self, command: OSCSetCommand) -> None:
        """Send a 'set' command to the device.

        Args:
            command (`OSCCommand`):
                The completed command template (`stepseries.commands`).

        Raises:
            `TypeError`:
                `command` is not an `OSCSetCommand`.
        """

        if not isinstance(command, OSCSetCommand):
            raise TypeError(
                "argument 'command' expected to be 'OSCSetCommand', "
                f"'{type(command).__name__}' found"
            )

        if command.__class__ in self._invalid_commands:
            raise InvalidCommandError(
                f"command '{command.__class__.__name__}' cannot run on a STEP800"
                "\n\n\tSTEP400-only commands:\n"
                + "\n".join(["\t  - " + c.__name__ for c in self._invalid_commands])
                + "\n\nFor more information, see: https://ponoor.com/en/docs/step-series/osc-command-reference/differences-between-step400-and-step800/"  # noqa
            )

        return super().set(command)

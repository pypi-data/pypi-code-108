#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""4 axis stepper motor driver with and Ethernet interface."""


from .stepXXX import STEPXXX


class STEP400(STEPXXX):
    """Send and receive data from a STEP400 motor driver.

    Note:
        It is recommended to create a default message handler for this
        driver. Here is an example:

            >>> from stepseries.step400 import STEP400
            >>>
            >>> def default_handler(message) -> None:
            ...     print(message)
            ...
            >>> driver = STEP400(0, '10.1.21.56')  # Your IP and dip ID here
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

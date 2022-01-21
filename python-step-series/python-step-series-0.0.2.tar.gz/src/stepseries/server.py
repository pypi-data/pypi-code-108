#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Manages IO with multiple STEP-series devices."""


import atexit
from threading import Thread
from typing import Any, List, Tuple

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from stepseries.commands import OSCCommand
from stepseries.exceptions import ClientNotFoundError

# Work around for this circular import; allows annotations while
# writing code and doesn't break when running it.
try:
    from .stepXXX import STEPXXX
except ImportError:
    STEPXXX = Any


class Manager:

    _bound_devices: List[Tuple[STEPXXX, SimpleUDPClient, ThreadingOSCUDPServer, Thread]]

    def __init__(self) -> None:
        self._bound_devices = list()

        # Shutdown hook to ensure servers are properly closed
        atexit.register(self.shutdown)

    def _handle_incoming_message(
        self,
        client_address: Tuple[str, int],
        message_address: str,
        *osc_args: Tuple[Any]
    ) -> None:
        # Find the device bound to this address
        address, _ = client_address
        for (device, _, _, _) in self._bound_devices:
            if device.address == address:
                device._handle_incoming_message(message_address, *osc_args)

    def add_device(self, device: STEPXXX) -> None:
        """
        For internal use only. Add a device to send data to when it is
        received.
        """
        # Check if the device wants to bind to a pre-existing server
        # Bind the device to that server if needed
        client = SimpleUDPClient(device.address, device.port)
        for (_, _, server, _) in self._bound_devices:
            if (device.server_address, device.server_port) == server.server_address:
                self._bound_devices.append((device, client, server, None))
                return

        # Create a new server and bind the device to it
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self._handle_incoming_message, True)
        server = ThreadingOSCUDPServer(
            (device.server_address, device.server_port), dispatcher
        )
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()

        # Only add the thread to this list to keep a reference to it
        self._bound_devices.append((device, client, server, thread))

    def remove_device(self, device: STEPXXX) -> None:
        """
        For internal use only. Remove a tracked device to stop sending
        data to it.
        """
        for i, (d, _, s, _) in enumerate(self._bound_devices):
            if d == device:
                self._bound_devices.pop(i)
                s.shutdown()
                d._is_closed = True
                break

    def shutdown(self) -> None:
        """Shuts down all tracked servers."""

        for _, _, s, _ in self._bound_devices:
            s.shutdown()
        self._bound_devices = list()

    def send(self, device: STEPXXX, message: OSCCommand) -> None:
        """Send `message` to the `device`."""

        # Get the client bound to this device
        client = None
        for d, c, _, _ in self._bound_devices:
            if d == device:
                client = c
                break
        else:
            raise ClientNotFoundError("device is not registered with a server")

        client.send(message.build())


DEFAULT_SERVER = Manager()

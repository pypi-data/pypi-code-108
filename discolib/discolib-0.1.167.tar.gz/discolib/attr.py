#
# DISCo Python interface library
# Copyright (c) 2021 Greg Van Aken
#
"""attr.py: Attribute classes for objects representing attributes discovered on component(s)."""

import struct
from discolib.io import DiscoIO
from discolib.protocol import Cmd, CommandPacket
from serialclass import SerialClass

class DiscoAttribute(SerialClass):
    """A single port attribute on the component(s)."""

    def __init__(self, port: int, type: str, name: str, io_handler: DiscoIO) -> None:
        self.port = port
        self.type = type
        self.name = name
        self._setpoint = None
        self._readback = None
        self._io = io_handler

    def __str__(self) -> str:
        """Get a json-style representation of the attribute."""
        return str(self.serialize(ignore_protected=True))

    def __repr__(self) -> str:
        """Get a json-style representation of the attribute."""
        return self.__str__()

    @property
    def setpoint(self):
        """Get/set the setpoint of the attribute."""
        return self._setpoint

    @property
    def readback(self):
        """Get the readback of the attribute."""
        return self._readback

    @setpoint.setter
    def setpoint(self, value):
        """Issue a write to set the setpoint of the attribute."""
        self._setpoint = value
        data = bytes(CommandPacket(Cmd.SET_PORT_SETPOINT, port=self.port, payload=struct.pack(self.type, self._setpoint)))
        self._io.write(data)

    @setpoint.getter
    def setpoint(self):
        """Issue a read to get the setpoint of the attribute."""
        data = bytes(CommandPacket(Cmd.GET_PORT_SETPOINT, port=self.port))
        self._io.write(data)
        resp = self._io.read()
        self._setpoint, = struct.unpack(self.type, resp)
        return self._setpoint

    @readback.getter
    def readback(self):
        """Issue a read to get the readback of the attribute."""
        data = bytes(CommandPacket(Cmd.GET_PORT_READBACK, port=self.port))
        self._io.write(data)
        resp = self._io.read()       
        self._readback, = struct.unpack(self.type, resp)
        return self._readback

#
# DISCo Python interface library
# Copyright (c) 2021 Greg Van Aken
#
"""core.py: Main library interface, includes top-level Disco class representing component(s) space(s)."""
from discolib.attr import DiscoAttribute
from discolib.io import DiscoIO
from discolib.protocol import CommandPacket, Cmd

from typing import List
import json

class Disco:
    """Houses all attributes and interaction functions."""
    def _cmd_to_port(self, cmd_packet: CommandPacket) -> bytes:
        """Send a byte command (without data) to a port."""
        data = bytes(cmd_packet)
        self._io.write(data)
        resp = self._io.read()
        return resp

    def _get_ports(self) -> List:
        """Retrieve all ports and the attributes they represent."""
        data = bytes(CommandPacket(Cmd.GET_PORTS))
        self._io.write(data)
        resp = self._io.read()
        ports = list(resp)
        for port in ports:
            port_dict = {}
            port_dict['port'] = port
            resp = self._cmd_to_port(CommandPacket(Cmd.GET_PORT_NAME, port=port))
            port_dict['name'] = resp.decode().strip('\x00')
            resp = self._cmd_to_port(CommandPacket(Cmd.GET_PORT_TYPE, port=port))
            port_dict['type'] = resp.decode()
            self._attrs.append(port_dict)
        return self._attrs

    def __init__(self, io_handler: DiscoIO) -> None:
        """Initialize all attributes and construct their accessors."""
        self._io = io_handler
        self._attrs = []
        self._attr_dicts = []
        for port in self._get_ports():
            attr = DiscoAttribute(port['port'], port['type'], port['name'], self._io)
            setattr(self, attr.name, attr)
            self._attr_dicts.append(attr.serialize(ignore_protected=True))

    def get_attrs(self) -> List:
        """Retrieve a list of all attribute objects."""
        return self._attrs

    def get_attr_dicts(self) -> List:
        """Retrieve a list of dictionary representations of each attribute."""
        return self._attr_dicts

    def get_attr_json(self, indent=None) -> str:
        """Retrieve a json string representation of all attributes."""
        return json.dumps(self._attr_dicts, indent=indent)


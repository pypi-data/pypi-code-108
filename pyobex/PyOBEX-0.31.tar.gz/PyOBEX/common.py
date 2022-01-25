"""
common.py - Classes providing common facilities for other modules.

Copyright (C) 2007 David Boddie <david@boddie.org.uk>

This file is part of the PyOBEX Python package.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import socket
import struct
import sys

from PyOBEX import headers

if hasattr(socket, "AF_BLUETOOTH"):

    class Socket(socket.socket):
        def __init__(self):
            super().__init__(socket.AF_BLUETOOTH, socket.SOCK_STREAM,
                             socket.BTPROTO_RFCOMM)
else:
    from bluetooth import BluetoothSocket

    class Socket(BluetoothSocket):
        def __init__(self):
            super().__init__()
            self.has_native_sendall = hasattr(super(), "sendall") and callable(
                getattr(super(), "sendall"))

        def sendall(self, data):
            if self.has_native_sendall:
                super().sendall(data)
            else:
                while data:
                    sent = self.send(data)
                    if sent > 0:
                        data = data[sent:]
                    elif sent < 0:
                        raise socket.error


class ObexVersion:

    major = 1
    minor = 0

    def to_byte(self):
        return (self.major & 0x0f) << 4 | (self.minor & 0xf)

    def from_byte(self, byte):
        self.major = (byte >> 4) & 0x0f
        self.minor = byte & 0x0f
        return self

    def __gt__(self, other):
        return (self.major, self.minor) > (other.major, other.minor)


class Message:

    code = 0
    format = ">BH"

    def __init__(self, data=(), header_data=()):

        self.data = data
        self.header_data = list(header_data)
        self.minimum_length = self.length(Message.format)
        self.obex_version = None
        self.flags = None
        self.max_packet_length = None

    @staticmethod
    def length(format_):

        return format_.count("B") + format_.count("H") * 2

    def read_data(self, data):

        # Extract the header data from the complete data.
        header_data = data[self.minimum_length:]
        self.read_headers(header_data)

    def read_headers(self, header_data):

        i = 0
        header_list = []
        data = None
        while i < len(header_data):

            # Read header ID and data type.
            header_id = struct.unpack(">B", header_data[i:i+1])[0]
            id_type = header_id & 0xc0
            if id_type == 0x00:
                # text
                length = struct.unpack(">H", header_data[i+1:i+3])[0] - 3
                data = header_data[i+3:i+3+length]
                i += 3 + length
            elif id_type == 0x40:
                # bytes
                length = struct.unpack(">H", header_data[i+1:i+3])[0] - 3
                data = header_data[i+3:i+3+length]
                i += 3 + length
            elif id_type == 0x80:
                # 1 byte
                data = header_data[i+1]
                i += 2
            elif id_type == 0xc0:
                # 4 bytes
                data = header_data[i+1:i+5]
                i += 5

            header_class = headers.header_dict.get(header_id, headers.Header)
            header_list.append(header_class(data, encoded=True))

        self.header_data = header_list

    def add_header(self, header, max_length):

        if self.minimum_length + len(header.data) > max_length:
            return False

        self.header_data.append(header)
        return True

    def reset_headers(self):
        self.header_data = []

    def encode(self):

        length = self.minimum_length + sum(map(lambda h: len(h.data),
                                               self.header_data))
        args = (Message.format + self.format, self.code, length) + self.data
        return struct.pack(*args) + b"".join(map(lambda h: h.data,
                                                 self.header_data))


class MessageHandler:

    format = ">BH"

    message_dict = {}

    if sys.platform in ["darwin", "win32"]:

        def _read_packet(self, socket_):

            data = b""
            while len(data) < 3:
                data += socket_.recv(3 - len(data))
            type_, length = struct.unpack(self.format, data)
            while len(data) < length:
                data += socket_.recv(length - len(data))
            return type_, length, data
    else:

        def _read_packet(self, socket_):

            data = socket_.recv(3, socket.MSG_WAITALL)
            type_, length = struct.unpack(self.format, data)
            if length > 3:
                data += socket_.recv(length - 3, socket.MSG_WAITALL)
            return type_, length, data

    def decode(self, socket_):

        code, length, data = self._read_packet(socket_)

        if code in self.message_dict:
            message = self.message_dict[code]()
            message.read_data(data)
            return message

        return UnknownResponse(code, length, data)


class Response(Message):

    # Define the additional format information required by responses.
    # Subclasses should redefine this when required to ensure that their
    # minimum lengths are calculated correctly.
    format = ""

    def __init__(self, data=(), header_data=()):

        Message.__init__(self, data, header_data)
        self.minimum_length = self.length(Message.format + self.format)


class UnknownResponse(Response):
    def __init__(self, code, length, data):
        super().__init__(data)
        self.code = code
        self.length = length
        self.data = data[3:]


# aliases for renamed classes
# the old names are deprecated and should not be used anymore
# they are scheduled for removal in the future
# pylint: disable=invalid-name
OBEX_Version = ObexVersion
# pylint: enable=invalid-name

"""
requests.py - Classes encapsulating OBEX requests.

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

import struct
from PyOBEX.common import ObexVersion, Message, MessageHandler


class Request(Message):

    # Define the additional format information required by requests.
    # Subclasses should redefine this when required to ensure that their
    # minimum lengths are calculated correctly.
    format = ""

    def __init__(self, data=(), header_data=()):

        Message.__init__(self, data, header_data)
        self.minimum_length = self.length(Message.format + self.format)

    def is_final(self):

        return (self.code & 0x80) == 0x80


class Connect(Request):

    code = OBEX_Connect = 0x80
    format = "BBH"

    def read_data(self, data):

        # Extract the connection data from the complete data.
        extra_data = data[self.length(Message.format):self.minimum_length]

        obex_version, flags, max_packet_length = struct.unpack(
            ">"+self.format, extra_data)

        self.obex_version = ObexVersion().from_byte(obex_version)
        self.flags = flags
        self.max_packet_length = max_packet_length

        Request.read_data(self, data)


class Disconnect(Request):

    code = OBEX_Disconnect = 0x81
    format = ""


class Put(Request):

    code = OBEX_Put = 0x02
    format = ""


class PutFinal(Put):

    code = OBEX_Put_Final = 0x82
    format = ""


class Get(Request):

    code = OBEX_Get = 0x03
    format = ""


class GetFinal(Get):

    code = OBEX_Get_Final = 0x83
    format = ""


class SetPath(Request):

    code = OBEX_Set_Path = 0x85
    format = "BB"
    NavigateToParent = 1
    DontCreateDir = 2

    def __init__(self, data=(), header_data=()):
        super().__init__(data, header_data)
        self.flags = None
        self.constants = None

    def read_data(self, data):

        # Extract the extra message data from the complete data.
        extra_data = data[self.length(Message.format):self.minimum_length]

        flags, constants = struct.unpack(">"+self.format, extra_data)

        self.flags = flags
        self.constants = constants

        Request.read_data(self, data)


class Abort(Request):

    code = OBEX_Abort = 0xff
    format = ""


class UnknownRequest(Request):

    pass


class RequestHandler(MessageHandler):

    OBEX_User_First = 0x10
    OBEX_User_Last = 0x1f

    message_dict = {
        Connect.code: Connect,
        Disconnect.code: Disconnect,
        Put.code: Put,
        PutFinal.code: PutFinal,
        Get.code: Get,
        GetFinal.code: GetFinal,
        SetPath.code: SetPath,
        Abort.code: Abort
        }

    UnknownMessageClass = UnknownRequest


# aliases for renamed classes
# the old names are deprecated and should not be used anymore
# they are scheduled for removal in the future
# pylint: disable=invalid-name
Get_Final = GetFinal
Put_Final = PutFinal
Set_Path = SetPath
# pylint: enable=invalid-name

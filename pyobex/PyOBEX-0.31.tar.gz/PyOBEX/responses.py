"""
responses.py - Classes encapsulating OBEX responses.

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
from PyOBEX.common import (MessageHandler, ObexVersion, Response,
                           UnknownResponse)


class FailureResponse(Response):

    pass


class Continue(Response):
    code = OBEX_Continue = 0x90


class Success(Response):
    code = OBEX_OK = OBEX_Success = 0xA0


class ConnectSuccess(Response):
    code = OBEX_OK = OBEX_Success = 0xA0
    format = "BBH"


class BadRequest(FailureResponse):
    code = OBEX_Bad_Request = 0xC0


class Unauthorized(FailureResponse):
    code = OBEX_Unauthorized = 0xC1


class Forbidden(FailureResponse):
    code = OBEX_Forbidden = 0xC3


class NotFound(FailureResponse):
    code = OBEX_Not_Found = 0xC4


class PreconditionFailed(FailureResponse):
    code = OBEX_Precondition_Failed = 0xCC


class ResponseHandler(MessageHandler):

    message_dict = {
        Continue.code: Continue,
        Success.code: Success,
        BadRequest.code: BadRequest,
        Unauthorized.code: Unauthorized,
        Forbidden.code: Forbidden,
        NotFound.code: NotFound,
        PreconditionFailed.code: PreconditionFailed
    }

    UnknownMessageClass = UnknownResponse

    def decode_connection(self, socket):

        code, length, data = self._read_packet(socket)

        if code == ConnectSuccess.code:
            message = ConnectSuccess()
        elif code in ResponseHandler.message_dict:
            message = ResponseHandler.message_dict[code]()
        else:
            return self.UnknownMessageClass(code, length, data)

        obex_version, flags, max_packet_length = struct.unpack(">BBH",
                                                               data[3:7])

        message.obex_version = ObexVersion()
        message.obex_version.from_byte(obex_version)
        message.flags = flags
        message.max_packet_length = max_packet_length
        message.read_data(data)
        return message


# aliases for renamed classes
# the old names are deprecated and should not be used anymore
# they are scheduled for removal in the future
# pylint: disable=invalid-name
Bad_Request = BadRequest
Not_Found = NotFound
Precondition_Failed = PreconditionFailed
# pylint: enable=invalid-name

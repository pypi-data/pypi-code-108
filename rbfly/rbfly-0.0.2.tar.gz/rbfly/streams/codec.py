#
# rbfly - a library for RabbitMQ Streams using Python asyncio
#
# Copyright (C) 2021-2022 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Data and functions for RabbitMQ Streams encoding and decoding.
"""

import struct
import typing as tp

from . import const
from ._codec import FrameDecoder, Encoder, decode_publish_confirm, \
    decode_messages
from .offset import Offset, OffsetType, SIMPLE_OFFSET

FMT_FRAME_SIZE = struct.Struct('>I')
FMT_ARRAY_LEN = struct.Struct('>i')
FMT_STRING_LEN = struct.Struct('>h')

FMT_HEADER = struct.Struct('>HH')
FMT_TUNE = struct.Struct('>HHII')
FMT_CLOSE = struct.Struct('>H')
FMT_SUBSCRIPTION_ID = struct.Struct('>B')
FMT_CREDIT = struct.Struct('>HHBH')
FMT_CREDIT_SOLO = struct.Struct('>H')
FMT_CREDIT_RESPONSE = struct.Struct('>HB')
FMT_OFFSET_SPEC = struct.Struct('>H')
FMT_OFFSET_SPEC_OFFSET = struct.Struct('>HQ')
FMT_OFFSET_SPEC_TIMESTAMP = struct.Struct('>Hq')
FMT_OFFSET_VALUE = struct.Struct('>Q')
FMT_PUBLISH_ERROR = struct.Struct('>QH')

FMT_PUBLISHER_ID = struct.Struct('>B')
FMT_MESSAGE_ID = struct.Struct('>Q')

FMT_REQUEST_RESPONSE = struct.Struct('>IH')
FMT_REQUEST = struct.Struct('>HHI')

LEN_FRAME_SIZE = FMT_FRAME_SIZE.size
LEN_ARRAY_LEN = FMT_ARRAY_LEN.size
LEN_HEADER = FMT_HEADER.size
LEN_REQUEST_RESPONSE = FMT_REQUEST_RESPONSE.size
LEN_PUBLISH_ERROR = FMT_PUBLISH_ERROR.size

HEARTBEAT = b'\x00\x17\x00\x01'

def create_request(key: int, correlation_id: int, data: bytes) -> bytes:
    """
    Create request RabbitMQ Streams request.

    :var key: RabbitMQ Streams request key (command id).
    :var correlation_id: Correlation id.
    :var data: Content of RabbitMQ Streams request.
    """
    header = FMT_REQUEST.pack(key, const.VERSION, correlation_id)
    return header + data

def encode_properties(properties: dict[str, str]) -> bytes:
    """
    Encode RabbitMQ Streams properties data.
    """
    data = b''.join(
        encode_string(k) + encode_string(v)
        for k, v in properties.items()
    )
    return FMT_ARRAY_LEN.pack(len(properties)) + data

def sasl_authenticatation_data(username: str, password: str) -> bytes:
    """
    Create SASL authentication data for text/plain authentication.
    """
    # it is unclear how it should be encoded really
    # - username and password start with null
    # - above, concatenated, is prefixed with length; is it uint32 or int32?
    n = FMT_ARRAY_LEN.pack(len(username) + len(password) + 2)
    data = n + b'\x00' + username.encode() + b'\x00' + password.encode()
    return encode_string('PLAIN') + data

def encode_stream(stream: str) -> bytes:
    """
    Encode RabbitMQ Streams stream create request data.

    :var stream: Stream name.
    """
    return encode_string(stream) + FMT_ARRAY_LEN.pack(0)

def declare_publisher(
        publisher_id: int, publisher_ref: str, stream: str
    ) -> bytes:
    """
    Encode RabbitMQ Streams publisher declaration.

    :param publisher_id: Publisher id.
    :param publisher_ref: Publisher reference.
    :param stream: RabbitMQ stream name.
    """
    return FMT_PUBLISHER_ID.pack(publisher_id) \
        + encode_string(publisher_ref) \
        + encode_string(stream)

def encode_query_message_id(publisher_ref: str, stream: str) -> bytes:
    """
    Encode RabbitMQ Strreams message id query (publisher sequence query).

    :param publisher_ref: Publisher reference.
    :param stream: RabbitMQ stream name.
    """
    return encode_string(publisher_ref) + encode_string(stream)

def encode_subscribe(
        subscription_id: int,
        stream: str,
        offset: Offset,
        credit: int,
    ) -> bytes:
    """
    Encode RabbitMQ Streams subscription request.

    :param subscription_id: Subscription id.
    :param stream: RabbitMQ stream name.
    :param credit: Initial credit.
    """
    return FMT_SUBSCRIPTION_ID.pack(subscription_id) \
        + encode_string(stream) \
        + encode_offset(offset) \
        + FMT_CREDIT_SOLO.pack(credit) \
        + encode_properties({})

def encode_offset(offset: Offset) -> bytes:
    """
    Encode offset specification.

    :param offset: RabbitMQ Streams offset specification.
    """
    assert offset.type != OffsetType.REFERENCE

    if offset in SIMPLE_OFFSET:
        data = FMT_OFFSET_SPEC.pack(offset.type.value)
    elif offset.type == OffsetType.OFFSET:
        assert offset.value is not None
        data = FMT_OFFSET_SPEC_OFFSET.pack(offset.type.value, offset.value)
    elif offset.type == OffsetType.TIMESTAMP:
        assert offset.value is not None
        ts = int(offset.value * 1000)
        data = FMT_OFFSET_SPEC_TIMESTAMP.pack(offset.type.value, ts)
    else:
        assert 'unknown offset specification: {}'.format(offset)
    return data

def encode_query_offset(stream: str, reference: str) -> bytes:
    """
    Encode RabbitMQ Stream offset query.

    :param stream: Name of RabbitMQ stream.
    :param reference: Reference for RabbitMQ stream offset.
    """
    return encode_string(reference) + encode_string(stream)

def encode_credit(subscription_id: int, credit: int) -> bytes:
    """
    Encode RabbitMQ Streams credit request.

    :param subscription_id: Subscription id.
    :param credit: Credit value.
    """
    return FMT_CREDIT.pack(const.KEY_CREDIT, const.VERSION, subscription_id, credit)

def encode_store_offset(stream: str, reference: str, offset: Offset) -> bytes:
    """
    Encode RabbitMQ Streams command to store offset.

    :param stream: Name of RabbitMQ stream.
    :param reference: Reference for RabbitMQ stream offset.
    :param offset: RabbitMQ Streams offset specification.
    """
    assert offset.type == OffsetType.OFFSET
    return FMT_HEADER.pack(const.KEY_STORE_OFFSET, const.VERSION) \
        + encode_string(reference) \
        + encode_string(stream) \
        + FMT_OFFSET_VALUE.pack(offset.value)

def encode_close(code: int, reason: str) -> bytes:
    """
    Encode RabbitMQ Streams close request.

    # TODO: what are possible codes and reasons?

    :param code: Closing code.
    :param reason: Closing reason.
    """
    return FMT_CLOSE.pack(code) + encode_string(reason)

def encode_string(value: str) -> bytes:
    """
    Encode RabbitMQ Streams protocol string.
    """
    return FMT_STRING_LEN.pack(len(value)) + value.encode()

def decode_request(data: bytes, start: int) -> tuple[int, int]:
    """
    Decode RabbitMQ Streams response.

    The expected response is the one with correlation id.
    """
    return FMT_REQUEST_RESPONSE.unpack_from(data, start + LEN_HEADER)  # type: ignore

def decode_close(data: bytes, start: int) -> tuple[int, str]:
    """
    Decode close request.

    :param data: Data received from RabbitMQ Streams broker.
    :param start: Decoding starting point in the data.
    """
    offset = start + LEN_HEADER
    code = FMT_CLOSE.unpack_from(data, offset)[0]
    size = FMT_STRING_LEN.unpack_from(data, offset + FMT_CLOSE.size)[0]

    offset += FMT_CLOSE.size + FMT_STRING_LEN.size
    reason = data[offset:offset + size].decode()
    return code, reason

def decode_credit(data: bytes, start: int) -> tuple[int, int]:
    """
    Decode RabbitMQ Streams credit response.
    """
    return FMT_CREDIT_RESPONSE.unpack_from(data, start + LEN_HEADER)  # type: ignore

def encode_metadata_query(stream: str) -> bytes:
    """
    Encode metadata query.
    """
    return FMT_ARRAY_LEN.pack(1) + encode_string(stream)

def decode_publish_error(
        data: bytes, start: int
    ) -> tuple[int, tuple[tuple[int, int]]]:
    """
    Decode list of publishing errors.

    :param data: Data received from RabbitMQ Streams broker.
    :param start: Decoding starting point in the data.
    """
    offset = start + LEN_HEADER
    publisher_id = data[offset]
    offset += 1
    size = FMT_ARRAY_LEN.unpack_from(data, offset)[0]
    offset += LEN_ARRAY_LEN
    items = (
        FMT_PUBLISH_ERROR.unpack_from(data, offset + i * LEN_PUBLISH_ERROR)
        for i in range(size)
    )
    return tp.cast(
        tuple[int, tuple[tuple[int, int]]],
        (publisher_id, tuple(items))
    )

# vim: sw=4:et:ai

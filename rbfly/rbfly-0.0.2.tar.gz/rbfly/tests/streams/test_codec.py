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
Unit tests for encoding and decoding of RabbitMQ streams requests and
commands.
"""

import struct
import typing as tp

from rbfly.amqp import Message
from rbfly.streams import codec
from rbfly.streams.offset import Offset
from rbfly.streams.protocol import RabbitMQStreamsProtocol
from rbfly.streams.types import MessageQueue

import pytest
from unittest import mock

FMT_FRAME_SIZE = struct.Struct('>IHH')

DELIVERED_MSG_DATA_1 = b'P\x00\x00\x01\x00\x00\x00\x01\x00\x00\x01}\x1e]\x8d\x10\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00k\x89\xe4\xca\x00\x00\x00\x0e\x00\x00\x00(\x00\x00\x00\x00\x00\x00\x00\x0f\x00Su\xa0\n3210000123'
DELIVERED_MSG_DATA_2 = b'P\x00\x00\x02\x00\x00\x00$\x00\x00\x01}\x1e\xd9\xc7\xca\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03\xce\x13B\x0f\xcd\x00\x00\x00\x18\x00\x00\x00(\x00\x00\x00\x00\x00\x00\x00\x0f\x00Su\xa0\n0000000064\x00\x00\x00\x0f\x00Su\xa0\n0000000065'
DELIVERED_DATA = (  # type: ignore
    (
        DELIVERED_MSG_DATA_1,
        None,
        [Message(b'3210000123', stream_offset=0, stream_timestamp=1636891987)]
    ),
    (
        DELIVERED_MSG_DATA_1,
        0,
        [Message(b'3210000123', stream_offset=0, stream_timestamp=1636891987)]
    ),
    (DELIVERED_MSG_DATA_1, 1, []),  # request offset > 0
    (
        DELIVERED_MSG_DATA_2,
        974,
        [
            Message(b'0000000064', stream_offset=974, stream_timestamp=1636900128),
            Message(b'0000000065', stream_offset=975, stream_timestamp=1636900128),
        ],
    ),
    (
        DELIVERED_MSG_DATA_2,
        975,
        [Message(b'0000000065', stream_offset=975, stream_timestamp=1636900128)]
    ),
)

OFFSET_DATA = (
    (Offset.FIRST, b'\x00\x01'),
    (Offset.LAST, b'\x00\x02'),
    (Offset.NEXT, b'\x00\x03'),
    (Offset.offset(1024), b'\x00\x04\x00\x00\x00\x00\x00\x00\x04\x00'),

    # timestamp is encoded in milliseconds
    (Offset.timestamp(256), b'\x00\x05\x00\x00\x00\x00\x00\x03\xe8\x00'),
)

def test_create_request() -> None:
    """
    Test encoding a RabbitMQ Streams request.
    """
    result = codec.create_request(16, 2, b'abc')
    assert result == b'\x00\x10\x00\x01\x00\x00\x00\x02abc'

def test_encode_properties() -> None:
    """
    Test encoding RabbitMQ Streams properties.
    """
    properties = {'product': 'test-product', 'platform': 'Python'}
    result = codec.encode_properties(properties)
    expected = b'\x00\x00\x00\x02' \
            + b'\x00\x07product\x00\x0ctest-product' \
            + b'\x00\x08platform\x00\x06Python'
    assert result == expected

def test_encode_sasl_authentication_data() -> None:
    """
    Test serializing RabbitMQ SASL authentication data.
    """
    result = codec.sasl_authenticatation_data('abc', 'xyzt')
    expected = b'\x00\x05PLAIN\x00\x00\x00\x09\x00abc\x00xyzt'
    assert result == expected

def test_encode_stream() -> None:
    """
    Test encoding data for RabbitMQ Streams creation.
    """
    result = codec.encode_stream('test-stream')
    expected = b'\x00\x0btest-stream\x00\x00\x00\x00'
    assert result == expected

def test_declare_publisher() -> None:
    """
    Test encoding publisher declaration.
    """
    result = codec.declare_publisher(2, 'stream_ref_1', 'stream')
    expected = b'\x02\x00\x0cstream_ref_1\x00\x06stream'
    assert result == expected

def test_encode_message_id_query() -> None:
    """
    Test encoding message id query.
    """
    result = codec.encode_query_message_id('ref', 'stream')
    assert result == b'\x00\x03ref\x00\x06stream'

def test_encode_close() -> None:
    """
    Test encoding RabbitMQ Streams close request.
    """
    result = codec.encode_close(1, 'OK')
    assert result == b'\x00\x01\00\x02OK'

def test_decode_close() -> None:
    """
    Test decoding RabbitMQ Streams close request.
    """
    code, reason = codec.decode_close(b'skip\x80\x16\x00\x01\x00\x02\00\x02OKpost', 4)
    assert code == 2
    assert reason == 'OK'

def test_encode_string() -> None:
    """
    Test serializing RabbitMQ Streams protocol string.
    """
    result = codec.encode_string('abcde')
    assert result == b'\x00\x05abcde'

def test_encode_publish_single() -> None:
    """
    Test encoding single published message.
    """
    encoder = codec.Encoder(1024)
    data = [Message(b'123')]
    result = encoder.encode_publish(5, 10, *data)

    expected = b'\x00\x02\x00\x01\x05\x00\x00\x00\x01' \
        + b'\x00\x00\x00\x00\x00\x00\x00\x0a\x00\x00\x00\x08\x00Su\xa0\x03123'
    assert result == expected

def test_encode_publish_multi() -> None:
    """
    Test encoding multiple published messages.
    """
    encoder = codec.Encoder(1024)
    data = [Message(b'123') , Message(b'9876')]
    result = encoder.encode_publish(5, 10, *data)

    expected = b'\x00\x02\x00\x01\x05\x00\x00\x00\x02' \
        + b'\x00\x00\x00\x00\x00\x00\x00\x0a\x00\x00\x00\x08\x00Su\xa0\x03123' \
        + b'\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x09\x00Su\xa0\x049876'

    assert result == expected

@pytest.mark.parametrize('data, offset, expected', DELIVERED_DATA)
def test_decode_delivered_message(
        data: bytes,
        offset: tp.Optional[int],
        expected: list[Message]
    ) -> None:
    """
    Test decoding delivered messages.
    """
    result = MessageQueue()
    codec.decode_messages(data, 0, offset, result, True)
    assert list(result) == expected

@pytest.mark.parametrize('offset, expected', OFFSET_DATA)
def test_encode_offset(offset: Offset, expected: bytes) -> None:
    """
    Test encoding RabbitMQ Streams offset specification.
    """
    assert codec.encode_offset(offset) == expected

def test_decode_publish_error() -> None:
    """
    Test decoding publishing error.
    """
    data = b'\x00\x04\x00\x01\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00T\x00\x12'
    result = codec.decode_publish_error(data, 0)
    assert (1, ((84, 0x12),)) == result

#
# protocol frame encoding and decoding
#
def test_send_frame() -> None:
    """
    Test sending RabbitMQ streams frame with asyncio transport.
    """
    transport = mock.MagicMock()
    with mock.patch('asyncio.get_running_loop'):
        protocol = RabbitMQStreamsProtocol()
        protocol.connection_made(transport)

        protocol.send_frame(b'54321')
        calls = transport.write.call_args_list

        # size of the frame is sent first, then its data
        assert calls == [mock.call(b'\x00\x00\x00\x05'), mock.call(b'54321')]

def test_frame_on_empty() -> None:
    """
    Test RabbitMQ Streams protocol frame decoding when decoder's buffer is
    empty.
    """
    decoder = codec.FrameDecoder()
    frame = create_frame(b'\xff')

    it = decoder.commands(frame)

    # check index, command key value and available data
    assert next(it) == (4, 1)
    assert decoder.data == b'\x00\x00\x00\x05\x00\x01\x00\x01\xff'

    # no more data
    assert next(it, None) is None
    assert decoder.data == b''

def test_frame_twice() -> None:
    """
    Test updating RabbitMQ Streams frame decoding with two frames.
    """
    decoder = codec.FrameDecoder()
    frames = create_frame(b'\xff') + create_frame(b'\xfe\xef')

    it = decoder.commands(frames)
    assert next(it) == (4, 1)
    assert decoder.data[4:9] == b'\x00\x01\x00\x01\xff'
    assert next(it) == (13, 1)
    assert decoder.data[13:] == b'\x00\x01\x00\x01\xfe\xef'

    assert next(it, None) is None
    assert decoder.data == b''

def test_frame_incomplete() -> None:
    """
    Test RabbitMQ Streams protocol frame decoding with incomplete frame
    data.
    """
    decoder = codec.FrameDecoder()

    # 2nd frame is incomplete
    frames = create_frame(b'\xff') + create_frame(b'\xfe\xef', 4)
    assert list(decoder.commands(frames)) == [(4, 1)]

    # finish buffer update
    it = decoder.commands(b'\xab\xba')
    assert next(it) == (4, 1)
    assert decoder.data[4:] == b'\x00\x01\x00\x01\xfe\xef\xab\xba'
    assert next(it, None) is None
    assert decoder.data == b''


def create_frame(data: bytes, n: tp.Optional[int]=None) -> bytes:
    """
    Utility function to create RabbitMQ Streams protocol frame.
    """
    size = len(data) if n is None else n
    size += FMT_FRAME_SIZE.size - 4
    return FMT_FRAME_SIZE.pack(size, 1, 1) + data

# vim: sw=4:et:ai

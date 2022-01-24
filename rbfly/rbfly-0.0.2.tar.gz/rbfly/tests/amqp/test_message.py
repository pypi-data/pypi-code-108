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

from rbfly.amqp._message import Message, encode_amqp, decode_amqp

import pytest

DATA = (
    (Message(b'\x01\x00\x00\x00\x02'), b'\x00Su\xa0\x05\x01\x00\x00\x00\x02'),
    (Message(b'abcde'), b'\x00Su\xa0\x05abcde'),
    (Message(b'a' * 256), b'\x00Su\xb0\x00\x00\x01\x00' + b'a' * 256),
    (Message('abcde'), b'\x00Sw\xa1\x05abcde'),
    (Message('a' * 256), b'\x00Sw\xb1\x00\x00\x01\x00' + b'a' * 256),
)

MESSAGE_REPR = (
    (
        repr(Message('a-string')),
        '"Message(body=\'a-string\', stream_offset=0, stream_timestamp=0.0)"',
    ),
    (
        repr(Message(b'binary-data-and-more')),
        '"Message(body=b\'binary-dat\', stream_offset=0, stream_timestamp=0.0)"',
    ),
)

@pytest.mark.parametrize('message, expected', DATA)
def test_encode(message: Message, expected: bytes) -> None:
    """
    Test encoding AMQP messages.
    """
    msg_buffer = bytearray(1024)
    size = encode_amqp(msg_buffer, message)
    assert msg_buffer[:size] == expected

def test_encode_binary_invalid() -> None:
    """
    Test error on encoding too long binary AMQP messages.
    """
    msg_buffer = bytearray(1024)
    with pytest.raises(ValueError):
        encode_amqp(msg_buffer, Message(b'a' * 2 ** 32))

@pytest.mark.parametrize('message, data', DATA)
def test_decode(message: Message, data: bytes) -> None:
    """
    Test decoding AMQP messages.
    """
    result = decode_amqp(data)
    assert result == message

@pytest.mark.parametrize('message, expected', MESSAGE_REPR)
def test_message_repr(message: Message, expected: str) -> None:
    """
    Test AMQP message representation.
    """
    assert repr(message) == expected

# vim: sw=4:et:ai

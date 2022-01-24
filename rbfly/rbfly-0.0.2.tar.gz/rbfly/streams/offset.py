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
RabbitMQ Streams offset specification is used by a client application to
declare, which messages from a streams should be received on stream
subscription.

:py:meth:`rbfly.streams.StreamsClient.subscribe` method accepts optional
`offset` parameter, which can be one of the following:

:py:const:`rbfly.streams.Offset.NEXT`
    Receive new messages from a stream only. Default offset specification.
:py:const:`rbfly.streams.Offset.FIRST`
    Receive all messages, starting with the very first message in a
    stream. Equivalent to `Offset.offset(0)`.
:py:const:`rbfly.streams.Offset.LAST`
    Receive messages from a streams starting with first message stored in
    the current stream chunk (see also below).
:py:meth:`rbfly.streams.Offset.offset`
    Receive messages from a stream starting with specific offset value.
:py:meth:`rbfly.streams.Offset.reference`
    Use the reference to get the offset stored in a stream. Receive
    messages starting from the next offset (this is `offset + 1`).
:py:meth:`rbfly.streams.Offset.timestamp`
    Receive messages from a stream starting with the specified timestamp of
    a message.

The following diagram visualizes offset location in a stream when each
chunk has 100 messages::

                               +- Offset.reference('ref-a') + 1
                               |
      chunk 1: [0] [1, ref-a] [2] ... [99]
                |
                +- Offset.FIRST

      chunk 2: [100, 1633006475.571] [101, 1633006475.999] ... [199, 1633006477.999]
                                       |                             |
                                       +- Offset.offset(101)         +- Offset.timestamp(1633006476.0)

      ...    : ...
                                       +- end of stream
                                       |
      chunk 10: [900] [901] ... [999]  +
                  |                    |
                  +- Offset.LAST       +- Offset.NEXT

.. note::
   Timestamp is `Erlang runtime system
   <https://www.erlang.org/doc/apps/erts/time_correction.html#Erlang_System_Time>`_.
   It is a view of POSIX time.
"""

from __future__ import annotations

import dataclasses as dtc
import enum
import typing as tp

class OffsetType(enum.IntEnum):
    """
    Offset type for RabbitMQ stream subscription.
    """
    FIRST = 0x0001
    LAST = 0x0002
    NEXT = 0x0003
    OFFSET = 0x0004
    TIMESTAMP = 0x0005
    REFERENCE = 0xffff  # NOTE: used for API design, not part of RabbitMQ
                        #       Streams protocol

@dtc.dataclass(frozen=True)
class Offset:
    """
    Offset specification for RabbitMQ stream subscription.
    """
    type: OffsetType
    value: tp.Optional[int | float | str]=None


    #: Receive all messages, starting with the very first message
    #: in a stream. Equivalent to `Offset.offset(0)`.
    FIRST: 'Offset'=dtc.field(init=False)

    #: Receive messages from a streams starting with first message stored
    #: in the current stream chunk.
    LAST: 'Offset'=dtc.field(init=False)

    #: Receive new messages from a stream only. Default offset
    #: specification.
    NEXT: 'Offset'=dtc.field(init=False)

    @staticmethod
    def offset(offset: int) -> Offset:
        """
        Create offset specification with offset value.

        :param offset: Offset value.
        """
        return Offset(OffsetType.OFFSET, offset)

    @staticmethod
    def timestamp(timestamp: float) -> Offset:
        """
        Create offset specification with timestamp value.

        :param timestamp: Unix timestamp in seconds since epoch.
        """
        return Offset(OffsetType.TIMESTAMP, timestamp)

    @staticmethod
    def reference(reference: str) -> Offset:
        """
        Create offset specification, which queries and stores stream
        offset with offset reference.

        :param reference: Offset reference string.
        """
        return Offset(OffsetType.REFERENCE, reference)

    def __str__(self) -> str:
        result = 'Offset.{}'.format(self.type.name)
        if self not in SIMPLE_OFFSET:
            result += '({})'.format(self.value)
        return result

    __repr__ = __str__

# define constants for API use
Offset.FIRST = Offset(OffsetType.FIRST)
Offset.LAST = Offset(OffsetType.LAST)
Offset.NEXT = Offset(OffsetType.NEXT)

# indicate offset sepecifications, which require no parameter
SIMPLE_OFFSET = (Offset.FIRST, Offset.LAST, Offset.NEXT)

# vim: sw=4:et:ai

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
Connection manager for protocols implementing Asyncio stream protocol
interface.
"""

import asyncio
import logging
import typing as tp
from abc import abstractproperty, abstractmethod

from .util import Option

logger = logging.getLogger(__name__)

P = tp.TypeVar('P', bound='RProto')
T = tp.TypeVar('T')

class RProto(tp.Protocol):
    @abstractproperty
    def connected(self) -> bool: ...

class ConnectionManager(tp.Generic[P]):
    _protocol: Option[P]

    def __init__(self) -> None:
        self._protocol = Option[P]()
        self._lock = asyncio.Lock()

    @abstractmethod
    async def _create_protocol(self) -> P: ...

    @abstractmethod
    async def _connect(self, protocol: P) -> None: ...

    @abstractmethod
    async def _disconnect(self, protocol: P) -> None: ...

    @property
    def connected(self) -> bool:
        return not self._protocol.empty and self._protocol.value.connected

    async def get_protocol(self, *, wait_connected: bool=True) -> P:
        # prevent creating multiple protocols with the lock; this will
        # happen when there are multiple subscribers, or multiple
        # publishers, or mix of both
        async with self._lock:
            if wait_connected and not self.connected:
                protocol = await self._reconnect()
                self._protocol = protocol
            elif not wait_connected and not self.connected:
                raise ConnectionError('protocol is disconnected')

        assert self.connected
        return self._protocol.value

    async def _reconnect(self) -> Option[P]:
        while True:
            try:
                logger.info('connecting...')
                protocol = await self._create_protocol()
                await self._connect(protocol)

            # Python 3.10.1 - we might get OSError when connecting as well
            except (ConnectionError, OSError) as ex:
                logger.warning('connection error: %s', ex)
                await asyncio.sleep(5)
            else:
                return Option(protocol)

    async def disconnect(self) -> None:
        if self.connected:
            await self._disconnect(self._protocol.value)
        else:
            logger.info('no active connection, silent disconnect')

# vim: sw=4:et:ai

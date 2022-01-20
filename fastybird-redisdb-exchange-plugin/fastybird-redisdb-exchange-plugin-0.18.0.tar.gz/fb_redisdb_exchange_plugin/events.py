#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

"""
Redis DB exchange plugin events
"""

# Library dependencies
from whistle import Event


class BeforeMessageHandledEvent(Event):
    """
    Event fired when new message is received from exchange

    @package        FastyBird:RedisDbExchangePlugin!
    @module         events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __payload: str

    EVENT_NAME: str = "redisdb-exchange.beforeMessageHandled"

    # -----------------------------------------------------------------------------

    def __init__(self, payload: str) -> None:
        self.__payload = payload

    # -----------------------------------------------------------------------------

    def payload(self) -> str:
        """Received message payload"""
        return self.__payload


class AfterMessageHandledEvent(Event):
    """
    Event fired after received message from exchange is consumed

    @package        FastyBird:RedisDbExchangePlugin!
    @module         events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __payload: str

    EVENT_NAME: str = "redisdb-exchange.afterMessageHandled"

    # -----------------------------------------------------------------------------

    def __init__(self, payload: str) -> None:
        self.__payload = payload

    # -----------------------------------------------------------------------------

    def payload(self) -> str:
        """Received message payload"""
        return self.__payload


class ConnectionClosedEventEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Event fired when connection to Redis is closed

    @package        FastyBird:RedisDbExchangePlugin!
    @module         events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    EVENT_NAME: str = "redisdb-exchange.connectionClosed"

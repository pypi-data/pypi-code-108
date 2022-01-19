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
Redis DB exchange plugin connection service
"""

# Python base dependencies
import json
from typing import Dict, Optional, Union

# Library dependencies
from redis import Redis
from redis.client import PubSub
from whistle import EventDispatcher

# Library libs
from fb_redisdb_exchange_plugin.events import ConnectionClosedEventEvent
from fb_redisdb_exchange_plugin.exceptions import InvalidStateException
from fb_redisdb_exchange_plugin.logger import Logger


class Connection(Redis):  # pylint: disable=abstract-method,too-many-ancestors
    """
    Redis client

    @package        FastyBird:RedisDbExchangePlugin!
    @module         connection

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __pub_sub: Optional[PubSub] = None

    __identifier: str
    __channel_name: str

    __event_dispatcher: Optional[EventDispatcher]

    __logger: Logger

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        identifier: str,
        host: str,
        port: int,
        channel_name: str,
        logger: Logger,
        username: Optional[str] = None,
        password: Optional[str] = None,
        event_dispatcher: Optional[EventDispatcher] = None,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            username=username,
            password=password,
        )

        self.__identifier = identifier
        self.__channel_name = channel_name

        self.__event_dispatcher = event_dispatcher

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def subscribe(self) -> None:
        """Subscribe to default exchange channel"""
        if self.__pub_sub is not None:
            raise InvalidStateException("Exchange is already subscribed to exchange")

        # Connect to pub sub exchange
        self.__pub_sub = super().pubsub()
        # Subscribe to channel
        self.__pub_sub.subscribe(self.__channel_name)

        self.__logger.debug(
            "Successfully subscribed to RedisDB exchange channel: %s",
            self.__channel_name,
            extra={
                "source": "redisdb-exchange-plugin-connection",
                "type": "subscribe",
            },
        )

    # -----------------------------------------------------------------------------

    def unsubscribe(self) -> None:
        """Unsubscribe from default exchange channel"""
        if self.__pub_sub is not None:
            # Unsubscribe from channel
            self.__pub_sub.unsubscribe(self.__channel_name)
            # Disconnect from pub sub exchange
            self.__pub_sub.close()

            self.__logger.debug(
                "Successfully unsubscribed from RedisDB exchange channel: %s",
                self.__channel_name,
                extra={
                    "source": "redisdb-exchange-plugin-connection",
                    "type": "unsubscribe",
                },
            )

            self.__pub_sub = None

    # -----------------------------------------------------------------------------

    def receive(self) -> Optional[Dict]:
        """Try to receive new message from exchange"""
        if self.__pub_sub is not None:
            result = self.__pub_sub.get_message()

            if (
                result is not None
                and result.get("type") == "message"
                and isinstance(result.get("data", bytes("{}", "utf-8")), bytes)
            ):
                message_data = result.get("data", bytes("{}", "utf-8"))
                message = message_data.decode("utf-8") if isinstance(message_data, bytes) else ""

                try:
                    data: Dict[str, Union[str, int, float, bool, None]] = json.loads(message)

                    # Ignore own messages
                    if data.get("sender_id", None) is not None and data.get("sender_id", None) == self.__identifier:
                        return None

                    return data

                except json.JSONDecodeError as ex:
                    self.__logger.exception(ex)

        return None

    # -----------------------------------------------------------------------------

    def close(self) -> None:
        """Close opened connection to Redis database"""
        self.unsubscribe()

        super().close()

        if self.__event_dispatcher is not None:
            self.__event_dispatcher.dispatch(
                event_id=ConnectionClosedEventEvent.EVENT_NAME,
                event=ConnectionClosedEventEvent(),
            )

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Get connection generated identifier"""
        return self.__identifier

    # -----------------------------------------------------------------------------

    def __del__(self) -> None:
        super().close()

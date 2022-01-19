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
Redis DB exchange plugin exchange service
"""

# Python base dependencies
import json
import time
from typing import Dict, Optional

# Library dependencies
import fb_metadata.exceptions as metadata_exceptions
from fb_exchange.client import IClient
from fb_exchange.consumer import Consumer
from fb_metadata.loader import load_schema_by_routing_key
from fb_metadata.routing import RoutingKey
from fb_metadata.types import ModuleOrigin
from fb_metadata.validator import validate
from kink import inject
from whistle import EventDispatcher

# Library libs
from fb_redisdb_exchange_plugin.connection import Connection
from fb_redisdb_exchange_plugin.events import (
    AfterMessageHandledEvent,
    BeforeMessageHandledEvent,
)
from fb_redisdb_exchange_plugin.exceptions import (
    HandleDataException,
    HandleRequestException,
)
from fb_redisdb_exchange_plugin.logger import Logger


@inject(alias=IClient)
class Client(IClient):
    """
    Redis exchange client

    @package        FastyBird:RedisDbExchangePlugin!
    @module         client

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __connection: Connection

    __event_dispatcher: Optional[EventDispatcher]
    __consumer: Optional[Consumer]

    __logger: Logger

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        connection: Connection,
        logger: Logger,
        event_dispatcher: Optional[EventDispatcher] = None,
        consumer: Optional[Consumer] = None,
    ) -> None:
        self.__event_dispatcher = event_dispatcher
        self.__connection = connection
        self.__logger = logger

        self.__consumer = consumer

    # -----------------------------------------------------------------------------

    def start(self) -> None:
        """Start exchange services"""
        self.__connection.subscribe()

        self.__logger.info(
            "Starting Redis DB exchange client",
            extra={
                "source": "redisdb-exchange-plugin-client",
                "type": "start",
            },
        )

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Close all opened connections & stop exchange thread"""
        self.__connection.unsubscribe()
        self.__connection.close()

        self.__logger.info(
            "Closing Redis DB exchange client",
            extra={
                "source": "redisdb-exchange-plugin-client",
                "type": "stop",
            },
        )

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Process Redis exchange messages"""
        try:
            data = self.__connection.receive()

            if data is not None:
                self.__receive(data)

            time.sleep(0.001)

        except OSError as ex:
            raise HandleRequestException("Error reading from redis database") from ex

    # -----------------------------------------------------------------------------

    def register_consumer(self, consumer: Consumer) -> None:
        """Register client consumer"""
        self.__consumer = consumer

    # -----------------------------------------------------------------------------

    def __receive(self, data: Dict) -> None:
        if self.__event_dispatcher is not None:
            self.__event_dispatcher.dispatch(
                event_id=BeforeMessageHandledEvent.EVENT_NAME, event=BeforeMessageHandledEvent(payload=json.dumps(data))
            )

        if self.__consumer is not None:
            try:
                origin = self.__validate_origin(origin=data.get("origin", None))
                routing_key = self.__validate_routing_key(
                    routing_key=data.get("routing_key", None),
                )

                if (
                    routing_key is not None
                    and origin is not None
                    and data.get("data", None) is not None
                    and isinstance(data.get("data", None), dict) is True
                ):
                    data = self.__validate_data(
                        origin=origin,
                        routing_key=routing_key,
                        data=data.get("data", None),
                    )

                    self.__consumer.consume(
                        origin=origin,
                        routing_key=routing_key,
                        data=data,
                    )

                else:
                    self.__logger.warning(
                        "Received exchange message is not valid",
                        extra={
                            "source": "redisdb-exchange-plugin-client",
                            "type": "receive",
                        },
                    )

            except HandleDataException as ex:
                self.__logger.exception(ex)

        if self.__event_dispatcher is not None:
            self.__event_dispatcher.dispatch(
                event_id=AfterMessageHandledEvent.EVENT_NAME, event=AfterMessageHandledEvent(payload=json.dumps(data))
            )

    # -----------------------------------------------------------------------------

    @staticmethod
    def __validate_origin(origin: Optional[str]) -> Optional[ModuleOrigin]:
        if origin is not None and isinstance(origin, str) is True and ModuleOrigin.has_value(origin):
            return ModuleOrigin(origin)

        return None

    # -----------------------------------------------------------------------------

    @staticmethod
    def __validate_routing_key(routing_key: Optional[str]) -> Optional[RoutingKey]:
        if routing_key is not None and isinstance(routing_key, str) is True and RoutingKey.has_value(routing_key):
            return RoutingKey(routing_key)

        return None

    # -----------------------------------------------------------------------------

    def __validate_data(self, origin: ModuleOrigin, routing_key: RoutingKey, data: Dict) -> Dict:
        """Validate received exchange message against defined schema"""
        try:
            schema: str = load_schema_by_routing_key(routing_key)

        except metadata_exceptions.FileNotFoundException as ex:
            self.__logger.error(
                "Schema file for origin: %s and routing key: %s could not be loaded",
                origin.value,
                routing_key.value,
                extra={
                    "source": "redisdb-exchange-plugin-client",
                    "type": "validate-data",
                },
            )

            raise HandleDataException("Provided data could not be validated") from ex

        except metadata_exceptions.InvalidArgumentException as ex:
            self.__logger.error(
                "Schema file for origin: %s and routing key: %s is not configured in mapping",
                origin.value,
                routing_key.value,
                extra={
                    "source": "redisdb-exchange-plugin-client",
                    "type": "validate-data",
                },
            )

            raise HandleDataException("Provided data could not be validated") from ex

        try:
            return validate(json.dumps(data), schema)

        except metadata_exceptions.MalformedInputException as ex:
            raise HandleDataException("Provided data are not in valid json format") from ex

        except metadata_exceptions.LogicException as ex:
            self.__logger.error(
                "Schema file for origin: %s and routing key: %s could not be parsed & compiled",
                origin.value,
                routing_key.value,
                extra={
                    "source": "redisdb-exchange-plugin-client",
                    "type": "validate-data",
                },
            )

            raise HandleDataException("Provided data could not be validated") from ex

        except metadata_exceptions.InvalidDataException as ex:
            raise HandleDataException("Provided data are not valid") from ex

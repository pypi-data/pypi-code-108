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
FastyBird BUS connector receivers module proxy
"""

# Python base dependencies
from queue import Full as QueueFull
from queue import Queue
from typing import List, Optional, Set

# Library libs
from fastybird_fb_bus_connector.api.v1parser import V1Parser
from fastybird_fb_bus_connector.api.v1validator import V1Validator
from fastybird_fb_bus_connector.exceptions import (
    InvalidStateException,
    ParsePayloadException,
)
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.receivers.base import IReceiver
from fastybird_fb_bus_connector.receivers.entities import BaseEntity
from fastybird_fb_bus_connector.types import ProtocolVersion


class Receiver:
    """
    BUS messages receivers proxy

    @package        FastyBird:FbBusConnector!
    @module         receivers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __receivers: Set[IReceiver]
    __queue: Queue
    __parser: V1Parser
    __validator: V1Validator

    __logger: Logger

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        receivers: List[IReceiver],
        parser: V1Parser,
        validator: V1Validator,
        logger: Logger,
    ) -> None:
        self.__receivers = set(receivers)
        self.__parser = parser
        self.__validator = validator

        self.__logger = logger

        self.__queue = Queue(maxsize=1000)

    # -----------------------------------------------------------------------------

    def append(self, entity: BaseEntity) -> None:
        """Append new entity to process"""
        try:
            self.__queue.put(item=entity)

        except QueueFull:
            self.__logger.error("Connector receiver processing queue is full. New messages could not be added")

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Process received message"""
        try:
            if not self.__queue.empty():
                entity = self.__queue.get()

                if isinstance(entity, BaseEntity):
                    for receiver in self.__receivers:
                        receiver.receive(entity=entity)

        except InvalidStateException as ex:
            self.__logger.error(
                "Received message could not be processed",
                extra={
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )

    # -----------------------------------------------------------------------------

    def is_empty(self) -> bool:
        """Check if all messages are processed"""
        return self.__queue.empty()

    # -----------------------------------------------------------------------------

    def on_message(  # pylint: disable=too-many-arguments
        self,
        payload: bytearray,
        length: int,
        address: Optional[int],
        protocol_version: ProtocolVersion,
    ) -> None:
        """Handle received message"""
        if self.__validator.version == protocol_version and self.__validator.validate_version(payload=payload) is False:
            return

        if self.__validator.version == protocol_version and self.__validator.validate(payload=payload) is False:
            self.__logger.warning(
                "Received message is not valid FIB v%s convention message: %s",
                protocol_version.value,
                payload,
            )

            return

        try:
            if self.__validator.version == protocol_version:
                self.append(
                    entity=self.__parser.parse_message(
                        payload=payload,
                        length=length,
                        address=address,
                    ),
                )

        except ParsePayloadException as ex:
            self.__logger.error(
                "Received message could not be successfully parsed to entity",
                extra={
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )

            return

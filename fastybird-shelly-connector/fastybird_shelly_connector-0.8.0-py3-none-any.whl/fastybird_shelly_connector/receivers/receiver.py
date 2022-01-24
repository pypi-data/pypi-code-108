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
Shelly connector receivers module receivers proxy
"""

# Python base dependencies
import time
from abc import ABC, abstractmethod
from queue import Full as QueueFull
from queue import Queue
from typing import List, Set

# Library libs
from fastybird_shelly_connector.api.gen1parser import Gen1Parser
from fastybird_shelly_connector.api.gen1validator import Gen1Validator
from fastybird_shelly_connector.exceptions import (
    FileNotFoundException,
    InvalidStateException,
    LogicException,
    ParsePayloadException,
)
from fastybird_shelly_connector.logger import Logger
from fastybird_shelly_connector.receivers.entities import BaseEntity, DeviceFoundEntity
from fastybird_shelly_connector.registry.model import DevicesRegistry
from fastybird_shelly_connector.types import ClientMessageType


class IReceiver(ABC):  # pylint: disable=too-few-public-methods
    """
    Plugin messages receiver interface

    @package        FastyBird:ShellyConnector!
    @module         receivers/receiver

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @abstractmethod
    def receive(self, entity: BaseEntity) -> None:
        """Handle received entity"""


class Receiver:
    """
    Plugin messages receivers proxy

    @package        FastyBird:ShellyConnector!
    @module         receivers/receiver

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __validator: Gen1Validator
    __parser: Gen1Parser

    __receivers: Set[IReceiver]
    __devices_registry: DevicesRegistry
    __queue: Queue

    __logger: Logger

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        validator: Gen1Validator,
        parser: Gen1Parser,
        receivers: List[IReceiver],
        devices_registry: DevicesRegistry,
        logger: Logger,
    ) -> None:
        self.__receivers = set(receivers)
        self.__devices_registry = devices_registry

        self.__validator = validator
        self.__parser = parser

        self.__logger = logger

        self.__queue = Queue(maxsize=1000)

    # -----------------------------------------------------------------------------

    def on_coap_message(  # pylint: disable=too-many-arguments
        self,
        device_identifier: str,
        device_type: str,
        device_ip_address: str,
        message_payload: str,
        message_type: ClientMessageType,
    ) -> None:
        """Handle message received via CoAP client"""
        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=device_identifier,
        )

        if device_record is not None:
            self.__devices_registry.set_last_communication_timestamp(
                device=device_record,
                last_communication_timestamp=time.time(),
            )

        try:
            if (
                self.__validator.validate_coap_message(
                    message_payload=message_payload,
                    message_type=message_type,
                )
                is False
            ):
                return

        except (LogicException, FileNotFoundException) as ex:
            self.__logger.error(
                "Received message validation against schema failed",
                extra={
                    "device": {
                        "identifier": device_identifier,
                        "type": device_type,
                    },
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )

            return

        try:
            entity = self.__parser.parse_coap_message(
                device_identifier=device_identifier,
                device_type=device_type,
                device_ip_address=device_ip_address,
                message_payload=message_payload,
                message_type=message_type,
            )

        except (FileNotFoundException, LogicException, ParsePayloadException) as ex:
            self.__logger.error(
                "Received message could not be successfully parsed to entity",
                extra={
                    "device": {
                        "identifier": device_identifier,
                        "type": device_type,
                    },
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )

            return

        self.append(entity=entity)

    # -----------------------------------------------------------------------------

    def on_mdns_message(
        self,
        device_identifier: str,
        device_ip_address: str,
    ) -> None:
        """Handle message received via mDNS client"""
        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=device_identifier,
        )

        if device_record is not None:
            self.__devices_registry.set_last_communication_timestamp(
                device=device_record,
                last_communication_timestamp=time.time(),
            )

        self.append(
            entity=DeviceFoundEntity(
                device_identifier=device_identifier,
                device_ip_address=device_ip_address,
            ),
        )

    # -----------------------------------------------------------------------------

    def on_http_message(  # pylint: disable=too-many-arguments
        self,
        device_identifier: str,
        device_ip_address: str,
        message_payload: str,
        message_type: ClientMessageType,
    ) -> None:
        """Handle message received via HTTP client"""
        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=device_identifier,
        )

        if device_record is not None:
            self.__devices_registry.set_last_communication_timestamp(
                device=device_record,
                last_communication_timestamp=time.time(),
            )

        try:
            if (
                self.__validator.validate_http_message(
                    message_payload=message_payload,
                    message_type=message_type,
                )
                is False
            ):
                return

        except (LogicException, FileNotFoundException) as ex:
            self.__logger.error(
                "Received message validation against schema failed",
                extra={
                    "device": {
                        "identifier": device_identifier,
                        "ip_address": device_ip_address,
                    },
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )
            return

        try:
            entity = self.__parser.parse_http_message(
                device_identifier=device_identifier,
                device_ip_address=device_ip_address,
                message_payload=message_payload,
                message_type=message_type,
            )

        except (FileNotFoundException, LogicException, ParsePayloadException) as ex:
            self.__logger.error(
                "Received message could not be successfully parsed to entity",
                extra={
                    "device": {
                        "identifier": device_identifier,
                        "ip_address": device_ip_address,
                    },
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )
            return

        self.append(entity=entity)

    # -----------------------------------------------------------------------------

    def append(self, entity: BaseEntity) -> None:
        """Append new entity for handle"""
        try:
            self.__queue.put(item=entity)

        except QueueFull:
            self.__logger.error("Receiver queue is full. New messages could not be added")

    # -----------------------------------------------------------------------------

    def loop(self) -> None:
        """Handle received message"""
        try:
            if not self.__queue.empty():
                entity = self.__queue.get()

                if isinstance(entity, BaseEntity):
                    for receiver in self.__receivers:
                        receiver.receive(entity=entity)

        except InvalidStateException as ex:
            self.__logger.error(
                "Receiver queue item couldn't be handled",
                extra={
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )

    # -----------------------------------------------------------------------------

    def is_empty(self) -> bool:
        """Check if all messages were handled"""
        return self.__queue.empty()

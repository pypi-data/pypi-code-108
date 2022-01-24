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
Shelly connector clients module CoAP client
"""

# Python base dependencies
import select
import struct
from socket import (  # pylint: disable=no-name-in-module
    AF_INET,
    INADDR_ANY,
    IP_ADD_MEMBERSHIP,
    IPPROTO_IP,
    IPPROTO_UDP,
    SHUT_RDWR,
    SO_REUSEADDR,
    SOCK_DGRAM,
    SOL_SOCKET,
    error,
    inet_aton,
    socket,
)
from threading import Thread
from typing import Optional

# Library libs
from fastybird_shelly_connector.clients.base import IClient
from fastybird_shelly_connector.logger import Logger
from fastybird_shelly_connector.receivers.receiver import Receiver
from fastybird_shelly_connector.registry.records import SensorRecord
from fastybird_shelly_connector.types import ClientMessageType, ClientType
from fastybird_shelly_connector.utilities.helpers import Timer


class CoapClient(IClient, Thread):
    """
    CoAP client

    @package        FastyBird:ShellyConnector!
    @module         clients/coap

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __stopped: bool = True

    __socket: Optional[socket] = None

    __receiver: Receiver

    __logger: Logger

    __timer: Optional[Timer] = None

    __BIND_IP: str = "0.0.0.0"
    __COAP_IP: str = "224.0.1.187"
    __COAP_PORT: int = 5683

    __DISCOVERY_INTERVAL: int = 60

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        receiver: Receiver,
        logger: Logger,
    ) -> None:
        Thread.__init__(self, name="CoAP server thread", daemon=True)

        self.__receiver = receiver

        self.__logger = logger

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> ClientType:
        """Client type"""
        return ClientType.COAP

    # -----------------------------------------------------------------------------

    def start(self) -> None:
        """Start communication"""
        self.__create_client()

        self.__timer = Timer(interval=self.__DISCOVERY_INTERVAL)

        self.__stopped = False

        if not Thread.is_alive(self):
            Thread.start(self)

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Stop communication"""
        self.__timer = None

        self.__stopped = True

        if self.__socket is not None:
            try:
                self.__socket.shutdown(SHUT_RDWR)
                self.__socket = None

            except error:
                pass

    # -----------------------------------------------------------------------------

    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self.__socket is not None

    # -----------------------------------------------------------------------------

    def discover(self) -> None:
        """Send discover command"""
        if self.__socket is not None:
            self.__logger.debug(
                "Sending CoAP discover UDP",
                extra={
                    "client": {
                        "type": ClientType.COAP.value,
                    },
                },
            )

            msg = bytes(b"\x50\x01\x00\x0A\xb3cit\x01d\xFF")

            self.__socket.sendto(msg, (self.__COAP_IP, self.__COAP_PORT))

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Process CoAP requests"""

    # -----------------------------------------------------------------------------

    def write_sensor(self, sensor_record: SensorRecord) -> None:
        """Write value to device sensor"""

    # -----------------------------------------------------------------------------

    def run(self) -> None:
        """Process CoAP requests"""
        if self.__socket is None:
            return

        while not self.__stopped:
            if self.__timer is not None and self.__timer.check():
                self.discover()

            try:
                self.__handle_request()

            except Exception as ex:  # pylint: disable=broad-except
                self.__logger.error(
                    "Error receiving CoAP UDP",
                    extra={
                        "client": {
                            "type": ClientType.COAP.value,
                        },
                        "exception": {
                            "message": str(ex),
                            "code": type(ex).__name__,
                        },
                    },
                )

    # -----------------------------------------------------------------------------

    def __create_client(self) -> None:
        """Create CoAP socket client"""
        if self.__socket is None:
            try:
                self.__socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
                self.__socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                self.__socket.bind((self.__BIND_IP, self.__COAP_PORT))

                mreq = struct.pack("=4sl", inet_aton(self.__COAP_IP), INADDR_ANY)  # pylint: disable=no-member

                self.__socket.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)

            except Exception as ex:  # pylint: disable=broad-except
                self.__logger.error(
                    "CoAP client can't be created",
                    extra={
                        "client": {
                            "type": ClientType.COAP.value,
                        },
                        "exception": {
                            "message": str(ex),
                            "code": type(ex).__name__,
                        },
                    },
                )

    # -----------------------------------------------------------------------------

    def __handle_request(  # pylint: disable=too-many-statements,too-many-branches,too-many-locals
        self,
    ) -> None:
        r_list, _, __ = select.select(  # pylint: disable=c-extension-no-member
            [self.__socket],
            [],
            [],
            0.1,
        )

        for ready in r_list:
            if isinstance(ready, socket):
                data_tmp, address = ready.recvfrom(1024)

                data = bytearray(data_tmp)

                if len(data) < 10:
                    return

                ip_address = address[0]

                pos = 0

                # Receive messages with ip from proxy
                if data[0] == 112 and data[1] == 114 and data[2] == 120 and data[3] == 121:
                    pos = 8

                byte = data[pos]
                tkl = byte & 0x0F

                # ver = byte >> 6
                # typex = (byte >> 4) & 0x3
                # token_length = byte & 0xF

                code = data[pos + 1]
                # message_id = 256 * data[2] + data[3]

                pos = pos + 4 + tkl

                if code in (30, 69):
                    byte = data[pos]
                    tot_delta = 0

                    device_type = ""
                    device_identifier = ""

                    while byte != 0xFF:
                        delta = byte >> 4
                        length = byte & 0x0F

                        if delta == 13:
                            pos = pos + 1
                            delta = data[pos] + 13

                        elif delta == 14:
                            pos = pos + 2
                            delta = data[pos - 1] * 256 + data[pos] + 269

                        tot_delta = tot_delta + delta

                        if length == 13:
                            pos = pos + 1
                            length = data[pos] + 13

                        elif length == 14:
                            pos = pos + 2
                            length = data[pos - 1] * 256 + data[pos] + 269

                        value = data[pos + 1 : pos + length]
                        pos = pos + length + 1

                        if tot_delta == 3332:
                            device_type, device_identifier, _ = str(value, "cp1252").split("#", 2)

                        byte = data[pos]

                    try:
                        payload = str(data[pos + 1 :], "cp1252")

                    except Exception as ex:  # pylint: disable=broad-except
                        self.__logger.error(
                            "Can't convert received payload",
                            extra={
                                "client": {
                                    "type": ClientType.COAP.value,
                                },
                                "exception": {
                                    "message": str(ex),
                                    "code": type(ex).__name__,
                                },
                            },
                        )
                        return

                    if payload:  # Fix for DW2 payload error
                        payload = payload.replace(",,", ",").replace("][", "],[")

                    self.__logger.debug(
                        "CoAP Code: %d, Type: %s, Id: %s, Payload: %s",
                        code,
                        device_type,
                        device_identifier,
                        payload.replace(" ", ""),
                        extra={
                            "client": {
                                "type": ClientType.COAP.value,
                            },
                            "device": {
                                "identifier": device_identifier,
                                "ip_address": ip_address,
                                "type": device_type,
                            },
                        },
                    )

                    if code == 30:
                        self.__receiver.on_coap_message(
                            device_identifier=device_identifier.lower(),
                            device_type=device_type.lower(),
                            device_ip_address=ip_address,
                            message_payload=payload,
                            message_type=ClientMessageType.COAP_STATUS,
                        )

                    elif code == 69:
                        self.__receiver.on_coap_message(
                            device_identifier=device_identifier.lower(),
                            device_type=device_type.lower(),
                            device_ip_address=ip_address,
                            message_payload=payload,
                            message_type=ClientMessageType.COAP_DESCRIPTION,
                        )

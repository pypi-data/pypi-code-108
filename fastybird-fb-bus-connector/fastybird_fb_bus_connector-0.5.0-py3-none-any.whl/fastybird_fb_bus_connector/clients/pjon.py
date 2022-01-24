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
FastyBird BUS connector clients module PJON client
"""

# Python base dependencies
import time
from typing import Dict, List, Optional

# Library dependencies
import pjon_cython as pjon
from kink import inject

# Library libs
from fastybird_fb_bus_connector.clients.base import IClient
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.receivers.receiver import Receiver
from fastybird_fb_bus_connector.types import Packet, PacketContent, ProtocolVersion
from fastybird_fb_bus_connector.utilities.helpers import PacketsHelpers


@inject(alias=IClient)
class PjonClient(IClient, pjon.ThroughSerialAsync):  # pylint: disable=no-member
    """
    PJON client

    @package        FastyBird:FbBusConnector!
    @module         clients/pjon

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __version: ProtocolVersion

    __receiver: Receiver

    __logger: Logger

    __MASTER_ADDRESS: int = 254
    __SERIAL_BAUD_RATE: int = 38400
    __SERIAL_INTERFACE: str = "/dev/ttyAMA0"

    # -----------------------------------------------------------------------------

    @inject
    def __init__(  # pylint: disable=too-many-arguments
        self,
        client_address: Optional[int],
        client_baud_rate: Optional[int],
        client_interface: Optional[str],
        protocol_version: ProtocolVersion,
        receiver: Receiver,
        logger: Logger,
    ) -> None:
        pjon.ThroughSerialAsync.__init__(  # pylint: disable=no-member
            self,
            client_address if client_address is not None else self.__MASTER_ADDRESS,
            (client_interface if client_interface is not None else self.__SERIAL_INTERFACE).encode("utf-8"),
            client_baud_rate if client_baud_rate is not None else self.__SERIAL_BAUD_RATE,
        )

        self.set_synchronous_acknowledge(False)
        self.set_asynchronous_acknowledge(False)

        self.__version = protocol_version

        self.__receiver = receiver

        self.__logger = logger

    # -----------------------------------------------------------------------------

    @property
    def version(self) -> ProtocolVersion:
        """Protocol version used by client"""
        return self.__version

    # -----------------------------------------------------------------------------

    def broadcast_packet(self, payload: List[int], waiting_time: float = 0.0) -> bool:
        """Broadcast packet to all devices"""
        return self.send_packet(pjon.PJON_BROADCAST, payload, waiting_time)  # pylint: disable=no-member

    # -----------------------------------------------------------------------------

    def send_packet(self, address: int, payload: List[int], waiting_time: float = 0.0) -> bool:
        """Send packet to specific device address"""
        crc16 = self.__crc16(bytes(payload))

        payload.append(crc16 >> 8)
        payload.append(crc16 & 0xFF)

        # Be sure to set the null terminator!!!
        payload.append(PacketContent.TERMINATOR.value)

        self.send(address, bytes(payload))

        # if result != pjon.PJON_ACK:
        #     if result == pjon.PJON_BUSY:
        #         self.__logger.warning(
        #             "Sending packet: %s for device: %s failed, bus is busy",
        #             PacketsHelpers.get_packet_name(int(payload[0])),
        #             address
        #         )
        #
        #     elif result == pjon.PJON_FAIL:
        #         self.__logger.warning(
        #             "Sending packet: %s for device: %s failed"
        #             PacketsHelpers.get_packet_name(int(payload[0])),
        #             address
        #         )
        #
        #     else:
        #         self.__logger.warning(
        #             "Sending packet: %s for device: %s failed, unknown error"
        #             PacketsHelpers.get_packet_name(int(payload[0])),
        #             address
        #         )
        #
        #     return False

        if address == pjon.PJON_BROADCAST:  # pylint: disable=no-member
            self.__logger.debug(
                f"Successfully sent broadcast packet: {PacketsHelpers.get_packet_name(Packet(payload[1]))}",
                extra={
                    "device": {
                        "address": address,
                    },
                },
            )

        else:
            self.__logger.debug(
                f"Successfully sent packet: "
                f"{PacketsHelpers.get_packet_name(Packet(payload[1]))} for device with address: {address}",
                extra={
                    "device": {
                        "address": address,
                    },
                },
            )

        if waiting_time > 0:
            # Store start timestamp
            current_time = time.time()

            while (time.time() - current_time) <= waiting_time:
                _, send_packet_result = self.loop()

                if send_packet_result == pjon.PJON_ACK:  # pylint: disable=no-member
                    return True

            return False

        return True

    # -----------------------------------------------------------------------------

    def handle(self) -> int:
        """Process client"""
        try:
            result = self.loop()

            return int(result[0])

        except pjon.PJON_Connection_Lost:  # pylint: disable=no-member
            self.__logger.warning("Connection with device was lost")

        except pjon.PJON_Packets_Buffer_Full:  # pylint: disable=no-member
            self.__logger.warning("Buffer is full")

        except pjon.PJON_Content_Too_Long:  # pylint: disable=no-member
            self.__logger.warning("Content is long")

        return 0

    # -----------------------------------------------------------------------------

    def receive(self, received_payload: bytes, length: int, packet_info: Dict) -> None:
        """Process received message by clients"""
        sender_address: Optional[int] = None

        try:
            # Get sender address from header
            sender_address = int(str(packet_info.get("sender_id")))

        except KeyError:
            # Sender address is not present in header
            pass

        raw_payload: List[int] = []

        for char in bytearray(received_payload):
            raw_payload.append(int(char))

        if ProtocolVersion.has_value(int(raw_payload[0])) is False:
            self.__logger.warning(
                "Received unknown protocol version",
                extra={
                    "packet": {
                        "protocol_version": int(raw_payload[0]),
                    },
                },
            )

            return

        if Packet.has_value(int(raw_payload[1])) is False:
            self.__logger.warning(
                "Received unknown packet",
                extra={
                    "packet": {
                        "type": int(raw_payload[1]),
                    },
                },
            )

            return

        calculated_crc = self.__crc16(bytes(raw_payload[0 : (length - 3)]))
        in_packet_crc = (int(raw_payload[length - 3]) << 8) | int(raw_payload[length - 2])

        if calculated_crc != in_packet_crc:
            self.__logger.warning(f"Invalid CRC check: {calculated_crc} vs {in_packet_crc}")

            return

        if raw_payload[-1] != PacketContent.TERMINATOR.value:
            self.__logger.warning("Missing packet terminator")

            return

        payload = raw_payload[0 : (length - 3)]

        # Get packet identifier from payload
        packet_id = Packet(int(payload[1]))

        self.__logger.debug(
            "Received packet: %s for device with address: %s",
            PacketsHelpers.get_packet_name(packet_id),
            sender_address,
        )

        self.__receiver.on_message(
            payload=bytearray(payload),
            length=len(payload),
            address=sender_address,
            protocol_version=self.version,
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def __crc16(calculate_data: bytes, poly: int = 0x8408) -> int:
        """CRC-16-CCITT Algorithm"""
        data = bytearray(calculate_data)

        crc = 0xFFFF

        for byte in data:
            cur_byte = 0xFF & byte

            for _ in range(0, 8):
                if (crc & 0x0001) ^ (cur_byte & 0x0001):
                    crc = (crc >> 1) ^ poly

                else:
                    crc >>= 1

                cur_byte >>= 1

        crc = ~crc & 0xFFFF
        crc = (crc << 8) | ((crc >> 8) & 0xFF)

        return crc & 0xFFFF

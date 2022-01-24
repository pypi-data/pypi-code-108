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
FastyBird BUS connector api module validator for API v1
"""

# Library libs
from fastybird_fb_bus_connector.types import Packet, PairingResponse, ProtocolVersion


class V1Validator:
    """
    BUS payload validator

    @package        FastyBird:FbBusConnector!
    @module         api/v1validator

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @property
    def version(self) -> ProtocolVersion:
        """Validator protocol version number"""
        return ProtocolVersion.V1

    # -----------------------------------------------------------------------------

    def validate(self, payload: bytearray) -> bool:
        """Validate topic against sets of regular expressions"""
        if not self.validate_version(payload=payload):
            return False

        if self.validate_discover_device(payload=payload):
            if (
                self.validate_pair_command_search_devices(payload=payload)
                or self.validate_pair_command_provide_register_structure(payload=payload)
                or self.validate_pair_command_pairing_finished(payload=payload)
            ):
                return True

        if (
            self.validate_read_single_register(payload=payload)  # pylint: disable=too-many-boolean-expressions
            or self.validate_read_multiple_registers(payload=payload)
            or self.validate_write_single_register(payload=payload)
            or self.validate_write_multiple_registers(payload=payload)
            or self.validate_report_single_register(payload=payload)
            or self.validate_read_device_state(payload=payload)
            or self.validate_write_device_state(payload=payload)
            or self.validate_report_device_state(payload=payload)
            or self.validate_pong_response(payload=payload)
        ):
            return True

        return False

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_version(payload: bytearray) -> bool:
        """Validate payload against version definition"""
        return ProtocolVersion(int(payload[0])) == ProtocolVersion.V1

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_read_single_register(payload: bytearray) -> bool:
        """Validate payload against read single register packet structure"""
        return Packet(int(payload[1])) == Packet.READ_SINGLE_REGISTER

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_read_multiple_registers(payload: bytearray) -> bool:
        """Validate payload against read multiple registers packet structure"""
        return Packet(int(payload[1])) == Packet.READ_MULTIPLE_REGISTERS

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_write_single_register(payload: bytearray) -> bool:
        """Validate payload against write single register packet structure"""
        return Packet(int(payload[1])) == Packet.WRITE_SINGLE_REGISTER

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_write_multiple_registers(payload: bytearray) -> bool:
        """Validate payload against write multiple registers packet structure"""
        return Packet(int(payload[1])) == Packet.WRITE_MULTIPLE_REGISTERS

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_report_single_register(payload: bytearray) -> bool:
        """Validate payload against report single register packet structure"""
        return Packet(int(payload[1])) == Packet.REPORT_SINGLE_REGISTER

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_read_device_state(payload: bytearray) -> bool:
        """Validate payload against get device state packet structure"""
        return Packet(int(payload[1])) == Packet.READ_STATE

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_write_device_state(payload: bytearray) -> bool:
        """Validate payload against set device state packet structure"""
        return Packet(int(payload[1])) == Packet.WRITE_STATE

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_report_device_state(payload: bytearray) -> bool:
        """Validate payload against report device state packet structure"""
        return Packet(int(payload[1])) == Packet.REPORT_STATE

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_pong_response(payload: bytearray) -> bool:
        """Validate payload against pong response packet structure"""
        return Packet(int(payload[1])) == Packet.PONG

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_discover_device(payload: bytearray) -> bool:
        """Validate payload against pair device packet structure"""
        return Packet(int(payload[1])) == Packet.DISCOVER

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_pair_command_search_devices(payload: bytearray) -> bool:
        """Validate payload against search devices response packet structure"""
        return PairingResponse(int(payload[2])) == PairingResponse.SEARCH

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_pair_command_provide_register_structure(payload: bytearray) -> bool:
        """Validate payload against pair device command provide register structure packet structure"""
        return PairingResponse(int(payload[2])) == PairingResponse.PROVIDE_REGISTER_STRUCTURE

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_pair_command_pairing_finished(payload: bytearray) -> bool:
        """Validate payload against pair device command pairing finished packet structure"""
        return PairingResponse(int(payload[2])) == PairingResponse.PAIRING_FINISHED

#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Communication protocol for modbus TCP ports. Makes use of the
`pymodbus <https://pymodbus.readthedocs.io/en/latest/>`_ library.
"""

import logging
from ipaddress import IPv4Address, IPv6Address
from typing import List, Union

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Defaults as ModbusDefaults
from pymodbus.exceptions import ConnectionException

from hvl_ccb.utils.validation import validate_and_resolve_host, validate_tcp_port
from .base import CommunicationProtocol, CommunicationException
from ..configuration import configdataclass

logger = logging.getLogger(__name__)


class ModbusTcpConnectionFailedException(ConnectionException, CommunicationException):
    """
    Exception raised when the connection failed.
    """

    pass


@configdataclass
class ModbusTcpCommunicationConfig:
    """
    Configuration dataclass for :class:`ModbusTcpCommunication`.
    """
    # Host is the IP address or hostname of the connected device.
    host: Union[str, IPv4Address, IPv6Address]

    # Unit number to be used when connecting with Modbus/TCP. Typically this is used
    # when connecting to a relay having Modbus/RTU-connected devices.
    unit: int

    # TCP port
    port: int = ModbusDefaults.Port

    def clean_values(self):
        self.force_value("host", validate_and_resolve_host(self.host, logger))
        validate_tcp_port(self.port, logger)


class ModbusTcpCommunication(CommunicationProtocol):
    """
    Implements the Communication Protocol for modbus TCP.
    """

    def __init__(self, configuration):
        """Constructor for modbus"""
        super().__init__(configuration)

        # create the modbus port specified in the configuration
        logger.debug(
            f"Create ModbusTcpClient with host: {self.config.host}, "
            f"Port: {self.config.port}, Unit: {self.config.unit}"
        )
        self.client = ModbusTcpClient(
            self.config.host, port=self.config.port, unit=self.config.unit
        )

    @staticmethod
    def config_cls():
        return ModbusTcpCommunicationConfig

    def open(self) -> None:
        """
        Open the Modbus TCP connection.

        :raises ModbusTcpConnectionFailedException: if the connection fails.
        """

        # open the port
        logger.debug("Open Modbus TCP Port.")

        with self.access_lock:
            if not self.client.connect():
                raise ModbusTcpConnectionFailedException

    def close(self):
        """
        Close the Modbus TCP connection.
        """

        # close the port
        logger.debug("Close Modbus TCP Port.")

        with self.access_lock:
            self.client.close()

    def write_registers(self, address: int, values: Union[List[int], int]):
        """
        Write values from the specified address forward.

        :param address: address of the first register
        :param values: list with all values
        """

        logger.debug(f"Write registers {address} with values {values}")

        with self.access_lock:
            try:
                self.client.write_registers(
                    address=address, values=values, unit=self.config.unit
                )
            except ConnectionException as e:
                logger.error(str(e), exc_info=e)
                raise ModbusTcpConnectionFailedException from e

    def read_holding_registers(self, address: int, count: int) -> List[int]:
        """
        Read specified number of register starting with given address and return
        the values from each register.

        :param address: address of the first register
        :param count: count of registers to read
        :return: list of `int` values
        """

        logger.debug(f"Read holding registers {address} with count {count}.")

        with self.access_lock:
            try:
                registers = self.client.read_holding_registers(
                    address=address, count=count
                ).registers
            except ConnectionException as e:
                logger.error(str(e), exc_info=e)
                raise ModbusTcpConnectionFailedException from e

        logger.debug(f"Returned holding registers {address}: {registers}")

        return registers

    def read_input_registers(self, address: int, count: int) -> List[int]:
        """
        Read specified number of register starting with given address and return
        the values from each register in a list.

        :param address: address of the first register
        :param count: count of registers to read
        :return: list of `int` values
        """

        logger.debug(f"Read input registers {address} with count {count}.")

        with self.access_lock:
            try:
                registers = self.client.read_input_registers(
                    address=address, count=count
                ).registers
            except ConnectionException as e:
                logger.error(str(e), exc_info=e)
                raise ModbusTcpConnectionFailedException from e

        logger.debug(f"Returned input registers {address}: {registers}")

        return registers

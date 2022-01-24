#  Copyright (c) 2021-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Communication and auxiliary classes for Technix
"""

import logging
from abc import ABC
from typing import Union, Type, Optional, NamedTuple

from hvl_ccb import configdataclass
from hvl_ccb.comm import (
    SerialCommunicationConfig,
    SerialCommunication,
    TelnetCommunicationConfig,
    TelnetCommunication,
)
from hvl_ccb.comm.base import SyncCommunicationProtocolConfig, SyncCommunicationProtocol
from hvl_ccb.dev.base import DeviceException
from hvl_ccb.utils.enum import ValueEnum
from hvl_ccb.utils.typing import Number

logger = logging.getLogger(__name__)


class TechnixError(DeviceException):
    """
    Technix related errors.
    """


class TechnixFaultError(TechnixError):
    """
    Raised when the fault flag was detected while the interlock is closed
    """


@configdataclass
class _TechnixCommunicationConfig(SyncCommunicationProtocolConfig):
    #: The terminator is CR
    terminator: bytes = b"\r"


class _TechnixCommunication(SyncCommunicationProtocol, ABC):
    """
    Generic communication class for Technix, which can be implemented via
    `TechnixSerialCommunication` or `TechnixTelnetCommunication`
    """

    def query(self, command: str) -> str:
        """
        Send a command to the interface and handle the status message.
        Possibly raises an exception.

        :param command: Command to send
        :raises TechnixError: if the connection is broken
        :return: Answer from the interface
        """

        with self.access_lock:
            logger.debug(f"TechnixCommunication, send: '{command}'")
            answer: Optional[str] = super().query(command)  # string or None
            logger.debug(f"TechnixCommunication, receive: '{answer}'")
            if answer is None:
                msg = f"TechnixCommunication did get no answer on command: '{command}'"
                logger.error(msg)
                raise TechnixError(msg)
            return answer


@configdataclass
class TechnixSerialCommunicationConfig(
    _TechnixCommunicationConfig, SerialCommunicationConfig
):
    """
    Configuration for the serial communication for Technix
    """

    pass


class TechnixSerialCommunication(_TechnixCommunication, SerialCommunication):
    """
    Serial communication for Technix
    """

    @staticmethod
    def config_cls():
        return TechnixSerialCommunicationConfig


@configdataclass
class TechnixTelnetCommunicationConfig(
    _TechnixCommunicationConfig, TelnetCommunicationConfig
):
    """
    Configuration for the telnet communication for Technix
    """

    #: Port at which Technix is listening
    port: int = 4660


class TechnixTelnetCommunication(TelnetCommunication, _TechnixCommunication):
    """
    Telnet communication for Technix
    """

    @staticmethod
    def config_cls():
        return TechnixTelnetCommunicationConfig


_TechnixCommunicationClasses = Union[
    Type[TechnixSerialCommunication], Type[TechnixTelnetCommunication]
]


class _SetRegisters(ValueEnum):
    VOLTAGE = "d1"  # Output Voltage programming
    CURRENT = "d2"  # Output Current programming
    HVON = "P5"  # HV on
    HVOFF = "P6"  # HV off
    LOCAL = "P7"  # Local/remote mode
    INHIBIT = "P8"  # Inhibit


class _GetRegisters(ValueEnum):
    VOLTAGE = "a1"  # Output Voltage Monitor
    CURRENT = "a2"  # Output Current Monitor
    STATUS = "E"  # Image of the power supply logical status


class _Status(NamedTuple):
    """
    Container for the different statuses of the device. It can also handle the most
    recent reading of the voltage and current at the output.
    """

    inhibit: bool
    remote: bool
    hv_off: bool
    hv_on: bool
    output: bool
    open_interlock: bool
    fault: bool
    voltage_regulation: bool

    voltage: Optional[Number]
    current: Optional[Number]

#  Copyright (c) 2021-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Module containing base device and communication classes and enums.

Communication with device is performed via its ethernet port and a Telnet connection.
"""
import logging
from typing import Optional, NamedTuple

from hvl_ccb.comm import TelnetCommunication, TelnetCommunicationConfig
from hvl_ccb.comm.base import SyncCommunicationProtocolConfig, SyncCommunicationProtocol
from hvl_ccb.configuration import configdataclass
from hvl_ccb.dev.base import DeviceException
from hvl_ccb.utils.enum import ValueEnum
from hvl_ccb.utils.typing import Number

logger = logging.getLogger(__name__)


class T560Error(DeviceException):
    """
    T560 related errors.
    """


class T560Communication(SyncCommunicationProtocol, TelnetCommunication):
    """
    Communication class for T560. It uses a TelnetCommunication with the
    SyncCommunicationProtocol
    """

    @staticmethod
    def config_cls():
        return T560CommunicationConfig

    def query(self, command: str) -> str:
        """
        Send a command to the device and handle the response.

        For device setting queries, response will be 'OK' if successful,
        or '??' if setting cannot be carried out, raising an error.

        :param command: Command string to be sent
        :raises T560Error: if no response is received,
            or if the device responds with an error message.
        :return: Response from the device.
        """

        with self.access_lock:
            logger.debug(f"T560Communication, send: '{command}'")
            response: Optional[str] = super().query(command)
            logger.debug(f"T560Communication, receive: '{response}'")
            if response is None or response == "??":
                msg = f"T560Communication did not receive a valid response to {command}"
                logger.error(msg)
                raise T560Error(msg)
        return response


@configdataclass
class T560CommunicationConfig(
    SyncCommunicationProtocolConfig, TelnetCommunicationConfig
):
    # The line terminator for a command sent to the device is CR
    terminator: bytes = b"\r"
    port: int = 2000


class TriggerMode(ValueEnum):
    """
    Available T560 trigger modes
    """

    OFF = "OFF"
    COMMAND = "REM"
    EXT_RISING_EDGE = "POS"
    EXT_FALLING_EDGE = "NEG"
    INT_SYNTHESIZER = "SYN"


class GateMode(ValueEnum):
    """
    Available T560 gate modes
    """

    OFF = "OFF"
    OUTPUT = "OUT"
    INPUT = "INP"


class AutoInstallMode(ValueEnum):
    """
    Modes for installing configuration settings to the device.
    """

    OFF = 0
    INSTALL = 1
    QUEUE = 2


class Polarity(ValueEnum):
    """
    Possible channel polarity states
    """

    ACTIVE_HIGH = "POS"
    ACTIVE_LOW = "NEG"


class _ChannelStatus(NamedTuple):
    polarity: Polarity
    enabled: bool
    delay: Number
    width: Number


class _TriggerStatus(NamedTuple):
    mode: TriggerMode
    level: Number
    frequency: Number


class _GateStatus(NamedTuple):
    mode: GateMode
    polarity: Polarity

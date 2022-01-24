#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Communication protocol for serial ports. Makes use of the `pySerial
<https://pythonhosted.org/pyserial/index.html>`_ library.
"""

import logging
import warnings
from typing import Optional, Union, cast

# Note: PyCharm does not recognize the dependency correctly, it is added as pyserial.
import serial

from .base import (
    AsyncCommunicationProtocolConfig,
    AsyncCommunicationProtocol,
    CommunicationException,
)
from ..configuration import configdataclass, ConfigurationValueWarning
from ..utils.enum import ValueEnum, unique
from ..utils.typing import Number

logger = logging.getLogger(__name__)


class SerialCommunicationIOError(IOError, CommunicationException):
    """Serial communication related I/O errors."""


@unique
class SerialCommunicationParity(ValueEnum):
    """
    Serial communication parity.
    """

    EVEN = serial.PARITY_EVEN
    MARK = serial.PARITY_MARK
    NAMES = serial.PARITY_NAMES
    NONE = serial.PARITY_NONE
    ODD = serial.PARITY_ODD
    SPACE = serial.PARITY_SPACE


@unique
class SerialCommunicationStopbits(ValueEnum):
    """
    Serial communication stopbits.
    """

    ONE = serial.STOPBITS_ONE
    ONE_POINT_FIVE = serial.STOPBITS_ONE_POINT_FIVE
    TWO = serial.STOPBITS_TWO


@unique
class SerialCommunicationBytesize(ValueEnum):
    """
    Serial communication bytesize.
    """

    FIVEBITS = serial.FIVEBITS
    SIXBITS = serial.SIXBITS
    SEVENBITS = serial.SEVENBITS
    EIGHTBITS = serial.EIGHTBITS


@configdataclass
class SerialCommunicationConfig(AsyncCommunicationProtocolConfig):
    """
    Configuration dataclass for :class:`SerialCommunication`.
    """

    Parity = SerialCommunicationParity
    Stopbits = SerialCommunicationStopbits
    Bytesize = SerialCommunicationBytesize

    #: Port is a string referring to a COM-port (e.g. ``'COM3'``) or a URL.
    #: The full list of capabilities is found `on the pyserial documentation
    #: <https://pythonhosted.org/pyserial/url_handlers.html>`_.
    port: Optional[str] = None

    #: Baudrate of the serial port
    baudrate: int = 9600

    #: Parity to be used for the connection.
    parity: Union[str, SerialCommunicationParity] = Parity.NONE

    #: Stopbits setting, can be 1, 1.5 or 2.
    stopbits: Union[Number, SerialCommunicationStopbits] = Stopbits.ONE

    #: Size of a byte, 5 to 8
    bytesize: Union[int, SerialCommunicationBytesize] = Bytesize.EIGHTBITS

    #: Timeout in seconds for the serial port
    timeout: Number = 2

    def clean_values(self):

        super().clean_values()

        if not isinstance(self.parity, SerialCommunicationParity):
            self.force_value("parity", SerialCommunicationParity(self.parity))

        if not isinstance(self.stopbits, SerialCommunicationStopbits):
            self.force_value("stopbits", SerialCommunicationStopbits(self.stopbits))

        if not isinstance(self.bytesize, SerialCommunicationBytesize):
            self.force_value("bytesize", SerialCommunicationBytesize(self.bytesize))

        if self.timeout < 0:
            raise ValueError("Timeout has to be >= 0.")
        if self.timeout < 1:  # min. viable threshold as tested w/ Arduino Nano board
            warnings.warn(
                "Setting a too low timeout for a serial connection communication may "
                "lead to random errors during a communication with a device.",
                category=ConfigurationValueWarning,
            )

    def create_serial_port(self) -> serial.Serial:
        """
        Create a serial port instance according to specification in this configuration

        :return: Closed serial port instance
        """

        ser = serial.serial_for_url(self.port, do_not_open=True)
        assert not ser.is_open

        ser.baudrate = self.baudrate
        ser.parity = cast(SerialCommunicationParity, self.parity).value
        ser.stopbits = cast(SerialCommunicationStopbits, self.stopbits).value
        ser.bytesize = cast(SerialCommunicationBytesize, self.bytesize).value
        ser.timeout = self.timeout

        return ser

    def terminator_str(self) -> str:
        return self.terminator.decode()


class SerialCommunication(AsyncCommunicationProtocol):
    """
    Implements the Communication Protocol for serial ports.
    """

    def __init__(self, configuration):
        """
        Constructor for SerialCommunication.
        """

        super().__init__(configuration)

        self._serial_port = self.config.create_serial_port()

    @staticmethod
    def config_cls():
        return SerialCommunicationConfig

    def open(self):
        """
        Open the serial connection.

        :raises SerialCommunicationIOError: when communication port cannot be opened.
        """

        # open the port
        with self.access_lock:
            try:
                self._serial_port.open()
            except serial.SerialException as exc:
                # ignore when port is already open
                logger.error(str(exc), exc_info=exc)
                if str(exc) != "Port is already open.":
                    raise SerialCommunicationIOError from exc

    def close(self):
        """
        Close the serial connection.
        """

        # close the port
        with self.access_lock:
            self._serial_port.close()

    @property
    def is_open(self) -> bool:
        """
        Flag indicating if the serial port is open.

        :return: `True` if the serial port is open, otherwise `False`
        """
        return self._serial_port.is_open

    def read_bytes(self) -> bytes:
        """
        Read the bytes from the serial port till the terminator is found.
        The input buffer may hold additional lines afterwards.

        This method uses `self.access_lock` to ensure thread-safety.

        :return: Bytes read from the serial port; `b''` if there was nothing to read.
        :raises SerialCommunicationIOError: when communication port is not opened
        """

        with self.access_lock:
            try:
                return self._serial_port.read_until(self.config.terminator)
            except serial.SerialException as exc:
                logger.error(str(exc), exc_info=exc)
                raise SerialCommunicationIOError from exc

    def write_bytes(self, data: bytes) -> int:
        """
        Write bytes to the serial port.

        This method uses `self.access_lock` to ensure thread-safety.

        :param data: data to write to the serial port
        :return: number of bytes written
        :raises SerialCommunicationIOError: when communication port is not opened
        """

        with self.access_lock:
            try:
                return self._serial_port.write(data)
            except serial.SerialException as exc:
                logger.error(str(exc), exc_info=exc)
                raise SerialCommunicationIOError from exc

    def read_single_bytes(self, size: int = 1) -> bytes:
        """
        Read the specified number of bytes from the serial port.
        The input buffer may hold additional data afterwards.

        :return: Bytes read from the serial port; `b''` if there was nothing to read.
        """

        with self.access_lock:
            try:
                return self._serial_port.read(size)
            except serial.SerialException as exc:
                logger.error(str(exc), exc_info=exc)
                raise SerialCommunicationIOError from exc

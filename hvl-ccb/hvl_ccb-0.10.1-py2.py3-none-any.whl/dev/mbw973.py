#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device class for controlling a MBW 973 SF6 Analyzer over a serial connection.

The MBW 973 is a gas analyzer designed for gas insulated switchgear and measures
humidity, SF6 purity and SO2 contamination in one go.
Manufacturer homepage: https://www.mbw.ch/products/sf6-gas-analysis/973-sf6-analyzer/
"""

import logging
from typing import Dict, Type, Union

from .base import SingleCommDevice, DeviceException
from .utils import Poller
from ..comm import SerialCommunication, SerialCommunicationConfig
from ..comm.serial import (
    SerialCommunicationParity,
    SerialCommunicationStopbits,
    SerialCommunicationBytesize,
)
from ..configuration import configdataclass
from ..utils.typing import Number

logger = logging.getLogger(__name__)


class MBW973Error(DeviceException):
    """
    General error with the MBW973 dew point mirror device.
    """

    pass


class MBW973ControlRunningException(MBW973Error):
    """
    Error indicating there is still a measurement running, and a new one cannot be
    started.
    """

    pass


class MBW973PumpRunningException(MBW973Error):
    """
    Error indicating the pump of the dew point mirror is still recovering gas,
    unable to start a new measurement.
    """

    pass


@configdataclass
class MBW973SerialCommunicationConfig(SerialCommunicationConfig):
    #: Baudrate for MBW973 is 9600 baud
    baudrate: int = 9600

    #: MBW973 does not use parity
    parity: Union[str, SerialCommunicationParity] = SerialCommunicationParity.NONE

    #: MBW973 does use one stop bit
    stopbits: Union[int, SerialCommunicationStopbits] = SerialCommunicationStopbits.ONE

    #: One byte is eight bits long
    bytesize: Union[
        int, SerialCommunicationBytesize
    ] = SerialCommunicationBytesize.EIGHTBITS

    #: The terminator is only CR
    terminator: bytes = b"\r"

    #: use 3 seconds timeout as default
    timeout: Number = 3


class MBW973SerialCommunication(SerialCommunication):
    """
    Specific communication protocol implementation for the MBW973 dew point mirror.
    Already predefines device-specific protocol parameters in config.
    """

    @staticmethod
    def config_cls():
        return MBW973SerialCommunicationConfig


@configdataclass
class MBW973Config:
    """
    Device configuration dataclass for MBW973.
    """

    #: Polling period for `is_done` status queries [in seconds].
    polling_interval: Number = 2

    def clean_values(self):
        if self.polling_interval <= 0:
            raise ValueError("Polling interval needs to be positive.")


class MBW973(SingleCommDevice):
    """
    MBW 973 dew point mirror device class.
    """

    def __init__(self, com, dev_config=None):

        # Call superclass constructor
        super().__init__(com, dev_config)

        # polling status
        self.status_poller = Poller(
            self.is_done,
            polling_delay_sec=self.config.polling_interval,
            polling_interval_sec=self.config.polling_interval,
        )

        # is done with dew point = True, new measurement sample required and
        # not ready yet = False
        self.is_done_with_measurements = True

        # dict telling what measurement options are selected
        self.measurement_options = {
            "dewpoint": True,
            "SF6_Vol": False,
        }

        self.last_measurement_values = {}

    @staticmethod
    def default_com_cls():
        return MBW973SerialCommunication

    @staticmethod
    def config_cls():
        return MBW973Config

    def start(self) -> None:
        """
        Start this device. Opens the communication protocol and retrieves the
        set measurement options from the device.

        :raises SerialCommunicationIOError: when communication port cannot be opened.
        """

        logger.info("Starting device " + str(self))
        super().start()

        # check test options
        self.write("HumidityTest?")
        self.measurement_options["dewpoint"] = bool(self.read_int())

        self.write("SF6PurityTest?")
        self.measurement_options["SF6_Vol"] = bool(self.read_int())

    def stop(self) -> None:
        """
        Stop the device. Closes also the communication protocol.
        """

        logger.info("Stopping device " + str(self))
        super().stop()

    def write(self, value) -> None:
        """
        Send `value` to `self.com`.

        :param value: Value to send, converted to `str`.
        :raises SerialCommunicationIOError: when communication port is not opened
        """
        self.com.write_text(str(value))

    def read(self, cast_type: Type = str):
        """
        Read value from `self.com` and cast to `cast_type`.
        Raises `ValueError` if read text (`str`) is not convertible to `cast_type`,
        e.g. to `float` or to `int`.

        :return: Read value of `cast_type` type.
        """
        return cast_type(self.com.read_text())

    def read_float(self) -> float:
        """
        Convenience wrapper for `self.read()`, with typing hint for return value.

        :return: Read `float` value.
        """
        return self.read(float)

    def read_int(self) -> int:
        """
        Convenience wrapper for `self.read()`, with typing hint for return value.

        :return: Read `int` value.
        """
        return self.read(int)

    def is_done(self) -> bool:
        """
        Poll status of the dew point mirror and return True, if all
        measurements are done.

        :return: True, if all measurements are done; False otherwise.
        :raises SerialCommunicationIOError: when communication port is not opened
        """

        # assume everything is done
        done = True

        if self.measurement_options["dewpoint"]:
            # ask if done with DP
            self.write("DoneWithDP?")
            done = done and bool(self.read_int())

        if self.measurement_options["SF6_Vol"]:
            # ask if done with SF6 volume measurement
            self.write("SF6VolHold?")
            done = done and bool(self.read_int())

        self.is_done_with_measurements = done

        if self.is_done_with_measurements:
            self.status_poller.stop_polling()
            self.read_measurements()

        return self.is_done_with_measurements

    def start_control(self) -> None:
        """
        Start dew point control to acquire a new value set.

        :raises SerialCommunicationIOError: when communication port is not opened
        """

        # send control?
        self.write("control?")

        if self.read_float():
            raise MBW973ControlRunningException

        # send Pump.on? to check, whether gas is still being pumped back
        self.write("Pump.on?")

        if self.read_float():
            raise MBW973PumpRunningException

        # start control of device
        self.write("control=1")
        logger.info("Starting dew point control")
        self.is_done_with_measurements = False
        self.status_poller.start_polling()

    def read_measurements(self) -> Dict[str, float]:
        """
        Read out measurement values and return them as a dictionary.

        :return: Dictionary with values.
        :raises SerialCommunicationIOError: when communication port is not opened
        """

        self.write("Fp?")
        frostpoint = self.read_float()

        self.write("Fp1?")
        frostpoint_ambient = self.read_float()

        self.write("Px?")
        pressure = self.read_float()

        self.write("PPMv?")
        ppmv = self.read_float()

        self.write("PPMw?")
        ppmw = self.read_float()

        self.write("SF6Vol?")
        sf6_vol = self.read_float()

        values = {
            "frostpoint": frostpoint,
            "frostpoint_ambient": frostpoint_ambient,
            "pressure": pressure,
            "ppmv": ppmv,
            "ppmw": ppmw,
            "sf6_vol": sf6_vol,
        }

        logger.info("Read out values")
        logger.info(values)

        self.last_measurement_values = values

        return values

    def set_measuring_options(
        self, humidity: bool = True, sf6_purity: bool = False
    ) -> None:
        """
        Send measuring options to the dew point mirror.

        :param humidity: Perform humidity test or not?
        :param sf6_purity: Perform SF6 purity test or not?
        :raises SerialCommunicationIOError: when communication port is not opened
        """

        self.write(f"HumidityTest={1 if humidity else 0}")
        self.write(f"SF6PurityTest={1 if sf6_purity else 0}")

        self.measurement_options["dewpoint"] = humidity
        self.measurement_options["SF6_Vol"] = sf6_purity

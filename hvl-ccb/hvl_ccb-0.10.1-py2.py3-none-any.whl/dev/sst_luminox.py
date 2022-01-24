#  Copyright (c) 2020-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device class for a SST Luminox Oxygen sensor. This device can measure the oxygen
concentration between 0 % and 25 %.

Furthermore, it measures the barometric pressure and internal temperature.
The device supports two operating modes: in streaming mode the device measures all
parameters every second, in polling mode the device measures only after a query.

Technical specification and documentation for the device can be found a the
manufacturer's page:
https://www.sstsensing.com/product/luminox-optical-oxygen-sensors-2/
"""

import logging
import re
from enum import Enum
from time import sleep
from typing import Union, Tuple, List, cast, Optional, Dict

from .base import SingleCommDevice, DeviceException
from ..comm import SerialCommunication, SerialCommunicationConfig
from ..comm.serial import (
    SerialCommunicationParity,
    SerialCommunicationStopbits,
    SerialCommunicationBytesize,
)
from ..configuration import configdataclass
from ..utils.enum import ValueEnum
from ..utils.typing import Number

logger = logging.getLogger(__name__)


class LuminoxException(DeviceException):
    """
    General Exception for Luminox Device.
    """
    pass


class LuminoxOutputModeError(LuminoxException):
    """
    Wrong output mode for requested data
    """

    pass


class LuminoxOutputMode(Enum):
    """
    output mode.
    """

    streaming = 0
    polling = 1


class LuminoxMeasurementTypeError(LuminoxException):
    """
    Wrong measurement type for requested data
    """

    pass


LuminoxMeasurementTypeValue = Union[float, int, str]
"""A typing hint for all possible LuminoxMeasurementType values as read in  either
streaming mode or in a polling mode with `LuminoxMeasurementType.all_measurements`.

Beware: has to be manually kept in sync with `LuminoxMeasurementType` instances
`cast_type` attribute values.
"""


LuminoxMeasurementTypeDict = Dict[
    Union[str, "LuminoxMeasurementType"], LuminoxMeasurementTypeValue
]
"""A typing hint for a dictionary holding LuminoxMeasurementType values. Keys are
allowed as strings because `LuminoxMeasurementType` is of a `StrEnumBase` type.
"""


class LuminoxMeasurementType(ValueEnum, init="value cast_type value_re"):  # type:ignore
    """
    Measurement types for `LuminoxOutputMode.polling`.

    The `all_measurements` type will read values for the actual measurement types
    as given in `LuminoxOutputMode.all_measurements_types()`; it parses multiple
    single values using regexp's for other measurement types, therefore, no regexp is
    defined for this measurement type.
    """

    partial_pressure_o2 = "O", float, r"[0-9]{4}.[0-9]"
    percent_o2 = "%", float, r"[0-9]{3}.[0-9]{2}"
    temperature_sensor = "T", float, r"[+-][0-9]{2}.[0-9]"
    barometric_pressure = "P", int, r"[0-9]{4}"
    sensor_status = "e", int, r"[0-9]{4}"
    date_of_manufacture = "# 0", str, r"[0-9]{5} [0-9]{5}"
    serial_number = "# 1", str, r"[0-9]{5} [0-9]{5}"
    software_revision = "# 2", str, r"[0-9]{5}"
    all_measurements = "A", str, None

    @classmethod
    def all_measurements_types(cls) -> Tuple["LuminoxMeasurementType", ...]:
        """
        A tuple of `LuminoxMeasurementType` enum instances which are actual
        measurements, i.e. not date of manufacture or software revision.
        """
        return cast(
            Tuple["LuminoxMeasurementType", ...],
            (
                cls.partial_pressure_o2,
                cls.temperature_sensor,
                cls.barometric_pressure,
                cls.percent_o2,
                cls.sensor_status,
            ),
        )

    @property
    def command(self) -> str:
        return self.value.split(" ")[0]

    def parse_read_measurement_value(
        self, read_txt: str
    ) -> Union[LuminoxMeasurementTypeDict, LuminoxMeasurementTypeValue]:
        if self is LuminoxMeasurementType.all_measurements:
            return {
                measurement: measurement._parse_single_measurement_value(read_txt)
                for measurement in LuminoxMeasurementType.all_measurements_types()
            }
        return self._parse_single_measurement_value(read_txt)

    def _parse_single_measurement_value(
        self, read_txt: str
    ) -> LuminoxMeasurementTypeValue:

        parsed_data: List[str] = re.findall(f"{self.command} {self.value_re}", read_txt)
        if len(parsed_data) != 1:
            self._parse_error(parsed_data)

        parsed_measurement: str = parsed_data[0]
        try:
            parsed_value = self.cast_type(
                # don't check for empty match - we know already that there is one
                re.search(self.value_re, parsed_measurement).group()  # type: ignore
            )
        except ValueError as e:
            logger.error(str(e), exc_info=e)
            self._parse_error(parsed_data)

        return parsed_value

    def _parse_error(self, parsed_data: List[str]) -> None:
        err_msg = (
            f"Expected measurement value for {self.name.replace('_', ' ')} of type "
            f'{self.cast_type}; instead tyring to parse: "{parsed_data}"'
        )
        logger.error(err_msg)
        raise LuminoxMeasurementTypeError(err_msg)


@configdataclass
class LuminoxSerialCommunicationConfig(SerialCommunicationConfig):
    #: Baudrate for SST Luminox is 9600 baud
    baudrate: int = 9600

    #: SST Luminox does not use parity
    parity: Union[str, SerialCommunicationParity] = SerialCommunicationParity.NONE

    #: SST Luminox does use one stop bit
    stopbits: Union[int, SerialCommunicationStopbits] = SerialCommunicationStopbits.ONE

    #: One byte is eight bits long
    bytesize: Union[
        int, SerialCommunicationBytesize
    ] = SerialCommunicationBytesize.EIGHTBITS

    #: The terminator is CR LF
    terminator: bytes = b"\r\n"

    #: use 3 seconds timeout as default
    timeout: Number = 3


class LuminoxSerialCommunication(SerialCommunication):
    """
    Specific communication protocol implementation for the SST Luminox oxygen sensor.
    Already predefines device-specific protocol parameters in config.
    """

    @staticmethod
    def config_cls():
        return LuminoxSerialCommunicationConfig


@configdataclass
class LuminoxConfig:
    """
    Configuration for the SST Luminox oxygen sensor.
    """

    # wait between set and validation of output mode
    wait_sec_post_activate: Number = 0.5
    wait_sec_trials_activate: Number = 0.1
    nr_trials_activate: int = 5

    def clean_values(self):
        if self.wait_sec_post_activate <= 0:
            raise ValueError(
                "Wait time (sec) post output mode activation must be a positive number."
            )
        if self.wait_sec_trials_activate <= 0:
            raise ValueError(
                "Re-try wait time (sec) for mode activation must be a positive number."
            )
        if self.nr_trials_activate <= 0:
            raise ValueError(
                "Trials for mode activation must be a positive integer >=1)."
            )


class Luminox(SingleCommDevice):
    """
    Luminox oxygen sensor device class.
    """

    def __init__(self, com, dev_config=None):

        # Call superclass constructor
        super().__init__(com, dev_config)

        self.output: Optional[LuminoxOutputMode] = None

    @staticmethod
    def config_cls():
        return LuminoxConfig

    @staticmethod
    def default_com_cls():
        return LuminoxSerialCommunication

    def start(self) -> None:
        """
        Start this device. Opens the communication protocol.
        """

        logger.info(f"Starting device {self}")
        super().start()

    def stop(self) -> None:
        """
        Stop the device. Closes also the communication protocol.
        """

        logger.info(f"Stopping device {self}")
        super().stop()

    def _write(self, value: str) -> None:
        """
        Write given `value` string to `self.com`.

        :param value: String value to send.
        :raises SerialCommunicationIOError: when communication port is not opened
        """

        self.com.write_text(value)

    def _read(self) -> str:
        """
        Read a string value from `self.com`.

        :return: Read text from the serial port, without the trailing terminator,
            as defined in the communcation protocol configuration.
        :raises SerialCommunicationIOError: when communication port is not opened
        """
        return self.com.read_text().rstrip(self.com.config.terminator_str())

    def activate_output(self, mode: LuminoxOutputMode) -> None:
        """
        activate the selected output mode of the Luminox Sensor.
        :param mode: polling or streaming
        """
        with self.com.access_lock:
            self._write(f"M {mode.value}")
            # needs a little bit of time ot activate
            sleep(self.config.wait_sec_post_activate)

            for trial in range(self.config.nr_trials_activate + 1):
                msg = self._read()
                if (
                    not msg == f"M 0{mode.value}"
                    and trial == self.config.nr_trials_activate
                ):
                    err_msg = (
                        f"Stream mode activation was not possible "
                        f"after {self.config.nr_trials_activate} trials {self}"
                    )
                    logger.error(err_msg)
                    raise LuminoxOutputModeError(err_msg)
                if msg == f"M 0{mode.value}":
                    msg = (
                        f"Stream mode activation possible "
                        f"in trial {trial} out of {self.config.nr_trials_activate}"
                    )
                    logger.info(msg)
                    break
                sleep(self.config.wait_sec_trials_activate)

        self.output = mode
        logger.info(f"{mode.name} mode activated {self}")

    def read_streaming(self) -> LuminoxMeasurementTypeDict:
        """
        Read values of Luminox in the streaming mode. Convert the single string
        into separate values.

        :return: dictionary with `LuminoxMeasurementType.all_measurements_types()` keys
            and accordingly type-parsed values.
        :raises LuminoxOutputModeError: when streaming mode is not activated
        :raises LuminoxMeasurementTypeError: when any of expected measurement values is
            not read
        """
        if not self.output == LuminoxOutputMode.streaming:
            err_msg = f"Streaming mode not activated {self}"
            logger.error(err_msg)
            raise LuminoxOutputModeError(err_msg)

        read_txt = self._read()
        return cast(
            LuminoxMeasurementTypeDict,
            cast(
                LuminoxMeasurementType, LuminoxMeasurementType.all_measurements
            ).parse_read_measurement_value(read_txt),
        )

    def query_polling(
        self,
        measurement: Union[str, LuminoxMeasurementType],
    ) -> Union[LuminoxMeasurementTypeDict, LuminoxMeasurementTypeValue]:
        """
        Query a value or values of Luminox measurements in the polling mode,
        according to a given measurement type.

        :param measurement: type of measurement
        :return: value of requested measurement
        :raises ValueError: when a wrong key for LuminoxMeasurementType is provided
        :raises LuminoxOutputModeError: when polling mode is not activated
        :raises LuminoxMeasurementTypeError: when expected measurement value is not read
        """
        if not isinstance(measurement, LuminoxMeasurementType):
            try:
                measurement = cast(
                    LuminoxMeasurementType,
                    LuminoxMeasurementType[measurement],  # type: ignore
                )
            except KeyError as e:
                logger.error(str(e), exc_info=e)
                measurement = cast(
                    LuminoxMeasurementType,
                    LuminoxMeasurementType(measurement),
                )

        if not self.output == LuminoxOutputMode.polling:
            err_msg = f"Polling mode not activated {self}"
            logger.error(err_msg)
            raise LuminoxOutputModeError(err_msg)

        with self.com.access_lock:
            self._write(str(measurement))
            read_txt = self._read()
        read_value = measurement.parse_read_measurement_value(read_txt)
        return read_value

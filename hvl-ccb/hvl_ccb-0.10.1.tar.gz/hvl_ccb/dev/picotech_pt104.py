#  Copyright (c) 2020-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Controller for the Pico Technology PT-104 temperature logger device.
The controller is written as a wrapper around Pico Technology driver for the PT-104
device.

This code is directly based on: https://github.com/trombastic/Pico_PT104/ .

Extra installation
~~~~~~~~~~~~~~~~~~

Pico Technology driver for the PT-104 device is available only on Windows and on Linux.

To use this PT-104 device wrapper:

1. install the :code:`hvl_ccb` package with a :code:`picotech` extra feature::

        $ pip install "hvl_ccb[picotech]"

   this will install the Python bindings for the library.

2. install the library

    * on Windows: download and install PicoSDK from https://www.picotech.com/downloads
      (choose "PicoLog Data Loggers" > "PT-104" > "Software");
    * on Linux:
        - for Ubuntu/Debian, install :code:`libusbpt104` from :code:`.deb` file found in
          https://labs.picotech.com/debian/pool/main/libu/libusbpt104/ (note: at the
          moment the PT-104 driver is not a part of the official :code:`picoscope`
          package; cf.
          https://www.picotech.com/support/topic40626.html );
        - for any other supported Linux distribution, follow instructions to install
          the "USB PT-104 devices" drivers in https://www.picotech.com/downloads/linux ;

"""

import logging
from abc import ABC
from ctypes import byref, c_long, c_short, c_ushort
from dataclasses import dataclass, field
from enum import IntEnum
from functools import wraps
from ipaddress import IPv4Address, IPv6Address
from time import time
from typing import Type, Dict, Optional, Union

import aenum
from picosdk.errors import CannotFindPicoSDKError  # type: ignore

try:
    from picosdk.usbPT104 import usbPt104 as pt104  # type: ignore
except CannotFindPicoSDKError:
    # PicoSDK Python wrapper tries to import PicoSDK system library already on import
    raise ImportError

from .base import SingleCommDevice, DeviceException
from ..comm import NullCommunicationProtocol
from ..configuration import configdataclass
from hvl_ccb.utils.validation import validate_and_resolve_host, validate_tcp_port

logger = logging.getLogger(__name__)


class Pt104Exception(DeviceException):
    """
    Exception to indicate communication issues with the pt104.
    """
    pass


def require_started(method):
    """
    Check if device `is_started` and raise an `Pt104Exception` if not.

    :param method: `Pt104` instance method to wrap
    :return: Whatever `method` returns
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.is_started:
            err_msg = f"{self} is not started. Run `start()` method first."
            logger.error(err_msg)
            raise Pt104Exception(err_msg)
        return method(self, *args, **kwargs)

    return wrapper


class Pt104Channels(IntEnum):
    CHANNEL_1 = 1
    CHANNEL_2 = 2
    CHANNEL_3 = 3
    CHANNEL_4 = 4
    CHANNEL_5 = 5
    CHANNEL_6 = 6
    CHANNEL_7 = 7
    CHANNEL_8 = 8
    MAX_CHANNELS = CHANNEL_8


class Pt104Wires(IntEnum):
    WIRES_2 = 2
    WIRES_3 = 3
    WIRES_4 = 4
    MIN_WIRES = WIRES_2
    MAX_WIRES = WIRES_4


class Pt104DataTypes(IntEnum):
    OFF = 0
    PT100 = 1
    PT1000 = 2
    RESISTANCE_TO_375R = 3
    RESISTANCE_TO_10K = 4
    DIFFERENTIAL_TO_115MV = 5
    DIFFERENTIAL_TO_2500MV = 6
    SINGLE_ENDED_TO_115MV = 7
    SINGLE_ENDED_TO_2500MV = 8

    @property
    def is_active(self):
        return self is not Pt104DataTypes.OFF


_pt104_ct_dict = pt104.COMMUNICATION_TYPE()


class Pt104CommunicationType(aenum.IntEnum, init="value open_unit"):  # type: ignore
    USB = (
        _pt104_ct_dict["CT_USB"],
        pt104._OpenUnit,  # UsbPt104OpenUnit
    )
    ETHERNET = (
        _pt104_ct_dict["CT_ETHERNET"],
        pt104._OpenUnitViaIp,  # UsbPt104OpenUnitViaIP
    )

    @property
    def requires_host(self) -> bool:
        return self == self.__class__.ETHERNET


@configdataclass
class Pt104DeviceConfig:
    """
    Configuration dataclass for PT104
    """

    #: Serial number
    serial_number: str
    #: Interface to communicate on
    interface: Pt104CommunicationType
    #: Host TCP/IP address, if applicable
    host: Optional[Union[str, IPv4Address, IPv6Address]] = None
    #: TCP port number, if applicable
    port: Optional[int] = None

    def clean_values(self):
        if self.interface.requires_host:
            self.force_value("host", validate_and_resolve_host(self.host, logger))
            validate_tcp_port(self.port, logger)

    @property
    def host_address(self) -> Optional[str]:
        if self.host:
            port_sufix = f":{self.port}" if self.port else ""
            return f"{self.host}{port_sufix}"
        return None


@dataclass
class Pt104ChannelConfig:
    data_type: Pt104DataTypes = Pt104DataTypes.OFF
    nb_wires: Pt104Wires = Pt104Wires.WIRES_4
    low_pass_filter: bool = True
    value: c_long = c_long(0)
    last_query: float = field(init=False)

    def __post_init__(self):
        self.last_query = time()


class Pt104(SingleCommDevice, ABC):
    """
    PicoTech pt104 data logger class.
    """

    def __init__(self, com, dev_config=None) -> None:
        """
        Constructor for pt104.

        :param com: object to use as communication protocol.
        """

        # Call superclass constructor
        super().__init__(com, dev_config)

        self.channels: Dict[Pt104Channels, Pt104ChannelConfig] = {
            ch: Pt104ChannelConfig()
            for ch in (
                Pt104Channels.CHANNEL_1,
                Pt104Channels.CHANNEL_2,
                Pt104Channels.CHANNEL_3,
                Pt104Channels.CHANNEL_4,
            )
        }
        self._handle: Optional[c_short] = None

    @staticmethod
    def default_com_cls() -> Type[NullCommunicationProtocol]:
        return NullCommunicationProtocol

    @staticmethod
    def config_cls():
        return Pt104DeviceConfig

    @staticmethod
    def _validate_channel(self, channel: int):
        if channel not in self.channels:
            raise ValueError(f"Invalid channel {channel}; available channels are: "
                             f"", ".join(self.channels.keys())}.")

    @property
    def is_connected(self) -> bool:
        """Check the connection status.

        :return: `True` if connection with device is initiated, `False` otherwise.
        """
        return self._handle is not None

    @property
    def is_started(self) -> bool:
        """Check if device is started.

        :return: `True` if device is started, `False` otherwise.
        """
        return self.is_connected

    def start(self) -> None:
        """Connect to a Pt-104A data acquisition module via USB or Ethernet
        """
        logger.info("Starting device " + str(self))
        super().start()

        if self.is_connected:
            self.stop()

        self._handle = c_short()

        open_unit_extra_args = []
        if self.config.interface.requires_host:
            open_unit_extra_args.append(self.config.host_address.encode())
        status_unit = self.config.interface.open_unit(
            byref(self._handle),
            self.config.serial_number.encode(),
            *open_unit_extra_args
        )

        if status_unit != 0:
            self._handle = None
            msg = (
                f"Communication with pt104 could not be established, "
                f"error code: {status_unit}"
            )
            logger.error(msg)
            raise Pt104Exception(msg)

        self.set_channels()

    @property
    def active_channel_count(self) -> int:
        """return the number of active channels
        :return: number of active channels
        """
        n = 0
        for channel, conf in self.channels.items():
            if conf.data_type.is_active:
                n += 1
        return n

    def stop(self) -> None:
        """disconnect from the unit
        :return: bool
        """
        logger.info("Stopping device " + str(self))
        pt104.UsbPt104CloseUnit(self._handle)
        self._handle = None
        super().stop()

    @require_started
    def set_channel(
        self,
        channel: Pt104Channels,
        data_type: Pt104DataTypes,
        nb_wires: Pt104Wires,
        low_pass_filter: bool = True,
    ) -> None:
        """writes the channel configuration to self.channels and the device.
        :param channel: channel number (Pt104Channels)
        :param data_type: data type of the connected probe (DataType)
        :param nb_wires: number of wires (Pt104Wires)
        :param low_pass_filter: use the low pass filter [True, False]
        :return: status
        """
        logger.info(f"Configuring channel: {channel}")
        self._validate_channel(self, channel)
        self.channels[channel].data_type = data_type
        self.channels[channel].nb_wires = nb_wires
        self.channels[channel].low_pass_filter = low_pass_filter

        cs = pt104.UsbPt104SetChannel(self._handle, channel, data_type, nb_wires)
        if cs != 0:
            msg = f"Setting channel {channel} failed with error {cs}"
            logger.error(msg)
            raise Pt104Exception(msg)

    def set_channels(self) -> None:
        """sets the channel configuration from self.channels
        """
        for channel in self.channels:
            self.set_channel(channel, self.channels[channel].data_type,
                             self.channels[channel].nb_wires)

    @require_started
    def get_value(self, channel: Pt104Channels, raw_value: bool = False) -> float:
        """queries the measurement value from the unit
        :param channel: channel number (Pt104Channels)
        :param raw_value: skip conversion
        :return: measured value
        """
        self._validate_channel(self, channel)
        result = None
        count = 0
        while result is None:
            count += 1
            self._wait_for_conversion(channel)
            status_channel = pt104.UsbPt104GetValue(
                self._handle,
                channel,
                byref(self.channels[channel].value),
                self.channels[channel].low_pass_filter,
            )
            self.channels[channel].last_query = time()
            if status_channel == 0:
                if raw_value:
                    result = float(self.channels[channel].value.value)
                    return result
                result = self.scale_value(
                    float(self.channels[channel].value.value), channel
                )
                return result
            else:
                msg = f"Error while reading {channel}, error code {status_channel}"
                logger.error(msg)
            if count == 10:
                msg = f"Could not retrieve value from pt104 {channel} after 10 trials"
                logger.error(msg)
                raise Pt104Exception(msg)

    @property
    def get_value_channel_1(self) -> float:
        """queries the measurement value from channel 1
        :return: scaled measured value
        """
        return self.get_value(Pt104Channels.CHANNEL_1)

    @property
    def get_value_channel_2(self) -> float:
        """queries the measurement value from channel 2
        :return: scaled measured value
        """
        return self.get_value(Pt104Channels.CHANNEL_2)

    @property
    def get_value_channel_3(self) -> float:
        """queries the measurement value from channel 3
        :return: scaled measured value
        """
        return self.get_value(Pt104Channels.CHANNEL_3)

    @property
    def get_value_channel_4(self) -> float:
        """queries the measurement value from channel 4
        :return: scaled measured value
        """
        return self.get_value(Pt104Channels.CHANNEL_4)

    def set_mains(self, sixty_hertz: bool = False) -> None:
        """This function is used to inform the driver of the
        local mains (line) frequency.
        This helps the driver to filter out electrical noise.
        :param sixty_hertz: mains frequency is sixty
        :return: success
        """
        if sixty_hertz:
            sixty = c_ushort(1)
            logger.info("set mains freq to 60 Hz")
        else:
            sixty = c_ushort(0)
            logger.info("set mains freq to 50 Hz")
        pt104.UsbPt104SetMains(self._handle, sixty)

    def _wait_for_conversion(self, channel: Pt104Channels) -> None:
        """wait until the adc conversion is finished
        :param channel: channel number (Pt104Channels)
        :return:
        """
        conversion_time = self.active_channel_count * 0.75
        last_query = self.channels[channel].last_query
        while last_query + conversion_time > time():
            pass

    def scale_value(self, value: float, channel: Pt104Channels) -> float:
        """scales the value from the device.
        :param value: value to convert as float
        :param channel: channel number (Pt104Channels)
        :return: Temperature in °C, Resistance in mOhm, Voltage in mV
        """
        if self.channels[channel].data_type in [Pt104DataTypes.PT100,
                                                Pt104DataTypes.PT1000]:
            return value / 10.0 ** 3  # °C
        if self.channels[channel].data_type == Pt104DataTypes.RESISTANCE_TO_375R:
            return value / 10.0 ** 3  # mOhm
        if self.channels[channel].data_type == Pt104DataTypes.RESISTANCE_TO_10K:
            return value  # mOhm
        if self.channels[channel].data_type in [
            Pt104DataTypes.DIFFERENTIAL_TO_115MV,
            Pt104DataTypes.SINGLE_ENDED_TO_115MV,
        ]:
            return value / 10.0 ** 9  # mV
        if self.channels[channel].data_type in [
            Pt104DataTypes.DIFFERENTIAL_TO_2500MV,
            Pt104DataTypes.SINGLE_ENDED_TO_2500MV,
        ]:
            return value / 10.0 ** 8  # mV
        else:
            raise Pt104Exception('selected datatype not recognized')

#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
A LabJack T-series devices wrapper around the LabJack's LJM Library; see
https://labjack.com/ljm .
The wrapper was originally developed and tested for a LabJack T7-PRO device.

Extra installation
~~~~~~~~~~~~~~~~~~

To use this LabJack T-series devices wrapper:

1. install the :code:`hvl_ccb` package with a :code:`labjack` extra feature::

        $ pip install "hvl_ccb[labjack]"

   this will install the Python bindings for the library.

2. install the library - follow instruction in
   https://labjack.com/support/software/installers/ljm .

"""
from __future__ import annotations

import logging
from collections.abc import Sequence
from numbers import Real
from typing import Union, Optional, List, cast, Dict

from aenum import Enum, IntEnum

from hvl_ccb.dev.base import DeviceException
from .._dev import labjack
from ..comm import LJMCommunication
from ..dev import SingleCommDevice
from ..utils.enum import NameEnum, StrEnumBase
from ..utils.typing import Number
from ..utils.validation import validate_bool, validate_number

logger = logging.getLogger(__name__)


class LabJackError(DeviceException):
    """
    General Exception for the LabJack device.
    """

    pass


class LabJackIdentifierDIOError(LabJackError):
    """
    Error indicating a wrong DIO identifier
    """

    pass


class LabJack(SingleCommDevice):
    """
    LabJack Device.

    This class is tested with a LabJack T7-Pro and should also work with T4 and T7
    devices communicating through the LJM Library. Other or older hardware versions and
    variants of LabJack devices are not supported.
    """

    DeviceType = labjack.DeviceType
    """
    LabJack device types.
    """

    def __init__(self, com, dev_config=None) -> None:
        """
        Constructor for a LabJack Device.

        :param com: Communication protocol object of type
            LJMCommunication. If a configuration (dict or configdataclass) is given,
            a new communication protocol object will be instantiated.
        :param dev_config: There is no device configuration for LabJack yet.
        """
        super().__init__(com, dev_config)

        # cached device type
        self._device_type: Optional[labjack.DeviceType] = None

        # clock configuration for pulse out feature
        self.configured_pulse_addresses: List[
            Union[str, labjack.TSeriesDIOChannel]] = []

    @staticmethod
    def default_com_cls():
        return LJMCommunication

    def start(self) -> None:
        """
        Start the Device.
        """

        logger.info(f"Starting device {str(self)}")
        super().start()

    def stop(self) -> None:
        """
        Stop the Device.
        """

        logger.info(f"Stopping device {str(self)}")
        super().stop()

    def _read_float(self, *names: str) -> Union[float, Sequence[float]]:
        """
        Read a numeric value.

        :param name: name to read via communication protocol
        :return: read numeric value
        """
        return self.com.read_name(*names, return_num_type=float)

    def _read_int(self, *names: str) -> Union[int, Sequence[int]]:
        """
        Read an integer value.

        :param name: name to read via communication protocol
        :return: read integer value
        """
        return self.com.read_name(*names, return_num_type=int)

    def get_serial_number(self) -> int:
        """
        Returns the serial number of the connected LabJack.

        :return: Serial number.
        """

        return cast(int, self._read_int("SERIAL_NUMBER"))

    def get_sbus_temp(self, number: int) -> float:
        """
        Read the temperature value from a serial SBUS sensor.

        :param number: port number (0..22)
        :return: temperature in Kelvin
        """

        return cast(float, self._read_float(f"SBUS{number}_TEMP"))

    def get_sbus_rh(self, number: int) -> float:
        """
        Read the relative humidity value from a serial SBUS sensor.

        :param number: port number (0..22)
        :return: relative humidity in %RH
        """

        return cast(float, self._read_float(f"SBUS{number}_RH"))

    class AInRange(StrEnumBase, init="value_str"):  # type:ignore
        TEN = "10"
        ONE = "1"
        ONE_TENTH = "0.1"
        ONE_HUNDREDTH = "0.01"

        def __str__(self) -> str:
            return self.value_str

        @property
        def value(self) -> float:
            return float(self.value_str)

    def get_ain(self, *channels: int) -> Union[float, Sequence[float]]:
        """
        Read currently measured value (voltage, resistance, ...) from one or more
        of analog inputs.

        :param channels: AIN number or numbers (0..254)
        :return: the read value (voltage, resistance, ...) as `float`or `tuple` of
            them in case multiple channels given
        """
        ch_str = [f"AIN{ch}" for ch in channels]
        return self._read_float(*ch_str)

    def set_analog_output(self, channel: int, value: Number) -> None:
        """
        Set the voltage of a analog output port

        :param channel: DAC channel number 1/0
        :param value: The output voltage value 0-5 Volts int/float
        """
        validate_number("DAC channel number", channel, (0, 1), int, logger)
        validate_number("DAC output voltage", value, (0.0, 5.0), logger=logger)
        self.com.write_name(f"DAC{channel}", value)

    def set_ain_range(self, channel: int, vrange: Union[Real, AInRange]) -> None:
        """
        Set the range of an analog input port.

        :param channel: is the AIN number (0..254)
        :param vrange: is the voltage range to be set
        """
        vrange = self.AInRange(str(vrange))
        self.com.write_name(f"AIN{channel}_RANGE", vrange.value)

    def set_ain_resolution(self, channel: int, resolution: int) -> None:
        """
        Set the resolution index of an analog input port.

        :param channel: is the AIN number (0..254)
        :param resolution: is the resolution index within
            0...`get_product_type().ain_max_resolution` range; 0 will set the
            resolution index to default value.
        """

        ain_max_resolution = self.get_product_type().ain_max_resolution  # type: ignore
        if resolution not in range(ain_max_resolution + 1):
            raise LabJackError(f"Not supported resolution index: {resolution}")

        self.com.write_name(f"AIN{channel}_RESOLUTION_INDEX", resolution)

    def set_ain_differential(self, pos_channel: int, differential: bool) -> None:
        """
        Sets an analog input to differential mode or not.
        T7-specific: For base differential channels, positive must be even channel
        from 0-12 and negative must be positive+1. For extended channels 16-127,
        see Mux80 datasheet.

        :param pos_channel: is the AIN number (0..12)
        :param differential: True or False
        :raises LabJackError: if parameters are unsupported
        """

        if pos_channel not in range(13):
            raise LabJackError(f"Not supported pos_channel: {pos_channel}")

        if pos_channel % 2 != 0:
            raise LabJackError(
                f"AIN pos_channel for positive part of differential pair"
                f" must be even: {pos_channel}"
            )

        neg_channel = pos_channel + 1

        self.com.write_name(
            f"AIN{pos_channel}_NEGATIVE_CH", neg_channel if differential else 199
        )

    class ThermocoupleType(NameEnum, init="ef_index"):  # type:ignore
        """
        Thermocouple type; NONE means disable thermocouple mode.
        """

        NONE = 0
        E = 20
        J = 21
        K = 22
        R = 23
        T = 24
        S = 25
        C = 30
        PT100 = 40
        PT500 = 41
        PT1000 = 42

    class CjcType(NameEnum, init="slope offset"):  # type:ignore
        """
        CJC slope and offset
        """

        internal = 1, 0
        lm34 = 55.56, 255.37

    class TemperatureUnit(NameEnum, init="ef_config_a"):  # type:ignore
        """
        Temperature unit (to be returned)
        """

        K = 0
        C = 1
        F = 2

    def set_ain_thermocouple(
        self,
        pos_channel: int,
        thermocouple: Union[None, str, ThermocoupleType],
        cjc_address: int = 60050,
        cjc_type: Union[str, CjcType] = (
            CjcType.internal  # type: ignore
        ),
        vrange: Union[Real, AInRange] = (
            AInRange.ONE_HUNDREDTH  # type: ignore
        ),
        resolution: int = 10,
        unit: Union[str, TemperatureUnit] = (
            TemperatureUnit.K  # type: ignore
        ),
    ) -> None:
        """
        Set the analog input channel to thermocouple mode.

        :param pos_channel: is the analog input channel of the positive part of the
            differential pair
        :param thermocouple: None to disable thermocouple mode, or string specifying
            the thermocouple type
        :param cjc_address: modbus register address to read the CJC temperature
        :param cjc_type: determines cjc slope and offset, 'internal' or 'lm34'
        :param vrange: measurement voltage range
        :param resolution: resolution index (T7-Pro: 0-12)
        :param unit: is the temperature unit to be returned ('K', 'C' or 'F')
        :raises LabJackError: if parameters are unsupported
        """

        if thermocouple is None:
            thermocouple = self.ThermocoupleType.NONE  # type: ignore

        thermocouple = self.ThermocoupleType(thermocouple)

        # validate separately from `set_ain_range` to fail before any write happens
        # (in `set_ain_differential` first)
        vrange = self.AInRange(str(vrange))

        unit = self.TemperatureUnit(unit)

        cjc_type = self.CjcType(cjc_type)

        self.set_ain_differential(pos_channel=pos_channel, differential=True)
        self.set_ain_range(pos_channel, vrange)
        self.set_ain_resolution(pos_channel, resolution)
        self.set_ain_range(pos_channel + 1, vrange)
        self.set_ain_resolution(pos_channel + 1, resolution)

        # specify thermocouple mode
        self.com.write_name(f"AIN{pos_channel}_EF_INDEX", thermocouple.ef_index)

        # specify the units for AIN#_EF_READ_A and AIN#_EF_READ_C (0 = K, 1 = C, 2 = F)
        self.com.write_name(f"AIN{pos_channel}_EF_CONFIG_A", unit.ef_config_a)

        # specify modbus address for cold junction reading CJC
        self.com.write_name(f"AIN{pos_channel}_EF_CONFIG_B", cjc_address)

        # set slope for the CJC reading, typically 1
        self.com.write_name(f"AIN{pos_channel}_EF_CONFIG_D", cjc_type.slope)

        # set the offset for the CJC reading, typically 0
        self.com.write_name(f"AIN{pos_channel}_EF_CONFIG_E", cjc_type.offset)

    def read_thermocouple(self, pos_channel: int) -> float:
        """
        Read the temperature of a connected thermocouple.

        :param pos_channel: is the AIN number of the positive pin
        :return: temperature in specified unit
        """

        return round(cast(float, self._read_float(f"AIN{pos_channel}_EF_READ_A")), 2)

    class DIOStatus(IntEnum):
        """
        State of a digital I/O channel.
        """

        LOW = 0
        HIGH = 1

    def set_digital_output(self, address: str, state: Union[int, DIOStatus]) -> None:
        """
        Set the value of a digital output.

        :param address: name of the output -> `'FIO0'`
        :param state: state of the output -> `DIOStatus` instance or corresponding `int`
            value
        """
        dt = self.get_product_type()
        if address not in (
            dt.dio  # type: ignore
        ):
            raise LabJackIdentifierDIOError
        state = self.DIOStatus(state)
        self.com.write_name(address, state)

    DIOChannel = labjack.TSeriesDIOChannel

    def get_digital_input(
        self, address: Union[str, labjack.TSeriesDIOChannel]
    ) -> LabJack.DIOStatus:
        """
        Get the value of a digital input.

        allowed names for T7 (Pro): FIO0 - FIO7, EIO0 - EIO 7, CIO0- CIO3, MIO0 - MIO2
        :param address: name of the output -> 'FIO0'
        :return: HIGH when `address` DIO is high, and LOW when `address` DIO is low
        """
        if not isinstance(address, self.DIOChannel):
            address = self.DIOChannel(address)
        dt = self.get_product_type()
        if address not in (
            dt.dio  # type: ignore
        ):
            dt_name = dt.name  # type: ignore
            raise LabJackIdentifierDIOError(
                f"DIO {address.name} is not available for this device type: {dt_name}."
            )
        try:
            ret = self._read_int(address.name)
            return self.DIOStatus(ret)
        except ValueError as e:
            logger.error(str(e), exc_info=e)
            raise LabJackIdentifierDIOError(f"Expected 0 or 1 return value, got {ret}.")

    class CalMicroAmpere(Enum, init="value current_source_query"):  # type: ignore
        """
        Pre-defined microampere (uA) values for calibration current source query.
        """

        TEN = "10uA", "CURRENT_SOURCE_10UA_CAL_VALUE"
        TWO_HUNDRED = "200uA", "CURRENT_SOURCE_200UA_CAL_VALUE"

    def get_cal_current_source(self, name: Union[str, CalMicroAmpere]) -> float:
        """
        This function will return the calibration of the chosen current source,
        this ist not a measurement!

        The value was stored during fabrication.

        :param name: '200uA' or '10uA' current source
        :return: calibration of the chosen current source in ampere
        """
        if not isinstance(name, self.CalMicroAmpere):
            name = self.CalMicroAmpere(name)
        return cast(float, self._read_float(name.current_source_query))

    def get_product_id(self) -> int:
        """
        This function returns the product ID reported by the connected device.

        Attention: returns `7` for both T7 and T7-Pro devices!

        :return: integer product ID of the device
        """
        return cast(int, self._read_int("PRODUCT_ID"))

    def get_product_type(self, force_query_id: bool = False) -> labjack.DeviceType:
        """
        This function will return the device type based on reported device type and
        in case of unambiguity based on configuration of device's communication
        protocol (e.g. for "T7" and  "T7_PRO" devices), or, if not available first
        matching.


        :param force_query_id: boolean flag to force `get_product_id` query to device
            instead of using cached device type from previous queries.
        :return: `DeviceType` instance
        :raises LabJackIdentifierDIOError: when read Product ID is unknown
        """
        if force_query_id or not self._device_type:
            try:
                device_type_or_list = self.DeviceType.get_by_p_id(self.get_product_id())
            except ValueError as e:
                logger.error(str(e), exc_info=e)
                raise LabJackIdentifierDIOError from e
            if isinstance(device_type_or_list, self.DeviceType):
                device_type = device_type_or_list
            else:  # isinstance(device_type_or_list, list):
                device_type_list: List[labjack.DeviceType] = device_type_or_list
                # can be None in case a non-default com or its config was used
                conf_device_type = getattr(self.com.config, "device_type", None)
                if conf_device_type:
                    if conf_device_type not in device_type_list:
                        raise LabJackIdentifierDIOError(
                            f"Configured devices type {conf_device_type!s} does not "
                            f"match any of the unambiguously reported device types: "
                            f"{','.join(str(dt) for dt in device_type_list)}."
                        )
                    device_type = conf_device_type
                else:
                    device_type = device_type_list[0]
            self._device_type = device_type
        return self._device_type

    def get_product_name(self, force_query_id=False) -> str:
        """
        This function will return the product name based on product ID reported by
        the device.

        Attention: returns "T7" for both T7 and T7-Pro devices!

        :param force_query_id: boolean flag to force `get_product_id` query to device
            instead of using cached device type from previous queries.
        :return: device name string, compatible with `LabJack.DeviceType`
        """
        return self.get_product_type(force_query_id=force_query_id).name

    def set_ain_resistance(
        self, channel: int, vrange: Union[Real, AInRange], resolution: int
    ) -> None:
        """
        Set the specified channel to resistance mode. It utilized the 200uA current
        source of the LabJack.

        :param channel: channel that should measure the resistance
        :param vrange: voltage range of the channel
        :param resolution: resolution index of the channel T4: 0-5, T7: 0-8, T7-Pro 0-12
        """
        self.set_ain_range(channel, vrange)
        self.set_ain_resolution(channel, resolution)

        # resistance mode
        self.com.write_name(f"AIN{channel}_EF_INDEX", 4)
        # excitation with 200uA current source
        self.com.write_name(f"AIN{channel}_EF_CONFIG_B", 0)

    def read_resistance(self, channel: int) -> float:
        """
        Read resistance from specified channel.

        :param channel: channel with resistor
        :return: resistance value with 2 decimal places
        """
        return round(cast(float, self._read_float(f"AIN{channel}_EF_READ_A")), 2)

    class ClockFrequency(IntEnum):
        """
        Available clock frequencies, in Hz
        """
        MAXIMUM = 80_000_000
        FORTY_MHZ = 40_000_000
        TWENTY_MHZ = 20_000_000
        TEN_MHZ = 10_000_000
        FIVE_MHZ = 5_000_000
        TWENTY_FIVE_HUNDRED_KHZ = 2_500_000
        TWELVE_HUNDRED_FIFTY_KHZ = 1_250_000
        MINIMUM = 312_500

    class BitLimit(IntEnum):
        """
        Maximum integer values for clock settings
        """
        THIRTY_TWO_BIT = 2 ** 32 - 1

    @property
    def _clock_config(self) -> Dict[str, int]:
        clock_config = {"divisor": self.com.read_name("DIO_EF_CLOCK0_DIVISOR"),
                        "roll_value": self.com.read_name("DIO_EF_CLOCK0_ROLL_VALUE")}
        # adjust zeroes to corresponding real values for frequency/period conversion:
        if clock_config["divisor"] == 0:
            clock_config["divisor"] = 1
        if clock_config["roll_value"] == 0:
            clock_config["roll_value"] = self.BitLimit.THIRTY_TWO_BIT

        return clock_config

    @_clock_config.setter
    def _clock_config(self, clock_config: Dict[str, int]):
        self.com.write_name("DIO_EF_CLOCK0_DIVISOR", clock_config["divisor"])
        self.com.write_name("DIO_EF_CLOCK0_ROLL_VALUE", clock_config["roll_value"])

    def enable_clock(self, clock_enabled: bool) -> None:
        """
        Enable/disable LabJack clock to configure or send pulses.
        :param clock_enabled: True -> enable, False -> disable.
        :raises TypeError: if clock_enabled is not of type bool
        """
        validate_bool("clock enabled", clock_enabled, logger=logger)
        self.com.write_name("DIO_EF_CLOCK0_ENABLE", int(clock_enabled))

    def get_clock(self) -> Dict[str, Number]:
        """
        Return clock settings read from LabJack.
        """
        divisor, roll_value = self._clock_config.values()
        clock_frequency = self.ClockFrequency.MAXIMUM / divisor
        clock_period = clock_frequency * roll_value
        clock_settings = {"clock_frequency": clock_frequency,
                          "clock_period": clock_period}
        return clock_settings

    def set_clock(self,
                  clock_frequency: Union[Number, ClockFrequency] = 10_000_000,
                  clock_period: Number = 1) -> None:
        """
        Configure LabJack clock for pulse out feature.
        :param clock_frequency: clock frequency in Hz; default 10 MHz for base 10.
        :raises ValueError: if clock_frequency is not allowed (see ClockFrequency).
        :param clock_period: clock roll time in seconds; default 1s, 0 for max.
        :raises ValueError: if clock_period exceeds the 32bit tick limit.
        Clock period determines pulse spacing when using multi-pulse settings.
        Ensure period exceeds maximum intended pulse end time.
        """
        validate_number("clock frequency", clock_frequency,
                        limits=(self.ClockFrequency.MINIMUM,
                                self.ClockFrequency.MAXIMUM),
                        logger=logger)
        clock_frequency = self.ClockFrequency(clock_frequency)
        divisor = int(self.ClockFrequency.MAXIMUM / clock_frequency)
        validate_number("clock period", clock_period,
                        limits=(0, self.BitLimit.THIRTY_TWO_BIT/clock_frequency),
                        logger=logger)
        clock_period_ticks = int(clock_period * clock_frequency)

        self.enable_clock(False)
        self._clock_config = {"divisor": divisor, "roll_value": clock_period_ticks}
        # adjust zero input to real period for logging.
        if clock_period == 0:
            clock_period = self.BitLimit.THIRTY_TWO_BIT/clock_frequency
        logger.info(f"Clock frequency is set to {clock_frequency:_} Hz")
        logger.info(f"Clock period is set to {clock_period} s")

    def config_high_pulse(self, address: Union[str, labjack.TSeriesDIOChannel],
                          t_start: Number, t_width: Number, n_pulses: int = 1) -> None:
        """
        Configures one FIO channel to send a timed HIGH pulse.
        Configure multiple channels to send pulses with relative timing accuracy.
        Times have a maximum resolution of 1e-7 seconds @ 10 MHz.
        :param address: FIO channel: [T7] FIO0;2;3;4;5. [T4] FIO6;7.
        :raises LabJackError if address is not supported.
        :param t_start: pulse start time in seconds.
        :raises ValueError: if t_start is negative or would exceed the clock period.
        :param t_width: duration of high pulse, in seconds.
        :raises ValueError: if t_width is negative or would exceed the clock period.
        :param n_pulses: number of pulses to be sent; single pulse default.
        :raises TypeError if n_pulses is not of type int.
        :raises Value Error if n_pulses is negative or exceeds the 32bit limit.
        """
        if not isinstance(address, self.DIOChannel):
            address = self.DIOChannel(address)

        device_type = self.get_product_type()
        if address not in device_type.pulse_out_addr:
            msg = f"{address} does not support pulse feature"
            logging.error(msg)
            raise LabJackError(msg)

        divisor, roll_value = self._clock_config.values()

        clock_frequency = int(self.ClockFrequency.MAXIMUM/divisor)
        clock_period = clock_frequency * roll_value

        validate_number("pulse start", t_start,
                        limits=(0, clock_period), logger=logger)
        validate_number("pulse width", t_width,
                        limits=(0, clock_period - t_start), logger=logger)
        validate_number("n pulses", n_pulses,
                        limits=(0, self.BitLimit.THIRTY_TWO_BIT),
                        number_type=int, logger=logger)

        start_tick = int(t_start * clock_frequency)
        end_tick = int((t_start + t_width) * clock_frequency)
        addr = address.address

        self.enable_clock(False)
        self.com.write_names({f"DIO{addr}": 0,
                              f"DIO{addr}_EF_ENABLE": 0,
                              f"DIO{addr}_EF_OPTIONS": 0,
                              f"DIO{addr}_EF_INDEX": 2,
                              f"DIO{addr}_EF_CONFIG_B": start_tick,
                              f"DIO{addr}_EF_CONFIG_A": end_tick,
                              f"DIO{addr}_EF_CONFIG_C": n_pulses})

        if address not in self.configured_pulse_addresses:
            self.configured_pulse_addresses.append(address)
        logger.info(f"Pulse configured for {address}")

    def send_pulses(self, *addresses: Union[str, labjack.TSeriesDIOChannel]) -> None:
        """
        Sends pre-configured pulses for specified addresses.
        :param addresses: tuple of FIO addresses
        :raises LabJackError if an address has not been configured.
        """
        address_list = []
        for address in addresses:
            if not isinstance(address, self.DIOChannel):
                address = self.DIOChannel(address)
            if address not in self.configured_pulse_addresses:
                msg = f"No pulse configured for {address}"
                logging.error(msg)
                raise LabJackError(msg)
            address_list.append(address.address)

        self.enable_clock(False)
        for addr in address_list:
            self.com.write_name(f"DIO{addr}_EF_ENABLE", 1)

        self.enable_clock(True)
        logger.info(f"Pulses sent on {addresses}")

    def disable_pulses(self,
                       *addresses: Optional[Union[str, labjack.TSeriesDIOChannel]]
                       ) -> None:
        """
        Disable previously configured pulse channels.
        :param addresses: tuple of FIO addresses.
        All channels disabled if no argument is passed.
        """
        self.enable_clock(False)
        if len(addresses) == 0:
            addresses = tuple(self.configured_pulse_addresses)

        for address in addresses:
            if not isinstance(address, self.DIOChannel):
                address = self.DIOChannel(address)
            if address not in self.configured_pulse_addresses:
                logging.warning(f"No pulse configured for {address}")
                continue
            self.com.write_name(f"DIO{address.address}_EF_ENABLE", 0)
            self.configured_pulse_addresses.remove(address.name)
            logger.info(f"Pulse disabled for {address}")

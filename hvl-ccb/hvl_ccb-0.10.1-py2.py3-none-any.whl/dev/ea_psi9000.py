#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device class for controlling a Elektro Automatik PSI 9000 power supply over VISA.

It is necessary that a backend for pyvisa is installed.
This can be NI-Visa oder pyvisa-py (up to now, all the testing was done with NI-Visa)
"""

import dataclasses
import logging
import time
from typing import ClassVar, Iterable, Tuple, Union

from hvl_ccb.dev.base import DeviceException
from .visa import VisaDevice, VisaDeviceConfig
from ..comm import (
    VisaCommunication,
    VisaCommunicationConfig,
)
from ..configuration import configdataclass
from ..utils.typing import Number

logger = logging.getLogger(__name__)


class PSI9000Error(DeviceException):
    """
    Base error class regarding problems with the PSI 9000 supply.
    """

    pass


@configdataclass
class PSI9000VisaCommunicationConfig(VisaCommunicationConfig):
    """
    Visa communication protocol config dataclass with specification for the PSI 9000
    power supply.
    """

    interface_type: Union[
        str, VisaCommunicationConfig.InterfaceType
    ] = VisaCommunicationConfig.InterfaceType.TCPIP_SOCKET  # type: ignore


class PSI9000VisaCommunication(VisaCommunication):
    """
    Communication protocol used with the PSI 9000 power supply.
    """

    @staticmethod
    def config_cls():
        return PSI9000VisaCommunicationConfig


@configdataclass
class PSI9000Config(VisaDeviceConfig):
    """
    Elektro Automatik PSI 9000 power supply device class.
    The device is communicating over a VISA TCP socket.

    Using this power supply, DC voltage and current can be supplied to a load with up
    to 2040 A and 80 V (using all four available units in parallel). The maximum power
    is limited by the grid, being at 43.5 kW available through the CEE63 power socket.
    """

    #: Power limit in W depending on the experimental setup. With
    #: 3x63A, this is 43.5kW. Do not change this value, if you do not know what you
    #: are doing. There is no lower power limit.
    power_limit: Number = 43500

    #: Lower voltage limit in V, depending on the experimental setup.
    voltage_lower_limit: Number = 0.0

    #: Upper voltage limit in V, depending on the experimental setup.
    voltage_upper_limit: Number = 10.0

    #: Lower current limit in A, depending on the experimental setup.
    current_lower_limit: Number = 0.0

    #: Upper current limit in A, depending on the experimental setup.
    current_upper_limit: Number = 2040.0

    wait_sec_system_lock: Number = 0.5
    wait_sec_settings_effect: Number = 1
    wait_sec_initialisation: Number = 2

    # limit with 63 A grid connection, absolute limit, never ever change this value
    _POWER_GRID_LIMIT: ClassVar = 43500

    # do not touch this values, unless you really know what you are doing
    _VOLTAGE_UPPER_LIMIT: ClassVar = 81.6  # nominal voltage + 2% (absolute max)
    _CURRENT_UPPER_LIMIT: ClassVar = 2080.8  # nominal current + 2 % (absolute max)

    def clean_values(self) -> None:
        super().clean_values()
        # check that power_limit is in range
        if self.power_limit > self._POWER_GRID_LIMIT or self.power_limit < 0:
            raise ValueError(
                f"Power limit out of range. Must be in " f"0..{self._POWER_GRID_LIMIT}"
            )

        # check that lower voltage limits are in range
        if (
            self.voltage_lower_limit < 0
            or self.voltage_lower_limit > self.voltage_upper_limit
            or self.voltage_lower_limit > self._VOLTAGE_UPPER_LIMIT
        ):
            raise ValueError("Lower voltage limit out of range.")

        # check that upper voltage limits are in range
        if (
            self.voltage_upper_limit < 0
            or self.voltage_upper_limit < self.voltage_lower_limit
            or self.voltage_upper_limit > self._VOLTAGE_UPPER_LIMIT
        ):
            raise ValueError("Upper voltage limit out of range.")

        # check that lower current limits are in range
        if (
            self.current_lower_limit < 0
            or self.current_lower_limit > self.current_upper_limit
            or self.current_lower_limit > self._CURRENT_UPPER_LIMIT
        ):
            raise ValueError("Lower current limit out of range.")

        # check that upper current limits are in range
        if (
            self.current_upper_limit < 0
            or self.current_upper_limit < self.current_lower_limit
            or self.current_upper_limit > self._CURRENT_UPPER_LIMIT
        ):
            raise ValueError("Upper current limit out of range.")
        if self.wait_sec_system_lock <= 0:
            raise ValueError(
                "Wait time for system lock must be a positive value (in seconds)."
            )
        if self.wait_sec_settings_effect <= 0:
            raise ValueError(
                "Wait time for settings effect must be a positive value (in seconds)."
            )
        if self.wait_sec_initialisation <= 0:
            raise ValueError(
                "Wait time after initialisation must be a positive value (in seconds)."
            )


class PSI9000(VisaDevice):
    """
    Elektro Automatik PSI 9000 power supply.
    """

    # unlock the device only if measured voltage and current are below these values
    # user defined, not a technical requirement of the device
    SHUTDOWN_VOLTAGE_LIMIT = 0.1
    SHUTDOWN_CURRENT_LIMIT = 0.1

    # Master slave nominal voltage and current, if 4 devices are in parallel
    MS_NOMINAL_VOLTAGE = 80
    MS_NOMINAL_CURRENT = 2040

    def __init__(
        self,
        com: Union[PSI9000VisaCommunication, PSI9000VisaCommunicationConfig, dict],
        dev_config: Union[PSI9000Config, dict, None] = None,
    ):
        super().__init__(com, dev_config)

    @staticmethod
    def config_cls():
        return PSI9000Config

    def start(self) -> None:
        """
        Start this device.
        """

        logger.info("Starting device " + str(self))
        super().start()

    def stop(self) -> None:
        """
        Stop this device. Turns off output and lock, if enabled.
        """

        logger.info("Stopping power supply.")

        current_lock = self.get_system_lock()

        if current_lock and self.get_output():
            # locked and output on
            self.set_voltage_current(0, 0)
            time.sleep(self.config.wait_sec_settings_effect)
            self.set_output(False)
            time.sleep(self.config.wait_sec_settings_effect)

        if current_lock:
            # locked
            self.set_system_lock(False)

        super().stop()

    @staticmethod
    def default_com_cls():
        return PSI9000VisaCommunication

    def set_system_lock(self, lock: bool) -> None:
        """
        Lock / unlock the device, after locking the control is limited to this class
        unlocking only possible when voltage and current are below the defined limits

        :param lock: True: locking, False: unlocking
        """

        current_system_lock = self.get_system_lock()

        if lock is current_system_lock:
            logger.info(f"Lock already at desired state: {lock}")
            return

        if lock:
            # we want to lock the system
            self.com.write("SYSTem:LOCK ON")
            time.sleep(self.config.wait_sec_system_lock)
            new_system_lock = self.get_system_lock()

            if not new_system_lock:
                # locking was unsuccessful
                raise PSI9000Error("Locking system unsuccessful.")

            logger.info("Power supply is now locked and ready for access.")
            return

        if not lock:
            # we want to unlock the system
            voltage, current = self.measure_voltage_current()

            if (
                voltage > self.SHUTDOWN_VOLTAGE_LIMIT
                or current > self.SHUTDOWN_CURRENT_LIMIT
            ):
                err_msg = (
                    f"Output voltage and current should be zero: "
                    f"V = {voltage} V, I = {current} A"
                )
                logger.error(err_msg)
                raise PSI9000Error(err_msg)

            self.com.write("SYSTem:LOCK OFF")
            time.sleep(self.config.wait_sec_system_lock)
            new_system_lock = self.get_system_lock()

            if new_system_lock:
                # locking was unsuccessful
                raise PSI9000Error("Unlocking system was unsuccessful.")

            logger.info("Power supply is now unlocked and ready for shutdown.")
            return

    def get_system_lock(self) -> bool:
        """
        Get the current lock state of the system. The lock state is true,
        if the remote control is active and false, if not.

        :return: the current lock state of the device
        """

        lock_string = self.com.query("SYSTem:LOCK:OWNer?")
        if lock_string == "REMOTE":
            return True
        elif lock_string == "NONE" or lock_string == "LOCAL":
            return False
        else:
            raise PSI9000Error(
                f"Illegal answer to SYSTem:LOCK:OWNer? received: {lock_string}"
            )

    def set_output(self, target_onstate: bool) -> None:
        """
        Enables / disables the DC output.

        :param target_onstate: enable or disable the output power
        :raises PSI9000Error: if operation was not successful
        """

        if target_onstate:
            self.com.write("OUTPut ON")
        elif not target_onstate:
            self.com.write("OUTPut OFF")

        output_state = self.get_output()

        if target_onstate and output_state:
            logger.info("Output successfully switched on.")
        elif target_onstate and not output_state:
            logger.error("Output was not switched on.")
            raise PSI9000Error("Output was not switched on.")
        elif not target_onstate and not output_state:
            logger.info("Output successfully switched off.")
        elif not target_onstate and output_state:
            logger.error("Output was not switched off.")
            raise PSI9000Error("Output was not switched off.")

    def get_output(self) -> bool:
        """
        Reads the current state of the DC output of the source. Returns True,
        if it is enabled, false otherwise.

        :return: the state of the DC output
        """

        on_off_string = self.com.query("OUTPut?")
        if on_off_string == "ON":
            return True
        elif on_off_string == "OFF":
            return False
        else:
            raise PSI9000Error(f"Query of OUTPut? is not ON or OFF: {on_off_string}")

    def measure_voltage_current(self) -> Tuple[float, float]:
        """
        Measure the DC output voltage and current

        :return: Umeas in V, Imeas in A
        """

        list_ret = self.com.query("MEASure:VOLTage?", "MEASure:CURRent?")
        assert len(list_ret) == 2
        ret = self._remove_units(list_ret)
        return ret[0], ret[1]

    def set_voltage_current(self, volt: float, current: float) -> None:
        """
        Set voltage and current setpoints.

        After setting voltage and current, a check is performed if writing was
        successful.

        :param volt: is the setpoint voltage: 0..81.6 V (1.02 * 0-80 V)
            (absolute max, can be smaller if limits are set)
        :param current: is the setpoint current: 0..2080.8 A (1.02 * 0 - 2040 A)
            (absolute max, can be smaller if limits are set)
        :raises PSI9000Error: if the desired setpoint is out of limits
        """

        self.com.write(f"SOURce:VOLTage {volt:f}", f"SOURce:CURRent {current:f}")

        read_voltage, read_current = self.get_voltage_current_setpoint()

        if read_voltage == volt and read_current == current:
            logger.info(
                f"Setting voltage to {volt:.2f} V and current to {current:.2f} A was "
                f"successful."
            )

        else:
            v_lower, i_lower = self.get_ui_lower_limits()
            v_upper, i_upper, p_upper = self.get_uip_upper_limits()

            err_msg = (
                f"Setting U = {volt:f} V and I = {current:f} A was not successful: "
                f"voltage has to be between {v_lower} V and {v_upper} V, "
                f"current between {i_lower} A and {i_upper} A. "
                f"Actual settings are: U = {read_voltage} V, I = {read_current} A"
            )
            logger.error(err_msg)
            raise PSI9000Error(err_msg)

    def get_voltage_current_setpoint(self) -> Tuple[float, float]:
        """
        Get the voltage and current setpoint of the current source.

        :return: Uset in V, Iset in A
        """

        list_ret = self.com.query("SOURce:VOLTage?", "SOURce:CURRent?")
        assert len(list_ret) == 2
        ret = self._remove_units(list_ret)
        return ret[0], ret[1]

    def set_upper_limits(
        self,
        voltage_limit: float = None,
        current_limit: float = None,
        power_limit: float = None,
    ) -> None:
        """
        Set the upper limits for voltage, current and power.
        After writing the values a check is performed if the values are set.
        If a parameter is left blank, the maximum configurable limit is set.

        :param voltage_limit: is the voltage limit in V
        :param current_limit: is the current limit in A
        :param power_limit: is the power limit in W
        :raises PSI9000Error: if limits are out of range
        """

        voltage_limit = (
            voltage_limit
            if voltage_limit is not None
            else self.config.voltage_upper_limit
        )
        current_limit = (
            current_limit
            if current_limit is not None
            else self.config.current_upper_limit
        )
        power_limit = (
            power_limit if power_limit is not None else self.config.power_limit
        )

        v_lower, i_lower = self.get_ui_lower_limits()

        # Creates a new configclass object just to check the limits; will raise
        # ValueError if not within limits (see PSI9000Config.clean_values)
        dataclasses.replace(
            self.config,
            voltage_lower_limit=v_lower,
            current_lower_limit=i_lower,
            voltage_upper_limit=voltage_limit,
            current_upper_limit=current_limit,
            power_limit=power_limit,
        )

        self.com.write(
            f"SOURce:VOLTage:LIMit:HIGH {voltage_limit}",
            f"SOURce:CURRent:LIMit:HIGH {current_limit}",
            f"SOURce:POWer:LIMit:HIGH {power_limit}",
        )

        # wait until settings are made
        time.sleep(self.config.wait_sec_settings_effect)

        v_higher, i_higher, p_higher = self.get_uip_upper_limits()

        if (
            v_higher == voltage_limit
            and i_higher == current_limit
            and p_higher == power_limit
        ):
            logger.info(
                f"New upper voltage, current, power limits set: Umax = {voltage_limit} "
                f"V, Imax = {current_limit} A, Pmax = {power_limit} W"
            )

        else:
            raise PSI9000Error("Setting upper limits was not successful.")

    def set_lower_limits(
        self, voltage_limit: float = None, current_limit: float = None
    ) -> None:
        """
        Set the lower limits for voltage and current.
        After writing the values a check is performed if the values are set correctly.

        :param voltage_limit: is the lower voltage limit in V
        :param current_limit: is the lower current limit in A
        :raises PSI9000Error: if the limits are out of range
        """

        voltage_limit = (
            voltage_limit
            if voltage_limit is not None
            else self.config.voltage_lower_limit
        )
        current_limit = (
            current_limit
            if current_limit is not None
            else self.config.current_lower_limit
        )

        v_upper, i_upper, p_upper = self.get_uip_upper_limits()

        # Creates a new configclass object just to check the limits; will raise
        # ValueError if not within limits (see PSI9000Config.clean_values)
        dataclasses.replace(
            self.config,
            voltage_upper_limit=v_upper,
            current_upper_limit=i_upper,
            power_limit=p_upper,
            voltage_lower_limit=voltage_limit,
            current_lower_limit=current_limit,
        )

        self.com.write(
            f"SOURce:VOLTage:LIMit:LOW {voltage_limit}",
            f"SOURce:CURRent:LIMit:LOW {current_limit}",
        )

        v_lower, i_lower = self.get_ui_lower_limits()

        if v_lower == voltage_limit and i_lower == current_limit:
            logger.info(
                f"New lower voltage and current limits set: Umin = {voltage_limit} V, "
                f"Imin = {current_limit} A"
            )

        else:
            raise PSI9000Error("Setting lower limits was unsuccessful.")

    def get_ui_lower_limits(self) -> Tuple[float, float]:
        """
        Get the lower voltage and current limits. A lower power limit does not exist.

        :return: Umin in V, Imin in A
        """

        list_ret = self.com.query(
            "SOURce:VOLTage:LIMit:LOW?", "SOURce:CURRent:LIMit:LOW?"
        )
        assert len(list_ret) == 2
        ret = self._remove_units(list_ret)
        return ret[0], ret[1]

    def get_uip_upper_limits(self) -> Tuple[float, float, float]:
        """
        Get the upper voltage, current and power limits.

        :return: Umax in V, Imax in A, Pmax in W
        """

        list_ret = self.com.query(
            "SOURce:VOLTage:LIMit:HIGH?",
            "SOURce:CURRent:LIMit:HIGH?",
            "SOURce:POWer:LIMit:HIGH?",
        )
        assert len(list_ret) == 3
        ret = self._remove_units(list_ret)
        return ret[0], ret[1], ret[2]

    def check_master_slave_config(self) -> None:
        """
        Checks if the master / slave configuration and initializes if successful

        :raises PSI9000Error: if master-slave configuration failed
        """

        # verify that MS is enabled
        if self.com.query("SYSTem:MS:ENABle?") != "ON":
            logger.error("Master-slave-mode not enabled.")
            raise PSI9000Error("Master-slave-mode not enabled.")

        # verify that this device ist MASTER
        if self.com.query("SYSTem:MS:LINK?") != "MASTER":
            logger.error("Device is not Master.")
            raise PSI9000Error("Device is not Master.")

        # begin initialization
        self.com.write("SYSTem:MS:INITialisation")
        time.sleep(self.config.wait_sec_initialisation)

        # check for correct init
        if self.com.query("SYSTem:MS:CONDition?") != "INIT":
            logger.error("Master-slave initialisation failed.")
            raise PSI9000Error("Master-slave initialisation failed.")

        # read resulting master-slave nominal voltage and current
        ms_voltage, ms_current = self._remove_units(
            self.com.query("SYSTem:MS:NOMinal:VOLTage?", "SYSTem:MS:NOMinal:CURRent?")
        )

        # check for correct total voltage and current
        if (
            ms_current != self.MS_NOMINAL_CURRENT
            or ms_voltage != self.MS_NOMINAL_VOLTAGE
        ):
            err_msg = (
                f"Nominal voltage and current should be {self.MS_NOMINAL_VOLTAGE} V, "
                f"{self.MS_NOMINAL_CURRENT} A; but are {ms_voltage} V, {ms_current} A."
            )
            logger.error(err_msg)
            raise PSI9000Error(err_msg)

        # here the initialization is successful
        logger.info("Initialization of Master/Slave successful")

    @staticmethod
    def _remove_units(list_with_strings: Iterable[str]) -> Tuple[float, ...]:
        """
        Removes the last two characters of each string in the list and
        convert it to float (is only working for units with one character e.g. V, A, W)

        :param list_with_strings: list with return strings containing value and unit
        :return: list of floats without units
        """

        return tuple(float(value[:-2]) for value in list_with_strings)

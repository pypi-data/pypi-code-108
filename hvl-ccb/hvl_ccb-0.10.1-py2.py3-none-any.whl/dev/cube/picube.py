#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
A PICube is a BaseCube with build in Power Inverter
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from time import sleep, time
from typing import Optional

from hvl_ccb.configuration import configdataclass
from hvl_ccb.dev.cube import constants
from hvl_ccb.dev.cube.constants import PICubeTestParameterError, _CubeOpcEndpoint
from hvl_ccb.dev.cube.base import (
    BaseCube,
    BaseCubeConfiguration,
    BaseCubeOpcUaCommunication,
    BaseCubeOpcUaCommunicationConfig,
)
from hvl_ccb.utils.typing import Number
from hvl_ccb.utils.validation import validate_number

logger = logging.getLogger(__name__)


@configdataclass
class PICubeOpcUaCommunicationConfig(BaseCubeOpcUaCommunicationConfig):
    endpoint_name: _CubeOpcEndpoint = _CubeOpcEndpoint.PI_CUBE  # type: ignore


class PICubeOpcUaCommunication(BaseCubeOpcUaCommunication):
    @staticmethod
    def config_cls():
        return PICubeOpcUaCommunicationConfig


@configdataclass
class PICubeConfiguration(BaseCubeConfiguration):
    timeout_test_parameters: Number = 2.0

    def clean_values(self):
        super().clean_values()
        if self.timeout_test_parameters < 0:
            raise ValueError(
                "Timeout for setting test parameters needs to be not negative."
            )


@dataclass
class _TestParameter:
    """
    Class to access the test parameter. For the PICube it is possible to set
    a voltage target and specify the slope of the voltage ramp.
    """

    _handle: PICube
    tolerance: Number = 0.01  # tolerance is needed because of numerical precision

    @property
    def voltage(self) -> float:
        """
        Target voltage of the PICube.

        :return: target voltage in volt
        """
        display_value = float(self._handle.read(constants._Power.VOLTAGE_TARGET))
        power_setup = self._handle._power_setup
        logger.info(
            f"Test parameter: voltage is {display_value:_.2f} {power_setup.unit}"
        )
        return self._handle._apply_polarity(display_value / power_setup.scale)

    @voltage.setter
    def voltage(self, value: Number) -> None:
        """
        Target voltage of the PICube

        :param value: target voltage in volt
        :raises PICubeTestParameterError: if the value cannot be set within
            the given time
        """
        power_setup = self.power_setup
        if power_setup is None:
            return

        unit = power_setup.unit

        if self._handle.power_setup in constants.DC_POWER_SETUPS:
            if self._handle._polarity == constants.Polarity.POSITIVE:
                validate_number(
                    "voltage", value, (0, self._handle.voltage_max), logger=logger
                )
            else:
                validate_number(
                    "voltage", value, (self._handle.voltage_max, 0), logger=logger
                )
        else:
            validate_number(
                "voltage", value, (0, self._handle.voltage_max), logger=logger
            )

        voltage_opc = value * power_setup.scale

        self._handle.write(constants._Power.VOLTAGE_TARGET, abs(voltage_opc))

        start_time = time()
        rec_target_voltage = self.voltage
        while not (self._check_tolerance(value, rec_target_voltage, self.tolerance)):
            if (time() - start_time) >= self._handle.config.timeout_test_parameters:
                msg = (
                    f"Test parameters: voltage should be set to {value:_.2f} V, "
                    f"but is {rec_target_voltage:_.2f} V."
                )
                logger.error(msg)
                raise PICubeTestParameterError(msg)
            sleep(0.1)
            rec_target_voltage = self.voltage

        logger.info(f"Test parameters: voltage is set to {voltage_opc:_.2f} {unit}")

    @property
    def slope(self) -> float:
        """
        slope of the voltage ramp. While the value is always positive, the slope will
        be negative if the target voltage is below the current voltage.

        :return: slope in V/s
        """
        display_value = float(self._handle.read(constants._Power.VOLTAGE_SLOPE))
        power_setup = self._handle._power_setup
        logger.info(f"Test parameter: slope is {display_value:_.2f} {power_setup.unit}")
        return display_value / power_setup.scale

    @slope.setter
    def slope(self, value: Number) -> None:
        """
        slope of the voltage ramp. While the value is always positive, the slope will
        be negative if the target voltage is below the current voltage.

        :param value: slope in V/s
        :raises PICubeTestParameterError: if the value cannot be set within
            the given time
        """
        power_setup = self.power_setup
        if power_setup is None:
            return

        slope_max = power_setup.slope_max
        slope_min = power_setup.slope_min
        unit = power_setup.unit

        validate_number("slope", value, (slope_min, slope_max), logger=logger)

        slope_opc = value * power_setup.scale

        self._handle.write(constants._Power.VOLTAGE_SLOPE, slope_opc)

        start_time = time()
        rec_slope = self.slope  # tolerance is needed because of numerical precision
        while not (self._check_tolerance(value, rec_slope, self.tolerance)):
            if (time() - start_time) >= self._handle.config.timeout_test_parameters:
                msg = (
                    f"Test parameters: slope should be set to {value:_.2f} V/s, "
                    f"but is {rec_slope:_.2f} V/s."
                )
                logger.error(msg)
                raise PICubeTestParameterError(msg)
            sleep(0.1)
            rec_slope = self.slope

        logger.info(f"Test parameters: slope is set to {slope_opc:_.2f} {unit}/s")

    @property
    def power_setup(self) -> Optional[constants.PowerSetup]:
        """
        Checks if cube is in correct state and returns the power state.

        :return: Power Setup of PICube.
        """
        if self._handle._status is not constants.SafetyStatus.RED_OPERATE:
            logger.warning(
                f"To set test parameters, the PICube needs to be in "
                f"Status 'RED_OPERATE', but is in '{self._handle._status.name}'"
            )
            return None
        power_setup = self._handle._power_setup
        if power_setup in (constants.PowerSetup.NO_SOURCE,
                           constants.PowerSetup.EXTERNAL_SOURCE):
            logger.warning(
                f"It is not possible to set new test parameters while "
                f"the PICube is in '{power_setup}' mode."
            )
            return None
        return power_setup

    def _check_tolerance(
            self, set_value: Number, actual_value: Number, tol: Number
    ) -> bool:
        """
        Checks if the actual value is within the tolerance of the set value.

        :param set_value:
        :param actual_value:
        :param tol: value between 0 and 1
        :return: `True` if within the tolerance, otherwise `False`
        """
        if self._handle._polarity == constants.Polarity.NEGATIVE:
            value = (1 - tol) * set_value >= actual_value >= (1 + tol) * set_value
        else:
            value = (1 - tol) * set_value <= actual_value <= (1 + tol) * set_value
        return value


class PICube(BaseCube):
    """
    Variant of the BaseCube with build in Power Inverter
    """

    def __init__(self, com, dev_config=None):
        super().__init__(com, dev_config)
        self.test_parameter = _TestParameter(self)

    @staticmethod
    def default_com_cls():
        return PICubeOpcUaCommunication

    @staticmethod
    def config_cls():
        return PICubeConfiguration

    @property
    def operate(self) -> Optional[bool]:
        # this construct is necessary to keep mypy happy
        return super().operate

    @operate.setter
    def operate(self, state: bool) -> None:
        """
        Set operate state. If the state is RED_READY, this will turn on the high
        voltage and close the safety switches.
        If the state is RED_OPERATE and a status change to RED_READY is queried - with
        a measured output voltage above the voltage limit -- a warning is logged

        :param state: set operate state
        :raises CubeStatusChangeError: if `state=True` and cube is not in RED_READY or
            if `state=False` and cube is not in RED_OPERATE
        """

        if self.power_setup in constants.DC_POWER_SETUPS:
            voltage_limit = self.measurement_ch_3.noise_level
        elif self.power_setup in constants.AC_POWER_SETUPS:
            voltage_limit = self.measurement_ch_1.noise_level
        elif self.power_setup == constants.PowerSetup.POWER_INVERTER_220V:
            # TODO voltage_limit for PowerInverter_220, what is the return of actual
            #  voltage?
            #  Which value is returned?
            voltage_limit = 10
        else:
            voltage_limit = 0

        if (
            self.voltage_actual > voltage_limit
            and self._status is constants.SafetyStatus.RED_OPERATE
            and not state
        ):
            logger.warning(
                "The output voltage needs to be 0 V in order to change "
                "Status from RED_OPERATE to RED_READY."
            )
            return
        BaseCube.operate.fset(self, state)  # type: ignore

    @property
    def voltage_max(self) -> float:
        """
        Reads the maximum voltage of the setup and returns in V.

        :return: the maximum voltage of the setup in V.
        """
        power_setup = self._power_setup
        value = float(self.read(constants._Power.VOLTAGE_MAX))
        logger.info(
            f"Maximum Output Voltage with current Setup "
            f"is {value:_.2f} {power_setup.unit}"
        )
        value = value / power_setup.scale
        return self._apply_polarity(value)

    @property
    def voltage_actual(self) -> float:
        """
        Reads the actual measured voltage and returns the value in V.

        :return: the actual voltage of the setup in V.
        """
        power_setup = self._power_setup
        value = float(self.read(constants._Power.VOLTAGE_ACTUAL))
        logger.info(f"Actual Output Voltage is {value:_.2f} {power_setup.unit}")
        value = value / power_setup.scale
        return self._apply_polarity(value)

    @property
    def voltage_primary(self) -> float:
        """
        Read the current primary voltage at the output of the frequency converter
        (before transformer).

        :return: primary voltage in V
        """

        value = float(self.read(constants._Power.VOLTAGE_PRIMARY))
        logger.info(
            f"Primary Voltage at the Output of the Power Inverter is {value:_.2f} V"
        )
        return value

    @property
    def current_primary(self) -> float:
        """
        Read the current primary current at the output of the frequency converter
        (before transformer).

        :return: primary current in A
        """

        value = float(self.read(constants._Power.CURRENT_PRIMARY))
        logger.info(
            f"Primary Current at the Output of the Power Inverter is {value:_.2f} A"
        )
        return value

    @property
    def frequency(self) -> float:
        """
        Read the electrical frequency of the current PICube setup.

        :return: the frequency in Hz
        """

        value = float(self.read(constants._Power.FREQUENCY))
        logger.info(f"Output Frequency of the Power Inverter is {value} Hz")
        return value

    @property
    def _power_setup(self) -> constants.PowerSetup:
        """
        Return the power setup selected in the PICube's settings, without logging

        :return: the power setup
        """
        return constants.PowerSetup(self.read(constants._Power.SETUP))

    @property
    def power_setup(self) -> constants.PowerSetup:
        """
        Return the power setup selected in the PICube's settings.

        :return: the power setup
        """

        value = self._power_setup
        logger.info(
            f"Current programmed Power Setup of the PICube "
            f"is {value.name}"  # type: ignore
        )
        return value

    @property
    def _polarity(self) -> Optional[constants.Polarity]:
        value = None
        if self._power_setup in constants.DC_POWER_SETUPS:
            value = constants.Polarity(self.read(constants._Power.POLARITY))
        return value

    @property
    def polarity(self) -> Optional[constants.Polarity]:
        """
        Polarity of a DC setup.
        :return: if a DC setup is programmed the polarity is returned, else None.
        """

        value = self._polarity
        if value is not None:
            logger.info(
                f"The polarity of the experiment setup is {value.name}"  # type: ignore
            )
        else:
            logger.info("Only DC-Setups have a polarity.")
        return value

    def _apply_polarity(self, value: Number) -> Number:
        if (self._power_setup in constants.DC_POWER_SETUPS and
                self._polarity == constants.Polarity.NEGATIVE):
            value = -value
        return value

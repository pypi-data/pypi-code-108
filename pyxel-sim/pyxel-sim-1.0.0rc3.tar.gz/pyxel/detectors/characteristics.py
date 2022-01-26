#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
import typing as t

import numpy as np

from pyxel.util.memory import get_size


class Characteristics:
    """Characteristic attributes of the detector.

    Parameters
    ----------
    quantum_efficiency: float, optional
        Quantum efficiency.
    charge_to_volt_conversion: float, optional
        Sensitivity of charge readout. Unit: V/e-
    pre_amplification: float, optional
        Gain of pre-amplifier. Unit: V/V
    full_well_capacity: float, optional
        Full well capacity. Unit: e-
    adc_voltage_range: tuple of floats, optional
        ADC voltage range. Unit: V
    adc_bit_resolution: int, optional
        ADC bit resolution.
    """

    def __init__(
        self,
        quantum_efficiency: t.Optional[float] = None,  # unit: NA
        charge_to_volt_conversion: t.Optional[float] = None,  # unit: volt/electron
        pre_amplification: t.Optional[float] = None,  # unit: V/V
        full_well_capacity: t.Optional[float] = None,  # unit: electron
        adc_bit_resolution: t.Optional[int] = None,
        adc_voltage_range: t.Optional[t.Tuple[float, float]] = None,  # unit: V
    ):
        if quantum_efficiency and not (0.0 <= quantum_efficiency <= 1.0):
            raise ValueError("'quantum_efficiency' must be between 0.0 and 1.0.")
        if charge_to_volt_conversion and not (
            0.0 <= charge_to_volt_conversion <= 100.0
        ):
            raise ValueError(
                "'charge_to_volt_conversion' must be between 0.0 and 100.0."
            )
        if pre_amplification and not (0.0 <= pre_amplification <= 10000.0):
            raise ValueError("'pre_amplification' must be between 0.0 and 10000.0.")
        if full_well_capacity and not (0.0 <= full_well_capacity <= 1.0e7):
            raise ValueError("'full_well_capacity' must be between 0 and 1e7.")
        if adc_bit_resolution and not (4 <= adc_bit_resolution <= 64):
            raise ValueError("'adc_bit_resolution' must be between 4 and 64.")
        if adc_voltage_range and not len(adc_voltage_range) == 2:
            raise ValueError("Voltage range must have length of 2.")

        self._quantum_efficiency = quantum_efficiency
        self._charge_to_volt_conversion = charge_to_volt_conversion
        self._pre_amplification = pre_amplification
        self._full_well_capacity = full_well_capacity
        self._adc_voltage_range = adc_voltage_range
        self._adc_bit_resolution = adc_bit_resolution

        self._numbytes = 0

    @property
    def quantum_efficiency(self) -> float:
        """Get Quantum efficiency."""
        if self._quantum_efficiency:
            return self._quantum_efficiency
        else:
            raise ValueError(
                "'quantum_efficiency' not specified in detector characteristics."
            )

    @quantum_efficiency.setter
    def quantum_efficiency(self, value: float) -> None:
        """Set Quantum efficiency."""
        if np.min(value) < 0.0 and np.max(value) <= 1.0:
            raise ValueError("'quantum_efficiency' values must be between 0.0 and 1.0.")

        self._quantum_efficiency = value

    @property
    def charge_to_volt_conversion(self) -> float:
        """Get charge to volt conversion parameter."""
        if self._charge_to_volt_conversion:
            return self._charge_to_volt_conversion
        else:
            raise ValueError(
                "'charge_to_volt_conversion' not specified in detector characteristics."
            )

    @charge_to_volt_conversion.setter
    def charge_to_volt_conversion(self, value: float) -> None:
        """Set charge to volt conversion parameter."""
        if not (0.0 <= value <= 100.0):
            raise ValueError(
                "'charge_to_volt_conversion' must be between 0.0 and 100.0."
            )
        self._charge_to_volt_conversion = value

    @property
    def pre_amplification(self) -> float:
        """Get voltage pre-amplification gain."""
        if self._pre_amplification:
            return self._pre_amplification
        else:
            raise ValueError(
                "'pre_amplification' not specified in detector characteristics."
            )

    @pre_amplification.setter
    def pre_amplification(self, value: float) -> None:
        """Set voltage pre-amplification gain.."""
        if not (0.0 <= value <= 10000.0):
            raise ValueError("'pre_amplification' must be between 0.0 and 10000.0.")

        self._pre_amplification = value

    @property
    def adc_bit_resolution(self) -> int:
        """Get bit resolution of the Analog-Digital Converter."""
        if self._adc_bit_resolution:
            return self._adc_bit_resolution
        else:
            raise ValueError(
                "'adc_bit_resolution' not specified in detector characteristics."
            )

    @adc_bit_resolution.setter
    def adc_bit_resolution(self, value: int) -> None:
        """Set bit resolution of the Analog-Digital Converter."""
        self._adc_bit_resolution = value

    @property
    def adc_voltage_range(self) -> t.Tuple[float, float]:
        """Get voltage range of the Analog-Digital Converter."""
        if self._adc_voltage_range:
            return self._adc_voltage_range
        else:
            raise ValueError(
                "'adc_voltage_range' not specified in detector characteristics."
            )

    @adc_voltage_range.setter
    def adc_voltage_range(self, value: t.Tuple[float, float]) -> None:
        """Set voltage range of the Analog-Digital Converter."""
        self._adc_voltage_range = value

    @property
    def full_well_capacity(self) -> float:
        """Get Full well capacity."""
        if self._full_well_capacity:
            return self._full_well_capacity
        else:
            raise ValueError(
                "'full_well_capacity' not specified in detector characteristics."
            )

    @full_well_capacity.setter
    def full_well_capacity(self, value: float) -> None:
        """Set Full well capacity."""
        if value not in range(10000001):
            raise ValueError("'full_well_capacity' must be between 0 and 1e+7.")

        self._full_well_capacity = value

    @property
    def numbytes(self) -> int:
        """Recursively calculates object size in bytes using Pympler library.

        Returns
        -------
        int
            Size of the object in bytes.
        """
        self._numbytes = get_size(self)
        return self._numbytes

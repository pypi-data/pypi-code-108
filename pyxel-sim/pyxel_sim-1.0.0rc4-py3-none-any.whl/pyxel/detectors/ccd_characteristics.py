#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
from pyxel.detectors import Characteristics


class CCDCharacteristics(Characteristics):
    """Characteristic attributes of a :term:`CCD` detector.

    Parameters
    ----------
    quantum_efficiency: float
        Quantum efficiency.
    charge_to_volt_conversion: float
        Sensitivity of charge readout. Unit: V/e-
    pre_amplification: float
        Gain of pre-amplifier. Unit: V/V
    adc_gain: float
        Gain of the Analog-Digital Converter. Unit: ADU/V
    full_well_capacity: float
        Full well capacity. Unit: e-
    """

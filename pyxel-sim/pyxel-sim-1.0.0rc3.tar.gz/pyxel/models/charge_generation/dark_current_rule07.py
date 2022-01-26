#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Simple models to generate charge due to dark current process."""
import typing as t

import numpy as np

from pyxel.detectors import CMOS
from pyxel.util import temporary_random_state


def lambda_e(lambda_cutoff: float) -> float:
    """Compute lambda_e.

    Parameters
    ----------
    lambda_cutoff: int
        Cut-off wavelength of the detector.

    Returns
    -------
    le: float
    """
    lambda_scale = 0.200847413  # um
    lambda_threshold = 4.635136423  # um
    pwr = 0.544071282
    if lambda_cutoff < lambda_threshold:
        le = lambda_cutoff / (
            1
            - ((lambda_scale / lambda_cutoff) - (lambda_scale / lambda_threshold))
            ** pwr
        )
    else:
        le = lambda_cutoff
    return le


def compute_mct_dark_rule07(pitch: float, temperature: float, cut_off: float) -> float:
    """Compute dark current.

    Parameters
    ----------
    pitch: float
        the x and y dimension of the pixel in micrometer
    temperature: float
        the devices temperature
    cut_off: float
        the detector wavelength cut-off in micrometer

    Returns
    -------
    dark_current: float
        In e-/pixel/s.
    """
    c = 1.16  # activation energy factor
    q = 1.602e-19  # Charge of one electron, unit= A.s
    k = 1.3806504e-23  # Constant of Boltzmann, unit = m2.kg/s2/K

    j0 = 8367  # obtained through fit of experimental data, see paper

    e_c = 1.24 / lambda_e(
        cut_off
    )  # [eV] the optical gap extracted from the mid response cutoff

    rule07 = j0 * np.exp(-c * q * e_c / (k * temperature))  # A/cm3

    amp_to_eps = 6.242e18  # e-/s
    um2_to_cm2 = 1.0e-8
    factor = amp_to_eps * pitch * pitch * um2_to_cm2  # to convert Amp/cm2 in e/pixel/s
    dc = rule07 * factor

    return dc


@temporary_random_state
def dark_current_rule07(
    detector: CMOS,
    cutoff_wavelength: float = 2.5,  # unit: um
    seed: t.Optional[int] = None,
) -> None:
    """Generate charge from dark current process.

    Based on Rule07 paper by W.E. Tennant Journal of Electronic Materials volume 37, pages1406–1410 (2008).

    Parameters
    ----------
    detector: Detector
    cutoff_wavelength: float
        Cutoff wavelength. Unit: um
    seed: int, optional
    """
    # TODO: investigate on the knee of rule07 for higher 1/le*T values
    if not isinstance(detector, CMOS):
        raise TypeError("Expecting a CMOS object for detector.")
    if not (1.7 <= cutoff_wavelength <= 15.0):
        raise ValueError("'cutoff' must be between 1.7 and 15.0.")

    geo = detector.geometry

    pitch = geo.pixel_vert_size  # assumes a square pitch
    temperature = detector.environment.temperature

    dc = compute_mct_dark_rule07(
        pitch=pitch, temperature=temperature, cut_off=cutoff_wavelength
    )
    ne = dc * detector.time_step

    # The number of charge generated with Poisson distribution using rule07 empiric law for lambda
    charge_number = np.random.poisson(ne, size=(geo.row, geo.col)).astype(float)

    detector.charge.add_charge_array(charge_number)

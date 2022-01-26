#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

import astropy.constants as const
import astropy.units as u
import numpy as np

from pyxel.detectors import MKID


def apply_dead_time_filter(phase_2d: np.ndarray, maximum_count: float) -> np.ndarray:
    """Apply dead time filter.

    Parameters
    ----------
    phase_2d : ndarray
    maximum_count : float

    Returns
    -------
    ndarray
    """
    phase_clipped_2d = np.clip(phase_2d, a_min=None, a_max=maximum_count)

    return phase_clipped_2d


# TODO: more documentation (Enrico). See #324.
def dead_time_filter(
    detector: MKID,
    tau_0: float = 4.4 * 1.0e-7,
    n_0: float = 1.72 * 1.0e10,
    t_c: float = 1.26,
    v: float = 30.0,
    t_op: float = 0.3,
    tau_pb: float = 2.8 * 1.0e-10,
    tau_esc: float = 1.4 * 1.0e-10,
    tau_sat: float = 1.0e-3,
) -> None:
    """Dead time filter.

    The underlying physics of this model is described in :cite:p:`PhysRevB.104.L180506`;
    more information can be found on the website :cite:p:`Mazin`.

    Parameters
    ----------
    detector: MKID
        Pyxel Detector :term:`MKID` object.
    tau_0 : float
        Material dependent characteristic time for the electron-phonon coupling. Unit: s
    n_0 : float
        Material dependent single spin density of states at
        the Fermi-level. Unit: um^-3 eV^-1
    t_c : float
        Material dependent critical temperature. Unit: K
    v : float
        Superconducting volume. Unit: um^3
    t_op : float
        Temperature. Unit: K
    tau_pb : float
        Phonon pair-breaking time. Unit: s
    tau_esc : float
        Phonon escape time. Unit: s
    tau_sat : float
        Saturation time. Unit: s
    """
    # Validation phase
    if not isinstance(detector, MKID):
        # Later, this will be checked in when YAML configuration file is parsed
        raise TypeError("Expecting an `MKID` object for 'detector'.")

    # Boltzmann's constant [eV K^-1]
    boltzmann_cst: float = const.k_B.to(u.eV / u.K).value

    # Compute superconducting gap energy
    delta = 1.76 * boltzmann_cst * t_c  # type: float

    # Compute number of quasiparticles in a superconducting volume V
    # TODO: check that T << (delta / boltzmann_cst)
    n_qp = (
        2.0
        * v
        * n_0
        * np.sqrt(2.0 * np.pi * boltzmann_cst * t_op * delta)
        * np.exp(-delta / (boltzmann_cst * t_op))
    )  # type: float

    # Compute recombination constant
    recombination_cst = (
        tau_0 * n_0 * (boltzmann_cst * t_c) ** 3 / (2.0 * delta ** 2)
    )  # type: float

    # Compute intrinsic quasiparticle lifetime with respect to recombination
    tau_qp = v / (recombination_cst * n_qp)  # type: float

    # Compute apparent quasi-particle lifetime, without saturation lifetime
    # tau_apparent = 1. / (2. / (tau_qp * (1. + (char.tau_esc / char.tau_pb))))

    # Compute apparent quasi-particle lifetime, including saturation lifetime
    tau_apparent_sat = 1.0 / (
        2.0 / (tau_qp * (1.0 + (tau_esc / tau_pb))) + (1.0 / tau_sat)
    )  # type: float

    dead_time = tau_apparent_sat

    phase_2d = apply_dead_time_filter(
        phase_2d=detector.phase.array,
        maximum_count=1.0 / dead_time,
    )

    detector.phase.array = phase_2d

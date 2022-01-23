# BSD 3-Clause License
#
# Copyright (c) 2021, Austin Cummings
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''Cherenkov functions

.. autosummary::
   :toctree:
   :recursive:

   Cherenkov_threshold
   Cherenkov_angle
   Cherenkov_photons

'''

import numpy as np
from . import constants as const
from . import atmosphere as atm


def Cherenkov_threshold(z, wavelength):
    """Calculates the threshold energy for Cherenkov

    Calculates the threshold energy for Cherenkov production by electrons at a given altitude (in km) and wavelength (in nm)
    Cherenkov theory originally given in: Cherenkov, P. A. (1934). "Visible emission of clean liquids by action of gamma radiation".
    Doklady Akademii Nauk SSSR. 2: 451.

    Parameters
    ----------
    z : float
        altitude in km
    wavelength : float
        wavelength in nm

    Returns
    -------
    float
        Cherenkov threshold energy (for electrons) in MeV
    """
    threshold_energy = const.electron_mass * np.sqrt(1 / (1 - 1 / (atm.index_of_refraction(z, wavelength)**2)))

    return threshold_energy


def Cherenkov_angle(z, wavelength, beta):
    """ Calculates Cherenkov angle.

    Calculates the angle at which the Cherenkov emission is emitted (in degrees) at a given altitude (in km), wavelength (in nm), and beta value (v/c)
    Cherenkov theory originally given in: Cherenkov, P. A. (1934). "Visible emission of clean liquids by action of gamma radiation".
    Doklady Akademii Nauk SSSR. 2: 451.

    Parameters
    ----------
    z : float
        altitude in km
    wavelength : float
        wavelength in nm
    beta : float
        beta = v/c

    Returns
    -------
    float
        Cherenkov angle in degrees
    """
    theta_Cherenkov = (180 / np.pi) * np.arccos(1 / (beta * atm.index_of_refraction(z, wavelength)))

    return theta_Cherenkov


def Cherenkov_photons(z, wavelength, beta):
    """Calculates number of Cherenkov photons

    Calculate the number of Cherenkov photons produced by a single charged particle per unit wavelength and distance (m^-2)
    for a given altitude (in km), wavelength (in nm), and beta value (v/c)
    Theory given in: Tamm, I.E.; Frank, I.M. (1937), Dokl. Akad. Nauk SSSR, 14: 107

    Parameters
    ----------
    z : ArrayLike
        altitude in km
    wavelength : ArrayLike
        wavelength in nm
    beta : ArrayLike
        beta = v/c

    Returns
    -------
    ArrayLike
        the number of differential Cherenkov photons produced by a single electron per unit distance (in m) and wavelength (in m)
    """
    n1 = atm.index_of_refraction(z, wavelength)

    if isinstance(beta, np.ndarray) and isinstance(wavelength, np.ndarray):
        dNdLdw = ((2 * np.pi * const.alpha_fsc) / (wavelength[None, None, :] * 1e-9)**2) * (1 - 1 / (beta[:, :, None] * n1[:, None, :])**2)
    else:
        dNdLdw = ((2 * np.pi * const.alpha_fsc) / (wavelength * 1e-9)**2) * (1 - 1 / (beta * n1)**2)

    return dNdLdw

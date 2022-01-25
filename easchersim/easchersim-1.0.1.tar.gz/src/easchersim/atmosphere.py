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


''' Atmospheric Functions

.. autosummary::
   :toctree:
   :recursive:

   atmospheric_extinction_coefficient
   atmos_density
   moliere_radius
   number_density
   index_of_refraction
   rayleigh_extinction_coefficient
   optical_depth
   slant_X_from_L_table

'''

import numpy as np
from scipy.interpolate import griddata
from scipy import integrate

from . import constants as const
from . import geometry as geo


def atmospheric_extinction_coefficient(file):
    r"""Loads in 2D array of atmospheric extinction coefficients from predefined file (over altitude and wavelength).

    Base implementation uses the results of L. Elterman. Number Tech. Rep. AFCRL-68-0153. 1968.

    Parameters
    ----------
        file: str
            file containing atmospheric extinction coefficients over altitude and wavelength

    Returns
    -------
        list
            wavelength in nm, altitudes in km, coefficients in m^-1
    """

    # Load wavelengths in nm
    wavelengths = np.loadtxt(file, delimiter=',', max_rows=1)

    # Load altitudes in km
    altitudes = np.loadtxt(file, delimiter=',', skiprows=1, max_rows=1)

    # Load in extinction coefficients in km^-1
    coefficients = np.loadtxt(file, delimiter=',', skiprows=2)

    # Remove any 0 values from array
    coefficients[coefficients == 0.0] = 1e-10

    # Convert to m^-1 and take the logarithm to smooth the data
    coefficients = np.log(coefficients / 1000)

    return [wavelengths, altitudes, coefficients]


def atmos_density(z):
    """Calculates the atmospheric density (in g/cm^3) of the atmosphere using Linsley's model for input altitude(s) (in km)

    Parameters
    ----------
        z: float
            altitude in km

    Returns
    -------
        float
            atm density in g/cm^3
    """

    # Find the appropriate atmospheric layer for the given altitude(s)
    if isinstance(z, np.ndarray):
        layers = np.argmax(np.less(z[:, None], const.atmos_layer_boundaries[None, :]), axis=1)

    else:
        layers = np.argmax(np.less(z, const.atmos_layer_boundaries))

    # Calculate the atmospheric density
    density = np.where(layers < 4, (const.atmos_b[layers] / const.atmos_c[layers]) * np.exp(-z * 1e5 / const.atmos_c[layers]), 1 / const.atmos_c[layers])

    # Above the maximum altitude in the model, the density is 0
    density[z > const.z_max] = 0

    return density


def moliere_radius(z):
    """Calculates the Moliere radius.

    Calculates the Moliere radius (the radius within which 90% of the shower energy deposition is contained: in km) at a given altitude (in km)
    as parameterized by: Dova, M. T., Epele, L. N., & Mariazzi, A. G. 2003, Astropart. Phys., 18, 351

    Parameters
    ----------
        z: float
            altitude in km

    Returns
    -------
        float
            Moliere radius in km
    """

    # Calculate the atmospheric density
    atmospheric_density = atmos_density(z)

    # Calculate the Moliere radius
    moliere_radius = 1e-5 * 9.6 / atmospheric_density

    return moliere_radius


def number_density(z):
    """Calculates the particle number density (in particles/cm^3) of the atmosphere for input altitude(s) (in km)

    Parameters
    ----------
        z: float
            altitude in km

    Returns
    -------
        float
            particle number density (in particles/cm^3)
    """

    return atmos_density(z) * (const.N_A / const.mm_air) * 1e-3


def index_of_refraction(z, wavelength):
    """Calculates the index of refraction.

    Calculates the index of refraction for input altitude(s) (in km) and wavelength(s) (in nm)
    Baseline approximation of the index of refraction, as given in:
    Handbook of Chemistry and Physics, 67th Edition, R.C. Weast ed. (The Chemical Rubber Co., Cleveland, 1986) E373
    
    Wavelength correction to the index of refraction as given in K. Bernlohr, Astropart. Phys., 30:149-158, 2008.

    Parameters
    ----------
        z: float
            altitude in km
        wavelength: float
            wavelength in nm

    Returns
    -------
        float
            index of refraction
    """

    n1 = 1 + (0.283e-3) * atmos_density(z) / atmos_density(0)

    if isinstance(z, np.ndarray) and isinstance(wavelength, np.ndarray):
        n = 1 + (n1[:, None] - 1) * (0.967 + 0.033 * (400 / wavelength[None, :])**2.5)
    else:
        n = 1 + (n1 - 1) * (0.967 + 0.033 * (400 / wavelength)**2.5)

    return n


def rayleigh_extinction_coefficient(z, wavelength):
    """ Calculates the Rayleigh extinction coefficient.

    Calculates the Rayleigh extinction coefficient (in m^-1) given input altitude(s) (in km) and wavelength(s) (in nm) a, 375-384
    King correction factor (Fk) to account for depolarization. Constant results from:
    R. Thalman, K. J. Zarzana, M. A. Tolbert, and R. Volkamer., Air. J. Quant. Spectrosc. Radiat. Transf., (147):171-177, 2014.
    
    Lord Rayleigh, The London, Edinburgh, and Dublin Philosophical Magazine and Journal of Science, 47:287

    Parameters
    ----------
        z: float
            altitude in km
        wavelength: float
            wavelength in nm

    Returns
    -------
        float
            Rayleigh extinction coefficient (in m^-1)
    """

    n2 = index_of_refraction(z, wavelength)**2
    N = number_density(z) * 1e6

    Fk = 1.0608

    alpha_Rayleigh = 24 * np.pi**3 * (((n2 - 1) / (n2 + 2))**2) * Fk * (1 / ((wavelength * 1e-9)**4)) * (1 / N[:, None])

    return alpha_Rayleigh


def optical_depth(data_wavelength, data_altitude, data_extinction_coefficients, wavelength_bins, L_bins, det_alt, theta_D, Rayleigh_flag):

    """Calculates the optical depth.

    Calculates the optical depth (tau: unitless) between emission and detection given distance along trajectory (in km), wavelength (in nm)
    and detector viewing angle (in degrees). Light is attenuated by e^(-tau(z,w))
    Takes in a boolean flag for whether to consider attenuation above 50km altitudes
    Ensure that the input wavelength bins do not exceed the bounds of the data (270nm-4000nm for Elterman 1968)

    Parameters
    ----------
    data_wavelength : ArrayLike
        wavelength of input extinction coefficient data in nm
    data_altitude : ArrayLike
        altitude of input extinction coefficient data in km
    data_extinction_coefficients : ArrayLike
        input extinction coefficient data for (wavelength, altitude)
    wavelength_bins : ArrayLike
        wavelength bins on which to calculate the optical depth
    L_bins : ArrayLike
        distance bins along the shower trajectory on which to calculate the optical depth in km
    det_alt : float
        detector altitude in km
    theta_D : float
        detector viewing angle in degrees
    Rayleigh_flag : bool
        true if consider attenuation above 50km otherwise false

    Returns
    -------
    ArrayLike
        optical depth for the given (wavelength_bins, L_bins) (tau: unitless)
    """

    # Flip the input distance bins because the optical depth must be calculated FROM the detector
    L_bins = L_bins[::-1]

    data_wavelength, data_altitude = np.meshgrid(data_wavelength, data_altitude)
    data_extinction_coefficients = data_extinction_coefficients.T

    # Calculate the altitudes of the distances along the trajectory
    altitude_bins = geo.z_from_L(L_bins, theta_D, det_alt)

    wavelength_bins, altitude_bins = np.meshgrid(wavelength_bins, altitude_bins)

    # 2D interpolation of the extinction coefficients
    # If Rayleigh_flag == True, above 50km, consider ONLY Rayleigh scattering
    # If False, no scattering above 50km
    if Rayleigh_flag:
        extinction_coefficients = np.where(altitude_bins > 50, rayleigh_extinction_coefficient(altitude_bins[:, 0], wavelength_bins[0]), np.exp(griddata((data_wavelength.flatten(), data_altitude.flatten()), data_extinction_coefficients.flatten(), (wavelength_bins, altitude_bins), method='cubic', fill_value=0)))
        extinction_coefficients[altitude_bins > const.alt_max] = 0
    else:
        extinction_coefficients = np.exp(griddata((data_wavelength.flatten(), data_altitude.flatten()), data_extinction_coefficients.flatten(), (wavelength_bins, altitude_bins), method='cubic', fill_value=0))
        extinction_coefficients[altitude_bins > 50] = 0

    # Cumulatively integrate the extinction coefficients along the trajectory
    optical_depth = -integrate.cumtrapz(extinction_coefficients.T, L_bins * 1e3, axis=1, initial=0)
    optical_depth = np.flip(optical_depth, axis=1)

    return optical_depth


def slant_X_from_L_table(L_bins, det_alt, theta_D):
    """Calculates the grammage profile (in g/cm^2) along the trajectory, given the detector altitude (in km)
    and the detector viewing angle (in degrees)

    Parameters
    ----------
    L_bins : ArrayLike
        distance bins along the shower trajectory on which to calculate the slant depth in km
    det_alt : float
        detector altitude in km
    theta_D : float
        detector viewing angle in degrees

    Returns
    -------
    list
        grammage profile in g/cm^2
    """

    # Calculating a finer spacing of the distance bins along the trajectory
    L_bins = np.linspace(min(L_bins), max(L_bins), 10000)

    # Calculating the altitudes and densities of the positions along the trajectory
    altitude_bins = geo.z_from_L(L_bins, theta_D, det_alt)

    density = atmos_density(altitude_bins)

    # Integrating the grammage along the trajectory
    grammage = integrate.cumtrapz(density, L_bins * 1e5, initial=0)

    return [L_bins, grammage]

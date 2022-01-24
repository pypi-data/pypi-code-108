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

''' Geometric Functions

.. autosummary::
   :toctree:
   :recursive:

   Earth_limb_theta_D
   theta_D_from_theta_EE
   theta_EE_from_theta_D
   theta_AE_from_theta_D
   z_from_L
   L_from_z
   ellipse_focii
   ellipse_coordinates

'''

import numpy as np
from . import constants as const


def Earth_limb_theta_D(det_alt):
    """Calculates the detector viewing angle (the angle between the trajectory and the detector doward zenith: in degrees)
       where the Earth's limb occurs given the detector altitude (in km)

    Parameters
    ----------
    det_alt : float
        detector altitude in km

    Returns
    -------
    float
        detector viewing angle in degrees
    """
    theta_D = (180 / np.pi) * np.arcsin(const.R_Earth / (const.R_Earth + det_alt))

    return theta_D


def theta_D_from_theta_EE(det_alt, theta_EE):
    """Calculates the detector viewing angle (the angle between the trajectory and the detector doward zenith: in degrees)
    given the Earth emergence angle (the angle between the Earth horizontal and the trajectory: in degrees)
    and the altitude of the detector (in km)

    Parameters
    ----------
    det_alt : float
        detector altitude in km
    theta_EE : float
        earth emergence angle in degrees

    Returns
    -------
    float
        detector viewing angle in degrees
    """
    theta_EE = theta_EE * (np.pi / 180)
    theta_D = (180 / np.pi) * np.arcsin((const.R_Earth / (const.R_Earth + det_alt)) * np.sin(np.pi / 2 + theta_EE))

    return theta_D


def theta_EE_from_theta_D(det_alt, theta_D):
    """Calculates the Earth emergence angle (the angle between the Earth horizontal and the trajectory: in degrees)
    of the below limb event given the detector viewing angle (the angle between the trajectory and the detector doward zenith: in degrees)
    and altitude of the detector (in km)

    Parameters
    ----------
    det_alt : float
        detector altitude in km
    theta_D : [loat
        detector viewing angle in degrees

    Returns
    -------
    float
        Earth emergence angle in degrees
    """
    theta_D = theta_D * (np.pi / 180)
    theta_EE = (180 / np.pi) * (np.arccos(((const.R_Earth + det_alt) / const.R_Earth) * np.sin(theta_D)))

    return theta_EE


def theta_AE_from_theta_D(det_alt, theta_D):
    """Calculates the atmosphere entrance angle (the angle between the downwards CR trajectory and the atmosphere normal: in degrees)
    given the detector altitude (in km) and the detector viewing angle (the angle between the trajectory and the detector doward zenith: in degrees)

    Parameters
    ----------
    det_alt : float
        detector altitude in km
    theta_D : float
        detector viewing angle in degrees

    Returns
    -------
    float
        atmospheric entrance angle in degrees
    """
    theta_D = theta_D * (np.pi / 180)
    theta_AE = (180 / np.pi) * np.arcsin(((const.R_Earth + det_alt) / (const.R_Earth + const.alt_max)) * np.sin(theta_D))

    return theta_AE


def z_from_L(L, theta_D, det_alt):
    """Calculates the altitude (in km) given the distance along the trajectory (in km) and the
    detector viewing angle (the angle between the trajectory and the detector doward zenith: in degrees)

    Parameters
    ----------
    L : float
        distance alog shower axis in km
    theta_D : float
        detector viewing angle in degrees
    det_alt : float
        detector altitude in km

    Returns
    -------
    float
        altitude in km
    """
    theta_D_Earth_limb = Earth_limb_theta_D(det_alt)

    if theta_D > theta_D_Earth_limb:
        theta_AE = theta_AE_from_theta_D(det_alt, theta_D) * (np.pi / 180)
        z = np.sqrt((const.R_Earth + const.alt_max)**2 + L**2 - 2 * L * (const.R_Earth + const.alt_max) * np.cos(theta_AE)) - const.R_Earth
    else:
        theta_EE = theta_EE_from_theta_D(det_alt, theta_D) * (np.pi / 180)
        z = np.sqrt(const.R_Earth**2 + L**2 + 2 * const.R_Earth * L * np.sin(theta_EE)) - const.R_Earth

    return z


def L_from_z(z, theta_D, det_alt):
    """Calculates the distance along the trajectory (in km) given an altitude (in km) and the
    detector viewing angle (the angle between the trajectory and the detector doward zenith: in degrees)

    Parameters
    ----------
    z : float
        altitude in km
    theta_D : float
        detector viewing angle in degrees
    det_alt : float
        detector altitude in km

    Returns
    -------
    float
        distance along shower axis in km
    """
    theta_D_Earth_limb = Earth_limb_theta_D(det_alt)

    if theta_D > theta_D_Earth_limb:
        theta_AE = theta_AE_from_theta_D(det_alt, theta_D) * (np.pi / 180)
        a = 1
        b = -2 * (const.R_Earth + const.alt_max) * np.cos(theta_AE)
        c = (const.R_Earth + const.alt_max)**2 - (const.R_Earth + z)**2
        root_1 = (-b - np.sqrt(b**2 - 4 * a * c)) / (2 * a)
        root_2 = (-b + np.sqrt(b**2 - 4 * a * c)) / (2 * a)
    else:
        theta_EE = theta_EE_from_theta_D(det_alt, theta_D) * (np.pi / 180)
        a = 1
        b = 2 * const.R_Earth * np.sin(theta_EE)
        c = const.R_Earth**2 - (z + const.R_Earth)**2
        root_1 = (-b - np.sqrt(b**2 - 4 * a * c)) / (2 * a)
        root_2 = (-b + np.sqrt(b**2 - 4 * a * c)) / (2 * a)

    return max(np.array([root_1, root_2]))


def ellipse_focii(Ls, L_detector, electron_zenith, Cherenkov_angle):
    """Calculates the minor and major focii (in km) of the ellipse generated on the detection plane (assuming the plane normal to the shower incidence)
    given the distance of the emission point from the shower starting point (in km), the detection plane distance (in km),
    the electron zenith angle with respect to the shower axis (in degrees), and the Cherenkov angle (in degrees)

    Parameters
    ----------
    Ls : ArrayLike
        distance along shower trajectory in km
    L_detector : float
        distance from shower starting point to detection plane in km
    electron_zenith : ArrayLike
        zenith angles of electrons with respect to the shower axis in degrees
    Cherenkov_angle : ArrayLike
        Cherenkov angle in degrees

    Returns
    -------
    ArrayLike
        minor and major focii of the Cherenkov ring projected on the detection plane in km
    """

    electron_zenith, Cherenkov_angle = (np.pi / 180) * electron_zenith, (np.pi / 180) * Cherenkov_angle

    minor_foci = (L_detector - Ls[None, :]) * (np.tan(Cherenkov_angle[None, :]) / np.cos(electron_zenith)) * np.sqrt(1 + np.sin(electron_zenith) / (1 - np.tan(electron_zenith)**2 * np.tan(Cherenkov_angle[None, :])**2))
    major_foci = minor_foci / np.sqrt(1 - np.tan(electron_zenith)**2 * np.tan(Cherenkov_angle[None, :])**2)

    return [minor_foci, major_foci]


def ellipse_coordinates(Ls, L_detector, electron_zenith, Cherenkov_angle, Cherenkov_azimuth):
    """Calculates the x and y coordinates of the ellipse generated on the detection plane (assuming the plane normal to the shower incidence)
    given the distance of the emission point from the shower starting point (in km), the detection plane distance (in km),
    the electron zenith angle with respect to the shower axis (in degrees), and the Cherenkov angle (in degrees)

    Parameters
    ----------
    Ls : ArrayLike
        distance along shower trajectory in km
    L_detector : float
        distance from shower starting point to detection plane in km
    electron_zenith : ArrayLike
        zenith angles of electrons with respect to the shower axis in degrees
    Cherenkov_angle : ArrayLike
        Cherenkov angle in degrees
    Cherenkov_azimuth : ArrayLike
        azimuth angles about the Cherenkov ring in degrees

    Returns
    -------
    ArrayLike
        x,y coordinates of ellipses generated by Cherenkov rings projected on the detection plane
    """

    # Calculating the major and minor focii of the generated ellipse
    focii = ellipse_focii(Ls, L_detector, electron_zenith, Cherenkov_angle)
    minor_foci, major_foci = focii[0], focii[1]

    electron_zenith, Cherenkov_angle = (np.pi / 180) * electron_zenith, (np.pi / 180) * Cherenkov_angle
    
    # Using the azimuth bin size difference to smear the coordinates
    dtheta = np.diff(Cherenkov_azimuth)[0]/2

    ellipse_x = (L_detector - Ls[None, :, None]) * np.tan(electron_zenith[:, :, None]) + (L_detector - Ls[None, :, None]) * ((np.sin(electron_zenith[:, :, None]) / np.cos(electron_zenith[:, :, None])**2) * np.tan(Cherenkov_angle[None, :, None])**2) / (1 - np.tan(electron_zenith[:, :, None])**2 * np.tan(Cherenkov_angle[None, :, None])**2) + major_foci[:, :, None] * np.cos(Cherenkov_azimuth)
    ellipse_y = minor_foci[:, :, None] * np.sin(Cherenkov_azimuth+dtheta*np.random.uniform(-1,1,minor_foci.shape).reshape(minor_foci.shape)[:, :, None])

    return [ellipse_x, ellipse_y]

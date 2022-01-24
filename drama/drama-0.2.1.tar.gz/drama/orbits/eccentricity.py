"""Provides function related to eccentricity calculations."""
import numpy as np

from drama import constants as const


def frozen_eccentricity(orbit_height, inclination, include_j5=False):
    """Calculate the frozen eccentricity for a given height and inclination.

    Parameters
    ----------
    orbit_height : float
        orbit height [m]
    inclination : float
        orbit iclination in degrees
    include_j5 : bool
         if True, take the J5 zonal coefficient into account (Default value = False)

    Returns
    -------
    float
        Keplerian eccentricity
    """
    r_earth = const.r_earth  # Earth's radius
    a = r_earth + orbit_height  # semi-major axis

    # Zonal Coefficients
    j2 = const.j2
    j3 = const.j3

    inclination_rad = np.deg2rad(inclination)  # inclination [rad]
    e = -0.5 * (j3 / j2) * (r_earth / a) * np.sin(inclination_rad)

    if include_j5:
        j5 = const.j5
        f1 = -(5.0 / 8) * (j5 / j2) * ((r_earth / a) ** 3) * np.sin(inclination_rad)
        f2 = 1.0 - 9.0 * (np.cos(inclination_rad)) ** 2
        -24.0 * ((np.cos(inclination_rad)) ** 4) / (
            1 - 5 * (np.cos(inclination_rad)) ** 2
        )

        e = e + f1 * f2
    return e

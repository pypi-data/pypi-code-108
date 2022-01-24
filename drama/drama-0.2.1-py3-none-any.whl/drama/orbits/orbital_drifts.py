"""orbital_drifts provides function to compute drifts between orbits."""
import numpy as np

from drama import constants as const


def nodal_regression(e: float, a: float, i: float, include_j4: bool = True) -> float:
    """Calculate the nodal regression given the orbit eccentricity, inclination and semi-major axis.

    Parameters
    ----------
    e : float
        eccentricity
    a : float
        semi-major axis [m]
    i : float
        orbit inclination [deg]
    include_j4 : bool
        if True, take into account the J4 zonal (default value = True)

    Returns
    -------
    float
        nodal regression [rad/s]
    """
    r_earth = const.r_earth
    j2 = const.j2
    j4 = const.j4
    inclination_rad = np.deg2rad(i)
    mean_motion = np.sqrt(const.gm_earth / (a ** 3))
    semi_latus = a * (1 - e ** 2)

    nodal_regression_j2 = (
        -3
        * mean_motion
        * (r_earth ** 2)
        * j2
        * np.cos(inclination_rad)
        / (2 * semi_latus ** 2)
    )
    if include_j4:
        t2 = (
            3
            * mean_motion
            * (r_earth ** 4)
            * (j2 ** 2)
            * np.cos(inclination_rad)
            / (32.0 * semi_latus ** 4)
        ) * (12 - 4 * e ** 2 - (80 + 5 * e ** 2) * (np.sin(inclination_rad) ** 2))

        t3 = (
            15
            * mean_motion
            * (r_earth ** 4)
            * j4
            * np.cos(inclination_rad)
            / (32.0 * semi_latus ** 4)
        ) * (8 + 12 * e ** 2 - (14 + 21 * e ** 2) * (np.sin(inclination_rad) ** 2))
        nodal_regression_total = nodal_regression_j2 + t2 + t3
    else:
        nodal_regression_total = nodal_regression_j2
    return nodal_regression_total


def omega_per_dot(e: float, a: float, i: float, include_j4: bool = True):
    """Calculates the drift of the argument of perigee.

    Parameters
    ----------
    e : float
        eccentricity
    a : float
        semi-major axis [m]
    i : float
        orbit inclination [deg]
    include_j4 : bool
        if True, take into account the J4 zonal (default value = True)

    Returns
    -------
    float
        drift of argument of perigee [rad/s]
    """
    r_earth = const.r_earth
    j2 = const.j2
    j4 = const.j4

    inclination_rad = np.deg2rad(i)
    mean_motion = np.sqrt(const.gm_earth / (a ** 3))  # mean motion
    semi_latus = a * (1 - e ** 2)  # semi-latus rectum

    omega_per_dot_j2 = (
        (3.0 / 4)
        * mean_motion
        * j2
        * ((r_earth / semi_latus) ** 2)
        * (4.0 - 5.0 * (np.sin(inclination_rad)) ** 2)
    )

    if include_j4:
        t2 = (
            (9.0 / 384)
            * mean_motion
            * (j2 ** 2)
            * ((r_earth / semi_latus) ** 4)
            * (
                56.0 * e ** 2
                + (760.0 - 36.0 * e ** 2) * ((np.sin(inclination_rad)) ** 2)
                - (890.0 + 45.0 * e ** 2) * ((np.sin(inclination_rad)) ** 4)
            )
        )

        t3 = (
            (-15.0 / 128)
            * mean_motion
            * j4
            * ((r_earth / semi_latus) ** 4)
            * (
                64.0
                + 72.0 * e ** 2
                - (248.0 + 252.0 * e ** 2) * ((np.sin(inclination_rad)) ** 2)
                + (196.0 + 189.0 * e ** 2) * ((np.sin(inclination_rad)) ** 4)
            )
        )

        omega_per_dot_total = omega_per_dot_j2 + t2 + t3
    else:
        omega_per_dot_total = omega_per_dot_j2

    return omega_per_dot_total

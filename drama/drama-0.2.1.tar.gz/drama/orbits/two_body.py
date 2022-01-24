"""Functions that solve the classical two body problem.
"""
from __future__ import annotations
from collections import namedtuple
from dataclasses import dataclass
import collections.abc
import copy

import numpy as np
import numpy.typing as npt
from scipy.spatial.transform import Rotation as R

from drama.constants import gm_earth, r_earth, j2

StateVector = namedtuple("StateVector", ["r_eci", "v_eci"])


@dataclass
class OrbitParameters:
    """Data structure for keeping track of the classical orbital elements. Units
    are s, m and rad."""

    delta_t: float | np.ndarray
    a: float | np.ndarray
    e: float | np.ndarray
    i: float | np.ndarray
    raan: float | np.ndarray
    arg_p: float | np.ndarray
    true_anomaly: float | np.ndarray

    def __getitem__(self, key):
        op = copy.copy(self)
        op_vars = vars(op)
        for k in op_vars:
            if isinstance(op_vars[k], (collections.abc.Sequence, np.ndarray)):
                op_vars[k] = op_vars[k][key]
        return op


def true_anomaly_to_eccentric(
    e: float | np.ndarray, true_anomaly: float | np.ndarray
) -> float | np.ndarray:
    """Calculate the eccentric anomaly from the true anomaly.

    Parameters
    ----------
    e : float | np.ndarray
        Eccentricity [rad].
    true_anomaly : float | np.ndarray
        True anomaly [rad]

    Returns
    -------
    float | np.ndarray
        Eccentric anomaly in the range [0, 2π] [rad].
    """
    return (
        2
        * np.arctan2(
            np.sqrt(1 - e) * np.sin(true_anomaly / 2),
            np.sqrt(1 + e) * np.cos(true_anomaly / 2),
        )
    ) % (2 * np.pi)


def eccentric_anomaly_to_mean(
    e: float | np.ndarray, eccentric_anomaly: float | np.ndarray
) -> float | np.ndarray:
    """Calculate the mean anomaly from the eccentric anomaly.

    Parameters
    ----------
    e : float | np.ndarray
        Eccentricity [rad].
    eccentric_anomaly : float | np.ndarray
        Eccentric anomaly [rad]

    Returns
    -------
    float | np.ndarray
        Mean anomaly in the range [0, 2π] [rad].
    """
    return (eccentric_anomaly - e * np.sin(eccentric_anomaly)) % (2 * np.pi)


def true_anomaly_to_mean(
    e: float | np.ndarray, true_anomaly: float | np.ndarray
) -> float | np.ndarray:
    """Calculate the true anomaly from the mean anomaly.

    Parameters
    ----------
    e : float | np.ndarray
        Eccentricity [rad].
    true_anomaly : float | np.ndarray
        True anomaly [rad]

    Returns
    -------
    float | np.ndarray
        Mean anomaly in the range [0, 2π] [rad].
    """
    eccentric = true_anomaly_to_eccentric(e, true_anomaly)
    return eccentric_anomaly_to_mean(e, eccentric)


def mean_anomaly_to_eccentric(
    e: float | np.ndarray,
    mean_anomaly: float | np.ndarray,
    error: float | np.ndarray = 1e-8,
) -> np.ndarray:
    """Calculate the mean anomaly from the eccentric anomaly.

    The function uses the Newton-Raphson method to solve Kepler’s equation:
    E - esin(E) = M,
    for the eccentric anomaly E.

    Parameters
    ----------
    e : float
        Eccentricity [rad].
    true_anomaly : float
        True anomaly [rad]
    error : float
        The tolerance of the Newton-Raphson method.

    Returns
    -------
    float
        Mean anomaly in the range [0, 2π] [rad].

    Notes
    -----
    Based on Algorithm 3.1 of Curtis_[1].

    References
    ----------
    ..[1] Curtis, H. D. (2013). Orbital mechanics for engineering
    students. Butterworth-Heinemann.
    """
    # bound M to [0, 2π]
    mean_anomaly = np.atleast_1d(mean_anomaly)
    mean_anomaly = mean_anomaly % (2 * np.pi)
    # select a starting value for E
    # eccentric_a = mean_anomaly + e / 2 if mean_anomaly < np.pi else mean_anomaly - e / 2
    eccentric_a = np.empty_like(mean_anomaly)
    less_than_pi = mean_anomaly < np.pi
    eccentric_a[less_than_pi] = mean_anomaly[less_than_pi] + e / 2
    more_than_pi = mean_anomaly >= np.pi
    eccentric_a[more_than_pi] = mean_anomaly[more_than_pi] - e / 2
    ratio = np.ones_like(eccentric_a)
    while np.abs(ratio.max()) > error:
        ratio = (eccentric_a - e * np.sin(eccentric_a) - mean_anomaly) / (
            1 - e * np.cos(eccentric_a)
        )
        eccentric_a = eccentric_a - ratio
    return eccentric_a


def eccentric_anomaly_to_true(
    e: float | np.ndarray, eccentric_anomaly: float | np.ndarray
) -> float | np.ndarray:
    """Calculate the true anomaly from the eccentric anomaly.

    Parameters
    ----------
    e : float | np.ndarray
        Eccentricity [rad].
    eccentric_anomaly : float | np.ndarray
        Eccentric anomaly [rad]

    Returns
    -------
    float | np.ndarray
        True anomaly in the range [0, 2π] [rad].
    """
    sin_ea_o2 = np.sin(eccentric_anomaly / 2)
    cos_ea_o2 = np.cos(eccentric_anomaly / 2)
    return (2 * np.arctan2(np.sqrt(1 + e) * sin_ea_o2, np.sqrt(1 - e) * cos_ea_o2)) % (
        2 * np.pi
    )


def mean_anomaly_to_true(
    e: float, mean_anomaly: float, error: float = 1e-8
) -> float | np.ndarray:
    """Calculate the mean anomaly from the true anomaly.

    Parameters
    ----------
    e : float
        Eccentricity [rad].
    mean_anomaly : float
        Mean anomaly [rad]

    Returns
    -------
    float
        True anomaly in the range [0, 2π] [rad].
    """
    eccentric_a = mean_anomaly_to_eccentric(e, mean_anomaly, error)
    return eccentric_anomaly_to_true(e, eccentric_a)


def orbital_elements_to_rv(
    a: float | np.ndarray,
    e: float | np.ndarray,
    i: float | np.ndarray,
    raan: float | np.ndarray,
    arg_p: float | np.ndarray,
    true_anomaly: float | np.ndarray,
) -> StateVector:
    """Convert the classical Keplerian elements (semi-major axis a, eccentricity
    e, inclination i, RAAN Ω, argument of periapsis ω, and true anomaly ν) to
    state vector of position and velocity in an inertial coordinate frame (ECI).

    Parameters
    ----------
    a : float
        Semi-major axis [m].
    e : float
        Eccentricity.
    i : float
        Inclination [rad].
    raan : float
        Right ascension of ascending node [rad].
    arg_p : float
        Argument of perigee [rad].
    true_anomaly : float
        True anomaly [rad].

    Returns
    -------
    tuple[np.ndarray]
        A named tuple, StateVector, with elements r_eci and v_eci. Each element
        is an ndarray in cartesian coordinates.

    Notes
    -----
    The algorithm is based on Algorithm 10 of Vallado_[1] and Algorithm 4.5 of
    Curtis_[2]

    References
    ----------
    .. [1] Vallado DA, McClain WD. Fundamentals of Astrodynamics and
    Applications. 4th ed. Hawthorne, CA: Microcosm Press; 2013.
    ..[2] Curtis, H. D. (2013). Orbital mechanics for engineering
    students. Butterworth-Heinemann.
    """
    sin_ta = np.sin(true_anomaly)
    cos_ta = np.cos(true_anomaly)
    # semi-latus rectum
    p = a * (1 - e ** 2)
    # radial distance from centre of orbiting body from central body
    r = p / (1 + e * cos_ta)
    # the position vector is compute in the perifocal plane where the basis
    # vectors are P, Q and N:
    # * P is in the direction of periapsis
    # * Q lies at 90° true anomaly
    # * N is normal to the orbital plane.
    if isinstance(r, np.ndarray) or isinstance(cos_ta, np.ndarray):
        r_pqn = np.column_stack((r * cos_ta, r * sin_ta, np.zeros_like(r)))
        # handle the case where p is a scalar. If we do not convert it to an array, indexing p will raise an IndexError: invalid index to scalar variable.
        p = np.atleast_1d(p)
        # velocity in the perifocal frame
        v_pqn = np.sqrt(gm_earth / p)[:, np.newaxis] * np.column_stack(
            (-sin_ta, e + cos_ta, np.zeros_like(cos_ta))
        )
    else:
        r_pqn = np.array([r * cos_ta, r * sin_ta, 0]).squeeze()
        v_pqn = np.sqrt(gm_earth / p) * np.array([-sin_ta, e + cos_ta, 0])
    arg_p, i, raan = np.atleast_1d(arg_p, i, raan)
    r_3 = R.from_euler("zxz", np.column_stack((arg_p, i, raan)), degrees=False)
    if r_pqn.ndim == 2:
        r_eci = r_3.as_matrix() @ r_pqn[..., np.newaxis]
        v_eci = r_3.as_matrix() @ v_pqn[..., np.newaxis]
    else:
        r_eci = r_3.as_matrix() @ r_pqn
        v_eci = r_3.as_matrix() @ v_pqn
    return StateVector(r_eci.squeeze(), v_eci.squeeze())


def j2_kepler(
    delta_t: float | np.ndarray,
    a: float,
    e: float,
    i: float,
    raan: float,
    arg_p: float,
    true_anomaly: float,
) -> tuple[StateVector, OrbitParameters]:
    """Compute the pertubations of the classical orbital parameters due to J2 and propagate the orbits by `delta_t` seconds.

    Parameters
    ----------
    delta_t : float
        Time by which to propagate the orbit [s].
    a : float
        Semi-major axis [m].
    e : float
        Eccentricity
    i : float
        Inclination [rad].
    raan : float
        Right ascension of ascending node [rad].
    arg_p : float
        Argument of perigee [rad].
    true_anomaly : float
        True anomaly [rad].

    Returns
    -------
    tuple[np.ndarray]
        A named tuple, StateVector, with elements r_eci and v_eci. Each element
        is an ndarray in cartesian coordinates.

    Notes
    -----
    The algorithm is based on Algorithm 65 of Vallado_[1]. We assume that the
    first and second derivatives of the mean motion are zero. This gives a
    J2-only solution. Thus we neglect equations that involve these two terms (we
    do not propagate the semi-major axis nor the eccentricity).

    To esnure that we are on the correct path the code was checked against
    similar implementations in orbit-propagator by Satellogic SA and
    SatelliteToolbox.jl by Ronan Arraes Jardim Chagas.

    References
    ----------
    .. [1] Vallado DA, McClain WD. Fundamentals of Astrodynamics and
    Applications. 4th ed. Hawthorne, CA: Microcosm Press; 2013.
    """
    mean_motion = np.sqrt(gm_earth / (a ** 3))
    # semi-latus rectum
    p = a * (1 - e ** 2)
    # Ensure that the eccentricity is not less than 0.
    if e < 0:
        raise ValueError(
            f"The eccentricity must be larger than 0. Current value: {e:.3f}."
        )
    mean_anomaly_0 = true_anomaly_to_mean(e, true_anomaly)
    raan_dot = -3 * mean_motion * (r_earth ** 2) * j2 * np.cos(i) / (2 * p ** 2)
    arg_p_dot = (
        3 / 4 * mean_motion * j2 * ((r_earth / p) ** 2) * (4.0 - 5.0 * (np.sin(i)) ** 2)
    )
    # Propagate Ω and ω by Δt.
    raan = (raan + raan_dot * delta_t) % (2 * np.pi)
    arg_p = (arg_p + arg_p_dot * delta_t) % (2 * np.pi)
    # Credit to SatelliteToolbox.jl. In the source code the developer correctly
    # notes that in the peudocode that the book provides the first time
    # derivative of the mean anomaly is not included despite the fact that it is
    # not equal to zero (see equation 9-41). So we include both the contribution
    # of of the time derivative of the mean anomaly and of the mean motion.
    mean_anomaly_dot_0 = (
        -3
        * mean_motion
        * r_earth ** 2
        * j2
        * np.sqrt(1 - e ** 2)
        / (4 * p ** 2)
        * (3 * np.sin(i) ** 2 - 2)
    )
    # Propagate the anomaly to t_0 + Δt.
    mean_anomaly = (mean_anomaly_0 + (mean_anomaly_dot_0 + mean_motion) * delta_t) % (
        2 * np.pi
    )
    true_anomaly = mean_anomaly_to_true(e, mean_anomaly)
    # orbital_elements_to_rv expects i to have the same shape as raan and arg_p, even
    # though it is invariant with time. This is because the construction of the rotation
    # matrix for conversion from the perifocal to the inertial frame expects all
    # rotation angles to have the same shape.
    if isinstance(delta_t, np.ndarray):
        i = np.repeat(i, raan.size)
    # Compute the position and velocity in ECI.
    return (
        orbital_elements_to_rv(a, e, i, raan, arg_p, true_anomaly),
        OrbitParameters(delta_t, a, e, i, raan, arg_p, true_anomaly),
    )

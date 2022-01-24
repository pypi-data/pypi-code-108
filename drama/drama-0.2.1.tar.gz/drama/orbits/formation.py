from __future__ import absolute_import, division, print_function

from collections import namedtuple
import math

import numpy as np

from drama import constants
from drama.orbits.orbital_drifts import nodal_regression, omega_per_dot


RelOrbit = namedtuple("RelOrbit", ["mean_anomaly", "u", "dr_r", "dr_t", "dr_n"])


def clohessy_wiltshire(
    a,
    i_deg,
    dae,
    domega_deg,
    mean_anomaly,
    phi_deg=90,
    da=0,
    di_deg=0,
    du_deg=0,
    u0_deg=0,
):
    """Calculates relative orbit with to reference orbit. This ignores drifts,
        which will be treated separately

    Parameters
    ----------
    a :
        reference semi-major axis
    i_deg :
        inclination, in degree
    dae :
        delta eccentricity times a (maximum radial baseline)
    domega_deg :
        difference in ascending nodes
    phi_deg :
        delta eccenticity angle in degree (defaults to 90)
    da :
        semi-major axist difference (defaults to zero)
    di_deg :
        inclination difference (defaults to zero)
    du_deg :
        Difference in mean argument of latitude (defaults to
        zero)
    u0_deg :
        starting mean moment of latitude (Default value = 0)
    t :
        time in seconds. If not set a time vector corresponding to
        one revolution is generated (Default value = None)

    Returns
    -------
    RelOrbit
        Tuple with the time vector and separation along the R, T, and
        N directions.
    """

    # Convert angle variables to radian
    nform = np.array(dae).size
    u = 0
    i = np.radians(i_deg)
    domega = np.radians(domega_deg)
    phi = np.radians(phi_deg)
    di = np.radians(di_deg)
    du = np.radians(du_deg)
    # Orbit period
    Torb = 2.0 * np.pi * np.sqrt((a ** 3) / constants.gm_earth)
    u = mean_anomaly + np.deg2rad(u0_deg)
    # Some conversions
    daev = np.array(
        [
            np.array(dae * np.cos(phi)).flatten(),
            np.array(dae * np.sin(phi)).flatten(),
        ]
    )
    vd_i = np.array(
        [np.array(di).flatten(), np.array(domega).flatten() * np.sin(i)]
    )
    theta = np.arctan2(vd_i[1], vd_i[0])
    d_i = np.linalg.norm(vd_i, axis=0)
    dincv = np.array(
        [
            np.array(di).flatten(),
            (np.array(d_i).flatten() * np.array(np.sin(theta)).flatten()),
        ]
    )
    dr_r = (
        da
        - daev[0].reshape([nform, 1]) * np.cos(u)
        - daev[1].reshape([nform, 1]) * np.sin(u)
    )
    dr_t = (
        a * du
        - 3.0 * da / 2 * u
        - 2 * daev[1].reshape([nform, 1]) * np.cos(u)
        + 2 * daev[0].reshape([nform, 1]) * np.sin(u)
    )
    dr_n = -a * dincv[1].reshape([nform, 1]) * np.cos(u) + a * dincv[0].reshape(
        [nform, 1]
    ) * np.sin(u)
    if nform == 1:
        return RelOrbit(
            mean_anomaly.flatten(),
            u.flatten(),
            dr_r.flatten(),
            dr_t.flatten(),
            dr_n.flatten(),
        )
    else:
        return RelOrbit(mean_anomaly.flatten(), u.flatten(), dr_r, dr_t, dr_n)


def rel_orbit_drifts(a, i_deg, dae, e=0, da=0, di_deg=0):
    """Calculates drifts with respect to reference orbit
        Inputs are like for clohessy_wiltshire()
        Output is a tuple with the differential drifs of the ascending node
        and the drift of the argument of perigee for both spacecraft,
        all in degree/day

    Parameters
    ----------
    a : float
        semi-major axis
    i_deg : float
        orbit inclination [deg]
    dae : float
        vertical baseline due to eccentricity
    e : float
        eccentricity (Default value = 0)
    da : float
        difference in semi-major axis [m] (Default value = 0)
    di_deg : float
        difference in orbit inclination [deg] (Default value = 0)

    Returns
    -------
    Tuple
        differential drift of ascending node, and argument of perigee of main and companion satellites.
    """
    s_in_d = 3600.0 * 24
    # Diferential nodal regression
    accuracy = False if math.isclose(e, 0) else True
    domega_dt_ref = nodal_regression(e, a, i_deg, include_j4=accuracy)
    domega_dt_slv = nodal_regression(
        e + dae / a, a + da, i_deg + di_deg, include_j4=accuracy
    )
    d_dif_omega_dt = np.degrees(domega_dt_slv - domega_dt_ref) * s_in_d

    # For the argument of perigee, we take that of the orbit. The assumption is
    dphi_dt_ref = np.degrees(omega_per_dot(e, a, i_deg, include_j4=accuracy))
    dphi_dt_slv = np.degrees(
        omega_per_dot(e + dae / a, a + da, i_deg + di_deg, include_j4=accuracy)
    )
    dphi_dt_ref = dphi_dt_ref * s_in_d
    dphi_dt_slv = dphi_dt_slv * s_in_d
    # d_dif_phi_dt = np.degrees(dphi_dt_slv - dphi_dt_ref) * s_in_d
    return (d_dif_omega_dt, dphi_dt_ref, dphi_dt_slv)

import numpy as np
from matplotlib import pyplot as plt

from drama import constants as const
import drama.orbits.eccentricity as ecc
from drama.orbits import orbital_drifts as orbdrfts


def get_sunsync_repeat_orbit(K, N, verbose=False, acc=None, silent=False):
    """Iteratively calculates orbit parameters for a sun-synchronous repeat
        orbit with a chosen number of cycles (K) and a chosen number of
        orbits (N)

    Parameters
    ----------
    K :
        number of cycles (days) for repeat  [d]
    N :
        number of orbits for repeat
    verbose :
         (Default value = False)
    acc :
         (Default value = None)
    silent :
         (Default value = False)

    Returns
    -------
    type
        Keplerian semi-major axis [m], Keplerian eccentricity,
        Keplerian inclination angle [deg]

    """

    # Basic constants to be used
    gm_earth_d = const.gm_earth * (86400.0 ** 2.0)  # [m^3/s^2] --> [m^3/d^2]
    r_earth = const.r_earth
    j2 = const.j2
    omega_dot_r = np.deg2rad(0.985647240)  # secular motion [rad/d]

    Tn = float(K) / N  # draconic period [d]
    n0 = 2.0 * np.pi / Tn  # [rad/d]
    a = (gm_earth_d / (n0 ** 2.0)) ** (1.0 / 3.0)  # semi-major axis [m]
    # inclination [rad]
    i = np.arccos(
        ((a ** 2.0) * omega_dot_r) / (-1.5 * n0 * j2 * (r_earth ** 2.0))
    )
    if not silent:
        print("\na = ", a, " [m]    ;  i = ", np.rad2deg(i), " [deg]")
    # start iteration

    if acc is None:  # accuracy of semi-major axis
        acc = 100.0
    while acc > 1.0:
        # calculate secular perturbations [rad/d]
        w_dot = (
            -(3.0 / 4.0)
            * n0
            * j2
            * ((r_earth / a) ** 2.0)
            * (1.0 - 5.0 * (np.cos(i)) ** 2.0)
        )
        delta_n = (
            -(3.0 / 4.0)
            * n0
            * j2
            * ((r_earth / a) ** 2.0)
            * (1.0 - 3.0 * (np.cos(i)) ** 2.0)
        )

        # calculate refined n0,a,i
        n0 = 2.0 * np.pi / Tn - delta_n - w_dot  # [rad/d]
        a_tmp = (gm_earth_d / (n0 ** 2.0)) ** (1 / 3.0)  # semi-major axis [m]

        # inclination [rad]
        i_tmp = np.arccos(
            ((a ** 2.0) * omega_dot_r) / (-1.5 * n0 * j2 * (r_earth ** 2.0))
        )

        # update accuracy
        acc = np.abs(a - a_tmp)

        # recursive definition
        a = a_tmp
        i = i_tmp
        if verbose:
            print("\na = ", a, " [m]    ;  i = ", np.rad2deg(i), " [deg]")

    # derive frozen eccentricity & inclination
    (e, i_h) = get_sunsync_orbit(a)
    if not silent:
        print("\nAltitude:  h = ", a - const.r_earth, " [m]")
        print("Inclination:  ", i_h, " [deg]")
        print("Eccentricity: ", e)

    return a, e, np.rad2deg(i)


def get_sunsync_orbit(a):
    """Derives frozen eccentricity and sunsunychronous inclination

    Parameters
    ----------
    a :
        Keplerian semi-major axis [m]

    Returns
    -------
    type
        Keplerian eccentricity, Keplerian inclination angle [deg]

    """

    acc = 1.0e-07  # accuracy
    dif = 10.0
    h = a - const.r_earth  # orbital height
    i0 = 100.0
    e0 = 0.1

    while dif > acc:
        i = get_sunsync_inclination(a, e0)
        e = ecc.frozen_eccentricity(h, i0, include_j5=True)

        # get difference
        dif = np.abs(i - i0) + np.abs(e - e0)

        # recursive definition
        e0 = e
        i0 = i

    return e, i


def get_sunsync_inclination(a, e):
    """Calculates sunsynchronous inclination

    Parameters
    ----------
    a :
        semi-major axis [m]
    e :
        eccentricity

    Returns
    -------
    type
        inclination angle [deg]

    """

    omega_dot_requested = 0.985627240  # secular motion per day

    acc = 1.0
    i = 90.0
    i_inc = 30.0

    while acc >= 1.0e-7:
        omega_dot_tmp = (
            np.degrees(orbdrfts.nodal_regression(e, a, i)) * 3600 * 24
        )
        if omega_dot_tmp > omega_dot_requested:
            i = i - i_inc
        if omega_dot_tmp < omega_dot_requested:
            i = i + i_inc
        i_inc = i_inc / 2.0
        acc = np.abs(omega_dot_tmp - omega_dot_requested)

    return i


def alt_inc_sunsync(min_alt, max_alt, e=0):
    """Calculates and plots the inclination as a function of altitude for
        sunsynchronous orbits

    Parameters
    ----------
    min_alt :
        Minimum range of altitudes [km]
    max_alt :
        Maximum range of altitudes [km]
    e :
        eccentricity (Default value = 0)

    Returns
    -------
    type
        a matrix containing altitudes and their corresponding
        inclinations

    """
    noOut = False
    plt.figure()
    plt.xlabel("Inclination [deg]", size=20)
    plt.ylabel("Orbital Height [km]", size=20)
    plt.title("Sun-Synchronous Orbits", size=22)

    # convert e to a list
    if not isinstance(e, (list, np.ndarray)):
        e = [e]
        noOut = True

    r_earth = const.r_earth
    GM_earth = const.gm_earth
    j2 = const.j2
    alt_arr = np.array(range(min_alt, max_alt + 1), dtype="float")

    a = (
        alt_arr * 1000.0 + r_earth
    )  # semi-major axis [km], assuming circular orbit
    n0 = np.sqrt(GM_earth / a ** 3.0)
    mean_motion_earth = 2.0 * np.pi / (365.242199 * 86400)  # [rad/sec]
    omega_dot = mean_motion_earth

    for k in range(0, len(e)):

        p = a * (1.0 - (e[k]) ** 2.0)
        # inclination
        i = np.arccos(
            (omega_dot * p ** 2.0) / (-1.5 * n0 * j2 * r_earth ** 2.0)
        )
        i = np.rad2deg(i)

        # Plotting
        plt.plot(i, alt_arr, label="e = " + str(e[k]))
        plt.grid(b=True, which="both", color="0.65", linestyle="-")
        plt.legend(loc=4)

    if noOut:
        return
    else:
        arr1 = alt_arr.reshape(1, alt_arr.size)
        arr2 = i.reshape(1, i.size)
        out = np.concatenate((arr1, arr2))
        idx = np.argmax(i, axis=None) - 1.0
        maxh = alt_arr[idx]
        return out, maxh

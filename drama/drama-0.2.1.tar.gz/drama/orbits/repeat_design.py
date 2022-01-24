from collections import namedtuple

import matplotlib.pyplot as plt
import numpy as np

from drama import constants as const
from drama.utils import misc as misc


def basic_orbit_param(
    hmin=580.0e03,
    hmax=780.0e03,
    start_cycle=6,
    stop_cycle=13,
    latitude=0,
    doPlot=1,
):
    """Calculates valid combinations of repeat_cycle, orbital height and
        orbits per cycle

    Parameters
    ----------
    hmin :
        minimum orbital height [m] (Default value = 580.0e03)
    hmax :
        maximum orbital height [m] (Default value = 780.0e03)
    start_cycle :
        minimum repeat cycle [days] (Default value = 6)
    stop_cycle :
        maximum repeat cycle [days] (Default value = 13)
    latitude :
        latitude [deg] (Default value = 0)
    doPlot :
        if set show the plots (Default value = 1)

    Returns
    -------
    type
        associative list (dict) containing days, h_sat, n_orbit,
        swath, covered_latitude

    """

    R_earth = const.r_earth
    GM_earth = const.gm_earth
    T_day = 24 * 60.0 * 60.0

    # minimum orbital period
    T_orb_min = 2 * np.pi * np.sqrt((hmin + R_earth) ** 3 / GM_earth)
    # maximum orbital period
    T_orb_max = 2 * np.pi * np.sqrt((hmax + R_earth) ** 3 / GM_earth)

    # minimum repeats
    n_repeat_min = np.floor(T_day * start_cycle / T_orb_max)
    # maximum repeats
    n_repeat_max = np.ceil(T_day * stop_cycle / T_orb_min)

    repeat_cycle = np.array(range(start_cycle, stop_cycle + 1), dtype="int")
    n_repeat = np.array(
        range(int(n_repeat_min), int(n_repeat_max) + 1), dtype="float"
    )

    h_sat = np.zeros((len(repeat_cycle), len(n_repeat)))  # satellite height
    ds = np.zeros((len(repeat_cycle), len(n_repeat)))  # swath
    valid = np.ones((len(repeat_cycle), len(n_repeat)), dtype="int")
    repeat_number_array = np.zeros((len(repeat_cycle), len(n_repeat)))
    repeat_cycle_array = np.zeros(
        (len(repeat_cycle), len(n_repeat)), dtype="int"
    )

    for i in range(0, len(repeat_cycle)):
        for j in range(0, len(n_repeat)):
            repeat_number_array[i, j] = n_repeat[j]
            repeat_cycle_array[i, j] = repeat_cycle[i]
            T_orbit = repeat_cycle[i] * T_day / n_repeat[j]

            # semi-major axis
            a = (((T_orbit / (2.0 * np.pi)) ** 2) * GM_earth) ** (1.0 / 3)
            # satellite height
            h_sat[i, j] = a - R_earth  # satellite height

            # covered swath
            ds[i, j] = (
                2 * np.pi * R_earth * np.cos(np.deg2rad(latitude))
            ) / n_repeat[j]

            # If repeat_cycle & n_repeat have common divisor then invalid
            if misc.checkcommondivisors(repeat_cycle[i], n_repeat[j]) == 1:
                valid[i, j] = 0

    # Get indices of valid heights
    tmp = (h_sat > (hmin + 1000.0)) & (h_sat < (hmax - 1000.0)) & (valid > 0)
    tmp = np.reshape(tmp, (np.product(tmp.shape)))
    tmp = np.where(tmp == True)[0]

    Out = namedtuple("out", ["days", "h_sat", "n_orbits", "swath"])

    # Convert to one dimensional arrays
    repeat_cycle_array = np.reshape(
        repeat_cycle_array, (np.product(repeat_cycle_array.shape))
    )
    h_sat = np.reshape(h_sat, (np.product(h_sat.shape)))
    repeat_number_array = np.reshape(
        repeat_number_array, (np.product(repeat_number_array.shape))
    )
    ds = np.reshape(ds, (np.product(ds.shape)))

    out = Out(
        repeat_cycle_array[tmp], h_sat[tmp], repeat_number_array[tmp], ds[tmp]
    )

    if doPlot:
        # Start Plotting
        plt.figure()
        X = repeat_cycle_array[tmp]
        Y = h_sat[tmp] / 1000.0
        Z = repeat_number_array[tmp]
        plt.plot(X, Y, "+")
        plt.xlabel("Repeat Cycle [days]")
        plt.ylabel("Orbital Height [km]")
        plt.ylim([hmin / 1000.0, hmax / 1000.0])
        plt.xlim([min(repeat_cycle) - 1, max(repeat_cycle) + 1])
        plt.grid(b=True, which="both", color="0.65", linestyle="-")

        for i in range(0, len(Z)):
            plt.text(X[i], Y[i], str(int(Z[i])), color="red", fontsize=12)
        plt.show()
    return out

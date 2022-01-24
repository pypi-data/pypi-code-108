"""timing groups together functions to compute a suitable timing configuration for a given swath.

It takes into account the tilt of the antenna and its size."""

from collections import namedtuple

import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

from drama import constants as const
from drama.geo import geometry as sargeo


blind_out = namedtuple(
    "BlindRanges",
    ["inc_s", "inc_e", "look_s", "look_e", "slant_range_s", "slant_range_e"],
)


def blind_ranges(
    angular_range, orbit_h, PRF, duty_cycle, angle_is_look=False, radian=False
):
    """Code to find the positions of the blind ranges

       :author: Paco Lopez-Dekker

    Parameters
    ----------
    angular_range :
        tuple with start and end angle (typically,
        indicent angle, in degree)
    orbit_h :
        orbit height
    PRF :
        PRF
    duty_cycle :
        a number between 0 and 0.5
    angle_is_look :
        set to True if angular range are look angles.
        Defaults to False
    radian :
        set to True if input and output angles are in radians (Default value = False)

    Returns
    -------
    type
        a named tuple with the start and end of the blind incident
        and look angles, and the start of the blind slant ranges

    """
    if radian:
        ang_range = np.array(angular_range)
    else:
        ang_range = np.array(angular_range) * np.pi / 180
    if angle_is_look:
        inc_range = sargeo.look_to_inc(ang_range, orbit_h)
    else:
        inc_range = ang_range
    inc_v = np.arange(
        inc_range[0], inc_range[1], (inc_range[1] - inc_range[0]) / 1000
    )
    sr_v = sargeo.inc_to_sr(inc_v, orbit_h)

    # Find out blind ranges
    delta_r_unamb = const.c / 2 / PRF
    blind_ranges = np.arange(0, np.max(sr_v), delta_r_unamb)
    good_indices = np.where(blind_ranges > np.min(sr_v))
    blind_ranges = blind_ranges[good_indices]
    if blind_ranges.size == 0:
        print("No blind ranges found")
        return 0
    delta_r_duty = const.c / 2 * (2 * duty_cycle / PRF)
    r2inc = interpolate.InterpolatedUnivariateSpline(sr_v, inc_v, k=2)
    blind_inc_1 = r2inc(blind_ranges)
    blind_inc_2 = r2inc(blind_ranges + delta_r_duty)

    res = blind_out(
        blind_inc_1 * 180 / np.pi,
        blind_inc_2 * 180 / np.pi,
        sargeo.inc_to_look(blind_inc_1, orbit_h) * 180 / np.pi,
        sargeo.inc_to_look(blind_inc_2, orbit_h) * 180 / np.pi,
        blind_ranges,
        blind_ranges + delta_r_duty,
    )
    return res


def timing_diagram(
    angular_range,
    orbit_h,
    PRFs,
    duty_cycle,
    angle_is_look=False,
    radian=False,
    nadir_echo_len=10e-6,
    plot_tx=True,
    plot_echo_incomplete=True,
    plot_nadir=True,
):
    """Code to find the positions of the blind ranges

       :author: Paco Lopez-Dekker

    Parameters
    ----------
    angular_range :
        tuple with start and end angle (typically,
        indicent angle, in degree)
    orbit_h :
        orbit height
    PRFs :
        a vector of PRF values
    duty_cycle :
        a number between 0 and 0.5
    angle_is_look :
        set to True if angular range are look angles.
        Defaults to False
    radian :
        set to True if input and output angles are in radians (Default value = False)
    nadir_echo_len :
         (Default value = 10e-6)
    plot_tx :
         (Default value = True)
    plot_echo_incomplete :
         (Default value = True)
    plot_nadir :
         (Default value = True)

    Returns
    -------
    type
        a named tuple with the start and end of the blind incident
        and look angles, and the start of the blind slant ranges

    """
    if radian:
        ang_range = np.array(angular_range)
    else:
        ang_range = np.array(angular_range) * np.pi / 180
    if angle_is_look:
        inc_range = sargeo.look_to_inc(ang_range, orbit_h)
    else:
        inc_range = ang_range
    inc_v = np.linspace(inc_range[0], inc_range[1], 1000)
    inc_v = inc_v.reshape((inc_v.size, 1))
    sr_v = sargeo.inc_to_sr(inc_v, orbit_h)
    # Find out blind ranges
    PRF = np.array(PRFs)
    PRF = PRF.reshape((1, PRF.size))
    delta_r_duty = const.c / 2 * (duty_cycle / PRF)
    delta_r = delta_r_duty
    delta_r_unamb = const.c / 2 / PRF
    rgwin_min = np.floor(sr_v.min() / delta_r_unamb.max()).astype(np.int)
    rgwin_max = np.floor(sr_v.max() / delta_r_unamb.min()).astype(np.int)
    nwin = rgwin_max - rgwin_min + 1
    sr_win_start = delta_r_unamb * np.arange(rgwin_min, rgwin_max + 1).reshape(
        (nwin, 1)
    )
    sr_win_end = sr_win_start + delta_r
    sr_echowin_end = sr_win_start - delta_r
    (gr_win_start, theta_i_win_start, theta_l_win_start, kk) = sargeo.sr_to_geo(
        sr_win_start, orbit_h
    )
    (gr_win_end, theta_i_win_end, theta_l_win_end, kk) = sargeo.sr_to_geo(
        sr_win_end, orbit_h
    )
    (
        gr_echowin_end,
        theta_i_echowin_end,
        theta_l_echowin_end,
        kk,
    ) = sargeo.sr_to_geo(sr_echowin_end, orbit_h)
    # sr_v_amb = np.mod(sr_v, delta_r_unamb)
    # blind_mask = np.less(sr_v_amb, delta_r_duty)
    # Nadir return
    sr_nadir = orbit_h
    nnadir = np.floor((sr_v.max() - sr_nadir) / delta_r_unamb.min() + 1).astype(
        np.int
    )
    sr_nadir_start = sr_nadir + delta_r_unamb * np.arange(nnadir).reshape(
        (nnadir, 1)
    )
    sr_nadir_end = sr_nadir_start + nadir_echo_len
    (
        gr_nadir_start,
        theta_i_nadir_start,
        theta_l_nadir_start,
        kk,
    ) = sargeo.sr_to_geo(sr_nadir_start, orbit_h)
    (gr_nadir_end, theta_i_nadir_end, theta_l_nadir_end, kk) = sargeo.sr_to_geo(
        sr_nadir_end, orbit_h
    )
    if angle_is_look:
        theta_win_start = theta_l_win_start
        theta_win_end = theta_l_win_end
        theta_echowin_end = theta_l_echowin_end
        theta_nadir_start = theta_l_nadir_start
        theta_nadir_end = theta_l_nadir_end
        ylabel = "Look angle [deg]"
    else:
        theta_win_start = theta_i_win_start
        theta_win_end = theta_i_win_end
        theta_echowin_end = theta_i_echowin_end
        theta_nadir_start = theta_i_nadir_start
        theta_nadir_end = theta_i_nadir_end
        ylabel = "Incident angle [deg]"
    if plot_tx or plot_echo_incomplete or plot_nadir:
        plt.figure()
        for ind in range(nwin):
            if plot_tx:
                plt.fill_between(
                    PRF.flatten(),
                    np.degrees(theta_win_start[ind]),
                    np.degrees(theta_win_end[ind]),
                    facecolor="red",
                    alpha=0.5,
                )
            if plot_echo_incomplete:
                plt.fill_between(
                    PRF.flatten(),
                    np.degrees(theta_echowin_end[ind]),
                    np.degrees(theta_win_start[ind]),
                    facecolor="grey",
                    alpha=0.5,
                )
        if plot_nadir:
            for ind in range(nnadir):
                # print(np.degrees(theta_nadir_start[ind,0]))
                plt.fill_between(
                    PRF.flatten(),
                    np.degrees(theta_nadir_start[ind]),
                    np.degrees(theta_nadir_end[ind]),
                    facecolor="blue",
                    color="blue",
                    alpha=0.5,
                )
        ax = plt.gca()

        plt.xlabel("PRF [Hz]")
        plt.ylabel(ylabel)
        plt.grid(True)
        # Second axis
        ax2 = ax.twinx()
        tickloc = ax.get_yticks()
        if angle_is_look:
            tickval = (
                sargeo.inc_to_gr(
                    sargeo.look_to_inc(np.radians(tickloc), orbit_h), orbit_h
                )
                / 1e3
            )
        else:
            tickval = sargeo.inc_to_gr(np.radians(tickloc), orbit_h) / 1e3
        ax2.set_ylim(ax.get_ylim())
        # ax2.set_ylim(angular_range)
        ax2.set_yticks(tickloc)
        tickvalstr = ["%4.1f" % thisval for thisval in tickval]
        ax2.set_yticklabels(tickvalstr)
        ax2.set_ylabel("Ground range [km]")
        plt.tight_layout()
        ax.set_ylim(angular_range)
        ax2.set_ylim(angular_range)
    return (ax, ax2, angle_is_look, orbit_h)


def mode_on_timing(PRF, start, swathwidth, timing_diagram):
    """

    Parameters
    ----------
    PRF :
        PRF [Hz]
    start :
        start of swath in degree or in meter (if ground range, assumed
        if larger than 90)
    swathwidth :
        swathwidth in meter
    timing_diagram :


    Returns
    -------

    """
    (ax, ax2, angle_is_look, orbit_h) = timing_diagram
    if start > 90:
        print("Start paramter assumed to be ground swath start")
        gr0 = start
        (srs, theta_i_v, theta_l_v) = sargeo.gr_to_geo(
            np.array([start, start + swathwidth]), orbit_h
        )
        if angle_is_look:
            theta_v = theta_l_v
        else:
            theta_v = theta_i_v
    else:
        if angle_is_look:
            gr0 = sargeo.inc_to_gr(
                sargeo.look_to_inc(np.radians(start), orbit_h), orbit_h
            )
            (srs, theta_i_v, theta_l_v) = sargeo.gr_to_geo(
                np.array([gr0, gr0 + swathwidth]), orbit_h
            )
            theta_v = theta_l_v
        else:
            gr0 = sargeo.inc_to_gr(np.radians(start), orbit_h)
            (srs, theta_i_v, theta_l_v) = sargeo.gr_to_geo(
                np.array([gr0, gr0 + swathwidth]), orbit_h
            )
            theta_v = theta_i_v
    ax2.plot([PRF, PRF], np.degrees(theta_v), linewidth=4)
    print(
        "Swath ground range (near, far) [km]: (%4.1f, %4.1f)"
        % (gr0 / 1e3, (gr0 + swathwidth) / 1e3)
    )
    print(
        "Swath incident angle (near, far) [deg]: (%3.1f, %3.1f)"
        % (np.degrees(theta_i_v[0]), np.degrees(theta_i_v[1]))
    )


def conf_to_timing(
    conf, Nswth, tilt, Le, duty_cycle, La=None, v_orb=None, n_sat=1
):
    """Code to find a suitable timing configuration for the swaths given the
       size and the tilt angle of the antenna. PRFs for the different swaths
       are set to the highest possible values
       NOTE. The returned solution is not necessarily optimal.

       :author: Lorenzo Iannini

    Parameters
    ----------
    conf :
        configuration trampa.io.cfg.ConfigFile object with
        configuration read from parameter file
    Nswth :
        number of swaths
    tilt :
        antenna tilt in elevation [degrees]
    Le :
        antenna length in elevation
    duty_cycle :
        a number between 0 and 0.5
    La :
        antenna length in azimuth. Default set to None. If provided
        the PRF will not exceed the antenna bandwidth
    v_orb :
        satellite velocity (Default value = None)
    n_sat :
        number of satellites in the constellation. For the antenna
        bandwidth requirement, n_sat*PRF is considered (Default value = 1)

    Returns
    -------
    type
        a named tuple with the start and end of the blind incident
        and look angles, and the start of the blind slant ranges

    """
    wl = const.c / conf.sar.f0
    Horb = conf.orbit.Horb

    # antenna bandwidth (azimuth)
    if (La is not None) & (v_orb is not None):
        antenna_bw = 2 * np.sin(wl / La) * v_orb / wl
    else:
        antenna_bw = np.Inf
    # ---- Compute angle coverages ----
    # The antenna boresight is pointed on the farthest beam
    la_swth_width = [None] * Nswth
    la_swth = np.zeros((2, Nswth))
    PRFs = np.zeros(Nswth)

    la_swth_center = tilt
    for swth in np.flip(np.arange(Nswth)):
        la_swth_width[swth] = (
            wl / (Le * np.cos(np.radians(tilt - la_swth_center))) / np.pi * 180
        )
        la_swth[0, swth] = la_swth_center - la_swth_width[swth] / 2
        la_swth[1, swth] = la_swth_center + la_swth_width[swth] / 2
        sr_near = sargeo.look_to_sr(np.radians(la_swth[0, swth]), Horb)
        sr_far = sargeo.look_to_sr(np.radians(la_swth[1, swth]), Horb)
        sr_swth_width = sr_far - sr_near

        # Finds hypothetic maximum PRF (no blind ranges conflicts)
        PRF_max = const.c / 2 / sr_swth_width / (1 + 2 * duty_cycle)
        # range window
        rgwin = np.ceil(2 * sr_near / const.c * PRF_max).astype(np.int)
        # finds the compatible highest range window
        sr_min_win = np.inf
        while (rgwin > 0) & (sr_min_win > sr_near):
            PRF_win = const.c * ((rgwin) - duty_cycle) / 2 / sr_far
            sr_min_win = const.c * ((rgwin - 1) + duty_cycle) / 2 / PRF_win
            rgwin = rgwin - 1
        # Lower PRF (range window) to the antenna bandwidth
        PRF_win_nsat = n_sat * PRF_win
        while (PRF_win_nsat > antenna_bw) & (rgwin > 0):
            rgwin = rgwin - 1
            PRF_win = PRF_win_nsat / n_sat
            PRF_win_nsat = n_sat * const.c * ((rgwin) - duty_cycle) / 2 / sr_far
        # Set PRF value
        PRFs[swth] = PRF_win
        la_swth_center = la_swth_center - la_swth_width[swth]
    inc_near = np.degrees(sargeo.look_to_inc(np.radians(la_swth[0, :]), Horb))
    inc_far = np.degrees(sargeo.look_to_inc(np.radians(la_swth[1, :]), Horb))
    return (PRFs, inc_near, inc_far)


def timing_windows(
    conf,
    inc_near,
    inc_far,
    PRF_min=1000,
    PRF_max=5000,
    PRF_step=1,
    duty_cycle=0.2,
):
    """Find the available PRF windows given a specific incidence angle range

    Parameters
    ----------
    conf :
        configuration drama.io.cfg.ConfigFile object
    inc_near :
        incidence angle [deg] at near range
    inc_far :
        incidence angle [deg] at far range
    PRF_min :
        minimum PRF to evaluate (Default value = 1000)
    PRF_max :
        maximum PRF to evaluate (Default value = 5000)
    PRF_step :
        quantization interval PRF (Default value = 1)
    duty_cycle :
        duty cycle (0 - 1) (Default value = 0.2)

    Returns
    -------
    type
        PRF_vec vector [PRF_min -> PRF_max with 1 Hz step],
        PRF_valid vector filled with: 0 - non-valid PRF, 1 - valid PRF

    """
    wl = const.c / conf.sar.f0
    Horb = conf.orbit.Horb

    sr_near = sargeo.inc_to_sr(np.radians(inc_near), Horb)
    sr_far = sargeo.inc_to_sr(np.radians(inc_far), Horb)
    sr_swth_width = sr_far - sr_near

    PRF_vec = np.arange(PRF_min, PRF_max, PRF_step)
    PRF_valid = np.zeros_like(PRF_vec)

    # range window
    rgwin = np.ceil(2 * sr_near / const.c * PRF_max).astype(np.int)

    # finds the compatible PRF ranges for each listening window
    while rgwin >= 0:
        PRF_min_win = (rgwin + duty_cycle) / (2 * sr_near / const.c)
        PRF_max_win = (rgwin + 1 - duty_cycle) / (2 * sr_far / const.c)
        valid_idx = np.logical_and(
            (PRF_vec > PRF_min_win), (PRF_vec < PRF_max_win)
        )
        PRF_valid[valid_idx] = 1
        rgwin = rgwin - 1

    return PRF_vec, PRF_valid

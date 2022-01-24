import os
import time

import matplotlib
import numpy as np
from matplotlib import pyplot as plt

import drama.constants as cnst
import drama.geo as geo
import drama.utils as trtls
from .antenna_patterns import pattern
from .azimuth_performance import (
    mode_from_conf,
    beamcentertime_to_zeroDopplertime,
    plot_pattern,
)
from drama.geo.geo_history import GeoHistory
from drama.utils.misc import save_object, load_object


# import drama.performance.sar.antenna_patterns as trpat
# from collections import namedtuple

__author__ = "Paco Lopez Dekker"
__email__ = "F.LopezDekker@tudeft.nl"


# RASRdata_ = namedtuple('RASRdata', ['la_v', 'inc_v', 'la_amb_out', 'RASupr', 'RASupr_tap', 'conf'])


class RASRdata(object):
    """
    A class containing range ambiguity data and some utilities
    """

    def __init__(
        self,
        la_v,
        inc_v,
        la_amb,
        RASupr,
        RASupr_tap,
        t_in_burst,
        conf,
        modename,
        swth,
    ):
        self.la_v = la_v
        self.inc_v = inc_v
        self.la_amb_out = la_amb
        self.RASupr = RASupr
        self.RASupr_tap = RASupr_tap
        self.conf = conf
        self.modename = modename
        self.swth = swth
        self.t_in_burst = t_in_burst

    @classmethod
    def from_file(cls, filename):
        data = load_object(filename)
        return cls(
            data.la_v,
            data.inc_v,
            data.la_amb_out,
            data.RASupr,
            data.RASupr_tap,
            data.t_in_burst,
            data.conf,
            data.modename,
            data.swth,
        )

    @classmethod
    def from_filelist(cls, list):
        la_v = []
        inc_v = []
        la_amb_out = []
        RASupr = []
        RASupr_tap = []
        swth = []
        for filename in list:
            data = load_object(filename)
            la_v.append(data.la_v)
            inc_v.append(data.inc_v)
            la_amb_out.append(data.la_amb_out)
            shp_ras = data.RASupr.shape
            RASupr.append(data.RASupr)
            RASupr_tap.append(data.RASupr_tap)
            # Now we assume that all files have same number of azimuth samples
            t_in_burst = data.t_in_burst
            conf = data.conf
            modename = data.modename
            swth.append(data.swth + np.zeros_like(data.la_v))

        # Now aggregate into single object
        la_v = np.array(la_v).flatten()
        lsort = np.argsort(la_v)
        la_v = la_v[lsort]
        inc_v = (np.array(inc_v).flatten())[lsort]
        swth = (np.array(swth).flatten())[lsort]

        RASupr = np.array(RASupr)
        RASupr_tap = np.array(RASupr_tap)
        la_amb_out = np.array(la_amb_out)
        # Reorganize that as if it was a single swath
        # RASupr_out = np.zeros((n_az_pts, Namb_az * 2 + 1, 2 * Namb, la_v.size))
        RASupr = (
            np.transpose(RASupr, (1, 2, 3, 0, 4)).reshape(
                shp_ras[0:3] + (la_v.size,)
            )
        )[:, :, :, lsort]
        RASupr_tap = (
            np.transpose(RASupr_tap, (1, 2, 3, 0, 4)).reshape(
                shp_ras[0:3] + (la_v.size,)
            )
        )[:, :, :, lsort]
        la_amb_out = (
            np.transpose(la_amb_out, (1, 2, 3, 0, 4)).reshape(
                shp_ras[0:3] + (la_v.size,)
            )
        )[:, :, :, lsort]
        # dt_amb = (np.transpose(dt_amb, (1, 0, 2, 3)).reshape((nbrst, la_v.size, namb)))[:, lsort, :]
        # dsr_amb = (np.transpose(dsr_amb, (1, 0, 2, 3)).reshape((nbrst, la_v.size, namb)))[:, lsort, :]
        return cls(
            la_v,
            inc_v,
            la_amb_out,
            RASupr,
            RASupr_tap,
            t_in_burst,
            conf,
            modename,
            swth,
        )

    def save(self, filename):
        save_object(self, filename)

    def calc_rasr(self, scattering_profile_func=None):
        shp = self.RASupr.shape
        if scattering_profile_func is None:

            def sprof(la):
                return 1 + np.zeros_like(la)

        else:
            sprof = scattering_profile_func

        rel_sig = sprof(np.degrees(self.la_v)).reshape((1, 1, 1, shp[3]))
        rel_amb = sprof(np.degrees(self.la_amb_out)) * self.RASupr
        self.rasr_parcial = rel_amb / rel_sig
        self.rasr_total = self.rasr_parcial.sum(axis=1).sum(axis=1)
        self.rasr_tap_parcial = (
            sprof(np.degrees(self.la_amb_out)) * self.RASupr_tap / rel_sig
        )
        self.rasr_tap_total = self.rasr_tap_parcial.sum(axis=1).sum(axis=1)


class RASR(RASRdata):
    """
    A class to compute range ambiguities. It is done as a class to allow quick re-analysis
    changing the backscattering profile
    """

    def __init__(
        self,
        conf,
        modename,
        swth,
        t_in_bs=[-1, 0.0, 1],
        txname="sentinel",
        rxname="sesame",
        tx_ant=None,
        rx_ant=None,
        n_az_pts=11,
        Tanalysis=10,
        Namb=2,
        savedirr="",
        view_amb_patterns=False,
        view_patterns=False,
        plot_patterns=False,
        plot_AASR=False,
        fontsize=12,
        vmin=None,
        vmax=None,
        making_off=False,
        n_amb_az=1,
        ddop=25,
        dsr=250,
        silent=False,
        use_ne=True,
        az_sampling=None,
        bistatic=True,
        verbosity=1,
    ):
        """ Computes azimuth ambiguities for single-channel systems. The operation
            mode is defined by the steering rates

            :param conf: configuration trampa.io.cfg.ConfigFile object with
                         configuration read from parameter file
            :param modename: name of section in configuration file describing
                             the mode
            :param swth: swath or subswath analyzed
            :param t_in_bs: zero Doppler time of target within burst. Note that
                            the burst length considering the zero Doppler times
                            of the imaged targets will be larger than the raw-data
                            time for TOPS-like modes with positive squint rates.
                           å For spotlight modes the oposite true.
            :param txname: name of section in parameter structure defining the
                           tx radar (antenna)
            :param rxname: same for rx radar (antenna)
            :param tx_ant: pattern class instance with tx antenna: if not given it is generated according to
                           definition in conf.
            :param rx_ant: pattern class instance with rx antenna: if not given bla, bla, bla...
            :param n_az_pts: number of points in burst, if times not explicitly given
            :param Namb: number of positive ambiguities considered; i.e. the
                         actual number of ambiguities accounted for is 2 * Namb
            :param n_amb_az: azimuth ambiguities considered
            :param savedirr: where to save the outputs
            :param ddop: Doppler step used in interpolation of geohist
            :param dsr: slant-range step ised in interpolation of geohist
            :param use_ne: True if you want to use numexpr to speed things up a bit
            :param az_sampling: azimuth sampling frequency used for simulation
            :param verbosity: how much info you want to have

        """
        # self.conf = conf
        self.info = trtls.PrInfo(verbosity, "RASR")
        # Check parameterts
        n_amb_az = int(np.max([n_amb_az, 1]))
        wl = cnst.c / conf.sar.f0
        (
            incs,
            PRFs,
            proc_bw,
            steering_rates,
            burst_lengths,
            short_name,
            proc_tap,
            tau_p,
            bw_p,
        ) = mode_from_conf(conf, modename)
        Npts = 256
        PRF = PRFs[swth]
        if modename == "stripmap_wideswath":
            PRFaz = PRFs[swth] * conf.stripmap_wideswath.n_sat
        else:
            PRFaz = PRFs[swth]
        if az_sampling is None:
            az_sampling = PRF
        inc_range = incs[swth]
        inc_v = np.linspace(incs[swth, 0], incs[swth, 1])
        # self.inc_v = inc_v
        la_v = geo.inc_to_look(np.radians(inc_v), conf.orbit.Horb)
        inc_ve = np.linspace(incs[swth, 0] - 2, incs[swth, 1] + 1)
        la_ve = geo.inc_to_look(np.radians(inc_ve), conf.orbit.Horb)
        try:
            txcnf = getattr(conf, txname)
            rxcnf = getattr(conf, rxname)
        except:
            raise ValueError(
                "Either transmitter or receiver section not defined"
            )
        if bistatic:
            dau = conf.formation_primary.dau[0]
        else:
            dau = 0
        ghist = GeoHistory(
            conf,
            tilt=txcnf.tilt,
            tilt_b=rxcnf.tilt,
            latitude=0,
            bistatic=bistatic,
            dau=dau,
            inc_range=inc_range + np.array([-10, 20]),
            inc_swth=incs[swth],
            verbosity=verbosity,
        )

        self.info.msg("Compute Patterns", 1)
        if hasattr(txcnf, "wa_tx"):
            wa_tx = txcnf.wa_tx
        else:
            wa_tx = 1
        if tx_ant is None:
            tx_phase_attr = "w_tx_phase_%i" % int(swth + 1)
            mcnf = getattr(conf, modename)
            if hasattr(mcnf, tx_phase_attr):
                we_tx = np.exp(1j * np.radians(getattr(mcnf, tx_phase_attr)))
                # print(np.angle(we_tx))
                self.info.msg(
                    "calc_nesz: applying elevation weighting to tx pattern!", 1
                )
                el0 = 0  # Pointing given in phase!
            else:
                we_tx = 1
                el0 = np.degrees(np.mean(la_v)) - txcnf.tilt
            if hasattr(txcnf, "element_pattern"):
                elcnf = getattr(conf, txcnf.element_pattern)
                el_ant = pattern(conf.sar.f0,
                                 type_a=elcnf.type_a,
                                 type_e=elcnf.type_e,
                                 La=elcnf.La,
                                 Le=elcnf.Le,
                                 el0=el0,
                                 Nel_a=elcnf.Na,
                                 Nel_e=elcnf.Ne,
                                 wa=elcnf.wa_tx,
                                 we=elcnf.we_tx,
                                 steering_rate=steering_rates[swth],
                                 Tanalysis=Tanalysis)
            else:
                el_ant = None
            tx_ant = pattern(
                conf.sar.f0,
                type_a=txcnf.type_a,
                type_e=txcnf.type_e,
                La=txcnf.La,
                Le=txcnf.Le,
                el0=el0,
                Nel_a=txcnf.Na,
                Nel_e=txcnf.Ne,
                wa=wa_tx,
                we=we_tx,
                steering_rate=steering_rates[swth],
                Tanalysis=Tanalysis,
                element_pattern=el_ant,
            )

        else:
            print("calc_rasr: using supplied tx pattern")
        if rx_ant is None:
            if hasattr(rxcnf, "wa_rx"):
                if type(rxcnf.wa_rx) is np.ndarray:
                    wa_rx = rxcnf.wa_rx
                else:
                    c0 = rxcnf.wa_rx
                    Na = rxcnf.Na
                    wa_rx = c0 - (1 - c0) * np.cos(
                        2 * np.pi * np.arange(Na) / (Na - 1)
                    )
            else:
                wa_rx = 1

            if hasattr(rxcnf, "we_rx"):
                if type(rxcnf.we_rx) is np.ndarray:
                    we_rx = rxcnf.we_rx
                else:
                    c0 = rxcnf.we_rx
                    Ne = rxcnf.Ne
                    we_rx = c0 - (1 - c0) * np.cos(
                        2 * np.pi * np.arange(Ne) / (Ne - 1)
                    )
            else:
                we_rx = 1

            if hasattr(rxcnf, "azimuth_spacing"):
                azimuth_spacing = rxcnf.azimuth_spacing
            else:
                azimuth_spacing = 1
            if hasattr(rxcnf, "elevation_spacing"):
                elevation_spacing = rxcnf.elevation_spacing
            else:
                elevation_spacing = 1
            if bistatic:
                # FIX-ME
                rx_el0 = (
                    0
                )  # because we do optimal pointing, which is not totally fair for burst modes
            else:
                rx_el0 = np.degrees(np.mean(la_v)) - txcnf.tilt

            if hasattr(rxcnf, "element_pattern"):
                self.info.msg("Initializing element pattern")
                elcnf = getattr(conf, rxcnf.element_pattern)
                rel_ant = pattern(conf.sar.f0,
                                  type_a=elcnf.type_a,
                                  type_e=elcnf.type_e,
                                  La=elcnf.La,
                                  Le=elcnf.Le,
                                  el0=rx_el0,
                                  Nel_a=elcnf.Na,
                                  Nel_e=elcnf.Ne,
                                  wa=elcnf.wa_rx,
                                  we=elcnf.we_rx,
                                  steering_rate=steering_rates[swth],
                                  Tanalysis=Tanalysis)
            else:
                rel_ant = None
            rx_ant = pattern(
                conf.sar.f0,
                type_a=rxcnf.type_a,
                type_e=rxcnf.type_e,
                La=rxcnf.La,
                Le=rxcnf.Le,
                el0=rx_el0,
                Nel_a=rxcnf.Na,
                Nel_e=rxcnf.Ne,
                wa=wa_rx,
                we=we_rx,
                steering_rate=steering_rates[swth],
                Tanalysis=Tanalysis,
                spacing_a=azimuth_spacing,
                spacing_e=elevation_spacing,
                element_pattern=rel_ant,
            )

        else:
            print("calc_rasr: using supplied rx pattern")

        fdt0 = ghist.v_Dop_spl(la_v, 0) * 2 / wl
        fd0 = np.mean(fdt0)
        if hasattr(rxcnf, "trickedDBF"):
            if hasattr(rxcnf, "DBF"):
                if rxcnf.DBF:
                    fd_amb_large = 2 * ghist.v_orb / rxcnf.La * rxcnf.Na
                    fd = fd0 + np.linspace(
                        -(n_amb_az + 0.5) * fd_amb_large,
                        (n_amb_az + 0.5) * fd_amb_large,
                        Npts,
                    )
                    # For each of the n_amb_az major ambiguitities (element-dependent)
                    # the method accounts for the 2 minor ones at thier side (PRF-dpendent)
                    n_amb_az = n_amb_az * 3 + 1
                else:
                    fd = fd0 + np.linspace(
                        -(n_amb_az + 0.5) * PRF, (n_amb_az + 0.5) * PRF, Npts
                    )
            else:
                fd = fd0 + np.linspace(
                    -(n_amb_az + 0.5) * PRF, (n_amb_az + 0.5) * PRF, Npts
                )
        else:
            fd = fd0 + np.linspace(
                -(n_amb_az + 0.5) * PRF, (n_amb_az + 0.5) * PRF, Npts
            )

        tuv = ghist.Doppler2tuv(la_v, fd, conf.sar.f0)
        (t, u, v, u_b, v_b) = tuv
        steering_rate = steering_rates[swth]
        squint = steering_rate * t
        s1_pat, xpat = tx_ant.pat_2D(v, u, grid=False, squint_rad=squint)
        sesame_pat, xpat = rx_ant.pat_2D(v_b, u_b, grid=False)
        # plt.figure()
        # plt.imshow(np.abs(np.abs(s1_pat)), origin='lower', cmap='viridis')
        # In time domain
        burst_length = burst_lengths[swth]
        # Tanalysis = Tanalysis
        # Time vector
        t0 = 0
        PRFovs = 1  # 2
        tv = (
            np.arange(int(Tanalysis * az_sampling)) / az_sampling
            - Tanalysis / 2
        )
        # Time in burst, this is also azimuth time of target in zero Doppler geom
        # FIXME: this is not valid for spotlight modes
        dudt = ghist.dudt(la_v)[
            0
        ]  # The second element in tuple is for the receiver
        if t_in_bs is None:
            self.info.msg(
                "calc_rasr: nor burt times given, calculating them from burst length"
            )
            burst_length = burst_lengths[swth]
            # FIXME: course approximation
            dr_approx = (
                2 / wl * ghist.v_orb ** 2 / ghist.sr_spl.ev(np.mean(la_v), t0)
            )
            t_int = proc_bw[swth] / dr_approx
            burst_length_eff = burst_length - t_int
            if n_az_pts > 1:
                bcts = np.linspace(
                    -burst_length_eff / 2, burst_length_eff / 2, n_az_pts
                )
                t_in_bs = beamcentertime_to_zeroDopplertime(
                    bcts, steering_rate, np.mean(dudt)
                )
            else:
                t_in_bs = np.array([0])
        else:
            t_in_bs = np.array(t_in_bs)
            n_az_pts = t_in_bs.size
        # relative to busrt center
        # t_in_bs = [-0.3, 0.0,  0.3]
        # Set font..
        font = {"family": "Arial", "weight": "normal", "size": fontsize}
        matplotlib.rc("font", **font)

        RASupr_out = np.zeros((n_az_pts, n_amb_az * 2 + 1, 2 * Namb, la_v.size))
        RASupr_tap_out = np.zeros_like(RASupr_out)

        u = ghist.t2u_spl(la_v, tv)
        v = ghist.t2v_spl(la_v, tv)
        if bistatic:
            u_b = ghist.t2u_b_spl(la_v, tv)
            v_b = ghist.t2v_b_spl(la_v, tv)
        else:
            u_b = u
            v_b = v
        # Delta Doppler to ambiguities
        if hasattr(rxcnf, "trickedDBF"):
            if hasattr(rxcnf, "DBF"):
                if rxcnf.DBF:
                    dfamb = np.array([-PRF, 0, PRF]).reshape((1, 3))
                    for n_amb in np.arange(Namb):
                        idx_amb = np.round((n_amb + 1) * fd_amb_large / PRF)
                        dfamb0 = (
                            PRF * idx_amb * np.array(([-1, 1])).reshape((1, 2))
                        )
                        dfamb = np.concatenate((dfamb, dfamb0), axis=1)
                        dfamb = np.concatenate((dfamb, dfamb0 - PRF), axis=1)
                        dfamb = np.concatenate((dfamb, dfamb0 + PRF), axis=1)
                else:
                    dfamb = PRF * (
                        np.concatenate(
                            (
                                np.arange(-n_amb_az, 0),
                                np.arange(1, n_amb_az + 1),
                            )
                        ).reshape((1, 2 * n_amb_az))
                    )
            else:
                dfamb = PRFaz * (
                    np.concatenate(
                        (np.arange(-n_amb_az, 0), np.arange(1, n_amb_az + 1))
                    ).reshape((1, 2 * n_amb_az))
                )
        else:
            dfamb = PRFaz * (
                np.concatenate(
                    (np.arange(-n_amb_az, 0), np.arange(1, n_amb_az + 1))
                ).reshape((1, 2 * n_amb_az))
            )

        la_amb_out = np.zeros_like(RASupr_out)
        fd0 = np.zeros((n_az_pts, la_v.size))
        for t_in_b_ind in range(n_az_pts):
            t_in_b = t_in_bs[t_in_b_ind]
            #  Antenna squint will be
            squint = steering_rate * (tv - t_in_b)
            if rxcnf.az_steer:
                sesame_squint = steering_rate * (tv - t_in_b)
            else:
                sesame_squint = None
            if hasattr(rxcnf, "DBF"):
                if rxcnf.DBF:
                    # Simplest Doppler dependent DBF
                    sesame_squint = u_b

            score_steer = None
            if hasattr(rxcnf, "SCORE"):
                if rxcnf.SCORE:
                    # Simplest Doppler dependent SCORE
                    score_steer = v_b
            # u for target is approximately given by
            # u = dudt * t
            # Thus target is at beam center when
            # squint = u -> t_bc

            t_bc = -steering_rate * t_in_b / (dudt - steering_rate)
            # t_bc = t_in_b * dudt / (dudt - steering_rate)
            u_bc = steering_rate * t_bc
            s1_pat, xpat = tx_ant.pat_2D(v, u, grid=False, squint_rad=squint)

            sesame_pat, xpat = rx_ant.pat_2D(
                v_b,
                u_b,
                grid=False,
                squint_rad=sesame_squint,
                steer_rad=score_steer,
            )
            # Two way patterns
            tw_pat = np.abs(s1_pat * sesame_pat) ** 2

            # Slant range and Doppler
            sr = ghist.sr_spl(la_v, tv)
            fdt0 = (
                ghist.v_Dop_spl.ev(la_v.reshape((la_v.size, 1)), t_bc) * 2 / wl
            )
            fd0[t_in_b_ind, :] = fdt0.flatten()
            famb = fdt0 + dfamb
            dop = ghist.v_Dop_spl(la_v, tv) * 2 / wl
            self.info.msg(
                "Min/Max Doppler: (%f, %f)" % (dop.min(), dop.max()), 1
            )
            dDop = dop - fdt0
            mask = np.where(np.abs(dDop) < proc_bw[swth] / 2, 1, 0)

            # if proc_tap[swth] != 1:
            c0 = proc_tap[swth]
            rDop = (dDop + proc_bw[swth] / 2) / proc_bw[swth]
            azwin = (mask * (c0 - (1 - c0) * np.cos(2 * np.pi * rDop))) ** 2
            azwin = azwin.reshape((1,) + mask.shape)

            mask = mask.reshape((1,) + mask.shape)
            la_ambs = []
            u_ambs = []
            v_ambs = []
            u_b_ambs = []
            v_b_ambs = []
            s1_pat_ambs = []
            sesame_pat_ambs = []
            tw_pat_ambs = []
            tw_sumpat_amb = 0
            ramb_supressions = []
            amb_ids = []
            # Initialize srdop to azimuth elevaton interpolaton
            # print(sr.min())
            # print(cnst.c / 2 / PRF)
            # ghist.init_srDop2t((Dop.min(), Dop.max()),
            #                    (sr.min(), sr.max()),
            #                    conf.sar.f0)
            ghist.init_srDop2t(
                (dop.min(), dop.max()),
                (
                    sr.min() - Namb * cnst.c / 2 / PRF,
                    sr.max() + Namb * cnst.c / 2 / PRF,
                ),
                conf.sar.f0,
                ddop=ddop,
                dsr=dsr,
            )
            for i_amb in range(Namb):
                # Near range ambiguity
                amb_ids.append(-(i_amb + 1))
                sr_amb = sr - (i_amb + 1) * cnst.c / 2 / PRF
                good = np.where(sr_amb > ghist.sr_min)
                bad = np.where(sr_amb < ghist.sr_min)
                la_amb = np.zeros((n_amb_az * 2 + 1,) + sr.shape)
                t_amb = np.zeros_like(la_amb)
                for i_az_amb in range(-n_amb_az, n_amb_az + 1):
                    t_1 = time.time()
                    la_amb[i_az_amb][good] = ghist.srdop2la_spl.ev(
                        dop[good] + dfamb[0, i_az_amb], sr_amb[good]
                    )
                    t_amb[i_az_amb][good] = ghist.srdop2ta_spl.ev(
                        dop[good] + dfamb[0, i_az_amb], sr_amb[good]
                    )
                    if not silent:
                        t_2 = time.time()
                        self.info.msg(
                            "la_amb and t_amb interp computation time time: %f"
                            % (t_2 - t_1),
                            1,
                        )
                la_ambs.append(la_amb)
                t_1 = time.time()
                u_amb = ghist.t2u_spl.ev(la_amb, t_amb)
                v_amb = ghist.t2v_spl.ev(la_amb, t_amb)
                if bistatic:
                    u_b_amb = ghist.t2u_b_spl.ev(la_amb, t_amb)
                    v_b_amb = ghist.t2v_b_spl.ev(la_amb, t_amb)
                else:
                    u_b_amb = u_amb
                    v_b_amb = v_amb
                if not silent:
                    t_2 = time.time()
                    self.info.msg(
                        "lu_amb and v_amb interp computation time time: %f"
                        % (t_2 - t_1),
                        1,
                    )
                u_ambs.append(u_amb)
                v_ambs.append(v_amb)
                u_b_ambs.append(u_b_amb)
                v_b_ambs.append(v_b_amb)
                # Ambiguous patterns
                t_1 = time.time()
                s1_pat_amb, xpat = tx_ant.pat_2D(
                    v_amb, u_amb, grid=False, squint_rad=squint, use_ne=use_ne
                )

                for i_az_amb in range(-n_amb_az, n_amb_az + 1):
                    s1_pat_amb[i_az_amb][bad] = 0
                s1_pat_ambs.append(s1_pat_amb)

                # if hasattr(rxcnf, 'DBF'):
                #     if rxcnf.DBF:
                #         # Simplest Doppler dependent DBF
                #
                #         sesame_squint = sesame_squint.reshape((u.shape[0],
                #                                                1, u.shape[1]))
                #
                # if hasattr(rxcnf, 'SCORE'):
                #     if rxcnf.SCORE:
                #         score_steer = score_steer.reshape((u.shape[0],
                #                                            1, u.shape[1]))
                sesame_pat_amb, xpat = rx_ant.pat_2D(
                    v_b_amb,
                    u_b_amb,
                    grid=False,
                    squint_rad=sesame_squint,
                    use_ne=use_ne,
                    steer_rad=score_steer,
                )
                if not silent:
                    t_2 = time.time()
                    self.info.msg(
                        "Ambiguous pattern computation time time: %f"
                        % (t_2 - t_1),
                        1,
                    )
                for i_az_amb in range(-n_amb_az, n_amb_az + 1):
                    sesame_pat_amb[i_az_amb][bad] = 0
                sesame_pat_ambs.append(sesame_pat_amb)
                tw_pat_amb = np.abs(s1_pat_amb * sesame_pat_amb) ** 2
                tw_pat_ambs.append(tw_pat_amb)
                tw_sumpat_amb += tw_pat_amb
                # RASR spectrum
                shp_ex = (1,) + tw_pat.shape
                rasr_spec = tw_pat_amb / tw_pat.reshape(shp_ex)
                rasr_supr = np.sum(tw_pat_amb * mask, axis=-1) / np.sum(
                    tw_pat.reshape(shp_ex) * mask, axis=-1
                )
                RASupr_out[t_in_b_ind, :, 2 * i_amb, :] = rasr_supr
                rasr_supr_tap = np.sum(azwin * rasr_spec, axis=-1) / np.sum(
                    azwin, axis=-1
                )
                RASupr_tap_out[t_in_b_ind, :, 2 * i_amb, :] = rasr_supr_tap
                la_amb_out[t_in_b_ind, :, 2 * i_amb, :] = np.sum(
                    azwin * la_amb, axis=-1
                ) / np.sum(azwin, axis=-1)

                # Far range ambiguity
                amb_ids.append((i_amb + 1))
                sr_amb = sr + (i_amb + 1) * cnst.c / 2 / PRF
                good = np.where(sr_amb > ghist.sr_min)
                bad = np.where(sr_amb < ghist.sr_min)
                # la_amb, t_amb = ghist.srDop2t(Dop, sr_amb, conf.sar.f0)
                for i_az_amb in range(-n_amb_az, n_amb_az + 1):
                    la_amb[i_az_amb][good] = ghist.srdop2la_spl.ev(
                        dop[good] + dfamb[0, i_az_amb], sr_amb[good]
                    )
                    t_amb[i_az_amb][good] = ghist.srdop2ta_spl.ev(
                        dop[good] + dfamb[0, i_az_amb], sr_amb[good]
                    )

                la_ambs.append(la_amb)
                u_amb = ghist.t2u_spl.ev(la_amb, t_amb)
                v_amb = ghist.t2v_spl.ev(la_amb, t_amb)
                if bistatic:
                    u_b_amb = ghist.t2u_b_spl.ev(la_amb, t_amb)
                    v_b_amb = ghist.t2v_b_spl.ev(la_amb, t_amb)
                else:
                    u_b_amb = u_amb
                    v_b_amb = v_amb
                u_ambs.append(u_amb)
                v_ambs.append(v_amb)
                u_b_ambs.append(u_b_amb)
                v_b_ambs.append(v_b_amb)
                # Ambiguous patterns
                s1_pat_amb, xpat = tx_ant.pat_2D(
                    v_amb, u_amb, grid=False, squint_rad=squint
                )
                for i_az_amb in range(-n_amb_az, n_amb_az + 1):
                    s1_pat_amb[i_az_amb][bad] = 0
                s1_pat_ambs.append(s1_pat_amb)
                # if hasattr(rxcnf, 'DBF'):
                #     if rxcnf.DBF:
                #         # Simplest Doppler dependent DBF
                #         sesame_squint = sesame_squint.reshape((u.shape[0],
                #                                                1, u.shape[1]))
                sesame_pat_amb, xpat = rx_ant.pat_2D(
                    v_b_amb,
                    u_b_amb,
                    grid=False,
                    squint_rad=sesame_squint,
                    steer_rad=score_steer,
                )
                for i_az_amb in range(-n_amb_az, n_amb_az + 1):
                    sesame_pat_amb[i_az_amb][bad] = 0
                sesame_pat_ambs.append(sesame_pat_amb)
                tw_pat_amb = np.abs(s1_pat_amb * sesame_pat_amb) ** 2
                tw_pat_ambs.append(tw_pat_amb)
                tw_sumpat_amb += tw_pat_amb
                # RASR spectrum
                rasr_spec = tw_pat_amb / tw_pat.reshape(shp_ex)
                rasr_supr = np.sum(tw_pat_amb * mask, axis=-1) / np.sum(
                    tw_pat.reshape(shp_ex) * mask, axis=-1
                )
                RASupr_out[t_in_b_ind, :, 2 * i_amb + 1, :] = rasr_supr
                rasr_supr_tap = np.sum(azwin * rasr_spec, axis=-1) / np.sum(
                    azwin, axis=-1
                )
                RASupr_tap_out[t_in_b_ind, :, 2 * i_amb + 1, :] = rasr_supr_tap
                la_amb_out[t_in_b_ind, :, 2 * i_amb + 1, :] = np.sum(
                    azwin * la_amb, axis=-1
                ) / np.sum(azwin, axis=-1)

            # TODO we need to include somewhere a scattering profile to account for the incident angle!
            # Azimuth ambiguity

            # Plots
            title = "%s, sw%i, $\Delta t_{az}$=%4.2f s" % (
                short_name,
                swth + 1,
                t_in_b,
            )
            modeandswth = "%s_sw%i" % (short_name, swth + 1)
            modedir = os.path.join(savedirr, modeandswth)
            name = "%s_sw%i_dtaz%ims" % (
                short_name,
                swth + 1,
                int(1000 * t_in_b),
            )
            plt_this_one = t_in_b_ind in [0, int(n_az_pts / 2), n_az_pts - 1]

            if view_patterns and plt_this_one:
                plt.figure()
                extent = [np.min(tv), np.max(tv), inc_range[0], inc_range[1]]
                plt.imshow(
                    trtls.db(np.abs(s1_pat) ** 2),
                    origin="lower",
                    extent=extent,
                    aspect="auto",
                    cmap="viridis",
                    vmin=-25,
                    vmax=0,
                )
                plt.xlabel("Time [s]")
                plt.ylabel("Incident angle [deg]")
                plt.colorbar()
                plt.figure()
                plt.imshow(
                    trtls.db(np.abs(sesame_pat) ** 2),
                    origin="lower",
                    extent=extent,
                    aspect="auto",
                    cmap="viridis",
                    vmin=-25,
                    vmax=0,
                )
                plt.xlabel("Time [s]")
                plt.ylabel("Incident angle [deg]")
                plt.colorbar()
                savefile = os.path.join(modedir, name) + "_2D_pat.png"
                os.makedirs(os.path.dirname(savefile), exist_ok=True)
                plt.savefig(savefile, bbox_inches="tight")

            if view_amb_patterns and plt_this_one:
                for ind in range(2 * Namb):
                    plt.figure()
                    extent = [
                        np.min(tv),
                        np.max(tv),
                        inc_range[0],
                        inc_range[1],
                    ]
                    plt.imshow(
                        trtls.db(np.abs(s1_pat_amb[:, ind, :]) ** 2),
                        origin="lower",
                        extent=extent,
                        aspect="auto",
                        cmap="viridis",
                        vmin=-25,
                        vmax=0,
                    )
                    plt.xlabel("Time [s]")
                    plt.ylabel("Incident angle [deg]")
                    plt.colorbar()

            if plot_patterns and plt_this_one:
                lat_ind = 25
                savefile = os.path.join(modedir, name) + "_az_pat.png"
                plot_pattern(
                    tv,
                    t_bc,
                    dDop,
                    s1_pat,
                    sesame_pat,
                    tw_pat,
                    tw_pat_amb,
                    tw_sumpat_amb,
                    proc_bw[swth],
                    Namb,
                    title,
                    savefile,
                    lat_ind=lat_ind,
                    making_off=making_off,
                )

        #        plt.figure()
        #        plt.plot(Dop[lat_ind], trtls.db(AASRt[lat_ind]))
        #        plt.xlim(fdt0[lat_ind] - PRF/2, fdt0[lat_ind] + PRF/2)
        #        plt.ylim(trtls.db(AASRt[lat_ind]).min(), 10)
        #        plt.grid(True)
        #
        #        plt.plot(Dop[lat_ind][goodf], trtls.db(AASRt[lat_ind][goodf]),
        #                 lw=2)
        #        plt.xlabel("$f_\mathrm{Doppler}$ [Hz]")
        #        plt.ylabel('AASR')
        #        plt.title(mode_names[mode])

        # Output
        title = "%s, sw%i" % (short_name, swth + 1)
        modeandswth = "%s_sw%i" % (short_name, swth + 1)
        modedir = os.path.join(savedirr, modeandswth)
        name = "%s_sw%i" % (short_name, swth + 1)

        # self.la_v = la_v
        # self.inc_v = inc_v
        # self.RASupr = RASupr_out
        # self.RASupr_tap = RASupr_tap_out
        super().__init__(
            la_v,
            inc_v,
            la_amb_out,
            RASupr_out,
            RASupr_tap_out,
            t_in_bs,
            conf,
            modename,
            swth,
        )
        # RASRdata.__init__(self, la_v, inc_v, RASupr_out, RASupr_tap_out, conf)
        self.tx_pat = s1_pat
        self.tx_pat_ambs = s1_pat_ambs
        self.rx_pat = sesame_pat
        self.rx_pat_ambs = sesame_pat_ambs

        # u, v, u_b, v_b

    def export(self):
        # RASRdata = namedtuple('RASRdata', ['la_v', 'inc_v','la_amb_out', 'RASupr', 'RASupr_tap', 'conf'])
        data = RASRdata(
            self.la_v,
            self.inc_v,
            self.la_amb_out,
            self.RASupr,
            self.RASupr_tap,
            self.t_in_burst,
            self.conf,
            self.modename,
            self.swth,
        )
        return data

    def save(self, filename):
        data = RASRdata(
            self.la_v,
            self.inc_v,
            self.la_amb_out,
            self.RASupr,
            self.RASupr_tap,
            self.t_in_burst,
            self.conf,
            self.modename,
            self.swth,
        )
        save_object(data, filename)

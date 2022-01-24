""" This module provides code to compute the azimuth performance for some SAR modes
"""
import os

import matplotlib
import numpy as np
import scipy.interpolate as interpol
from matplotlib import pyplot as plt

import drama.constants as cnst
import drama.geo as geo
import drama.utils as trtls
from .antenna_patterns import pattern
from drama.geo.geo_history import GeoHistory
from drama.io import cfg
from drama.utils.misc import save_object, load_object


# import drama.performance.sar.antenna_patterns as trpat


def mode_from_conf(conf, modename="stripmap"):
    """

    Parameters
    ----------
    conf :

    modename :
         (Default value = 'stripmap')

    Returns
    -------

    """
    try:
        mcnf = getattr(conf, modename)
        # inc
        incs = np.zeros((mcnf.inc_near.size, 2))
        incs[:, 0] = mcnf.inc_near
        incs[:, 1] = mcnf.inc_far
        PRFs = mcnf.PRF
        proc_bw = mcnf.proc_bw
        steering_rate = np.zeros(incs.shape[0])
        steering_rate[:] = np.radians(mcnf.steering_rate)
        burst_length = np.ones_like(steering_rate)
        burst_length[:] = mcnf.burst_length
        short_name = mcnf.short_name
        proc_tap = np.ones_like(steering_rate)
        pulse_length = mcnf.pulse_length
        pulse_bw = mcnf.pulse_bw
        if hasattr(mcnf, "proc_tapering"):
            proc_tap[:] = mcnf.proc_tapering
        return (
            incs,
            PRFs,
            proc_bw,
            steering_rate,
            burst_length,
            short_name,
            proc_tap,
            pulse_length,
            pulse_bw,
        )
    except:
        mesg = "Mode %s is not defined" % modename
        raise ValueError(mesg)


def beamcentertime_to_zeroDopplertime(bct, steering_rate, dudt):
    """Computes the zero Doppler time from the beamcenter and the steering rate

    Parameters
    ----------
    """
    # t_bc = - steering_rate * t_in_b / (dudt - steering_rate)
    # if steering_rate == 0:
    #     # FIXME: no squint considered here!!!
    #     zdt = bct
    # else:
    #     #zdt = - bct * (dudt - steering_rate) / steering_rate
    zdt = bct * (1 - steering_rate / dudt)
    return zdt


def plot_pattern(
    tv,
    t_bc,
    ddop,
    tx_pat,
    rx_pat,
    tw_pat,
    tw_pat_amb,
    tw_sumpat_amb,
    proc_bw,
    n_amb,
    title,
    savefile,
    lat_ind=25,
    making_off=False,
    t_span=2,
):
    """

    Parameters
    ----------
    lat_ind :
         (Default value = 25)
    making_off :
         (Default value = False)
    t_span :
         (Default value = 2)

    Returns
    -------

    """
    # lat_ind = 25
    goodf = np.where(np.abs(ddop[lat_ind]) < proc_bw / 2)
    plt.figure()
    plt.plot(tv, trtls.db(np.abs(tx_pat[lat_ind]) ** 2), label="$G_{tx}$")
    plt.xlabel("Integration window [s]")
    plt.ylabel("G [dB]")
    plt.ylim(-40, 3)
    plt.xlim(-t_span / 2 + t_bc[lat_ind], t_span / 2 + t_bc[lat_ind])
    plt.title(title)
    plt.grid(True)
    os.makedirs(os.path.dirname(savefile), exist_ok=True)
    if making_off:
        svfl = (
            os.path.splitext(savefile)[0]
            + "_p1."
            + os.path.splitext(savefile)[1]
        )
        plt.savefig(svfl, bbox_inches="tight")

    plt.plot(tv, trtls.db(np.abs(rx_pat[lat_ind]) ** 2), label="$G_{rx}$")
    if making_off:
        svfl = (
            os.path.splitext(savefile)[0]
            + "_p2."
            + os.path.splitext(savefile)[1]
        )
        plt.savefig(svfl, bbox_inches="tight")

    plt.plot(tv, trtls.db(tw_pat[lat_ind]), "g", lw=1)
    plt.plot(
        tv[goodf], trtls.db(tw_pat[lat_ind][goodf]), "g", label="$G_{2w}$", lw=3
    )
    if making_off:
        svfl = (
            os.path.splitext(savefile)[0]
            + "_p3."
            + os.path.splitext(savefile)[1]
        )
        plt.savefig(svfl, bbox_inches="tight")

    for ind in range(2 * n_amb):
        plt.plot(tv, (trtls.db(tw_pat_amb[lat_ind, ind])), "--", lw=1)
        if making_off:
            svfl = (
                os.path.splitext(savefile)[0]
                + ("_p%i." % (int(4 + ind)))
                + os.path.splitext(savefile)[1]
            )
            plt.savefig(svfl, bbox_inches="tight")

    plt.plot(tv, (trtls.db(tw_sumpat_amb[lat_ind])), "r", lw=1)
    plt.plot(
        tv[goodf],
        (trtls.db(tw_sumpat_amb[lat_ind][goodf])),
        "r",
        lw=3,
        label="$\sum G_{2w,a}$ ",
    )

    plt.legend()

    plt.savefig(savefile, bbox_inches="tight")


class AASRdata(object):
    """A class containing azimuth ambiguity data and some utilities

    Parameters
    ----------
    la_v :
        look angles
    inc_v :
        incident angles
    aasr :
        integrated AASR
    aasr_par :
        AASR for each ambiguity
    aasr_tap :
        integrated AASR considering processing with tapering
    aasr_par_tap :
        param t_in_burst: azimuth positions in burst, expressed as zero Doppler offsets with respect to burst center
    dt_amb :
        slow-time offset of ambiguity
    dsr_amb :
        slant-range offset of ambiguity

    Returns
    -------

    """

    def __init__(
        self,
        la_v,
        inc_v,
        aasr,
        aasr_par,
        aasr_tap,
        aasr_par_tap,
        t_in_burst,
        dt_amb,
        dsr_amb,
        conf,
        modename,
        swth,
    ):
        """
        Initialise AASRdata
        """
        self.la_v = la_v
        self.inc_v = inc_v
        self.aasr = aasr
        self.aasr_tap = aasr_tap
        self.aasr_par = aasr_par
        self.aasr_par_tap = aasr_par_tap
        self.t_in_burst = t_in_burst
        self.dt_amb = dt_amb
        self.dsr_amb = dsr_amb
        self.conf = conf
        self.modename = modename
        self.swth = swth

    @classmethod
    def from_file(cls, filename):
        data = load_object(filename)
        # I think this two step approach make it robust to changes to class methods
        return cls(
            data.la_v,
            data.inc_v,
            data.aasr,
            data.aasr_par,
            data.aasr_tap,
            data.aasr_par_tap,
            data.t_in_burst,
            data.dt_amb,
            data.dsr_amb,
            data.conf,
            data.modename,
            data.swth,
        )

    @classmethod
    def from_filelist(cls, list):
        la_v = []
        inc_v = []
        aasr = []
        aasr_par = []
        aasr_tap = []
        aasr_par_tap = []
        dt_amb = []
        dsr_amb = []
        nfile = len(list)
        swth = []
        for filename in list:
            data = load_object(filename)
            la_v.append(data.la_v)
            inc_v.append(data.inc_v)
            aasr.append(data.aasr)
            aasr_tap.append(data.aasr_tap)
            aasr_par.append(data.aasr_par)
            aasr_par_tap.append(data.aasr_par_tap)
            dt_amb.append(data.dt_amb)
            dsr_amb.append(data.dsr_amb)
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

        nbrst = t_in_burst.size
        aasr = np.array(aasr)
        aasr_tap = np.array(aasr_tap)
        aasr_par = np.array(aasr_par)
        aasr_par_tap = np.array(aasr_par_tap)
        dt_amb = np.array(dt_amb)
        dsr_amb = np.array(dsr_amb)
        namb = aasr_par_tap.shape[-1]
        if len(aasr.shape) == 3:
            aasr = (np.transpose(aasr, (1, 0, 2)).reshape((nbrst, la_v.size)))[
                :, lsort
            ]
            aasr_tap = (
                np.transpose(aasr_tap, (1, 0, 2)).reshape((nbrst, la_v.size))
            )[:, lsort]
            aasr_par = (
                np.transpose(aasr_par, (1, 0, 2, 3)).reshape(
                    (nbrst, la_v.size, namb)
                )
            )[:, lsort, :]
            aasr_par_tap = (
                np.transpose(aasr_par_tap, (1, 0, 2, 3)).reshape(
                    (nbrst, la_v.size, namb)
                )
            )[:, lsort, :]
            dt_amb = (
                np.transpose(dt_amb, (1, 0, 2, 3)).reshape(
                    (nbrst, la_v.size, namb)
                )
            )[:, lsort, :]
            dsr_amb = (
                np.transpose(dsr_amb, (1, 0, 2, 3)).reshape(
                    (nbrst, la_v.size, namb)
                )
            )[:, lsort, :]
        return cls(
            la_v,
            inc_v,
            aasr,
            aasr_par,
            aasr_tap,
            aasr_par_tap,
            t_in_burst,
            dt_amb,
            dsr_amb,
            conf,
            modename,
            swth,
        )

    def save(self, filename):
        save_object(self, filename)

    def plot_aasr(
        self, intrinsic=True, tapered=True, burst_ind=None, partial=True
    ):
        """

        Parameters
        ----------
        intrinsic :
             (Default value = True)
        tapered :
             (Default value = True)
        burst_ind :
             (Default value = None)
        partial :
             (Default value = True)

        Returns
        -------

        """
        plt.figure()
        n_az = self.aasr.shape[0]
        n_amb = self.aasr_par.shape[2]
        amb_id = np.concatenate(
            (np.arange(-n_amb / 2, 0), np.arange(1, n_amb / 2 + 1))
        ).reshape((1, n_amb))
        amb_id = amb_id.flatten()
        if burst_ind is None:
            burst_ind = int(n_az / 2)
        # plt.plot(inc_v, trtls.db(AASR))
        if intrinsic:
            plt.plot(
                self.inc_v,
                trtls.db(self.aasr[burst_ind]),
                label="Intrinsic",
                lw=3,
            )
            if partial:
                for aind in range(n_amb):
                    lb = r"$I_{%i}$" % (int(amb_id[aind]))
                    plt.plot(
                        self.inc_v,
                        trtls.db(self.aasr_par[burst_ind, :, aind]),
                        label=lb,
                    )

        if tapered:
            plt.plot(
                self.inc_v,
                trtls.db(self.aasr_tap[burst_ind]),
                label="Tapered",
                lw=3,
            )
            if partial:
                for aind in range(n_amb):
                    lb = r"$T_{%i}$" % (int(amb_id[aind]))
                    plt.plot(
                        self.inc_v,
                        trtls.db(self.aasr_par[burst_ind, :, aind]),
                        label=lb,
                    )
        plt.legend(loc="best")

        plt.grid(True)
        plt.xlabel("Incident angle [deg]")
        plt.ylabel("AASR [dB]")
        # plt.title(title)
        # savefile = os.path.join(modedir, name) + "_AASR.png"
        # os.makedirs(os.path.dirname(savefile), exist_ok=True)
        # plt.savefig(savefile, bbox_inches='tight')


class NESZdata(object):
    """A class containing azimuth ambiguity data and some utilities"""

    def __init__(
        self, la_v, inc_v, nesz, nesz_tap, t_in_burst, conf, modename, swth
    ):
        """

        :param la_v: look angles
        :param inc_v: incident angles
        :param nesz: NESZ
        :param nesz_tap: NESZ, considering processing with tapering
        :param t_in_burst: azimuth positions in burst, expressed as zero Doppler
                           offsets with respect to burst center
        :param conf: radar configuration
        :param modename:
        :param swth:
        """
        self.la_v = la_v
        self.inc_v = inc_v
        self.nesz = nesz
        self.nesz_tap = nesz_tap
        self.t_in_burst = t_in_burst
        self.conf = conf
        self.modename = modename
        self.swth = swth

    @classmethod
    def from_file(cls, filename):
        data = load_object(filename)
        # I think this two step approach make it robust to changes to class methods
        return cls(
            data.la_v,
            data.inc_v,
            data.nesz,
            data.nesz_tap,
            data.t_in_burst,
            data.conf,
            data.modename,
            data.swth,
        )

    @classmethod
    def from_filelist(cls, list):
        la_v = []
        inc_v = []
        nesz = []
        nesz_tap = []
        nfile = len(list)
        modename = []
        swth = []
        for filename in list:
            data = load_object(filename)
            la_v.append(data.la_v)
            inc_v.append(data.inc_v)
            nesz.append(data.nesz)
            nesz_tap.append(data.nesz_tap)
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

        nbrst = t_in_burst.size
        nesz = np.array(nesz)
        nesz_tap = np.array(nesz_tap)
        if len(nesz.shape) == 3:
            nesz = (np.transpose(nesz, (1, 0, 2)).reshape((nbrst, la_v.size)))[
                :, lsort
            ]
            nesz_tap = (
                np.transpose(nesz_tap, (1, 0, 2)).reshape((nbrst, la_v.size))
            )[:, lsort]

        return cls(
            la_v, inc_v, nesz, nesz_tap, t_in_burst, conf, modename, swth
        )

    def prf(self):
        """ """
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
        ) = mode_from_conf(self.conf, self.modename)
        return PRFs[self.swth]

    def save(self, filename):
        """

        Parameters
        ----------
        filename :


        Returns
        -------

        """
        save_object(self, filename)

    def plot_nesz(self, intrinsic=True, tapered=True, burst_ind=None):
        """

        Parameters
        ----------
        intrinsic :
             (Default value = True)
        tapered :
             (Default value = True)
        burst_ind :
             (Default value = None)

        Returns
        -------

        """
        plt.figure()
        n_az = self.nesz.shape[0]
        if burst_ind is None:
            burst_ind = int(n_az / 2)
        # plt.plot(inc_v, trtls.db(AASR))
        if intrinsic:
            plt.plot(self.inc_v, self.nesz[burst_ind], label="Intrinsic", lw=3)

        if tapered:
            plt.plot(
                self.inc_v, self.nesz_tap[burst_ind], label="Tapered", lw=3
            )

        plt.legend(loc="best")

        plt.grid(True)
        plt.xlabel("Incident angle [deg]")
        plt.ylabel("NESZ [dB]")


def calc_aasr(
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
    plot_patterns=True,
    plot_AASR=True,
    fontsize=12,
    vmin=None,
    vmax=None,
    making_off=False,
    az_sampling=None,
    t_span_pattern=2,
    verbosity=1,
    bistatic=True,
):
    """Computes azimuth ambiguities for single-channel systems. The operation
        mode is defined by the steering rates

    Parameters
    ----------
    conf :
        configuration trampa.io.cfg.ConfigFile object with
        configuration read from parameter file
    modename :
        name of section in configuration file describing
        the mode
    swth :
        swath or subswath analyzed
    t_in_bs :
        zero Doppler time of target within burst. Note that
        the burst length considering the zero Doppler times
        of the imaged targets will be larger than the raw-data
        time for TOPS-like modes with positive squint rates.
        For spotlight modes the opposite true. (Default value = [-1)
    txname :
        name of section in parameter structure defining the
        tx radar (antenna) (Default value = 'sentinel')
    rxname :
        same for rx radar (antenna) (Default value = 'sesame')
    tx_ant :
        pattern class instance with tx antenna: if not given it is generated according to
        definition in conf. (Default value = None)
    rx_ant :
        pattern class instance with rx antenna: if not given bla, bla, bla... (Default value = None)
    n_az_pts :
        number of points in burst, if times not explicitly given (Default value = 11)
    Namb :
        number of positive ambiguities considered; i.e. the
        actual number of ambiguities accounted for is 2 * Namb (Default value = 2)
    savedirr :
        where to save the outputs (Default value = '')
    az_sampling :
        azimuth sampling in calculation. Defaults to PRF
    making_off :
        make several plots to illustrate ambiguity computation (Default value = False)
    t_span_pattern :
        time range in plot of ambiguity calculation (Default value = 2)
    verbosity :
        controls how much output is printed during computation (Default value = 1)
    bistatic :
        True for bistatic, False for monostatic (Default value = True)
    0.0 :

    1] :

    Tanalysis :
         (Default value = 10)
    view_amb_patterns :
         (Default value = False)
    view_patterns :
         (Default value = False)
    plot_patterns :
         (Default value = True)
    plot_AASR :
         (Default value = True)
    fontsize :
         (Default value = 12)
    vmin :
         (Default value = None)
    vmax :
         (Default value = None)

    Returns
    -------

    """
    # Console output
    info = trtls.PrInfo(verbosity, "calc_aasr")
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
    if modename == "stripmap_wideswath":
        PRF = PRFs[swth] * conf.stripmap_wideswath.n_sat
    else:
        PRF = PRFs[swth]
    if az_sampling is None:
        az_sampling = PRF
    inc_range = incs[swth]
    inc_v = np.linspace(incs[swth, 0], incs[swth, 1])
    la_v = geo.inc_to_look(np.radians(inc_v), conf.orbit.Horb)
    inc_ve = np.linspace(incs[swth, 0] - inc_range[0] + 0.1, incs[swth, 1] + 1)
    la_ve = geo.inc_to_look(np.radians(inc_ve), conf.orbit.Horb)
    try:
        txcnf = getattr(conf, txname)
        rxcnf = getattr(conf, rxname)
    except:
        raise ValueError("Either transmitter or receiver section not defined")
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
        inc_range=inc_range + np.array([-3, 3]),
        verbosity=verbosity,
    )

    info.msg("Compute Patterns", 2)
    if hasattr(txcnf, "wa_tx"):
        wa_tx = txcnf.wa_tx
    else:
        wa_tx = 1
    if hasattr(rxcnf, "we_tx"):
        we_tx = rxcnf.we_tx
    else:
        we_tx = 1
    if tx_ant is None:
        tx_az_phase_attr = "wa_tx_phase_%i" % int(swth + 1)
        tx_el_phase_attr = "we_tx_phase_%i" % int(swth + 1)
        mcnf = getattr(conf, modename)
        if hasattr(mcnf, tx_el_phase_attr):
            we_tx = np.exp(1j * np.radians(getattr(mcnf, tx_el_phase_attr)))
            # print(np.angle(we_tx))
            info.msg(
                "calc_nesz: applying elevation weighting to tx pattern!", 1
            )
            el0 = 0  # Pointing given in phase!
        else:
            we_tx = 1
            el0 = np.degrees(np.mean(la_v)) - txcnf.tilt
        # PLD 20220114 Adding code for azimuth beam spoiling
        if hasattr(mcnf, tx_az_phase_attr):
            info.msg("Applying azimuth phase spoiling. This will probably not work with azimuth steeing modes", 1)
            wa_tx = np.exp(1j * np.radians(getattr(mcnf, tx_az_phase_attr)))
            # print(np.angle(we_tx))

            az0 = 0  # Pointing given in phase!
        if hasattr(txcnf, "element_pattern"):
            if type(txcnf.element_pattern) == list:
                rel_ant = []
                for elcnf__ in txcnf.element_pattern:
                    elcnf_ = getattr(conf, elcnf__)
                    el_ant_ = pattern(conf.sar.f0,
                                      type_a=elcnf_.type_a,
                                      type_e=elcnf_.type_e,
                                      La=elcnf_.La,
                                      Le=elcnf_.Le,
                                      el0=(np.degrees(np.mean(la_v)) - elcnf_.tilt),
                                      Nel_a=elcnf_.Na,
                                      Nel_e=elcnf_.Ne,
                                      wa=elcnf_.wa_tx,
                                      we=elcnf_.we_tx,
                                      steering_rate=steering_rates[swth],
                                      Tanalysis=Tanalysis)
                    el_ant.append(el_ant_)
            else:
                elcnf = getattr(conf, txcnf.element_pattern)
                el_ant = pattern(conf.sar.f0,
                                 type_a=elcnf.type_a,
                                 type_e=elcnf.type_e,
                                 La=elcnf.La,
                                 Le=elcnf.Le,
                                 el0=(np.degrees(np.mean(la_v)) - elcnf.tilt),
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
        info.msg("calc_aasr: using supplied tx pattern")
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
            info.msg("Initializing element pattern")

            if type(rxcnf.element_pattern) == list:
                rel_ant = []
                for elcnf__ in rxcnf.element_pattern:
                    elcnf_ = getattr(conf, elcnf__)
                    rel_ant_ = pattern(conf.sar.f0,
                                       type_a=elcnf_.type_a,
                                       type_e=elcnf_.type_e,
                                       La=elcnf_.La,
                                       Le=elcnf_.Le,
                                       el0=rx_el0,
                                       Nel_a=elcnf_.Na,
                                       Nel_e=elcnf_.Ne,
                                       wa=elcnf_.wa_rx,
                                       we=elcnf_.we_rx,
                                       steering_rate=steering_rates[swth],
                                       Tanalysis=Tanalysis)
                    rel_ant.append(rel_ant_)
            else:
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
        print("calc_aasr: using supplied rx pattern")

    fdt0 = ghist.v_Dop_spl(la_v, 0) * 2 / wl
    fd0 = np.mean(fdt0)
    # FIXME
    if hasattr(rxcnf, "trickedDBF"):
        if rxcnf.DBF:
            # FIXME: this broke my STEREOID simulation, and it not correct in general.
            # fd_amb_large = 2 * ghist.v_orb / rxcnf.La * rxcnf.Na
            fd_amb_large = PRF
            fd = fd0 + np.linspace(
                -(Namb + 0.5) * fd_amb_large, (Namb + 0.5) * fd_amb_large, Npts
            )
        else:
            fd = fd0 + np.linspace(
                -(Namb + 0.5) * PRF, (Namb + 0.5) * PRF, Npts
            )
    else:
        fd = fd0 + np.linspace(-(Namb + 0.5) * PRF, (Namb + 0.5) * PRF, Npts)

    tuv = ghist.Doppler2tuv(la_v, fd, conf.sar.f0)
    (t, u, v, u_b, v_b) = tuv
    steering_rate = steering_rates[swth]
    squint = steering_rate * t
    tx_pat, xpat = tx_ant.pat_2D(v, u, grid=False, squint_rad=squint)
    rx_pat, xpat = rx_ant.pat_2D(v_b, u_b, grid=False)
    # plt.figure()
    # plt.imshow(np.abs(np.abs(s1_pat)), origin='lower', cmap='viridis')
    # In time domain
    burst_length = burst_lengths[swth]
    # Tanalysis = Tanalysis
    # Time vector
    t0 = 0
    tv = np.arange(int(Tanalysis * az_sampling)) / az_sampling - Tanalysis / 2
    # Time in burst, this is also azimuth time of target in zero Doppler geom
    # FIXME: this is not valid for spotlight modes
    dudt, dudt_r = ghist.dudt(la_v)  # The second element in tuple is for the receiver
    # PLD 7 June 2020
    # Adjusting steering rate of receiver to accont for different du_dt
    steering_rate_r = np.mean(dudt_r) / np.mean(dudt) * steering_rate
    info.msg("Steering rates: %f, %f" % (steering_rate, steering_rate_r), 2)
    if t_in_bs is None:
        print(
            "calc_aasr: nor burt times given, calculating them from burst length"
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

    # Prepare outputs
    aasr_out = np.zeros((n_az_pts, la_v.size))
    aasr_par_out = np.zeros((n_az_pts, la_v.size, 2 * Namb))
    aasr_tap_out = np.zeros_like(aasr_out)
    aasr_par_tap_out = np.zeros_like(aasr_par_out)
    dt_amb_out = np.zeros_like(aasr_par_out)
    dsr_amb_out = np.zeros_like(aasr_par_out)

    u = ghist.t2u_spl(la_v, tv)
    v = ghist.t2v_spl(la_v, tv)
    if bistatic:
        u_b = ghist.t2u_b_spl(la_v, tv)
        v_b = ghist.t2v_b_spl(la_v, tv)
    else:
        u_b = u
        v_b = v
    # Delta Doppler to ambiguities
    # FIXME
    if hasattr(rxcnf, "trickedDBF"):
        if rxcnf.DBF:
            dfamb = np.array([-PRF, PRF]).reshape((1, 2))
            for n_amb in np.arange(Namb):
                idx_amb = np.round((n_amb + 1) * fd_amb_large / PRF)
                dfamb0 = PRF * idx_amb * np.array(([-1, 1])).reshape((1, 2))
                dfamb = np.concatenate((dfamb, dfamb0), axis=1)
                dfamb = np.concatenate((dfamb, dfamb0 - PRF), axis=1)
                dfamb = np.concatenate((dfamb, dfamb0 + PRF), axis=1)
        else:
            dfamb = PRF * (
                np.concatenate(
                    (np.arange(-Namb, 0), np.arange(1, Namb + 1))
                ).reshape((1, 2 * Namb))
            )
    else:
        dfamb = PRF * (
            np.concatenate(
                (np.arange(-Namb, 0), np.arange(1, Namb + 1))
            ).reshape((1, 2 * Namb))
        )

    for t_in_b_ind in range(n_az_pts):
        t_in_b = t_in_bs[t_in_b_ind]
        #  Antenna squint will be
        squint = steering_rate * (tv - t_in_b)
        if rxcnf.az_steer:
            sesame_squint = steering_rate_r * (tv - t_in_b)
        else:
            sesame_squint = None
        if hasattr(rxcnf, "DBF"):
            if rxcnf.DBF:
                # Simplest Doppler dependent DBF
                sesame_squint = np.copy(u_b)
        score_steer = None
        if hasattr(rxcnf, "SCORE"):
            if rxcnf.SCORE:
                # Simplest Doppler dependent SCORE
                score_steer = np.copy(v_b)
        # u for target is approximately given by
        # u = dudt * t
        # Thus target is at beam center when
        # squint = u -> t_bc

        t_bc = -steering_rate * t_in_b / (dudt - steering_rate)
        # t_bc = t_in_b * dudt / (dudt - steering_rate)
        u_bc = steering_rate * t_bc

        # Slant range and Doppler
        sr = ghist.sr_spl(la_v, tv)
        # Time at which we see Doppler ambiguities
        fdt0 = ghist.v_Dop_spl.ev(la_v.reshape((la_v.size, 1)), t_bc) * 2 / wl
        famb = fdt0 + dfamb
        tuv = ghist.Doppler2tuv(la_v, famb, conf.sar.f0)

        t_amb = tuv[0]
        dt_amb = t_amb - t_bc
        dt_amb_out[t_in_b_ind] = dt_amb
        sr0 = ghist.sr_spl.ev(la_v.reshape((la_v.size, 1)), t0)
        sr_amb = ghist.sr_spl.ev(la_v.reshape((la_v.size, 1)), t_amb)
        dsr_amb = sr_amb - sr0
        dsr_amb_out[t_in_b_ind] = dsr_amb
        sr_amb = sr0 - dsr_amb

        # Look angle at t0 of ambiguity; we correct for range migration
        sr0e = ghist.sr_spl.ev(la_ve.reshape((la_ve.size, 1)), t0)
        sr2look = interpol.interp1d(sr0e.flatten(), la_ve)
        la_amb = sr2look(sr_amb).reshape(dt_amb.shape + (1,))

        # Geometry of ambiguities
        tv_rshp = tv.reshape((1, 1, tv.size))
        tv_amb = tv_rshp + dt_amb.reshape(dt_amb.shape + (1,))
        u_amb = ghist.t2u_spl.ev(la_amb, tv_amb)
        v_amb = ghist.t2v_spl.ev(la_amb, tv_amb)
        if bistatic:
            u_b_amb = ghist.t2u_b_spl.ev(la_amb, tv_amb)
            v_b_amb = ghist.t2v_b_spl.ev(la_amb, tv_amb)
        else:
            u_b_amb = u_amb
            v_b_amb = v_amb

        Dop = ghist.v_Dop_spl(la_v, tv) * 2 / wl

        tx_pat, xpat = tx_ant.pat_2D(v, u, grid=False, squint_rad=squint)
        rx_pat, xpat = rx_ant.pat_2D(
            v_b,
            u_b,
            grid=False,
            squint_rad=sesame_squint,
            steer_rad=score_steer,
        )
        # Ambiguous patterns
        tx_pat_amb, xpat = tx_ant.pat_2D(
            v_amb, u_amb, grid=False, squint_rad=squint
        )
        if hasattr(rxcnf, "DBF"):
            if rxcnf.DBF:
                # Simplest Doppler dependent DBF
                sesame_squint = sesame_squint.reshape(
                    (u.shape[0], 1, u.shape[1])
                )

        if hasattr(rxcnf, "SCORE"):
            if rxcnf.SCORE:
                score_steer = score_steer.reshape((u.shape[0], 1, u.shape[1]))

        rx_pat_amb, xpat = rx_ant.pat_2D(
            v_b_amb,
            u_b_amb,
            grid=False,
            squint_rad=sesame_squint,
            steer_rad=score_steer,
        )

        # Two way patterns
        tw_pat = np.abs(tx_pat * rx_pat) ** 2
        tw_pat_amb = np.abs(tx_pat_amb * rx_pat_amb) ** 2
        tw_sumpat_amb = np.sum(tw_pat_amb, axis=1)

        # AASR spectrum, integrated for all ambiguities
        aasrt = tw_sumpat_amb / tw_pat
        # Individual ones
        aasrt_par = tw_pat_amb / tw_pat.reshape(
            (tw_pat.shape[0], 1, tw_pat.shape[1])
        )

        # Azimuth ambiguity
        dDop = Dop - fdt0
        mask = np.where(np.abs(dDop) < proc_bw[swth] / 2, 1, 0)
        aasr_tot = np.sum(tw_sumpat_amb * mask, axis=-1) / np.sum(
            tw_pat * mask, axis=-1
        )
        # print(tw_pat.shape)
        # print(tw_pat_amb.shape)
        mask_rshp = mask.reshape((tw_pat.shape[0], 1, tw_pat.shape[1]))
        aasr_par = np.sum(tw_pat_amb * mask_rshp, axis=-1) / np.sum(
            tw_pat * mask, axis=-1
        ).reshape((tw_pat.shape[0], 1))
        aasr_out[t_in_b_ind, :] = aasr_tot
        aasr_par_out[t_in_b_ind, :, :] = aasr_par

        if proc_tap[swth] != 1:
            c0 = proc_tap[swth]
            rDop = (dDop + proc_bw[swth] / 2) / proc_bw[swth]
            azwin = (mask * (c0 - (1 - c0) * np.cos(2 * np.pi * rDop))) ** 2
            aasr_tap = np.sum(azwin * aasrt, axis=-1) / np.sum(azwin, axis=-1)
            azwin_rshp = azwin.reshape((tw_pat.shape[0], 1, tw_pat.shape[1]))
            aasr_par_tap = np.sum(aasrt_par * azwin_rshp, axis=-1) / np.sum(
                azwin, axis=-1
            ).reshape((tw_pat.shape[0], 1))
            aasr_tap_out[t_in_b_ind, :] = aasr_tap
            aasr_par_tap_out[t_in_b_ind, :, :] = aasr_par_tap
            #            plt.figure()
            #            plt.plot(dDop[25,:], azwin[25,:])
            #            plt.figure()
            #            plt.plot(dDop[25,:], trtls.db(AASRt[25]))

        # Plots
        title = "%s, sw%i, $\Delta t_{az}$=%4.2f s" % (
            short_name,
            swth + 1,
            t_in_b,
        )
        modeandswth = "%s_sw%i" % (short_name, swth + 1)
        modedir = os.path.join(savedirr, modeandswth)
        name = "%s_sw%i_dtaz%ims" % (short_name, swth + 1, int(1000 * t_in_b))
        plt_this_one = t_in_b_ind in [0, int(n_az_pts / 2), n_az_pts - 1]

        if view_patterns and plt_this_one:
            plt.figure()
            extent = [np.min(tv), np.max(tv), inc_range[0], inc_range[1]]
            plt.imshow(
                trtls.db(np.abs(tx_pat) ** 2),
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
                trtls.db(np.abs(rx_pat) ** 2),
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
                extent = [np.min(tv), np.max(tv), inc_range[0], inc_range[1]]
                plt.imshow(
                    trtls.db(np.abs(tx_pat_amb[:, ind, :]) ** 2),
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
                tx_pat,
                rx_pat,
                tw_pat,
                tw_pat_amb,
                tw_sumpat_amb,
                proc_bw[swth],
                Namb,
                title,
                savefile,
                lat_ind=lat_ind,
                making_off=making_off,
                t_span=t_span_pattern,
            )

        if plot_AASR and plt_this_one:
            plt.figure()
            # plt.plot(inc_v, trtls.db(AASR))
            if proc_tap[swth] != 1:
                plt.plot(inc_v, trtls.db(aasr_tot), label="Intrinsic")
                plt.plot(
                    inc_v,
                    trtls.db(aasr_tap),
                    label=("Tap. coef. %3.2f" % proc_tap[swth]),
                )
                plt.legend(loc="best")
            else:
                plt.plot(inc_v, trtls.db(aasr_tot))
            plt.grid(True)
            plt.xlabel("Incident angle [deg]")
            plt.ylabel("AASR [dB]")
            plt.title(title)
            savefile = os.path.join(modedir, name) + "_AASR.png"
            os.makedirs(os.path.dirname(savefile), exist_ok=True)
            plt.savefig(savefile, bbox_inches="tight")

    # Output
    title = "%s, sw%i" % (short_name, swth + 1)
    modeandswth = "%s_sw%i" % (short_name, swth + 1)
    modedir = os.path.join(savedirr, modeandswth)
    name = "%s_sw%i" % (short_name, swth + 1)
    if plot_AASR:
        if n_az_pts > 8:
            plt.figure()
            AASR_final = np.where(
                aasr_tap_out > aasr_out, aasr_out, aasr_tap_out
            )
            corners = [
                np.min(t_in_bs),
                np.max(t_in_bs),
                inc_range[0],
                inc_range[1],
            ]
            aspect = (
                4
                * (np.max(t_in_bs) - np.min(t_in_bs))
                / (inc_range[1] - inc_range[0])
            )
            AASR_dB = 10 * np.log10(AASR_final.transpose())
            if vmin is None:
                vmin = np.nanmin(AASR_dB)
            if vmax is None:
                vmax = np.nanmax(AASR_dB)
            ims = plt.imshow(
                AASR_dB,
                origin="lower",
                aspect=aspect,
                interpolation="nearest",
                cmap="viridis_r",
                extent=corners,
                vmin=vmin,
                vmax=vmax,
            )
            plt.xlabel("Zero Doppler Time [s]")
            ax = plt.gca()
            ax.locator_params(axis="x", nbins=3)
            plt.ylabel("Incident angle [deg]")
            plt.title("AASR")
            cbar = trtls.add_colorbar(ims)
            cbar.set_label("dB")
            savefile = os.path.join(modedir, name) + "_AASR_all.png"
            plt.savefig(savefile, bbox_inches="tight")
        else:
            plt.figure()
            # plt.plot(inc_v, trtls.db(AASR))
            for t_in_b_ind in range(n_az_pts):
                t_in_b = t_in_bs[t_in_b_ind]
                if proc_tap[swth] != 1:
                    plt.plot(
                        inc_v,
                        trtls.db(aasr_tap_out[t_in_b_ind]),
                        label=("Intr. $\Delta t_{az}$=%4.2f s" % t_in_b),
                    )
                    # plt.plot(inc_v, trtls.db(AASR_tap_out[t_in_b_ind]), '--',
                    #         label=("Tap. coef. %3.2f" % proc_tap[swth]))

                else:
                    plt.plot(
                        inc_v,
                        trtls.db(aasr_tot),
                        label=("Intr. $\Delta t_{az}$=%4.2f s" % t_in_b),
                    )
            plt.grid(True)
            plt.legend(loc="best")
            plt.xlabel("Incident angle [deg]")
            plt.ylabel("AASR [dB]")
            plt.title(title)
            savefile = os.path.join(modedir, name) + "_AASR.png"
            os.makedirs(os.path.dirname(savefile), exist_ok=True)
            plt.savefig(savefile, bbox_inches="tight")

    return AASRdata(
        la_v,
        inc_v,
        aasr_out,
        aasr_par_out,
        aasr_tap_out,
        aasr_par_tap_out,
        t_in_bs,
        dt_amb_out,
        dsr_amb_out,
        conf,
        modename,
        swth,
    )


def calc_nesz(
    conf,
    modename,
    swth,
    t_in_bs=[-1, 0.0, 1],
    txname="sentinel",
    rxname="sesame",
    tx_ant=None,
    rx_ant=None,
    n_az_pts=11,
    Tanalysis=2.5,
    extra_losses=0,
    savedirr="",
    plot_nesz=True,
    fontsize=12,
    vmin=None,
    vmax=None,
    az_sampling=None,
    t_span_pattern=2,
    verbosity=1,
    bistatic=True,
):
    """Computes azimuth ambiguities for single-channel systems. The operation
        mode is defined by the steering rates

    Parameters
    ----------
    conf :
        configuration drama.io.cfg.ConfigFile object with
        configuration read from parameter file
    modename :
        name of section in configuration file describing
        the mode
    swth :
        swath or subswath analyzed
    t_in_bs :
        zero Doppler time of target within burst. Note that
        the burst length considering the zero Doppler times
        of the imaged targets will be larger than the raw-data
        time for TOPS-like modes with positive squint rates.
        For spotlight modes the opposite true. (Default value = [-1)
    txname :
        name of section in parameter structure defining the
        tx radar (antenna) (Default value = 'sentinel')
    rxname :
        same for rx radar (antenna) (Default value = 'sesame')
    tx_ant :
        pattern class instance with tx antenna: if not given it is generated according to
        definition in conf. (Default value = None)
    rx_ant :
        pattern class instance with rx antenna: if not given bla, bla, bla... (Default value = None)
    n_az_pts :
        number of points in burst, if times not explicitly given (Default value = 11)
    extra_losses :
        losses not considered elsewhere, in dB (thus not included in noise
        temperature of receiver, nor Tx power. (Default value = 0)
    savedirr :
        where to save the outputs (Default value = '')
    az_sampling :
        azimuth sampling in calculation (Default value = None)
    verbosity :
        how much output we want to have (Default value = 1)
    bistatic :
        True (default) for a bistatic system
    0.0 :

    1] :

    Tanalysis :
         (Default value = 2.5)
    plot_nesz :
         (Default value = True)
    fontsize :
         (Default value = 12)
    vmin :
         (Default value = None)
    vmax :
         (Default value = None)
    t_span_pattern :
         (Default value = 2)

    Returns
    -------

    """
    info = trtls.PrInfo(verbosity, "calc_nesz")
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
    if modename == "stripmap_wideswath":
        PRF = PRFs[swth] * conf.stripmap_wideswath.n_sat
    else:
        PRF = PRFs[swth]
    if az_sampling is None:
        az_sampling = PRF
    inc_range = incs[swth]
    time_bandwidth = tau_p[swth] * bw_p[swth]
    info.msg("Time bandwidth: %3.2f" % time_bandwidth)
    inc_v = np.linspace(incs[swth, 0], incs[swth, 1])
    la_v = geo.inc_to_look(np.radians(inc_v), conf.orbit.Horb)
    inc_ve = np.linspace(incs[swth, 0] - 2, incs[swth, 1] + 1)
    la_ve = geo.inc_to_look(np.radians(inc_ve), conf.orbit.Horb)
    try:
        txcnf = getattr(conf, txname)
        rxcnf = getattr(conf, rxname)
    except:
        raise ValueError("Either transmitter or receicer section not defined")
    ghist = GeoHistory(
        conf,
        tilt=txcnf.tilt,
        tilt_b=rxcnf.tilt,
        latitude=0,
        bistatic=bistatic,
        dau=conf.formation_primary.dau[0],
        inc_range=inc_range + np.array([-1, 1]),
        verbosity=verbosity,
    )

    info.msg("Compute Patterns", 1)
    if hasattr(txcnf, "wa_tx"):
        wa_tx = txcnf.wa_tx
    else:
        wa_tx = 1
    if tx_ant is None:
        tx_az_phase_attr = "wa_tx_phase_%i" % int(swth + 1)
        tx_el_phase_attr = "we_tx_phase_%i" % int(swth + 1)
        mcnf = getattr(conf, modename)
        if hasattr(mcnf, tx_el_phase_attr):
            we_tx = np.exp(1j * np.radians(getattr(mcnf, tx_el_phase_attr)))
            # print(np.angle(we_tx))
            info.msg(
                "calc_nesz: applying elevation weighting to tx pattern!", 1
            )
            el0 = 0  # Pointing given in phase!
        else:
            we_tx = 1
            el0 = np.degrees(np.mean(la_v)) - txcnf.tilt
        # PLD 20220114 Adding code for azimuth beam spoiling
        if hasattr(mcnf, tx_az_phase_attr):
            info.msg("Applying azimuth phase spoiling. This will probably not work with azimuth steeing modes", 1)
            wa_tx = np.exp(1j * np.radians(getattr(mcnf, tx_az_phase_attr)))
            # print(np.angle(we_tx))
            info.msg(
                "calc_nesz: applying elevation weighting to tx pattern!", 1
            )
            az0 = 0  # Pointing given in phase!


        if hasattr(txcnf, "element_pattern"):
            if type(txcnf.element_pattern) == list:
                el_ant = []
                for elcnf__ in txcnf.element_pattern:
                    elcnf_ = getattr(conf, elcnf__)
                    el_ant_ = pattern(conf.sar.f0,
                                      type_a=elcnf_.type_a,
                                      type_e=elcnf_.type_e,
                                      La=elcnf_.La,
                                      Le=elcnf_.Le,
                                      el0=(np.degrees(np.mean(la_v)) - elcnf_.tilt),
                                      Nel_a=elcnf_.Na,
                                      Nel_e=elcnf_.Ne,
                                      wa=elcnf_.wa_tx,
                                      we=elcnf_.we_tx,
                                      steering_rate=steering_rates[swth],
                                      Tanalysis=Tanalysis)
                    el_ant.append(el_ant_)
            else:
                elcnf = getattr(conf, txcnf.element_pattern)
                el_ant = pattern(conf.sar.f0,
                                 type_a=elcnf.type_a,
                                 type_e=elcnf.type_e,
                                 La=elcnf.La,
                                 Le=elcnf.Le,
                                 el0=(np.degrees(np.mean(la_v)) - elcnf.tilt),
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
        info.msg("calc_nesz: using supplied tx pattern")
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
            info.msg("Initializing element pattern")

            if type(rxcnf.element_pattern) == list:
                rel_ant = []
                for elcnf__ in rxcnf.element_pattern:
                    elcnf_ = getattr(conf, elcnf__)
                    rel_ant_ = pattern(conf.sar.f0,
                                       type_a=elcnf_.type_a,
                                       type_e=elcnf_.type_e,
                                       La=elcnf_.La,
                                       Le=elcnf_.Le,
                                       el0=rx_el0,
                                       Nel_a=elcnf_.Na,
                                       Nel_e=elcnf_.Ne,
                                       wa=elcnf_.wa_rx,
                                       we=elcnf_.we_rx,
                                       steering_rate=steering_rates[swth],
                                       Tanalysis=Tanalysis)
                    rel_ant.append(rel_ant_)
            else:
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
        print("calc_nesz: using supplied rx pattern")

    fdt0 = ghist.v_Dop_spl(la_v, 0) * 2 / wl
    fd0 = np.mean(fdt0)
    namb = 1
    fd = fd0 + np.linspace(-(namb + 0.5) * PRF, (namb + 0.5) * PRF, Npts)
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
    tv = np.arange(int(Tanalysis * az_sampling)) / az_sampling - Tanalysis / 2
    # Time in burst, this is also azimuth time of target in zero Doppler geom
    # FIXME: this is not valid for spotlight modes
    dudt, dudt_r = ghist.dudt(la_v) #  The second element in tuple is for the receiver
    # PLD 7 June 2020
    # Adjusting steering rate of receiver to accont for different du_dt
    steering_rate_r = np.mean(dudt_r) / np.mean(dudt) * steering_rate
    if t_in_bs is None:
        info.msg(
            "calc_nesz: nor burt times given, calculating them from burst length"
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
    # Set font..
    font = {"family": "Arial", "weight": "normal", "size": fontsize}
    matplotlib.rc("font", **font)

    nesz_out = np.zeros((n_az_pts, la_v.size))
    nesz_tap_out = np.zeros_like(nesz_out)

    u = ghist.t2u_spl(la_v, tv)
    v = ghist.t2v_spl(la_v, tv)
    if bistatic:
        u_b = ghist.t2u_b_spl(la_v, tv)
        v_b = ghist.t2v_b_spl(la_v, tv)
    else:
        u_b = u
        v_b = v

    # Delta Doppler to ambiguities
    v_ground = ghist.v_orb * cnst.r_earth / (cnst.r_earth + conf.orbit.Horb)

    for t_in_b_ind in range(n_az_pts):
        t_in_b = t_in_bs[t_in_b_ind]
        #  Antenna squint will be
        squint = steering_rate * (tv - t_in_b)
        if rxcnf.az_steer:
            sesame_squint = steering_rate_r * (tv - t_in_b)
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

        # Slant range and Doppler
        sr = ghist.sr_spl(la_v, tv)
        # Time at which we see Doppler ambiguities
        fdt0 = ghist.v_Dop_spl.ev(la_v.reshape((la_v.size, 1)), t_bc) * 2 / wl

        # Look angle at t0 of ambiguity; we correct for range migration
        sr0e = ghist.sr_spl.ev(la_ve.reshape((la_ve.size, 1)), t0)
        sr2look = interpol.interp1d(sr0e.flatten(), la_ve)

        # Geometry of ambiguities
        tv_rshp = tv.reshape((1, 1, tv.size))

        Dop = ghist.v_Dop_spl(la_v, tv) * 2 / wl

        s1_pat, xpat = tx_ant.pat_2D(v, u, grid=False, squint_rad=squint)
        sesame_pat, xpat = rx_ant.pat_2D(
            v_b,
            u_b,
            grid=False,
            squint_rad=sesame_squint,
            steer_rad=score_steer,
        )

        if hasattr(rxcnf, "DBF"):
            if rxcnf.DBF:
                # Simplest Doppler dependent DBF
                sesame_squint = sesame_squint.reshape(
                    (u.shape[0], 1, u.shape[1])
                )

        # Two way patterns
        tw_pat = np.abs(s1_pat * sesame_pat)
        # Amplitude of received signal for NESZ = 1 (0 dB)
        # Pulse energy
        E_p = txcnf.P_peak * time_bandwidth
        # 2-D Resolution
        A_res = (
            cnst.c
            / 2
            / bw_p[swth]
            / np.sin(np.radians(inc_v))
            * v_ground
            / proc_bw[swth]
        )
        A_1 = (
            np.sqrt(E_p)
            * tw_pat
            * wl
            / ((4 * np.pi) ** 1.5 * sr ** 2)
            * np.sqrt(A_res.reshape((inc_v.size, 1)))
            * tx_ant.g0
            * rx_ant.g0
        )

        dDop = Dop - fdt0
        mask = np.where(np.abs(dDop) < proc_bw[swth] / 2, 1, 0)

        Es = np.sum(A_1 * mask, axis=-1) ** 2
        En = np.sum(cnst.k * rxcnf.T_sys * bw_p[swth] * mask, axis=-1)
        nesz = trtls.db(En / Es * az_sampling / PRF) + extra_losses
        nesz_out[t_in_b_ind, :] = nesz

        if proc_tap[swth] != 1:
            c0 = proc_tap[swth]
            rDop = (dDop + proc_bw[swth] / 2) / proc_bw[swth]
            azwin = mask * (c0 - (1 - c0) * np.cos(2 * np.pi * rDop))
            azwin = azwin / tw_pat
            Es = np.sum(azwin * A_1 * mask, axis=-1) ** 2
            En = np.sum(
                cnst.k * rxcnf.T_sys * bw_p[swth] * mask * azwin ** 2, axis=-1
            )
            nesz_tap = trtls.db(En / Es * az_sampling / PRF) + extra_losses
            nesz_tap_out[t_in_b_ind, :] = nesz_tap

        # Plots
        title = "%s, sw%i, $\Delta t_{az}$=%4.2f s" % (
            short_name,
            swth + 1,
            t_in_b,
        )
        modeandswth = "%s_sw%i" % (short_name, swth + 1)
        modedir = os.path.join(savedirr, modeandswth)
        name = "%s_sw%i_dtaz%ims" % (short_name, swth + 1, int(1000 * t_in_b))
        plt_this_one = t_in_b_ind in [0, int(n_az_pts / 2), n_az_pts - 1]

        if plot_nesz and plt_this_one:
            plt.figure()
            # plt.plot(inc_v, trtls.db(AASR))
            if proc_tap[swth] != 1:
                plt.plot(inc_v, nesz, label="Intrinsic")
                plt.plot(
                    inc_v, nesz_tap, label=("Tap. coef. %3.2f" % proc_tap[swth])
                )
                plt.legend(loc="best")
            else:
                plt.plot(inc_v, nesz)
            plt.grid(True)
            plt.xlabel("Incident angle [deg]")
            plt.ylabel("NESZ [dB]")
            plt.title(title)
            savefile = os.path.join(modedir, name) + "_NESZ.png"
            os.makedirs(os.path.dirname(savefile), exist_ok=True)
            plt.savefig(savefile, bbox_inches="tight")

    # Output
    title = "%s, sw%i" % (short_name, swth + 1)
    modeandswth = "%s_sw%i" % (short_name, swth + 1)
    modedir = os.path.join(savedirr, modeandswth)
    name = "%s_sw%i" % (short_name, swth + 1)
    if plot_nesz:
        plt.figure()
        # plt.plot(inc_v, trtls.db(AASR))
        for t_in_b_ind in range(n_az_pts):
            t_in_b = t_in_bs[t_in_b_ind]
            if proc_tap[swth] != 1:
                plt.plot(
                    inc_v,
                    nesz_tap_out[t_in_b_ind],
                    label=("Intr. $\Delta t_{az}$=%4.2f s" % t_in_b),
                )

            else:
                plt.plot(
                    inc_v,
                    nesz,
                    label=("Intr. $\Delta t_{az}$=%4.2f s" % t_in_b),
                )
        plt.grid(True)
        plt.legend(loc="best")
        plt.xlabel("Incident angle [deg]")
        plt.ylabel("NESZ [dB]")
        plt.title(title)
        savefile = os.path.join(modedir, name) + "_NESZ.png"
        os.makedirs(os.path.dirname(savefile), exist_ok=True)
        plt.savefig(savefile, bbox_inches="tight")
        if n_az_pts > 8:
            plt.figure()
            nesz_final = np.where(
                nesz_tap_out > nesz_out, nesz_out, nesz_tap_out
            )
            corners = [
                np.min(t_in_bs),
                np.max(t_in_bs),
                inc_range[0],
                inc_range[1],
            ]
            aspect = (
                4
                * (np.max(t_in_bs) - np.min(t_in_bs))
                / (inc_range[1] - inc_range[0])
            )
            if vmax is None:
                vmax = np.nanmax(nesz_final)
            if vmin is None:
                vmin = np.nanmin(nesz_final)
            ims = plt.imshow(
                nesz_final.transpose(),
                origin="lower",
                aspect=aspect,
                interpolation="nearest",
                cmap="viridis_r",
                extent=corners,
                vmin=vmin,
                vmax=vmax,
            )
            plt.xlabel("Zero Doppler Time [s]")
            ax = plt.gca()
            ax.locator_params(axis="x", nbins=3)
            plt.ylabel("Incident angle [deg]")
            plt.title("NESZ")
            cbar = trtls.add_colorbar(ims)
            cbar.set_label("dB")
            savefile = os.path.join(modedir, name) + "_NESZ_all.png"
            plt.savefig(savefile, bbox_inches="tight")
    return NESZdata(
        la_v, inc_v, nesz_out, nesz_tap_out, t_in_bs, conf, modename, swth
    )


if __name__ == "__main__":
    pardir = "/Users/plopezdekker/Documents/WORK/SESAME/PAR"
    test_savedirr = r"/Users/plopezdekker/Documents/WORK/SESAME/PAR/RESULTS/SARPERF/SESAME_5.5_10001/200km/DBF_f"
    parfile = os.path.join(pardir, "SESAME_Nodrift_A.par")
    testconf = cfg.ConfigFile(parfile)
    print(test_savedirr)
    #  azimuth_performance(conf, 'IWS', 1, savedirr=savedirr)

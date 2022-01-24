import os
from collections import namedtuple
from tkinter import filedialog as tkFileDialog, Tk

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as interp
from mpl_toolkits import axes_grid1

import drama.geo as geosar
import drama.orbits.formation as ff
import drama.orbits.two_body as tb
import drama.orbits.sunsync_orbit as sso
import drama.utils as drtls
from drama import constants
from drama.io import cfg

"""Define a named tuple with a list of new values of formation parameters
   t is a vector of days dae, domega, phi, di and du are as in
   clohessy_wiltshire, in degree in the case of angular values
"""
FormationEvents = namedtuple(
    "FormationEvents", ["t", "dae", "daOmega", "phi", "dai", "dau", "maintain_phi"],
)


def add_colorbar(im, aspect=20, pad_fraction=0.5, **kwargs):
    """Add a vertical color bar to an image plot.

    Parameters
    ----------
    im :

    aspect :
         (Default value = 20)
    pad_fraction :
         (Default value = 0.5)
    **kwargs :


    Returns
    -------

    """
    divider = axes_grid1.make_axes_locatable(im.axes)
    width = axes_grid1.axes_size.AxesY(im.axes, aspect=1 / aspect)
    pad = axes_grid1.axes_size.Fraction(pad_fraction, width)
    current_ax = plt.gca()
    cax = divider.append_axes("right", size=width, pad=pad)
    plt.sca(current_ax)
    return im.axes.figure.colorbar(im, cax=cax, **kwargs)


def get_new_file(par_file=None):
    """Mini gui to get filename

    Parameters
    ----------
    par_file :
         (Default value = None)

    Returns
    -------

    """
    if par_file is None:
        root = Tk()
        root.withdraw()
        root.overrideredirect(True)
        root.geometry("0x0+0+0")
        root.deiconify()
        root.lift()
        root.focus_force()
        par_file = tkFileDialog.asksaveasfilename(parent=root, defaultextension=".rat")
        root.destroy()
    return par_file


def read_FormationEvents(parfile=None, test=False, load_primary=False):
    """

    Parameters
    ----------
    parfile :
         (Default value = None)
    test :
         (Default value = False)
    load_primary :
         (Default value = False)

    Returns
    -------

    """
    # Place holder
    if test:
        t = np.array([0, 32, 64, 96, 176, 177], dtype=float)
        dae = 400.0 + np.zeros(t.shape)
        phi = 90.0 + np.zeros(t.shape)
        domega0 = -1200
        # np.degrees(1200 / (constants.r_earth + 740e3))
        domega = np.zeros(t.shape, dtype=float)
        domega[:] = np.NaN
        domega[0] = domega0
        dai = np.array([-200, -300, -800, -1200, 1200, 1200])
        maintain_phi = np.ones(t.shape, dtype=bool)
        # di = np.degrees(di / (constants.r_earth + 740e3))
        du = np.zeros(t.shape)
        events = FormationEvents(t, dae, domega, phi, dai, du, maintain_phi)
    else:
        parfile_ = drtls.misc.get_par_file(parfile)
        par_data = cfg.ConfigFile(parfile_)
        if load_primary:
            formation = par_data.formation_primary
        else:
            formation = par_data.formation
        t = formation.t
        dae = formation.dae
        phi = formation.phi
        daOmega = formation.daOmega
        dai = formation.dai
        dau = formation.dau
        # Check if the parameter file specifies an argument of perigee
        # maintenance policy, if not we assume it does
        if hasattr(formation, "maintain_phi"):
            maintain_phi = formation.maintain_phi
        else:
            maintain_phi = np.ones(t.shape, dtype=bool)
        events = FormationEvents(t, dae, daOmega, phi, dai, dau, maintain_phi)
    return events


class FormationTimeline:
    """A class for a formation timeline

    Parameters
    ----------
    events :
        list of formation changing events as FormationEvents
        named tuple
    parfile :
        file from which to read this events
    dt :
        time step, in days. Defaults to 1.
    look :
        right' or 'left'
    secondary :
        False (default) or True. If True, we are in a
        PICOSAR-like configuration, with a common Tx.
    dau :
        to override dau set in parameter file

    Returns
    -------

    """

    def __init__(
        self,
        parfile=None,
        dt=1.0,
        look="right",
        secondary=False,
        load_primary=False,
        init_kz_LUT=True,
        bistatic=True,
        slope=0,
        dau=None,
    ):
        """ Initialize FormationTimeline class
        """
        self.info = drtls.PrInfo(verbosity=2, header="FormationTimeline")
        self.parfile = drtls.misc.get_par_file(parfile)
        par_data = cfg.ConfigFile(self.parfile)
        if secondary:
            # A recursive class
            self.secondary = True
            self.prim_form = FormationTimeline(
                self.parfile,
                dt=dt,
                look=look,
                secondary=False,
                load_primary=True,
                init_kz_LUT=False,
                dau=dau,
            )
            # relative delay
            # FIX-ME: ulgy hack, but we assume that primary formation is fixed
            if type(self.prim_form.du) is np.ndarray:
                du = self.prim_form.du[0]
            else:
                du = self.prim_form.du
            orb_delay = du / 360 * self.prim_form.track.Torb * 3600
            self.track_prim = geosar.SingleSwath(
                orb_type="sunsync", look=look, par_file=self.parfile
            )
            self.track = geosar.SingleSwath(
                orb_type="sunsync",
                look=look,
                par_file=self.parfile,
                companion_delay=orb_delay,
            )
        else:
            self.secondary = False
            self.track = geosar.SingleSwath(
                orb_type="sunsync", look=look, par_file=self.parfile
            )
        self.f0 = par_data.sar.f0
        self.bistatic = bistatic
        self.nRev = self.track.norb
        self.nDay = self.track.repeat_cycle
        temp = sso.get_sunsync_repeat_orbit(self.nDay, self.nRev)
        self.a, self.e, self.i = temp
        self.orb_h = self.a - constants.r_earth
        # Estimate of the velocity
        self.v_orb = 2 * np.pi * self.a / (self.track.Torb * 3600.0)
        # Now load formation itself, the function is called reload to make
        # its use more intuitive
        self.reload(
            init_kz_LUT=init_kz_LUT,
            load_primary=load_primary,
            dt=dt,
            bistatic=bistatic,
            slope=slope,
            dau=dau,
        )

    def reload(
        self,
        init_kz_LUT=True,
        load_primary=False,
        dt=1.0,
        bistatic=True,
        slope=0,
        dau=None,
    ):
        """Recalculate formation without re-calculating the orbit

        Parameters
        ----------
        init_kz_LUT :
             (Default value = True)
        load_primary :
             (Default value = False)
        dt :
             (Default value = 1.0)
        bistatic :
             (Default value = True)
        slope :
             (Default value = 0)
        dau :
             (Default value = None)

        Returns
        -------

        """
        temp = read_FormationEvents(parfile=self.parfile, load_primary=load_primary)
        self.events = temp
        # Override values
        if dau is not None:
            self.events.dau[:] = dau
        events = self.events
        # Time vector
        ntimes = np.int((events.t[-1] - events.t[0]) / dt)
        self.t = events.t[0] + np.arange(ntimes) * dt
        self.dae = np.zeros(ntimes, dtype=float)
        self.domega = np.zeros(ntimes, dtype=float)
        self.phi = np.zeros(ntimes, dtype=float)
        self.da = 0
        self.di = np.zeros(ntimes, dtype=float)
        self.du = np.zeros(ntimes, dtype=float)
        self.delta_v = np.zeros(ntimes, dtype=float)
        mean_motion = self.v_orb / self.a

        for ind in np.arange(events.t.size - 1):
            t_ind = np.where((self.t >= events.t[ind]) & (self.t < events.t[ind + 1]))
            self.dae[t_ind] = events.dae[ind]

            this_di = np.degrees(events.dai[ind] / self.a)
            self.di[t_ind] = this_di
            self.du[t_ind] = np.degrees(events.dau[ind] / self.a)
            (ddodt, dpdtr, dpdts) = ff.rel_orbit_drifts(
                self.a, self.i, events.dae[ind], e=self.e, da=self.da, di_deg=this_di,
            )

            self.info.msg("Nodal drift = %f /day" % ddodt, 1)
            self.info.msg("Relative Arg. of Perigee drift = %f /day" % dpdts, 1)
            if np.isnan(events.phi[ind]):
                phi0 = self.phi[t_ind[0][0] - 1]
            else:
                phi0 = events.phi[ind]
            if events.maintain_phi[ind]:
                self.phi[t_ind] = phi0
            else:
                self.phi[t_ind] = (
                    self.t[t_ind] - self.t[t_ind[0][0]] + dt
                ) * dpdts + phi0

            if np.isnan(events.daOmega[ind]):
                domega0 = self.domega[t_ind[0][0] - 1]
            else:
                domega0 = np.degrees(events.daOmega[ind] / self.a)
            # print(ddodt)
            self.domega[t_ind] = (
                self.t[t_ind] - self.t[t_ind[0][0]] + dt
            ) * ddodt + domega0
            # Compute delta_v cost
            # For formation change
            if ind > 0:
                # Inclination vector change
                t_t_ind = t_ind[0][0]
                ddi = np.radians(this_di - self.di[t_t_ind - 1])
                ddomega = np.radians(self.domega[t_t_ind] - self.domega[t_t_ind - 1])
                ddiv = np.array([ddi, ddomega * np.sin(np.radians(self.i))])
                t_delta_v = np.linalg.norm(ddiv) * self.v_orb
                self.delta_v[t_t_ind] = self.delta_v[t_t_ind] + t_delta_v
                # dae change
                dde = events.dae[ind] - self.dae[t_t_ind - 1]
                t_delta_v = np.abs(dde) * mean_motion / 2
                self.delta_v[t_t_ind] = self.delta_v[t_t_ind] + t_delta_v
                # phi change
                dphi = np.radians(self.phi[t_t_ind] - self.phi[t_t_ind - 1])
                dphi = np.abs(np.angle(np.exp(1j * dphi)))
                dde = np.min([events.dae[ind - 1], events.dae[ind]]) * dphi
                t_delta_v = dde * mean_motion / 2
                self.delta_v[t_t_ind] = self.delta_v[t_t_ind] + t_delta_v
            # For formation maintenance
            if events.maintain_phi[ind]:
                daily_delta_ev = events.dae[ind] * np.radians(dpdts)

                daily_delta_v = np.abs(daily_delta_ev) * mean_motion / 2
                self.delta_v[t_ind] = self.delta_v[t_ind] + daily_delta_v
            # Initialize kz LUT
        if init_kz_LUT:
            self._init_kz_LUT()
            self._init_dDoppler_LUT(bistatic=bistatic)
            self._init_df_LUT(bistatic=bistatic, slope=slope)

    def baseline3d(self, all_orbit=False):
        """

        Parameters
        ----------
        all_orbit :
             (Default value = False)

        Returns
        -------

        """
        nshp = [self.t.size, 1]
        mean_anomaly = tb.true_anomaly_to_mean(self.track.orbital_parameters.e, self.track.orbital_parameters.true_anomaly)
        arg_p_deg = np.rad2deg(self.track.orbital_parameters.arg_p)
        if all_orbit:
            rel_orbs = ff.clohessy_wiltshire(
                self.a,
                self.i,
                self.dae.reshape(nshp),
                self.domega.reshape(nshp),
                mean_anomaly,
                phi_deg=self.phi.reshape(nshp),
                di_deg=self.di.reshape(nshp),
                du_deg=self.du.reshape(nshp),
                u0_deg=arg_p_deg,
            )
            return rel_orbs
        else:
            mean_anomaly_asc = mean_anomaly[self.track.asc_idx[0] : self.track.asc_idx[1]]
            mean_anomaly_desc = mean_anomaly[
                self.track.desc_idx[0] : self.track.desc_idx[1]
            ]
            arg_p_deg_asc = arg_p_deg[self.track.asc_idx[0] : self.track.asc_idx[1]]
            arg_p_deg_desc = arg_p_deg[self.track.desc_idx[0] : self.track.desc_idx[1]]
            rel_orbs_a = ff.clohessy_wiltshire(
                self.a,
                self.i,
                self.dae.reshape(nshp),
                self.domega.reshape(nshp),
                mean_anomaly_asc,
                phi_deg=self.phi.reshape(nshp),
                di_deg=self.di.reshape(nshp),
                du_deg=self.du.reshape(nshp),
                u0_deg=arg_p_deg_asc,
            )

            rel_orbs_d = ff.clohessy_wiltshire(
                self.a,
                self.i,
                self.dae.reshape(nshp),
                self.domega.reshape(nshp),
                mean_anomaly_desc,
                phi_deg=self.phi.reshape(nshp),
                di_deg=self.di.reshape(nshp),
                du_deg=self.du.reshape(nshp),
                u0_deg=arg_p_deg_desc,
            )
            return (rel_orbs_d, rel_orbs_a)

    def xbaseline(self, dr_r, dr_n, dr_t, incident=None, LoS=None, right_looking=True):
        """Calculate the effective cross-track baseline of two
        receivers. The receivers are separated in the radial direction
        by dr_r, in the tangential direction by dr_t, and in the
        perpendicular direction by dr_n.

        Parameters
        ----------
        dr_r : ndarray
            radial component of separation

        dr_n : ndarray
            normal component of separation

        dr_t : ndarray
            tangential component of separation

        incident : ndarray
            incident angle (Default value = None)

        LoS : ndarray
            line of sight vector (Default value = None)

        right_looking : bool
            True means right-looking antenna, false is
            left-looking (Default value = True)

        Returns
        -------
        ndarray
            the effective cross-track baseline
        """
        if not (LoS is None):
            # In this case we have to consider the LoS and coregistration
            # We calculate the 3-D baseline after coregistration
            # B_t = dr_n * LoS[:,0] / LoS[:,2]
            dr_t_coregistered = dr_n * (LoS[..., 0] / LoS[..., 2]).reshape(
                (LoS.shape[0], 1)
            )
            B3d = np.zeros((dr_t_coregistered.shape) + (3,))
            B3d[..., 1] = np.resize(dr_r, dr_t_coregistered.shape)
            B3d[..., 2] = np.resize(dr_n, dr_t_coregistered.shape)
            B3d[..., 0] = dr_t_coregistered
            # Now the resulting baseline has the same squint as the LoS.
            # so that the two SAR images actually interfere
            # (implicit coregistration). The cross-track baseline is the
            # magnitude of the baseline times the sine of the angle between it
            # and the LoS
            Bx = np.linalg.norm(
                np.cross(B3d, LoS.reshape((LoS.shape[0], 1, 3))), axis=2
            )
        else:
            # do not take into account the LoS, only the incident
            # angle
            look_angle = geosar.inc_to_look(np.radians(incident), self.orb_h)
            if not right_looking:
                look_angle = -look_angle
            Bx = dr_n * np.cos(look_angle) + dr_r * np.sin(look_angle)
        return Bx

    def h_amb(self, dr_r, dr_n, dr_t, incident, LoS=None, right_looking=True):
        """Calculate the height of ambiguity of two receivers. The
        receivers are separated in the radial direction by dr_r, in
        the tangential direction by dr_t, and in the perpendicular
        direction by dr_n.

        Parameters
        ----------
        dr_r : ndarray
            radial component of separation

        dr_n : ndarray
            normal component of separation

        dr_t : ndarray
            tangential component of separation

        incident : ndarray
            incident angle (Default value = None)

        LoS : ndarray
            line of sight vector (Default value = None)

        right_looking : bool
            True means right-looking antenna, false is
            left-looking (Default value = True)

        Returns
        -------
        ndarray
            the height of ambiguity as result of the cross-track baseline
        """
        Bp = self.xbaseline(dr_r, dr_n, dr_t, incident, LoS, right_looking)
        inc_range = geosar.inc_to_sr(np.radians(incident), self.orb_h)
        lambda0 = constants.c / self.f0
        h_amb = inc_range * np.sin(np.radians(incident)) * lambda0 / Bp
        return h_amb

    def ati_baseline(self, dr_r, dr_n, dr_t, LoS=None):
        """Calculate effective ATI baseline of two receivers. This is
            trivial for the unsquinted case where the baseline is the
            physcial separation, but slightly trickier if a LoS is
            given.  The receivers are separated in the radial
            direction by dr_r, in the tangential direction by dr_t,
            and in the perpendicular direction by dr_n.

        Parameters
        ----------
        dr_r : ndarray
            radial component of separation

        dr_n : ndarray
            normal component of separation

        dr_t : ndarray
            tangential component of separation

        LoS : ndarray
            line of sight vector (Default value = None)

        right_looking : bool
            True means right-looking antenna, false is
            left-looking (Default value = True)

        Returns
        -------
        ndarray
            the effective along-track baseline
        """

        if not (LoS is None):
            B_t_coreg = dr_n * (LoS[..., 0] / LoS[..., 2]).reshape((LoS.shape[0], 1))
            B_ATI = dr_t - B_t_coreg
        else:
            B_ATI = dr_t
        return B_ATI

    def Dopplers_shift_1w(
        self,
        dr_r,
        dr_n,
        dr_t,
        incident,
        LoS=None,
        R=None,
        right_looking=True,
        slope=0,
        include_vertical=False,
    ):
        """

        Parameters
        ----------
        dr_r :

        dr_n :

        dr_t :

        incident :

        LoS :
             (Default value = None)
        R :
             (Default value = None)
        right_looking :
             (Default value = True)
        slope :
             (Default value = 0)
        include_vertical :
             (Default value = False)

        Returns
        -------

        """

        lambda0 = constants.c / self.f0
        if not (LoS is None):
            LoSf = LoS * R.reshape((R.shape) + (1,))
            B3d = np.zeros((dr_r.shape) + (3,))
            # A vertical baseline results in a differntial Doppler, but
            # this must be actually understood as a range spectral shift
            # so it doesn't really reduce the common Doppler
            if include_vertical:
                B3d[:, :, 1] = dr_r
            B3d[:, :, 2] = dr_n  # = dr_n * LoS[:,2] / LoS[:,2]
            # B_t = dr_n * LoS[:,0] / LoS[:,2]
            B3d[:, :, 0] = dr_t
            LoSf2 = LoSf.reshape((LoS.shape[0], 1, 3)) - B3d
            LoS2 = LoSf2 / np.linalg.norm(LoSf2, axis=2).reshape(
                (LoSf2.shape[0], LoSf2.shape[1], 1)
            )
            Dop1 = (LoS[:, 0] * self.v_orb / lambda0).reshape((dr_r.shape[0], 1))
            Dop2 = LoS2[:, :, 0] * self.v_orb / lambda0
            return Dop2 - Dop1
        else:
            R = geosar.inc_to_sr(np.radians(incident), self.orb_h)
            dDop = self.v_orb / lambda0 * dr_t / R

        return dDop

    def spectral_shift(
        self,
        dr_r,
        dr_n,
        dr_t,
        incident,
        LoS=None,
        right_looking=True,
        slope=0,
        bistatic=True,
    ):
        """

        Parameters
        ----------
        dr_r :

        dr_n :

        dr_t :

        incident :

        LoS :
             (Default value = None)
        right_looking :
             (Default value = True)
        slope :
             (Default value = 0)
        bistatic :
             (Default value = True)

        Returns
        -------

        """
        Bp = self.xbaseline(dr_r, dr_n, dr_t, incident, LoS, right_looking)
        R = geosar.inc_to_sr(np.radians(incident), self.orb_h)
        lambda0 = constants.c / self.f0
        if bistatic:
            is_monostatic = 0
        else:
            is_monostatic = 1
        Delta_f = (constants.c * Bp * (1 + is_monostatic)) / (
            2 * lambda0 * R * np.tan(np.radians(incident) - np.arctan(slope))
        )
        return Delta_f

    def __get_interpolated_geo(self, inc, ascending):
        incident_angles = self.track.incident[0, :].flatten()
        inc_ind = (np.abs(incident_angles - np.radians(inc))).argmin()
        inc = np.degrees(incident_angles[inc_ind])
        latitudes = self.track.lats[:, inc_ind].flatten()

        if self.secondary:
            # Equivalent LoS as mean between tx and rx
            LoSslv = self.track.LoS_satcoord[:, inc_ind, :]
            LoSmst = self.track_prim.LoS_satcoord[:, inc_ind, :]
            Rmst = self.track_prim.R[:, inc_ind]
            Rslv = self.track.R[:, inc_ind]
        else:
            LoS_mst = None
            LoS_slv = None
            R_mst = None
            R_slv = None
        rorb_d, rorb_a = self.baseline3d()
        # Now we interpolate baselines onto a regular latitude grid
        latout = np.linspace(-90, 90, 181)
        if ascending:
            lat2dr_r_a = interp.interp1d(
                latitudes[self.track.asc_idx[0] : self.track.asc_idx[1]],
                rorb_a.dr_r,
                bounds_error=False,
            )
            dr_r = lat2dr_r_a(latout).transpose()

            lat2dr_n_a = interp.interp1d(
                latitudes[self.track.asc_idx[0] : self.track.asc_idx[1]],
                rorb_a.dr_n,
                bounds_error=False,
            )
            dr_n = lat2dr_n_a(latout).transpose()

            lat2dr_t_a = interp.interp1d(
                latitudes[self.track.asc_idx[0] : self.track.asc_idx[1]],
                rorb_a.dr_t,
                bounds_error=False,
            )
            dr_t = lat2dr_t_a(latout).transpose()
            if self.secondary:
                LoSmsti = interp.interp1d(
                    latitudes[self.track.asc_idx[0] : self.track.asc_idx[1]],
                    LoSmst[self.track.asc_idx[0] : self.track.asc_idx[1], :],
                    bounds_error=False,
                    axis=0,
                )
                LoS_mst = LoSmsti(latout)
                LoSslvi = interp.interp1d(
                    latitudes[self.track.asc_idx[0] : self.track.asc_idx[1]],
                    LoSslv[self.track.asc_idx[0] : self.track.asc_idx[1], :],
                    bounds_error=False,
                    axis=0,
                )
                LoS_slv = LoSslvi(latout)
                Rmsti = interp.interp1d(
                    latitudes[self.track.asc_idx[0] : self.track.asc_idx[1]],
                    Rmst[self.track.asc_idx[0] : self.track.asc_idx[1]],
                    bounds_error=False,
                    axis=0,
                )
                R_mst = Rmsti(latout)
                Rslvi = interp.interp1d(
                    latitudes[self.track.asc_idx[0] : self.track.asc_idx[1]],
                    Rslv[self.track.asc_idx[0] : self.track.asc_idx[1]],
                    bounds_error=False,
                    axis=0,
                )
                R_slv = Rslvi(latout)
        else:
            lat2dr_r_d = interp.interp1d(
                latitudes[self.track.desc_idx[0] : self.track.desc_idx[1]],
                rorb_d.dr_r,
                bounds_error=False,
            )
            dr_r = lat2dr_r_d(latout).transpose()

            lat2dr_n_d = interp.interp1d(
                latitudes[self.track.desc_idx[0] : self.track.desc_idx[1]],
                rorb_d.dr_n,
                bounds_error=False,
            )
            dr_n = lat2dr_n_d(latout).transpose()

            lat2dr_t_d = interp.interp1d(
                latitudes[self.track.desc_idx[0] : self.track.desc_idx[1]],
                rorb_d.dr_t,
                bounds_error=False,
            )
            dr_t = lat2dr_t_d(latout).transpose()
            if self.secondary:
                LoSmsti = interp.interp1d(
                    latitudes[self.track.desc_idx[0] : self.track.desc_idx[1]],
                    LoSmst[self.track.desc_idx[0] : self.track.desc_idx[1], :],
                    bounds_error=False,
                    axis=0,
                )
                LoS_mst = LoSmsti(latout)
                LoSslvi = interp.interp1d(
                    latitudes[self.track.desc_idx[0] : self.track.desc_idx[1]],
                    LoSslv[self.track.desc_idx[0] : self.track.desc_idx[1], :],
                    bounds_error=False,
                    axis=0,
                )
                LoS_slv = LoSslvi(latout)
                Rmsti = interp.interp1d(
                    latitudes[self.track.desc_idx[0] : self.track.desc_idx[1]],
                    Rmst[self.track.desc_idx[0] : self.track.desc_idx[1]],
                    bounds_error=False,
                    axis=0,
                )
                R_mst = Rmsti(latout)
                Rslvi = interp.interp1d(
                    latitudes[self.track.desc_idx[0] : self.track.desc_idx[1]],
                    Rslv[self.track.desc_idx[0] : self.track.desc_idx[1]],
                    bounds_error=False,
                    axis=0,
                )
                R_slv = Rslvi(latout)
        return (dr_r, dr_n, dr_t, inc, LoS_mst, LoS_slv, R_mst, R_slv)

    def get_baseline3d(self, inc, ascending=True, slope=0, bistatic=True):
        """

        Parameters
        ----------
        inc :

        ascending :
             (Default value = True)
        slope :
             (Default value = 0)
        bistatic :
             (Default value = True)

        Returns
        -------

        """
        # Delta_f=c*Bn/(2*lambda*R*tan(sarsens.theta-atan(slope)))/(1+is_monostatic)
        incident_angles = self.track.incident[0, :].flatten()
        inc_ind = (np.abs(incident_angles - np.radians(inc))).argmin()
        inc = np.degrees(incident_angles[inc_ind])
        latitudes = self.track.lats[:, inc_ind].flatten()
        northing = self.track.northing[:, inc_ind].flatten()
        rorb_d, rorb_a = self.baseline3d()
        # Now we interpolate baselines onto a regular latitude grid
        latout = np.linspace(-90, 90, 181)
        if ascending:
            lat2dr_r_a = interp.interp1d(
                latitudes[self.track.asc_idx[0] : self.track.asc_idx[1]],
                rorb_a.dr_r,
                bounds_error=False,
            )
            dr_r = lat2dr_r_a(latout).transpose()

            lat2dr_n_a = interp.interp1d(
                latitudes[self.track.asc_idx[0] : self.track.asc_idx[1]],
                rorb_a.dr_n,
                bounds_error=False,
            )
            dr_n = lat2dr_n_a(latout).transpose()

            lat2dr_t_a = interp.interp1d(
                latitudes[self.track.asc_idx[0] : self.track.asc_idx[1]],
                rorb_a.dr_t,
                bounds_error=False,
            )
            dr_t = lat2dr_t_a(latout).transpose()
            lat2north_a = interp.interp1d(
                latitudes[self.track.asc_idx[0] : self.track.asc_idx[1]],
                northing[self.track.asc_idx[0] : self.track.asc_idx[1]],
                bounds_error=False,
            )
            northing_out = lat2north_a(latout).transpose()
        else:
            lat2dr_r_d = interp.interp1d(
                latitudes[self.track.desc_idx[0] : self.track.desc_idx[1]],
                rorb_d.dr_r,
                bounds_error=False,
            )
            dr_r = lat2dr_r_d(latout).transpose()

            lat2dr_n_d = interp.interp1d(
                latitudes[self.track.desc_idx[0] : self.track.desc_idx[1]],
                rorb_d.dr_n,
                bounds_error=False,
            )
            dr_n = lat2dr_n_d(latout).transpose()

            lat2dr_t_d = interp.interp1d(
                latitudes[self.track.desc_idx[0] : self.track.desc_idx[1]],
                rorb_d.dr_t,
                bounds_error=False,
            )
            dr_t = lat2dr_t_d(latout).transpose()
            lat2north_d = interp.interp1d(
                latitudes[self.track.desc_idx[0] : self.track.desc_idx[1]],
                northing[self.track.desc_idx[0] : self.track.desc_idx[1]],
                bounds_error=False,
            )
            northing_out = lat2north_d(latout).transpose()

        return (dr_r, dr_n, dr_t, inc, northing_out)

    def __get_df(self, inc, ascending=True, slope=0, bistatic=True):
        # Delta_f=c*Bn/(2*lambda*R*tan(sarsens.theta-atan(slope)))/(1+is_monostatic)
        (
            dr_r,
            dr_n,
            dr_t,
            inc,
            LoS_mst,
            LoS_slv,
            R_mst,
            R_slv,
        ) = self.__get_interpolated_geo(inc, ascending)
        Deltaf = self.spectral_shift(
            dr_r, dr_n, dr_t, inc, slope=slope, bistatic=bistatic
        )
        return Deltaf

    def _init_df_LUT(self, bistatic=True, slope=0):
        """This assumes that the incicident angle LUT was already
            initialized

        Parameters
        ----------
        bistatic :
             (Default value = True)
        slope :
             (Default value = 0)

        Returns
        -------

        """
        print("Initializing spectral shift LUT")
        # Ascending
        self._asc_df_LUT = np.zeros(self._asc_kz_LUT.shape, dtype=np.float)
        for i_inc in range(0, self._inc_LUT.size):
            self._asc_df_LUT[i_inc] = self.__get_df(
                self._inc_LUT[i_inc], ascending=True, bistatic=bistatic, slope=slope,
            )
        # Descending
        self._desc_df_LUT = np.zeros(self._asc_kz_LUT.shape, dtype=np.float)
        for i_inc in range(0, self._inc_LUT.size):
            self._desc_df_LUT[i_inc] = self.__get_df(
                self._inc_LUT[i_inc], ascending=False, bistatic=bistatic, slope=slope,
            )

    def get_spectral_shift(self, inc_deg, lat=None, day=None, ascending=True):
        """Returns the Spectral shift shift

        Parameters
        ----------
        inc :
            incident angle in degree
        lat :
            latitude of interest, may be any array. None returns
            all latitudes for a fixed incident angle (Default value = None)
        day :
            day of interest, may be any array. None returns
            all latitudes for a fixed incident angle (Default value = None)
        inc_deg :

        ascending :
             (Default value = True)

        Returns
        -------

        """
        inc_ind = np.round((inc_deg - self._inc_LUT[0]) / self._inc_res)
        if type(inc_ind) == np.ndarray:
            inc_ind = np.where(inc_ind > 0, inc_ind, 0)
            inc_ind = (
                np.where(inc_ind < self._inc_LUT.size, inc_ind, self._inc_LUT.size - 1,)
            ).astype(np.int)
            try:
                lat_ind = np.round(np.array(lat) + 90).astype(np.int)
                day_ind = np.round(np.array(day)).astype(np.int)
            except:
                print("Somehow wrong dimensions to input params")
                raise
            if ascending:
                return self._asc_df_LUT[inc_ind, lat_ind, day_ind]
            else:
                return self._desc_df_LUT[inc_ind, lat_ind, day_ind]
        else:
            if inc_ind < 0:
                inc_ind = 0
            elif inc_ind > (self._inc_LUT.size - 1):
                inc_ind = self._inc_LUT.size - 1
            if ascending:
                return self._asc_df_LUT[inc_ind]
            else:
                return self._desc_df_LUT[inc_ind]

    def __get_dDop(self, inc, ascending=True, bistatic=True, include_vertical=False):
        (
            dr_r,
            dr_n,
            dr_t,
            inc,
            LoS_mst,
            LoS_slv,
            R_mst,
            R_slv,
        ) = self.__get_interpolated_geo(inc, ascending)
        dDop = self.Dopplers_shift_1w(
            dr_r, dr_n, dr_t, inc, LoS_slv, R_slv, include_vertical=include_vertical,
        )
        if bistatic is False:
            dDop = 2 * dDop
        return dDop

    def _init_dDoppler_LUT(self, bistatic=True, include_vertical=False):
        """This assumes that the incicident angle LUT was already
            initialized

        Parameters
        ----------
        bistatic :
             (Default value = True)
        include_vertical :
             (Default value = False)

        Returns
        -------

        """
        print("Initializing dDoppler LUT")
        # Ascending
        self._asc_dDop_LUT = np.zeros(self._asc_kz_LUT.shape, dtype=np.float)
        for i_inc in range(0, self._inc_LUT.size):
            self._asc_dDop_LUT[i_inc] = self.__get_dDop(
                self._inc_LUT[i_inc],
                ascending=True,
                bistatic=bistatic,
                include_vertical=include_vertical,
            )
        # Descending
        self._desc_dDop_LUT = np.zeros(self._asc_kz_LUT.shape, dtype=np.float)
        for i_inc in range(0, self._inc_LUT.size):
            self._desc_dDop_LUT[i_inc] = self.__get_dDop(
                self._inc_LUT[i_inc],
                ascending=False,
                bistatic=bistatic,
                include_vertical=include_vertical,
            )

    def get_Doppler_shift(self, inc_deg, lat=None, day=None, ascending=True):
        """Returns the Doppler shift

        Parameters
        ----------
        inc :
            incident angle in degree
        lat :
            latitude of interest, may be any array. None returns
            all latitudes for a fixed incident angle (Default value = None)
        day :
            day of interest, may be any array. None returns
            all latitudes for a fixed incident angle (Default value = None)
        inc_deg :

        ascending :
             (Default value = True)

        Returns
        -------

        """
        inc_ind = np.around((inc_deg - self._inc_LUT[0]) / self._inc_res).astype(int)
        if type(inc_ind) == np.ndarray:
            inc_ind = np.where(inc_ind > 0, inc_ind, 0)
            inc_ind = (
                np.where(inc_ind < self._inc_LUT.size, inc_ind, self._inc_LUT.size - 1,)
            ).astype(np.int)
            try:
                lat_ind = np.round(np.array(lat) + 90).astype(np.int)
                day_ind = np.round(np.array(day)).astype(np.int)
            except:
                print("Somehow wrong dimensions to input params")
                raise
            if ascending:
                return self._asc_dDop_LUT[inc_ind, lat_ind, day_ind]
            else:
                return self._desc_dDop_LUT[inc_ind, lat_ind, day_ind]
        else:
            if inc_ind < 0:
                inc_ind = 0
            elif inc_ind > (self._inc_LUT.size - 1):
                inc_ind = self._inc_LUT.size - 1
            if ascending:
                return self._asc_dDop_LUT[inc_ind]
            else:
                return self._desc_dDop_LUT[inc_ind]

    def __get_kz(self, inc, ascending=True):
        """ Returns kz
            :param inc: incident angle in degree
        """
        (
            dr_r,
            dr_n,
            dr_t,
            inc,
            LoS_mst,
            LoS_slv,
            R_mst,
            R_slv,
        ) = self.__get_interpolated_geo(inc, ascending)
        # Equivalent geom approximation
        if LoS_mst is None:
            LoS = None
        else:
            LoS = (LoS_mst + LoS_slv) / 2
        kz = 2 * np.pi / self.h_amb(dr_r, dr_n, dr_t, inc, LoS)
        return kz

    def _init_kz_LUT(self, inc_res_deg=1):
        """

        Parameters
        ----------
        inc_res_deg :
             (Default value = 1)

        Returns
        -------

        """
        print("Initializing kz LUT")
        self._inc_res = inc_res_deg
        incident_angles = self.track.incident[0, :].flatten()
        self._inc_LUT = np.arange(
            np.degrees(incident_angles.min()),
            np.degrees(incident_angles.max()),
            inc_res_deg,
        )
        # Ascending
        kz0 = self.__get_kz(self._inc_LUT[0], ascending=True)
        self._asc_kz_LUT = np.zeros(self._inc_LUT.shape + kz0.shape, dtype=np.float)
        self._asc_kz_LUT[0] = kz0
        for i_inc in range(1, self._inc_LUT.size):
            self._asc_kz_LUT[i_inc] = self.__get_kz(
                self._inc_LUT[i_inc], ascending=True
            )
        # Descending
        self._desc_kz_LUT = np.zeros(self._inc_LUT.shape + kz0.shape, dtype=np.float)
        for i_inc in range(0, self._inc_LUT.size):
            self._desc_kz_LUT[i_inc] = self.__get_kz(
                self._inc_LUT[i_inc], ascending=False
            )

    def get_kz(self, inc_deg, lat=None, day=None, ascending=True):
        """Returns kz

        Parameters
        ----------
        inc :
            incident angle in degree
        lat :
            latitude of interest, may be any array. None returns
            all latitudes for a fixed incident angle (Default value = None)
        day :
            day of interest, may be any array. None returns
            all latitudes for a fixed incident angle (Default value = None)
        inc_deg :

        ascending :
             (Default value = True)

        Returns
        -------

        """
        inc_ind = np.round((inc_deg - self._inc_LUT[0]) / self._inc_res).astype(int)
        if type(inc_ind) == np.ndarray:
            inc_ind = np.where(inc_ind > 0, inc_ind, 0)
            inc_ind = (
                np.where(inc_ind < self._inc_LUT.size, inc_ind, self._inc_LUT.size - 1,)
            ).astype(np.int)
            try:
                lat_ind = np.round(np.array(lat) + 90).astype(np.int)
                day_ind = np.round(np.array(day)).astype(np.int)
            except:
                print("Somehow wrong dimensions to input params")
                raise
            if ascending:
                return self._asc_kz_LUT[inc_ind, lat_ind, day_ind]
            else:
                return self._desc_kz_LUT[inc_ind, lat_ind, day_ind]
        else:
            if inc_ind < 0:
                inc_ind = 0
            elif inc_ind > (self._inc_LUT.size - 1):
                inc_ind = self._inc_LUT.size - 1
            if ascending:
                return self._asc_kz_LUT[inc_ind]
            else:
                return self._desc_kz_LUT[inc_ind]

    def acquisition_mask(
        self,
        inc_deg,
        lat=None,
        day=None,
        ascending=True,
        kz_range=None,
        h_amb_range=None,
        dDoppler_max=None,
        df_max=None,
        slope=0,
    ):
        """Returns  mask provided a number of criteria.

            The method behaves like get_kz, etc. The optional criteria are

        Parameters
        ----------
        kz_range :
            range of valid k_z (Default value = None)
        h_amb_range :
            range of valid heights of ambiguity. This does
            the same as kz_range, so it would be not very
            smart to use both criteria together (Default value = None)
        dDoppler_max :
            maximum relative Doppler shift allowed (Default value = None)
        df_max :
            maximum spectral shift allowed (Default value = None)
        slope :
            passed through to get_spectral_shift (Default value = 0)
        inc_deg :

        lat :
             (Default value = None)
        day :
             (Default value = None)
        ascending :
             (Default value = True)

        Returns
        -------

        """
        kz = np.abs(self.get_kz(inc_deg, lat, day, ascending=ascending))
        mask = np.ones_like(kz, dtype="bool")
        if not (kz_range is None):
            kz = np.where(np.isnan(kz), np.inf, kz)
            mask = np.logical_and(mask, kz > kz_range[0])
            mask = np.logical_and(mask, kz < kz_range[1])
        elif not (h_amb_range is None):
            h_amb = 2 * np.pi / np.where(np.isnan(kz), 1e-10, kz)
            mask = np.logical_and(mask, h_amb > h_amb_range[0])
            mask = np.logical_and(mask, h_amb < h_amb_range[1])
        if not (dDoppler_max is None):
            dDop = np.abs(
                self.get_Doppler_shift(inc_deg, lat, day, ascending=ascending)
            )
            dDop = np.where(np.isnan(dDop), np.inf, dDop)
            mask = np.logical_and(mask, dDop < dDoppler_max)
        if not (df_max is None):
            df = np.abs(
                self.get_spectral_shift(
                    inc_deg, lat, day, ascending=ascending, slope=slope
                )
            )
            df = np.where(np.isnan(df), np.inf, df)
            mask = np.logical_and(mask, df < df_max)
        return mask

    def view_baseline(
        self,
        what="perp",
        inc="mid",
        ascending=True,
        abs=True,
        vmax=None,
        vmin=None,
        just_plot=False,
        lat=0,
        rat_export=False,
        savefile=None,
        fontsize=12,
        fontweight="normal",
        cmap="viridis_r",
        contour=False,
        clevels=None,
        contour_colors="k",
        titleprefix=None,
        titlesufix=None,
        new_figure=True,
    ):
        """Visualize baseline evolution.

        Parameters
        ----------
        what :
            what to be plotted, can be 'ver', 'hor' or
            ('at' or 'tan') for vertical, cross-track
            horizontal, or along-track baseline respectively;
            'perp' for perpendicular baseline; 'h_amb'; 'Doppler'
            for the relative Doppler shift; ('kz' or 'k_z') for
            the kappa_z = 2*pi/h_amb (Default value = 'perp')
        inc :
            incident angle. Can be 'near', 'mid', 'far' or a value
            in degree (Default value = 'mid')
        new_figure :
            True if method should create a new figure, otherwise
            it will put the results in the active one. Useful for
            subplots, for example (Default value = True)
        ascending :
             (Default value = True)
        abs :
             (Default value = True)
        vmax :
             (Default value = None)
        vmin :
             (Default value = None)
        just_plot :
             (Default value = False)
        lat :
             (Default value = 0)
        rat_export :
             (Default value = False)
        savefile :
             (Default value = None)
        fontsize :
             (Default value = 12)
        fontweight :
             (Default value = 'normal')
        cmap :
             (Default value = 'viridis_r')
        contour :
             (Default value = False)
        clevels :
             (Default value = None)
        contour_colors :
             (Default value = 'k')
        titleprefix :
             (Default value = None)
        titlesufix :
             (Default value = None)

        Returns
        -------

        """
        incident_angles = self.track.incident[0, :].flatten()
        if type(inc) is str:
            if inc == "near":
                inc_ind = 0
            elif inc == "far":
                inc_ind = -1
            else:
                inc_ind = int(self.track.incident.shape[1] / 2)
        else:
            inc_ind = (np.abs(incident_angles - np.radians(inc))).argmin()

        inc = np.degrees(incident_angles[inc_ind])
        (
            dr_r,
            dr_n,
            dr_t,
            inc,
            LoS_mst,
            LoS_slv,
            R_mst,
            R_slv,
        ) = self.__get_interpolated_geo(inc, ascending)

        # Equivalent geom approximation
        if LoS_mst is None:
            LoS = None
        else:
            LoS = (LoS_mst + LoS_slv) / 2

        corners = [self.t[0], self.t[-1], -90, 90]
        cbarlabel = ""
        if what == "hor":
            im = dr_n
            title = "Horizontal Baseline"
            cbarlabel = "[m]"
            cntfmt = "%4f"
        elif what == "ver":
            im = dr_r
            title = "Vertical Baseline"
            cbarlabel = "[m]"
            cntfmt = "%4f"
        elif (what == "at") or (what == "tan"):
            im = self.ati_baseline(dr_r, dr_n, dr_t, LoS)
            title = "Along-track Baseline"
            cbarlabel = "[m]"
            cntfmt = "%4f"
        elif (what == "perp") or (what == "cross"):
            im = self.xbaseline(dr_r, dr_n, dr_t, inc, LoS)
            title = "Perpendicular Baseline"
            cbarlabel = "[m]"
            cntfmt = "%4f"
        elif what == "h_amb":
            im = self.h_amb(dr_r, dr_n, dr_t, inc, LoS)
            title = "Height of ambiguity"
            cbarlabel = "[m]"
            cntfmt = "%4.1f"
        elif what == "Doppler":
            im = self.Dopplers_shift_1w(dr_r, dr_n, dr_t, inc, LoS_slv, R_slv)
            title = "Doppler shift (1-way)"
            cbarlabel = "[Hz]"
            cntfmt = "%4.1f"
        elif (what == "df") or (what == "spectral_shift"):
            im = (
                self.spectral_shift(
                    dr_r, dr_n, dr_t, inc, LoS_slv, R_slv, bistatic=self.bistatic,
                )
                / 1e6
            )
            title = "Spectral shift"
            cbarlabel = "[MHz]"
            cntfmt = "%4.2f"
        elif (what == "kz") or (what == "k_z"):
            im = 2 * np.pi / self.h_amb(dr_r, dr_n, dr_t, inc, LoS)
            title = "$\kappa_z$"
            cbarlabel = "[rad/m]"
            cntfmt = "%4.2f"
        if ascending:
            title = "Asc. " + title
        else:
            title = "Desc. " + title
        if titleprefix is not None:
            title = titleprefix + title
        if titlesufix is not None:
            title = title + titlesufix
        if abs:
            im = np.abs(im)
        if new_figure:
            plt.figure()
        if just_plot:
            matplotlib.rcParams.update(
                {"font.size": fontsize, "font.weight": fontweight}
            )
            # plt.figure()
            _lat = np.array([lat]).flatten()
            for tlat in _lat:
                line = im[np.int(tlat + 90), :]
                plt.plot(self.t, line, label=("lat = %f" % tlat))
            pmin = -np.abs(line).max() if vmin is None else vmin
            pmax = np.abs(line).max() if vmax is None else vmax
            plt.ylim([pmin, pmax])
            plt.xlabel("Time [days]")
            plt.ylabel(title + " " + cbarlabel)
            plt.legend()
        elif contour:
            matplotlib.rcParams.update(
                {"font.size": fontsize, "font.weight": fontweight}
            )
            # plt.figure()
            if vmin is None:
                vmin = np.nanmin(im)
            if vmax is None:
                vmax = np.nanmax(im)

            ims = plt.imshow(
                im, origin="lower", extent=corners, vmax=vmax, vmin=vmin, cmap=cmap,
            )
            if clevels is None:
                levels = np.linspace(vmin, vmax, 11)[1:-1]
            else:
                levels = np.array(clevels)
            cnt = plt.contour(
                im,
                levels,
                origin="lower",
                extent=corners,
                colors=contour_colors,
                linestyles="dashed",
            )
            plt.clabel(cnt, levels, inline=1, fontsize=fontsize - 4, fmt=cntfmt)
            cbar = add_colorbar(ims)
            cbar.set_label(cbarlabel)
            # cb1 = plt.colorbar(ims, fraction=0.046, pad=0.04)
            plt.xlabel("Time [days]", fontsize=fontsize)
            plt.ylabel("Latitude [deg]", fontsize=fontsize)
            plt.xticks(fontsize=fontsize)
            plt.yticks(fontsize=fontsize)
            plt.title(title, fontsize=fontsize)
        else:
            matplotlib.rcParams.update(
                {"font.size": fontsize, "font.weight": fontweight}
            )
            # plt.figure()
            ims = plt.imshow(
                im, origin="lower", extent=corners, vmax=vmax, vmin=vmin, cmap=cmap,
            )

            cbar = add_colorbar(ims)
            cbar.set_label(cbarlabel)
            # cb1 = plt.colorbar(ims, fraction=0.046, pad=0.04)
            plt.xlabel("Time [days]", fontsize=18)
            plt.ylabel("Latitude [deg]", fontsize=18)
            plt.xticks(fontsize=fontsize)
            plt.yticks(fontsize=fontsize)
            plt.title(title, fontsize=fontsize)
        if rat_export:
            filename = get_new_file()
            rat.srat(filename, im)

        if not (savefile is None):
            if new_figure:
                os.makedirs(os.path.dirname(savefile), exist_ok=True)
                plt.savefig(savefile, bbox_inches="tight")
            else:
                self.info.msg(
                    "Ignoring savefile since I don't know who ons the figure", 1
                )

        return im

    def view_delta_v(
        self, savefile=None, fontsize=14, fontweight="bold", new_figure=True
    ):
        """

        Parameters
        ----------
        savefile :
             (Default value = None)
        fontsize :
             (Default value = 14)
        fontweight :
             (Default value = 'bold')
        new_figure :
             (Default value = True)

        Returns
        -------

        """

        matplotlib.rcParams.update({"font.size": fontsize, "font.weight": fontweight})
        if new_figure:
            plt.figure()
        plt.plot(self.t, np.cumsum(self.delta_v))
        plt.xlim((0, self.t[-1]))
        plt.xlabel("Time [days]")
        plt.ylabel(r"$\Delta v$ [m/s]")
        if (not (savefile is None)) and new_figure:
            os.makedirs(os.path.dirname(savefile), exist_ok=True)
            plt.savefig(savefile, bbox_inches="tight")

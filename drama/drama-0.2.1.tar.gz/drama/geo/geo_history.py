"""
geo_history includes code that computes the history of a target.
author: Paco Lopez-Dekker
"""

import copy
import time

import numpy as np
import scipy.interpolate as interpol

import drama.constants as cnst
import drama.utils as drtls
from drama.orbits import SingleOrbit
from drama.geo import geometry as geom


class GeoHistory(object):
    """A class to estimate the geom migration

    Parameters
    ----------
    conf : drama.io.cfg.ConfigFile
        ConfigFile object. It should have an orbit section
    tilt : float
        tilt angle of reference antenna plane (deg)
    inc_range : float
        self explainatory, in degree
    latitude : float
        approximate latitude of interest (0 by default)
    squint_a : float
        antenna squint, defaults to zero [deg]
    orb_type : float
        orbital type
    look : float
        left' or 'right'
    ext_source : float
        if True, use external data source
    bistatic : float
        compute bistatic geom
    dae : float
        vertical baseline due to eccentricity difference,
        assuming an argument of perigee of 90 degree
    dao : float
        horizontal baseline at equator due to ascening node
        offset
    di_deg : float
        inclination offset (provides baseline at high
        latitudes)
    dau : float
        along-track offset assuming that both spacecraft
        are on the same orbital plane (for dao = 0). This
        results in an additional cross-track baseline due
        to Earth's rotation
    tilt_b : float
        tilt angle of reference antenna plane for
        second spacecraft in the bistatic case (deg)
    longitude : float
        if specified the history will be computed for a
        point at this longitude (latitude above and
        altitude below).
    altitude : float
        the history will be computed for points at this
        altitude (latitude and latitude above)
    """

    def __init__(
        self,
        conf,
        tilt=0,
        inc_range=[15, 60],
        latitude=0,
        ascending=True,
        squint_a=0,
        orb_type="sunsync",
        look="right",
        ext_source=False,
        silent=False,
        bistatic=False,
        dae=0,
        dao=0,
        di_deg=0,
        dau=0,
        tilt_b=0,
        inc_swth=None,
        n_la_pts=200,
        verbosity=1,
        t_analysis=40,
        longitude=None,
        altitude=0,
    ):
        """ Inititalize GeoHistory
        """
        t_start = time.time()
        self.verbosity = verbosity
        self.info = drtls.PrInfo(verbosity, "GeoHistory")
        self.conf = copy.copy(conf)
        self.conf.orbit.timestep = 1.0
        if ext_source:
            print("External source option not implemented")
        self.orbit = SingleOrbit(orb_type=orb_type, conftuple=self.conf)

        # FIXME hard coded
        npts = int(2 * np.ceil((t_analysis * self.conf.orbit.timestep) / 2))
        t = (np.arange(npts) - npts / 2) * self.conf.orbit.timestep
        hnpts = int(npts / 2)
        # Set coordinates of the simulated strip either based on orbit latitude
        # (in case longitude = None) or based on specific point coordinates
        if longitude is None:
            orb_lat = np.arctan2(
                self.orbit.r_ecef[:, 2],
                np.linalg.norm(self.orbit.r_ecef[:, 0:2], axis=1),
            )
            if ascending:
                valind = np.where(self.orbit.v_ecef[:, 2] > 0)
            else:
                valind = np.where(self.orbit.v_ecef[:, 2] < 0)
            ref_ind = valind[0][
                np.argmin(np.abs(np.degrees(orb_lat[valind]) - latitude))
            ]

            self.r_ecef = self.orbit.r_ecef[ref_ind - hnpts : ref_ind + hnpts]
            self.v_ecef = self.orbit.v_ecef[ref_ind - hnpts : ref_ind + hnpts]
            self.v_orb = np.linalg.norm(self.orbit.v_ecef[ref_ind])

        else:
            (r_ecef_zd, v_ecef_zd, t_zd, la_zd, look_dir,) = geom.geo_to_zero_doppler(
                latitude, longitude, altitude, self.orbit
            )
            # Interpolate orbit centered on user-specified location
            self.r_ecef, self.v_ecef = self.orbit.interp_orbit(t_zd + t)
            self.v_orb = self.v_ecef[hnpts]

        self.bistatic = bistatic
        if bistatic:
            if dau != 0:
                v_orb_m = np.mean(np.linalg.norm(self.v_ecef, axis=1))
                orb_delay = -1 * dau / v_orb_m
            else:
                orb_delay = 0
            (a, e, i) = self.orbit.aei
            aei_b = (a, e + dae / a, i + di_deg)
            self.orbit_b = SingleOrbit(
                orb_type=orb_type,
                conftuple=self.conf,
                companion_delay=orb_delay,
                aei=aei_b,
            )

            if longitude is None:
                self.r_ecef_b = self.orbit_b.r_ecef[ref_ind - hnpts : ref_ind + hnpts]
                self.v_ecef_b = self.orbit_b.v_ecef[ref_ind - hnpts : ref_ind + hnpts]
                self.v_orb_b = np.linalg.norm(self.orbit_b.v_ecef[ref_ind])
            else:
                self.r_ecef_b, self.v_ecef_b = self.orbit_b.interp_orbit(t_zd + t)
                self.v_orb_b = self.v_ecef_b[hnpts]

        ref_ind = int(npts / 2)
        # FIXME: all other formation components ignored for now
        t_orb = time.time()
        if not silent:
            self.info.msg("Time for orbit computation: %f" % (t_orb - t_start), 1)
        self.timestep = conf.orbit.timestep
        self.inc_near = np.deg2rad(inc_range[0])
        self.inc_far = np.deg2rad(inc_range[1])
        self.la_near = geom.inc_to_look(self.inc_near, self.orbit.Horb)
        self.la_far = geom.inc_to_look(self.inc_far, self.orbit.Horb)
        # get ground range from incident angles
        self.grg_near = geom.inc_to_gr(self.inc_near, self.orbit.Horb)
        self.grg_far = geom.inc_to_gr(self.inc_far, self.orbit.Horb)
        self.tilt = np.radians(tilt)
        # look angle vector [deg]
        # start at zero to include transmitter nadir
        la_vector = np.linspace(0, self.la_far, n_la_pts)
        if inc_swth is None:
            la_vector_swth = np.array([self.la_near, self.la_far])
        else:
            la_vector_swth = np.array(
                [
                    geom.inc_to_look(np.radians(inc_swth[0]), self.orbit.Horb),
                    geom.inc_to_look(np.radians(inc_swth[1]), self.orbit.Horb),
                ]
            )

        #        print(orb_lat.size)
        #        print(ref_ind)
        #        print(orb_lat[ref_ind])
        right_looking = True if look == "right" else False
        LoS = geom.create_LoS(
            self.r_ecef,
            self.v_ecef,
            la_vector,
            right_looking=right_looking,
            squint_a=squint_a,
        )
        self.icps = geom.pt_get_intersection_ellipsoid(self.r_ecef, LoS)
        LoS_swth = geom.create_LoS(
            self.r_ecef,
            self.v_ecef,
            la_vector_swth,
            right_looking=right_looking,
            squint_a=squint_a,
        )
        self.icps_swth = geom.pt_get_intersection_ellipsoid(self.r_ecef, LoS_swth)
        self.icp = self.icps[hnpts]
        # Now do monostatic geom
        # Range vector
        R = self.icp.reshape((1,) + self.icp.shape) - self.r_ecef.reshape((npts, 1, 3))
        # Slant range vector
        sr = np.linalg.norm(R, axis=2)

        # Squint angle (u), in antenna plane (i.e. Doppler associated)
        R_norm = R / sr.reshape(sr.shape + (1,))
        # Reference look angle
        LoS_tilt = geom.create_LoS(
            self.r_ecef, self.v_ecef, np.array([np.radians(tilt)])
        )
        # Calculate LoS velocity component to target
        # just inner product of velocity vector with R norm
        self.v_Dop = np.einsum("ki,kji->kj", self.v_ecef, R_norm)
        # Calculate velocity and positions versor
        self.v_ecef_norm = np.linalg.norm(self.v_ecef, axis=1)
        v_ecef_ver = self.v_ecef / self.v_ecef_norm.reshape((npts, 1))
        r_ecef_ver = self.r_ecef / np.linalg.norm(self.r_ecef, axis=1).reshape(
            (npts, 1)
        )
        u = np.sum(R_norm * v_ecef_ver.reshape((npts, 1, 3)), axis=2)
        self.t2u_spl = interpol.RectBivariateSpline(la_vector, t, np.transpose(u))
        # Look angle (v)
        AntNad = np.cross(LoS_tilt.reshape((npts, 3)), v_ecef_ver)
        v = np.sum(R_norm * AntNad.reshape((npts, 1, 3)), axis=2)
        self.t2v_spl = interpol.RectBivariateSpline(la_vector, t, np.transpose(v))
        self.t = t
        self.u = u
        t_u2v = time.time()
        self._la_vector = la_vector
        self._u2t = []
        for i_la in range(la_vector.size):
            self._u2t.append(interpol.interp1d(u[:, i_la], t, kind="cubic"))
        if bistatic:
            # repeat for bistatic geom
            R_b = self.icp.reshape((1,) + self.icp.shape) - self.r_ecef_b.reshape(
                (npts, 1, 3)
            )
            # Slant range vector
            sr_b = np.linalg.norm(R_b, axis=2)
            sr = (sr_b + sr) / 2

            # Squint angle (u), in antenna plane (i.e. Doppler associated)
            R_b_norm = R_b / sr_b.reshape(sr.shape + (1,))
            # Reference look angle
            LoS_b_tilt = geom.create_LoS(
                self.r_ecef_b, self.v_ecef_b, np.array([np.radians(tilt)])
            )
            # Calculate LoS velocity component to target
            # just inner product of velocity vector with R norm
            self.v_Dop_b = np.einsum("ki,kji->kj", self.v_ecef_b, R_b_norm)
            # Replace the reference Doppler velocity with the average onee
            self.v_Dop = (self.v_Dop + self.v_Dop_b) / 2
            # Calculate velocity and positions versor
            self.v_ecef_b_norm = np.linalg.norm(self.v_ecef_b, axis=1)
            v_ecef_b_ver = self.v_ecef_b / self.v_ecef_b_norm.reshape((npts, 1))
            r_ecef_b_ver = self.r_ecef_b / np.linalg.norm(
                self.r_ecef_b, axis=1
            ).reshape((npts, 1))
            # FIXME: check antenna pointing
            self.bist_rots = geom.companion_pointing(
                self.icps_swth, self.r_ecef_b, self.v_ecef_b, tilt_b
            )
            R_b_ant = np.einsum("kij,kmi->kmj", self.bist_rots.ant_xyz, R_b_norm)
            self.R_b_ant = R_b_ant
            self.u_b = R_b_ant[:, :, 1]
            self.v_b = R_b_ant[:, :, 2]
            self.t2u_b_spl = interpol.RectBivariateSpline(
                la_vector, t, np.transpose(self.u_b)
            )
            # Look angle (v)
            # AntNad_b = np.cross(LoS_b_tilt.reshape((npts, 3)), v_ecef_b_ver)
            # v_b = np.sum(R_b_norm * AntNad_b.reshape((npts, 1, 3)), axis=2)
            self.t2v_b_spl = interpol.RectBivariateSpline(
                la_vector, t, np.transpose(self.v_b)
            )

        # Slant range interpolator
        self.sr_spl = interpol.RectBivariateSpline(la_vector, t, np.transpose(sr))
        # Slant range interpolator
        self.v_Dop_spl = interpol.RectBivariateSpline(
            la_vector, t, np.transpose(self.v_Dop)
        )
        self._v_Dop2t = []
        for i_la in range(la_vector.size):
            #  self.info.msg(self.info.msg("Min/Max Radial velocity: (%f, %f)" %
            #  (self.v_Dop[:, i_la].min(), self.v_Dop[:, i_la].max()), 1))
            self._v_Dop2t.append(
                interpol.interp1d(self.v_Dop[:, i_la], t, kind="cubic")
            )
        endt = time.time()
        if not silent:
            self.info.msg("u2t intepolator generator: %f" % (endt - t_u2v), 1)
            self.info.msg("Total initialization time: %f" % (endt - t_start), 2)

    def u2t(self, look_rad, u, ant_ref=False):
        """Returns t for a fiven u

        Parameters
        ----------
        look_rad : float or Sequence
            look angle in radians
        u : float

        ant_ref : bool
             (Default value = False)

        Returns
        -------
        float or numpy.ndarray
        """
        look = np.array(look_rad)
        if ant_ref:
            look = look + self.tilt
        if look.size == 1:
            look_ind = np.argmin(np.abs(look - self._la_vector))
            t = self._u2t[look_ind](u)
            # if self.bistatic:
            # u_b = self.t2u_spl.ev(look, t)
            # v_b = self.t2v_spl.ev(look, t)
        elif len(look.shape) == 1:
            t = np.zeros((look.size, u.shape[-1]))
            # if self.bistatic:
            # u_b = np.zeros_like(u)
            # v_b = np.zeros_like(u)
            for i_look in range(look.size):
                look_ind = np.argmin(np.abs(look[i_look] - self._la_vector))
                if u.ndim == 1:
                    u_ = u
                else:
                    u_ = u[i_look]
                tt = self._u2t[look_ind](u_)
                t[i_look, :] = tt
        else:
            raise Exception("Wrong dimensions!")
        return t

    def dudt(self, look_rad, t=0, dt=1):
        """Time derivative of u averaged over certain interval

        Parameters
        ----------
        look_rad : float or numpy.ndarray
            look angles [rad]
        t :
            time at which it is calculated, defaults to 0 [s]
        dt :
            time interval consideredm defaults to 1 [s]

        Returns
        -------

        """
        if type(t) == np.ndarray:
            du_dt = (
                self.t2u_spl.ev(look_rad, t + dt) - self.t2u_spl.ev(look_rad, t)
            ) / dt
            if self.bistatic:
                du_b_dt = (
                    self.t2u_b_spl.ev(look_rad, t + dt) - self.t2u_b_spl.ev(look_rad, t)
                ) / dt
            else:
                du_b_dt = du_dt  # Just replicate the monostati one
        else:
            du_dt = (self.t2u_spl(look_rad, t + dt) - self.t2u_spl(look_rad, t)) / dt
            if self.bistatic:
                du_b_dt = (
                    self.t2u_b_spl(look_rad, t + dt) - self.t2u_b_spl(look_rad, t)
                ) / dt
            else:
                du_b_dt = du_dt
        return du_dt, du_b_dt

    def Doppler2tuv(self, look_rad, f_D, f0, ant_ref=False):
        """Returns a tuple of time (t) azimuth (u) and elevation (v) angles
            as function of look angle and Doppler frequency. The first two
            parameters are passed (and treated like) the x and y inputs to a
            RectBivariateSpline interpolator. In a bistatic geom the
            tuple looks like (t, u, v, u_b, v_b)

        Parameters
        ----------
        look_rad :
            Zero Doppler look angle or np.array of angles
        f_D :
            Array of Doppler frequencies
        f0 :
            center frequency
        ant_ref :
            if True, then look_rad is w.r.t. antenna boresight (Default value = False)

        Returns
        -------

        """
        # f_D = 2 * v / lambda * sin(uD)
        look = np.array(look_rad)
        if ant_ref:
            look = look + self.tilt
        wl = cnst.c / f0
        vD = np.array(f_D) * wl / 2
        if look.size == 1:
            look_ind = np.argmin(np.abs(look - self._la_vector))
            t = self._v_Dop2t[look_ind](vD)
            u = self.t2u_spl.ev(look, t)
            v = self.t2v_spl.ev(look, t)
            if self.bistatic:
                u_b = self.t2u_spl.ev(look, t)
                v_b = self.t2v_spl.ev(look, t)
        elif len(look.shape) == 1:
            v = np.zeros((look.size, vD.shape[-1]))
            u = np.zeros_like(v)
            t = np.zeros_like(v)
            if self.bistatic:
                u_b = np.zeros_like(u)
                v_b = np.zeros_like(u)
            _dla = self._la_vector[1] - self._la_vector[0]
            look_ind = np.round((look - self._la_vector[0]) / _dla).astype(int)
            look_ind = np.where(look_ind < 0, 0, look_ind)
            look_ind = np.where(
                look_ind < self._la_vector.size, look_ind, self._la_vector.size - 1,
            )
            look_ind_u, look_ind_indices = np.unique(look_ind, return_inverse=True)

            # for i_look in range(look.size):
            for ind in range(look_ind_u.size):
                # look_ind = np.argmin(np.abs(look[i_look] - self._la_vector))
                look_ind = look_ind_u[ind]
                i_look = np.where(look_ind_indices == ind)[0]
                if vD.ndim == 1:
                    vD_ = vD
                    tt = (self._v_Dop2t[look_ind](vD_)).reshape((1, vD_.size))
                else:
                    vD_ = vD[i_look]
                    tt = self._v_Dop2t[look_ind](vD_)
                t[i_look, :] = tt
                look_i_look = look[i_look].reshape((i_look.size, 1))
                u[i_look, :] = self.t2u_spl.ev(look_i_look, tt)
                v[i_look, :] = self.t2v_spl.ev(look_i_look, tt)
                if self.bistatic:
                    u_b[i_look, :] = self.t2u_b_spl.ev(look_i_look, tt)
                    v_b[i_look, :] = self.t2v_b_spl.ev(look_i_look, tt)

        else:
            raise Exception("Wrong dimensions!")
        if self.bistatic:
            return t, u, v, u_b, v_b
        else:
            # In the monostatic geom I just fill the tuple with Nones
            return t, u, v, u, v

    def Doppler2sr(self, look_rad, f_D, f0, ant_ref=False):
        """Returns a tuple of time (t) and slant range (sr)
            as function of look angle and Doppler frequency. The first two
            parameters are passed (and treated like) the x and y inputs to a
            RectBivariateSpline interpolator. In a bistatic geom the
            tuple looks like (t, u, v, u_b, v_b)

        Parameters
        ----------
        look_rad :
            Zero Doppler look angle or np.array of angles
        f_D :
            Array of Doppler frequencies
        f0 :
            center frequency
        ant_ref :
            if True, then look_rad is w.r.t. antenna boresight (Default value = False)

        Returns
        -------

        """
        # f_D = 2 * v / lambda * sin(uD)
        look = np.array(look_rad)
        if ant_ref:
            look = look + self.tilt
        wl = cnst.c / f0
        vD = np.array(f_D) * wl / 2
        dla = self._la_vector[1] - self._la_vector[0]
        la0 = self._la_vector[0]
        if look.size == 1:
            # look_ind_0 = np.argmin(np.abs(look - self._la_vector))
            look_ind = (look - la0) / dla
            look_ind_0 = np.floor(look_ind).astype(np.int)
            if look_ind_0 < 0:
                look_ind_0 = 0
                l0w = 1
            else:
                l0w = 1 - look_ind + look_ind_0
            look_ind_1 = look_ind_0 + 1
            if look_ind_1 >= self._la_vector.size:
                look_ind_1 = self._la_vector.size - 1
                l0w = 1
                look_ind_0 = look_ind_1
            l1w = 1 - l0w

            t = (
                self._v_Dop2t[look_ind_0](vD) * l0w
                + self._v_Dop2t[look_ind_1](vD) * l1w
            )
            sr = self.sr_spl(look, t)
        elif len(look.shape) == 1:
            sr = np.zeros((look.size, vD.shape[-1]))
            t = np.zeros_like(sr)
            _dla = self._la_vector[1] - self._la_vector[0]
            look_ind = (look - self._la_vector[0]) / _dla
            # look_ind = np.round((look - self._la_vector[0]) / _dla).astype(int)
            look_ind_0 = np.floor(look_ind).astype(np.int)
            bad_ind0 = np.where(look_ind < 0)
            look_ind_0 = np.where(look_ind < 0, 0, look_ind_0)
            look_ind_1 = np.where(look_ind < 0, 0, look_ind_0 + 1)
            wl0 = 1 - look_ind + look_ind_0
            bad_ind1 = np.where(look_ind_1 >= self._la_vector.size)
            look_ind_0[bad_ind1] = self._la_vector.size - 1
            look_ind_1[bad_ind1] = self._la_vector.size - 1
            wl1 = 1 - wl0
            wl1[bad_ind1] = 1
            wl0[bad_ind1] = 0
            wl1[bad_ind0] = 1
            wl0[bad_ind0] = 0

            # look_ind_u, look_ind_indices = np.unique(look_ind,
            #                                         return_inverse=True)

            # for i_look in range(look.size):
            # for ind in range(look_ind_u.size):
            #     # look_ind = np.argmin(np.abs(look[i_look] - self._la_vector))
            #     look_ind = look_ind_u[ind]
            #     i_look = np.where(look_ind_indices == ind)[0]
            #     if vD.ndim == 1:
            #         vD_ = vD
            #         tt = (self._v_Dop2t[look_ind](vD_)).reshape((1, vD_.size))
            #     else:
            #         vD_ = vD[i_look]
            #         tt = self._v_Dop2t[look_ind](vD_)
            #     t[i_look, :] = tt
            #     look_i_look = look[i_look].reshape((i_look.size, 1))
            #     sr[i_look, :] = self.sr_spl.ev(look_i_look, tt)

            for ind in range(look_ind_0.size):
                if vD.ndim == 1:
                    vD_ = vD
                    self.info.msg(
                        "%i Min/Max Doppler vel : (%f, %f)"
                        % (ind, vD_.min(), vD_.max()),
                        1,
                    )
                    tt = wl0[ind] * (self._v_Dop2t[look_ind_0[ind]](vD_)).reshape(
                        (1, vD_.size)
                    ) + wl1[ind] * (self._v_Dop2t[look_ind_1[ind]](vD_)).reshape(
                        (1, vD_.size)
                    )
                else:
                    vD_ = vD[ind]
                    tt = wl0[ind] * self._v_Dop2t[look_ind_0[ind]](vD_) + wl1[
                        ind
                    ] * self._v_Dop2t[look_ind_1[ind]](vD_)
                t[ind, :] = tt
                # look_i_look = look[look_ind_0[ind]].reshape((i_look.size, 1))
                sr[ind, :] = self.sr_spl.ev(look[ind], tt)
        else:
            raise Exception("Wrong dimensions!")

        return t, sr

    def init_srDop2t(self, dop_range, sr_range, f0, dsr=1e2, ddop=10, silent=False):
        """This creates an interpolator to go from range-doppler to azimuth and nominal look angle

        Parameters
        ----------
        dop_range :
            param sr_range:
        dsr :
            param ddop: (Default value = 1e2)
        sr_range :

        f0 :

        ddop :
             (Default value = 10)
        silent :
             (Default value = False)

        Returns
        -------

        """
        t_start = time.time()
        ndops = np.int(np.ceil((dop_range[1] - dop_range[0]) / ddop))
        nsrs = np.int(np.ceil((sr_range[1] - sr_range[0]) / dsr))
        dops = np.linspace(dop_range[0], dop_range[1], num=ndops)

        td, sr = self.Doppler2sr(self._la_vector, dops, f0)
        self.sr_maxmin = sr.min(axis=0).max()
        srs = np.linspace(np.max([sr_range[0], self.sr_maxmin]), sr_range[1], num=nsrs)
        # print(sr.min())
        tas = np.zeros((ndops, nsrs))
        las = np.zeros_like(tas)
        for i_dop in range(ndops):
            auxint = interpol.interp1d(sr[:, i_dop], self._la_vector, kind="cubic")
            if srs.min() < sr[:, i_dop].min():
                self.info.msg("min of srs is smaller than min of sr")
            if srs.max() > sr[:, i_dop].max():
                self.info.msg("max of srs is larger than max of sr")
            las[i_dop, :] = auxint(srs)
            auxint = interpol.interp1d(sr[:, i_dop], td[:, i_dop], kind="cubic")
            tas[i_dop, :] = auxint(srs)
        # FIXME: this will fail
        sr_min_vs_dop = sr.min(axis=0)
        self.dop_to_sr_min = interpol.interp1d(dops, sr_min_vs_dop)
        self.sr_min = srs.min()
        self.srdop2la_spl = interpol.RectBivariateSpline(dops, srs, las)
        self.srdop2ta_spl = interpol.RectBivariateSpline(dops, srs, tas)
        endt = time.time()
        if not silent:
            self.info.msg(
                "srDop2t init computation time time: %f" % (endt - t_start), 1
            )

    def srDop2t(self, dop, sr_in, f0, silent=False):
        """Calculates the azimuth time given Doppler and slant range

        Parameters
        ----------
        dop : numpy.ndarray
            an array of Dopplers
        sr_in : float or numpy.ndarray
            slant range value, or array (same size as dop) or 2-D array, with the first
            dimension of the same size as dop
        f0 : float
            centre frequency
        silent : bool
             (Default value = False)

        Returns
        -------
        Tuple(numpy.ndarray, numpy.ndarray)
        """
        t_start = time.time()
        td, sr = self.Doppler2sr(self._la_vector, dop, f0)
        if type(sr_in) is np.ndarray:
            sri = sr_in
        else:
            sri = np.array([sr_in])
        if sri.size == 1:
            td_dim2 = 1
            td_out = np.empty(dop.size)
            la_out = np.empty_like(td_out)
            for ind in range(dop.size):
                auxint = interpol.interp1d(sr[:, ind], td[:, ind], kind="cubic")
                td_out[ind] = auxint(sri[0])
                auxint = interpol.interp1d(sr[:, ind], self._la_vector, kind="cubic")
                la_out[ind] = auxint(sri[0])
        elif len(sri.shape) == 1:
            td_dim2 = 1
            td_out = np.empty(dop.size)
            la_out = np.empty_like(td_out)
            for ind in range(dop.size):
                auxint = interpol.interp1d(sr[:, ind], td[:, ind], kind="cubic")
                td_out[ind] = auxint(sri[ind])
                auxint = interpol.interp1d(sr[:, ind], self._la_vector, kind="cubic")
                la_out[ind] = auxint(sri[ind])
        else:
            td_dim2 = sri.shape[1]
            td_out = np.empty((dop.size, td_dim2))
            la_out = np.empty_like(td_out)
            for ind in range(dop.size):
                auxint = interpol.interp1d(sr[:, ind], td[:, ind], kind="cubic")
                td_out[ind] = auxint(sri[ind])
                auxint = interpol.interp1d(sr[:, ind], self._la_vector, kind="cubic")
                la_out[ind] = auxint(sri[ind])

        endt = time.time()
        if not silent:
            print("srDop2t computation time time: %f" % (endt - t_start))
        return la_out, td_out

import copy
import numpy as np
import scipy.interpolate as interpolate
import drama.utils as drtls
from drama import constants as const
from drama.geo import geometry as geom
from drama.geo.swath_geo import SingleSwath
from drama.io import cfg as cfg
from drama.orbits import sunsync_orbit as sso


class BistaticRadarGeometry(object):
    """This class calculates useful geometric relations.

    Parameters
    ----------
    orbit_height :
        orbit height above surface
    r_planet :
        radious of planet, default's to Earth's
    gm_planet :
        mass of planet, default's to Earths
    degrees :
        if set, everything is in degrees, defaults to False.

    Returns
    -------

    """
    def __init__(self, par_file, companion_delay=None):
        self.swth_t = SingleSwath(par_file=par_file)
        if companion_delay is None:
            self.swth_r = self.swth_t
        else:
            self.swth_r = SingleSwath(par_file=par_file,
                                      companion_delay=companion_delay)

        self.los_t_ecef = self.swth_t.xyz - self.swth_t.r_ecef[:, np.newaxis, :]
        self.los_r_ecef = self.swth_t.xyz - self.swth_r.r_ecef[:, np.newaxis, :]
        # transform to local coordinate System
        self.r_t = np.zeros_like(self.los_t_ecef)
        self.r_r = np.zeros_like(self.los_t_ecef)
        self.v_t = np.zeros_like(self.los_t_ecef)
        self.v_r = np.zeros_like(self.los_t_ecef)
        self.r_t[..., 0] = np.sum(self.los_t_ecef * self.swth_t.local_x, axis=-1)
        self.r_t[..., 1] = np.sum(self.los_t_ecef * self.swth_t.local_y, axis=-1)
        self.r_t[..., 2] = np.sum(self.los_t_ecef * self.swth_t.local_z, axis=-1)
        self.r_r[..., 0] = np.sum(self.los_r_ecef * self.swth_t.local_x, axis=-1)
        self.r_r[..., 1] = np.sum(self.los_r_ecef * self.swth_t.local_y, axis=-1)
        self.r_r[..., 2] = np.sum(self.los_r_ecef * self.swth_t.local_z, axis=-1)
        ashp = (self.r_t.shape[0], 1, self.r_t.shape[2])
        self.v_t[..., 0] = np.sum(self.swth_t.v_ecef.reshape(ashp) * self.swth_t.local_x, axis=-1)
        self.v_t[..., 1] = np.sum(self.swth_t.v_ecef.reshape(ashp) * self.swth_t.local_y, axis=-1)
        self.v_t[..., 2] = np.sum(self.swth_t.v_ecef.reshape(ashp) * self.swth_t.local_z, axis=-1)
        self.v_r[..., 0] = np.sum(self.swth_r.v_ecef.reshape(ashp) * self.swth_t.local_x, axis=-1)
        self.v_r[..., 1] = np.sum(self.swth_r.v_ecef.reshape(ashp) * self.swth_t.local_y, axis=-1)
        self.v_r[..., 2] = np.sum(self.swth_r.v_ecef.reshape(ashp) * self.swth_t.local_z, axis=-1)
        # Magnitude (norm) of r_t and r_r
        r_n_t = np.linalg.norm(self.r_t, axis=2)
        r_n_r = np.linalg.norm(self.r_r, axis=2)
        self.r_v_t = self.r_t / r_n_t[:,:, np.newaxis]
        self.r_v_r = self.r_r / r_n_r[:,:, np.newaxis]
        # Time derivative of bistatic range
        v_t_rad = np.sum(self.v_t * self.r_v_t, axis=2)
        v_r_rad = np.sum(self.v_r * self.r_v_r, axis=2)
        self.dr_b = -v_t_rad - v_r_rad
        # Second derivative
        self.ddr_b = ((np.sum(self.v_t**2, axis=2) - v_t_rad**2) / r_n_t
                      + (np.sum(self.v_r**2, axis=2) - v_r_rad**2) / r_n_r)
        # Surface gradient of r_b
        self.sgrad_r_b = self.r_v_t[:, :, 0:2] + self.r_v_r[:, :, 0:2]
        # Surface gradient of dr_b (time-derivative of r_b)
        self.sgrad_dr_b = ((v_t_rad[:,:, np.newaxis] * self.r_v_t[:, :, 0:2] - self.v_t[:, :, 0:2]) / r_n_t[:,:, np.newaxis]
                           + (v_r_rad[:,:, np.newaxis] * self.r_v_r[:, :, 0:2] - self.v_r[:, :, 0:2]) / r_n_r[:,:, np.newaxis])
        # Initialize latitude
        self.lat = 0

    @property
    def lat(self):
        """ """
        return self.__lat

    @lat.setter
    def lat(self, lat):
        """

        Parameters
        ----------
        lat :

        Returns
        -------

        """
        self.__lat = lat
        mid_range = int(self.swth_t.lats.shape[1] / 2)
        lats = self.swth_t.lats
        asclats = lats[self.swth_t.asc_idx[0] : self.swth_t.asc_idx[1], mid_range]
        dsclats = lats[self.swth_t.asc_idx[1] :, mid_range]
        self.__asc_latind = np.argmin(np.abs(asclats - lat)) + self.swth_t.asc_idx[0]
        self.__dsc_latind = np.argmin(np.abs(dsclats - lat)) + self.swth_t.asc_idx[1]
        self.swth_t.lat = lat
        self.swth_r.lat = lat
        self.__asc_incm2dot_r_b = interpolate.interp1d(
            self.swth_t.master_inc[self.__asc_latind],
            self.dr_b[self.__asc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__asc_incm2ddot_r_b = interpolate.interp1d(
            self.swth_t.master_inc[self.__asc_latind],
            self.ddr_b[self.__asc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__asc_incm2sgrad_r_b_x = interpolate.interp1d(
            self.swth_t.master_inc[self.__asc_latind],
            self.sgrad_r_b[self.__asc_latind, :, 0],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__asc_incm2sgrad_r_b_y = interpolate.interp1d(
            self.swth_t.master_inc[self.__asc_latind],
            self.sgrad_r_b[self.__asc_latind, :, 1],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__asc_incm2sgrad_dr_b_x = interpolate.interp1d(
            self.swth_t.master_inc[self.__asc_latind],
            self.sgrad_dr_b[self.__asc_latind, :, 0],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__asc_incm2sgrad_dr_b_y = interpolate.interp1d(
            self.swth_t.master_inc[self.__asc_latind],
            self.sgrad_dr_b[self.__asc_latind, :, 1],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        # Descending
        self.__dsc_incm2dot_r_b = interpolate.interp1d(
            self.swth_t.master_inc[self.__dsc_latind],
            self.dr_b[self.__dsc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__dsc_incm2ddot_r_b = interpolate.interp1d(
            self.swth_t.master_inc[self.__dsc_latind],
            self.ddr_b[self.__dsc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__dsc_incm2sgrad_r_b_x = interpolate.interp1d(
            self.swth_t.master_inc[self.__dsc_latind],
            self.sgrad_r_b[self.__dsc_latind, :, 0],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__dsc_incm2sgrad_r_b_y = interpolate.interp1d(
            self.swth_t.master_inc[self.__dsc_latind],
            self.sgrad_r_b[self.__dsc_latind, :, 1],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__dsc_incm2sgrad_dr_b_x = interpolate.interp1d(
            self.swth_t.master_inc[self.__dsc_latind],
            self.sgrad_dr_b[self.__dsc_latind, :, 0],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__dsc_incm2sgrad_dr_b_y = interpolate.interp1d(
            self.swth_t.master_inc[self.__dsc_latind],
            self.sgrad_dr_b[self.__dsc_latind, :, 1],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )

    def inc2bistatic_angle_az(self, inc_m, ascending=True):
        """ Returns the azimuth projected bistatic angle

        Parameters
        ----------
        inc :

        ascending :
             (Default value = True)

        Returns
        -------

        """
        cmp_nrth = self.swth_r.inc2northing(np.radians(inc_m), ascending=ascending)
        ref_nrth = self.swth_t.inc2northing(np.radians(inc_m), ascending=ascending)
        return np.degrees(cmp_nrth - ref_nrth)

    def inc2dot_r_b(self, inc, ascending=True):
        """

        Parameters
        ----------
        inc :

        ascending :
             (Default value = True)

        Returns
        -------

        """
        if ascending:
            return self.__asc_incm2dot_r_b(inc)
        else:
            return self.__dsc_incm2dot_r_b(inc)

    def inc2ddot_r_b(self, inc, ascending=True):
        """

        Parameters
        ----------
        inc :

        ascending :
             (Default value = True)

        Returns
        -------

        """
        if ascending:
            return self.__asc_incm2ddot_r_b(inc)
        else:
            return self.__dsc_incm2ddot_r_b(inc)

    def inc2sgrad_r_b(self, inc, ascending=True):
        """

        Parameters
        ----------
        inc :

        ascending :
             (Default value = True)

        Returns
        -------

        """
        if ascending:
            grad_x = self.__asc_incm2sgrad_r_b_x(inc)
            grad_y = self.__asc_incm2sgrad_r_b_y(inc)
            return np.stack([grad_x, grad_y], axis=-1)
        else:
            grad_x = self.__dsc_incm2sgrad_r_b_x(inc)
            grad_y = self.__dsc_incm2sgrad_r_b_y(inc)
            return np.stack([grad_x, grad_y], axis=-1)

    def inc2sgrad_dot_r_b(self, inc, ascending=True):
        """

        Parameters
        ----------
        inc :

        ascending :
             (Default value = True)

        Returns
        -------

        """
        if ascending:
            grad_x = self.__asc_incm2sgrad_dr_b_x(inc)
            grad_y = self.__asc_incm2sgrad_dr_b_y(inc)
            return np.stack([grad_x, grad_y], axis=-1)
        else:
            grad_x = self.__dsc_incm2sgrad_dr_b_x(inc)
            grad_y = self.__dsc_incm2sgrad_dr_b_y(inc)
            return np.stack([grad_x, grad_y], axis=-1)

    def train_off_track_displacement(self, inc, dotr_s=1, ascending=True):
        """ Calculates displacement of target in SAR image due to a motion induced
        derivative of the bistatic range

        Parameters
        ----------
        inc :
            incident angle, in radians
        dotr_s:
            time derivative of bistatic range due to target motion
        ascending :
             (Default value = True)

        Returns
        -------

        """
        # azimuth (time) shift
        c1 = self.inc2sgrad_r_b(inc, ascending=ascending)[:, 0] / self.inc2sgrad_dot_r_b(inc, ascending=ascending)[:, 0]
        d_r_b = self.inc2dot_r_b(inc, ascending=ascending)
        dd_r_b = self.inc2ddot_r_b(inc, ascending=ascending)
        dta = (dd_r_b * c1 - d_r_b - dotr_s)

        dta2 = dta - np.sqrt((dd_r_b * c1 - d_r_b)**2 + dotr_s * (dotr_s + 2 * dd_r_b))
        dta = dta - np.sign(dta) * np.sqrt((dd_r_b * c1 - d_r_b - dotr_s)**2 + 2 * c1 * dd_r_b * dotr_s)
        dta2 = dta2 / dd_r_b
        dta = dta / dd_r_b
        dx = (dd_r_b * dta + dotr_s) / self.inc2sgrad_dot_r_b(inc, ascending=ascending)[:, 0]
        return dta, dx, (c1, d_r_b, dd_r_b, dta2)


# %%
if __name__ == '__main__':
    import os
    from matplotlib import pyplot as plt
    stereoid_dir = os.path.expanduser("~/Documents/CODE/STEREOID")
    # drama_dir = os.path.expanduser("~/Code/drama")
    run_id = "2019_1"
    par_dir = os.path.join(stereoid_dir, "PAR")
    par_file = os.path.join(par_dir, ("Hrmny_%s.cfg" % run_id))
    bsgeo = BistaticRadarGeometry(par_file=par_file, companion_delay= 350e3/7.4e3)

#%%
    bsgeo.v_t[3000,::40]
    bsgeo.swth_t._incident.shape
    inc = np.linspace(23, 45, 100)
    plt.figure()
    #plt.plot(np.degrees(bsgeo.swth_t._incident[4000]), bsgeo.dr_b[4000]/0.054)
    plt.plot(inc, bsgeo.inc2dot_r_b(np.radians(inc))/0.054, linewidth=2)
    plt.plot(inc, bsgeo.inc2dot_r_b(np.radians(inc), ascending=False)/0.054, linewidth=2)
    plt.figure()
    plt.plot(inc, bsgeo.inc2ddot_r_b(np.radians(inc))/0.054, linewidth=2)
    plt.plot(inc, bsgeo.inc2ddot_r_b(np.radians(inc), ascending=False)/0.054, linewidth=2)
    #plt.plot(np.degrees(bsgeo.swth_t._incident[3000]), bsgeo.ddr_b[3000]/0.054)
    plt.figure()
    sgrad_r_b = bsgeo.inc2sgrad_r_b(np.radians(inc))
    sgrad_r_b[10]
    sgrad_dr_b = bsgeo.inc2sgrad_dot_r_b(np.radians(inc))
    plt.plot(inc, np.degrees(np.arctan(sgrad_r_b[:,1]/sgrad_r_b[:,0])))
    plt.plot(inc, -np.degrees(np.arctan(sgrad_dr_b[:,1]/sgrad_dr_b[:,0])))
    #plt.plot(inc, sgrad_r_b[:,1]/sgrad_r_b[:,0])
    #plt.plot(inc, sgrad_dr_b[:,1]/sgrad_dr_b[:,0])
#%%
    # train off track shift
    plt.figure()
    dta, dx, (c1, d_r_b, dd_r_b, dta2) = bsgeo.train_off_track_displacement(np.radians(inc))
    plt.plot(inc, dx, linewidth=2, label=r"$\Delta x$")
    plt.plot(inc, dta * 7e3, linewidth=2, label=r"$\Delta y$")
    # plt.plot(inc, dta2 * 7e3, linewidth=2, label=r"$\Delta y$")
    plt.ylabel("Offset [m]")
    plt.xlabel("Tx angle of incidence [deg]")
    plt.legend()
    d_r_b[10] * dta[10]
    dx[10]
    bsgeo.inc2sgrad_dot_r_b(np.radians(35))
    #plt.savefig("train_off_track_offsets.png")
    plt.figure()
    plt.plot(inc, 90+np.degrees(np.arctan(dta * 7e3/dx)), linewidth=2) #, label=r"$\Delta y$")
    plt.plot(inc, np.degrees(np.arctan(sgrad_r_b[:,1]/sgrad_r_b[:,0])))
    # plt.plot(inc, dta2 * 7e3, linewidth=2)

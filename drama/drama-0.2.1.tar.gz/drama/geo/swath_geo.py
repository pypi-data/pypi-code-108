"""swath_geo includes functionality that computes the geometry over the swath of satellite."""
from collections import namedtuple
import copy

import numpy as np
import scipy.interpolate as interpolate

import drama.orbits as drorb
import drama.orbits.keplerian as keplerian
import drama.utils as drtls
from drama import constants as const
from drama.geo import geometry as geom
from drama.io import cfg as cfg
from drama.orbits import sunsync_orbit as sso


__author__ = "Paco Lopez Dekker"
__email__ = "F.LopezDekker@tudeft.nl"

Swath = namedtuple(
    "Swath",
    [
        "lat",
        "lon",
        "incident",
        "Northing",
        "GP_mask",
        "LoS_satcoord",
        "R",
        "xyz",
        "local_x", # Cross-track axis at each point on the surface
        "local_y", # along-track axis at each point on the surface
        "local_z"  # vertical axis at each point
    ],
)

Swaths = namedtuple("Swaths", ["master_swath", "slave_swath"])

SingleTrack = namedtuple(
    "SingleTrack",
    [
        "lat",
        "lon",
        "inc_angle",
        "northing",
        "slant_range",
        "mask",
        "time",
        "velocity_x",
        "velocity_y",
        "velocity_z",
    ],
)


def line_of_sight(geometry, geometry_slave=None, icp=None, look="right", squint=0, surf_x=None, surf_y=None, surf_n=None):
    """
    Calculates the intersection between line of sight (near and far
    range) with the ellipsoid and then retrieves the geometric
    parameters (incidence angle and northing) for both the
    satellites for a bistatic configuration.

    Parameters
    ----------
    geometry : tuple
        Tuple consisting of three ndarrays that describe the geometry of the
        main satellite. The three arrays are the look angles, the position
        vector and the velocity vector.
    
    geometry_slave : tuple
        Same as `geometry` describing the geometry of the secondary satellite.
        If this variable is not specified then only the line of sight of the
        main satellite will be computed. (Default value = None)

    icp : ndarray
        float 2-D array giving the intercept point(s) with the
        ellipsoid [m]. (Default value = None)

    look : str 
        look direction of the instrument. Possible values are "right" and "left"
        (Default value = "right")

    squint : float
        squint angle (Default value = 0)

    surf_x : ndarray
        Unit vector (versor) pointing in the ground-range direction on the
        surface at the point where `icp` lies. If this variable (along with
        `surf_y` and `surf_n`) is not provided by the caller then it is
        calculated by this function after finding `icp`. (Default value =
        None)
    
    surf_y : ndarray
        Unit vector (versor) pointing in the along-track direction on the
        surface at the point where `icp` lies (Default value = None)

    surf_n : ndarray
        Unit vector (versor) pointing in the direction normal to the surface at
        the point where `icp` lies (Default value = None)

    Returns
    -------
    namedtuple
        named tuple containing latitudes and longitudes for near and
        far range and versors required for computing LoS.
    """

    # unpack parameter tuple of first satelite
    la_deg, r_ecef, v_ecef = geometry
    # A bit of initialization
    right_looking = look == "right"
    n_p = r_ecef.shape[0]
    nla = la_deg.size
    la = np.radians(la_deg)
    r_x = const.r_equatorial["wgs84"]  # earth equatorial radius [m]
    r_y = const.r_equatorial["wgs84"]  # earth equatorial radius [m]
    r_z = const.r_polar["wgs84"]  # earth radius at pole [m]
    # Calculate velocity and positions versor for both the satellites
    v_ecf_ver = v_ecef / np.linalg.norm(v_ecef, axis=1).reshape((n_p, 1))
    r_ecf_ver = r_ecef / np.linalg.norm(r_ecef, axis=1).reshape((n_p, 1))
    # Build normal unit vector from cross product of versors
    n_ver = np.cross(v_ecf_ver, r_ecf_ver)
    # Calculate near and far range line of sight versors for both the
    # satellites
    if icp is None:
        # Calculate near and far range intersection points of line of sight
        # with ellipsoid
        los = geom.create_LoS(
            r_ecef, v_ecef, la, squint_a=squint, right_looking=right_looking
        )
        icp = geom.pt_get_intersection_ellipsoid(r_ecef, los)
        # Now we are going to generate a surface-bound coordinate system aligned
        # with the flight direction
        surf_n = icp / (np.array([r_x ** 2, r_y ** 2, r_z ** 2]).reshape(1, 1, 3))
        surf_n = surf_n / np.linalg.norm(surf_n, axis=2).reshape((n_p, nla, 1))
        # Now local x-versor, i.e, axis in the ground-range direction
        surf_x = np.cross(v_ecf_ver.reshape((n_p, 1, 3)), surf_n)
        surf_x = surf_x / np.linalg.norm(surf_x, axis=2).reshape((n_p, nla, 1))
        # And local y (i.e. along-track) versor
        surf_y = np.cross(surf_n, surf_x)
        r_icp = np.linalg.norm(icp - r_ecef[:, np.newaxis, :], axis=2)
    # else use the icp passed to function
    else:
        # LoS of the second satellite is from its antenna towards the
        # points on the ellipsoid
        los = icp - r_ecef[:, np.newaxis, :]
        r_icp = np.linalg.norm(los, axis=2)
        los = los / r_icp[:, :, np.newaxis]
    los_satcord = np.zeros(los.shape)
    # equivalent to np.sum(los * v_ecf_ver[:, np.newaxis, :], axis=2)
    los_satcord[:, :, 0] = np.einsum("ijk,ik->ij", los, v_ecf_ver)
    los_satcord[:, :, 1] = np.einsum("ijk,ik->ij", los, r_ecf_ver)
    los_satcord[:, :, 2] = np.einsum("ijk,ik->ij", los, n_ver)

    los_local_z = -1 * np.einsum("ijk,ijk->ij", surf_n, los)
    inc_angle = np.arccos(los_local_z)
    z_u = np.array([0, 0, 1])
    local_n_v = (
        z_u.reshape((1, 1, 3))
        - np.sum(surf_n * z_u.reshape((1, 1, 3)), 2).reshape((n_p, nla, 1)) * surf_n
    )
    local_n_v = local_n_v / np.linalg.norm(local_n_v, axis=2).reshape((n_p, nla, 1))
    local_e_v = np.cross(local_n_v, surf_n)
    los_local_xy = -los - los_local_z.reshape(n_p, nla, 1) * surf_n
    los_local_xy_N = np.sum(los_local_xy * local_n_v, axis=-1)
    los_local_xy_E = np.sum(los_local_xy * local_e_v, axis=-1)
    los_local_N = np.arctan2(los_local_xy_E, los_local_xy_N)
    # Convert intercept point to lat lon
    lat = np.degrees(
        np.arctan(icp[:, :, 2] / (np.sqrt(icp[:, :, 0] ** 2.0 + icp[:, :, 1] ** 2.0)))
    )
    lon = np.degrees(np.arctan2(icp[:, :, 1], icp[:, :, 0]))
    # check for points in the swath that are on the other side of the pole
    good_points = np.where(
        np.sum(r_ecef[:, :2].reshape(n_p, 1, 2) * icp[:, :, :2], axis=2) > 0
    )
    gp_mask = np.zeros((n_p, nla)) + np.nan
    gp_mask[good_points] = 1
    if n_p * nla - np.sum(gp_mask) > 0.0:
        print("There are points on the other side of the pole(s)")
    swath = Swath(lat, lon, inc_angle, los_local_N, gp_mask, los_satcord, r_icp, icp,
                  surf_x, surf_y, surf_n)
    if geometry_slave is not None:
        swath_slave = line_of_sight(geometry=geometry_slave, icp=icp,
                                    surf_x=surf_x, surf_y=surf_y, surf_n=surf_n)
        return swath, swath_slave
    return swath


class SingleSwath(keplerian.SingleOrbit):
    """This class calculates and stores a number of geometric
        relations over one orbit.

    Parameters
    ----------
    look :
        left or right, defaults to "right"
    orb_type :
        sunsync or repeat, defaults to "sunsync"
    par_file :
        All orbit parameters should be in par_file, defaults to None
    inc_angle :
        optional, incident angle range. If not given it is taken from the par_file, defaults to None.
    squint :
        antenna squint, defaults to zero [deg]
    companion_delay :
        along-track separation in seconds. If zero then a monostatic geometry is assumed, defaults to 0.

    Returns
    -------

    """

    def __init__(
        self,
        orb_type="sunsync",
        look="right",
        par_file=None,
        inc_angle=None,
        squint=0,
        companion_delay=0,
    ):
        """Initialise SingleSwath"""
        # Call SingleOrbit initialization
        super().__init__(
            orb_type=orb_type,
            conffile=par_file,
            companion_delay=companion_delay,
        )
        cfgdata = cfg.ConfigFile(drtls.get_par_file(par_file))
        # create look angle vector
        if inc_angle is None:
            la_near = np.rad2deg(
                geom.inc_to_look(np.deg2rad(cfgdata.sar.near_1), self.Horb)
            )
            la_far = np.rad2deg(
                geom.inc_to_look(np.deg2rad(cfgdata.sar.far_1), self.Horb)
            )
        else:
            la_near = np.rad2deg(geom.inc_to_look(np.deg2rad(inc_angle[0]), self.Horb))
            la_far = np.rad2deg(geom.inc_to_look(np.deg2rad(inc_angle[1]), self.Horb))
        gr_res = cfgdata.sar.gr_res
        # get incident angles from look angles
        inc_near = geom.look_to_inc(np.deg2rad(np.abs(la_near)), self.Horb)
        inc_far = geom.look_to_inc(np.deg2rad(np.abs(la_far)), self.Horb)
        # get ground range from incident angles
        grg_near = geom.inc_to_gr(inc_near, self.Horb)
        grg_far = geom.inc_to_gr(inc_far, self.Horb)
        #    print(groundR_far-groundR_near)
        # number of cells along swath width
        n_cells = int(np.absolute(grg_far - grg_near) / gr_res)
        # look angle vector [deg]
        la_vector = np.linspace(la_near, la_far, n_cells)
        # Get lat, lon, incident & Northing information
        if companion_delay == 0:
            swath_data = line_of_sight(
                (la_vector, self.r_ecef, self.v_ecef), squint=squint, look=look
            )
            self.is_bistatic = False
        else:
            # Primary orbit
            self.is_bistatic = True
            master_orb_data = drorb.SingleOrbit(conffile=par_file)
            self.asc_idx = master_orb_data.asc_idx
            self.desc_idx = master_orb_data.desc_idx
            swath_master, swath_data = line_of_sight(
                (la_vector, master_orb_data.r_ecef, master_orb_data.v_ecef),
                (la_vector, self.r_ecef, self.v_ecef),
                look=look,
            )
        self._lats = swath_data.lat
        self._lons = swath_data.lon
        self._incident = swath_data.incident
        self._northing = swath_data.Northing
        self._gp_mask = swath_data.GP_mask
        self._LoS_satcoord = swath_data.LoS_satcoord
        self._R = swath_data.R
        self._xyz = swath_data.xyz
        # Local axis
        self.local_x = swath_data.local_x  # cross-track
        self.local_y = swath_data.local_y  # along-track
        self.local_z = swath_data.local_z
        if self.is_bistatic:
            self.master_inc = swath_master.incident
        else:
            self.master_inc = self.incident
        self.lat = 0

    @property
    def lats(self):
        """ """
        if self._track_direction == "complete":
            return self._lats
        elif self._track_direction == "ascending":
            return self._lats[self.asc_idx[0] : (self.asc_idx[1] + 1), :]
        else:
            return self._lats[self.desc_idx[0] : (self.desc_idx[1] + 1), :]

    @property
    def lons(self):
        """ """
        if self._track_direction == "complete":
            return self._lons
        elif self._track_direction == "ascending":
            return self._lons[self.asc_idx[0] : (self.asc_idx[1] + 1), :]
        else:
            return self._lons[self.desc_idx[0] : (self.desc_idx[1] + 1), :]

    @property
    def incident(self):
        """ """
        if self._track_direction == "complete":
            return self._incident
        elif self._track_direction == "ascending":
            return self._incident[self.asc_idx[0] : (self.asc_idx[1] + 1), :]
        else:
            return self._incident[self.desc_idx[0] : (self.desc_idx[1] + 1), :]

    @property
    def northing(self):
        """ """
        if self._track_direction == "complete":
            return self._northing
        elif self._track_direction == "ascending":
            return self._northing[self.asc_idx[0] : (self.asc_idx[1] + 1), :]
        else:
            return self._northing[self.desc_idx[0] : (self.desc_idx[1] + 1), :]

    @property
    def gp_mask(self):
        """ """
        if self._track_direction == "complete":
            return self._gp_mask
        elif self._track_direction == "ascending":
            return self._gp_mask[self.asc_idx[0] : (self.asc_idx[1] + 1), :]
        else:
            return self._gp_mask[self.desc_idx[0] : (self.desc_idx[1] + 1), :]

    @property
    def R(self):
        """ """
        if self._track_direction == "complete":
            return self._R
        elif self._track_direction == "ascending":
            return self._R[self.asc_idx[0] : (self.asc_idx[1] + 1), :]
        else:
            return self._R[self.desc_idx[0] : (self.desc_idx[1] + 1), :]

    @property
    def xyz(self):
        """ """
        if self._track_direction == "complete":
            return self._xyz
        elif self._track_direction == "ascending":
            return self._xyz[self.asc_idx[0] : (self.asc_idx[1] + 1), :]
        else:
            return self._xyz[self.desc_idx[0] : (self.desc_idx[1] + 1), :]

    @property
    def LoS_satcoord(self):
        """ """
        if self._track_direction == "complete":
            return self._LoS_satcoord
        elif self._track_direction == "ascending":
            return self._LoS_satcoord[self.asc_idx[0] : (self.asc_idx[1] + 1), :]
        else:
            return self._LoS_satcoord[self.desc_idx[0] : (self.desc_idx[1] + 1), :]

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
        # Look for
        mid_range = int(self.lats.shape[1] / 2)
        asclats = self.lats[self.asc_idx[0] : self.asc_idx[1], mid_range]
        dsclats = self.lats[self.asc_idx[1] :, mid_range]
        self.__asc_latind = np.argmin(np.abs(asclats - lat)) + self.asc_idx[0]
        self.__dsc_latind = np.argmin(np.abs(dsclats - lat)) + self.asc_idx[1]
        self.__asc_incm2inc = interpolate.interp1d(
            self.master_inc[self.__asc_latind],
            self.incident[self.__asc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__dsc_incm2inc = interpolate.interp1d(
            self.master_inc[self.__dsc_latind],
            self.incident[self.__dsc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__asc_incm2north = interpolate.interp1d(
            self.master_inc[self.__asc_latind],
            self.northing[self.__asc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__dsc_incm2north = interpolate.interp1d(
            self.master_inc[self.__dsc_latind],
            self.northing[self.__dsc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )

    def inc2slave_inc(self, inc, ascending=True):
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
            return self.__asc_incm2inc(inc)
        else:
            return self.__dsc_incm2inc(inc)

    def inc2northing(self, inc, ascending=True):
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
            return self.__asc_incm2north(inc)
        else:
            return self.__dsc_incm2north(inc)

    def interpolate_swath(self, step_lat_lon=(0.25, 0.1), max_lat=90.0):
        """Sets up interpolation parameters and runs the interpolation procedure.

        Parameters
        ----------
        step_lat_lon : tuple
            latitude and longitude step for interpolation
            in degrees (Default value = (0.25)
        max_lat : float
            maximum considered latitude, defaults to 90.0
        0.1) :


        Returns
        -------

        """
        (self.dlat, self.dlon) = step_lat_lon
        self.max_lat = max_lat
        ascending = self.__interpolate(ascending=True)
        descending = self.__interpolate(ascending=False)
        Tracks = namedtuple("Tracks", ["ascending", "descending"])
        self.interpol = Tracks(ascending, descending)

    def __interpolate(self, ascending=True):
        """Runs the interpolation using the parameters defined during
        the initialisation.

        :param step_lat_lon: latitude and longitude step for
        interpolation in degrees, defaults to None, when None assigned
        to value defined by the constructor :type step_lat_lon: tuple
        :param max_lat: maximum considered latitude, defaults to None,
        when None assigned to value defined by the constructor :type
        max_lat: float
        :param ascending: interpolate ascending track if True,
        descending track if False
        :type ascending: boolean

        return: track: Assigns results as attributes of a
        namedtuple. A tuple containing the latitude
        and longitude values of the reference grid, the interpolated
        incidence angle, northing, and a mask of the mapped and
        not-mapped points. The time vector of the SingleSwath and the
        number of orbits per repeat cycle are also set. The time
        vector is interpolated to the lat lon grid.
        """
        inc_angLE_min = np.min(self.incident)
        inc_angle_max = np.max(self.incident)

        # Ascending
        if ascending is True:
            self.track_direction = "ascending"
        else:
            self.track_direction = "descending"
        lat1 = self.lats * self.gp_mask
        lon1 = self.lons * self.gp_mask

        # repeat it
        time1 = np.repeat(self.timevec, lat1.shape[1]).reshape(lat1.shape)
        v_ecef1_x = np.repeat(self.v_ecef[:, 0], lat1.shape[1]).reshape(lat1.shape)
        v_ecef1_y = np.repeat(self.v_ecef[:, 1], lat1.shape[1]).reshape(lat1.shape)
        v_ecef1_z = np.repeat(self.v_ecef[:, 2], lat1.shape[1]).reshape(lat1.shape)

        inc_angle1 = self.incident * self.gp_mask
        northing1 = self.northing * self.gp_mask
        slant1 = self.R * self.gp_mask

        # set edges of incidence array to zero (prevent interpolation issues)
        inc_angle1 = _reset_array_edges(inc_angle1, 0)
        slant1 = _reset_array_edges(slant1, 0)
        indx1 = np.where((lat1 > -self.max_lat) & (lat1 < self.max_lat))
        # caveat: this spoils the zero edges if self.max_lat is < 90° !
        lat1_ = lat1[indx1]
        lon1_ = lon1[indx1]
        inc_angle1_ = inc_angle1[indx1]
        northing1_ = northing1[indx1]
        slant1_ = slant1[indx1]
        v_ecef1_x_ = v_ecef1_x[indx1]
        v_ecef1_y_ = v_ecef1_y[indx1]
        v_ecef1_z_ = v_ecef1_z[indx1]

        # unwrap longitudes to avoid wrapping issues
        lon1_ = np.degrees(np.unwrap(np.radians(lon1_)))

        lat_min = np.min(self.lats)
        lat_max = np.max(self.lats)
        lon_min = np.min(lon1_)
        lon_max = np.max(lon1_)

        # reshaping for the interpolation
        lat = np.reshape(lat1_, np.prod(np.size(lat1_)))
        lon = np.reshape(lon1_, np.prod(np.size(lon1_)))
        inc_angle = np.reshape(inc_angle1_, np.prod(np.size(inc_angle1_)))
        northing = np.reshape(northing1_, np.prod(np.size(northing1_)))
        slant = np.reshape(slant1_, np.prod(np.size(northing1_)))
        # Regular grid construction
        Nlat = np.int(np.abs(lat_max - lat_min) / self.dlat) + 1
        Nlon = np.int(np.abs(lon_max - lon_min) / self.dlon) + 1
        lat_i = np.linspace(lat_min, lat_max, Nlat)  # regularly spaced lat vector
        lon_i = np.linspace(lon_min, lon_max, Nlon)  # regularly spaced lon vector
        lon_i_asc, lat_i_asc = np.meshgrid(lon_i, lat_i)

        # Interpolation
        interpol_results = [
            interpolate.griddata(
                (lon, lat),
                x,
                (lon_i_asc, lat_i_asc),
                method="linear",
                fill_value=999,
            )
            for x in (
                inc_angle,
                northing,
                slant,
                time1.flatten(),
                v_ecef1_x_.flatten(),
                v_ecef1_y_.flatten(),
                v_ecef1_z_.flatten(),
            )
        ]
        (
            inc_angle_i_asc,
            northing_i_asc,
            slant_i_asc,
            time_i_asc,
            velocity_i_asc_x,
            velocity_i_asc_y,
            velocity_i_asc_z,
        ) = interpol_results
        inc_angle_min = np.min(self.incident)
        inc_angle_max = np.max(self.incident)
        mask = np.logical_and(
            (inc_angle_i_asc > inc_angle_min), (inc_angle_i_asc < inc_angle_max)
        )

        track = SingleTrack(
            lat_i_asc[:, 0],
            lon_i_asc[0, :],
            inc_angle_i_asc,
            northing_i_asc,
            slant_i_asc,
            mask,
            time_i_asc,
            velocity_i_asc_x,
            velocity_i_asc_y,
            velocity_i_asc_z,
        )
        self.track_direction = "complete"  # reset
        return track


class SingleSwathBistatic(object):
    """Calculates many geometrical variables for one orbit at a user defined
    grid including swathData.

    Parameters
    ----------
    orb_type : str
        sunsync or repeat
    look : str
        left or right
    ext_source : boolean
        if True, use external data source
    par_file : str
        path to configuration file
    inc_angle : ndarray
       array with two elements, first is near and second is far
    dau : float
        along-track separation [m]
    """

    def __init__(
        self,
        orb_type="sunsync",
        look="right",
        ext_source=False,
        par_file=None,
        inc_angle=None,
        dau=None,
        n_orbits=None,
        verbosity=1,
    ):
        self.info = drtls.PrInfo(verbosity, "single swath bistatic")
        # Satellite
        self.config = cfg.ConfigFile(par_file)
        self.par_file = par_file
        if dau is None:
            dau = np.array(self.config.formation_primary.dau)[0]
        n_days = self.config.orbit.days_cycle
        self.norb = self.config.orbit.orbits_nbr
        if n_orbits is None:
            self.n_max_orbits = self.norb
        else:
            self.n_max_orbits = n_orbits
        torb = 3600 * 24.0 * n_days / self.norb
        if verbosity < 3:
            silent = True
        else:
            silent = False
        (a, e, i) = sso.get_sunsync_repeat_orbit(n_days, self.norb, silent=silent)
        self.orb_delay = dau / a / (np.pi * 2) * torb
        # Retrieve data for a single orbit for the first satellite
        horb = a - const.r_earth
        self.info.msg("single_swath_b: assuming constant along-track separation", 1)
        # v_orb_m = np.mean(np.linalg.norm(v_ecef1, axis=1))
        # self.orb_delay = -1 * np.mean(dr_t_asc) / v_orb_m
        self.info.msg("Orbit delay: %f" % self.orb_delay, 1)
        if inc_angle is None:
            la_near = np.rad2deg(
                geom.inc_to_look(np.deg2rad(self.config.sar.near_1), horb)
            )
            la_far = np.rad2deg(
                geom.inc_to_look(np.deg2rad(self.config.sar.far_1), horb)
            )
        else:
            la_near = np.rad2deg(geom.inc_to_look(np.deg2rad(inc_angle[0]), horb))
            la_far = np.rad2deg(geom.inc_to_look(np.deg2rad(inc_angle[1]), horb))
        Angle = namedtuple("Angle", ["near", "far"])
        self.look_angles = Angle(la_near, la_far)
        self.master_orbit = drorb.SingleOrbit(conffile=par_file)
        self.slave_orbit = drorb.SingleOrbit(
            conffile=par_file,
            aei=self.master_orbit.aei,
            companion_delay=self.orb_delay,
        )
        self.n_current_orbit = 0
        self.__calculate_swath(look=look)
        self.lat = 0

    def __calculate_swath(self, look="right"):
        """__calculate_swath computes swath related parameters
        given the current formation.

        Parameters
        ----------
        config : drama.io.cfg.ConfigFile
            configuration object with parameters of formation and orbit
        look : str
            left or right
        look_angles : tuple
            near and far range look angles

        Returns
        -------
        out :

        """
        # get incident angles from look angles
        inc_near = geom.look_to_inc(
            np.deg2rad(np.abs(self.look_angles.near)), self.master_orbit.Horb
        )
        inc_far = geom.look_to_inc(
            np.deg2rad(np.abs(self.look_angles.far)), self.master_orbit.Horb
        )
        # get ground range from incident angles
        ground_r_near = geom.inc_to_gr(inc_near, self.master_orbit.Horb)
        ground_r_far = geom.inc_to_gr(inc_far, self.master_orbit.Horb)

        # number of cells along swath width
        n_cells = int(
            np.absolute(ground_r_far - ground_r_near) / self.config.sar.gr_res
        )

        # look angle vector [deg]
        la_vector = np.linspace(self.look_angles.near, self.look_angles.far, n_cells)

        # Get lat, lon, incident & Northing information for both satellite when
        # look at the same points on the ground
        swath_master, swath_comp = line_of_sight(
            (la_vector, self.master_orbit.r_ecef, self.master_orbit.v_ecef),
            (la_vector, self.slave_orbit.r_ecef, self.slave_orbit.v_ecef),
            look=look,
        )
        self.results = Swaths(swath_master, swath_comp)
        # FIXME these assignments are reduntant, they are added for compatibility
        self.lats = swath_master.lat
        self.lons = swath_master.lon
        self.master_inc = swath_master.incident
        self.slave_inc = swath_comp.incident
        self.master_northing = swath_master.Northing
        self.slave_northing = swath_comp.Northing
        self.gp_mask = swath_master.GP_mask
        self.master_los_satcoord = swath_master.LoS_satcoord
        self.slave__los_satcoord = swath_comp.LoS_satcoord
        self.master_range = swath_master.R
        self.slave_range = swath_comp.R
        self.xyz = swath_master.xyz

    def __iter__(self):
        return self

    def __next__(self):
        if (self.n_current_orbit > self.norb) or (
            self.n_current_orbit > self.n_max_orbits
        ):
            raise StopIteration
        else:
            results = copy.deepcopy(self.results)
            next(self.master_orbit)
            next(self.slave_orbit)
            self.__calculate_swath()
            self.n_current_orbit += 1
            return results

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
        # Look for
        mid_range = int(self.lats.shape[1] / 2)
        asclats = self.lats[
            self.master_orbit.asc_idx[0] : self.master_orbit.asc_idx[1],
            mid_range,
        ]
        dsclats = self.lats[self.master_orbit.asc_idx[1] :, mid_range]
        self.__asc_latind = (
            np.argmin(np.abs(asclats - lat)) + self.master_orbit.asc_idx[0]
        )
        self.__dsc_latind = (
            np.argmin(np.abs(dsclats - lat)) + self.master_orbit.asc_idx[1]
        )
        self.__asc_incm2incs = interpolate.interp1d(
            self.master_inc[self.__asc_latind],
            self.slave_inc[self.__asc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__dsc_incm2incs = interpolate.interp1d(
            self.master_inc[self.__dsc_latind],
            self.slave_inc[self.__dsc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__asc_incm2northm = interpolate.interp1d(
            self.master_inc[self.__asc_latind],
            self.master_northing[self.__asc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__dsc_incm2northm = interpolate.interp1d(
            self.master_inc[self.__dsc_latind],
            self.master_northing[self.__dsc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__asc_incm2norths = interpolate.interp1d(
            self.master_inc[self.__asc_latind],
            self.slave_northing[self.__asc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )
        self.__dsc_incm2norths = interpolate.interp1d(
            self.master_inc[self.__dsc_latind],
            self.slave_northing[self.__dsc_latind],
            "linear",
            bounds_error=False,
            fill_value=np.NaN,
        )

    def inc2slave_inc(self, inc, ascending=True):
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
            return self.__asc_incm2incs(inc)
        else:
            return self.__dsc_incm2incs(inc)

    def inc2northing(self, inc, ascending=True):
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
            return self.__asc_incm2northm(inc)
        else:
            return self.__dsc_incm2northm(inc)

    def inc2slave_northing(self, inc, ascending=True):
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
            return self.__asc_incm2norths(inc)
        else:
            return self.__dsc_incm2norths(inc)

    def inc2bist_ang_az(self, inc, ascending=True):
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
            return self.__asc_incm2northm(inc) - self.__asc_incm2norths(inc)
        else:
            return self.__dsc_incm2northm(inc) - self.__dsc_incm2norths(inc)


def _reset_array_edges(array, value):
    """Set the rows and columns on the surrounding the edges of a 2D
    array to value.

    Parameters
    ----------
    array : numpy.array
        array to process
    value : float
        value to assign to edges of array

    Returns
    -------

    """
    array[0, :] = value
    array[-1, :] = value
    array[:, 0] = value
    array[:, -1] = value
    return array


if __name__ == "__main__":
    # test code
    import os

    stereoid_dir = os.path.expanduser("~/Code/stereoid")
    drama_dir = os.path.expanduser("~/Code/drama")
    run_id = "2019_1"
    par_dir = os.path.join(stereoid_dir, "PAR")
    par_file = os.path.join(par_dir, ("Hrmny_%s.cfg" % run_id))
    save_dir = os.path.join(drama_dir, "drama", "coverage", "test")
    one_orb = SingleSwath(par_file=par_file)

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as interpol

from drama.io import cfg as cfg
from drama.orbits import SingleOrbit
from drama.utils import misc as misc
from drama.geo import geometry as geo, geometry as geom


class SquintedGeo:
    """A class for Doppler-range relations.

    Parameters
    ----------
    latitude :
        latitude of wanted swath sector
    wvlength :
        wavelength of SAR signal
    squint :
        antenna's squint angle [deg]
    extreme_ang :
        initialization squint range [deg] -60 to 60
    orb_type :
        orbital type
    look :
        left' or 'right'
    ext_source :
        if True, use external data source
    parfile :
        file from which to read this events
    inc_angle :
        initialization incident angle range [deg]
    inkind :
        interpolation kind (quadratic, cubic,....)

    Returns
    -------

    """

    def __init__(
        self,
        latitude,
        wvlength,
        squint,
        extreme_ang=80,
        orb_type="sunsync",
        look="right",
        ext_source=False,
        parFile=None,
        parTuple=None,
        inc_angle=[1, 84],
        inkind="linear",
    ):
        """ Initialise DopplerRange class.
        """
        if parTuple is None:
            self.parFile = misc.get_par_file(parFile)
            inData = cfg.ConfigFile(self.parFile)
        else:
            inData = parTuple

        Single_orbData = SingleOrbit(
            orb_type=orb_type, conffile=parFile, conftuple=parTuple
        )
        self.Horb = Single_orbData.Horb
        self.gr_res = inData.sar.gr_res
        self.timestep = inData.orbit.timestep

        self.inkind = inkind
        self.squint = squint

        # create look angle vector
        if not inc_angle:
            self.la_near = np.rad2deg(
                geom.inc_to_look(np.deg2rad(inData.sar.near_1), self.Horb)
            )  # [deg]
            self.la_far = np.rad2deg(
                geom.inc_to_look(np.deg2rad(inData.sar.far_1), self.Horb)
            )  # [deg]
        else:
            self.la_near = np.rad2deg(
                geom.inc_to_look(np.deg2rad(inc_angle[0]), self.Horb)
            )
            self.la_far = np.rad2deg(
                geom.inc_to_look(np.deg2rad(inc_angle[1]), self.Horb)
            )

        r_ecef = Single_orbData.r_ecef
        v_ecef = Single_orbData.v_ecef

        # get incident angles from look angles
        inc_near = geom.look_to_inc(np.deg2rad(np.abs(self.la_near)), self.Horb)
        inc_far = geom.look_to_inc(np.deg2rad(np.abs(self.la_far)), self.Horb)

        # get ground range from incident angles
        groundR_near = geom.inc_to_gr(inc_near, self.Horb)
        groundR_far = geom.inc_to_gr(inc_far, self.Horb)

        # number of cells along swath width
        self.n_cells = int(
            np.absolute(groundR_far - groundR_near) / self.gr_res
        )

        # look angle vector [deg]
        la_vector = np.linspace(self.la_near, self.la_far, self.n_cells)

        # A bit of initialization
        Np = r_ecef.shape[0]
        Nla = la_vector.size
        la = np.radians(la_vector)

        # Calculate velocity and positions versor
        v_ecef_ver = v_ecef / np.linalg.norm(v_ecef, axis=1).reshape((Np, 1))
        r_ecef_ver = r_ecef / np.linalg.norm(r_ecef, axis=1).reshape((Np, 1))

        # Build cross product of versors
        n_ver = np.cross(v_ecef_ver, r_ecef_ver)  # cross product of versors

        # Calculate near and far range line of sight versors
        LoS = -np.cos(la.reshape(1, Nla, 1)) * r_ecef_ver.reshape(
            Np, 1, 3
        ) + np.sin(la.reshape(1, Nla, 1)) * n_ver.reshape(Np, 1, 3)

        # Calculate near and far range intersection points of line of sight
        # with ellipsoid
        icp = geo.pt_get_intersection_ellipsoid(r_ecef, LoS)

        # Convert intercept point to lat lon
        lat = np.degrees(
            np.arctan(
                icp[:, :, 2]
                / (np.sqrt(icp[:, :, 0] ** 2.0 + icp[:, :, 1] ** 2.0))
            )
        )

        # Find location of required latitude in array
        loc = np.where(
            np.abs(lat[:, 0] - latitude) == np.min(np.abs(lat[:, 0] - latitude))
        )[0][0]

        # Create Orbit segment
        # first point on swath
        pt0 = icp[loc, 0, :]

        # center point on satellite orbit
        st0 = r_ecef[loc, :]
        R_center = np.linalg.norm(st0 - pt0)
        d_extreme = R_center * np.tan(np.deg2rad(extreme_ang))
        steps = d_extreme / np.linalg.norm(r_ecef[1, :] - r_ecef[0, :])
        # required orbit segment
        orb_segments = range(loc - int(steps), loc + int(steps) + 1)

        # range vectors for each cell in required swath segment
        self.icp_req = icp[loc, :, :]  # n_cells x 3
        self.r_ecef_req = r_ecef[orb_segments]
        self.v_ecef_req = v_ecef[orb_segments]

        self.icp_ext = (
            np.zeros((self.icp_req.shape[0], self.r_ecef_req.shape[0], 3))
            + self.icp_req[:, np.newaxis, :]
        )
        r_ecef_ext = (
            np.zeros((self.icp_req.shape[0], self.r_ecef_req.shape[0], 3))
            + self.r_ecef_req[np.newaxis, :, :]
        )

        self.R_all = self.icp_ext - r_ecef_ext  # n_cells x orb_segments x 3

        # Range magnitude matrix (n_cells x orb_segments)
        self.R_all_mag = np.linalg.norm(self.R_all, axis=2)

        # Calculate squnit angle  (squint = np.arccos(-(R.V)/RV))
        v_new = np.reshape(
            self.v_ecef_req,
            (1, self.v_ecef_req.shape[0], self.v_ecef_req.shape[1]),
        )
        RV = np.linalg.norm(self.v_ecef_req, axis=1) * self.R_all_mag
        dot1 = np.sum(v_new * self.R_all, axis=2)
        v_mag = np.linalg.norm(self.v_ecef_req, axis=1)
        self.squint_r = np.arcsin(dot1 / RV)

        # Calculate incident angle [deg]
        p_new = np.reshape(
            self.icp_req, (self.icp_req.shape[0], 1, self.icp_req.shape[1])
        )
        dot2 = np.sum(-p_new * self.R_all, axis=2)
        RP = np.linalg.norm(p_new, axis=2) * self.R_all_mag
        self.theta_inc = np.arccos(dot2 / RP)

        # Matrix containing all doppler frequencies for each cell
        self.f_doppler = 2 * v_mag * np.sin(self.squint_r) / wvlength

        # time vector
        self.timevec = np.arange((self.icp_ext.shape[1])) * self.timestep
        self.timemat = (
            np.zeros((self.f_doppler.shape[0], self.f_doppler.shape[1]))
            + self.timevec[np.newaxis, :]
        )

        # ################################################################# #
        # ########################### Final Stage ######################### #
        # Doppler frequency corresponding to required squint
        # assume satellites velocity is constant over the orbital segment
        self.fds = (
            2
            * v_mag[int(len(v_mag) / 2)]
            * np.sin(np.deg2rad(squint))
            / wvlength
        )
        self.fd02t = np.zeros((self.n_cells))
        self.fds2t = np.zeros((self.n_cells))
        self.fd02r0 = np.zeros((self.n_cells))
        self.fd02th0 = np.zeros((self.n_cells))
        self.fds2rs = np.zeros((self.n_cells))
        self.fds2ths = np.zeros((self.n_cells))

        for i in range(0, self.n_cells):
            # Create segments around fd0 and fds
            ctr0 = np.where(
                np.abs(self.f_doppler[i, :])
                == np.min((np.abs(self.f_doppler[i, :])))
            )[0][0]
            [k0, n0] = [ctr0 - 5, ctr0 + 5]
            ctrs = np.where(
                np.abs(self.f_doppler[i, :] - self.fds)
                == np.min(np.abs(self.f_doppler[i, :] - self.fds))
            )[0][0]
            [ks, ns] = [ctrs - 5, ctrs + 5]

            # Doppler frequency to time function
            self.fd0t = interpol.interp1d(
                self.f_doppler[i, k0:n0], self.timevec[k0:n0], kind=self.inkind
            )
            self.fdst = interpol.interp1d(
                self.f_doppler[i, ks:ns], self.timevec[ks:ns], kind=self.inkind
            )

            # Time to Range relation
            self.t2r0 = interpol.interp1d(
                self.timevec[k0:n0], self.R_all_mag[i, k0:n0], kind=self.inkind
            )
            self.t2rs = interpol.interp1d(
                self.timevec[ks:ns], self.R_all_mag[i, ks:ns], kind=self.inkind
            )

            # Time to Theta_inc relation
            self.t2th0 = interpol.interp1d(
                self.timevec[k0:n0], self.theta_inc[i, k0:n0], kind=self.inkind
            )
            self.t2ths = interpol.interp1d(
                self.timevec[ks:ns], self.theta_inc[i, ks:ns], kind=self.inkind
            )

            self.fd02t[i] = self.fd0t(0)
            self.fds2t[i] = self.fdst(self.fds)
            self.fd02r0[i] = self.t2r0(self.fd02t[i])
            self.fd02th0[i] = np.rad2deg(self.t2th0(self.fd02t[i]))
            self.fds2rs[i] = self.t2rs(self.fds2t[i])
            self.fds2ths[i] = np.rad2deg(self.t2ths(self.fds2t[i]))

        # ###################### Final Relations ############################
        # R0 relations
        self.r02rs = interpol.interp1d(
            self.fd02r0, self.fds2rs, kind=self.inkind
        )
        self.r02th0 = interpol.interp1d(
            self.fd02r0, self.fd02th0, kind=self.inkind
        )
        self.r02ths = interpol.interp1d(
            self.fd02r0, self.fds2ths, kind=self.inkind
        )
        # RS relations
        self.rs2r0 = interpol.interp1d(
            self.fds2rs, self.fd02r0, kind=self.inkind
        )
        self.rs2th0 = interpol.interp1d(
            self.fds2rs, self.fd02th0, kind=self.inkind
        )
        self.rs2ths = interpol.interp1d(
            self.fds2rs, self.fds2ths, kind=self.inkind
        )
        # TH0 relations
        self.th02r0 = interpol.interp1d(
            self.fd02th0, self.fd02r0, kind=self.inkind
        )
        self.th02rs = interpol.interp1d(
            self.fd02th0, self.fds2rs, kind=self.inkind
        )
        self.th02ths = interpol.interp1d(
            self.fd02th0, self.fds2ths, kind=self.inkind
        )
        # THS relations
        self.ths2r0 = interpol.interp1d(
            self.fds2ths, self.fd02r0, kind=self.inkind
        )
        self.ths2rs = interpol.interp1d(
            self.fds2ths, self.fds2rs, kind=self.inkind
        )
        self.ths2th0 = interpol.interp1d(
            self.fds2ths, self.fd02th0, kind=self.inkind
        )

        # ######################### define bounds ######################### #
        self.r0_bounds = [min(self.fd02r0), max(self.fd02r0)]
        self.rs_bounds = [min(self.fds2rs), max(self.fds2rs)]
        self.th0_bounds = [min(self.fd02th0), max(self.fd02th0)]
        self.ths_bounds = [min(self.fds2ths), max(self.fds2ths)]

    def showPointOut(self, pt_loc):
        """Plot for testing (one point in swath)

        Parameters
        ----------
        pt_loc :
            index of point on swath of predefined latitude

        Returns
        -------

        """
        minloc = np.where(
            self.R_all_mag[pt_loc, :] == min(self.R_all_mag[pt_loc, :])
        )[0][0]
        plt.figure()
        gs = gridspec.GridSpec(3, 1)
        ax1 = plt.subplot(gs[0, 0])
        plt.plot(self.timevec, self.R_all_mag[pt_loc, :] / 1000.0)
        plt.ylabel("Range [km]", fontsize=14)
        plt.xlabel("time step [s]", fontsize=14)
        ax1.grid(True)
        ax1.plot(
            self.timevec[minloc], self.R_all_mag[pt_loc, minloc] / 1000.0, "or"
        )
        ax1.annotate(
            str(int(self.R_all_mag[pt_loc, minloc] / 10.0) / 100.0),
            xy=(self.timevec[minloc], self.R_all_mag[pt_loc, minloc] / 1000.0),
            xycoords="data",
        )

        ax2 = plt.subplot(gs[1, 0])
        plt.plot(self.timevec, self.f_doppler[pt_loc, :] / 1000.0)
        plt.ylabel("Doppler frequency [kHz]", fontsize=14)
        plt.xlabel("time step [s]", fontsize=14)
        ax2.grid(True)
        ax2.plot(
            self.timevec[minloc], self.f_doppler[pt_loc, minloc] / 1000.0, "or"
        )
        ax2.annotate(
            str(int(self.f_doppler[pt_loc, minloc] / 10.0) / 100.0),
            xy=(self.timevec[minloc], self.f_doppler[pt_loc, minloc] / 1000.0),
            xycoords="data",
        )
        ax3 = plt.subplot(gs[2, 0])
        plt.plot(self.timevec, np.rad2deg(self.theta_inc[pt_loc, :]))
        plt.ylabel("Incident angle [deg]", fontsize=14)
        plt.xlabel("time step [s]", fontsize=14)
        ax3.grid(True)
        ax3.plot(
            self.timevec[minloc],
            np.rad2deg(self.theta_inc[pt_loc, minloc]),
            "or",
        )
        ax3.annotate(
            str(
                int(np.rad2deg(self.theta_inc[pt_loc, minloc]) * 100.0) / 100.0
            ),
            xy=(
                self.timevec[minloc],
                np.rad2deg(self.theta_inc[pt_loc, minloc]),
            ),
            xycoords="data",
        )
        plt.grid
        plt.show

    def showAllOut(self):
        """Plot All relations"""
        plt.figure()
        gs = gridspec.GridSpec(4, 1)

        # r0 relations
        r0 = np.arange(
            int(self.r0_bounds[0]) + 1, int(self.r0_bounds[1] - 1), 1000
        )
        ax1 = plt.subplot(gs[0, 0])
        ax1.plot(r0 / 1000.0, self.r02rs(r0) / 1000.0, "b-")
        ax1.set_xlabel("range_zd [km]", fontsize=14)
        ax1.set_ylabel("range_sq [km]", color="b", fontsize=14)
        for al in ax1.get_yticklabels():
            al.set_color("b")

        ax12 = ax1.twinx()
        ax12.plot(r0 / 1000.0, self.r02th0(r0), "r-", label="theta_zd")
        ax12.plot(
            r0 / 1000.0, self.r02ths(r0), "-o", color="r", label="theta_sq"
        )
        ax12.set_ylabel("theta [deg]", color="r", fontsize=14)
        for al in ax12.get_yticklabels():
            al.set_color("r")
        ax1.grid(True)
        plt.legend()

        # rs relations
        rs = np.arange(
            int(self.rs_bounds[0]) + 1, int(self.rs_bounds[1] - 1), 1000
        )
        ax2 = plt.subplot(gs[1, 0])
        ax2.plot(rs / 1000.0, self.rs2r0(rs) / 1000.0, "b-")
        ax2.set_xlabel("range_sq [km]", fontsize=14)
        ax2.set_ylabel("range_zd [km]", color="b", fontsize=14)
        for al in ax2.get_yticklabels():
            al.set_color("b")

        ax22 = ax2.twinx()
        ax22.plot(rs / 1000.0, self.rs2th0(rs), "r-", label="theta_zd")
        ax22.plot(
            rs / 1000.0, self.rs2ths(rs), "-o", color="r", label="theta_sq"
        )
        ax22.set_ylabel("theta [deg]", color="r", fontsize=14)
        for al in ax22.get_yticklabels():
            al.set_color("r")
        ax2.grid(True)
        plt.legend()

        # th0 relations
        th0 = np.arange(
            int(self.th0_bounds[0]) + 1, int(self.th0_bounds[1] - 1), 1
        )
        ax3 = plt.subplot(gs[2, 0])
        ax3.plot(th0, self.th02r0(th0) / 1000.0, "b-", label="range_zd")
        ax3.plot(
            th0, self.th02rs(th0) / 1000.0, "-o", color="b", label="range_sq"
        )
        ax3.set_xlabel("theta_zd [deg]", fontsize=14)
        ax3.set_ylabel("range [km]", color="b", fontsize=14)
        for al in ax3.get_yticklabels():
            al.set_color("b")
        plt.legend()

        ax32 = ax3.twinx()
        ax32.plot(th0, self.th02ths(th0), "r-")
        ax32.set_ylabel("theta_sq [deg]", color="r", fontsize=14)
        for al in ax32.get_yticklabels():
            al.set_color("r")
        ax3.grid(True)

        # ths relations
        ths = np.arange(
            int(self.ths_bounds[0]) + 1, int(self.ths_bounds[1] - 1), 1
        )
        ax4 = plt.subplot(gs[3, 0])
        ax4.plot(ths, self.ths2r0(ths) / 1000.0, "b-", label="range_zd")
        ax4.plot(
            ths, self.ths2rs(ths) / 1000.0, "-o", color="b", label="range_sq"
        )
        ax4.set_xlabel("theta_sq [deg]", fontsize=14)
        ax4.set_ylabel("range [km]", color="b", fontsize=14)
        for al in ax4.get_yticklabels():
            al.set_color("b")
        plt.legend()

        ax42 = ax4.twinx()
        ax42.plot(ths, self.ths2th0(ths), "r-")
        ax42.set_ylabel("theta_zd [deg]", color="r", fontsize=14)
        for al in ax42.get_yticklabels():
            al.set_color("r")
        ax4.grid(True)


def compareAllOut(self1, self2, variable):
    """Plots two different squinted relations for comparison purposes

    Parameters
    ----------
    self1 :
        class object containing relations 1
    self2 :
        class object containing relations 2
    variable :
        string defining base for relations
        eg.( 'r0','rs','th0','ths')

    Returns
    -------

    """

    if variable == "r0":
        plt.figure()
        gs = gridspec.GridSpec(3, 1)
        r0 = np.arange(
            int(max(self1.r0_bounds[0], self2.r0_bounds[0])) + 1,
            int(min(self1.r0_bounds[1], self2.r0_bounds[1])) - 1,
            1000,
        )
        ax1 = plt.subplot(gs[0, 0])
        plt.plot(r0 / 1000.0, self1.r02rs(r0) / 1000.0, label="obj1")
        plt.plot(r0 / 1000.0, self2.r02rs(r0) / 1000.0, label="obj2")
        plt.ylabel("range_sq [km]", fontsize=14)
        ax1.grid(True)
        plt.legend()

        ax2 = plt.subplot(gs[1, 0])
        plt.plot(r0 / 1000.0, self1.r02th0(r0), label="obj1")
        plt.plot(r0 / 1000.0, self2.r02th0(r0), label="obj2")
        plt.ylabel("theta_zd [deg]", fontsize=14)
        ax2.grid(True)
        plt.legend()

        ax3 = plt.subplot(gs[2, 0])
        plt.plot(r0 / 1000.0, self1.r02ths(r0), label="obj1")
        plt.plot(r0 / 1000.0, self2.r02ths(r0), label="obj2")
        plt.xlabel("range_zd [km]", fontsize=14)
        plt.ylabel("theta_sq [deg]", fontsize=14)
        ax3.grid(True)
        plt.legend()

    elif variable == "rs":
        plt.figure()
        gs = gridspec.GridSpec(3, 1)
        rs = np.arange(
            int(max(self1.rs_bounds[0], self2.rs_bounds[0])) + 1,
            int(min(self1.rs_bounds[1], self2.rs_bounds[1])) - 1,
            1000,
        )
        ax1 = plt.subplot(gs[0, 0])
        plt.plot(rs / 1000.0, self1.rs2r0(rs) / 1000.0, label="obj1")
        plt.plot(rs / 1000.0, self2.rs2r0(rs) / 1000.0, label="obj2")
        plt.ylabel("range_zd [km]", fontsize=14)
        ax1.grid(True)
        plt.legend()

        ax2 = plt.subplot(gs[1, 0])
        plt.plot(rs / 1000.0, self1.rs2th0(rs), label="obj1")
        plt.plot(rs / 1000.0, self2.rs2th0(rs), label="obj2")
        plt.ylabel("theta_zd [deg]", fontsize=14)
        ax2.grid(True)
        plt.legend()

        ax3 = plt.subplot(gs[2, 0])
        plt.plot(rs / 1000.0, self1.rs2ths(rs), label="obj1")
        plt.plot(rs / 1000.0, self2.rs2ths(rs), label="obj2")
        plt.xlabel("range_sq [km]", fontsize=14)
        plt.ylabel("theta_sq [deg]", fontsize=14)
        ax3.grid(True)
        plt.legend()

    elif variable == "th0":
        plt.figure()
        gs = gridspec.GridSpec(3, 1)
        th0 = np.arange(
            int(max(self1.th0_bounds[0], self2.th0_bounds[0])) + 1,
            (int(min(self1.th0_bounds[1], self2.th0_bounds[1])) - 1),
            1,
        )
        ax1 = plt.subplot(gs[0, 0])
        plt.plot(th0, self1.th02r0(th0) / 1000.0, label="obj1")
        plt.plot(th0, self2.th02r0(th0) / 1000.0, label="obj2")
        plt.ylabel("range_zd [km]", fontsize=14)
        ax1.grid(True)
        plt.legend()

        ax2 = plt.subplot(gs[1, 0])
        plt.plot(th0, self1.th02rs(th0) / 1000.0, label="obj1")
        plt.plot(th0, self2.th02rs(th0) / 1000.0, label="obj2")
        plt.ylabel("range_sq [km]", fontsize=14)
        ax2.grid(True)
        plt.legend()

        ax3 = plt.subplot(gs[2, 0])
        plt.plot(th0, self1.th02ths(th0), label="obj1")
        plt.plot(th0, self2.th02ths(th0), label="obj2")
        plt.xlabel("theta_zd [deg]", fontsize=14)
        plt.ylabel("theta_sq [deg]", fontsize=14)
        ax3.grid(True)
        plt.legend()

    elif variable == "ths":
        plt.figure()
        gs = gridspec.GridSpec(3, 1)
        ths = np.arange(
            int(max(self1.ths_bounds[0], self2.ths_bounds[0])) + 1,
            (int(min(self1.ths_bounds[1], self2.ths_bounds[1])) - 1),
            1,
        )
        ax1 = plt.subplot(gs[0, 0])
        plt.plot(ths, self1.ths2r0(ths) / 1000.0, label="obj1")
        plt.plot(ths, self2.ths2r0(ths) / 1000.0, label="obj2")
        plt.ylabel("range_zd [km]", fontsize=14)
        ax1.grid(True)
        plt.legend()

        ax2 = plt.subplot(gs[1, 0])
        plt.plot(ths, self1.ths2rs(ths) / 1000.0, label="obj1")
        plt.plot(ths, self2.ths2rs(ths) / 1000.0, label="obj2")
        plt.ylabel("range_sq [km]", fontsize=14)
        ax2.grid(True)
        plt.legend()

        ax3 = plt.subplot(gs[2, 0])
        plt.plot(ths, self1.ths2th0(ths), label="obj1")
        plt.plot(ths, self2.ths2th0(ths), label="obj2")
        plt.xlabel("theta_sq [deg]", fontsize=14)
        plt.xlabel("theta_zd [deg]", fontsize=14)
        ax3.grid(True)
        plt.legend()

    else:
        print("Enter a valid variable! ('r0','rs','th0','ths')")


def errorDiff(self1, self2, variable):
    """Plots error of 2 objects representing different relations

    Parameters
    ----------
    self1 :
        class object containing relations 1
    self2 :
        class object containing relations 2
    variable :
        string defining base for relations
        eg.( 'r0','rs','th0','ths')

    Returns
    -------

    """

    if variable == "r0":
        plt.figure()
        gs = gridspec.GridSpec(3, 1)
        r0 = np.arange(
            int(max(self1.r0_bounds[0], self2.r0_bounds[0])) + 1,
            int(min(self1.r0_bounds[1], self2.r0_bounds[1])) - 1,
            1000,
        )
        ax1 = plt.subplot(gs[0, 0])
        plt.plot(r0 / 1000.0, abs(self1.r02rs(r0) - self2.r02rs(r0)))
        plt.ylabel("range_sq error [m]", fontsize=14)
        ax1.grid(True)

        ax2 = plt.subplot(gs[1, 0])
        plt.plot(r0 / 1000.0, abs(self1.r02th0(r0) - self2.r02th0(r0)))
        plt.ylabel("theta_zd error [deg]", fontsize=14)
        ax2.grid(True)

        ax3 = plt.subplot(gs[2, 0])
        plt.plot(r0 / 1000.0, abs(self1.r02ths(r0) - self2.r02ths(r0)))
        plt.xlabel("range_zd [km]", fontsize=14)
        plt.ylabel("theta_sq error [deg]", fontsize=14)
        ax3.grid(True)

    elif variable == "rs":
        plt.figure()
        gs = gridspec.GridSpec(3, 1)
        rs = np.arange(
            int(max(self1.rs_bounds[0], self2.rs_bounds[0])) + 1,
            int(min(self1.rs_bounds[1], self2.rs_bounds[1])) - 1,
            1000,
        )
        ax1 = plt.subplot(gs[0, 0])
        plt.plot(rs / 1000.0, abs(self1.rs2r0(rs) - self2.rs2r0(rs)))
        plt.ylabel("range_zd error [m]", fontsize=14)
        ax1.grid(True)

        ax2 = plt.subplot(gs[1, 0])
        plt.plot(rs / 1000.0, abs(self1.rs2th0(rs) - self2.rs2th0(rs)))
        plt.ylabel("theta_zd error [deg]", fontsize=14)
        ax2.grid(True)

        ax3 = plt.subplot(gs[2, 0])
        plt.plot(rs / 1000.0, abs(self1.rs2ths(rs) - self2.rs2ths(rs)))
        plt.xlabel("range_sq [km]", fontsize=14)
        plt.ylabel("theta_sq error [deg]", fontsize=14)
        ax3.grid(True)

    elif variable == "th0":
        plt.figure()
        gs = gridspec.GridSpec(3, 1)
        th0 = np.arange(
            int(max(self1.th0_bounds[0], self2.th0_bounds[0])) + 1,
            (int(min(self1.th0_bounds[1], self2.th0_bounds[1])) - 1),
            1,
        )
        ax1 = plt.subplot(gs[0, 0])
        plt.plot(th0, abs(self1.th02r0(th0) - self2.th02r0(th0)))
        plt.ylabel("range_zd error [m]", fontsize=14)
        ax1.grid(True)

        ax2 = plt.subplot(gs[1, 0])
        plt.plot(th0, abs(self1.th02rs(th0) - self2.th02rs(th0)))
        plt.ylabel("range_sq error[m]", fontsize=14)
        ax2.grid(True)

        ax3 = plt.subplot(gs[2, 0])
        plt.plot(th0, abs(self1.th02ths(th0) - self2.th02ths(th0)))
        plt.xlabel("theta_zd [deg]", fontsize=14)
        plt.ylabel("theta_sq error[deg]", fontsize=14)
        ax3.grid(True)

    elif variable == "ths":
        plt.figure()
        gs = gridspec.GridSpec(3, 1)
        ths = np.arange(
            int(max(self1.ths_bounds[0], self2.ths_bounds[0])) + 1,
            (int(min(self1.ths_bounds[1], self2.ths_bounds[1])) - 1),
            1,
        )
        ax1 = plt.subplot(gs[0, 0])
        plt.plot(ths, abs(self1.ths2r0(ths) - self2.ths2r0(ths)))
        plt.ylabel("range_zd error[m]", fontsize=14)
        ax1.grid(True)

        ax2 = plt.subplot(gs[1, 0])
        plt.plot(ths, abs(self1.ths2rs(ths) - self2.ths2rs(ths)))
        plt.ylabel("range_sq error[m]", fontsize=14)
        ax2.grid(True)

        ax3 = plt.subplot(gs[2, 0])
        plt.plot(ths, abs(self1.ths2th0(ths) - self2.ths2th0(ths)))
        plt.xlabel("theta_sq [deg]", fontsize=14)
        plt.xlabel("theta_zd error[deg]", fontsize=14)
        ax3.grid(True)

    else:
        print("Enter a valid variable! ('r0','rs','th0','ths')")

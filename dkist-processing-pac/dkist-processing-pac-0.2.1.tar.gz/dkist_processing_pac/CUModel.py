import pkg_resources
import numpy as np
from dkist_processing_pac import Data
from dkist_processing_pac.tag import tag


class CalibrationSequence():
    """Set up the Mueller matrices of the Calibration Unit at each step in a Calibration Sequence. The sequence is
    defined by vectors containing the angles of the polarizer and retarder, but each of these elements can either be
    inserted or removed from the beam as necessary.

    The complete model of the Calibration Unit consists of a polarizer followed by an elliptical retarder. The set of
    Mueller matrices for each element can be accessed directly and are updated in real time whenever they are queried.

    The set of N (number of steps) Mueller matrices for the entire CU is accessed via the .CM property.

    The fact that all components of the model are recomputed each time they are queried makes this class a natural fit
    for iterative fitting techniques.

    Multiple Calibration Sequences can be strung together with the + operator. This simply stores all CS's in the same
    object; each CS is allowed to have its own set of parameters.

    Attributes
    (only those you might need)
    ----------
    CM : numpy.ndarray
        Set of Mueller matrices for the entire CU at each step. Shape (N, 4, 4)

    S_in : numpy.ndarray
        The Stokes vector of idea input light. Defaults to [1,0,0,0]

    ret : numpy.ndarray
        The value of retardance computed at each step in the CS

    pol_mat : numpy.ndarray
        Set of Mueller matrices for the polarizer alone. Shape (N, 4, 4)

    ret_mat : numpy.ndarray
        Set of Mueller matrices for the retarder alone. Shape (N, 4, 4)

    Notes
    -----
    The current CU model has six parameters: the intercept and slope for horizontal, 45 degree, and circular retardance.
    Each of the three retardance values is given by

            ret_i(t) = ret_0_i + dret_i * (t - t_0),

    where ret_0_i is the retardance at time t_0.

    """

    def __init__(self, theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in, timeobs,
                 ret_0_h=0., dret_h=0.,
                 ret_0_45=0., dret_45=0.,
                 ret_0_r=0., dret_r=0.,
                 t_pol_0=1., t_ret_0=1., py=0,
                 I_sys = 1., Q_in=0, U_in=0, V_in=0):
        """Initialize the Calibration Unit at each of the polarizer/retarder angles provided in the Calibration Sequence

        The values for the properties of the optical elements and the angular uncertainty can also be provided.

        Parameters
        ----------
        theta_pol_steps : numpy.ndarray
            A 1D array of length N that has the angles (in degrees) of the polarizer at each step of the CS

        theta_ret_steps : numpy.ndarray
            A 1D array of length N that has the angles (in degrees) of the retarder at each step of the CS

        pol_in : numpy.ndarray
            A 1D Boolean array of length N that describes the state of the GOS polarizer at each step in the CS.
            True corresponds to the polarizer in the beam path.

        ret_in : numpy.ndarray
            A 1D Boolean array of length N that describes the state of the GOS retarder at each step in the CS.
            True corresponds to the retarder in the beam path.

        timeobs : numpy.ndarray
            A 1D array of length N containing the observation time (MJD) of each step of the CS.

        ret_0_i : float
            Value of the retardance i intercept (in radians).

        dret_i : float
            Value of the retardance i slope (in radians).

        py : float
            Transmission coefficient of the E_y electric field through the polarizer
        """
        if theta_ret_steps.shape != theta_pol_steps.shape or \
                theta_ret_steps.shape != pol_in.shape or \
                theta_ret_steps.shape != ret_in.shape or \
                theta_ret_steps.shape != timeobs.shape:
            raise ValueError('Calibration Sequence step arrays do not have the same shape')

        self.theta_pol_steps = theta_pol_steps * np.pi / 180
        self.theta_ret_steps = theta_ret_steps * np.pi / 180
        self.numsteps = self.theta_pol_steps.shape[0]
        self.py = py
        self.pol_in = pol_in
        self.ret_in = ret_in
        self.dark_in = dark_in
        self.delta_t = timeobs - np.min(timeobs)
        self.t_pol_0 = np.array([t_pol_0], dtype=np.float64)
        self.t_ret_0 = np.array([t_ret_0], dtype=np.float64)
        self.ret_0_h = np.array([ret_0_h], dtype=np.float64)
        self.dret_h = np.array([dret_h], dtype=np.float64)
        self.ret_0_45 = np.array([ret_0_45], dtype=np.float64)
        self.dret_45 = np.array([dret_45], dtype=np.float64)
        self.ret_0_r = np.array([ret_0_r], dtype=np.float64)
        self.dret_r = np.array([dret_r], dtype=np.float64)
        self.sequence_nums = [self.numsteps]
        self.Q_in = Q_in
        self.U_in = U_in
        self.V_in = V_in
        self.I_sys = np.array([I_sys], dtype=np.float64)

    @property
    def numdrawers(self):
        """The number of Drawers (AKA CS's) represented in this object

        Returns
        -------
        int
        """
        return len(self.sequence_nums)

    def __add__(self, other):
        """Concatenate two Calibration Sequences.

        Each Sequence retains its individual CU parameters

        Returns
        -------
        CalibrationSequence
            A new CalibrationSequence object
        """

        output = CalibrationSequence(np.append(self.theta_pol_steps, other.theta_pol_steps) * 180 / np.pi,
                                     np.append(self.theta_ret_steps, other.theta_ret_steps) * 180 / np.pi,
                                     np.append(self.pol_in, other.pol_in),
                                     np.append(self.ret_in, other.ret_in),
                                     np.append(self.dark_in, other.dark_in),
                                     np.append(self.delta_t, other.delta_t))

        output.t_pol_0 = np.append(self.t_pol_0, other.t_pol_0)
        output.t_ret_0 = np.append(self.t_ret_0, other.t_ret_0)
        output.I_sys = np.append(self.I_sys, other.I_sys)
        output.ret_0_h = np.append(self.ret_0_h, other.ret_0_h)
        output.dret_h = np.append(self.dret_h, other.dret_h)
        output.ret_0_45 = np.append(self.ret_0_45, other.ret_0_45)
        output.dret_45 = np.append(self.dret_45, other.dret_45)
        output.ret_0_r = np.append(self.ret_0_r, other.ret_0_r)
        output.dret_r = np.append(self.dret_r, other.dret_r)
        output.sequence_nums = self.sequence_nums + other.sequence_nums
        output.Q_in = self.Q_in
        output.U_in = self.U_in
        output.V_in = self.V_in

        return output

    def init_with_dresser(self, dresser):
        """Initialize CU parameters from a Dresser

        Really all this does is automatically set the CS configuration variables (theta_pol_steps, etc.) and then
        initialize zero arrays of the appropriate length for all of the parameters that will be fit.

        Parameters
        ----------
        dresser : `Data.Dresser`
            Object containing one or more Drawers of SoCCs.
        """
        for attr in ['theta_pol_steps', 'theta_ret_steps', 'pol_in', 'ret_in', 'dark_in', 'delta_t', 'numsteps']:
            setattr(self, attr, getattr(dresser, attr))

        self.py = 0.
        self.Q_in = 0.
        self.U_in = 0.
        self.V_in = 0.
        self.theta_pol_steps *= np.pi / 180
        self.theta_ret_steps *= np.pi / 180
        self.sequence_nums = dresser.drawer_step_list
        self.t_pol_0 = 1 + np.zeros(dresser.numdrawers, dtype=np.float64)
        self.t_ret_0 = 1 + np.zeros(dresser.numdrawers, dtype=np.float64)
        self.ret_0_h = np.zeros(dresser.numdrawers, dtype=np.float64)
        self.dret_h = np.zeros(dresser.numdrawers, dtype=np.float64)
        self.ret_0_45 = np.zeros(dresser.numdrawers, dtype=np.float64)
        self.dret_45 = np.zeros(dresser.numdrawers, dtype=np.float64)
        self.ret_0_r = np.zeros(dresser.numdrawers, dtype=np.float64)
        self.dret_r = np.zeros(dresser.numdrawers, dtype=np.float64)
        self.I_sys = 1. + np.zeros(dresser.numdrawers, dtype=np.float64)

    def load_pars_from_dict(self, params):
        """Update CU Model parameters based on a dictionary of the same

        This doesn't do any checks because it is assumed that `FittingFramework.verify_fit_mode` will have already
        done so.

        Probably don't call this directly

        Parameters
        ----------
        params : dict
            CU Model parameter key: value pairs
        """
        self.Q_in = params['Q_in']
        self.U_in = params['U_in']
        self.V_in = params['V_in']

        for i in range(self.numdrawers):
            self.t_pol_0[i] = params['t_pol_CS{:02n}'.format(i)]
            self.t_ret_0[i] = params['t_ret_CS{:02n}'.format(i)]

            self.I_sys[i] = params['I_sys_CS{:02n}'.format(i)]

            self.ret_0_h[i] = params['ret0h_CS{:02n}'.format(i)]
            self.dret_h[i] = params['dreth_CS{:02n}'.format(i)]
            self.ret_0_45[i] = params['ret045_CS{:02n}'.format(i)]
            self.dret_45[i] = params['dret45_CS{:02n}'.format(i)]
            self.ret_0_r[i] = params['ret0r_CS{:02n}'.format(i)]
            self.dret_r[i] = params['dretr_CS{:02n}'.format(i)]

    def set_py_from_database(self, wavelength):
        """Update the transmission coefficient in the y direction (py)

        Linear interpolation is used to match the input wavelength. py values outside of the database wavelength range
        are simply extended from the min/max database values.
        """
        wave, py = np.loadtxt(pkg_resources.resource_filename('dkist_processing_pac', 'data/py_table.txt'), unpack=True)
        self.py = np.interp(wavelength, wave, py)

        print('{}: py = {:7.6f} at {:4n} nm'.format(tag(), self.py, wavelength))

    @property
    def t_pol(self):
        """Transmission of the polarizer at each step in the CS

        If multiple CS's exist then the transmission will be valid for the entire suite.

        Returns
        -------
        numpy.ndarray
            Array of shape (N,)
        """
        t_pol = np.ones(self.numsteps)
        id1 = 0
        id2 = 0

        for i in range(self.numdrawers):
            id2 += self.sequence_nums[i]
            t_pol[id1:id2] = self.t_pol_0[i]
            id1 = id2

        return t_pol

    @property
    def t_ret(self):
        """Transmission of the retarder at each step in the CS

        If multiple CS's exist then the transmission will be valid for the entire suite.

        Returns
        -------
        numpy.ndarray
            Array of shape (N,)
        """
        t_ret = np.ones(self.numsteps)
        id1 = 0
        id2 = 0

        for i in range(self.numdrawers):
            id2 += self.sequence_nums[i]
            t_ret[id1:id2] = self.t_ret_0[i]
            id1 = id2

        return t_ret

    @property
    def S_in(self):
        """The Stokes vector incident on the Calibration Unit

        NOTE that this does not include the effects of M12. S_in is parametrized via:

        S_in = I_sys * [1, Q_in, U_in, V_in]

        Returns
        -------
        numpy.ndarray
            Array of shape (N,4)
        """
        S_in = np.zeros((self.numsteps, 4), dtype=np.float64)
        id1 = 0
        id2 = 0

        for i in range(self.numdrawers):
            id2 += self.sequence_nums[i]

            S_in[id1:id2] = self.I_sys[i] * np.array([[1., self.Q_in, self.U_in, self.V_in]] * self.sequence_nums[i])
            id1 = id2

        return S_in

    @property
    def ret_h(self):
        """The computed retardance at each step of the CS.

        If multiple CS's exist then ret will be valid for the entire suite.

        Returns
        -------
        numpy.ndarray
            Array of shape (N,)
        """
        ret = np.zeros(self.numsteps)
        id1 = 0
        id2 = 0

        for i in range(self.numdrawers):
            id2 += self.sequence_nums[i]
            ret[id1:id2] = self.ret_0_h[i] + self.dret_h[i] * self.delta_t[id1:id2]
            id1 = id2

        return ret

    @property
    def ret_45(self):
        """The computed retardance at each step of the CS.

        If multiple CS's exist then ret will be valid for the entire suite.

        Returns
        -------
        numpy.ndarray
            Array of shape (N,)
        """
        ret = np.zeros(self.numsteps)
        id1 = 0
        id2 = 0

        for i in range(self.numdrawers):
            id2 += self.sequence_nums[i]
            ret[id1:id2] = self.ret_0_45[i] + self.dret_45[i] * self.delta_t[id1:id2]
            id1 = id2

        return ret

    @property
    def ret_r(self):
        """The computed retardance at each step of the CS.

        If multiple CS's exist then ret will be valid for the entire suite.

        Returns
        -------
        numpy.ndarray
            Array of shape (N,)
        """
        ret = np.zeros(self.numsteps)
        id1 = 0
        id2 = 0

        for i in range(self.numdrawers):
            id2 += self.sequence_nums[i]
            ret[id1:id2] = self.ret_0_r[i] + self.dret_r[i] * self.delta_t[id1:id2]
            id1 = id2

        return ret

    @property
    def pol_mat(self):
        """The set of Mueller matrices for the polarizer.

        Returns
        -------
        numpy.ndarray
            Array of shape (N, 4, 4)
        """
        pol_mat = np.empty((self.numsteps, 4, 4), dtype=np.float64)
        t_pol = self.t_pol

        for i in range(self.numsteps):
            if self.pol_in[i]:
                rot_in = Data.rotation(self.theta_pol_steps[i])
                rot_out = Data.rotation(-self.theta_pol_steps[i])

                pol_mat[i] = rot_out @ Data.polarizer(t_pol[i], self.py) @ rot_in
            else:
                pol_mat[i] = np.diag(np.ones(4, dtype=np.float64))

        return pol_mat

    @property
    def ret_mat(self):
        """The set of Mueller matrices for the retarder

        Returns
        -------
        numpy.ndarray
            Array of shape (N, 4, 4)
        """
        ret_mat = np.empty((self.numsteps, 4, 4), dtype=np.float64)
        t_ret = self.t_ret
        ret_h = self.ret_h
        ret_45 = self.ret_45
        ret_r = self.ret_r

        for i in range(self.numsteps):
            if self.ret_in[i]:
                rot_in = Data.rotation(self.theta_ret_steps[i])
                rot_out = Data.rotation(-self.theta_ret_steps[i])
                ret_mat[i] = rot_out @ Data.elliptical_retarder(t_ret[i], ret_h[i], ret_45[i], ret_r[i]) @ rot_in
            else:
                ret_mat[i] = np.diag(np.ones(4, dtype=np.float64))

        return ret_mat

    @property
    def dark_mat(self):
        dark_mat = np.empty((self.numsteps, 4, 4), dtype=np.float32)
        for i in range(self.numsteps):
            if self.dark_in[i]:
                dark_mat[i] = np.zeros((4,4), dtype=np.float32)
            else:
                dark_mat[i] = np.diag(np.ones(4, dtype=np.float32))

        return dark_mat

    @property
    def CM(self):
        """Set of Mueller matrices for the entire CU.

        Returns
        -------
        numpy.ndarray
            Array of shape (N, 4, 4)
        """

        return self.ret_mat @ self.pol_mat @ self.dark_mat

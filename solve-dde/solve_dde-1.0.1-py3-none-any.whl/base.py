import warnings
from warnings import warn
warnings.simplefilter('always', UserWarning)
import numpy as np
from inspect import isfunction
from scipy.interpolate import CubicHermiteSpline
from .common import EPS, History


def check_arguments(fun, y0, h, t0):
    """Helper function for checking arguments for solve_dde. The function
    return the type of the history given by the user

    Parameters
    ----------
    fun : callable
        Right hand side function of system equations
    y0 :
        Initial conditions
    h : callable or list or tuple or DdeResult
        History data given by user
    t0 : float
        Initial time
    Return
    -------
    fun_wrapped : (callable)
        Wrapper of the right hand side function of system equations
    y0 : ndarray, shape (n,)
        Initial condition
    h_info : str
        The type of history given by user (tuple, function, DdeResult)
    y0_from_h : ndarray, shape (n,)
        values of y0 from the use of h.
    """
    y0 = np.asarray(y0)
    if np.issubdtype(y0.dtype, np.complexfloating):
        raise ValueError("`y0` is complex, but the chosen solver does "
                             "not support integration in a complex domain.")
    else:
        dtype = float
    y0 = y0.astype(dtype, copy=False)

    if(type(h) is tuple):
        h_info = 'from tuple'
        (t_past, y_past, yp_past) = h
        l = []
        for i in range(len(y0)):
            p = CubicHermiteSpline(t_past, y_past[i,:], yp_past[i,:],
                    extrapolate=False)
            l.append(p(t0))
        # as array of cubic hermite spline
        y0_from_h = np.asarray(l)
    elif(isfunction(h)):
        h_info = 'from function'
        y0_from_h = np.asarray(h(t0))
    elif(h.__class__.__name__ == 'DdeResult'):
        h_info = 'from DdeResult'
        if h.sol == None:
            y0_from_h = h.CE_cyclic(t0)
        else:
            y0_from_h = h.sol(t0)
    else:
        h_info = 'from constant'
        y0_from_h = np.asarray(h)
    if y0.ndim != 1:
        raise ValueError("`y0` must be 1-dimensional.")

    def fun_wrapped(t, y, Z):
        return np.asarray(fun(t, y, Z), dtype=dtype)

    # return fun_wrapped, y0, h_n, h_info
    return fun_wrapped, y0, h_info, np.asarray(y0_from_h)

class DdeSolver(object):
    """Base class for DDE solvers.

    Parameters
    ----------
    fun : callable
        Right-hand side of the system $\dot{y} = f(t,y(t),y(t-\tau_1),...,
        y(t-\tau_j)))$. The calling signature is ``fun(t, y, Z)``.
        Here ``t`` is a scalar, ``y`` is the current state and ``Z[:,i]`` the
        state of ``y`` evaluate at time ``$t-\tau_i$`` for $\tau_i=delays[i]$.
    t0 : float
        Initial time.
    t0_l : list
        List of initial times if restarting several time integration.
    before : bool
        After restarting integration, initial time is before last time of the
        previous integration.
    y0 : array_like, shape (n,)
        Initial state.
    h : callable or float or tuple or DdeResult
        Historical state of the differential system
    t_bound : float
        Boundary time --- the integration won't continue beyond it. It also
        determines the direction of the integration.
    delays : list
        List of constant and positive delays of the system
    jumps : list
        Times where discontinuities have to be killed in history, before
        initial time, or during the integration.
    Attributes
    ----------
    n : int
        Number of equations.
    status : string
        Current status of the solver: 'running', 'finished' or 'failed'.
    t_bound : float
        Boundary time.
    h : callable or float or tuple or DdeResult
        history function
    h_info :
        type of history given by user
    direction : float
        Integration direction: +1 or -1.
    t : float
        Current time.
    y : ndarray
        Current state.
    f : ndarray
        Current right hand side
    Z0 : ndarray
        evaluation of Z at initial time.
    t0 : float
        Initial time.
    delays : list
        list of delays
    Ndelays : int
        number of delays
    delayMax : float
        maximal delay
    delayMin : float
        minimal delay
    t_old : float
        Previous time. None if no steps were made yet.
    step_size : float
        Size of the last successful step. None if no steps were made yet.
    tracked_stages : int
        Track discontinuities up to the order of the solver. Default value is
        then tracked_stages equal to the solver's order.
    initDiscont : bool
        is there or not an initial discontinuity at initial time for the current
        integration
    firstInitDiscont : bool
        is there or not an initial discontinuity at initial time for the first
        integration
    nxtDisc : int
        next discontinuity to be kill
    discont : ndarray (nbr_discontinuities,)
        times where discontinuities will be killed
    nfev : int
        Number of the system's rhs evaluations.
    nfailed : int
        Number of rejected evaluations.
    nOverlap : int
        Number of overlapping evaluations of Z
    """
    TOO_SMALL_STEP = "Required step size is less than spacing between numbers."

    def __init__(self, fun, t0, y0, t_bound, h, delays, jumps, tracked_stages,
            warns):

        self._fun, self.y0, self.h_info, self.y0_from_h = check_arguments(fun,
                y0, h, t0)
        self.warns = warns
        self.y = self.y0.copy()
        self.t_old = None
        self.y_old = None
        self.h_previous = None

        self.t0 = t0
        self.t = t0
        self.t_bound = t_bound
        self.n = self.y.size

        # check if there is a discontinuity of order 0, i.e. if
        # 4 time EPS because EPS is machine precision 2.2e-16 ...
        if tracked_stages is not None:
            if self.warns: warn("User choosen to track" +
                    "discontinuities on {} stages".format(tracked_stages))
            self.tracked_stages = tracked_stages
        else:
            self.tracked_stages = self.order

        if(self.h_info != 'from DdeResult'):
            # initi of stats params
            self.nfev = 0
            self.nfailed = 0
            self.nOverlap = 0
            # list of t0 init
            self.data_init = []
            self.firstInitDiscont = False
        else:
            # restart from previous integrations
            # -> recovering previous info of h
            message = "Integration initialized from previous integration."

            self.nfev = h.nfev
            self.nfailed = h.nfailed
            self.nOverlap = h.nOverlap

            self.discont = h.discont
            self.nxtDisc = h.nxtDisc
            if self.nxtDisc < len(self.discont):
                message += " It still need to kill some disconts."
            # adding the new t0 to list
            self.data_init = h.data_init

            if isinstance(self.data_init[0][1], np.ndarray):
                self.firstInitDiscont = True
            else:
                self.firstInitDiscont = False

            if np.isclose(self.t, h.t[-1]):
                # restart at last time of previous integration
                # init t_old
                self.t_old = h.t[-1]
                self.y_old = h.y[:,-1]
                self.h_previous = (h.t[-1] - h.t[-2])
                
                self.before = False
                message += "Starting at t0=h.t[-1]."
            elif(h.t[0] <= self.t and self.t < h.t[-1]):
                arg = np.abs(h.t[h.t < t0] - t0).argmin()
                self.t_old = h.t[h.t < t0][arg]
                self.h_previous = h.t[h.t < t0][arg] - h.t[h.t < t0][arg-1]
                self.y_old = h.y[:,h.t < t0][:, arg]
                self.before = True
                message += "Starting before last tf (={}).".format(h.t[-1]) + \
                        "t0 = {} and t0 prev. integr = {}.".format(t0, h.t[0])
            else:
                #(h.t[0] > self.t or self.t > h.t[-1]):
                print('h.t[0] = {} t0 = {} h.t[-1] = {}'.format(
                    h.t[0], t0, h.t[-1]))
                raise ValueError("t0 (in tspan) > h.t[-1] or t0 < h.t[0]")
            
            if self.warns: warn(message)
        # check initial discont
        if(np.max(np.abs(self.y0_from_h - self.y)) < 100 * EPS):
            self.initDiscont = False
            self.th_dsc = self.yh_dsc = []
            self.data_init.append([self.t,None])
        else:
            if self.warns: warn("Detection of discontinuity of order 0" +
                "at initial time. Tracking discont 1 stage more")
            self.tracked_stages += 1
            self.initDiscont = True
            self.th_dsc = [self.t]
            self.yh_dsc = [self.y]
            self.data_init.append([self.t, self.y])

        if not delays:
            if self.warns:
                warn("no delays given by user, solver will work as solve_ivp")
            self.delayMin = self.delayMax = np.inf
            self.Ndelays = 0
            self.delays = []
        else:
            self.delays = sorted(delays)
            self.Ndelays = len(delays)
            self.delayMin = min(self.delays)
            self.delayMax = max(self.delays)
        # check if negative delays
        if(self.delayMin < 0.0):
            raise ValueError("delay min has negative value")


        # init of the history function used in eval_Z
        self.history = self.init_history_function(h)

        self.direction = np.sign(t_bound - t0) if t_bound != t0 else 1
        self.status = 'running'

        fun_single = self._fun
        def fun(t, y, Z):
            self.nfev += 1
            return self.fun_single(t, y, Z)

        self.fun = fun
        self.fun_single = fun_single
        # init y(t-tau_i) at t0
        self.Z0 = self.eval_Z(self.t)

        if jumps:
            # worth case supposed, if jumps given by user
            # the algo assume discontinuities of order 0
            if self.warns:
                warn("Jumps given by user. Tracking discont 1 stage more")
            self.tracked_stages += 1
            if self.t_oldest > min(jumps) or max(jumps) > self.t_bound:
                raise ValueError("jumps given by user outside time interval" +
                        "t_oldest = {}, tf = {} and jumps = {}".format(
                            self.t_oldest, self.t_bound, jumps))
            # add jumps if if intervall t_oldest t0 in th_dsc + yh_dsc

        # detection of discontinuities which can degradate
        # the accurency of integration
        self.discontDetection(jumps)

        self.f = self.fun(self.t, self.y, self.Z0) # initial value of f(t0,y0,Z0)

        return


    def discontDetection(self, jumps):
        """Discontinuity detection between t0 and tf.
            seen discontDetection_ for the detection implementation

        Parameters
        ----------
        jumps : (list)
            Time in history or in solution where discontinuities occur.
        Return
        -------
        nxtDisc : (int)
            index of the nearst discontinuity
        discont : ndarray, shape (nbr_discontinuities,)
            array with all disconts within the interval of integration

        """
        discont = self.discontDetection_(jumps)
        if self.h_info != 'from DdeResult':
            #  discontinuites detection
            self.discont = discont
            # index to the next discont
            self.nxtDisc = 0
        else:
            discont_sum = sorted(self.discont + discont)
            # remove duplicated values
            self.discont = np.delete(np.asarray(discont_sum),
                                     np.argwhere(
                                        np.ediff1d(discont_sum) < EPS
                                                ) + 1).tolist()
            # update of nxtDisc according to the restart
            self.nxtDisc = np.searchsorted(self.discont, self.t) + 1

    def discontDetection_(self, jumps):
        """ Implementation of the detection algorithm

        Parameters
        ----------
        jumps : (list)
            Time in history or in solution where discontinuities occur.
        Return
        -------
        discont : ndarray, shape (nbr_discontinuities,)
            array with all discont within my interval of integration
        """
        if not self.delays:
            # delays=[], solver used as ivp
            if jumps:
                discont = jumps
            else:
                discont = []
            return discont
        else:
            discont = []
            # transport along time of discontinuities
            transp_discont = np.asarray(self.delays)

            to_transport = [self.t]

            # if jumps and self.h_info == 'from DdeResult':
            if jumps:
                # remove jumps outside tspan
                to_transport += jumps
            if self.h_info == 'from DdeResult' and not self.initDiscont \
                        and not self.firstInitDiscont and not jumps:
                if self.warns:
                    warn("Start from previous integration without any " +
                            "jumps or initial discont")
                # cas where no discont, return 
                return []
            tmp = [(t_ + transp_discont).tolist() for t_ in to_transport]
            tmp_fla = sorted([val for sub_d in tmp for val in sub_d])
            for i in range(1,self.tracked_stages+1):
                discont.append(tmp_fla)
                z = 1 # number of time for delays
                for j in range(i+1,self.tracked_stages+1): # get intermediere discont
                    for k in range(1,self.Ndelays):
                        inter_to_trans = tmp_fla[k:]
                        inter_d = [(t_ + z * transp_discont[:-k]).tolist() for \
                                t_ in inter_to_trans]
                        inter_d_fla = [val for sub_d in inter_d for val in sub_d]
                        discont.append(inter_d_fla)
                        # discont.append(inter_d.tolist())
                    z += 1
                # flatten tmp for add ones more transp_discont
                tmp = [(t_ + transp_discont * (i+1)).tolist() for t_ in to_transport]
                tmp_fla = sorted([val for sub_d in tmp for val in sub_d])
            # flatened the list of list of discont and discont as array
            discont = np.asarray(sorted([val for sub_d in discont
                                             for val in sub_d]))
            # no discontinuities cluster, remove them
            discont = np.delete(discont, np.argwhere(
                                                     np.ediff1d(discont) < EPS
                                                        ) + 1)
            # remove inital time from discont tracking
            discont = discont[discont> self.t0].tolist()
        return discont


    def init_history_function(self, h):
        """ Initialization of the historical function which give historical 
        state of the system according to the type of history `h` given by the 
        user as :
            1. function for simple evaluation
            2. tuple of (t_past, y_past, yp_past) for cubic Hermite
                interpolation with scipy.interpolate.CubicHermiteSpline
            3. constant
            4. previous integration

        Parameters
        ---------
        h :
            History conditions
        Returns
        -------
        h_ : History object
            The History object which is callable. Depending of the h_info
            attribute, the callable return past historical state. Seen History 
            class in common.py for more informations.

        """
        if self.h_info == 'from tuple':
            # unpack of time value, state and state's derivative
            (self.t_past, self.y_past, self.yp_past) = h
            self.t_oldest = self.t_past[0]
            if(self.t_oldest < (self.t0 - self.delayMax)):
                raise("Not enough data in the history to evaluate " +
                        "the entire history interval")
            self.y_oldest = self.y_past[:,0]
            self.yp_oldest = self.yp_past[:,0]
            # construction of the CubicHermiteSpline interp from t, y, yp _past
            data_histo = []
            for k in range(self.n):
                # extrapolation not possible
                p = CubicHermiteSpline(self.t_past, self.y_past[k,:],
                                       self.yp_past[k,:], extrapolate=False)
                data_histo.append(p)

        elif self.h_info == 'from function':
            self.t_oldest = self.t0 - self.delayMax

            self.y_oldest = np.asarray(h(self.t_oldest))
            self.yp_oldest = np.array([0.0 for i in range(self.n)])

            data_histo = h

        elif self.h_info == 'from constant':
            self.t_oldest = self.t0 - self.delayMax

            self.y_oldest = np.asarray(h)
            self.yp_oldest = np.array([0.0 for i in range(self.n)])

            data_histo = h
        elif self.h_info == 'from DdeResult':
            self.solver_old = h

            self.t_oldest = self.t0 - self.delayMax
            # if not dense_ouput=True in last integration -> sol == None
            if self.solver_old.sol == None:
                if self.solver_old.CE_cyclic.t_min > self.t_oldest:
                    raise ValueError("Z_cyclic can not assess all past values."+
                            "Use dense output for restart here")
                data_histo = self.solver_old.CE_cyclic
            else:
                data_histo = self.solver_old.sol
            self.CE = data_histo
        else:
            raise ValueError("wrong initialization of the dde history, " +
                    "h_info = {}".format(self.h_info))

        h_ = History(self.t_oldest, self.t0, data_histo, self.h_info,
                self.th_dsc, self.yh_dsc, self.warns)
        if h_(self.t0).shape != self.y0.shape:
            print('h_(t0) {} y0 {}'.format(h_(self.t0),self.y0))
            print('h_(self.t0).shape {} self.y0.shape {}'.format(
                h_(self.t0).shape, self.y0.shape))
            raise ValueError("Size of returned history and y0 are different")

        return h_


    def eval_Z(self, t_eval):
        """Evaluation of Z, where Z[:,i] is $y(t-\tau_i)$ with
        $\tau_i=delays[i]$. From the value of t-delays[i], Z can by evaluate
        by several ways.

        Parameters
        ----------
        t_eval : float
            Current time.
        Returns
        -------
        Z : ndarray, shape (n,Ndelays)
            Computed values of $y(t_tau_i), \forall i$.
        """
        if not self.delays:
            return None
        Z = np.zeros((self.n,self.Ndelays))
        t_past = t_eval - np.asarray(self.delays)
        for k in range(self.Ndelays):
            t_past_k = t_past[k]
            if t_past_k < self.t0 or np.abs(t_past_k - self.t0) < EPS:
                # case where we using historical data
                Z_k = self.history(t_past_k)

            else:
                if t_past_k < self.t or np.abs(t_past_k - self.t) < 10 * EPS:
                    # use of continous extansion of RK method
                    Z_k = self.CE(t_past_k)
                else:
                    # overlapping
                    sol = self.dense_output()
                    Z_k = sol(t_past_k)
                    # self.nOverlap += 1
            Z[:,k] = Z_k
        return Z

    @property
    def step_size(self):
        if self.t_old is None:
            return None
        else:
            return np.abs(self.t - self.t_old)

    def step(self):
        """Perform one integration step.

        Returns
        -------
        message : string or None
            Report from the solver. Typically a reason for a failure if
            `self.status` is 'failed' after the step was taken or None
            otherwise.
        """
        if self.status != 'running':
            raise RuntimeError("Attempt to step on a failed or finished "
                               "solver.")

        if self.n == 0 or self.t == self.t_bound:
            # Handle corner cases of empty solver or no integration.
            self.t_old = self.t
            self.t = self.t_bound
            message = None
            self.status = 'finished'
        else:
            t = self.t
            success, message = self._step_impl()

            if not success:
                self.status = 'failed'
            else:
                self.t_old = t
                if self.direction * (self.t - self.t_bound) >= 0:
                    self.status = 'finished'

        return message

    def dense_output(self):
        """Compute a local interpolant over the last successful step.

        Returns
        -------
        sol : `DenseOutput`
            Local interpolant over the last successful step.
        """
        if self.t_old is None:
            raise RuntimeError("Dense output is available after a successful "
                               "step was made.")

        if self.n == 0 or self.t == self.t_old:
            # Handle corner cases of empty solver and no integration.
            return ConstantDenseOutput(self.t_old, self.t, self.y)
        else:
            return self._dense_output_impl()

    def _step_impl(self):
        raise NotImplementedError

    def _dense_output_impl(self):
        raise NotImplementedError


class DenseOutput(object):
    """Base class for local interpolant over step made by an ODE solver.

    It interpolates between `t_min` and `t_max` (see Attributes below).
    Evaluation outside this interval is not forbidden, but the accuracy is not
    guaranteed.

    Attributes
    ----------
    t_min, t_max : float
        Time range of the interpolation.
    """
    def __init__(self, t_old, t):
        self.t_old = t_old
        self.t = t
        self.t_min = min(t, t_old)
        self.t_max = max(t, t_old)

    def __call__(self, t):
        """Evaluate the interpolant.

        Parameters
        ----------
        t : float or array_like with shape (n_points,)
            Points to evaluate the solution at.

        Returns
        -------
        y : ndarray, shape (n,) or (n, n_points)
            Computed values. Shape depends on whether `t` was a scalar or a
            1-D array.
        """
        t = np.asarray(t)
        if t.ndim > 1:
            raise ValueError("`t` must be a float or a 1-D array.")
        return self._call_impl(t)

    def _call_impl(self, t):
        raise NotImplementedError


class ConstantDenseOutput(DenseOutput):
    """Constant value interpolator.

    This class used for degenerate integration cases: equal integration limits
    or a system with 0 equations.
    """
    def __init__(self, t_old, t, value):
        super(ConstantDenseOutput, self).__init__(t_old, t)
        self.value = value

    def _call_impl(self, t):
        if t.ndim == 0:
            return self.value
        else:
            ret = np.empty((self.value.shape[0], t.shape[0]))
            ret[:] = self.value[:, None]
            return ret

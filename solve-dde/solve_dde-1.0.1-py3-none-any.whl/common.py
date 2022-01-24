import sys
from itertools import groupby
from warnings import warn
import numpy as np
from inspect import isfunction

EPS = np.finfo(float).eps


def validate_first_step(first_step, t0, t_bound):
    """Assert that first_step is valid and return it."""
    if first_step <= 0:
        raise ValueError("`first_step` must be positive.")
    if first_step > np.abs(t_bound - t0):
        raise ValueError("`first_step` exceeds bounds.")
    return first_step


def validate_max_step(max_step):
    """Assert that max_Step is valid and return it."""
    if max_step <= 0:
        raise ValueError("`max_step` must be positive.")
    return max_step


def warn_extraneous(extraneous):
    """Display a warning for extraneous keyword arguments.

    The initializer of each solver class is expected to collect keyword
    arguments that it doesn't understand and warn about them. This function
    prints a warning for each key in the supplied dictionary.

    Parameters
    ----------
    extraneous : dict
        Extraneous keyword arguments
    """
    if extraneous:
        warn("The following arguments have no effect for a chosen solver: {}."
             .format(", ".join("`{}`".format(x) for x in extraneous)))


def validate_tol(rtol, atol, n):
    """Validate tolerance values."""
    if rtol < 100 * EPS:
        warn("`rtol` is too low, setting to {}".format(100 * EPS))
        rtol = 100 * EPS

    atol = np.asarray(atol)
    if atol.ndim > 0 and atol.shape != (n,):
        raise ValueError("`atol` has wrong shape.")

    if np.any(atol < 0):
        raise ValueError("`atol` must be positive.")

    return rtol, atol


def norm(x):
    """Compute RMS norm."""
    return np.linalg.norm(x) / x.size ** 0.5


def select_initial_step(fun, t0, y0, Z0, f0, direction, order, rtol, atol):
    """Empirically select a good initial step.

    The algorithm is described in [1]_.

    Parameters
    ----------
    fun : callable
        Right-hand side of the system.
    t0 : float
        Initial value of the independent variable.
    y0 : ndarray, shape (n,)
        Initial value of the dependent variable.
    Z0 : ndarray, shape (n,Ndelays)
        Initial values of delayed variable.
    f0 : ndarray, shape (n,)
        Initial value of the derivative, i.e., ``fun(t0, y0)``.
    direction : float
        Integration direction.
    order : float
        Error estimator order. It means that the error controlled by the
        algorithm is proportional to ``step_size ** (order + 1)`.
    rtol : float
        Desired relative tolerance.
    atol : float
        Desired absolute tolerance.

    Returns
    -------
    h_abs : float
        Absolute value of the suggested initial step.

    References
    ----------
    .. [1] E. Hairer, S. P. Norsett G. Wanner, "Solving Ordinary Differential
           Equations I: Nonstiff Problems", Sec. II.4.
    """
    if y0.size == 0:
        return np.inf

    scale = atol + np.abs(y0) * rtol
    d0 = norm(y0 / scale)
    d1 = norm(f0 / scale)
    if d0 < 1e-5 or d1 < 1e-5:
        h0 = 1e-6
    else:
        h0 = 0.01 * d0 / d1

    y1 = y0 + h0 * direction * f0
    f1 = fun(t0 + h0 * direction, y1, Z0)
    d2 = norm((f1 - f0) / scale) / h0

    if d1 <= 1e-15 and d2 <= 1e-15:
        h1 = max(1e-6, h0 * 1e-3)
    else:
        h1 = (0.01 / max(d1, d2)) ** (1 / (order + 1))

    return min(100 * h0, h1)

class History(object):
    """ History class

    Attributes
    ----------
    t_min, t_max : float
        Limits of the intervall of the historical past values.
    repeated_t : bool
        Is here repeated time values in ts which translate discontinuities.
    data_histo : list or callable
        historical data given by user. Several types of data are accepted as :

            data_histo : list
                * If h_info == `from tuple`, then `data_histo` is a list of
                CubicHermiteSpline of length equal to number of the
                integrated variables
                * If h_info == `from constant`, then `data_histo` is
                * If h_info == `from function`, then `data_histo` is a callable
                * If h_info == `from DdeResult`, then `data_histo` is callable

    """
    def __init__(self, t_min, t_max, data_histo, h_info, t_dsc=[], y_dsc=[], warns=True):
        self.warns = warns
        self.data_histo = data_histo
        self.h_info = h_info
        self.n_call = 0
        self.t_min = t_min
        self.t_max = t_max
        self.t_dsc = np.asarray(t_dsc)
        self.y_dsc = np.asarray(y_dsc)

    def _call_single(self, t):
        if self.t_min > t and t > self.t_max \
                and not (np.isclose(self.t_min,t) or np.isclose(self.t_max,t)):
            raise ValueError("Impossible to evaluate historical state as outside intervall")
        self.n_call += 1

        # if `t` is
        if self.t_dsc.size > 0 and np.any(np.abs(self.t_dsc - t) < EPS):
            ind = np.abs(self.t_dsc - t).argmin()
            return self.y_dsc[ind]

        if self.h_info == 'from tuple':
            l = []
            for i in range(len(self.data_histo)):
                l.append(self.data_histo[i](t))
            return np.vstack(l).reshape(len(l),)

        elif self.h_info == 'from function':
            return np.asarray(self.data_histo(t),dtype=float)

        elif self.h_info == 'from constant':
            return np.asarray(self.data_histo, dtype=float)

        elif self.h_info == 'from DdeResult':
            return self.data_histo(t)
        else:
            raise ValueError("`h_info` is not as expected. Evaluation of history is not possible.")


    def __call__(self, t):
        """Evaluate the historical state.

        Parameters
        ----------
        t : float
            Points to evaluate at.

        Returns
        -------
        y : ndarray, shape (n_states,)
            Computed past state. Shape depends on whether `t` is a scalar
        """
        t = np.asarray(t)

        if t.ndim == 0:
            return self._call_single(t)
        # Is there in np.array t some t_dsc ?
        if self.t_dsc.size > 0 and np.any(np.abs(self.t_dsc - t) < EPS):
            if self.warns: warn("Times were discontinuity have been located are in t."
                    "Special management of this case is made")
            idxs = np.argwhere(np.abs(self.t_dsc - t) < EPS)
            # del discont values
            t_ = np.delete(t, idxs)
            order = np.argsort(t_)
            t_histo = t_[order]
        else:
            order = np.argsort(t)
            t_histo = t[order]

        if t_histo.size != 0:
            if self.h_info == 'from tuple':
                l = []
                for i in range(len(self.interp_n)):
                    l.append(self.data_histo[i](t_histo))
                # h = np.vstack(l).reshape(1, len(l))
                h = np.vstack(l).reshape(len(l), 1)

            elif self.h_info == 'from function':
                h = np.zeros((len(self.data_histo(0.0)), len(t_histo)))
                for i in range(len(t_histo)):
                    h[:,i] = np.asarray(self.data_histo(t_histo[i]))

            elif self.h_info == 'from constant':
                data_shape = np.asarray(self.data_histo).reshape(len(self.data_histo), 1)
                h = np.full((len(self.data_histo),len(t_histo)),
                        data_shape)

            elif self.h_info == 'from DdeResult':
                h = self.data_histo(t_histo)
            else:
                raise ValueError("`h_info` is not as expected. Evaluation of history is not possible.")

        else:
            h = np.asarray([])

        if self.t_dsc.size > 0 and np.any(np.abs(self.t_dsc - t) < EPS):
            if t_histo.size != 0:
                t_tmp = t_histo.copy()
                for k in range(len(self.t_dsc)):
                    if (t[0] < self.t_dsc[k] or np.isclose(t[0], self.t_dsc[k])) \
                            and (self.t_dsc[k] < t[-1] or np.isclose(t[-1], self.t_dsc[k])):
                        idx = np.searchsorted(t_tmp, self.t_dsc[k]) + 1
                        t_tmp = np.insert(t_tmp, idx, self.t_dsc[k])
                        h = np.insert(h, idx, self.y_dsc[k].reshape(len(self.y_dsc[k]), 1), axis=1)
            else:
                for k in range(len(self.t_dsc)):
                    if (t[0] < self.t_dsc[k] or np.isclose(t[0], self.t_dsc[k])) \
                            and (self.t_dsc[k] < t[-1] or np.isclose(t[-1], self.t_dsc[k])):
                        h = np.append(h, [self.y_dsc[k]]).reshape(len(self.y_dsc[k]), 1)
        return h

class ContinuousExt(object):
    """Continuous extension of the solution.

    It is organized as a collection of `DenseOutput` objects which represent
    local interpolants. It provides an algorithm to select a right interpolant
    for each given point.

    The interpolants cover the range between `t_min` and `t_max` (see
    Attributes below).

    When evaluating at a breakpoint (one of the values in `ts`) a segment with
    the lower index is selected.

    Parameters
    ----------
    ts : array_like, shape (n_segments + 1,)
        Time instants between which local interpolants are defined. Must
        be strictly increasing or decreasing (zero segment with two points is
        also allowed).
    interpolants : list of history and DenseOutput with respectively 1 and
        n_segments-1 elements
        Local interpolants. An i-th interpolant is assumed to be defined
        between ``ts[i]`` and ``ts[i + 1]``.
    ys : array_like, shape (n_segments + 1,)
        solution associated to ts. Needed to get solution values when
        discontinuities occur
    Attributes
    ----------
    t_min, t_max : float
        Time range of the interpolation.
    repeated_t : bool
        Is here repeated time values in ts which translate discontinuities.
    t_dsc : list
        Times where there are discontinuies.
    y_dsc : list
        Values at discontinuities.
    n_segments : int
        Number of interpolant.
    n : int
        Number of equations.
    """

    def __init__(self, ts, interpolants, ys, t_dsc=[], y_dsc=[], warns=True):
        self.t_dsc = np.asarray(t_dsc)
        self.y_dsc = np.asarray(y_dsc)
        self.warns = warns
        ts = np.asarray(ts)
        d = np.diff(ts)

        if not ((ts.size == 2 and ts[0] == ts[-1]) or
                np.all(d > 0) or np.all(d < 0)):
            print('ts', ts, 'd', d)

            print('np.all(d > 0)', np.all(d > 0))
            raise ValueError("`ts` must be strictly increasing or decreasing.")

        self.n_segments = len(interpolants)
        self.n = len(ys[0])

        if ts.shape != (self.n_segments + 1,) or len(ts) != len(ys):
            raise ValueError("Numbers of time stamps and interpolants "
                             "don't match.")
        if len(ts) != len(ys):
            raise ValueError("number of ys and ts don't match.")

        self.ts = ts
        self.interpolants = interpolants
        if ts[-1] >= ts[0]:
            self.t_min = ts[0]
            self.t_max = ts[-1]
            self.ascending = True
            self.ts_sorted = ts
        else:
            self.t_min = ts[-1]
            self.t_max = ts[0]
            self.ascending = False
            self.ts_sorted = ts[::-1]

    def _call_single(self, t):
        if self.t_min > t or t > self.t_max\
                and not (np.isclose(self.t_min,t) or np.isclose(self.t_max,t)):
            raise ValueError('t not in interpolation time intervall')
        # Here we preserve a certain symmetry that when t is in self.ts,
        # then we prioritize a segment with a lower index.

        # if discont case + t is a discont
        if self.t_dsc.size > 0 and np.any(np.abs(self.t_dsc - t) < EPS):
            # return the discont value at t discont
            ind = np.abs(self.t_dsc - t).argmin()
            return self.y_dsc[ind]

        if self.ascending:
            ind = np.searchsorted(self.ts_sorted, t, side='left')
        else:
            ind = np.searchsorted(self.ts_sorted, t, side='right')

        segment = min(max(ind - 1, 0), self.n_segments - 1)
        if not self.ascending:
            segment = self.n_segments - 1 - segment

        return self.interpolants[segment](t)

    def __call__(self, t):
        """Evaluate the solution.

        Parameters
        ----------
        t : float or array_like with shape (n_points,)
            Points to evaluate at.

        Returns
        -------
        y : ndarray, shape (n_states,) or (n_states, n_points)
            Computed values. Shape depends on whether `t` is a scalar or a
            1-D array.
        """
        t = np.asarray(t)
        if t.ndim == 0:
            return self._call_single(t)
        elif self.t_min > t[0] or t[-1] > self.t_max\
                and not (np.isclose(self.t_min,t[0]) or
                        np.isclose(self.t_max,t[-1])):
            raise ValueError('The bounds of t array not in interpolation ' +
                    'time intervall. tmin = %s tmax %s t[0] = %s t[-1] = %s' %
                    (self.t_min, self.t_max, t[0], t[-1]))
        isDiscontIn_t = []
        idxs = []
        # check if discont are in t array and locate where
        for i in range(len(self.t_dsc)):
            if np.any(np.abs(t - self.t_dsc[i]) < EPS):
                idxs.append(np.abs(t - self.t_dsc[i]).argmin())
                isDiscontIn_t.append(True)
            else:
                isDiscontIn_t.append(False)

        if any(isDiscontIn_t):
            if self.warns: warn("Discontinuities moments are present in t.")
            t = np.delete(t, idxs)

        order = np.argsort(t)
        reverse = np.empty_like(order)
        reverse[order] = np.arange(order.shape[0])
        t_sorted = t[order]


        # See comment in self._call_single.
        if self.ascending:
            segments = np.searchsorted(self.ts_sorted, t_sorted, side='left')
        else:
            segments = np.searchsorted(self.ts_sorted, t_sorted, side='right')
        segments -= 1
        segments[segments < 0] = 0
        segments[segments > self.n_segments - 1] = self.n_segments - 1
        if not self.ascending:
            segments = self.n_segments - 1 - segments

        ys = []
        group_start = 0
        for segment, group in groupby(segments):

            group_end = group_start + len(list(group))

            y = self.interpolants[segment](t_sorted[group_start:group_end])
            ys.append(y)
            group_start = group_end
        # print('self.interpolants[0]', self.interpolants[0])
        # print('ys[0].shape', ys[0].shape, 'ys[1].shape', ys[1].shape)
        ys = np.hstack(ys)
        ys = ys[:, reverse]

        # Insertion of discontinuities
        if any(isDiscontIn_t):
            t_tmp = t_sorted.copy()
            for k in range(len(self.t_dsc)):
                if isDiscontIn_t[k]:
                    idx = np.searchsorted(t_tmp, self.t_dsc[k])
                    t_tmp = np.insert(t_tmp, idx, self.t_dsc[k])
                    ys = np.insert(ys, idx, self.y_dsc[k], axis=1)
        return ys

class ContinuousExtCyclic(object):
    """ Cyclic collection of dense ouput list and the corresponding times list.
    Informations only in time intervall [t, t-delayMax] are keeped. This class
    is written from ContinuousExtension.
    A cyclic management of data permit a better code efficency

    The interpolants cover the range between `t_min = t_current - delayMax`
    and `t_current` where t_current is the current integration time
    (see Attributes below).

    When evaluating at a breakpoint (one of the values in `ts`) a segment with
    the lower index is selected.

    Parameters
    ----------
    t0 : float
        Initial time
    delayMax : float
        Maximal delay
    history : History object
        History object
    t_dsc : list
        The times of jumps
    y_dsc : list
        The values of y at t_dsc

    Attributes
    ----------
    ts : array_like, shape (n_segments + 1,)
        Time instants between which local interpolants are defined. Must
        be strictly increasing or decreasing (zero segment with two points is
        also allowed).
    interpolants : list of history and DenseOutput with respectively 1 and
        n_segments-1 elements
        Local interpolants. An i-th interpolant is assumed to be defined
        between ``ts[i]`` and ``ts[i + 1]``.
    t_min, t_max : float
        Time range of the interpolation.
    n_segments : int
        Number of interpolant.
    """

    def __init__(self, t0, delayMax, history, t_dsc=[], y_dsc=[]):
        self.t_dsc = np.asarray(t_dsc)
        self.y_dsc = np.asarray(y_dsc)
        self.delayMax = delayMax
        self.t0 = t0
        self.t_min = self.t0 - self.delayMax
        self.t_max = self.t0
        self.ts = [self.t_min, self.t0]
        if history.__class__.__name__ not in ('History','ContinuousExt', 'ContinuousExtCyclic'):
            raise TypeError('History not History object')
        if self.t_dsc.size > 0:
            if self.t_dsc.shape[0] != self.y_dsc.shape[0]:
                print('self.t_dsc %s self.y_dsc %s' % (self.t_dsc, self.y_dsc.shape))
                raise ValueError('t_dsc and y_dsc have not same shape')
        self.interpolants = [history]
        self.n_segments = 1

    def update(self,t,sol):
        """ Update the cyclic storage of past values by adding new time and
            continous extension

        Parameters
        ----------
        t : float or list
            New time points to add in self.ts
        sol : callable or list of callable
            New sol in intervall between self.ts[-1] et t

        Returns
        -------
        self.ts : list
            Update of self.ts
        self.interpolants : list
            Update of self.interpolants
        """
        if isinstance(t,list) and isinstance(sol,list):
            if not np.isclose(t[-1], self.t0):
                raise ValueError('Problem of time continuity')
            self.ts = t
            self.interpolants = sol
            self.n_segments = len(self.interpolants)
        else:
            self.t_min = t - self.delayMax
            self.t_max = t
            self.ts.append(t)
            self.interpolants.append(sol)
            self.n_segments += 1

        self.cleanUp()
        if len(self.ts) != self.n_segments + 1:
            raise ValueError("Numbers of time stamps and interpolants don't match.")
        if not np.all(np.diff(self.ts) > 0):
             raise ValueError("`ts` must be strictly increasing")

    def cleanUp(self):
        """Remove times and callable function sol (continous extension) when
        not anymore useful. Useful informations for past values are in the
        intervall [t_current-delayMax, t_current]

        Returns
        -------
        self.ts : list
            Update of self.ts
        self.interpolants : list
            Update of self.interpolants
        self.n_segments : int
            Update of self.n_segments
        """
        idx = [x for x, val in enumerate(self.ts) if val < self.t_min]
        to_rm = []
        for i in idx:
            if not (self.ts[i] < self.t_min and self.t_min < self.ts[i+1]):
                to_rm.append(i)
        # reverse the to-rm list for not throw off the subsequent indexes.
        for i in sorted(to_rm, reverse=True):
            del self.ts[i], self.interpolants[i]
        self.n_segments = len(self.interpolants)

    def _call_single(self, t):

        if self.t_min > t and t > self.t_max \
                and  not (np.isclose(self.t_min,t) or np.isclose(self.t_max,t)):
            print('t_min %s t%s t_max %s' % (self.t_min, t, self.t_max))
            raise ValueError('t not in delayed state time intervall')

        if self.t_dsc.size > 0 and np.any(np.abs(self.t_dsc - t) < EPS):
            ind = np.abs(self.t_dsc - t).argmin()
            return self.y_dsc[ind]
        else:
            ind = np.searchsorted(self.ts, t, side='left')
            segment = min(max(ind - 1, 0), self.n_segments - 1)
            return self.interpolants[segment](t)

    def __call__(self, t):
        """Evaluate the solution.

        Parameters
        ----------
        t : float
            Points to evaluate at.

        Returns
        -------
        y : ndarray, shape (n_states,)
            Computed values. Shape depends on whether `t` is a scalar
        """
        t = np.asarray(t)
        if t.ndim == 0:
            return self._call_single(t)
        else:
            raise ValueError('t must be array where ndim == 0')

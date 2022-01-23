import sys

try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

if framework:
    print('Loading math utility functions...')

from omfit_classes.utils_base import *
from omfit_classes.utils_base import _available_to_user_math

import numpy as np
import scipy
from scipy import interpolate, optimize, integrate, ndimage
from scipy.interpolate.polyint import _Interpolator1D
from scipy.ndimage import _ni_support
import functools

# --------------------------------
# numpy error handling decorators
# --------------------------------
def np_errors(**kw):
    context = np.errstate(**kw)

    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kw):
            with context:
                return f(*args, **kw)

        return decorated

    return decorator


np_ignored = np_errors(all='ignore')
np_raised = np_errors(all='raise')
np_printed = np_errors(all='print')
np_warned = np_errors(all='warn')

# -------
# arrays
# -------
@_available_to_user_math
def get_array_hash(y):
    """
    Get the hash for an array.
    A hash is an fixed sized integer that identifies a particular value,
    comparing this integer is faster than comparing the whole array
    (if you already have it stored).

    Example::

        y1 = np.arange(3)
        y2 = np.arange(3) + 1
        assert(get_array_hash(y1) == get_array_hash(y2)) # will raise an error

    :param y: np.ndarray.
    :return: hash.

    """
    return bytes(y).__hash__()


@_available_to_user_math
def ismember(A, B):
    """
    Mimics the Matlab ismember() function to look for occurrences of A into B

    :param A: number or list/array

    :param B: number or list/array

    :return: returns lia, locb lists.
        lia: returns 'True' where the data in A is found in B and 'False' elsewhere.
        locb: contains the lowest index in B for each value in A that is a member of B.
        while it contains 'None' elsewhere (where A is not a member of B)
    """
    bind = {}
    tmp = {}

    a = np.atleast_1d(A)
    b = np.atleast_1d(B)

    for i, elt in enumerate(a):
        if elt in b:
            tmp[elt] = True

    for i, elt in enumerate(b):
        if elt not in bind:
            bind[elt] = i

    lia = [tmp.get(itm, False) for itm in a]
    locb = [bind.get(itm, None) for itm in a]

    return lia, locb  # two lists in output


@_available_to_user_math
def map1d(vecfun, ndarr, axis=-1, args=[], **kwargs):
    r"""
    Map a vector operation to a single axis of any multi-dimensional array.

    input:
        :param vecfun: A function that takes a 1D vector input.
        :param ndarr: A np.ndarray.
        :param axis: Axis of the array on which vecfun will operate.
        :param \*args: Additional arguments passed to vecfun.
        :param \**kwargs: Additional key word arguments are also passed to vecfun.

    output:
        A new array of same dimensionality as ndarr.

    """
    # don't modify original array
    nda = copy.copy(ndarr)

    if len(nda.shape) == 1:
        nda = vecfun(nda, *args, **kwargs)
    else:
        # move axis of interest to the back
        nda = nda.swapaxes(axis, -1)
        newshape = list(nda.shape)
        # flatten all other dimensions
        nda = nda.reshape(-1, newshape[-1])
        # apply vector operation
        for i, v in enumerate(nda):
            nda[i] = vecfun(v, *args, **kwargs)
        # reform nD array
        newshape[-1] = -1
        nda = nda.reshape(newshape)
        # put axis back where it was
        nda = nda.swapaxes(-1, axis)

    return nda


@_available_to_user_math
def uniform_resample_2D_line(X0, Y0, n):
    """
    Resampling of 2D line with uniform distribution of points along the line

    :param X0: input x coordinates of 2D path

    :param Y0: input y coordinates of 2D path

    :param n: number of points for output 2d path

    :return: tuple of x,y uniformly resampled path
    """
    X01 = np.hstack((X0[-1], X0))
    Y01 = np.hstack((Y0[-1], Y0))
    L0 = np.cumsum(np.sqrt(np.diff(X01) ** 2 + np.diff(Y01) ** 2))
    l = np.linspace(min(L0), max(L0), n)
    x = interpolate.interp1d(L0, X0)(l)
    y = interpolate.interp1d(L0, Y0)(l)
    return x, y


@_available_to_user_math
def stepwise_data_index(y, broaden=0):
    """
    This function returns the indices that one must use
    to reproduce the step-wise data with the minimum number
    of points. In the ascii-art below, it returns the indices
    of the crosses. The original data can then be reproduced
    by nearest-neighbor interpolation::


         Y ^
           |              x.....x
           |        x....x
           |  x....x             x......x
           |
           0-----------------------------> X

    Hint: can also be used to compress linearly varying data::

          i = stepwise_data_index(np.gradient(y))

    The original data can then be reproduced by linear interpolation.

    :param y: input array

    :param broaden: return `broaden` points around the x's

    :return: indices for compression
    """

    y = np.abs(np.gradient(y))
    if broaden > 1:
        y = smooth(y, int(broaden // 2) * 2 + 1)
    return np.unique([0] + tolist(np.where(y)[0]) + [len(y) - 1])


def pack_points(n, x0, p):
    """
    Packed points distribution between -1 and 1

    :param n: number of points

    :param x0: pack points around `x0`, a float between -1 and 1

    :param p: packing proportional to `p` factor >0

    :return: packed points distribution between -1 and 1
    """
    x = np.linspace(-1, 1, n)
    y = np.sinh((x - x0) * p)
    y = (y - min(y)) / (max(y) - min(y)) * (max(x) - min(x)) + min(x)
    return y


def simplify_polygon(x, y, tolerance=None, preserve_topology=True):
    """
    Returns a simplified representation of a polygon

    :param x: array of x coordinates

    :param y: array of y coordinates

    :param tolerance: all points in the simplified object will be within the tolerance distance of the original geometry
        if tolerance is None, then a tolerance guess is returned

    :param preserve_topology: by default a slower algorithm is used that preserves topology

    :return: x and y coordinates of simplified polygon geometry
        if tolerance is None, then a tolerance guess is returned
    """
    if tolerance is None:
        dd = np.sqrt(np.gradient(x) ** 2 + np.gradient(y) ** 2)
        dd = dd[dd > 0]
        tolerance = np.median(dd) / 100.0
        return tolerance
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=ImportWarning, message="can't resolve package*")
        from shapely.geometry import Polygon
    polygon = Polygon(zip(x, y))
    polygon = polygon.simplify(tolerance=tolerance, preserve_topology=preserve_topology)
    tmp = np.array(list(polygon.exterior.coords))
    return tmp[:, 0], tmp[:, 1]


# -------
# iterables
# -------


def torecarray(data2D, names=None):
    """
    Converts a 2D list of lists, or a dictionary of dictionaries with 1d elements to a recarray

    :param data2D: 2D input data

    :param names: recarray columns names

    :return: recarray
    """
    if isinstance(data2D, dict):
        if isinstance(list(data2D[list(data2D.keys())[0]].keys())[0], dict):
            data2D = dictdict_2_dictlist(data2D)
        names = list(data2D.keys())
        data2D = [data2D[k] for k in data2D]

    dtype = []
    for k, name in enumerate(names):
        dtype.append((name, np.array(data2D[k]).dtype))

    M = np.recarray(len(data2D[0]), dtype=dtype)
    for k, item in enumerate(names):
        M[item][:] = data2D[k][:]
    return M


def dictdict_2_dictlist(data):
    """
    dictionary of dictionaries with 1d elements, to dictionary of lists

    :param data: dictionary of dictionaries

    :return: dictionary of dictionaries
    """
    col = set()
    for k in data:
        item = data[k]
        col.update(list(map(str, list(item.keys()))))
    col = sorted(list(col))

    data = {}
    for c in col:
        data[c] = []
        for k in data:
            item = data[k]
            if c in list(item.keys()):
                data[c].append(item[c])
            else:
                data[c].append(np.nan)

    for c in col:
        data[c] = np.array(data[c])
    return data


@_available_to_user_math
def flatten_iterable(l):
    """
    flattens iterable of iterables structures

    :param l: input iterable structure

    :return: generator with items in the structure
    """
    import collections

    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, str):
            for sub in flatten_iterable(el):
                yield sub
        else:
            yield el


@_available_to_user_math
def lists_loop_generator(*argv, **kwargs):
    r"""
    This function generates a list of items combining the entries from multiple lists

    :param \*args: multiple 1D lists (of equal length, or of 0 or 1 element length)

    :param permute: output all element permutations

    :return:  list of items combining the entries from multiple lists

    Examples::

        shots = 123
        times = [1,2]
        runs = 'a01'
        shots, times, runs = lists_loop_generator(shots,times,runs)
        for shot, time, run in zip(shots,times,runs):
            myCode(shot,time,run)

        shots = [123,446]
        times = [1,2]
        runs = 'a01'
        shots, times, runs = lists_loop_generator(shots,times,runs)

    now permute will return lists of length 2 or length 4
    """

    import itertools

    # Define inputs and make sure that they are type list
    inList = list(argv)
    for i, arg in enumerate(inList):
        if not isinstance(arg, list):
            inList[i] = [arg]

    # Get permutation keyword argument
    permute = kwargs.pop('permute', False)

    # Check the lengths
    n = []
    for el in inList:
        n.append(len(el))

    # Check if length of all elements are equal
    lens = len(set(iter(n)))
    len_equal = lens <= 1

    myList = []
    if len_equal and not permute:
        # Single values or all flat lists to zip
        myList = inList
    elif len_equal and permute:
        # All flat lists and permuteuting before zip')
        myTuples = list(itertools.product(*inList))
        for i in range(len(inList)):
            myList.append([item[i] for item in myTuples])
    elif not len_equal and not permute:
        # Only two allowable options: list has max(n) elements or list is 0 or 1D
        for i, el in enumerate(inList):
            if len(el) == np.max(n):
                # List element has appropriate number of entries
                continue
            elif len(el) == 1:
                # List element is single; duplicating
                inList[i] = el * np.max(n)
            else:
                printe('Error, list element is neither the same as others, nor 1D')
                raise OMFITexception('Inputs error')
        myList = inList
    elif not len_equal and permute:
        # Permuting before zip
        myTuples = list(itertools.product(*inList))
        for i in range(len(inList)):
            myList.append([item[i] for item in myTuples])

    return myList


# Uncertainties helpers
def is_uncertain(var):
    """
    :param var: Variable or array to test

    :return: True if input variable or array is uncertain
    """

    from builtins import any
    import uncertainties

    def _uncertain_check(x):
        return isinstance(x, uncertainties.core.AffineScalarFunc)

    if isinstance(var, str):
        return False
    elif np.iterable(var) or isinstance(var, np.ndarray):  # isinstance needed for 0D arrays from squeeze
        tmp = np.array(var)
        if tmp.dtype not in ['O', 'object']:
            return False
        else:
            # the argument of any is a generator object (using a list slows things down)
            return any(_uncertain_check(x) for x in tmp.flat)
    else:
        return _uncertain_check(var)


# Modify uncertainties.unumpy.core.wrap_array_func to give unc_tag keyword holding
# repr of uncertainty Variable being varied to the function being called
def wrap_array_func(func):
    from uncertainties.unumpy.core import array_derivative
    import uncertainties.core as uncert_core

    # !!! This function is not used in the code, and is also not
    # in the user guide: should it be promoted?
    #
    # !!! The implementation seems superficially similar to
    # !!! uncertainties.core.wrap(): is there code/logic duplication
    # !!! (which should be removed)?
    """
    Return a version of the function func() that works even when
    func() is given a NumPy array that contains numbers with
    uncertainties, as first argument.
    This wrapper is similar to uncertainties.core.wrap(), except that
    it handles an array argument instead of float arguments, and that
    the result can be an array.
    However, the returned function is more restricted: the array
    argument cannot be given as a keyword argument with the name in
    the original function (it is not a drop-in replacement).
    func -- function whose first argument is a single NumPy array,
    and which returns a NumPy array.
    """

    def wrapped_func(arr, *args, **kwargs):
        # Nominal value:
        arr_nominal_value = unumpy.nominal_values(arr)
        func_nominal_value = func(arr_nominal_value, *args, **kwargs)

        # The algorithm consists in numerically calculating the derivatives
        # of func:

        # Variables on which the array depends are collected:
        variables = set()
        for element in arr.flat:
            # floats, etc. might be present
            if isinstance(element, uncert_core.AffineScalarFunc):
                variables |= set(element.derivatives.keys())

        # If the matrix has no variables, then the function value can be
        # directly returned:
        if not variables:
            return func_nominal_value

        # Calculation of the derivatives of each element with respect
        # to the variables.  Each element must be independent of the
        # others.  The derivatives have the same shape as the output
        # array (which might differ from the shape of the input array,
        # in the case of the pseudo-inverse).
        derivatives = np.vectorize(lambda _: {})(func_nominal_value)
        for var in variables:

            # A basic assumption of this package is that the user
            # guarantees that uncertainties cover a zone where
            # evaluated functions are linear enough.  Thus, numerical
            # estimates of the derivative should be good over the
            # standard deviation interval.  This is true for the
            # common case of a non-zero standard deviation of var.  If
            # the standard deviation of var is zero, then var has no
            # impact on the uncertainty of the function func being
            # calculated: an incorrect derivative has no impact.  One
            # scenario can give incorrect results, however, but it
            # should be extremely uncommon: the user defines a
            # variable x with 0 standard deviation, sets y = func(x)
            # through this routine, changes the standard deviation of
            # x, and prints y; in this case, the uncertainty on y
            # might be incorrect, because this program had no idea of
            # the scale on which func() is linear, when it calculated
            # the numerical derivative.

            # The standard deviation might be numerically too small
            # for the evaluation of the derivative, though: we set the
            # minimum variable shift.

            shift_var = max(var._std_dev, 1e-8 * abs(var._nominal_value))
            # An exceptional case is that of var being exactly zero.
            # In this case, an arbitrary shift is used for the
            # numerical calculation of the derivative.  The resulting
            # derivative value might be quite incorrect, but this does
            # not matter as long as the uncertainty of var remains 0,
            # since it is, in this case, a constant.
            if not shift_var:
                shift_var = 1e-8

            # Shift of all the elements of arr when var changes by shift_var:
            shift_arr = array_derivative(arr, var) * shift_var

            # Origin value of array arr when var is shifted by shift_var:
            shifted_arr_values = arr_nominal_value + shift_arr
            ### OMFIT addition
            kwargs['unc_tag'] = repr(var)
            ### End OMFIT addition
            func_shifted = func(shifted_arr_values, *args, **kwargs)
            numerical_deriv = (func_shifted - func_nominal_value) / shift_var

            # Update of the list of variables and associated
            # derivatives, for each element:
            for (derivative_dict, derivative_value) in list(zip(derivatives.flat, numerical_deriv.flat)):

                if derivative_value:
                    derivative_dict[var] = derivative_value

        # numbers with uncertainties are built from the result:
        return np.vectorize(uncert_core.AffineScalarFunc)(func_nominal_value, np.vectorize(uncert_core.LinearCombination)(derivatives))

    wrapped_func = uncert_core.set_doc(
        """\
    Version of %s(...) that works even when its first argument is a NumPy
    array that contains numbers with uncertainties.
    Warning: elements of the first argument array that are not
    AffineScalarFunc objects must not depend on uncert_core.Variable
    objects in any way.  Otherwise, the dependence of the result in
    uncert_core.Variable objects will be incorrect.
    Original documentation:
    %s"""
        % (func.__name__, func.__doc__)
    )(wrapped_func)

    # It is easier to work with wrapped_func, which represents a
    # wrapped version of 'func', when it bears the same name as
    # 'func' (the name is used by repr(wrapped_func)).
    wrapped_func.__name__ = func.__name__

    return wrapped_func


def chunks(l, n):
    """Yield successive n-sized chunks from l"""
    for i in range(0, len(l), n):
        yield l[i : i + n]


@_available_to_user_math
def unsorted_unique(x):
    """
    Find the unique elements of an array
    The order of the elements is according to their first appearance

    :param x: input array or list

    :return: unique array or list (depending on whether the input was an array or a list)
    """
    tmp = []
    for k in x:
        if k not in tmp:
            tmp.append(k)
    if isinstance(x, np.ndarray):
        return np.array(tmp)
    else:
        return tmp


@_available_to_user_math
def closestIndex(my_list, my_number=0):
    """
    Given a SORTED iterable (a numeric array or list of numbers) and a numeric scalar my_number, find the index of the
    number in the list that is closest to my_number

    :param my_list: Sorted iterable (list or array) to search for number closest to my_number

    :param my_number: Number to get close to in my_list

    :return: Index of my_list element closest to my_number

    :note: If two numbers are equally close, returns the index of the smallest number.
    """

    if not hasattr(my_list, '__iter__'):
        raise TypeError("closestIndex() in utils_math.py requires an iterable as the first argument. Got " "instead: {:}".format(my_list))

    if not is_numeric(my_number):
        if hasattr(my_number, '__iter__') and len(my_number) == 1 and is_numeric(my_number[0]):
            printw(
                'Warning: closestIndex got a len()=1 iterable instead of a scalar for my_number. my_number[0] will '
                'be used, but please input a scalar next time.'
            )
            # Before, the function would run without an error if given a one element array, but it would not return the
            # correct answer.
            my_number = my_number[0]
            printd('my_number is now {:}'.format(my_number))
        else:
            raise TypeError(
                "closestIndex() in utils_math.py requires a numeric scalar as the second argument. Got " "instead: {:}".format(my_number)
            )

    import bisect

    pos = bisect.bisect_left(my_list, my_number)
    if pos == 0:
        return 0
    if pos == len(my_list):
        return pos - 1
    before = pos - 1
    after = pos
    if my_list[after] - my_number < my_number - my_list[before]:
        return pos
    else:
        return pos - 1


@_available_to_user_math
def order_axes(M, order):
    """
    arbitrary sort axes of a multidimensional array

    :param M: input multidimensional array

    :param order: integers with list of axes to be ordered

    :return: M with reordered axes
    """
    source = ''.join([chr(k + 65) for k in sorted(order)])
    dest = ''.join([chr(k + 65) for k in order])
    return np.einsum(source + '->' + dest, M)


# -----------
# binning
# -----------
@_available_to_user_math
def qgriddata(px, py, data, X, Y, func=np.sum, fill=np.nan):
    """
    :param px:

    :param py:

    :param data:

    :param X:

    :param Y:

    :param func:

    :return:
    """
    if len(X.shape) == 2:
        x = X[1, :]
    else:
        x = X
    nx = len(x)

    if len(Y.shape) == 2:
        y = Y[1, :]
    else:
        y = Y
    ny = len(y)

    indx = interpolate.interp1d(x, np.arange(nx) * 1.0, kind='nearest', bounds_error=False)(px)
    indy = interpolate.interp1d(y, np.arange(ny) * 1.0, kind='nearest', bounds_error=False)(py)

    res = np.zeros(nx * ny)
    res[:] = fill
    ind = np.array(indx + indy * ny, np.int64)

    tmp = {}
    for kd, ki in enumerate(ind):
        if ki not in tmp:
            tmp[ki] = [data[kd]]
        else:
            tmp[ki].append(data[kd])
    for ki in tmp:
        res[ki] = func(tmp[ki])

    res = res.reshape((nx, ny))
    return res


# -----------
# interpolation
# -----------
class RectBivariateSplineNaN:
    def __init__(self, Z, R, Q, *args, **kw):
        tmp = Q.copy()
        bad = np.isnan(tmp)
        self.thereAreNaN = False
        if bad.any():
            self.thereAreNaN = True
            tmp[bad] = 0
            self.mask = interpolate.RectBivariateSpline(Z, R, bad, kx=1, ky=1)
        self.spline = interpolate.RectBivariateSpline(Z, R, tmp, *args, **kw)

    def __call__(self, *args):
        tmp = self.spline(*args)
        if self.thereAreNaN:
            mask = self.mask(*args)
            tmp[mask > 0.01] = np.nan
        return tmp

    def ev(self, *args):
        tmp = self.spline.ev(*args)
        if self.thereAreNaN:
            mask = self.mask.ev(*args)
            tmp[mask > 0.01] = np.nan
        return tmp


@_available_to_user_math
class interp1e(interpolate.interp1d):
    """
    Shortcut for scipy.interpolate.interp1d with fill_value='extrapolate' and bounds_error=False as defaults
    """

    __doc__ += (
        interpolate.interp1d.__doc__.replace('\n    ----------\n', ':\n')
        .replace('\n    -------\n', ':\n')
        .replace('\n    --------\n', ':\n')
    )

    def __init__(self, x, y, *args, **kw):
        kw.setdefault('fill_value', 'extrapolate')
        kw.setdefault('bounds_error', False)
        interpolate.interp1d.__init__(self, x, y, *args, **kw)


@_available_to_user_math
class interp1dPeriodic:
    """
    1D linear interpolation for periodic functions
    """

    def __init__(self, t, y, *args, **kw):
        """
        :param t: array
            Independent variable: Angle (rad). Doesn't have to be on any particular interval as it will be unwrapped.
        :param y: array matching length of t
            Dependent variable: values as a function of t
        """
        self.t_other, ti = np.unique(np.unwrap(t), return_index=True)
        if self.t_other[0] > self.t_other[1]:
            self.t_other = -self.t_other
        self.tckp = interpolate.splrep(self.t_other, y[ti], k=1, per=1)

    def __call__(self, t_self, *args):
        """
        :param t_self: float or array
            New basis for independent variable: Angle (rad). Doesn't have to be on any particular interval.
        :return: float or array matching length of t_self
            Interpolated values at new t values specified by t_self
        """
        if np.iterable(t_self):
            t_self = np.unwrap(t_self)
            if t_self[0] < t_self[1]:
                t_self = -t_self
        tmp = interpolate.splev((t_self - self.t_other[0]) % max(self.t_other - self.t_other[0]) + self.t_other[0], self.tckp, ext=2)
        if np.iterable(t_self):
            return tmp
        else:
            return tmp[0]


@_available_to_user_math
class uinterp1d(interp1e):
    """
    Adjusted scipy.interpolate.interp1d (documented below)
    to interpolate the nominal_values and std_devs of an uncertainty array.

    NOTE: uncertainty in the `x` data is neglected, only uncertainties in the `y` data are propagated.

    :param std_pow: float. Uncertainty is raised to this power, interpolated, then lowered.
      (Note std_pow=2 interpolates the variance, which is often used in fitting routines).

    Additional arguments and key word arguments are as in interp1e (documented below).

    :Examples:

    >> x = np.linspace(0,2*np.pi,30)
    >> u = unumpy.uarray(np.cos(x),np.random.rand(len(x)))
    >>
    >> fi = utils.uinterp1d(x,u,std_pow=2)
    >> xnew = np.linspace(x[0],x[-1],1e3)
    >> unew = fi(xnew)
    >>
    >> f = figure(num='uniterp example')
    >> f.clf()
    >> ax = f.add_subplot(111)
    >> uerrorbar(x,u)
    >> uband(xnew,unew)


    interp1e Documentation:

    """

    __doc__ += interp1e.__doc__.replace('\n    ----------\n', ':\n').replace('\n    -------\n', ':\n').replace('\n    --------\n', ':\n')

    def __init__(self, x, y, kind='linear', axis=-1, copy=True, bounds_error=True, fill_value=np.nan, assume_sorted=False, std_pow=2, **kw):
        from uncertainties import unumpy

        self._std_pow = std_pow
        self._y_is_uncertain = is_uncertain(y)
        # convert Variables to floats, shape to shape+[2]
        if self._y_is_uncertain:
            axis = axis % y.ndim
            yfloat = np.rollaxis(np.array([unumpy.nominal_values(y), unumpy.std_devs(y) ** std_pow]), 0, len(y.shape) + 1)
        else:
            yfloat = y
        x = unumpy.nominal_values(x)
        interp1e.__init__(
            self,
            x,
            yfloat,
            kind=kind,
            axis=axis,
            copy=copy,
            bounds_error=bounds_error,
            fill_value=fill_value,
            assume_sorted=assume_sorted,
            **kw,
        )
        # overwrite y attr (note _y used internally)
        self.y = y

    def _finish_y(self, y, x_shape):
        """Return y to uncertainty array before returning"""
        from uncertainties import unumpy

        y = interp1e._finish_y(self, y, x_shape)
        if self._y_is_uncertain:
            y = unumpy.uarray(np.take(y, 0, axis=-1), np.abs(np.take(y, 1, axis=-1)) ** (1.0 / self._std_pow))
        return y


@_available_to_user_math
class uinterp1e(uinterp1d):
    """
    Adjusted unterp1d to extrapolate

    Arguments and key word arguments are as in uinterp1d (documented below).

    :uinterp1d Documentation:

    """

    __doc__ += uinterp1d.__doc__.replace('\n    ----------\n', ':\n').replace('\n    -------\n', ':\n').replace('\n    --------\n', ':\n')

    def __init__(self, x, y, kind='linear', axis=-1, copy=True, assume_sorted=False, std_pow=2, **kw):
        kw.setdefault('bounds_error', False)
        kw.setdefault('fill_value', 'extrapolate')
        uinterp1d.__init__(self, x, y, kind=kind, axis=axis, copy=copy, assume_sorted=assume_sorted, **kw)


@_available_to_user_math
class URegularGridInterpolator(interpolate.RegularGridInterpolator):
    """
    Adjusted scipy.interpolate.RegularGridInterpolator (documented below)
    to interpolate the nominal_values and std_devs of an uncertainty array.

    :param std_pow: float. Uncertainty is raised to this power, interpolated, then lowered.
        (Note std_pow=2 interpolates the variance, which is often used in fitting routines).

    Additional arguments and key word arguments are as in RegularGridInterpolator.

    :Examples:

    Make some sample 2D data

    >> x = np.linspace(0,2*np.pi,30)
    >> y = np.linspace(0,2*np.pi,30)
    >> z = np.cos(x[:,np.newaxis]+y[np.newaxis,:])
    >> u = unumpy.uarray(np.cos(x[:,np.newaxis]+y[np.newaxis,:]),np.random.rand(*z.shape))

    Form interpolator

    >> fi = URegularGridInterpolator((x,y),u,std_pow=2)

    interpolate along the diagonal of (x,y)

    >> xnew = np.linspace(x[0],x[-1],1e3)
    >> unew = fi(zip(xnew,xnew))

    Compare original and interpolated values.

    >> f = figure(num='URegularGridInterpolator example')
    >> f.clf()
    >> ax = f.add_subplot(111)
    >> uerrorbar(x,u.diagonal())
    >> uband(xnew,unew)

    Note the interpolated uncertainty between points is curved by std_pow=2. The curve is affected by
    the uncertainty of nearby off diagonal points (not shown).


    :RegularGridInterpolator Documentation:

    """

    __doc__ += (
        interpolate.RegularGridInterpolator.__doc__.replace('\n    ----------\n', ':\n')
        .replace('\n    -------\n', ':\n')
        .replace('\n    --------\n', ':\n')
        .replace('\n    -----\n', ':\n')
    )

    def __init__(self, points, values, method="linear", bounds_error=True, fill_value=np.nan, std_pow=2, **kw):
        from uncertainties import unumpy

        y = values
        self._std_pow = std_pow
        self._values_are_uncertain = is_uncertain(y)
        # convert Variables to floats, shape to shape+[2]
        if self._values_are_uncertain:
            yfloat = np.rollaxis(np.array([unumpy.nominal_values(y), unumpy.std_devs(y) ** std_pow]), 0, len(y.shape) + 1)
        else:
            yfloat = y
        interpolate.RegularGridInterpolator.__init__(
            self, points, yfloat, method=method, bounds_error=bounds_error, fill_value=fill_value, **kw
        )
        # overwrite y attr (note _y used internally)
        self.uvalues = y

    def __call__(self, xi, method=None):
        """
        Interpolate floats, then re-form uncertainty array.

        """
        from uncertainties import unumpy

        y = interpolate.RegularGridInterpolator.__call__(self, xi, method=method)
        if self._values_are_uncertain:
            y = unumpy.uarray(np.take(y, 0, axis=-1), np.take(y, 1, axis=-1) ** (1.0 / self._std_pow))
        return y

    __call__.__doc__ = interpolate.RegularGridInterpolator.__call__.__doc__


# -----------
# basic math
# -----------
@_available_to_user_math
def cumtrapz(y, x=None, dx=1.0, axis=-1, initial=0):
    """
    This is a convenience function for scipy.integrate.cumtrapz.
    Notice that here `initial=0` which is what one most often wants, rather than the `initial=None`,
    which is the default for the scipy function.

    Cumulatively integrate y(x) using the composite trapezoidal rule.
    This is the right way to integrated derivatives quantities which were calculated with `gradient`.
    If a derivative was obtained with the `diff` command, then the `cumsum` command should be used for its integration.

    :param y: Values to integrate.

    :param x: The coordinate to integrate along. If None (default), use spacing dx between consecutive elements in y.

    :param dx: Spacing between elements of y. Only used if x is None

    :param axis : Specifies the axis to cumulate. Default is -1 (last axis).

    :param initial :  If given, uses this value as the first value in the returned result.
                      Typically this value should be 0. If None, then no value at x[0] is returned and the returned array has one element
                      less than y along the axis of integration.

    :return: The result of cumulative integration of y along axis. If initial is None, the shape is such that the axis
             of integration has one less value than y. If initial is given, the shape is equal to that of y.
    """
    return integrate.cumtrapz(y, x=x, dx=dx, axis=axis, initial=initial)


@_available_to_user_math
def deriv(x, y):
    """
    This function returns the derivative of the 2nd order lagrange interpolating polynomial of y(x)

    :param x: x axis array

    :param y: y axis array

    :return: dy/dx
    """
    x = np.array(x)
    y = np.array(y)

    def dlip(ra, r, f):
        '''dlip - derivative of lagrange interpolating polynomial'''
        r1, r2, r3 = r
        f1, f2, f3 = f
        return (
            ((ra - r1) + (ra - r2)) / (r3 - r1) / (r3 - r2) * f3
            + ((ra - r1) + (ra - r3)) / (r2 - r1) / (r2 - r3) * f2
            + ((ra - r2) + (ra - r3)) / (r1 - r2) / (r1 - r3) * f1
        )

    return np.array(
        [dlip(x[0], x[0:3], y[0:3])]
        + list(dlip(x[1:-1], [x[0:-2], x[1:-1], x[2:]], [y[0:-2], y[1:-1], y[2:]]))
        + [dlip(x[-1], x[-3:], y[-3:])]
    )


@_available_to_user_math
def reverse_enumerate(l):
    import itertools

    return zip(range(len(l) - 1, -1, -1), reversed(l))


@_available_to_user_math
def factors(n):
    """
    get all the factors of a number

    > print(list(factors(100)))
    """
    import math

    large_factors = []
    for i in range(1, int(math.sqrt(n) + 1)):
        if n % i is 0:
            yield i
            if i is not n / i:
                large_factors.insert(0, n / i)
    for factor in large_factors:
        yield factor


def greatest_common_delta(input_int_array):
    """
    Given an array of integers it returns the greatest uniform delta step

    :param input_int_array: array of integers

    :return: greatest uniform delta step
    """
    input_int_array = np.atleast_1d(input_int_array).astype(int)
    if len(input_int_array) < 2:
        return 1

    delta = np.unique(np.diff(np.unique(input_int_array)))
    if len(input_int_array) < 2 or len(delta) < 2:
        return delta[0]

    from math import gcd

    d = gcd(delta[0], delta[1])
    for k in range(len(delta)):
        d = gcd(delta[k], d)

    return d


@_available_to_user_math
def mad(x, axis=-1, std_norm=True):
    """
    Median absolute deviation, defined as `1.4826 * np.median(np.abs(np.median(x)-x))`

    :param x: input data

    :param axis: axis along which to apply mad

    :param std_norm: if True (default) multiply output by 1.4826 to make MAD normalization agree with standard deviation for normal distribution. This normalization makes mad a robust estimator of the standard deviation.
                     http://books.google.com/books?id=i2bD50PbIikC&lpg=PA118&dq=1.4826&pg=PA118#v=onepage&q=1.4826&f=false

    :return: Median absolute deviation of the input data
    """
    norm = 1.0
    if std_norm:
        norm = 1.4826

    return norm * np.median(np.abs(np.expand_dims(np.median(x, axis=axis), axis=axis) - x), axis=axis)


@_available_to_user_math
def mad_outliers(data, m=3.0, outliers_or_valid='valid'):
    """
    Function to identify outliers data based on median absolute deviation (mad) distance.
    Note: used median absolute deviation defined as `1.4826 * np.median(np.abs(np.median(x)-x))`

    :param data: input data array (if a dictionary of arrays, the `mad_outliers` function is applied to each of the values in the dictionary)

    :param m: mad distance multiplier from the median after which a point is considered an outlier

    :param outliers_or_valid: return valid/outlier points (`valid` is default)

    :return: boolean array indicating which data points are a within `m` mad from the median value (i.e. the valid points)
    """
    if isinstance(data, dict):
        for k, item in enumerate(data.keys()):
            if k == 0:
                out = mad_outliers(data[item], m, outliers_or_valid)
            else:
                out &= mad_outliers(data[item], m, outliers_or_valid)
        if outliers_or_valid == 'valid':
            return out
        else:
            return ~out

    d = 1.4826 * np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else 0
    if outliers_or_valid == 'valid':
        return s < m
    else:
        return s >= m


def bin_outliers(data, mincount, nbins, outliers_or_valid='valid'):
    """
    Function to identify outliers data based on binning of data.
    The algorythm bins the data in `nbins` and then considers valid data only the data that falls within
    the bins that have at least `mincount` counts.

    :param data: input data array (if a dictionary of arrays, the `bin_outliers` function is applied to each of the values in the dictionary)

    :param mincount: minimum number of counts within a bin for data to be considered as valid

    :param nbins: number of bins for binning of data

    :param outliers_or_valid: return valid/outlier points (`valid` is default)

    :return: boolean array indicating which data points are a valid or not
    """
    if isinstance(data, dict):
        for k, item in enumerate(data.keys()):
            if k == 0:
                out = bin_outliers(data[item], mincount, nbins, outliers_or_valid)
            else:
                out &= bin_outliers(data[item], mincount, nbins, outliers_or_valid)
        if outliers_or_valid == 'valid':
            return out
        else:
            return ~out

    tmp = np.histogram(data.flat, nbins)
    ih = np.where(tmp[0] > mincount)[0]
    limits = np.nanmin(tmp[1][ih]), np.nanmax(tmp[1][ih + 1])
    if outliers_or_valid == 'valid':
        return (data >= limits[0]) & (data <= limits[1])
    else:
        return (data < limits[0]) | (data > limits[1])


@_available_to_user_math
def powerlaw_fit(x, y):
    """
    evaluates multidimensional power law for y based on inputs x

    :param x: 2D array of inputs [N,M]

    :param y: 1D array of output [M]

    :return: power law coefficient `p`, fitting function `f(p,x)`
    """
    fitfunc = lambda p, x: 10 ** (np.sum(p[:-1][:, np.newaxis] * np.log10(x), 0) + p[-1])
    errfunc = lambda p, x, y: (np.log10(y) - np.log10(fitfunc(p, x))).astype(float)
    from scipy import optimize

    pinit = [1] * x.shape[0] + [0]
    out = optimize.leastsq(errfunc, pinit, args=(x, y), full_output=1)
    return out[0], fitfunc


@_available_to_user_math
def exp_no_overflow(arg, factor=1.0, minpad=1e3, extra_pad=1e3, return_big_small=False):
    """
    Performs exp(arg) but first limits the value of arg to prevent floating math errors. Checks sys.float_info to so it
    can avoid floating overflow or underflow. Can be informed of factors you plan on multiplying with the exponential
    result later in order to make the limits more restrictive (the limits are "padded") and avoid over/underflow later
    on in your code.

    :param arg: Argument of exponential function

    :param factor: Factor that might be multiplied in to exponential function later. Adjusts limits to make them more
        restrictive and prevent overflow later on. The adjustment to limits is referred to as padding.

    :param minpad: Force the padding to be at least a certain size.

    :param extra_pad: Extra padding beyond what's determined by minpad and factor

    :param return_big_small: T/F: flag to just return big and small numbers. You may be able to speed up execution in
        repeated calls by getting appropriate limits, doing your own cropping, and looping exp() instead of looping
        exp_no_overflow(). Even in this case, exp_no_overflow() can help you pick good limits. Or if you don't have time
        for any of that, you can probably use -70 and 70 as the limits on arg, which will get you to order 1e30.

    :return: exp(arg) with no math errors, or (big, small) if return_big_small is set
    """

    # Sanitize:
    if minpad == 0:
        minpad = 1
    extra_pad = max([extra_pad, 1.0])

    # Define a pad. Padding gives a margin below overflow limit to allow for multiplying the exp() time some factor.
    # Make sure the big pad is >= 1, small pad is <= 1, and neither is 0.
    bigpad = max([np.atleast_1d(abs(factor)).max(), 1.0, minpad]) * extra_pad
    smallpad = max([min([np.atleast_1d(abs(factor)).min(), 1.0, 1.0 / minpad]), np.sqrt(sys.float_info.min)]) / extra_pad

    # printd('bigpad = {:}, smallpad = {:}'.format(bigpad, smallpad))

    # Take the operating system's floating max (min) and reduce (increase) it by pad, then take the log because this
    # thing will be compared to the argument of exp().
    big = float(np.log(sys.float_info.max / bigpad))
    small = float(np.log(sys.float_info.min / smallpad))

    if return_big_small:
        return big, small

    # Apply the limits to get floating over/underflow protection
    scalar_input = not np.shape(arg)
    arg = np.atleast_1d(arg)
    arg2 = copy.copy(arg)
    arg2[np.isnan(arg2)] = 0
    arg[arg2 > big] = big
    arg[arg2 < small] = small

    # printd('big = {:}, small = {:}'.format(big, small))
    result = np.exp(arg)

    return result[0] if scalar_input else result


@_available_to_user_math
def dimens(x):
    """
    Returns the number of dimensions in a mixed list/array object. Handles mutli-level nested iterables.

    From Craig Burgler on stack exchange https://stackoverflow.com/a/39255678/6605826

    This would be useful, for example on a case like:
    x = [np.array([1, 2, 3]), np.array([2, 5, 10, 20])]

    :param x: iterable (maybe nested iterable)

    :return: int
        Generalized dimension count, considering that some elements in a list might be iterable and others not.
    """
    try:
        size = len(x)
    except TypeError:  # Not an iterable
        return 0
    else:
        if size:  # Non-empty iterable
            return 1 + max(list(map(dimens, x)))
        else:  # Empty iterable
            return 1


@_available_to_user_math
def safe_divide(numerator, denominator, fill_value=0):
    """
    Division function to safely compute the ratio of two lists/arrays.
    The fill_value input parameter specifies what value should be filled in
    for the result whenever the denominator is 0.

    :param numerator: numerator of the division

    :param denominator: denominator of the division

    :param fill_value: fill value when denominator is 0

    :return: division with fill_value where nan or inf would have been instead
    """

    division = np.zeros_like(numerator) + fill_value
    ind = denominator != 0
    division[ind] = numerator[ind] / denominator[ind]
    return division


@_available_to_user_math
def nannanargmin(x, axis=1):
    """
    Performs nanargmin along an axis on a 2D array while dodging errors from empty rows or columns

    argmin finds the index where the minimum value occurs. nanargmin ignores NaNs while doing this.

    However, if nanargmin is operating along just one axis and it encounters a row that's all NaN, it raises a
    ValueError, because there's no valid index for that row. It can't insert NaN into the result, either,
    because the result should be an integer array (or else it couldn't be used for indexing), and NaN is a float.
    This function is for cases where we would like nanargmin to give valid results where possible and clearly invalid
    indices for rows that are all NaN. That is, it returns -N, where N is the row length, if the row is all NaN.

    :param x: 2D float array
        Input data to process

    :param axis: int
        0 or 1

    :return: 1D int array
        indices of the minimum value of each row or column.
        Rows/columns which are all NaN will be have -N, where N is the
        size of the relevant dimension (so -N is invalid).
    """
    # Use nanmin to find where the result would have NaNs
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        nanny = np.nanmin(x, axis=axis)
    # Prepare a result array that starts with invalid values to indicate failure; must be replaced later where possible
    result = np.empty(np.shape(nanny), dtype=np.int64)
    result[:] = -len(nanny)
    # Use np.nanargmin only on the rows or columns where that are not all NaN
    if axis == 1:
        result[~np.isnan(nanny)] = np.nanargmin(x[~np.isnan(nanny), :], axis=1)
    elif axis == 0:
        result[~np.isnan(nanny)] = np.nanargmin(x[:, ~np.isnan(nanny)], axis=0)
    else:
        raise ValueError(f'Unsupported axis argument: {axis}. This function supports 2D arrays, so please choose axis=0 or 1')
    return result


# -----------
# inverse scale-length
# -----------
def calcz(x, y, consistent_reconstruction=True):
    """
    Calculate Z: the inverse normalized scale-length
    The function is coded in such a way to avoid NaN and Inf where y==0

    z = -dy/dx/y

    :param x: x axis array

    :param y: y axis array

    :param consistent_reconstruction: calculate z so that
        integration of z with integz exactly generates original profile

    >> z_cF =calcz(rho,ne,consistent_reconstruction=False)
    >> z_cT=calcz(rho,ne,consistent_reconstruction=True)
    >> pyplot.plot(rho,ne)
    >> pyplot.plot(rho,integz(rho,z_cT,rho[0],ne[0],rho),'.')
    >> pyplot.plot(rho,integz(rho,z_cF,rho[0],ne[0],rho),'x')

    :return: z calculated at x
    """
    if not consistent_reconstruction or np.any(y == 0):
        tmp = np.nanmin(np.abs(y[np.where(y != 0)]))
        return -deriv(x, y) / (np.abs(y) + tmp * 1e-32) * np.sign(y)
    else:
        rat = np.log(y / y[-1])
        z = np.zeros(y.size)
        for i in range(1, len(y)):
            z[i] = 2 * (rat[i] - rat[i - 1]) / (x[i] - x[i - 1]) - z[i - 1]
        return -z


def mergez(x0, z0, x1, z1, core, nml, edge, x):
    """
    Perform merge of two Z profiles

    * `rho < core`: Z goes linearly to 0 on axis

    * `core < rho < nml`: profile 0

    * `nml < rho < edge`: linearly connect Z at `nml` and `edge`

    * `rho > edge`: profile 1

    :param x0: abscissa of first profile

    :param z0: values of first Z profile

    :param x1: abscissa of second profile

    :param z1: values of second Z profile

    :param core: abscissa of core boundary

    :param nml: abscissa of nml boundary

    :param edge: abscissa of edge boundary

    :param: returns tuple of merged x and z points
    """
    if edge < min(x1):
        raise Exception('edge must be > min(x1)')
    elif core < 0:
        raise Exception('core must be >= 0')
    elif core < nml and nml > max(x0):
        raise Exception('nml must be < max(x0)')

    # capture all of the important points
    x_ = []
    if core < nml:
        x_.extend(x0[np.where(((x0 > 0) & (x0 > core) & (x0 <= nml)))[0]])
    x_.extend(x1[np.where(x1 >= edge)[0]])
    x_.append(nml)
    x_.append(edge)
    x_.extend(x)
    x_ = np.unique(x_)

    # profile outside of edge (included)
    x1_ = x_[np.where((x_ >= edge) & (x_ > core))[0]]
    z1_ = interp1e(x1, z1)(x1_)

    # profile between core (included) and nml (included)
    if core < nml:
        x0_ = x_[np.where((x_ > 0) & (x_ > core) & (x_ <= nml))[0]]
        z0_ = interp1e(x0, z0)(x0_)
    elif core != 0:
        x0_ = [core]
        z0_ = [z1_[0]]
    else:
        x0_ = []
        z0_ = []

    x_ = np.hstack((0, x0_, x1_))
    z_ = np.hstack((0, z0_, z1_))

    x_, i = np.unique(x_, return_index=True)
    z_ = z_[i]

    return x, interp1e(x_, z_)(x)


def integz(x0, z0, xbc, ybc, x, clipz=True):
    """
    Integrate inverse scale-length Z to get profile

    :param x0: abscissa of the Z profile

    :param z0: Z profile

    :param xbc: abscissa of the boundary condition

    :param ybc: value of the boundary condition

    :param x: integrate the Z profile at these points

    :param clipz: use clipped z for extrapolation (alternatively linear)

    :return: integrated Z profile at points defined by x
    """
    from uncertainties import unumpy

    # make sure that the boundary condtion point is part of the itegration
    x_ = x
    x = np.unique(np.hstack((x_, xbc)))

    # evaluate z at requested points and allow for clipping
    z = uinterp1e(x0, z0)(x)
    if clipz:
        inside = np.where((x >= min(x0)) & (x <= max(x0)))[0].astype(int)
        low = np.where(x < min(x0))[0].astype(int)
        high = np.where(x > max(x0))[0].astype(int)
        z[low] = z[inside][0]
        z[high] = z[inside][-1]

    # backward integration <<<
    i0 = np.where(x <= xbc)[0]
    x0 = x[i0]
    z0 = z[i0]
    y0 = []
    if len(x0):
        t0 = -(z0[:-1] + z0[1:]) * np.diff(x0) / 2.0
        y0 = np.cumprod([ybc] + (unumpy.exp(-t0[::-1]).tolist()))[::-1]

    # forward integration >>>
    i1 = list(range(len(x)))[max(np.hstack((0, i0))) :]
    x1 = x[i1]
    z1 = z[i1]
    y1 = []
    if len(x1):
        t1 = (z1[:-1] + z1[1:]) * np.diff(x1) / 2.0
        y1 = np.cumprod([ybc] + (unumpy.exp(-t1).tolist()))[1:]

    return uinterp1e(x, np.hstack((y0, y1)))(x_)


# -----------
# peak detection
# -----------
@_available_to_user_math
def detect_peaks(x, mph=None, mpd=1, threshold=0, edge='rising', kpsh=False, valley=False, show=False, ax=None):

    """Detect peaks in data based on their amplitude and other features.

    Parameters
    ----------
    x : 1D array_like
        data.
    mph : {None, number}, optional (default = None)
        detect peaks that are greater than minimum peak height.
    mpd : positive integer, optional (default = 1)
        detect peaks that are at least separated by minimum peak distance (in
        number of data).
    threshold : positive number, optional (default = 0)
        detect peaks (valleys) that are greater (smaller) than `threshold`
        in relation to their immediate neighbors.
    edge : {None, 'rising', 'falling', 'both'}, optional (default = 'rising')
        for a flat peak, keep only the rising edge ('rising'), only the
        falling edge ('falling'), both edges ('both'), or don't detect a
        flat peak (None).
    kpsh : bool, optional (default = False)
        keep peaks with same height even if they are closer than `mpd`.
    valley : bool, optional (default = False)
        if True (1), detect valleys (local minima) instead of peaks.
    show : bool, optional (default = False)
        if True (1), plot data in matplotlib figure.
    ax : a matplotlib.axes.Axes instance, optional (default = None).

    Returns
    -------
    ind : 1D array_like
        indeces of the peaks in `x`.

    Notes
    -----
    The detection of valleys instead of peaks is performed internally by simply
    negating the data: `ind_valleys = detect_peaks(-x)`

    The function can handle NaN's

    See this IPython Notebook [1]_.

    References
    ----------
    .. [1] http://nbviewer.ipython.org/github/demotu/BMC/blob/master/notebooks/DetectPeaks.ipynb

    Examples
    --------
    >> from detect_peaks import detect_peaks
    >> x = np.random.randn(100)
    >> x[60:81] = np.nan
    >> # detect all peaks and plot data
    >> ind = detect_peaks(x, show=True)
    >> print(ind)

    >> x = np.sin(2*np.pi*5*np.linspace(0, 1, 200)) + np.random.randn(200)/5.
    >> # set minimum peak height = 0 and minimum peak distance = 20
    >> detect_peaks(x, mph=0, mpd=20, show=True)

    >> x = [0, 1, 0, 2, 0, 3, 0, 2, 0, 1, 0]
    >> # set minimum peak distance = 2
    >> detect_peaks(x, mpd=2, show=True)

    >> x = np.sin(2*np.pi*5*np.linspace(0, 1, 200)) + np.random.randn(200)/5.
    >> # detection of valleys instead of peaks
    >> detect_peaks(x, mph=0, mpd=20, valley=True, show=True)

    >> x = [0, 1, 1, 0, 1, 1, 0]
    >> # detect both edges
    >> detect_peaks(x, edge='both', show=True)

    >> x = [-2, 1, -2, 2, 1, 1, 3, 0]
    >> # set threshold = 2
    >> detect_peaks(x, threshold = 2, show=True)
    """

    def _plot(x, mph, mpd, threshold, edge, valley, ax, ind):
        """Plot results of the detect_peaks function, see its help."""
        if ax is None:
            from matplotlib import pyplot

            _, ax = pyplot.subplots(1, 1, figsize=(8, 4))
        ax.plot(x, 'b', lw=1)
        if ind.size:
            label = 'valley' if valley else 'peak'
            label = label + 's' if ind.size > 1 else label
            ax.plot(ind, x[ind], '+', mfc=None, mec='r', mew=2, ms=8, label='%d %s' % (ind.size, label))
            ax.legend(loc='best', framealpha=0.5, numpoints=1)
        ax.set_xlim(-0.02 * x.size, x.size * 1.02 - 1)
        ymin, ymax = x[np.isfinite(x)].min(), x[np.isfinite(x)].max()
        yrange = ymax - ymin if ymax > ymin else 1
        ax.set_ylim(ymin - 0.1 * yrange, ymax + 0.1 * yrange)
        ax.set_xlabel('Data #', fontsize=14)
        ax.set_ylabel('Amplitude', fontsize=14)
        mode = 'Valley detection' if valley else 'Peak detection'
        ax.set_title("%s (mph=%s, mpd=%d, threshold=%s, edge='%s')" % (mode, str(mph), mpd, str(threshold), edge))

    x = np.atleast_1d(x).astype('float64')
    if x.size < 3:
        return np.array([], dtype=int)
    if valley:
        x = -x
    # find indices of all peaks
    dx = x[1:] - x[:-1]
    # handle NaN's
    indnan = np.where(np.isnan(x))[0]
    if indnan.size:
        x[indnan] = np.inf
        dx[np.where(np.isnan(dx))[0]] = np.inf
    ine, ire, ife = np.array([[], [], []], dtype=int)
    if not edge:
        ine = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) > 0))[0]
    else:
        if edge.lower() in ['rising', 'both']:
            ire = np.where((np.hstack((dx, 0)) <= 0) & (np.hstack((0, dx)) > 0))[0]
        if edge.lower() in ['falling', 'both']:
            ife = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) >= 0))[0]
    ind = np.unique(np.hstack((ine, ire, ife)))
    # handle NaN's
    if ind.size and indnan.size:
        # NaN's and values close to NaN's cannot be peaks
        ind = ind[np.in1d(ind, np.unique(np.hstack((indnan, indnan - 1, indnan + 1))), invert=True)]
    # first and last values of x cannot be peaks
    if ind.size and ind[0] == 0:
        ind = ind[1:]
    if ind.size and ind[-1] == x.size - 1:
        ind = ind[:-1]
    # remove peaks < minimum peak height
    if ind.size and mph is not None:
        ind = ind[x[ind] >= mph]
    # remove peaks - neighbors < threshold
    if ind.size and threshold > 0:
        dx = np.min(np.vstack([x[ind] - x[ind - 1], x[ind] - x[ind + 1]]), axis=0)
        ind = np.delete(ind, np.where(dx < threshold)[0])
    # detect small peaks closer than minimum peak distance
    if ind.size and mpd > 1:
        ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
        idel = np.zeros(ind.size, dtype=bool)
        for i in range(ind.size):
            if not idel[i]:
                # keep peaks with the same height if kpsh is True
                idel = idel | (ind >= ind[i] - mpd) & (ind <= ind[i] + mpd) & (x[ind[i]] > x[ind] if kpsh else True)
                idel[i] = 0  # Keep current peak
        # remove the small peaks and sort back the indices by their occurrence
        ind = np.sort(ind[~idel])

    if show:
        if indnan.size:
            x[indnan] = np.nan
        if valley:
            x = -x
        _plot(x, mph, mpd, threshold, edge, valley, ax, ind)

    return ind


@_available_to_user_math
def find_feature(y, x=None, M=0.01, k=5.0, xmin=None, xmax=None, retall=False):
    """
    Identify edges and center of a sharp feature (pedestal, peak, or well) in a otherwise smooth profile.

    :param y: np.ndarray. Parameter of interest, such as T_e

    :param x: np.ndarray. Position basis, such as psi_N (Default is np.arange(len(y))

    :param M: float. Gaussian smoothing sigma in units of position basis

    :param k: float. Difference of gaussians factor (second smoothing sigma is M*k)

    :param xmin: float. Lower limit on range of X values to consider in search

    :param xmax: float. Upper limit on range of X values to consider in search

    :param retall: bool. Return gaussian smoothed functions

    :returns : ( Inner edge, outer edge, center, value at inner edge, value at outer edge )

    :Examples:

    Here, is a simple 1D example using find_feature to identify the steep gradient region of a tanh.

    >> x = np.linspace(0,1,1000)
    >> center = 0.8
    >> halfwidth = 0.05
    >> y = np.tanh((center-x)/halfwidth)+1
    >> dydx = deriv(x,y)
    >> indx = find_feature(dydx,x=x)
    >> xpt = x[indx]
    >> ypt = dydx[indx]

    >> foundwidth = x[indx[2]]-x[indx[0]]
    >> print("Width within {:.2f}%".format((1-2*halfwidth/foundwidth)*100))

    Note we chose M to set the appropriate scale of interest for the above problem.
    We can see the sensitivity to this by scanning the tanh width in a 2D example.

    >> xs = x.reshape(1,-1)
    >> halfwidths = np.linspace(0.01,0.1,50).reshape(-1,1)
    >> ys = np.tanh((center-xs)/halfwidths)+1
    >> dydxs = np.gradient(ys)[1]/np.gradient(x)

    M sets the scale for the steepness of interest
    using one M for a range of bump sizes isolates only the scale of interest
    >> indxs = np.apply_along_axis(find_feature,1,dydxs,x=x,M=0.01,k=5)
    Tracking the scale of the bump with M approximates tanh widths
    >> #indxs = [find_feature(dy,x=x,M=2*hw/10.,k=5) for dy,hw in zip(dydxs,halfwidths)]

    >> # found peak and edge points of steep gradient region
    >> foundwidths = map(lambda indx: x[indx[2]]-x[indx[0]], indxs)
    >> xpts = [x[i] for i in indxs]
    >> ypts = [yy[i] for yy,i in  zip(ys,indxs)]
    >> dypts= [yy[i] for yy,i in  zip(dydxs,indxs)]

    >> # tanh half width points
    >> # Note np.tanh(1) = 0.76, and d/dxtanh = sech^2 = 0.42
    >> ihws = np.array([(np.abs(x-center-hw).argmin(),
    >>                   np.abs(x-center+hw).argmin()) for hw in halfwidths[:,0]])
    >> xhws = [x[i] for i in ihws]
    >> yhws = [yy[i] for yy,i in  zip(ys,ihws)]
    >> dyhws= [yy[i] for yy,i in  zip(dydxs,ihws)]

    Visualize the comparison between tanh widths and the identified region of steep gradient
    >> close('all')
    >> f,ax = pyplot.subplots(3,1)
    >> ax[0].set_ylabel('y = np.tanh((c-x)2/w)+1')
    >> ax[0].set_xlabel('x')
    >> ax[1].set_ylabel('dy/dx')
    >> ax[1].set_xlabel('x')
    >> for i in  [0,24,49]:
    ...     l,  = ax[0].plot(x,ys[i])
    ...     w1, = ax[0].plot(xhws[i],yhws[i],marker='o',ls='',fillstyle='none',color=l.get_color())
    ...     w2, = ax[0].plot(xpts[i],ypts[i],marker='x',ls='',fillstyle='none',color=l.get_color())
    ...     l,  = ax[1].plot(x,dydxs[i])
    ...     w1, = ax[1].plot(xhws[i],dyhws[i],marker='o',ls='',fillstyle='none',color=l.get_color())
    ...     w2, = ax[1].plot(xpts[i],dypts[i],marker='x',ls='',fillstyle='none',color=l.get_color())
    >> ax[-1].set_ylabel('Edge Width')
    >> ax[-1].set_xlabel('Tanh Width')
    >> ax[-1].plot([0,2*halfwidths[-1,0]],[0,2*halfwidths[-1,0]])
    >> ax[-1].plot(2*halfwidths[:,0],foundwidths,marker='o',lw=0)

    """
    # must be 1D
    yy = np.atleast_1d(y).ravel()
    # isolate x range
    if x is None:
        x = np.arange(y.shape[0])
    if xmin is None:
        xmin = np.NINF
    if xmax is None:
        xmax = np.inf
    xx = np.atleast_1d(x).ravel()
    w = np.where((xx >= xmin) & (xx <= xmax))[0]
    xx, yy = xx[w], yy[w]

    # difference of gaussian smooths
    dx = np.mean(np.diff(xx))
    s_1 = ndimage.filters.gaussian_filter(yy, M / dx)
    s_2 = ndimage.filters.gaussian_filter(yy, M * k / dx)
    sdiff = s_1 - s_2

    # feature location
    peak_i = np.argmax(np.abs(sdiff))
    # find width from gaussian smooths crossing on either side of peak
    left_i = 0
    left_all = np.where(np.diff(np.signbit(sdiff[:peak_i])))[0]
    if len(left_all) > 0:
        left_i += left_all[-1]
    right_i = peak_i
    right_all = np.where(np.diff(np.signbit(sdiff[peak_i:])))[0]
    if len(right_all) > 0:
        right_i += right_all[0]
    result = np.array((left_i, peak_i, right_i))

    if retall:
        result = (result, s_1, s_2)
    return result


# -----------
# fit parabolas
# -----------
def parabola(x, y):
    """
    y = a*x^2 + b*x + c

    :return: a,b,c
    """
    if np.any(np.isnan(x)) or np.any(np.isnan(y)):
        raise np.linalg.LinAlgError('parabola could not be fit with x=%s y=%s' % (x, y))
    # A=np.matrix([[x[0]**2,x[0],1],[x[1]**2,x[1],1],[x[2]**2,x[2],1]])
    # a,b,c=np.array(A.I*np.matrix(y[0:3]).T).flatten().tolist()
    # polyfit is equally fast but more robust when x values are similar, and matrix A becomes singular, eg.
    # x,y=[-1E-16,1,1+1E-16],[1,1,1]
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', np.RankWarning)
        a, b, c = np.polyfit(x, y, 2)
    return a, b, c


def parabolaMax(x, y, bounded=False):
    """
    Calculate a parabola through x,y, then return the extremum point of
    the parabola

    :param x: At least three abcissae points
    :param y: The corresponding ordinate points
    :param bounded: False, 'max', or 'min'
          - False: The extremum is returned regardless of location relative to x (default)
          - 'max' ('min'): The extremum location must be within the bounds of x, and if not return the location and value of max(y) (min(y))
    :return: x_max,y_max - The location and value of the extremum
    """
    a, b, c = parabola(x, y)
    x_max = -b / (2 * a)
    y_max = a * x_max ** 2 + b * x_max + c
    if bounded and (x_max > max(x) or x_max < min(x)):
        printe('ParabolaMax found the maximum outside the input abcissae; using arg%s(y) instead' % bounded)
        iy = eval('arg%s(y)' % bounded)
        x_max = x[iy]
        y_max = y[iy]
    return x_max, y_max


def parabolaCycle(X, Y, ix):
    ix = np.array([-1, 0, 1]) + ix

    if (X[0] - X[-1]) < 1e-15:
        if ix[0] < 0:
            ix[0] = len(X) - 1 - 1
        if ix[-1] > (len(X) - 1):
            ix[-1] = 0 + 1
    else:
        if ix[0] < 0:
            ix[0] = len(X) - 1
        if ix[-1] > (len(X) - 1):
            ix[-1] = 0

    return parabola(X[ix], Y[ix])


def parabolaMaxCycle(X, Y, ix, bounded=False):
    """
    Calculate a parabola through X[ix-1:ix+2],Y[ix-1:ix+2], with proper
    wrapping of indices, then return the extremum point of the parabola

    :param X: The abcissae points: an iterable to be treated as periodic
    :param y: The corresponding ordinate points
    :param ix: The index of X about which to find the extremum
    :param bounded: False, 'max', or 'min'
          - False: The extremum is returned regardless of location relative to x (default)
          - 'max' ('min'): The extremum location must be within the bounds of x, and if not return the location and value of max(y) (min(y))
    :return: x_max,y_max - The location and value of the extremum
    """
    ix = np.array([-1, 0, 1]) + ix

    if (X[0] - X[-1]) < 1e-15:
        if ix[0] < 0:
            ix[0] = len(X) - 1 - 1
        if ix[-1] > (len(X) - 1):
            ix[-1] = 0 + 1
    else:
        if ix[0] < 0:
            ix[0] = len(X) - 1
        if ix[-1] > (len(X) - 1):
            ix[-1] = 0

    try:
        return parabolaMax(X[ix], Y[ix], bounded=bounded)
    except Exception:
        printe([ix, X[ix], Y[ix]])
        return X[ix[1]], Y[ix[1]]


def paraboloid(x, y, z):
    """
    z = ax*x^2 + bx*x + ay*y^2 + by*y + c

    NOTE: This function uses only the first 5 points of the x, y, z arrays
    to evaluate the paraboloid coefficients

    :return: ax,bx,ay,by,c
    """
    if np.any(np.isnan(x.flatten())) or np.any(np.isnan(y.flatten())) or np.any(np.isnan(z.flatten())):
        raise np.linalg.LinAlgError('paraboloid could not be fit with x=%s y=%s z=%s' % (x, y, z))
    A = []
    for k in range(5):
        A.append([x[k] ** 2, x[k], y[k] ** 2, y[k], 1])
    A = np.array(A)
    ax, bx, ay, by, c = np.dot(np.linalg.inv(A), np.array(z[:5]))
    return ax, bx, ay, by, c


# -----------
# filtering
# -----------
@_available_to_user_math
def smooth(x, window_len=11, window='hanning', axis=0):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the beginning and end part of the output signal.

    input:
        :param x: the input signal
        :param window_len: the dimension of the smoothing window; should be an odd integer; is ignored if `window` is an array
        :param window: the window function to use, see scipy.signal.get_window documentation for list of available windows
                'flat' or 'boxcar' will produce a moving average smoothing
                Can also be an array, in which case it is used as the window function and `window_len` is ignored
        :param axis: The axis that is smoothed

    output:
        the smoothed signal

    :Examples:

    >> t=np.linspace(-2,2,100)
    >> x=np.sin(t)+randn(len(t))*0.1
    >> y=smooth(x,11)

    see also:

    scipy.signal.get_window, np.convolve, scipy.signal.lfilter
    """

    def smooth1d(x, win):
        window_len = win.size
        s = np.r_[x[window_len - 1 : 0 : -1], x, x[-1:-window_len:-1]]
        y = np.convolve(win / win.sum(), s, mode='valid')
        start = int(np.ceil(window_len / 2.0) - 1)
        stop = start + len(x)
        return y[start:stop]

    window_len = int(window_len)
    if window_len < 3:
        return x
    if window == 'flat':  # backwards compatibility
        window = 'boxcar'
    if isinstance(window, str) or isinstance(window, tuple):
        if window_len % 2 == 0:  # Use odd-length window to avoid shifting data
            window_len += 1
        win = scipy.signal.get_window(window, window_len, fftbins=False)
    else:
        win = np.asarray(window)
        if len(win.shape) != 1:
            raise ValueError('window must be 1-D')
    if x.shape[axis] < win.size:
        raise ValueError("Input vector needs to be bigger than window length " "of {}".format(win.size))

    return np.apply_along_axis(smooth1d, axis, x, win)


@_available_to_user_math
def smoothIDL(data, n_smooth=3, timebase=None, causal=False, indices=False, keep=False):
    """
    An efficient top hat smoother based on the `smooth` IDL routine.
    The use of cumsum-shift(cumsum) means that execution time
    is 2xN flops compared to 2 x n_smooth x N for a convolution.
    If supplied with a timebase, the shortened timebase is returned as
    the first of a tuple.

    :param data: (timebase, data) is a shorthand way to pass timebase

    :param n_smooth: smooth bin size

    :param timebase: if passed, a tuple with (timebase,smoothed_data) gets returned

    :param causal: If True, the smoothed signal never preceded the input,
              otherwise, the smoothed signal is "centred" on the input
              (for n_smooth odd) and close (1//2 timestep off) for even

    :param indices: if True, return the timebase indices instead of the times

    :param keep: Better to throw the partially cooked ends away, but if you want to
                 keep them use keep=True.  This is useful for quick filtering
                 applications so that original and filtered signals are easily
                 compared without worrying about timebase

    >> smooth([1,2,3,4],3)
    np.array([ 2.,  3.])
    >> smooth([1.,2.,3.,4.,5.],3)
    np.array([ 2.,  3.,  4.])
    >> smooth([1,2,3,4,5],timebase=np.array([1,2,3,4,5]),n_smooth=3, causal=False)
    (np.array([2, 3, 4]), np.array([ 2.,  3.,  4.]))
    >> smooth([0,0,0,3,0,0,0],timebase=[1,2,3,4,5,6,7],n_smooth=3, causal=True)
    ([3, 4, 5, 6, 7], np.array([ 0.,  1.,  1.,  1.,  0.]))
    >> smooth([0,0,0,3,0,0,0],timebase=[1,2,3,4,5,6,7],n_smooth=3, causal=True, indices=True)
    ([2, 3, 4, 5, 6], np.array([ 0.,  1.,  1.,  1.,  0.]))
    >> smooth([0,   0,   0,   0,   5,   0,    0,  0,   0,   0,   0], 5, keep=1)
    np.array([ 0.,  0.,  1.,  1.,  1.,  1.,  1.,  0.,  0., -1., -1.])
    """
    if len(data) == 2:  # a tuple (timebase, data)
        timebase = data[0]
        data = data[1]
    csum = np.cumsum(data)
    if not (keep):
        sm_sig = csum[n_smooth - 1 :]
        # just the valid bit
        # sm_sig[1:] -= csum[0:-n_smooth]  #  should work?  - bug in python?
        sm_sig[1:] = sm_sig[1:] - csum[0:-n_smooth]
        sm_sig = sm_sig / float(n_smooth)
    else:  # try to retain full length for quick tests - only allow causal=False
        if causal:
            raise ValueError("can't be causal and keep ends")
        else:
            sm_sig = np.array(data) * 0  # get a vector of the right length
            half_offs = int(n_smooth // 2)  # use integer round down, only perfect for odd n
            # See test code [0, 0, 0, 1, 0, 0, 0]
            # for the n=3 case, want sm[3] to be cs[4]-cs[1] so load cs[1:] into sm,
            # then subtract cs[0] from sm[2] etc
            # for n=5, want sm[5] to be cs[7]-cs[2] so load cs[2:] into sm
            # and subtr cs[0] from sm[3]
            sm_sig[0:-half_offs] = csum[half_offs:]  # get the first bit left shifted
            sm_sig[half_offs + 1 :] = sm_sig[half_offs + 1 :] - csum[0 : -(half_offs + 1)]
            sm_sig = sm_sig / float(n_smooth)
    if timebase is None:
        return sm_sig
    else:
        if causal:
            offset = n_smooth - 1
        elif keep:
            offset = 0
        else:
            offset = int(n_smooth // 2)

        if indices:
            sm_timebase = list(range(offset, offset + len(sm_sig)))
        else:
            sm_timebase = timebase[offset : offset + len(sm_sig)]

        return (sm_timebase, sm_sig)


@_available_to_user_math
def pcs_rc_smooth(xx, yy, s):
    """
    RC lowpass smoothing filter using same formula as in the PCS. Can be used to reproduce PCS lowpass filtering.

    :param xx: array
        Independent variable (like time). Does not have to be evenly spaced.

    :param yy: array matching xx
        Depending variable

    :param s: float
        Smoothing time constant in units matching xx

    :return: array
        Smoothed/filtered version of yy
    """
    printd('   start rc_smooth w/ s = {:}'.format(s), topic='pcs_rc_smooth')
    rc = s  # Renaming it makes its meaning clearer
    dx = np.diff(xx)
    dx = np.append(dx[0], dx)
    a = dx / (rc + dx)
    printd('   mean(dx) = {:}, mean(a) ={:}'.format(np.mean(dx), np.mean(a)), topic='pcs_rc_smooth')
    ys = yy * 0
    ys[0] = yy[0]
    printd('   min(a) = {:}, max(a) = {:}'.format(min(a), max(a)), topic='pcs_rc_smooth')

    with np.errstate(under='ignore'):  # Ignore harmless underflow (might happen if yy -> 0 & ys asymptotes to 0)
        for ii in range(1, len(yy)):
            ys[ii] = ys[ii - 1] * (1 - a[ii]) + yy[ii] * a[ii]

    printd(' ys[-1] = {:}'.format(ys[-1]), topic='pcs_rc_smooth')
    return ys


@_available_to_user_math
def smooth_by_convolution(
    yi, xi=None, xo=None, window_size=None, window_function='gaussian', axis=0, causal=False, interpolate=False, std_dev=2
):
    """
    Convolution of a non-uniformly discretized array with window function.

    The output values are np.nan where no points are found in finite windows (weight is zero).
    The gaussian window is infinite in extent, and thus returns values for all xo.

    Supports uncertainties arrays.
    If the input --does not-- have associated uncertainties, then the output will --not-- have associated uncertainties.

    :param yi: array_like (...,N,...). Values of input array

    :param xi: array_like (N,). Original grid points of input array (default y indicies)

    :param xo: array_like (M,). Output grid points of convolution array (default xi)

    :param window_size: float.
      Width of passed to window function (default maximum xi step).
      For the Gaussian, sigma=window_size/4. and the convolution is integrated across +/-4.*sigma.

    :param window_function: str/function.
      Accepted strings are 'hanning','bartlett','blackman','gaussian', or 'boxcar'.
      Function should accept x and window_size as arguments and return a corresponding weight.

    :param axis: int. Axis of y along which convolution is performed

    :param causal: int. Forces f(x>0) = 0.

    :param interpolate: False or integer number > 0
     Paramter indicating to interpolate data so that there are`interpolate`
     number of data points within a time window. This is useful in presence of sparse
     data, which would result in stair-case output if not interpolated.
     The integer value sets the # of points per window size.

    :param std_dev: str/int
       Accepted strings are 'none', 'propagate', 'population', 'expand', 'deviation', 'variance'.
       Only 'population' and 'none' are valid if yi is not an uncertainties array (i.e. std_devs(yi) is all zeros).
       Setting to an integer will convolve the error uncertainties to the std_dev power before taking the std_dev root.
       std_dev = 'propagate' is true propagation of errors (slow if not interpolating)
       std_dev = 'population' is the weighted "standard deviation" of the points themselves (strictly correct for the boxcar window)
       std_dev = 'expand' is propagation of errors weighted by w~1/window_function
       std_dev = 'deviation' is equivalent to std_dev=1
       std_dev = 'variance' is equivalent to std_dev=2

    :return: convolved array on xo

    >> M=300
    >> ninterp = 10
    >> window=['hanning','gaussian','boxcar'][1]
    >> width=0.05
    >> f = figure(num='nu_conv example')
    >> f.clf()
    >> ax = f.add_subplot(111)
    >>
    >> xo=np.linspace(0,1,1000)
    >>
    >> x0=xo
    >> y0=(x0>0.25)&(x0<0.75)
    >> pyplot.plot(x0,y0,'b-',label='function')
    >>
    >> x1=np.cumsum(rand(M))
    >> x1=(x1-min(x1))/(max(x1)-min(x1))
    >> y1=(x1>0.25)&(x1<0.75)
    >> pyplot.plot(x1,y1,'b.',ms=10,label='subsampled function')
    >> if window=='hanning':
    >>     ys=smooth(interp1e(x0,y0)(xo),int(len(xo)*width))
    >>     pyplot.plot(xo,ys,'g-',label='smoothed function')
    >>     yc=smooth(interp1e(x1,y1)(xo),int(len(xo)*width))
    >>     pyplot.plot(xo,yc,'m--',lw=2,label='interp subsampled then convolve')
    >>
    >> y1=unumpy.uarray(y1,y1*0.1)
    >> a=time.time()
    >> yo=nu_conv(y1,xi=x1,xo=xo,window_size=width,window_function=window,std_dev='propagate',interpolate=ninterp)
    >> print('nu_conv time: {:}'.format(time.time()-a))
    >> ye=nu_conv(y1,xi=x1,xo=xo,window_size=width,window_function=window,std_dev='expand',interpolate=ninterp)
    >>
    >> uband(x1,y1,color='b',marker='.',ms=10)
    >> uband(xo,yo,color='r',lw=3,label='convolve subsampled')
    >> uband(xo,ye,color='c',lw=3,label='convolve with expanded-error propagation')
    >>
    >> legend(loc=0)
    >> pyplot.ylim([-0.1,1.1])
    >> pyplot.title('%d points , %s window, %3.3f width, interpolate %s'%(M,window,width, ninterp))

    """
    if len(yi.shape) > 1:
        yo = np.apply_along_axis(
            smooth_by_convolution,
            axis,
            yi,
            xi=xi,
            xo=xo,
            window_size=window_size,
            window_function=window_function,
            causal=causal,
            interpolate=interpolate,
            std_dev=std_dev,
        )
        return yo

    from scipy import interpolate as scipy_interpolate
    from uncertainties import unumpy

    # named functions
    if isinstance(window_function, str):
        win_mult = 1.0
        if window_function == 'gaussian':
            f = lambda x, a: unumpy.exp(-0.5 * (4.0 * x / a) ** 2) / (a / 4.0) / np.sqrt(2 * np.pi)
            win_mult = 2.0
        elif window_function == 'hanning':
            f = lambda x, a: (np.abs(x) <= a / 2.0) * (1 - unumpy.cos(2 * np.pi * (x - a / 2.0) / a)) / a
        elif window_function == 'bartlett':
            f = lambda x, a: (np.abs(x) <= a / 2.0) * (1 - np.abs(x) * 2.0 / a)
        elif window_function == 'blackman':
            f = lambda x, a: (np.abs(x) <= a / 2.0) * (
                0.42 - 0.5 * unumpy.cos(2.0 * np.pi * (x + a / 2.0) / a) + 0.08 * unumpy.cos(4.0 * np.pi * (x + a / 2.0) / a)
            )
        elif window_function in ['boxcar', 'median']:
            f = lambda x, a: 1.0 * ((x >= -a / 2.0) * (x <= a / 2.0)) / a
        elif window_function in ['triangle']:
            f = lambda x_, a: (a >= abs(x_)) * (1 - abs(x_ / a))
            win_mult = 2.0
        else:
            raise Exception('Valid window functions are: gaussian, hanning, bartlett, blackman, boxcar')
    else:
        f = window_function

    # handle std_dev
    if isinstance(std_dev, str):
        std_dev = std_dev.lower()
        if std_dev == 'variance':
            std_dev = 2
        elif std_dev == 'deviation':
            std_dev = 1
    elif std_dev is None:
        std_dev = 'none'

    # defaults
    if xi is None:
        xi = np.arange(yi.shape[0])
    if xo is None:
        xo = xi
    if window_size is None:
        window_size = max(np.diff(xi)) / 2.0

    # initialize input/output arrays
    yo = np.zeros(xo.shape)
    if is_uncertain(yi):
        ei = unumpy.std_devs(yi)
        yi = unumpy.nominal_values(yi)
        eo = np.zeros(xo.shape)
    else:
        ei = 0.0 * yi
        eo = np.zeros(xo.shape)
        if std_dev not in ['population', 'none']:
            std_dev = 'none'

    # remove nans
    i = np.where((~np.isnan(xi)) & (~np.isnan(yi)))
    xi = xi[i]
    yi = yi[i]
    ei = ei[i]
    # If there is no non-Nan input data, no point continuing
    if yi.shape[0] == 0:
        printw('    Smooth by convolution: Zero length input, returning Nan output')
        if std_dev == 'none':
            return xo * np.nan
        else:
            return unumpy.uarray(xo * np.nan, xo * np.nan)
    if np.any(np.isnan(yi)):
        printe(yi)
        raise RuntimeError('nans detected')
    if not xi.size:
        if std_dev == 'none':
            return xo * np.nan
        else:
            return unumpy.uarray(xo * np.nan, xo * np.nan)

    # interpolation (# of points per window size)
    if interpolate and len(xi) > 1:
        if not (interpolate is False or is_int(interpolate) or interpolate > 0):
            raise ValueError('interpolate argument should be False or a number')
        xi1 = np.linspace(min(xi), max(xi), int(np.ceil((max(xi) - min(xi)) / (window_size * win_mult) * interpolate)))
        yi = scipy_interpolate.interp1d(xi, yi)(xi1)
        if ei is not None:
            ei = scipy_interpolate.interp1d(xi, ei)(xi1)
        xi = xi1

    # grid-center values for trapezoidal integration
    dx = np.ediff1d(xi, to_end=0)
    y_center = np.hstack([(yi[:-1] + yi[1:]) * 0.5, 0])

    # convolution
    for k, xo_k in enumerate(xo):
        # find distances to requested x point
        x = xo_k - xi

        # select points within time window
        if not causal:
            i = np.abs(x) <= window_size * win_mult / 2.0
        else:
            i = np.abs(x - window_size * win_mult / 4.0) <= window_size * win_mult / 4.0
        npts = np.count_nonzero(i)

        # set output to nan if points are outside of convolution window
        if npts == 0:
            yo[k] = np.nan
            eo[k] = np.nan

        # explicitly use single data point if its the only thing available
        elif npts == 1:
            yo[k] = yi[i][0]
            eo[k] = ei[i][0]

        # median value and median std
        elif window_function == 'median':
            yo[k] = np.median(yi[i])
            eo[k] = np.median(ei[i])

        # use weighted convolution if multiple points in window
        else:
            # generate window and it's normalization
            ff = f(x[i], window_size)
            if causal:
                ff *= x[i] >= 0
            ff_center = ff[:-1] + np.diff(ff) * 0.5
            norm = np.sum(ff_center * dx[i][:-1])  # trapezoidal integration

            # set output to nan if the norm is zero
            if norm == 0:
                yo[k] = np.nan
                eo[k] = np.nan

            else:
                # normalize window
                ff = ff / norm

                # treat value and error together
                if std_dev in ['propagate', 'expand']:  # propagate uncertainties (slow)
                    # grid-center points of weighted values for trapezoidal integration
                    if std_dev == 'propagate':
                        # simply propogate the uncertainties through the convolution integral
                        fy = unumpy.uarray(ff * yi[i], ff * ei[i])
                    else:
                        # expand the errorbar of points in the integral bounds by
                        # an amount proportional to 1/window_function before propagating them,
                        # increasing the error associated with the convolution.
                        # Note integrals with only far off points will have larger errors then any of the given points
                        fy = unumpy.uarray(ff * yi[i], (f(0, window_size) / norm) * ei[i])
                    fy_center = (fy[:-1] + fy[1:]) * 0.5
                    # trapezoidal integration (uncertainties propagate themselves)
                    # considerable speedup is possible if input grid is uniform
                    if interpolate or np.all(dx[i][:-1] == dx[i][0]):
                        yk = np.sum(fy_center * dx[i][0])
                    else:
                        yk = np.sum(fy_center * dx[i][:-1])

                    # re-separate values and uncertainties
                    yo[k] = unumpy.nominal_values(yk)
                    eo[k] = unumpy.std_devs(yk)

                # convolve value and estimate error separately
                else:
                    # grid-center points of weighted values for trapezoidal integration
                    fy = ff * yi[i]
                    fy_center = (fy[:-1] + fy[1:]) * 0.5
                    # trapezoidal integration
                    yo[k] = np.sum(fy_center * dx[i][:-1])

                    # associated error estimate
                    if std_dev == 'population':
                        # this is the "weighted standard deviation"
                        # it would be strictly correct if yo[k] was a weighted np.mean like np.sum(ff_center*dx*y_center) / np.sum(ff_center*dx)
                        # (http://stats.stackexchange.com/questions/6534/how-do-i-calculate-a-weighted-standard-deviation-in-excel)
                        w = ff_center * dx[i][:-1]
                        eo[k] = np.sqrt(np.sum(w * (y_center[i][:-1] - yo[k]) ** 2) / (np.sum(w) * (npts - 1) / npts))
                        # eo[k] = np.sqrt(np.sum(w * (y_center[i][:-1] - yo[k]) ** 2))

                    elif type(std_dev) in [float, int]:
                        # convolve error/covariance/etc. (gives error envelope)
                        # grid-center points of nth power of weighted values for trapezoidal integration
                        fe = np.power(ff * ei[i], std_dev)
                        fe_center = (fe[:-1] + fe[1:]) * 0.5
                        # trapezoidal integration and nth root
                        eo[k] = np.power(np.sum(fe_center * dx[i][:-1]), 1.0 / std_dev)

                    elif std_dev == 'none':
                        pass

                    elif std_dev != 'propagate':
                        raise ValueError('std_dev=%s is an invalid optional key word argument' % repr(std_dev))

    if std_dev == 'none':
        return yo
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        uo = unumpy.uarray(yo, eo)
    return uo


@_available_to_user_math
def trismooth(*args, **kw):
    """
    Smooth with triangle kernel, designed to mimic smooth in reviewplus
    :param args:
        y: float array,
        y, window_size: float array, float
        y, x, window_size: float array, float array, float
        OR
        y, window_size[optional] as OMFITmdsValue, float
        If x or window_size are not defined, smooth_by_convolution will pick values automatically.
        window_size is the half width fo the kernel.

        The default window_size set by smooth_by_convolution will probably be too small,
        unless you are providing a much higher resolution output grid with xo. You should probably set window_size by
        providing at least two arguments.
    :param kw: Keywords passed to smooth_by_convolution.
    :return: float array or uarray or tuple of arrays
        ysmo = result from smooth_by_convolution; array (default) or uarray (std_dev is modified)
        if OMFITmdsValue:
            (x, ysmo)
        else:
            ysmo
    """
    y = args[0]
    from omfit_classes.omfit_mds import OMFITmdsValue

    if isinstance(y, OMFITmdsValue):
        m = y
        x = y.dim_of(0)
        y = y.data()
        if len(args) > 1:
            window_size = args[1]
        else:
            window_size = None
    else:
        m = None
        if len(args) == 2:
            window_size = args[1]
            x = None
        elif len(args) >= 3:
            x = args[1]
            window_size = args[2]
        else:
            window_size = x = None

    kw.setdefault('std_dev', 'none')
    kw.setdefault('xi', x)
    kw.setdefault('xo', x)
    kw.setdefault('window_size', window_size)
    kw['window_function'] = 'triangle'
    ys = smooth_by_convolution(y, **kw)
    if m is not None:
        return x, ys  # MDS mode; got an object with x,y, so return an object with x,y. Allows pyplot.plot(*trismooth()).
    else:
        return ys


@_available_to_user_math
def cicle_fourier_smooth(R, Z, keep_M_harmonics, equalAngle=False, doPlot=False):
    """
    smooth closed periodic boundary by zeroing out high harmonics components

    :param R: x coordinates of the boundary

    :param Z: y coordinates of the boundary

    :param keep_M_harmonics: how many harmonics to keep

    :param equalAngle: use equal angle interpolation, and if so, how many points to use

    :param doPlot: plot plasma boundary before and after

    :return: smoothed R and Z coordinates
    """
    closes = False
    if R[0] == R[-1] and Z[0] == Z[-1]:
        closes = True
        Rc = R
        Zc = Z
        R = R[:-1]
        Z = Z[:-1]
    else:
        Rc = np.hstack((R, R[0]))
        Zc = np.hstack((Z, Z[0]))

    R1 = R
    Z1 = Z

    if equalAngle:
        R0 = np.mean(R)
        Z0 = np.mean(Z)
        T = np.unwrap(np.arctan2(Z - Z0, R - R0))
        T1 = np.linspace(0, 2 * np.pi, equalAngle + 1)[:-1]
        R1 = interp1dPeriodic(T, R - R0)(T1) + R0
        Z1 = interp1dPeriodic(T, Z - Z0)(T1) + Z0
    n = int(len(R1) // 2 - keep_M_harmonics)

    # fourier transform
    Rf = np.fft.fftshift(np.fft.fft(R1))
    Zf = np.fft.fftshift(np.fft.fft(Z1))

    # zero out unwanted harmonics
    Rf[:n] *= 0
    Rf[-n:] *= 0
    Zf[:n] *= 0
    Zf[-n:] *= 0

    # inverse fourier transform
    RS = np.real(np.fft.ifft(np.fft.ifftshift(Rf)))
    ZS = np.real(np.fft.ifft(np.fft.ifftshift(Zf)))

    RSc = np.hstack((RS, RS[0]))
    ZSc = np.hstack((ZS, ZS[0]))

    # plotting
    if doPlot:
        from matplotlib import pyplot

        pyplot.gca().plot(Rc, Zc, 'k', label='original')
        pyplot.gca().plot(RSc, ZSc, 'r', label='smoothed M=%d' % keep_M_harmonics)
        pyplot.gca().set_aspect('equal')

    if closes:
        return RS, ZS
    else:
        return RSc, ZSc


# for backwards compatability
nu_conv = smooth_by_convolution


class FilteredNDInterpolator:
    """
    A class for smoothing ND data. Useful for down-sampling and gridding.

    """

    def __init__(self, points, values, size_scales=None, check_finite=False, std_dev=True, filter_type='median'):
        """
        Mean or median filter interpolate in N dimensions.
        Calculates the mean or median of all values within a size_scale "sphere" of the interpolation point.
        Unlike linear interpolation, you can incorporate information from all your data when down-sampling
        to a regular grid.

        Of course, it would be better to do a weight function (gaussian, hanning, etc) convolution, but the
        "volume" elements required for integration get very computationally expensive in multiple dimensions.
        In that case, try linear interpolation followed by regular-grid convolution (ndimage processing).

        :param points: np.ndarray of floats shape (M, D), where D is the number of dimensions
        :param values: np.ndarray of floats shape (M,)
        :param size_scales: tuple (D,) scales of interest in each dimension
        :param check_finite: bool. Cleans non-finite points and/or values prior to interpolation
        :param std_dev: bool. Estimate uncertainty of mean or median interpolation
        :param filter_type: str. Accepts 'mean' or 'median'

        :Examples:

        This example shows the interpolator is reasonably fast, but note it is nowhere
        near as scalable to 100k+ points as linear interpolation + ndimage processing.

        >> ngrid = 100
        >> width = (0.05, 0.05)
        >> noise_factor = 0.5

        >> def func(x, y):
        >>     return x * (1 - x) * np.cos(4 * np.pi * x) * np.sin(4 * np.pi * y ** 2) ** 2

        >> x = np.linspace(0, 1, ngrid)
        >> y = np.linspace(0, 1, ngrid)
        >> grid_x, grid_y = np.meshgrid(x, y)
        >> xy = np.array(np.meshgrid(x, y)).T.reshape(-1, 2)

        >> fig, axs = pyplot.subplots(3, 2, sharex=True, sharey=True, figsize=(8, 9))
        >> axs[0, 0].set_title('Original')
        >> data = func(grid_x, grid_y)
        >> im = axs[0, 0].imshow(data, extent=(0, 1, 0, 1), origin='lower', aspect='auto')
        >> kw = dict(extent=(0, 1, 0, 1), origin='lower', aspect='auto', clim=im.get_clim())

        >> axs[0, 1].set_title('Noisy')
        >> data = data + (np.random.random(data.shape) - 0.5) * np.ptp(data) * noise_factor
        >> im = axs[0, 1].imshow(data, **kw )

        >> ns = [400, 1600, 6400]
        >> times, nums = [], []
        >> for npts, axi in zip(ns, axs[1:]):
        >>     print('npts = {:}'.format(npts))
        >>     points = np.random.rand(npts, 2)
        >>     values = func(points[:, 0], points[:, 1])
        >>     values = values + (np.random.random((npts,)) - 0.5) * np.ptp(values) * noise_factor

        >>     strt = datetime.datetime.now()
        >>     # ci = ConvolutionNDInterpolator(points, values, xi=xy, window_size=width, window_function='boxcar')
        >>     ci = FilteredNDInterpolator(points, values, size_scales=width, filter_type='mean')(grid_x, grid_y)
        >>     ctime = datetime.datetime.now() - strt
        >>     print('   > Convolution took {:}'.format(ctime))
        >>     times.append(ctime.total_seconds())
        >>     nums.append(npts)

        >>     ax = axi[1]
        >>     ax.set_title('Interpolated {:} pts'.format(npts))
        >>     yi = LinearNDInterpolator(points, values)(grid_x, grid_y)
        >>     im = ax.imshow(nominal_values(yi), **kw)
        >>     l, = ax.plot(points[:, 0], points[:, 1], 'k.', ms=1)

        >>     ax = axi[0]
        >>     ax.set_title('Convolved {:} pts'.format(npts))
        >>     im = ax.imshow(nominal_values(ci), **kw)
        >>     l, = ax.plot(points[:, 0], points[:, 1], 'k.', ms=1)

        >>fig.tight_layout()
        >>axs[0, 0].set_xlim(0, 1)
        >>axs[0, 0].set_ylim(0, 1)

        >>fig, axs = pyplot.subplots()
        >>axs.plot([0] + nums, [0] + times, marker='o')
        >>axs.set_xlabel('# of points')
        >>axs.set_ylabel('time (s)')
        >>print('sec/k ~ {:.3e}'.format(1e3 * np.mean(np.array(times) / ns)))


        This example shows that the median filter is "edge preserving" and contrasts both filters
        with a more sophisticated convolution. Note the boxcar convolution is not identical to the
        mean filter for low sampling because the integral weights isolated points more than very closely
        spaced points.

        >> npts = 50
        >> window = ['hanning', 'gaussian', 'boxcar'][1]
        >> width = 0.05
        >> ped = 0.1
        >> pedwidth = 0.03
        >> fun = lambda x: (0.9-x)*2*(x < 0.9) + 1.0 - np.tanh((x-(1.0-ped))/(0.25*pedwidth))

        >> fig, axs = pyplot.subplots(3, sharex=True, sharey=True)
        >> axs[0].set_title('Pedestal width {:}, Filter Length Scale {:}'.format(pedwidth, width))
        >> for npts, ax in zip([20, 50, 200], axs):
        >>     x0 = np.linspace(0, 1, 1000)

        >>     x1 = np.cumsum(rand(npts))
        >>     x1 = (x1 - min(x1)) / (max(x1) - min(x1))
        >>     y1 = fun(x1) + np.random.random(x1.shape) * 0.4 * fun(x1)
        >>     y1 = uarray(y1, y1 * 0.1)

        >>     t0 = datetime.datetime.now()
        >>     yc = nu_conv(y1, xi=x1, xo=x0, window_size=width, window_function=window, std_dev='propagate')
        >>     tc = datetime.datetime.now() - t0
        >>     print('nu_conv time: {:}'.format(tc))
        >>     t0 = datetime.datetime.now()
        >>     yd = FilteredNDInterpolator(x1.reshape(-1, 1), y1, size_scales=width / 2.)(x0)
        >>     td = datetime.datetime.now() - t0
        >>     print('median filter time: {:}'.format(td))
        >>     t0 = datetime.datetime.now()
        >>     ym = FilteredNDInterpolator(x1.reshape(-1, 1), y1, size_scales=width / 2., filter_type='mean')(x0)
        >>     tm = datetime.datetime.now() - t0
        >>     print('median filter time: {:}'.format(td))

        >>     #ax.plot(x0, fun(x0), label='function')
        >>     uband(x0, yc, ax=ax, lw=3, label='{:} convolution, {:.2f}s'.format(window.title(), tc.total_seconds()))
        >>     uband(x0, ym, ax=ax, lw=3, label='Mean Filter, {:.2f}s'.format(tm.total_seconds()))
        >>     uband(x0, yd, ax=ax, lw=3, label='Median Filter, {:.2f}s'.format(td.total_seconds()))
        >>     uerrorbar(x1, y1, ax=ax, markersize=4, ls='-', lw=0.5, label='{:} data points'.format(npts), color='k')
        >>     ax.legend(loc=0, frameon=False)
        >>     ax.set_ylim([-0.1, 5])
        >> fig.tight_layout()


        """
        from uncertainties import unumpy

        # clean up the input
        sigmas = unumpy.std_devs(values)
        values = unumpy.nominal_values(values)
        points = np.atleast_2d(points)
        nd = points.shape[1]
        if nd >= 10:
            raise RuntimeError("I don't want to do a 10+ dimension convolution. Do you?")
        if is_int(size_scales):
            size_scales = [size_scales] * nd

        # remove nans
        if check_finite:
            valid = np.isfinite(values) * np.product(np.isfinite(points), axis=-1)
            points = points[valid]
            values = values[valid]
            sigmas = sigmas[valid]
            if not values.size:
                return unumpy.uarray(np.arange(xi.shape[0]) * np.nan, np.arange(xi.shape[0]) * np.nan)

        # normalize to relevant length scales
        points_norm = points / size_scales
        offsets = np.mean(points_norm, axis=0)
        points_norm -= offsets[np.newaxis, :]

        # don't bother with errors if there are none
        if np.sum(sigmas) == 0:
            std_dev = False

        self._points_norm = points_norm.astype(np.float16)  # normalized to order 1-100ish by size_scales
        self._size_scales = size_scales
        self._offsets = offsets
        self._std_dev = std_dev
        self._values = values
        self._sigmas = sigmas
        self._ndim = nd
        self._filter_type = filter_type.lower()
        self._force_fast = False

    def __call__(self, *args):
        r"""

        :param \*args: Tuple of D np.ndarrays representing the coordinates of the points to interpolate to.
        :return: Interpolated values at each point (same dimensions as the arrays in args).
        """
        from scipy.spatial import distance_matrix
        from uncertainties import unumpy

        t0 = datetime.datetime.now()
        xx = np.array(args)

        # inform if bad inputs
        if xx.shape[0] != self._ndim:
            raise ValueError("MeanNDInterpolator must be called with the correct number of dimensions")

        # normalize the requested points
        xi = xx.T.reshape(-1, self._ndim)  # (M, D)
        xi_norm = (xi / self._size_scales - self._offsets).astype(np.float16)
        printd('x cleaning took {:}'.format(datetime.datetime.now() - t0))

        # trim points outside region of interest
        valid = (self._points_norm > xi_norm.min(axis=0) - 1) & (self._points_norm < xi_norm.max(axis=0) + 1)
        valid = np.where(np.product(valid, axis=-1))[0]
        points_norm = self._points_norm[valid]
        values = self._values[valid]
        sigmas = self._sigmas[valid]

        # this performs better than anything I did myself
        t0 = datetime.datetime.now()
        distance = distance_matrix(points_norm, xi_norm, p=2, threshold=1000000)
        printd('Distance took {:}'.format(datetime.datetime.now() - t0))

        tn = datetime.datetime.now()
        near = np.less(distance, 1).astype(np.float16)
        num_near = np.sum(near, axis=0)
        near[near == 0] = np.nan
        printd('Sphere nearness took {:}'.format(datetime.datetime.now() - tn))

        tv = datetime.datetime.now()
        if self._filter_type == 'mean':
            vi = np.nanmean(values[:, np.newaxis] * near, axis=0)
        else:
            vi = np.nanmedian(values[:, np.newaxis] * near, axis=0)
        printd('Values took {:}'.format(datetime.datetime.now() - tv))
        ts = datetime.datetime.now()
        if self._std_dev:
            si = np.sqrt(np.nansum(sigmas[:, np.newaxis] ** 2 * near, axis=0)) / num_near
            if self._filter_type != 'mean':
                si *= 1.253
        else:
            si = np.zeros_like(vi)
        printd('Sigmas took {:}'.format(datetime.datetime.now() - ts))

        result = unumpy.uarray(vi, si).reshape(*xx.shape[1:][::-1]).T
        return result


class WeightedAvgBadInput(ValueError, doNotReportException):
    """weighted_avg got some invalid values and has halted."""


@_available_to_user_math
def weighted_avg(x, err=None, minerr=None, return_stddev_mean=False, return_stddev_pop=False, nan_policy='ignore'):
    """
    Weighted average using uncertainty

    Propagates errors and calculates weighted standard deviation. While nu_conv
    does these for a sliding window vs. time, this function is simpler and does
    calculations for a single mean of an array.

    :param x: 1D float array
        The input data to be averaged

    :param err: 1D float array
        Uncertainty in x. Should have the same units as x. Should have the same length as x.
        Special case: a single value of err will be used to propagate errors for the standard
        deviation of the mean, but will produce uniform (boring) weights.
        If no uncertainty is provided (err==None), then uniform weighting is used.

    :param minerr: float
        Put a floor on the uncertainties before calculating weight. This prevents a
        few points with unreasonbly low error from stealing the calculation.
        Should be a scalar with same units as x.

    :param return_stddev_mean: bool
        Flag for whether the standard deviation of the mean (propagated uncertainty)
        should be returned with the mean.

    :param return_stddev_pop: bool
        Flag for whether the standard deviation of the population (weighted standard deviation)
        should be returned with the mean.

    :param nan_policy: str
        'nan': return NaN if there are NaNs in x or err
        'error': raise an exception
        'ignore': perform the calculation on the non-nan elements only (default)

    :return: float or tuple
        mean                 if return_stddev_mean = False and return_stddev_pop = False
        (mean, xpop, xstdm)  if return_stddev_mean = True  and return_stddev_pop = True
        (mean, xpop)         if return_stddev_mean = False and return_stddev_pop = True
        (mean, xstdm)        if return_stddev_mean = True  and return_stddev_pop = False
        where xstdm and xpop are the propagated error and the weighted standard deviation.
    """

    x = np.atleast_1d(x)  # make sure we have an array and not a list
    nx = len(x)
    ne = len(np.atleast_1d(err))

    if np.any(np.isnan(x)) and nan_policy == 'raise':
        raise WeightedAvgBadInput('NaN detected in x values')
    if err is not None and np.any(np.isnan(err)) and nan_policy == 'raise':
        raise WeightedAvgBadInput('NaN detected in uncertainty')
    if (nan_policy == 'nan') and (((err is not None) and np.any(np.isnan(err))) or np.any(np.isnan(x))):
        nans = 1 + return_stddev_mean + return_stddev_pop
        return np.NaN if nans == 1 else (np.NaN,) * nans

    invalid_err = err is None or np.all(err == 0) or (ne != nx and ne != 1) or ((err is not None) and np.all(np.isnan(err)))

    if invalid_err:  # no valid uncertainties provided
        weight = x * 0 + 1
        printd('assigned all weights = 1 because no errors, zero errors, or mismatched lengths', topic='weighted_avg')
    else:
        err = np.atleast_1d(err)  # make sure we have an array and not a list
        if ne == 1:
            # if the user provided only one uncertainty value, they must want us to propagate errors for them.
            # The weighting is trivial in this case, as is the standard deviation of the population.
            # The stddev of the mean is easy, too, but we can calculate it.
            weight = x * 0 + err[0]
            printd(
                'Received only one uncertainty measurement. This will not do anything interesting to the weights, '
                'but it can be used in calculating the error in the mean, so we will take it.',
                topic='weighted_avg',
            )
        else:
            weight = copy.copy(err)
            printd('Got array of errors', topic='weighted_avg')
        eeq0 = err == 0  # Err EQuals 0
        weight[eeq0] = 1.0  # prevent division by 0 because we hate math errors
        if minerr is not None:
            printd('enforcing minimum uncertainty of %f' % minerr, topic='weighted_avg')
            weight[weight < minerr] = minerr  # weight is still holding onto uncertainty
        weight = 1.0 / weight ** 2  # weight = uncertainty^-2
        weight[eeq0] = 0.0  # put the zeros back in
        printd('Formed weights', topic='weighted_avg')

    p = weight / np.nansum(weight)  # normalized weight
    printd('weights have been normalized', topic='weighted_avg')

    xmean = np.nansum(x * p)  # weighted average of x
    printd('the weighted mean is %f' % xmean, topic='weighted_avg')

    xstdm = None
    xpop = None
    if return_stddev_mean or return_stddev_pop and not invalid_err:
        # Calculate standard deviations
        printd('estimating errors in the mean...', topic='weighted_avg')

        # standard deviation of the mean / propagated error in the weighted average
        # (this will be smaller than the errors in individual x measurements)
        xstdm = np.sqrt(np.nansum((p * err) ** 2))
        # standard deviation of the population / scatter in data while accounting for weight
        xpop = np.sqrt(np.nansum(p * (x - xmean) ** 2))
        printd(f'standard deviation of the mean (propagated error) = {xstdm}  ({ xstdm / xmean * 100} %)', topic='weighted_avg')
        printd(f'standard deviation of the population = {xpop}  ({xpop / xmean * 100} %)', topic='weighted_avg')

    if return_stddev_mean:
        if return_stddev_pop:
            printd('return xmean,xpop,xstdm', topic='weighted_avg')
            return xmean, xpop, xstdm
        else:
            printd('return xmean,xstdm', topic='weighted_avg')
            return xmean, xstdm
    else:
        if return_stddev_pop:
            printd('return xmean,xpop', topic='weighted_avg')
            return xmean, xpop
        else:
            printd('return xmean', topic='weighted_avg')
            return xmean


@_available_to_user_math
def firFilter(time_s, data, cutoff_hz, sharpness=0.5, full_output=False):
    """
    Filter signal data with FIR filter (lowpass, highpass)

    :param time_s: time basis of the data signal in seconds

    :param data: data signal

    :param cutoff_hz: a list of two elements with low and high cutoff frequencies [lowFreq,highFreq]

    :param sharpness: sharpness of the filter (taps of the FIR filter = sample_rate/2. * sharpness)

    :param full_output: return filter window and frequency in addition to filtered data

    :returns: filtered data or tuple with filtered data and filter window and frequency as a tuple
    """
    if len(np.atleast_1d(cutoff_hz)) < 2:
        raise Exception('argumen `cutoff_hz` must be a list of two elements [lowFreq,highFreq]')

    from scipy import signal

    sample_rate = 1.0 / np.abs(time_s[1] - time_s[0])
    nyq_rate = sample_rate / 2.0

    if np.isinf(nyq_rate):
        raise ValueError('Problem with time basis of the signal')
    numtaps = int(nyq_rate * sharpness / 2) * 2

    cutoff_hz = np.array(list(map(float, np.atleast_1d(cutoff_hz))))
    cutoff_hz[np.where(cutoff_hz <= 0)[0]] = 0
    cutoff_hz[np.where(cutoff_hz >= nyq_rate)[0]] = nyq_rate

    if cutoff_hz[0] == 0 and cutoff_hz[-1] == nyq_rate:
        return data

    if cutoff_hz[0] == 0:
        fir_coeff = signal.firwin(numtaps, cutoff_hz[-1] / nyq_rate)

    elif cutoff_hz[-1] == nyq_rate:
        if np.mod(numtaps, 2) == 0:
            numtaps += 1  # must be odd if highpass
        fir_coeff = signal.firwin(numtaps, cutoff_hz[0] / nyq_rate, pass_zero=False)

    else:
        fir_coeff = signal.firwin(numtaps, cutoff_hz / nyq_rate, pass_zero=False)

    data = np.hstack(([data[0]] * numtaps, data, [data[-1]] * numtaps))
    out = signal.lfilter(fir_coeff, 1.0, data)
    output = out[int(numtaps * 3 // 2) : -int(numtaps // 2) - np.mod(numtaps, 2)]
    if not full_output:
        return output
    else:
        f = fftfreq(numtaps, 1 / (2 * nyq_rate))
        return output, (f, np.abs(np.fft.fft(fir_coeff)))


@_available_to_user_math
def butter_smooth(xx, yy, timescale=None, cutoff=None, laggy=False, order=1, nan_screen=True, btype='low'):
    """
    Butterworth smoothing lowpass filter.

    Similar to firFilter, but with a notable difference in edge effects
    (butter_smooth may behave better at the edges of an array in some cases).

    :param xx: 1D array
        Independent variable. Should be evenly spaced for best results.

    :param yy: array matching dimension of xx

    :param timescale: float
        [specifiy either timescale or cutoff]
        Smoothing timescale. Units should match xx.

    :param cutoff: float
        [specify either timescale or cutoff]
        Cutoff frequency. Units should be inverse of xx. (xx in seconds, cutoff in Hz; xx in ms, cutoff in kHz, etc.)

    :param laggy: bool
        True: causal filter: smoothed output lags behind input
        False: acausal filter: uses information from the future so that smoothed output doesn't lag input

    :param order: int
        Order of butterworth filter.
        Lower order filters seem to have a longer tail after the ELM which is helpful for detecting the tail of the ELM.

    :param nan_screen: bool
        Perform smoothing on only the non-NaN part of the array, then pad the result out with NaNs to maintain length

    :param btype: string
        low or high. For smoothing, always choose low.
        You can do a highpass filter instead of lowpass by choosing high, though.

    :return: array matching dimension of xx
        Smoothed version of yy
    """

    if nan_screen:
        ok = ~np.isnan(xx) & ~np.isnan(yy)
        yout = np.empty(np.shape(yy))
        yout[:] = np.NaN
        xx = xx[ok]
        yy = yy[ok]
    else:
        yout = ok = None

    cutoff = 1.0 / timescale if cutoff is None else cutoff
    dx = np.mean(np.diff(xx))
    nyquist = 0.5 / dx
    cutoff_norm = cutoff / nyquist
    cutoff_norm = 0.9 if cutoff_norm > 0.9 else cutoff_norm
    printd(
        '   butter_smooth: nyquist = {}, timescale = {}, cutoff = {}, cutoff_norm = {}'.format(nyquist, timescale, cutoff, cutoff_norm),
        topic='butter_smooth',
    )
    b, a = scipy.signal.butter(order, cutoff_norm, btype=btype, analog=False)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Using a non-tuple sequence for multidimensional indexing is deprecated")
        warnings.filterwarnings("ignore", message="underflow encountered in multiply")
        if laggy:
            zi = scipy.signal.lfilter_zi(b, a)
            ys, _ = scipy.signal.lfilter(b, a, yy, zi=zi * yy[0])  # This one lags (the lag actually can help!)
        else:
            ys = scipy.signal.filtfilt(b, a, yy)  # This one doesn't lag

    if nan_screen:
        yout[ok] = ys
        return yout
    else:
        return ys


@_available_to_user_math
class fourier_boundary(object):
    """
    The routines to make and plot Fourier representation of a boundary
    from a list of points
    """

    def __init__(self, nf, rb, zb, symmetric=False):
        self.nf = nf
        self.symmetric = symmetric
        self.make_fourier(nf, rb, zb)

    def make_fourier(self, nf, rb, zb):
        nf2 = max(2048, nf * 2)
        r = np.asarray(rb)
        z = np.asarray(zb)
        self.r0 = (max(r) + min(r)) / 2
        self.z0 = 0
        self.amin = (max(r) - min(r)) / 2
        rad = np.sqrt(np.power(r - self.r0, 2) + np.power(z - self.z0, 2)) / self.amin
        theta = np.arctan2(z - self.z0, r - self.r0)
        ind = theta.argsort()
        rad = rad[ind]
        theta.sort()

        theta2 = np.append(theta, theta + 2.0 * np.pi)
        rad2 = np.append(rad, rad)

        splined_rad = scipy.interpolate.interp1d(theta2, rad2, kind='slinear')

        self.thetafine = np.linspace(0, 2 * np.pi, nf2)
        radfine = splined_rad(self.thetafine)

        four = scipy.fftpack.fft(radfine, n=nf2)

        self.realfour = 2.0 * four.real[: int(nf / 2)] / float(nf2)
        if self.symmetric:
            self.imagfour = np.zeros(int(nf / 2))
        else:
            self.imagfour = -2.0 * four.imag[: int(nf / 2)] / float(nf2)

    def fourier_coef(self):
        return (self.realfour, self.imagfour)

    def reconstruct_boundary(self):

        """Uses the fourier representation and amin, r0 and z0
        parameters to reconstruct the boundary
        """
        nph = np.matrix(range(int(self.nf / 2)))
        if self.symmetric:
            theta = np.matrix(self.thetafine)
        else:
            theta = np.matrix(self.thetafine)
        cm = np.cos(nph.transpose() * theta)
        sm = np.sin(nph.transpose() * theta)
        realf = np.matrix(self.realfour)
        realf[0, 0] = realf[0, 0] / 2
        imagf = np.matrix(self.imagfour)
        rad = self.amin * (realf * cm + imagf * sm)
        self.rf = np.squeeze(self.r0 + np.asarray(rad) * np.cos(self.thetafine))
        self.zf = np.squeeze(self.z0 + np.asarray(rad) * np.sin(self.thetafine))
        return (self.rf, self.zf)


@_available_to_user_math
def fourier(y, t=None):
    """
    Calculate fourier transform

    :param y: signal

    :param t: time basis of the signal (uniformly spaced)

    :return: tuple with Fourier transform of the signal and frequency basis

    >> t=r_[0:1:0.1]
    >> y=np.cos(2*np.pi*t)
    >>
    >> Y,W=fourier(y,t)
    >>
    >> ax=pyplot.subplot(2,1,1)
    >> ax.plot(t,y)
    >> ax.set_xlabel('t [s]')
    >> ax.set_ylabel('$y$')
    >>
    >> ax=pyplot.subplot(2,1,2)
    >> ax.plot(W/2./np.pi,Y)
    >> ax.set_xlabel('f [Hz]')
    >> ax.set_ylabel('$Y$')
    """
    N = len(y)
    if np.all(np.isreal(y)):
        tmp = np.fft.rfft(y)
        Y = np.hstack((np.conj(np.flipud(tmp[1:])), tmp[:-1])) / N
    else:
        tmp = np.fft.fft(y)
        Y = np.fft.fftshift(tmp) / N
    if t is None:
        return Y
    else:
        DT = max(t) - min(t)
        Wmax = (2.0 * np.pi * (N - 1)) / DT / 2.0
        if np.mod(N, 2) == 0:
            w = np.linspace(-Wmax, Wmax, N + 1)[:-1]
        else:
            w = np.linspace(-Wmax, Wmax, N)
        return Y, w


@_available_to_user_math
def windowed_FFT(t, y, nfft='auto', overlap=0.95, hanning_window=True, subtract_mean=True, real_input=None):
    """
    Bin data into windows and compute FFT for each.
    Gives amplitude vs. time and frequency.
    Useful for making spectrograms.

    input:
        :param t: 1D time vector in ms
        :param y: 1D parameter as a function of time
        :param nfft: Number of points in each FFT bin. More points = higher frequency resolution but lower time
            resolution.
        :param overlap: Fraction of window that overlaps previous/next window.
        :param hanning_window: Apply a Hanning window to y(t) before each FFT.
        :param subtract_mean: Subtract the average y value (of the entire data set, not individually per window) before
            calculating FFT
        :param real_input: T/F: Use rfft instead of fft because all inputs are real numbers.
            Set to None to decide automatically.
    output:
        :return: spectral density (time,frequency)
        :return: array of times at the center of each FFT window
        :return: frequency
        :return: amplitude(time, positive frequency)
        :return: power(time, positive frequency)
        :return: positive-only frequency array
        :return: nfft (helpful if you let it be set automatically)

    more on overlap for windows 0, 1, 2:
        overlap = 0.0 : no overlap, window 0 ends where window 1 begins
        overlap = 0.5 : half overlap, window 0 ends where window 2 begins
        overlap = 0.99: this is probably as high as you should go. It will look nice and smooth, but will take longer.
        overlap = 1.0 : FAIL, all the windows would stack on top of each other and infinite windows would be required.

    more on nfft:
        Set nfft='auto' and the function will pick a power of two that should give a reasonable view of the dataset.
        It won't choose nfft < 16.
    """

    printd('Running windowed_FFT()...')

    nt = len(t)  # Length of input array time base
    dt = np.mean(np.diff(t))  # Time step (the time step should be nearly uniform or else FFT doesn't make sense.
    #                     A little bit of noise is probably fine.)

    printd(' nt = {:}, dt = {:}'.format(nt, dt))

    # First round of data sanitization and error checking
    if len(y) != nt:  # Check for input errors
        printe(
            'Windowed FFT Error! Data dimensions do not match! The longer one will be cropped. This could give junk ' 'results! BE CAREFUL!'
        )
        nt = min([nt, len(y)])  # Crop to shorter of the two and try to keep going, but will probably fail
    if nt == 0:  # Check for input errors
        raise OMFITexception('Windowed FFT FATAL ERROR! NO DATA SUPPLIED')

    # Auto detect complex data
    if real_input is None:
        printd('Checking for complex numbers in input...')
        real_input = ~np.any(np.atleast_1d(np.iscomplex(y)))
        printd('Chose real_input = {:}'.format(real_input))

    # Basic setup calculations
    if nfft == 'auto':  # Option to pick nfft automatically based on dataset length. It will always pick a power of 2.
        nfpow = np.round(np.log10(nt / 50.0) / np.log10(2))
        if nfpow < 4:
            nfpow = 4
        nfft = 2 ** nfpow
        printd('auto selected nfft = {:}'.format(nfft))
    nfft = int(nfft)  # Make sure it's an int to prevent problems later

    binSpacingInPoints = int(np.round(nfft * (1.0 - overlap)))  # Space between start of an interval and start of next interval

    # Second round of data sanitization and error checking
    if nt < nfft:  # Check for input errors
        raise OMFITexception('Windowed FFT Error! len(t < nfft! Your data set is smaller than the requested FFT window.')
    if overlap > (nfft - 1.0) / nfft:  # Check for input errors
        raise OMFITexception('Windowed FFT Error! overlap too big! overlap>(1-nfft)/nfft')
    if binSpacingInPoints < 1:  # Check for input errors
        # This is almost the same check as the overlap check, which is okay. We really don't want a problem here.
        raise OMFITexception('Windowed FFT Error! FFT bin-bin spacing too small (try reducing overlap)')

    # Setup
    nBins = 1 + int((nt - nfft) // binSpacingInPoints)  # Number of bins or windows
    printd('number of FFT windows =', nBins)
    printd('number of points in input =', nt)
    printd('number of points in each FFT window =', nfft)
    printd('number of points between the starts of successive bins =', binSpacingInPoints)
    if nBins < 1:
        nBins = 1  # It's nonsensical not to have at least one bin

    if real_input:
        if nfft % 2:
            nfft_out = int((nfft + 1) // 2)
        else:
            nfft_out = int((nfft // 2)) + 1
    else:
        nfft_out = nfft
    f = np.zeros([nBins, nfft_out], dtype='complex')  # Make the array that will receive the data

    # Get a window function
    if hanning_window:
        window = np.hanning(nfft)
    else:
        window = 1.0  # No window

    if subtract_mean:
        # This is useful if your entire data set has a large DC offset. This tries to suppress the zero frequency
        # component and make the plot easier to read. However, the average of each window isn't the same as the average
        # across the entire data set, so the zero frequency component isn't perfectly suppressed by this method.
        offset = -np.mean(y)
    else:
        offset = 0.0

    # Do the FFT on each bin
    for i in range(nBins):
        yy = (y[i * binSpacingInPoints : i * binSpacingInPoints + nfft] + offset) * window
        if real_input:
            ff = np.fft.rfft(yy)
            f[i, :] = ff
        else:
            ff = np.fft.fft(yy)
            f[i, :] = ff

    # Get the frequency
    freq = np.abs(np.fft.fftfreq(nfft, d=dt)[0:nfft_out])

    # Fold in the spectral density from negative frequencies to get amplitude vs. positive frequency only
    if real_input:
        amp = np.abs(f)
        if nfft % 2:
            # nfft is odd, so avoid doubling the zero frequency component
            amp[:, 1:] *= 2
        else:
            # nfft is even, so avoid doubling the zero frequency component and also the nyquist frequency component
            amp[:, 1:-1] *= 2
        freqpos = freq
    else:
        # Get the positive frequency array:
        # If nfft is even, then 0:nfft/2+1 includes the most negative frequency and np.abs() makes it positive.
        # If nfft is odd, then the frequency array is symmetric and 0:nfft/2+1 gets all of the non-negative frequencies.
        freqpos = np.abs(freq[0 : int(nfft // 2) + 1])

        if nfft % 2:
            # Get the amplitude of all positive frequency fluctuations (including 0)
            amppos = np.abs(f[:, 0 : int(nfft // 2) + 1])  # Goes from 0 to nyquist
            # Get the amplitude of all negative freq fluctuations
            ampneg = np.fliplr(np.abs(f[:, int(nfft // 2) + 1 :]))  # Goes from -nyquist to -df
        else:
            # Get the amplitude of all positive frequency fluctuations (including 0)
            amppos = np.abs(f[:, 0 : int(nfft // 2)])  # Goes from 0 to nyquist - df, where df = freq[1] - freq[0]
            # Get the amplitude of all negative freq fluctuations
            ampneg = np.fliplr(np.abs(f[:, int(nfft // 2) :]))  # Goes from -df to -nyquist (after flipping)
            # Add a slot for the highest absolute frequency to the positive freq array
            amppos = np.concatenate([amppos, np.zeros([nBins, 1])], axis=1)  # Now this goes from 0 to nyquist

        # Add a slot for zero frequency to the negative array
        ampneg = np.concatenate([np.zeros([nBins, 1]), ampneg], axis=1)  # Now this goes from 0 to -nyquist

        # The amplitudes for positive and negative frequencies have the same array dimensions and can now be added.
        # If you just double the positive frequencies, you count zero twice, which is naughty. If nfft is even, the
        # nyquist frequency would be counted twice as well.
        amp = amppos + ampneg
    power = amp ** 2  # Power is just amplitude squared
    timebins = t[np.arange(int(nfft // 2), nt - int(nfft // 2) + 1, binSpacingInPoints)]  # These are times at the center of each FFT window

    return f.T, timebins, freq, amp.T, power.T, freqpos, nfft


# -----------
# Signal processing
# -----------
@_available_to_user_math
def noise_estimator(
    t,
    y,
    cutoff_timescale=None,
    cutoff_omega=None,
    window_dt=0,
    dt_var_thresh=1e-9,
    avoid_jumps=False,
    debug=False,
    debug_plot=None,
    restrict_cutoff=False,
):
    """
    Estimates uncertainty in a signal by assuming that high frequency (above cutoff frequency) variation is random noise

    :param t: 1D float array with regular spacing
        (ms) Time base for the input signal
    :param y: 1D float array with length matching t
        (arbitrary) Input signal value as a function of t
    :param cutoff_timescale: float
        (ms) For a basic RC filter, this would be tau = R*C. Define either this or cutoff_omega.
    :param cutoff_omega: float
        (krad/s) The cutoff angular frequency, above which variation is assumed to be noise. Overrides
        cutoff_timescale if specified. cutoff_timescale = 1.0/cutoff_omega
    :param window_dt: float or None
        (ms) Window half width for windowed_fft, used in some strategies for time varying noise.
        If <= 0, one scalar noise estimate is made for the entire range of t, using FFT methods.
        Set to None to choose window size automatically based on cutoff_timescale.
        This option does not seem to be as good as the standard method.
    :param debug: bool
        Flag for activating debugging tests, plots (unless debug_plot is explicitly disabled), and reports.
        Also returns all four estimates instead of just the best one.
    :param debug_plot: bool [optional]
        By default, debug_plot copies the value of debug, but you can set it to False to disable plots and still get
        other debugging features. Setting debug_plot without debug is not supported and will be ignored.
    :param dt_var_thresh: float
        (fraction) Threshold for variability in dt. t must be evenly spaced, so nominally dt will be a constant.
        Because of various real world issues, there could be some slight variation. As long as this is small, everything
        should be fine. You can adjust the threshold manually, but be careful: large variability in the spacing of the
        time base breaks assumptions in the signal processing techniques used by this method.
        If std(dt)/mean(dt) exceeds this threshold, an exception will be raised.
    :param avoid_jumps: bool
        Large jumps in signal will have high frequency components which shouldn't be counted with high frequency noise.
        You SHOULD pick a time range to avoid these jumps while estimating noise, but if you don't want to, you can try
        using this option instead.
        If this flag is true, an attempt will be made to identify time periods when jumps are happening. The time
        derivative, dy/dt, is evaluated at times where there are no detected jumps and interpolated back onto the full
        time base before being integrated to give a new signal. The new signal should have a continuous derivative with
        no spikes, such that its high frequency component should now be just noise. This will prevent the high frequency
        components of a jump in y from bleeding into the noise estimate near the jump. The noise estimate during the
        jump may not be accurate, but you were never going to get a good fix on that, anyway.
        The big problem that is solved by this option is that the jump causes spurious spectral noise which extends well
        before and after the jump itself. Cutting the jump out somehow confines the problem to the relatively narrow
        time range when the jump itself is happening.
    :param restrict_cutoff: bool
        Some versions of scipy throw an error if cutoff_frequency > nyquist frequency, and others do not. If your
        version hates high frequency cutoffs, set this to True and cutoff will be reduced to nyqusit - df/2.0, where
        df is the frequency increment of the FFT, if cutoff >= nyquist.
    :return: 1D uncertain float array with length matching t, or set of four such arrays with different estimates.
        Lowpass smoothed y with uncertainty (dimensions and units match input y)
        The standard estimate is a hilbert envelope of the high frequency part of the signal, times a constant for
        correct normalization::

            ylf = butterworth_lowpass(y, cutoff_frequency)
            yhf = butterworth_highpass(y, cutoff_frequency)
            uncertainty = smooth(hilbert_env(yhf)) * norm_factor
            return = unumpy.uarray(ylf, uncertainty)

        where smoothing of the envelope is accomplished by a butterworth lowpass filter using cutoff_frequency.
        ``norm_factor = np.sqrt(0.5) = std_dev(sin(x))``
        There are other estimates (accessible by setting the debug flag) based on the fluctuation amplitude in the
        windowed FFT above the cutoff frequency.
    """

    from scipy import interpolate as scipy_interpolate

    printd(
        'noise_estimator() called with len(t) = {}, len(y) = {}, cutoff_timescale = {}, cutoff_omega = {}'.format(
            len(t), len(y), cutoff_timescale, cutoff_omega
        )
    )

    # Setup -----------------------

    # Check inputs
    if debug_plot is None:
        debug_plot = debug
    if len(t) != len(y):
        raise ValueError('Dimensions of t and y do not match: {} vs {}'.format(len(t), len(y)))
    if (cutoff_omega is None) and (cutoff_timescale is None):
        raise ValueError('Must specify either cutoff_timescale or cutoff_omega!')
    if (cutoff_omega is not None) and (cutoff_timescale is not None):
        printw('Warning: both cutoff_timescale and cutoff_omega have been specified! ' 'cutoff_omega will override cutoff_timescale!')
    dt = np.diff(t)
    dt_var = np.std(dt) / np.mean(dt)
    if dt_var > dt_var_thresh:
        raise ValueError('t is not evenly spaced: std(dt)/mean(dt) = {} > {}'.format(dt_var, dt_var_thresh))
    dt = np.mean(dt)  # (ms)
    sample_frequency = 1.0 / dt  # (kHz)
    freq = np.fft.fftfreq(len(t), dt)
    df = freq[1] - freq[0]

    if cutoff_omega is None:
        cutoff_omega = 1.0 / cutoff_timescale  # (krad/s)
    cutoff_timescale = 1.0 / cutoff_omega  # (ms)
    cutoff_frequency = cutoff_omega / (2 * np.pi)  # (kHz)
    if window_dt is None:
        window_dt = cutoff_timescale * 5
    nt = len(t)

    nyquist_frequency = sample_frequency * 0.5
    old_cut = None
    if (cutoff_frequency >= nyquist_frequency) and restrict_cutoff:
        # Correct illegal settings
        printw('NOISE_ESTIMATOR: CUTOFF FREQUENCY MUST BE < NYQUIST FREQUENCY.')
        old_cut = cutoff_frequency
        cutoff_frequency = nyquist_frequency - df * 0.5
    elif (cutoff_frequency <= 0) and restrict_cutoff:
        old_cut = cutoff_frequency
        printw('CUTOFF FREQUENCY MUST BE > 0')
        cutoff_frequency = df * 0.5

    if old_cut is not None:
        print('Cutoff frequency modified to obey the rules; it is now {} (was {})'.format(cutoff_frequency, old_cut))
        cutoff_omega = cutoff_frequency * 2 * np.pi
        cutoff_timescale = 1.0 / cutoff_omega

    norm_factor = np.sqrt(0.5)  # std(sin(x)) = np.sqrt(0.5), hilbert_envelope(sin(x)) = 1

    printd(
        'noise_estimator(): cutoff_timescale = {} ms, cutoff_omega = {} krad/s, cutoff_frequency = {} kHz; '
        'dt = {} ms, sample_frequency = {} kHz, window_dt = {} ms'.format(
            cutoff_timescale, cutoff_omega, cutoff_frequency, dt, sample_frequency, window_dt
        )
    )

    # Calculate -----------------------

    def butter_filter(data, cutoff, fs, order=5, btype='high'):
        nyq = 0.5 * fs  # kHz
        normal_cutoff = cutoff / nyq
        b, a = scipy.signal.butter(order, normal_cutoff, btype=btype, analog=False)
        return scipy.signal.filtfilt(b, a, data)

    def est_from_fft(fft_out, df_):
        return abs(np.sum(np.real(fft_out) * df_, 0))

    if avoid_jumps:
        printd('  Avoiding jumps in signal')
        # Detect jumps by checking for unusually large spikes in the derivative
        dydt = np.gradient(y) / dt
        dydts = abs(butter_filter(dydt, cutoff_frequency, sample_frequency, btype='low'))
        thresh = np.percentile(dydts, 90) * 15
        # Interpolate the non-jumping dydt back onto the full timebase to cut jumps out smoothly
        dydt2 = scipy_interpolate.interp1d(t[dydts < thresh], dydt[dydts < thresh], bounds_error=False, fill_value='extrapolate')(t)
        # Integrate
        y_use = integrate.cumtrapz(dydt2, t, initial=0) + y[0]
    else:
        y_use = y
    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=FutureWarning)
        yhf = butter_filter(y_use, cutoff_frequency, sample_frequency)
    fyh = np.fft.fft(yhf)
    est1 = est_from_fft(fyh, df)

    est4 = abs(scipy.signal.hilbert(yhf)) * norm_factor
    est4f = abs(butter_filter(est4, cutoff_frequency, sample_frequency, btype='low'))

    if window_dt > 0:
        overlap = 0.95
        n_windows_0 = (t.max() - t.min()) / (window_dt * 2)
        n_windows = n_windows_0 * (1.0 / (1 - overlap))
        nfft = int(np.ceil(float(nt / n_windows_0)))
        fyht, tw, freqw, amp, power, freqpos, nfft_out = windowed_FFT(t, yhf, nfft=nfft, overlap=overlap, hanning_window=False)
        printd('noise_estimator(): nt = {}, overlap = {}, n_windows = {}, nfft = {}'.format(nt, overlap, n_windows, nfft))
        printd(
            'noise_estimator(): np.shape(fyht) = {}, np.shape(tw) = {}, np.shape(freqw) = {}'.format(
                np.shape(fyht), np.shape(tw), np.shape(freqw)
            )
        )
        dfw = freqw[1] - freqw[0]
        # When doing windowed_fft, the phase of these things vs. time can change, giving different +/- signs at
        # different times. Compensate by multiplying the whole thing by the sign of the highest absolute value at each
        # time.
        fsign = np.array([np.sign(np.real(fyht)[i, abs(fyht[i, :]).argmax()]) for i in range(np.shape(fyht)[0])])
        fyht2 = fyht * fsign[:, np.newaxis]

        est3_a = est_from_fft(fyht2, dfw) * norm_factor
        est3 = abs(scipy_interpolate.interp1d(tw, est3_a, bounds_error=False, fill_value=np.NaN)(t))
        est3f = butter_filter(est3[~np.isnan(est3)], cutoff_frequency / 2.0, sample_frequency, btype='low')
        est3 = abs(scipy_interpolate.interp1d(t[~np.isnan(est3)], est3f, bounds_error=False, fill_value=(est3f[0], est3f[-1]))(t))

        if debug:
            est2_a = est_from_fft(fyht, dfw) * norm_factor
            est2 = scipy_interpolate.interp1d(tw, est2_a, bounds_error=False, fill_value=np.NaN)(t)
            est2f = butter_filter(est2[~np.isnan(est2)], cutoff_frequency / 2.0, sample_frequency, btype='low')
            est2 = abs(scipy_interpolate.interp1d(t[~np.isnan(est2)], est2f, bounds_error=False, fill_value=(est2f[0], est2f[-1]))(t))
        else:
            est2 = 0

        printd(
            "noise_estimator(): np.shape(est3_a) = {}, np.shape(t) = {}, np.shape(est3) = {}".format(
                np.shape(est3_a), np.shape(t), np.shape(est3)
            )
        )
    else:
        est3 = est2 = freqw = fyht2 = dfw = tw = None

    ylf = butter_filter(y_use, cutoff_frequency, sample_frequency, btype='low')

    if debug_plot and debug:
        from matplotlib import pyplot
        from omfit_classes.utils_plot import uband

        fig, axs = pyplot.subplots(2, 2, sharex='col')
        # Plot 1: y vs. t with low frequency components shown
        ax = axs[0, 0]
        ax.plot(t, y, label='y (input)')
        ax.plot(t, y_use, label='y used')
        ax.plot(t, ylf, label='y lowpass')
        # ax.plot(t, yhf+ylf, label='y lowpass + y highpass')
        # uband(t, unumpy.uarray(ylf, est1), ax=ax, label='lowpass w/ simple est uncert')
        ax.plot(t, yhf, label='y highpass')
        ax.set_ylabel('y')
        uband(t, unumpy.uarray(ylf, est4f), ax=ax, label='lowpass w/ est uncert')

        # Plot 2: y vs. t with zero frequency component not included
        ax = axs[1, 0]
        ax.plot(t, yhf, label='y highpass')
        ax.axhline(est1, linestyle='--', label='noise level estimate 1 = {}'.format(est1))
        ax.axhline(-est1, linestyle='--')
        ax.set_ylabel('y')
        ax.set_xlabel('Time (ms)')
        if window_dt > 0:
            est2line = ax.plot(t, est2, label='noise level estimate 2')
            ax.plot(t, -est2, color=est2line[0].get_color())
            est3line = ax.plot(t, est3, label='noise level estimate 3')
            ax.plot(t, -est3, color=est3line[0].get_color())
        est4line = ax.plot(t, est4f, label='noise level estimate 4; avg = {}'.format(np.mean(est4f)))
        ax.plot(t, -est4f, color=est4line[0].get_color())
        ax.axhline(np.std(yhf), linestyle=':', color='k', label='std(yhf) = {}'.format(np.std(yhf)))

        # Plot 3: FFTs
        ax = axs[1, 1]
        ax.set_xlabel('f (kHz)')
        ax.set_ylabel('|FFT|*df')
        fy = np.fft.fft(y)
        fyl = np.fft.fft(ylf)
        # fyhl = np.fft.fft(ylf + yhf)

        fyline = ax.plot(freq[freq > 0], abs(fy[freq > 0]) * df, label='FFT(y)')
        ax.plot(freq[freq > 0], abs(fyl[freq > 0]) * df, label='FFT(y lowpass)')
        # ax.set_xscale("log", nonposx='clip')
        ax.set_yscale("log", nonposy='clip')
        # ax.plot(freq[freq > 0], abs(fyhl[freq > 0])*df, label='FFT(y lowpass + y highpass)')
        ax.plot(freq[freq > 0], abs(fyh[freq > 0]) * df, label='FFT(y highpass)')
        ax.axhline(
            abs(fy[freq == 0]) * df, color=fyline[0].get_color(), linestyle='--', label='FFT(y) @ f=0 ({})'.format(abs(fy[freq == 0]) * df)
        )
        ax.axhline(est1 * df, color='r', label='noise est 1', linestyle='--')

        ax.axvline(cutoff_frequency, color='k', linestyle='--', label='cutoff = {} kHz'.format(cutoff_frequency))

        if window_dt > 0:
            ax.plot(freqw, abs(fyht2[:, 0]) * dfw, label='first window in windowed_FFT')
            printd('np.shape(tw) = {}, np.shape(fyht2) = {}'.format(np.shape(tw), np.shape(fyht2)))

        # Plot 4: windowed FFT
        ax = axs[0, 1]
        if window_dt > 0:
            ax.imshow(np.real(fyht2.T), extent=(freqw.min(), freqw.max(), tw.min(), tw.max()), aspect='auto')
            ax.axvline(cutoff_frequency, color='k', linestyle='--', label='cutoff = {} kHz'.format(cutoff_frequency))

        else:
            # Not needed
            ax.axis('off')

        for ax in axs.flatten():
            ax.legend(loc=0)

    if debug:
        printd(
            "np.shape(ylf) = {}, np.shape(est1) = {}, np.shape(est2) = {}, np.shape(est3), np.shape(est4f) = {}".format(
                np.shape(ylf), np.shape(est1), np.shape(est2), np.shape(est3), np.shape(est4f)
            )
        )
        u1 = unumpy.uarray(ylf, est1)
        u2 = unumpy.uarray(ylf, est2) if est2 is not None else None
        u3 = unumpy.uarray(ylf, est3) if est3 is not None else None
        u4 = unumpy.uarray(ylf, est4f)
        return u1, u2, u3, u4
    else:
        return unumpy.uarray(ylf, est4f)


# -----------
# inverse hyperbolic sine transform
# -----------
@_available_to_user_math
def ihs_opti_transform(x, shift=False, lmbda=None, off=None):
    """
    Calculate the optimal coefficient for the inverse hyperbolic sine transformation of the data

    :param x: input data

    :param shift: calculate and return offset coefficients

    :param lmbda: initial guess for lmbda parameter

    :param off: initial guess for offset parameter

    :return: lmbda and offset coefficients (offset=0 if shift==False)
    """
    N = len(x)
    # compute uniform median statistics
    Ui = np.zeros(N) * 1.0
    Ui[-1] = 0.5 ** (1.0 / N)
    Ui[0] = 1 - Ui[-1]
    i = np.arange(2, N)
    Ui[1:-1] = (i - 0.3175) / (N + 0.365)
    # this function computes the x-axis values of the probability plot
    #  and computes a linear regression (including the correlation)
    #  and returns 1-r so that a minimization function maximizes the
    #  correlation
    from scipy import stats

    xvals = stats.distributions.norm.ppf(Ui)

    m = np.median(np.abs(xvals))
    off_guess = off
    lmbda_guess = lmbda

    def tempfunc1_lmbda(lmbda, off, xvals, samps):
        y = ihs(samps, lmbda, off)
        yvals = np.sort(y)
        r, prob = stats.pearsonr(xvals, yvals)
        c = (1 - r) * (1 + 1e-3 * np.log10(1 + np.abs(lmbda)))
        return c

    def tempfunc1_off(off, lmbda, xvals, samps):
        y = ihs(samps, lmbda, off)
        yvals = np.sort(y)
        r, prob = stats.pearsonr(xvals, yvals)
        c = (1 - r) * (1 + 1e-3 * np.log10(1 + np.abs(off / m)))
        return c

    def tempfunc2(Xopt, xvals, samps):
        lmbda, off = Xopt
        y = ihs(samps, lmbda, off)
        yvals = np.sort(y)
        r, prob = stats.pearsonr(xvals, yvals)
        c = (1 - r) * (1 + 1e-3 * np.log10(1 + np.abs(lmbda)) + 1e-3 * np.log10(1 + np.abs(off / m)))
        return c

    if not shift:
        return [np.abs(optimize.brent(tempfunc1_lmbda, brack=(0.1, 1.0), args=(0.0, xvals, x), tol=1e-2)), 0.0]
    else:
        off = off_guess
        lmbda = lmbda_guess
        if lmbda_guess is None:
            if off_guess is None:
                off = min(x)
            lmbda = np.abs(optimize.brent(tempfunc1_lmbda, brack=(0.1, 1.0), args=(off, xvals, x), tol=1e-0))
        if off_guess is None:
            off = optimize.brent(tempfunc1_off, brack=(min(x), np.mean(x)), args=(lmbda, xvals, x), tol=1e-0)
        return optimize.fmin_l_bfgs_b(
            tempfunc2, [lmbda, off], bounds=((1e-6, None), (None, None)), args=(xvals, x), disp=0, approx_grad=True
        )[0]


@_available_to_user_math
def ihs(x, lmbda=1.0, off=0.0):
    """
    Inverse hyperbolic sine transform: y=np.arcsinh(lmbda*(x-off))/lmbda

    :param x: input data

    :param lmbda: transformation coefficient

    :param off: offset coefficient

    :return: transformed data

    """
    x = np.atleast_1d(x)
    if lmbda == 0:
        return x.copy() - off
    else:
        return np.arcsinh(lmbda * (x - off)) / lmbda


@_available_to_user_math
def iihs(y, lmbda=1.0, off=0.0):
    """
    Inverse of Inverse hyperbolic sine transform: x=np.sinh(y*lmbda)/lmbda+off

    :param y: transformed data

    :param lmbda: transformation coefficient

    :param off: offset coefficient

    :return: original input data

    """
    y = np.atleast_1d(y)
    if lmbda == 0:
        return y.copy() + off
    else:
        return np.sinh(lmbda * y) / lmbda + off


@_available_to_user_math
def array_snippet(a):
    """
    Gives a string summarizing array or list contents: either elements [0, 1, 2, ..., -3, -2, -1] or all elements
    :param a: Array, list, or other compatible iterable to summarize
    :return: String with summary of array, or just str(a) for short arrays
    """
    return '[{}, {}, {}, ..., {}, {}, {}]'.format(a[0], a[1], a[2], a[-3], a[-2], a[-1]) if len(np.atleast_1d(a)) > 6 else str(a)


def ordinal(n, fmt="%d%s"):
    """
    Return ordinal of an integer '1st', '2nd', '3rd', '4th', '5th', ...
    Based on: https://stackoverflow.com/a/20007730/6605826

    :param n: integer

    :param fmt: string format to use ("%d%s" is the default)

    :return: string with ordinal number
    """
    return fmt % (n, "tsnrhtdd"[(np.floor(n // 10) % 10 != 1) * (n % 10 < 4) * n % 10 :: 4])


# -----------
# Display
# -----------
def array_info(inv):
    """
    :param inv: input variable (recarray, np.ndarray)

    :return: string summarizing arrays statistics
    """
    if not hasattr(inv, '__iter__'):
        return str(inv)
    inv0 = inv
    if isinstance(inv, np.recarray):
        if inv.dtype.names is not None:
            return '(' + str(inv.size) + 'x' + str(len(inv.dtype.names)) + ') -> ' + ', '.join(inv.dtype.names)
        else:
            return re.sub('\n', '', str(inv))
    else:
        ndim = len(inv.shape)
        if not inv.size:
            return '[' * ndim + ']' * ndim
        shape = '\t(' + 'x'.join(map(str, inv.shape)) + ')'
        if 'object' in inv.dtype.name:
            return '<%s>' % str(inv.dtype.name) + shape
        elif 's' in str(inv.dtype).lower():
            if len(inv.shape) == 1:
                from utils_widgets import treeText
                return treeText(inv.tolist()) + shape
            else:
                return '<%s>' % str(inv.dtype.name) + shape
        if inv.size <= 3:
            return re.sub('\n', '', str(inv.tolist()))
        elif inv.size > 1e5:
            return '[' * ndim + ' large array - stats not collected ' + ']' * ndim + shape
        try:
            anyInv = ''
            dinv = std_devs(inv.flat)
            if np.nansum(dinv) != 0:
                inv = nominal_values(inv)
                anyInv = '~'
            inv = np.ma.masked_invalid(inv)
            min = np.min(inv)
            max = np.max(inv)
            if np.any(np.ma.getmask(inv)):
                anyInv += '*'
            anyInv = anyInv.rjust(1)
            if min == max:
                return anyInv + '[' * ndim + ' all:' + format(min, ' 3.2E') + ' ' + ']' * ndim + shape
            else:
                mean = np.mean(inv)
                return (
                    anyInv
                    + '[' * ndim
                    + ' ' * np.max(np.array([(3 - ndim), 0]))
                    + ' min:'
                    + format(min, ' 3.2E')
                    + '\tmean:'
                    + format(mean, ' 3.2E')
                    + '\tmax:'
                    + format(max, ' 3.2E')
                    + ' '
                    + ']' * ndim
                    + shape
                )
        except Exception as _excp:
            return str(type(inv0))


# -----------
# roman numerals: : http://diveintopython.org/
# -----------
# Define exceptions
class RomanError(Exception):
    pass


class RomanOutOfRangeError(RomanError):
    pass


class RomanNotIntegerError(RomanError):
    pass


class RomanInvalidNumeralError(RomanError):
    pass


# Define digit mapping
_romanNumeralMap = (
    ('M', 1000),
    ('CM', 900),
    ('D', 500),
    ('CD', 400),
    ('C', 100),
    ('XC', 90),
    ('L', 50),
    ('XL', 40),
    ('X', 10),
    ('IX', 9),
    ('V', 5),
    ('IV', 4),
    ('I', 1),
)


@_available_to_user_math
def toRoman(n):
    """convert integer to Roman numeral"""
    if not (0 < n < 5000):
        raise RomanOutOfRangeError("number out of range (must be 1..4999)")
    if int(n) != n:
        raise RomanNotIntegerError("decimals can not be converted")

    result = ""
    for numeral, integer in _romanNumeralMap:
        while n >= integer:
            result += numeral
            n -= integer
    return result


# Define pattern to detect valid Roman numerals
_romanNumeralPattern = re.compile(
    """
    ^                   # beginning of string
    M{0,4}              # thousands - 0 to 4 M's
    (CM|CD|D?C{0,3})    # hundreds - 900 (CM), 400 (CD), 0-300 (0 to 3 C's),
                        #            or 500-800 (D, followed by 0 to 3 C's)
    (XC|XL|L?X{0,3})    # tens - 90 (XC), 40 (XL), 0-30 (0 to 3 X's),
                        #        or 50-80 (L, followed by 0 to 3 X's)
    (IX|IV|V?I{0,3})    # ones - 9 (IX), 4 (IV), 0-3 (0 to 3 I's),
                        #        or 5-8 (V, followed by 0 to 3 I's)
    $                   # end of string
    """,
    re.VERBOSE,
)


@_available_to_user_math
def fromRoman(s):
    """convert Roman numeral to integer"""
    if not s:
        raise RomanInvalidNumeralError('Input can not be blank')
    if not _romanNumeralPattern.search(s):
        raise RomanInvalidNumeralError('Invalid Roman numeral: %s' % s)

    result = 0
    index = 0
    for numeral, integer in _romanNumeralMap:
        while s[index : index + len(numeral)] == numeral:
            result += integer
            index += len(numeral)
    return result


# -----------
# elements
# -----------
_atomic_table = []


@_available_to_user_math
def atomic_element(
    symbol_A=None, symbol=None, name=None, Z=None, Z_ion=None, mass=None, A=None, abundance=None, use_D_T=True, return_most_abundant=True
):
    """
    Returns dictionary with name, symbol, symbol_A, Z, mass, A, abundance information of all the
    elements that match a a given query.
    Most of the information was gathered from: http://www.sisweb.com/referenc/source/exactmas.htm
    returns dictionary with name, symbol, symbol_A, Z, mass, A, abundance information of all the
    elements that match a a given query

    :param symbol_A: string
        Atomic symbol followed by the mass number in parenthesis eg. H(2) for Deuterium

    :param symbol: string
        Atomic symbol
           * can be followed by the mass number eg. H2 for Deuterium
           * can be prepreceded the mass number and followed by the ion charge number eg. 2H1 for Deuterium

    :param name: string
        Long name of the atomic element

    :param Z: int
        Atomic number (proton count in nucleus)

    :param Z_ion: int
        Charge number of the ion (if not specified, it is assumed `Z_ion = Z`)

    :param mass: float
        Mass of the atomic element in AMU
        For matching, it will be easier to use A

    :param A: int
        Mass of the atomic element rounded to the closest integer

    :param abundance: float
        Abundance of the atomic element as a fraction 0 < abundance <= 1

    :param use_D_T: bool
        Whether to use deuterium and tritium for isotopes of hydrogen

    :param return_most_abundant: bool
        Whether only the most abundant element should be returned for a query that matches multiple isotopes


    :return: dictionary with all the elements that match a query
    """
    # Load atomic data table if not done already
    if not len(_atomic_table):
        import json

        with open(os.path.split(__file__)[0] + os.sep + 'atomic_elements.json') as f:
            _atomic_table.append(json.load(f))

    if symbol:
        match = re.match(r'(\d*)([a-zA-Z]+)(\d*)$', symbol)
        if not match:
            raise ValueError('Wrong form of symbol, expected H, H2, or 2H1 or similar, but got %s' % symbol)
        symbol = match.groups()[1]
        if match.groups()[0] == '' and match.groups()[2] != '':
            A = int(match.groups()[2])
        elif match.groups()[0] != '' and match.groups()[2] != '':
            A = int(match.groups()[0])
            Z_ion = int(match.groups()[2])

    # Query dictionary
    kw = {'name': name, 'symbol': symbol, 'symbol_A': symbol_A, 'Z': Z, 'mass': mass, 'A': A, 'abundance': abundance}
    kw = {item: kw[item] for item in kw if kw[item] is not None}

    # Find matches
    matches = {}
    for item in _atomic_table[0]:
        match = True
        for query in kw:
            if kw[query] and _atomic_table[0][item][query] != kw[query]:
                match = False
                break
        if match:
            matches[item] = copy.deepcopy(_atomic_table[0][item])
            if Z_ion is None:
                matches[item][u'Z_ion'] = int(matches[item]['Z'])
            else:
                matches[item][u'Z_ion'] = int(Z_ion)

    # Return most abundant
    if return_most_abundant:
        tmp = {}
        for item in matches:
            if matches[item]['symbol'] not in tmp or tmp[matches[item]['symbol']]['abundance'] < matches[item]['abundance']:
                tmp[matches[item]['symbol']] = matches[item]
        matches.clear()
        for item in tmp:
            matches[tmp[item]['symbol_A']] = tmp[item]

    # Remove D(2) and T(3) if they are not allowed (use_D_T=False)
    if len(matches) > 1:
        for item in list(matches.keys()):
            if not use_D_T and (matches[item]['symbol_A'] == 'D(2)' or matches[item]['symbol_A'] == 'T(3)'):
                del matches[item]
            elif use_D_T and (matches[item]['symbol_A'] == 'H(2)' or matches[item]['symbol_A'] == 'H(3)'):
                del matches[item]

    # Handle no matches
    if not len(matches):
        raise ValueError('No atomic element satisfies %s' % ', '.join(['%s=%s' % (k[0], repr(k[1])) for k in list(kw.items())]))

    return matches


@_available_to_user_math
def element_symbol(z, n=None):
    """
    Return the element symbol given the charge (and possibly the number of neutrons)

    :param z: Ion's charge (number of protons)

    :param n: Ion's number of nucleons

    :return: Element symbol (1 or 2 character string)

    :note: If z==-1, then 'elec' is returned
    """
    if z == -1:
        return 'elec'
    else:
        return list(atomic_element(Z=z, A=n).values())[0]['symbol']


@_available_to_user_math
def element_label(**kw):
    """
    Return a LaTeX formatted string with the element's symbol, charge state as superscript, and optionally mass number
    as subscript.
    :param z_n or zn: int
        Nuclear charge / atomic number
    :param z_a or za: int [optional]
        Ionic charge, including any electrons which may be bound.
        Defaults to displaying fully-stripped ion if not specified (z_a = z_n).
    :param zamin: int
        Minimum for a range of Zs in a bundled charge state (like in SOLPS-ITER)
    :param zamax: int
        Minimum for a range of Zs in a bundled charge state (like in SOLPS-ITER)
    :param a or am: int [optional]
        Mass number. Provides additional filter on results.
    :return: string
        Prettily formatted symbol
    """
    z_n = kw.pop('z_n', kw.pop('zn', None))
    assert z_n is not None, 'Must specify z_n or zn'
    z_a = kw.pop('z_a', kw.pop('za', None))
    zamin = kw.pop('zamin', None)
    zamax = kw.pop('zamax', None)
    a = kw.pop('a', kw.pop('a_m', None))
    if z_n == -1:
        return '$e^-$'
    else:
        if z_a is not None:
            za = '%0d' % int(z_a)
        elif z_a is None and zamin is None and zamax is None:
            za = '%0d' % int(z_n)
        elif z_a is None and zamax > zamin:
            za = '{:0d}-{:0d}'.format(int(zamin), int(zamax))
        elif z_a is None and zamax == zamin and zamax is not None:
            za = '%0d' % int(zamin)
        else:
            za = '?'
            printw('WARNING: This code should not be reached. You may have weird z_a/zamin/zamax settings.')
        data = list(atomic_element(Z=z_n, A=a, return_most_abundant=True, use_D_T=a is not None).values())[0]
        return '${symbol:}^{{+{z_a:}}}$'.format(symbol=data['symbol'], z_a=za)


def z_from_symbol(symbol):
    """
    Given an atomic element symbol it returns it charge Z

    :param symbol: element symbol

    :return: element charge Z
    """
    return list(atomic_element(symbol=symbol).values())[0]['Z']


# -----------
# tension splines
# -----------
def _coefsplinet(t, y, tau):
    """
    Spline coefficients
    By VICTOR AGUIAR
    NUMERICAL ANALYSIS OF KINCAID

    :param t: nodes location

    :param y: value at the nodes

    :param x: return values at

    :param tau: tension
    """
    ## step 1:
    ## order t and y
    n = len(t)
    ## Create the arrays that will be filled up.
    delta = h = list(range(0, n - 1))
    ## Order the table from less to high.
    ind = t.argsort()
    t = t[ind]
    y = y[ind]
    ## step 2:
    ## compute h, a,b,o as described in Kincaid book
    h = t[1:n] - t[0 : n - 1]
    a = (1 / h) - (tau / np.sinh(tau * h))
    b = (tau * np.cosh(tau * h) / np.sinh(tau * h)) - (1 / h)
    g = (tau ** 2) * (y[1:n] - y[0 : n - 1]) / h
    ## step 3:
    ## initialize Zi or coefficients of spline
    z = np.zeros(n - 1)
    ## step 4:
    ## solve tri-diagonal system for Zi 1<=i<=n-1
    ## output
    nz = len(z)
    v = g[1:nz] - g[0 : nz - 1]
    ## matrix of coefficients
    diagel = b[0 : nz - 1] + b[1:nz]
    A = np.diag(diagel)
    ## complete the matrix
    na = len(a)
    a2 = a[1 : na - 1]
    a3 = a2 = np.diag(a2)
    dum1 = np.zeros((1, na - 2))
    dum2 = np.zeros((na - 1, 1))
    a2 = np.vstack([a2, dum1])
    a2 = np.hstack([dum2, a2])
    a3 = np.vstack([dum1, a3])
    a3 = np.hstack([a3, dum2])
    ## solve system using scipy library!!
    ## get zi
    A = A + a2 + a3
    z = np.linalg.solve(A, v)
    z = np.hstack([0, z, 0])
    return z, h


@_available_to_user_math
def splinet(t, y, x, tau):
    """
    Tension spline evaluator
    By VICTOR AGUIAR
    NUMERICAL ANALYSIS OF KINCAID

    :param t: nodes location

    :param y: value at the nodes

    :param x: return values at

    :param tau: tension
    """
    ind = t.argsort()
    t = t[ind]
    y = y[ind]
    x = np.sort(x)
    n = np.size(t)
    nx = np.size(x)  # x can be a vector
    ## INPUTS
    x = np.array(x)  # Evaluates  t,y in x
    sy = list(range(nx))  # sy is the image of x under the spline function.
    z, h = _coefsplinet(t, y, tau)
    m = np.size(z)
    ## evaluation
    for i in range(nx):
        dif = list((x[i] - t) >= 0)
        if dif[n - 1] != True:
            index = dif.index(False)
            if index == 0 or index == 1:
                index = 0
                sum1 = z[index] * np.sinh(tau * (t[index + 1] - x[i]))
                sum2 = z[index + 1] * np.sinh(tau * (x[i] - t[index]))
                div1 = (tau ** 2) * np.sinh(tau * h[index])
                sum3 = (y[index] - (z[index] / tau ** 2)) * (t[index + 1] - x[i]) / h[index]
                sum4 = (y[index + 1] - (z[index + 1] / (tau ** 2))) * (x[i] - t[index]) / h[index]
                sy[i] = ((sum1 + sum2) / div1) + sum3 + sum4
            else:
                index = index - 1
                sum1 = z[index] * np.sinh(tau * (t[index + 1] - x[i]))
                sum2 = z[index + 1] * np.sinh(tau * (x[i] - t[index]))
                div1 = (tau ** 2) * np.sinh(tau * h[index])
                sum3 = (y[index] - (z[index] / tau ** 2)) * (t[index + 1] - x[i]) / h[index]
                sum4 = (y[index + 1] - (z[index + 1] / tau ** 2)) * (x[i] - t[index]) / h[index]
                sy[i] = (sum1 + sum2) / div1 + sum3 + sum4
        else:
            index = n - 2
            sum1 = z[index] * np.sinh(tau * (t[index + 1] - x[i]))
            sum2 = z[index + 1] * np.sinh(tau * (x[i] - t[index]))
            div1 = (tau ** 2) * np.sinh(tau * h[index])
            sum3 = (y[index] - (z[index] / tau ** 2)) * (t[index + 1] - x[i]) / h[index]
            sum4 = (y[index + 1] - (z[index + 1] / tau ** 2)) * (x[i] - t[index]) / h[index]
            sy[i] = (sum1 + sum2) / div1 + sum3 + sum4
    ##return the image
    return sy


class CLSQTensionSpline(object):
    """
    Constrained least square tension spline.

    :param x: np.ndarray. Data grid.

    :param y: np.ndarray. Data values.

    :param t: int or np.ndarray. Knot number or locations.

    :param tau: float. Tension (higher is smoother).

    :param w: np.ndarray. Data weights (usually ~1/std_devs)

    :param xbounds: tuple. Minimum and maximum x of knot locations.

    :param min_separation: float. Minumum separation between knot locations.

    :param xy_constraints: list of tuples. Spline is constrained to have these values at these locations.

    :param xyprime_constraints: Spline is constrained to have these derivatives as these locations.

    :param optimize_knot_type: str. choose 'xy' to simultaneously optimize knot (x,y) values, 'x' to optimize
        x and y separately, and 'y' to simply use the prescribed knot locations.

    :Examples:

    Using the same data from the LSQUnivariateSpline examples,

    >> x = np.linspace(-3, 3, 50)
    >> y = np.exp(-x**2) + 0.1 * np.random.randn(50)

    We can fit a tension spline. We can even set some boundary constraints.

    >> t = [-1, 0, 1]
    >> spl = CLSQTensionSpline(x, y, t, tau=0.1, xy_constraints=[(-3,0)])
    >> xs = np.linspace(-3, 3, 1000)
    >> pyplot.subplots()
    >> pyplot.plot(x, y, marker='o', lw=0)
    >> pyplot.plot(xs, spl(xs))

    Note the xknots are optimized by default. We can compare to the un-optimized knot locations,
    but (for historical reasons) we wont be able to set constraints.

    >> sply = CLSQTensionSpline(x, y, t, tau=0.1, xy_constraints=[(-3,0)], optimize_knot_type='y')
    >> pyplot.plot(xs, sply(xs))

    """

    def __init__(
        self,
        x,
        y,
        t,
        tau=1,
        w=None,
        xbounds=(None, None),
        min_separation=0,
        xy_constraints=(),
        xyprime_constraints=(),
        optimize_knot_type='xy',
    ):
        """

        :param x: np.ndarray. Data grid.

        :param y: np.ndarray. Data values.

        :param t: int or np.ndarray. Knot number or locations.

        :param tau: float. Tension (higher is smoother).

        :param w: np.ndarray. Data weights (usually ~1/std_devs)

        :param xbounds: tuple. Minimum and maximum x of knot locations.

        :param min_separation: float. Minumum separation between knot locations.

        :param xy_constraints: list of tuples. Spline is constrained to have these values at these locations.

        :param xyprime_constraints: Spline is constrained to have these derivatives as these locations.

        :param optimize_knot_type: str. choose 'xy' to simultaneously optimize knot (x,y) values, 'x' to optimize
            x and y separately, and 'y' to simply use the prescribed knot locations.

        """
        # store variables
        if is_int(t):
            self._xknots = np.linspace(min(x), max(x), t)
        else:
            self._xknots = np.atleast_1d(t)
        if w is None:
            w = np.ones_like(x)
        # be robust to typical shorthand
        if xy_constraints is None:
            xy_constraints = ()
        if np.shape(xy_constraints) == (2,):
            xy_constraints = (xy_constraints,)
        if xyprime_constraints is None:
            xyprime_constraints = ()
        if np.shape(xyprime_constraints) == (2,):
            xyprime_constraints = (xyprime_constraints,)

        self._data = np.array([x, y])
        self._weights = w

        self._tau = tau
        self._min_sep = min_separation
        self._xyc = xy_constraints
        self._xyp = xyprime_constraints

        if xbounds is None or np.shape(xbounds) != (2,):
            xbounds = (None, None)
        self._xbounds = np.array(xbounds)

        # optimize knot values
        optimize_knot_type = optimize_knot_type.lower()
        if optimize_knot_type == 'xy':
            self._set_xyknots()  # optimize knot x,y pairs
        elif optimize_knot_type == 'x':
            self._set_xyknots()  # optimize the x of knots, optimizing y at each step
        elif optimize_knot_type == 'y':
            if len(xy_constraints) or len(xyprime_constraints):
                printe("WARNING: Constraints are not considered if only optimizing knot y values.")
            self._yknots = self._get_yknots()  # just get the best y for each given knot x

    def __call__(self, x):
        """

        :param x: np.ndarray. Desired x grid.

        :return: Interpolated y values.

        """
        return splinet(self._xknots, self._yknots, np.atleast_1d(x), self._tau)

    def _set_xyknots(self, xknots=None):
        """Simultaneous optimization of the x and y of each knot."""
        if xknots is None:
            xknots = self._xknots * 1.0

        # fit knots in a 1 by 1 box
        xnorm = np.ptp(self._data[0])
        x = self._data[0] / xnorm
        xbounds = self._xbounds
        ibounds = [i for i, v in enumerate(xbounds) if v is not None]
        xbounds[ibounds] /= xnorm
        xknots = xknots / xnorm
        min_sep = self._min_sep / xnorm

        ynorm = np.ptp(self._data[1])
        y = self._data[1] / ynorm
        w = self._weights * ynorm

        xyc = [(xc / xnorm, yc / ynorm) for xc, yc in self._xyc]
        xyp = [(xc / xnorm, yc / ynorm) for xc, yc in self._xyp]

        tau = self._tau
        nk = len(xknots)

        def cost(xyknots):
            xknots = xyknots[:nk]
            yknots = xyknots[nk:]
            try:
                f = splinet(xknots, yknots, x, tau)
            except Exception as error:
                print(error)
                f = 0 * y
            return np.sum(((y - f) * w) ** 2)

        # initial guess of knots
        args0 = np.ravel([xknots, interp1e(x, y)(xknots)])
        # global bounds
        bounds = [xbounds] * nk + [(min(y) - np.ptp(y), max(y) + np.ptp(y))] * nk
        # relational constraints
        cons = []
        if self._min_sep > 0:
            for i in range(nk - 1):
                cons.append({'type': 'ineq', 'fun': lambda x, i=i: (x[i + 1] - x[i]) - min_sep})
        for xc, yc in xyc:
            cons.append({'type': 'eq', 'fun': lambda x, xc=xc, yc=yc: splinet(x[:nk], x[nk:], [xc], tau)[0] - yc})
        eps = 1e-8  # consistent with default minimize steps
        for xp, yp in xyp:
            cons.append(
                {
                    'type': 'eq',
                    'fun': lambda x, xp=xp, yp=yp: (
                        splinet(x[:nk], x[nk:], [xp + eps / 2.0], tau)[0] - splinet(x[:nk], x[nk:], [xp - eps / 2.0], tau)[0]
                    )
                    / eps
                    - yp,
                }
            )
        options = {"eps": 1e-8}
        self.opt = optimize.minimize(cost, args0, bounds=bounds, constraints=cons, options=options)
        self._xknots = self.opt.x[:nk] * xnorm
        self._yknots = self.opt.x[nk:] * ynorm
        if not self.opt['success']:
            printe("WARNING: Optimizer failed due to\n{:}".format(self.opt['message']))

    def _get_yknots(self, xknots=None):
        """Original optimization of yknots given fixed xknots"""
        x, y = self._data
        w = self._weights
        tau = self._tau
        if xknots is None:
            xknots = self._xknots

        def cost(y0):
            f = splinet(xknots, y0, x, tau)
            return np.sum(((y - f) * w) ** 2)

        y0 = interp1e(x, y)(xknots)
        bounds = [(min(y) - np.ptp(y), max(y) + np.ptp(y))] * len(xknots)
        y0 = optimize.fmin_l_bfgs_b(cost, y0, args=(), bounds=bounds, approx_grad=True)[0]
        return y0

    def _set_xknots(self, xknots=None):
        """
        Optimize the xknots, using the original LSQUnivariateSplineT method for
        finding the yknots given xknots.

        """
        if xknots is None:
            xknots = self._xknots * 1.0

        # fit knots in a unit box
        xnorm = np.ptp(self._data[0])
        x = self._data[0] / xnorm
        xbounds = self._xbounds
        ibounds = [i for i, v in enumerate(xbounds) if v is not None]
        xbounds[ibounds] /= xnorm
        xknots = xknots / xnorm
        min_sep = self._min_sep / xnorm

        ynorm = np.ptp(self._data[1])
        y = self._data[1] / ynorm
        w = self._weights * ynorm

        xyc = [(xc / xnorm, yc / ynorm) for xc, yc in self._xyc]
        xyp = [(xc / xnorm, yc / ynorm) for xc, yc in self._xyp]

        tau = self._tau
        nk = len(xknots)

        def temp_spline(xknots, xnew):
            try:
                yknots = _get_yknots(x, y, xknots, tau=tau, w=w)
                s = splinet(xknots, yknots, xnew, tau)
            except Exception as error:
                print(error)
                s = 0 * xnew
            return s

        def cost(xknots):
            s = temp_spline(xknots, x)
            return np.sum(((y - s) * w) ** 2)

        # initial guess of knots
        args0 = xknots
        # global bounds
        bounds = [xbounds] * nk
        # relational constraints
        cons = []
        if self._min_sep > 0:
            for i in range(nk - 1):
                cons.append({'type': 'ineq', 'fun': lambda x, i=i: (x[i + 1] - x[i]) - min_sep})
        for xc, yc in self._xyc:
            cons.append({'type': 'eq', 'fun': lambda x: temp_spline(x, [xc])[0] - yc})
        eps = 1e-8  # consistent with default minimize steps
        for xc, yp in self._xyp:
            cons.append(
                {'type': 'eq', 'fun': lambda x: (temp_spline(x, [xc + eps / 2.0])[0] - temp_spline(x, [xc - eps / 2.0])[0]) / eps - yp}
            )
        options = {"eps": 1e-8}
        self.opt = optimize.minimize(cost, args0, bounds=bounds, constraints=cons, options=options)
        self._xknots = opt.x * xnorm
        self._yknots = _set_yknots(x, y, self._xknots, tau=tau, w=w) * ynorm
        if not self.opt['success']:
            printe("WARNING: Optimizer failed due to\n{:}".format(self.opt['message']))

    def get_knots(self):
        """
        Get the x locations of knots

        :return: tuple. list of (x, y) tuples of knot location and value.

        """
        knots = list(zip(self._xknots * 1, self._yknots * 1))
        return knots

    def get_knot_locations(self):
        """
        Get the x locations of knots

        :return: tuple. (x, y) knot location and value.

        """
        return self._xknots * 1

    def get_knot_values(self):
        """
        Get the x locations of knots

        :return: tuple. (x, y) knot location and value.

        """
        return self._yknots * 1


class AutoUnivariateSpline(interpolate.UnivariateSpline):
    """
    Class of univariate spline with smoothing optimized for reduced chi squared
    assuming w=1/std_devs.

    If no weight is supplied, it is taken to be 1/std_devs(y) and these should all
    be finite for this to make sense.

    :Examples:

    If we have some curve of data with meaningful deviations beyond the errorbars,

    >> nx = 50
    >> x = np.linspace(-3, 3, nx)
    >> y = np.exp(-x**2) + 0.3 * (np.random(nx) - 0.5)
    >> u = unumpy.uarray(y, 0.1 * np.ones(nx))
    >> fig, ax = pyplot.subplots()
    >> uerrorbar(x, u, marker='o', label='data', ax=ax)

    The scipy default spline uses smoothing s = len(x),

    >> xs = np.linspace(min(x), max(x), 1000)
    >> spl = UnivariateSpline(x, y, w = 1/std_devs(u))
    >> ax.plot(xs, spl(xs), label='default spline')

    but the unceratinties spline optimizes the smoothing for reduced chi squared ~1,

    >> uspl = AutoUnivariateSpline(x, u)
    >> ax.plot(xs, uspl(xs), label='auto spline')
    >> ax.legend()

    The figure shows the uncertainties spline more accurately captures the meaningful deviations beyond the errorbars.
    In numbers,

    >> default_smooth = spl._data[6]
    >> default_rchisq = spl.get_residual() / (nx - (len(spl.get_coeffs()) + len(spl.get_knots()) - 2))
    >> print('Default smoothing is {:.1f} results in reduced chi squared {:.1f}'.format(default_smooth, default_rchisq))
    >> print('Optimal smoothing of {:.1f} results in reduced chi squared {:.1f}'.format(uspl.get_smoothing_factor(),
    ...                                                                                  uspl.get_reduced_chisqr()))

    If the difference is not large, try running again (the deviations are random!).

    To see how the optimizer arrived at the result, you can get the full evolution. Remember, it is targeting
    a reduced chi squared of unity.

    >> s, f = uspl.get_evolution(norm=False)
    >> fig, ax = pyplot.subplots()
    >> ax.plot(s, f, marker='o', ls='')  # all points tested
    >> ax.plot([uspl.get_smoothing_factor()], [uspl.get_reduced_chisqr() - 1], marker='s')  # final value
    >> ax.set_xscale('log')
    >> ax.set_xlabel('s')
    >> ax.set_ylabel('Reduced chi squared - 1')

    """

    def __init__(self, x, y, w=None, bbox=(None, None), k=3, ext=0, check_finite=False, max_interior_knots=None, verbose=False):
        """
        :param x: np.ndarray. Must be increasing

        :param y: unumpy.uarray. Uncertainties array from uncertainties.unumpy.

        :param w: np.ndarray. Optionally overrides uncertainties from y. Assumed to be 1/std_devs of gaussian errors.

        :param bbox: (2,) array_like. 2-sequence specifying the boundary of the approximation interval.

        :param k: int. Degree of the smoothing spline. Must be 1 <= k <= 5. Default is k=3, a cubic spline.

        :param ext: int or str. Controls the extrapolation mode for elements not in the knot interval. Default 0.
            if ext=0 or 'extrapolate', return the extrapolated value.
            if ext=1 or 'zeros', return 0
            if ext=2 or 'raise', raise a ValueError
            if ext=3 of 'const', return the boundary value.

        :param check_finite: bool. Whether to check that the input arrays contain only finite numbers.

        :param max_interior_knots: int. Maximum number of interior knots in a successful optimization.
            Use this to enforce over smoothing.

        :param verbose: bool. Print warnings

        """
        from uncertainties import unumpy

        printd('Initializing AutoUnivariateSpline')
        # split the uncertainties array into its components
        yn = unumpy.nominal_values(y)
        ye = unumpy.std_devs(y)
        if w is None:
            if is_uncertain(y):
                w = 1.0 / ye
            else:
                w = np.ones_like(y) / (0.01 * np.mean(np.abs(y)))  # assume ~1% error
        # Sanitize x, y, e data
        if check_finite:
            w[w == np.inf] = max(w[w != np.inf]) * 1e6  # inf weight makes all residuals inf - can't optimize that
            valid = np.isfinite(x) * np.isfinite(yn) * np.isfinite(w)
            xv = x[valid]
            yv = yn[valid]
            wv = w[valid]
            printd(' - removed {:} of {:} values checking finite status'.format(len(valid) - len(xv), len(valid)))
            check_finite = False
        else:
            xv, yv, wv = x, yn, w
        # defaults
        nx = len(xv)
        # key word arguments always passed to smoothed splines
        kwargs = dict(w=wv, bbox=bbox, k=k, ext=ext, check_finite=check_finite)

        self._fev = []
        self._sev = []

        def cost(s):
            """Reduced chi squared of a smoothed spline"""
            fit = interpolate.UnivariateSpline(xv, yv, s=max(s, 0.0) * nx, **kwargs)
            res = fit.get_residual()
            nfree = len(fit.get_coeffs()) + len(fit.get_knots()) - 2
            nob = fit._data[0].shape[0]
            if (nob - nfree) <= 0:  # plateau when vastly under smoothing
                printd(' ** forcing the over-smooth plateau on vastly under-smoothed spline')
                fit = interpolate.LSQUnivariateSpline(xv, yv, t=(), **kwargs)
                res = fit.get_residual()
                nfree = len(fit.get_coeffs()) + len(fit.get_knots()) - 2
                nob = fit._data[0].shape[0]
            fun = np.abs(res / (nob - nfree) - 1)
            printd('s={:}, res = {:}, cost = {:}'.format(s, res, fun))
            self._sev.append(s[0])
            self._fev.append(fun)
            return fun

        # optimize the scaling factor on the default s=nx, so the optimizer should be dealing in order 1
        # Multiplied the sum((wv - yv)**2) to be robust to crazy weights like 1 when the data is ~1e19
        shigh = np.sum((wv * yv) ** 2) / nx  # very smooth (ok with a all 0 fit)
        slow = 1e-4 * shigh
        if max_interior_knots is not None:

            def check_max_knots(s):
                if isinstance(s, list):
                    s = s[0]
                check = max_interior_knots + 2.0 - len(interpolate.UnivariateSpline(xv, yv, s=max(s, 0.0) * nx, **kwargs).get_knots())
                printd('s = {:}, check = {:}'.format(s, check))
                return check

            # make sure we start somewhere valid
            for f1, f2 in zip(np.logspace(-7, 1, 9)[:-1], np.logspace(-7, 1, 9)[1:]):
                if check_max_knots(shigh * f2) >= 0:
                    # fine tune between higher and lower logscale factors
                    for l1, l2 in zip(np.linspace(f1, f2, 5, True)[:-1], np.linspace(f1, f2, 5, True)[1:]):
                        if check_max_knots(shigh * l2) >= 0:
                            slow = shigh * l1  # lower bound
                            shigh *= l2
                            break
                    break
            cons = [{'type': 'ineq', 'fun': check_max_knots}]
            bounds = [(slow, 10 * shigh)]  # I don't think COBYLA actually uses this, but SLSQP doesn't do ineq's
            method = 'COBYLA'
            options = dict(rhobeg=1e-3 * (bounds[0][1] - bounds[0][0]))
        else:
            check_max_knots = lambda s: 1
            cons = ()
            bounds = [(slow, shigh)]
            method = None
            options = {}

        # optimize the knots/coeffs
        self.opt = optimize.minimize(cost, (slow + shigh) * 0.5, bounds=bounds, constraints=cons, method=method, options=options)
        if not self.opt['success'] or not check_max_knots(self.opt.x) >= 0:
            # try over smoothing?
            # s1 = s0 * 100
            # self.opt = optimize.minimize(cost, s1, bounds=[(0.1 * s1, 100 * s1)], constraints=cons, method=method)
            # just bound it from our brute force (robust but might miss a smaller s0 optimum for fear of breaking cons)
            bounds = [(slow, shigh)]
            printd('  ** Falling back to unconstrained optimization between {:}'.format(bounds))
            self.opt = optimize.minimize(cost, shigh, bounds=bounds, method='L-BFGS-B')
            if not self.opt['success']:
                printe("WARNING: Optimizer failed due to\n{:}".format(self.opt['message']))
                if max_interior_knots is not None:
                    self.opt.x = shigh  # go with our brute search lowest smoothing that met the constraint optimum
            if not check_max_knots(self.opt.x) >= 0:
                printe("WARNING: Optimizer failed to minimize red-chi2 with only {:} knots".format(max_interior_knots))

        # for some reason it sometimes sticks on a boundary point despite having found an obvious internal minimum
        if self.opt.fun > np.min(self._fev):
            i = np.argmin(self._fev)
            check = check_max_knots(self._sev[i])
            if check < 0:
                if verbose:
                    printw(
                        'WARNING: Autoknotting found {:} (>{:}) knots lowers the reduced chi squared'.format(
                            max_interior_knots - int(check), max_interior_knots
                        )
                    )
            else:
                self.opt.x, self.opt.fun = self._sev[i], self._fev[i]

        interpolate.UnivariateSpline.__init__(self, xv, yv, s=self.opt.x * nx, **kwargs)
        printd("Final number of knots is {:} of maximum {:}".format(len(self.get_knots()) - 2, max_interior_knots))

    def get_reduced_chisqr(self):
        """

        :return: float. Reduced chi squared of the spline.

        """
        res = self.get_residual()
        nfree = len(self.get_coeffs()) + (len(self.get_knots()) - 2)
        nob = self._data[0].shape[0]
        return res / (nob - nfree)

    def get_smoothing_factor(self):
        """

        :return: float. Smoothing factor using in UnivariateSpline.

        """
        return self._data[6] * 1.0

    def get_evolution(self, norm=True):
        """

        :param norm: bool. Normalize s to the UnivariateSpline default npts.

        :return: tuple. sev, fev where sev is a record of all smoothing values tried
            in the optimization and fev is the corresponding reduced chi squared costs.

        """
        s, f = np.array(self._sev), np.array(self._fev)
        if not norm:
            s *= len(self._data[0])
        return s, f


class CLSQUnivariateSpline(interpolate.LSQUnivariateSpline):
    """
    Constrained least square univariate spline. This class sacrifices the generality
    of UnivariateSpline's smoothing but enables the ability to constrain values and/or
    derivatives of the spline.

    The constraints are used in an optimization of the knot locations, not fundamentally
    enforced in the underlying equations. Thus, constraints far from the natural spline
    will cause errors.

    :Examples:

    Using the same data from the LSQUnivariateSpline examples,

    >> x = np.linspace(-2, 2, 50)
    >> nominal_values = np.exp(-x**2)
    >> std_devs = 0.1 * np.ones_like(nominal_values)
    >> y = nominal_values + np.random.normal(loc=0, scale=std_devs)

    If we simply use this to fit a spline it will use AutoUnivariateSpline to optimize the knot
    locations.

    >> spl = CLSQUnivariateSpline(x, y, w=1./std_devs)
    >> xs = np.linspace(-2, 2, 1000)
    >> pyplot.subplots()
    >> pyplot.errorbar(x, y, std_devs, marker='o', ls='')
    >> pyplot.plot(xs, spl(xs), label='unconstrained')

    But the new part of this class is that is enables additional constraints on the spline.
    For example, we can request the spline have zero derivative at the left boundary.

    >> splc = CLSQUnivariateSpline(x, y, w=1/std_devs, min_separation=0.1, xyprime_constraints=[(-2,0)])
    >> pyplot.plot(xs, splc(xs), label='constrained')
    >> pyplot.legend()


    """

    def __init__(
        self,
        x,
        y,
        w=None,
        bbox=(None, None),
        k=3,
        ext=0,
        check_finite=False,
        t=None,
        optimize_knots=True,
        min_separation=0,
        xy_constraints=(),
        xyprime_constraints=(),
        maxiter=100,
        verbose=False,
    ):
        """
        Initialize a instance of a constrained least square univariate spline.

        :param x: (N,) array_like. Input dimension of data points. Must be increasing

        :param y: (N,) array_like. Input dimension of data points

        :param w: (N,) array_like. Weights for spline fitting. Must be positive. Default is equal weighting.

        :param bbox: (2,) array_like. 2-sequence specifying the boundary of the approximation interval.

        :param k: int. Degree of the smoothing spline. Must be 1 <= k <= 5. Default is k=3, a cubic spline.

        :param ext: int or str. Controls the extrapolation mode for elements not in the knot interval. Default 0.
            if ext=0 or 'extrapolate', return the extrapolated value.
            if ext=1 or 'zeros', return 0
            if ext=2 or 'raise', raise a ValueError
            if ext=3 of 'const', return the boundary value.

        :param check_finite: bool. Whether to check that the input arrays contain only finite numbers.

        :param t: (M,) array_like or integer. Interior knots of the spline in ascending order (t in
            LSQUnivariateSplien) or maximum number of interior knots (max_interior_knots in AutoUnivariateSpline).

        :param optimize_knots: bool. Allow optimizer to change knot locations after initial guess from t or AutoUnivariateSpline.

        :param min_separation: float. Minimum separation between knot locations if not explicitely specified by t.

        :param xy_constraints: list of tuples. Spline is constrained to have these values at these locations.

        :param xyprime_constraints: Spline is constrained to have these derivatives as these locations.
            x and y separately, and 'y' to simply use the prescribed knot locations.

        :param maxiter: int. Maximum number of iterations for spline coeff optimization under constraints.

        :param verbose: bool. Print warnings

        """
        from uncertainties import unumpy

        debug = False
        # set defaults
        if w is None:
            if is_uncertain(y):
                w = 1.0 / unumpy.std_devs(y)
            else:
                w = np.ones_like(y)
        y = unumpy.nominal_values(y)
        # Sanitize x, y, e data
        if check_finite:
            valid = np.isfinite(x) * np.isfinite(y) * np.isfinite(w)
            x = x[valid]
            y = y[valid]
            w = w[valid]
            printd(' - removed {:} of {:} values checking finite status'.format(len(valid) - len(x), len(valid)))
            check_finite = False
        # be robust to typical shorthand
        if xy_constraints is None:
            xy_constraints = ()
        if np.shape(xy_constraints) == (2,):
            xy_constraints = (xy_constraints,)
        if xyprime_constraints is None:
            xyprime_constraints = ()
        if np.shape(xyprime_constraints) == (2,):
            xyprime_constraints = (xyprime_constraints,)

        # store unique variables
        self._min_sep = min_separation
        self._xyc = xy_constraints
        self._xyp = xyprime_constraints

        # optimize knot locations on a unit scale
        xnorm = np.ptp(x)
        x0 = x / xnorm
        s0 = max(1e-8, min_separation / xnorm)
        ynorm = np.ptp(y)
        y0 = y / ynorm
        w0 = w * ynorm
        xyc = [(xc / xnorm, yc / ynorm) for xc, yc in xy_constraints]
        xyp = [(xc / xnorm, yc / ynorm) for xc, yc in xyprime_constraints]

        # helpful shorthand
        kwargs = dict(bbox=bbox, k=k, ext=ext, check_finite=check_finite)
        eps = 1e-8  # consistent with default minimize steps

        # initial guess
        if t is None or is_int(t):
            sp0 = AutoUnivariateSpline(x0, y0, w=w0, max_interior_knots=t, verbose=verbose, **kwargs)
            t0 = sp0.get_knots()[1:-1]
            auto_t = True
        else:
            printd(" CLSQUnivariateSpline starting with given knots")
            t0 = t / xnorm
            auto_t = False
            sp0 = interpolate.LSQUnivariateSpline(x0, y0, t0, w=w0, **kwargs)
        args0 = np.hstack((sp0.get_knots()[1:-1], sp0.get_coeffs()))

        # helpful constants
        nx = len(x0)
        nt = len(t0)
        nc = len(sp0.get_coeffs())
        nfree = len(args0[nt * int(optimize_knots) :]) - len(xyc) - len(xyp)
        nu = nx - nfree
        if nu <= 0:
            raise ValueError("Under constrained fit. Reduce number of knots.")
        t_front = [sp0._eval_args[0][0]] * (k + 1)
        t_back = [sp0._eval_args[0][-1]] * (k + 1)
        c_back = np.zeros(k + 1)
        if debug:
            print('eval args = {:}'.format(sp0._eval_args))
            print('guess tc  = {:}'.format(args0))

        def form_tck0(tc_args):
            """Form a full (t,c,k) tuple from only the varying knots and coeffs."""
            t = np.hstack((t_front, tc_args[:nt], t_back))
            c = np.hstack((tc_args[nt:], c_back))
            return (t, c, k)

        def tc_cost(tc_args):
            """
            Reduced chi squared given interior knots and all coeffs,
            and assuming w = 1/std_devs.
            """
            try:
                yf = interpolate.splev(x0, form_tck0(tc_args))
                reduced_chisqr = np.sum((w0 * (y0 - yf)) ** 2) / nu
                c = np.abs(reduced_chisqr - 1)
            except ValueError as error:  # protect against "Interior knots t must satisfy Schoenberg-Whitney conditions"
                c = np.sum((y0 * w0) ** 2)
            return c

        def c_cost(c_args):
            """Reduced chi squared if only changing the coeffs."""
            return tc_cost(np.hstack((t0, c_args)))

        if (auto_t or not optimize_knots) and (len(xy_constraints) + len(xyprime_constraints) == 0):
            # just a normal scipy coefficient optimization with the given or automatic knots
            printd(" CLSQUnivariateSpline defaulting to plain LSQUnivariateSpline")
            printd(" with knots at {}".format(t0 * xnorm))
            interpolate.LSQUnivariateSpline.__init__(self, x, y, t0 * xnorm, w=w, **kwargs)
        else:
            if optimize_knots:
                printd('CLSQUnivariateSpline optimizing knot locations')
                # global bounds
                bounds = [(min(x0) + max(eps, s0), max(x0) - max(eps, s0))] * nt
                bounds += [(None, None)] * nc
                # relational constraints
                cons = []
                if s0 > 0:
                    eps = 1e-3 * s0
                for xc, yc in xyc:
                    cons.append({'type': 'eq', 'fun': lambda args, xc=xc, yc=yc: interpolate.splev(xc, form_tck0(args)) - yc})
                for xp, yp in xyp:
                    cons.append({'type': 'eq', 'fun': lambda args, xp=xp, yp=yp: interpolate.splev(xp, form_tck0(args), der=1) - yp})
                # additional constraints for knot separation
                for i in range(1, nt):
                    cons.append({'type': 'ineq', 'fun': lambda t, i=i: (t[i] - t[i - 1]) - s0})
                # optimize the knot locations under given constraints
                self.opt = optimize.minimize(
                    tc_cost, args0, bounds=bounds, constraints=cons, options={"eps": eps, "maxiter": maxiter, "ftol": 1e-3}
                )
                if not self.opt['success']:
                    printe("WARNING: Optimizer failed due to\n{:}".format(self.opt['message']))
                tck = form_tck0(self.opt.x)
                # initialize self with all the data (unconstrained coeffs)
                interpolate.LSQUnivariateSpline.__init__(self, x, y, self.opt.x[:nt] * xnorm, w=w, **kwargs)

            else:
                printd('CLSQUnivariateSpline not optimizing knot locations')
                # relational constraints
                cons = []
                for xc, yc in xyc:
                    cons.append(
                        {'type': 'eq', 'fun': lambda args, xc=xc, yc=yc: interpolate.splev(xc, form_tck0(np.hstack((t0, args)))) - yc}
                    )
                for xp, yp in xyp:
                    cons.append(
                        {
                            'type': 'eq',
                            'fun': lambda args, xp=xp, yp=yp: interpolate.splev(xp, form_tck0(np.hstack((t0, args))), der=1) - yp,
                        }
                    )
                # optimize the coefficients to satisfy the constraints
                self.opt = optimize.minimize(c_cost, args0[nt:], constraints=cons, options={"eps": eps, "maxiter": maxiter, "ftol": 1e-3})
                if not self.opt['success']:
                    printe("WARNING: Optimizer failed due to\n{:}".format(self.opt['message']))
                tck = form_tck0(np.hstack((t0, self.opt.x)))
                # initialize self with all the data (unconstrained coeffs)
                interpolate.LSQUnivariateSpline.__init__(self, x, y, t, w=w, **kwargs)

            if debug:
                pyplot.subplots()
                errorbar(x0, y0, 1 / w)
                scatter(x0, interpolate.splev(x0, tck))
            # renormalize the optimal knots and coeffs
            tck = (tck[0] * xnorm, tck[1] * ynorm, tck[2])
            # set private t, c to the optimized t & c
            tmp = list(self._data)
            tmp[8:10] = tck[0:2]
            # reset the residual for the changed t & c
            tmp[10] = np.sum((w * (y - interpolate.splev(x, tck))) ** 2)
            self._data = tuple(tmp)
            # make sure they take effect for callable methods
            self._reset_class()

    def get_reduced_chisqr(self):
        """

        :return: float. Reduced chi squared of the spline.

        """
        res = self.get_residual()
        nfree = len(self.get_coeffs()) + len(self.get_knots()) - 2
        nob = self._data[0].shape[0]
        return res / (nob - nfree)


@_available_to_user_math
class MonteCarloSpline(CLSQUnivariateSpline):
    """
    Monte Carlo Uncertainty propagation through python spline fits.

    The concept follows https://gist.github.com/thriveth/4680e3d3cd2cfe561a57 by Th/oger Rivera-Thorsen (thriveth),
    and essentially forms n_trials unique spline instances with randomly perturbed data assuming w=1/std_devs
    of gaussian noise.

    Note, calling instances of this class returns unumpy.uarrays of Variable objects using the uncertainties package.

    :Examples:

    Using the same data from the LSQUnivariateSpline examples,

    >> x = np.linspace(-2, 2, 50)
    >> nominal_values = np.exp(-x**2)
    >> std_devs = 0.1 * np.ones_like(y)
    >> y = nominal_values + np.random.normal(loc=0, scale=std_devs)

    We can fit a monte carlo spline to get an errorbar on the interpolation.

    >> spl = MonteCarloSpline(x, y, w=1/std_devs)
    >> xs = np.linspace(-2, 2, 1000)
    >> fig, ax = pyplot.subplots()
    >> eb = ax.errorbar(x, y, std_devs, marker='o', ls='')
    >> ub = uband(xs, spl(xs), label='unconstrained')

    The individual Monte Carlo splines are CLSQUnivariateSpline instances, so we can
    set hard constraints as well.

    >> splc = MonteCarloSpline(x, y, w=1/std_devs, min_separation=0.1, xyprime_constraints=[(-2,0)])
    >> ub = uband(xs, splc(xs), label='constrained')
    >> ax.legend()

    Note, this class is a child of the scipy.interpolate.LSQUnivariateSpline class, and
    has all of the standard spline class methods. Where appropriate, these methods dig
    into the montecarlo trials to return uncertainties. For example,

    >> print('knots are fixed at {}'.format(splc.get_knots()))
    >> print('coeffs vary around {}'.format(splc.get_coeffs()))


    """

    def __init__(
        self,
        x,
        y,
        w=None,
        bbox=(None, None),
        k=3,
        ext=0,
        check_finite=False,
        t=None,
        optimize_knots=True,
        min_separation=0,
        xy_constraints=(),
        xyprime_constraints=(),
        maxiter=200,
        n_trials=100,
    ):
        """
        Initialize a instance of a MonteCarlo constrained least square univariate spline.

        :param x: (N,) array_like. Input dimension of data points. Must be increasing

        :param y: (N,) array_like. Input dimension of data points

        :param w: (N,) array_like. Weights for spline fitting. Must be positive. Default is equal weighting.

        :param bbox: (2,) array_like. 2-sequence specifying the boundary of the approximation interval.

        :param k: int. Degree of the smoothing spline. Must be 1 <= k <= 5. Default is k=3, a cubic spline.

        :param ext: int or str. Controls the extrapolation mode for elements not in the knot interval. Default 0.
            if ext=0 or 'extrapolate', return the extrapolated value.
            if ext=1 or 'zeros', return 0
            if ext=2 or 'raise', raise a ValueError
            if ext=3 of 'const', return the boundary value.

        :param check_finite: bool. Whether to check that the input arrays contain only finite numbers.

        :param t: (M,) array_like or integer. Interior knots of the spline in ascending order or maximum number
                   of interior knots.

        :param optimize_knots: bool. Allow optimizer to change knot locations after initial guess from t or AutoUnivariateSpline.

        :param min_separation: float. Minimum separation between knot locations if not explicitely specified by t.

        :param xy_constraints: list of tuples. Spline is constrained to have these values at these locations.

        :param xyprime_constraints: Spline is constrained to have these derivatives as these locations.
            x and y separately, and 'y' to simply use the prescribed knot locations.

        :param maxiter: int. Maximum number of iterations for spline coeff optimization under constraints.

        :param n_trials: int. Number of Monte Carlo spline iterations used to form errorbars.

        """
        from uncertainties import unumpy

        printd('MonteCarloSpline')
        t_0 = time.time()

        # initial spline sets the base attributes, methods, etc.
        printd(' - Initializing first CLSQUnivariateSpline')
        kwargs = dict(
            w=w,
            bbox=bbox,
            k=k,
            ext=ext,
            check_finite=check_finite,
            t=t,
            optimize_knots=optimize_knots,
            min_separation=min_separation,
            xy_constraints=xy_constraints,
            xyprime_constraints=xyprime_constraints,
            maxiter=maxiter,
        )
        CLSQUnivariateSpline.__init__(self, x, y, verbose=True, **kwargs)
        printd('  > Initialization first CLSQUnivariateSpline took {:.3e} seconds', (time.time() - t_0))

        # repeat n times for statistics
        printd('  - Initialization of all MC splines')
        printd('   > Initializing with knots = {:}'.format(t))
        self.montecarlo = [CLSQUnivariateSpline(x, y, **kwargs)]
        kwargs['optimize_knots'] = False
        kwargs['t'] = self.get_knots()[1:-1]  # fix the knots for speed & consistency
        printd('   > Fixing knots = {:}'.format(kwargs['t']))
        w = self._data[2]  # changed if check_finite removed nans
        kwargs['w'] = self._data[2]  # keep weighting by error?
        # kwargs['w'] = np.ones_like(self._data[2]) * np.mean(self._data[2])  # Monte Carlo determines UQ (don't double count!)
        kwargs['check_finite'] = False  # data already cleaned by first call
        for i in range(max(n_trials, 0)):
            xi = self._data[0]  # _data == x,y,w,xb,xe,k,s,n,t,c,fp,fpint,nrdata,ier
            yi = self._data[1] + np.random.normal(loc=0, scale=1 / w)
            spli = CLSQUnivariateSpline(xi, yi, **kwargs)
            self.montecarlo.append(spli)
        printd('  > Initialization of all MC splines took {:.3e} seconds', (time.time() - t_0))

        # reset some data that relies on (patched) methods
        tmp = list(self._data)
        tmp[10] = np.sum((tmp[2] * (tmp[1] - unumpy.nominal_values(self(tmp[0])))) ** 2, axis=0)
        self._data = tuple(tmp)
        # make sure they take effect for callable methods
        self._reset_class()
        # at this point the parent class get_knots and get_residual methods are valid

    def __call__(self, x, nu=0, ext=None):
        """
        Evaluate spline (or its nu-th derivative) at positions x.

        :param x: array_like. A 1-D array of points at which to return the value of the smoothed
            spline or its derivatives. Note: x can be unordered but the
            evaluation is more efficient if x is (partially) ordered.
        :param nu  : int. The order of derivative of the spline to compute.
        :param ext: int. Controls the value returned for elements of ``x`` not in the
            interval defined by the knot sequence.
            * if ext=0 or 'extrapolate', return the extrapolated value.
            * if ext=1 or 'zeros', return 0
            * if ext=2 or 'raise', raise a ValueError
            * if ext=3 or 'const', return the boundary value.
            The default value is 0, passed from the initialization of the class instance.

        """
        from uncertainties import unumpy

        t_0 = time.time()
        printd('Evaluating MonteCarloSpline fit results')
        ss = np.vstack([spl(x, nu=nu, ext=ext) for spl in self.montecarlo])
        result = unumpy.uarray(np.mean(ss, axis=0), np.std(ss, axis=0))
        printd('  - Evaluation of Monte Carlo splines took {:.3e} seconds'.format(time.time() - t_0))

        return result

    def antiderivative(self, n=1):
        """
        Construct a new spline representing the antiderivative of this spline.

        :param n: int. Order of antiderivative to evaluate.

        """
        base = CLSQUnivariateSpline.antiderivative(self, n=n)
        result = copy.deepcopy(self)
        for i, spl in enumerate(self.montecarlo):
            result.montecarlo[i] = spl.antiderivative(n=n)
        result._data = base._data

        return result

    def derivative(self, n=1):
        """
        Construct a new spline representing the derivative of this spline.

        :param n: int. Order of antiderivative to evaluate.

        """
        base = CLSQUnivariateSpline.antiderivative(self, n=n)
        result = copy.deepcopy(self)
        for i, spl in enumerate(self.montecarlo):
            result.montecarlo[i] = spl.derivative(n=n)
        result._data = base._data

        return result

    def derivatives(self, x):
        """Return all derivatives of the spline at the point x."""
        from uncertainties import unumpy

        ss = np.vstack([spl.derivatives(x) for spl in self.montecarlo])
        result = unumpy.uarray(np.mean(ss, axis=0), np.std(ss, axis=0))
        return result

    def get_coeffs(self):
        """Return spline coefficients."""
        from uncertainties import unumpy

        ss = np.vstack([spl.get_coeffs() for spl in self.montecarlo])
        result = unumpy.uarray(np.mean(ss, axis=0), np.std(ss, axis=0))
        return result

    def integral(self, a, b):
        """Return definite integral of the spline between two given points."""
        from uncertainties import unumpy

        ss = np.vstack([spl.integral(a, b) for spl in self.montecarlo])
        result = unumpy.uarray(np.mean(ss, axis=0), np.std(ss, axis=0))
        return result

    def roots(self):
        """Return the zeros of the spline."""
        # todo: make this robust to some instances having a different number of roots
        from uncertainties import unumpy

        ss = np.vstack([spl.roots() for spl in self.montecarlo])
        result = unumpy.uarray(np.mean(ss, axis=0), np.std(ss, axis=0))
        return result

    def set_smoothing_factor(self, s):
        """Continue spline computation with the given smoothing factor s and with the knots found at the last call."""
        self.set_smoothing_factor(s)
        for spl in self.montecarlo:
            spl.set_smoothing_factor(s)


# -----------
# paths
# -----------
@_available_to_user_math
def contourPaths(x, y, Z, levels, remove_boundary_points=False, smooth_factor=1):
    """
    :param x: 1D x coordinate

    :param y: 1D y coordinate

    :param Z: 2D data

    :param levels: levels to trace

    :param remove_boundary_points: remove traces at the boundary

    :param smooth_factor: smooth contours by cranking up grid resolution

    :return: list of segments
    """
    import matplotlib
    import matplotlib._contour as _contour

    sf = int(round(smooth_factor))
    if sf > 1:
        x = scipy.ndimage.zoom(x, sf)
        y = scipy.ndimage.zoom(y, sf)
        Z = scipy.ndimage.zoom(Z, sf)

    [X, Y] = np.meshgrid(x, y)
    contour_generator = _contour.QuadContourGenerator(X, Y, Z, None, True, 0)

    mx = min(x)
    Mx = max(x)
    my = min(y)
    My = max(y)

    allsegs = []
    for level in levels:
        segs = contour_generator.create_contour(level)
        if not remove_boundary_points:
            segs_ = segs
        else:
            segs_ = []
            for segarray in segs:
                x_ = segarray[:, 0]
                y_ = segarray[:, 1]
                valid = []
                for i in range(len(x_) - 1):
                    if np.isclose(x_[i], x_[i + 1]) and (np.isclose(x_[i], Mx) or np.isclose(x_[i], mx)):
                        continue
                    if np.isclose(y_[i], y_[i + 1]) and (np.isclose(y_[i], My) or np.isclose(y_[i], my)):
                        continue
                    valid.append((x_[i], y_[i]))
                    if i == len(x_):
                        valid.append(x_[i + 1], y_[i + 1])
                if len(valid):
                    segs_.append(np.array(valid))

        segs = list(map(matplotlib.path.Path, segs_))
        allsegs.append(segs)
    return allsegs


@_available_to_user_math
def streamPaths(xm, ym, u, v, start_points, minlength=0, maxlength=1e10, bounds_error=True):
    """
    Integrate vector field and returns stream line

    :params xm: uniformly spaced x grid

    :params xm: uniformly spaced y grid

    :params u: vector field in the x direction

    :params v: vector field in the y direction

    :params start_points: 2D array of seed x,y coordinate points used to start integration

    :params minlength: reject trajectories shorter than this length

    :params maxlength: stop tracing trajectory when this length is reached

    :param bounds_error: raise error if trajectory starts outside of bounds
    """
    import matplotlib

    def _get_integrator(u, v, dmap, minlength, maxlength):
        # rescale velocity onto grid-coordinates for integrations.
        u, v = dmap.data2grid(u, v)

        # speed (path length) will be in axes-coordinates
        u_ax = u / dmap.grid.nx
        v_ax = v / dmap.grid.ny
        speed = np.ma.sqrt(u_ax ** 2 + v_ax ** 2)

        def forward_time(xi, yi):
            ds_dt = matplotlib.streamplot.interpgrid(speed, xi, yi)
            if ds_dt == 0:
                raise TerminateTrajectory()
            dt_ds = 1.0 / ds_dt
            ui = matplotlib.streamplot.interpgrid(u, xi, yi)
            vi = matplotlib.streamplot.interpgrid(v, xi, yi)
            return ui * dt_ds, vi * dt_ds

        def backward_time(xi, yi):
            dxi, dyi = forward_time(xi, yi)
            return -dxi, -dyi

        def integrate(x0, y0):
            """Return x, y grid-coordinates of trajectory based on starting point.
            Integrate both forward and backward in time from starting point in
            grid coordinates.
            Integration is terminated when a trajectory reaches a domain boundary
            or when it crosses into an already occupied cell in the StreamMask. The
            resulting trajectory is None if it is shorter than `minlength`.
            """

            try:
                dmap.start_trajectory(x0, y0)
            except Exception:
                return None
            sf, xf_traj, yf_traj = matplotlib.streamplot._integrate_rk12(x0, y0, dmap, forward_time, maxlength)
            dmap.reset_start_point(x0, y0)
            sb, xb_traj, yb_traj = matplotlib.streamplot._integrate_rk12(x0, y0, dmap, backward_time, maxlength)
            # combine forward and backward trajectories
            stotal = sf + sb
            x_traj = xb_traj[::-1] + xf_traj[1:]
            y_traj = yb_traj[::-1] + yf_traj[1:]

            if stotal > minlength:
                return x_traj, y_traj
            else:  # reject short trajectories
                dmap.undo_trajectory()
                return None

        return integrate

    x = np.linspace(-1, 1, len(xm))
    y = np.linspace(-1, 1, len(ym))

    grid = matplotlib.streamplot.Grid(x, y)
    mask = matplotlib.streamplot.StreamMask(1)
    dmap = matplotlib.streamplot.DomainMap(grid, mask)

    start_points = copy.deepcopy(np.atleast_2d(start_points)).T
    start_points[:, 0] = ((start_points[:, 0] - min(xm)) / (max(xm) - min(xm)) - 0.5) * 2
    start_points[:, 1] = ((start_points[:, 1] - min(ym)) / (max(ym) - min(ym)) - 0.5) * 2

    ## Sanity checks.
    if (u.shape != grid.shape) or (v.shape != grid.shape):
        msg = "'u' and 'v' must be of shape 'Grid(x,y)'"
        raise ValueError(msg)

    u = np.ma.masked_invalid(u)
    v = np.ma.masked_invalid(v)

    integrate = _get_integrator(u, v, dmap, minlength, maxlength)

    sp2 = np.asanyarray(start_points, dtype=np.float64).copy()

    if not bounds_error:
        index = (
            (sp2[:, 0] < grid.x_origin)
            + (sp2[:, 0] > grid.x_origin + grid.width)
            + (sp2[:, 1] < grid.y_origin)
            + (sp2[:, 1] > grid.y_origin + grid.height)
        )
        sp2[index, :] = np.nan

    # Check if start_points are outside the data boundaries
    for xs, ys in sp2:
        if xs < grid.x_origin or xs > grid.x_origin + grid.width or ys < grid.y_origin or ys > grid.y_origin + grid.height:
            raise ValueError("Starting point ({}, {}) outside of" " data boundaries".format(xs, ys))

    sp2[:, 0] -= grid.x_origin
    sp2[:, 1] -= grid.y_origin

    allsegs = []
    for xs, ys in sp2:
        dmap.mask._mask *= 0
        xg, yg = dmap.data2grid(xs, ys)
        t = integrate(xg, yg)
        if t is not None:
            X = (((np.array(t[0]) / (len(xm) + 0) - 0.5) * 2) / 2.0 + 0.5) * (max(xm) - min(xm)) + min(xm)
            Y = (((np.array(t[1]) / (len(ym) + 0) - 0.5) * 2) / 2.0 + 0.5) * (max(ym) - min(ym)) + min(ym)
            allsegs.append(np.array([X, Y]))

    return allsegs


def _ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) >= (B[1] - A[1]) * (C[0] - A[0])


def _intersect(A, B, C, D):
    return _ccw(A, C, D) != _ccw(B, C, D) and _ccw(A, B, C) != _ccw(A, B, D)


def _perp(a):
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b


def _seg_intersect(a1, a2, b1, b2):
    if not _intersect(a1, a2, b1, b2):
        return None
    da = a2 - a1
    db = b2 - b1
    dp = a1 - b1
    dap = _perp(da)
    denom = np.dot(dap, db)
    num = np.dot(dap, dp)
    return (num / denom) * db + b1


@_available_to_user_math
def line_intersect(path1, path2, return_indices=False):
    """
    intersection of two 2D paths

    :param path1: array of (x,y) coordinates defining the first path

    :param path2: array of (x,y) coordinates defining the second path

    :param return_indices: return indices of segments where intersection occurred

    :return: array of intersection points (x,y)
    """

    warnings.filterwarnings('ignore', category=RuntimeWarning, message='invalid value.*')

    ret = []
    index = []

    path1 = np.array(path1).astype(float)
    path2 = np.array(path2).astype(float)

    switch = False
    if len(path1[:, 0]) > len(path2[:, 0]):
        path1, path2 = path2, path1
        switch = True

    m1 = (path1[:-1, :] + path1[1:, :]) / 2.0
    m2 = (path2[:-1, :] + path2[1:, :]) / 2.0
    l1 = np.sqrt(np.diff(path1[:, 0]) ** 2 + np.diff(path1[:, 1]) ** 2)
    l2 = np.sqrt(np.diff(path2[:, 0]) ** 2 + np.diff(path2[:, 1]) ** 2)

    for k1 in range(len(path1) - 1):
        d = np.sqrt((m2[:, 0] - m1[k1, 0]) ** 2 + (m2[:, 1] - m1[k1, 1]) ** 2)
        for k2 in np.where(d <= (l2 + l1[k1]) / 2.0)[0]:
            tmp = _seg_intersect(path1[k1], path1[k1 + 1], path2[k2], path2[k2 + 1])
            if tmp is not None:
                index.append([k1, k2])
                ret.append(tmp)

    ret = np.array(ret)

    if not len(ret):
        return []

    if switch:
        index = np.array(index)
        i = np.argsort(index[:, 1])
        index = [index[i, 1], index[i, 0]]
        index = np.array(index).T.astype(int).tolist()
        ret = ret[i]

    if return_indices:
        return ret, index

    return ret


@_available_to_user_math
def intersect3d_path_surface(path, surface):
    """
    3D intersections of a path and a surface (list of triangles)

    :param path: list of points in 3D [[X0,Y0,Z0],[X1,Y1,X1],...,[Xn,Yn,Xn]]

    :param surface: list of three points in 3D [[[X00,Y0,Z0],[X01,Y01,X01],[X02,Y02,X02]],...,[[Xn0,Yn0,Zn0],[Xn1,Yn1,Xn1],[Xn2,Yn2,Xn2]]]

    :return: list of intersections
    """
    intersections = []
    for triangle in surface:
        hit = intersect3d_path_triangle(path, triangle)
        intersections.extend(hit)
    return intersections


@_available_to_user_math
def intersect3d_path_triangle(path, triangle):
    """
    3D intersections of a path and a triangle

    :param path: list of points in 3D [[X0,Y0,Z0],[X1,Y1,X1],...,[Xn,Yn,Xn]]

    :param triangle: three points in 3D [[X0,Y0,Z0],[X1,Y1,X1],[X2,Y2,X2]]

    :return: list of intersections
    """
    intersections = []
    for k in range(len(path) - 1):
        line = path[k : k + 2]
        hit = intersect3d_line_triangle(line, triangle)
        if hit is not None:
            intersections.append(hit)
    return intersections


@_available_to_user_math
def intersect3d_line_triangle(line, triangle):
    """
    3D intersection of a line and a triangle
    https://stackoverflow.com/questions/42740765/intersection-between-line-and-triangle-in-3d

    :param line: two points in 3D [[X0,Y0,Z0],[X1,Y1,X1]]

    :param triangle: three points in 3D [[X0,Y0,Z0],[X1,Y1,X1],[X2,Y2,X2]]

    :return: None if no intersection is found, or 3D point of intersection
    """
    q1, q2 = line
    p1, p2, p3 = triangle

    def signed_tetra_volume(a, b, c, d):
        return np.sign(np.dot(np.cross(b - a, c - a), d - a) / 6.0)

    s1 = signed_tetra_volume(q1, p1, p2, p3)
    s2 = signed_tetra_volume(q2, p1, p2, p3)

    if s1 != s2:
        s3 = signed_tetra_volume(q1, q2, p1, p2)
        s4 = signed_tetra_volume(q1, q2, p2, p3)
        s5 = signed_tetra_volume(q1, q2, p3, p1)
        if s3 == s4 and s4 == s5:
            n = np.cross(p2 - p1, p3 - p1)
            t = np.dot(p1 - q1, n) / np.dot(q2 - q1, n)
            return np.array(q1 + t * (q2 - q1))

    return None


@_available_to_user_math
def get_s_on_wall(rp, zp, rlim, zlim, slim):
    """
    Given R,Z of a point p and curve lim and parameter slim counting distance along the curve, find s at point p.

    Primarily intended for mapping back from R,Z to s. Simple interpolation doesn't work because the rlim, zlim arrays
    do not monotonically increase.

    If the point is not on the curve, return s coordinate at point closest to (rp, zp).

    Units are quoted in meters, but it should work if all the units are changed consistently.

    :param rp: float or 1D float array
        R coordinate(s) of point(s) of interest in meters

    :param zp: float or 1D float array

    :param rlim: 1D float array
        R values of points along the wall in meters

    :param zlim: 1D float array
        Z values corresponding to rlim

    :param slim: 1D float array
        s values corresponding to rlim

    :return: float or 1D float array
        s at the point(s) on the wall closest to (rp, zp)
    """

    rp1 = np.atleast_1d(rp)
    zp1 = np.atleast_1d(zp)
    rp1nn = copy.copy(rp1)
    rp1nn[np.isnan(rp1)] = 0
    zp1nn = copy.copy(zp1)
    zp1nn[np.isnan(zp1)] = 0

    # Detect bad inputs
    tolerance = 5e-2  # Maybe (rp, zp) is just rounded so it's slightly outside of rlim, zlim; calculate anyway
    rbounds = [np.min(rlim) - tolerance, np.max(rlim) + tolerance]
    zbounds = [np.min(zlim) - tolerance, np.max(zlim) + tolerance]
    out_of_bounds = (
        (rp1nn > rbounds[1]) | (rp1nn < rbounds[0]) | (zp1nn > zbounds[1]) | (zp1nn < zbounds[0]) | np.isnan(rp1) | np.isnan(zp1)
    )
    if np.all(out_of_bounds):
        printe('All points are outside of the rectangle bounding rlim, zlim. Nothing to do here.')
        return np.array([np.NaN] * len(rp1))

    dr = np.diff(rlim)
    dz = np.diff(zlim)
    len2 = dr * dr + dz * dz
    len2[len2 < 1e-6] = 1e-6  # Set minimum len2 to avoid division by small numbers & really large a, which isn't useful

    rp_ = rp1[:, np.newaxis] + 0 * dr[np.newaxis, :]
    zp_ = zp1[:, np.newaxis] + 0 * dz[np.newaxis, :]
    drr = rp_ - rlim[np.newaxis, :-1]  # rp - r1
    dzz = zp_ - zlim[np.newaxis, :-1]  # zp - z1

    a = (drr * dr + dzz * dz) / len2
    projected_rp = rlim[np.newaxis, :-1] + a * dr[np.newaxis, :]
    projected_zp = zlim[np.newaxis, :-1] + a * dz[np.newaxis, :]
    dist2 = (projected_rp - rp_) ** 2 + (projected_zp - zp_) ** 2
    iclose = dist2.argmin(axis=1)
    rpclose = projected_rp[np.arange(len(iclose)), iclose]
    zpclose = projected_zp[np.arange(len(iclose)), iclose]
    selector = np.vstack((iclose, iclose + 1))

    rlimr = rlim[selector]
    zlimr = zlim[selector]
    slimr = slim[selector]

    sp = np.empty(len(rp1))
    sp[:] = np.NaN

    for i in range(len(sp)):
        if ~out_of_bounds[i]:
            if np.diff(rlimr[:, i]) < np.diff(zlimr[:, i]):
                sp[i] = interp1d(zlimr[:, i], slimr[:, i], bounds_error=False)(zpclose[i])
            else:
                sp[i] = interp1d(rlimr[:, i], slimr[:, i], bounds_error=False)(rpclose[i])

    if np.isscalar(rp) and len(sp) == 1:
        sp = sp[0]

    dist2 = (rp - rpclose) ** 2 + (zp - zpclose) ** 2
    dist2[out_of_bounds] = np.NaN
    k = ~np.isnan(sp)
    assert np.nanmedian(dist2) < 1e6, (
        f'Median distance between input strike point and project is too large.\n'
        f'Strike point: ({rp[k]}, {zp[k]}) m\n'
        f'Projection coefficient: {a[iclose[k]]} (index {iclose[k]})\n'
        f'strike point projected to wall: ({rpclose[k]}, {zpclose[k]})\n'
        f'Distance between strike point and projection: {np.sqrt(dist2[k])}\n'
        f's at projected point: {sp[k]} m'
    )

    return sp


@_available_to_user_math
def point_to_line(px, py, x1, y1, x2, y2, return_closest_point=False):
    """
    Calculate minimum distance from a set of points to a set of line segments.

    The segments might be defined by consecutive vertices in a polyline.
    The closest point is closest to the SEGMENT, not the line extended to infinity.

    The inputs can be arrays or scalars (that get forced into 1 element arrays).
    All arrays longer than 1 must have matching length.
    If (px, py) and (x1, x2, y1, y2) have the same length, the comparison is done for
    (px[0], py[0]) vs (x1[0], y1[0], x2[0], y2[0]). That is, line 0 (x1[0], ...) is only
    compared to point 0.

    All inputs should have matching units.

    :param px: 1D float array-like
        X coordinates of test points

    :param py: 1D float array-like
        Y coordinates of test points

    :param x1: 1D float array-like
        X-coordinates of the first endpoint of each line segment.

    :param x2: 1D float array-like
        X-coordinates of the second endpoint of each line segment.

    :param y1: 1D float array-like
        Y-coordinates of the first endpoint of each line segment.

    :param y2: 1D float array-like
        Y-coordinates of the second endpoint of each line segment.

    :param return_closest_point: bool
        Return the coordinates of the closest points instead of the distances.

    :return: array or tuple of arrays
        if return_closest_point = True:
            tuple of two 1D float arrays with the X and Y coordinates of the closest
            point on each line segment to each point.
        if return_closest_point = False:
            1D float array giving the shortest distances between the points and the line segments.
    """
    x1 = np.atleast_1d(x1)
    x2 = np.atleast_1d(x2)
    y1 = np.atleast_1d(y1)
    y2 = np.atleast_1d(y2)

    LineMag = np.hypot(x2 - x1, y2 - y1)

    u1 = ((px - x1) * (x2 - x1)) + ((py - y1) * (y2 - y1))
    u = u1 / (LineMag * LineMag)

    e1 = np.hypot(x1 - px, y1 - py)
    e2 = np.hypot(x2 - px, y2 - py)

    # Find closest point and distance
    ix = x1 + u * (x2 - x1)
    iy = y1 + u * (y2 - y1)
    d = np.hypot(ix - px, iy - py)

    # Handle cases where the closest point on the line is not on the line segment.
    i = np.where(((u < 0.00001) | (u > 1)))[0]
    d[i] = e1[i]
    ix[i] = (x1 + 0 * px)[i]
    iy[i] = (y1 + 0 * py)[i]
    ii = np.where(e1[i] > e2[i])[0]
    d[i[ii]] = e2[i[ii]]
    ix[i[ii]] = (x2 + 0 * px)[i[ii]]
    iy[i[ii]] = (y2 + 0 * py)[i[ii]]

    if return_closest_point:
        return ix, iy
    else:
        return d


@_available_to_user_math
def point_in_poly(x, y, poly):
    """
    Determine if a point is inside a given polygon or not.
    Polygon is a list of (x,y) pairs. This function returns True or False.
    The algorithm is called the "Ray Casting Method".
    Source: http://geospatialpython.com/2011/01/point-in-polygon.html , retrieved 20160105 18:39
    :param x, y: floats
        Coordinates of the point to test
    :param poly: List of (x,y) pairs defining a polygon.
    :return: bool
        Flag indicating whether or not the point is within the polygon.

    To test:
        polygon = [(0,10),(10,10),(10,0),(0,0)]
        point_x = 5
        point_y = 5
        inside = point_in_poly(point_x, point_y, polygon)
        print(inside)
    """
    n = len(poly)
    inside_ = False

    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside_ = not inside_
        p1x, p1y = p2x, p2y

    return inside_


@_available_to_user_math
def centroid(x, y):
    """
    Calculate centroid of polygon

    :param x: x coordinates of the polygon

    :param y: y coordinates of the polygon

    :return: tuple with x and y coordinates of centroid
    """
    x = np.array(x)
    y = np.array(y)
    dy = np.diff(y)
    dx = np.diff(x)
    x0 = (x[1:] + x[:-1]) * 0.5
    y0 = (y[1:] + y[:-1]) * 0.5
    A = np.sum(dy * x0)
    x_c = -np.sum(dx * y0 * x0) / A
    y_c = np.sum(dy * x0 * y0) / A
    return x_c, y_c


# -----------
# patch np
# -----------
if compare_version(np.__version__, '1.11') < 0:

    def gradient(f, *varargs, **kwargs):
        r"""
        Return the gradient of an N-dimensional array.

        The gradient is computed using second order accurate central differences
        in the interior and either first differences or second order accurate
        one-sides (forward or backwards) differences at the boundaries. The
        returned gradient hence has the same shape as the input array.

        Parameters
        ----------
        f : array_like
            An N-dimensional array containing samples of a scalar function.
        varargs : scalar or list of scalar, optional
            N scalars specifying the sample distances for each dimension,
            i.e. `dx`, `dy`, `dz`, ... Default distance: 1.
            single scalar specifies sample distance for all dimensions.
            if `axis` is given, the number of varargs must equal the number of axes.
        edge_order : {1, 2}, optional
            Gradient is calculated using N\ :sup:`th` order accurate differences
            at the boundaries. Default: 1.

            .. versionadded:: 1.9.1

        axis : None or int or tuple of ints, optional
            Gradient is calculated only along the given axis or axes
            The default (axis = None) is to calculate the gradient for all the axes of the input array.
            axis may be negative, in which case it counts from the last to the first axis.

            .. versionadded:: 1.11.0

        Returns
        -------
        gradient : list of np.ndarray
            Each element of `list` has the same shape as `f` giving the derivative
            of `f` with respect to each dimension.

        Examples
        --------

        >> x = np.array([1, 2, 4, 7, 11, 16], dtype=np.float64)
        >> np.gradient(x)
        np.array([ 1. ,  1.5,  2.5,  3.5,  4.5,  5. ])
        >> np.gradient(x, 2)
        np.array([ 0.5 ,  0.75,  1.25,  1.75,  2.25,  2.5 ])

        For two dimensional arrays, the return will be two arrays ordered by
        axis. In this example the first array stands for the gradient in
        rows and the second one in columns direction:

        >> np.gradient(np.array([[1, 2, 6], [3, 4, 5]], dtype=np.float64))
        [np.array([[ 2.,  2., -1.],
                [ 2.,  2., -1.]]), np.array([[ 1. ,  2.5,  4. ],
                [ 1. ,  1. ,  1. ]])]

        >> x = np.array([0, 1, 2, 3, 4])
        >> dx = np.gradient(x)
        >> y = x**2
        >> np.gradient(y, dx, edge_order=2)
        np.array([-0.,  2.,  4.,  6.,  8.])

        The axis keyword can be used to specify a subset of axes of which the gradient is calculated
        >> np.gradient(np.array([[1, 2, 6], [3, 4, 5]], dtype=np.float64), axis=0)
        np.array([[ 2.,  2., -1.],
               [ 2.,  2., -1.]])
        """
        f = np.asanyarray(f)
        N = len(f.shape)  # number of dimensions

        axes = kwargs.pop('axis', None)
        if axes is None:
            axes = tuple(range(N))
        # check axes to have correct type and no duplicate entries
        if isinstance(axes, int):
            axes = (axes,)
        if not isinstance(axes, tuple):
            raise TypeError("A tuple of integers or a single integer is required")

        # normalize axis values:
        axes = tuple(x + N if x < 0 else x for x in axes)
        if max(axes) >= N or min(axes) < 0:
            raise ValueError("'axis' entry is out of bounds")

        if len(set(axes)) != len(axes):
            raise ValueError("duplicate value in 'axis'")

        n = len(varargs)
        if n == 0:
            dx = [1.0] * N
        elif n == 1:
            dx = [varargs[0]] * N
        elif n == len(axes):
            dx = list(varargs)
        else:
            raise SyntaxError("invalid number of arguments")

        edge_order = kwargs.pop('edge_order', 1)
        if kwargs:
            raise TypeError('"{}" are not valid keyword arguments.'.format('", "'.join(list(kwargs.keys()))))
        if edge_order > 2:
            raise ValueError("'edge_order' greater than 2 not supported")

        # use central differences on interior and one-sided differences on the
        # endpoints. This preserves second order-accuracy over the full domain.

        outvals = []

        # create slice objects --- initially all are [:, :, ..., :]
        slice1 = [slice(None)] * N
        slice2 = [slice(None)] * N
        slice3 = [slice(None)] * N
        slice4 = [slice(None)] * N

        otype = f.dtype.char
        if otype not in ['f', 'd', 'F', 'D', 'm', 'M']:
            otype = 'd'

        # Difference of datetime64 elements results in timedelta64
        if otype == 'M':
            # Need to use the full dtype name because it contains unit information
            otype = f.dtype.name.replace('datetime', 'timedelta')
        elif otype == 'm':
            # Needs to keep the specific units, can't be a general unit
            otype = f.dtype

        # Convert datetime64 data into ints. Make dummy variable `y`
        # that is a view of ints if the data is datetime64, otherwise
        # just set y equal to the array `f`.
        if f.dtype.char in ["M", "m"]:
            y = f.view('int64')
        else:
            y = f

        for i, axis in enumerate(axes):

            if y.shape[axis] < 2:
                raise ValueError("Shape of array too small to calculate a numerical gradient, " "at least two elements are required.")

            # Numerical differentiation: 1st order edges, 2nd order interior
            if y.shape[axis] == 2 or edge_order == 1:
                # Use first order differences for time data
                out = np.empty_like(y, dtype=otype)

                slice1[axis] = slice(1, -1)
                slice2[axis] = slice(2, None)
                slice3[axis] = slice(None, -2)
                # 1D equivalent -- out[1:-1] = (y[2:] - y[:-2])/2.0
                out[slice1] = (y[slice2] - y[slice3]) / 2.0

                slice1[axis] = 0
                slice2[axis] = 1
                slice3[axis] = 0
                # 1D equivalent -- out[0] = (y[1] - y[0])
                out[slice1] = y[slice2] - y[slice3]

                slice1[axis] = -1
                slice2[axis] = -1
                slice3[axis] = -2
                # 1D equivalent -- out[-1] = (y[-1] - y[-2])
                out[slice1] = y[slice2] - y[slice3]

            # Numerical differentiation: 2st order edges, 2nd order interior
            else:
                # Use second order differences where possible
                out = np.empty_like(y, dtype=otype)

                slice1[axis] = slice(1, -1)
                slice2[axis] = slice(2, None)
                slice3[axis] = slice(None, -2)
                # 1D equivalent -- out[1:-1] = (y[2:] - y[:-2])/2.0
                out[slice1] = (y[slice2] - y[slice3]) / 2.0

                slice1[axis] = 0
                slice2[axis] = 0
                slice3[axis] = 1
                slice4[axis] = 2
                # 1D equivalent -- out[0] = -(3*y[0] - 4*y[1] + y[2]) / 2.0
                out[slice1] = -(3.0 * y[slice2] - 4.0 * y[slice3] + y[slice4]) / 2.0

                slice1[axis] = -1
                slice2[axis] = -1
                slice3[axis] = -2
                slice4[axis] = -3
                # 1D equivalent -- out[-1] = (3*y[-1] - 4*y[-2] + y[-3])
                out[slice1] = (3.0 * y[slice2] - 4.0 * y[slice3] + y[slice4]) / 2.0

            # divide by step size
            out /= dx[i]
            outvals.append(out)

            # reset the slice object in this dimension to ":"
            slice1[axis] = slice(None)
            slice2[axis] = slice(None)
            slice3[axis] = slice(None)
            slice4[axis] = slice(None)

        if len(axes) == 1:
            return outvals[0]
        else:
            return outvals

    np.gradient = gradient

# helpful generalization to handle uncertainties or not
def usqrt(y):
    """Handle uncertainties if needed"""
    from uncertainties import unumpy

    if is_uncertain(y):
        result = unumpy.sqrt(y)
    else:
        result = np.sqrt(unumpy.nominal_values(y))
    return result


# helpful generalization to handle uncertainties or not
def ulog(y):
    """Handle uncertainties if needed"""
    from uncertainties import unumpy

    if is_uncertain(y):
        result = unumpy.log(y)
    else:
        result = np.log(unumpy.nominal_values(y))
    return result


# copy scipy.ndimage filters (v1.1.0) and add causal key word argument
def _gaussian_kernel1d(sigma, order, radius, causal=False):
    """
    Computes a 1D Gaussian convolution kernel.
    """
    if order < 0:
        raise ValueError('order must be non-negative')
    p = np.polynomial.Polynomial([0, 0, -0.5 / (sigma * sigma)])
    x = np.arange(-radius, radius + 1)
    phi_x = np.exp(p(x), dtype=np.double)
    if causal:
        phi_x[radius + 1 :] = 0.0
        if order > 0:
            raise AssertionError('Cannot calculate causal gaussian kernel for order > 0')
    phi_x /= phi_x.sum()
    if order > 0:
        q = np.polynomial.Polynomial([1])
        p_deriv = p.deriv()
        for _ in range(order):
            # f(x) = q(x) * phi(x) = q(x) * exp(p(x))
            # f'(x) = (q'(x) + q(x) * p'(x)) * phi(x)
            q = q.deriv() + q * p_deriv
        phi_x *= q(x)
    return phi_x


@_available_to_user_math
def gaussian_filter1d(input, sigma, axis=-1, order=0, output=None, mode="reflect", cval=0.0, truncate=4.0, causal=False):
    """One-dimensional Gaussian filter.
    Parameters
    ----------
    %(input)s
    sigma : scalar
        standard deviation for Gaussian kernel
    %(axis)s
    order : int, optional
        An order of 0 corresponds to convolution with a Gaussian
        kernel. A positive order corresponds to convolution with
        that derivative of a Gaussian.
    %(output)s
    %(mode)s
    %(cval)s
    truncate : float, optional
        Truncate the filter at this many standard deviations.
        Default is 4.0.
    causal : bool or sequence of bools
        Remove all forward weightings.
    Returns
    -------
    gaussian_filter1d : np.ndarray
    Examples
    --------
    >> from scipy.ndimage import gaussian_filter1d
    >> gaussian_filter1d([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    np.array([ 1.42704095,  2.06782203,  3.        ,  3.93217797,  4.57295905])
    >> gaussian_filter1d([1.0, 2.0, 3.0, 4.0, 5.0], 4)
    np.array([ 2.91948343,  2.95023502,  3.        ,  3.04976498,  3.08051657])
    >> from matplotlib import pyplot
    >> np.random.seed(280490)
    >> x = np.random.randn(101).cumsum()
    >> y3 = gaussian_filter1d(x, 3)
    >> y6 = gaussian_filter1d(x, 6)
    >> pyplot.plot(x, 'k', label='original data')
    >> pyplot.plot(y3, '--', label='filtered, sigma=3')
    >> pyplot.plot(y6, ':', label='filtered, sigma=6')
    >> pyplot.legend()
    >> pyplot.grid()
    >> pyplot.show()

    Causality example,
    >> x = np.arange(0,100)
    >> y = 1.* (x > 40) * (x < 60)
    >> fig, ax = pyplot.subplots()
    >> ax.plot(x, y, 'x-')
    >> ax.plot(x, gaussian_filter1d(y,3.))
    >> ax.plot(x, gaussian_filter1d(y,3., causal=True))
    >> ax.set_ylim(0,1.5)

    """
    sd = float(sigma)
    # make the radius of the filter equal to truncate standard deviations
    lw = int(truncate * sd + 0.5)
    if order == 0:
        # symmetric, use forward order for consistency with causal kernel
        weights = _gaussian_kernel1d(sigma, order, lw, causal)
    else:
        # Since we are calling correlate, not convolve, revert the kernel
        weights = _gaussian_kernel1d(sigma, order, lw, causal)[::-1]

    return ndimage.correlate1d(input, weights, axis, output, mode, cval, 0)


@_available_to_user_math
def gaussian_filter(input, sigma, order=0, output=None, mode="reflect", cval=0.0, truncate=4.0, causal=False):
    """Multidimensional Gaussian filter.
    Parameters
    ----------
    %(input)s
    sigma : scalar or sequence of scalars
        Standard deviation for Gaussian kernel. The standard
        deviations of the Gaussian filter are given for each axis as a
        sequence, or as a single number, in which case it is equal for
        all axes.
    order : int or sequence of ints, optional
        The order of the filter along each axis is given as a sequence
        of integers, or as a single number.  An order of 0 corresponds
        to convolution with a Gaussian kernel. A positive order
        corresponds to convolution with that derivative of a Gaussian.
    %(output)s
    %(mode_multiple)s
    %(cval)s
    truncate : float
        Truncate the filter at this many standard deviations.
        Default is 4.0.
    causal : bool or sequence of bools
        Remove all forward weightings.
    Returns
    -------
    gaussian_filter : np.ndarray
        Returned array of same shape as `input`.
    Notes
    -----
    The multidimensional filter is implemented as a sequence of
    one-dimensional convolution filters. The intermediate arrays are
    stored in the same data type as the output. Therefore, for output
    types with a limited precision, the results may be imprecise
    because intermediate results may be stored with insufficient
    precision.
    Examples
    --------
    >> from scipy.ndimage import gaussian_filter
    >> a = np.arange(50, step=2).reshape((5,5))
    >> a
    np.array([[ 0,  2,  4,  6,  8],
           [10, 12, 14, 16, 18],
           [20, 22, 24, 26, 28],
           [30, 32, 34, 36, 38],
           [40, 42, 44, 46, 48]])
    >> gaussian_filter(a, sigma=1)
    np.array([[ 4,  6,  8,  9, 11],
           [10, 12, 14, 15, 17],
           [20, 22, 24, 25, 27],
           [29, 31, 33, 34, 36],
           [35, 37, 39, 40, 42]])
    >> from scipy import misc
    >> from matplotlib import pyplot
    >> fig = pyplot.figure()
    >> pyplot.gray()  # show the filtered result in grayscale
    >> ax1 = fig.add_subplot(121)  # left side
    >> ax2 = fig.add_subplot(122)  # right side
    >> ascent = misc.ascent()
    >> result = gaussian_filter(ascent, sigma=5)
    >> ax1.imshow(ascent)
    >> ax2.imshow(result)
    >> pyplot.show()

    Here is a nice little demo of the added OMFIT causal feature,

    >> nn = 24
    >> a = np.zeros((nn, nn))
    >> a[int(nn//2),int(nn//2)] = 1
    >> fig, axs = pyplot.subplots(2, 2)
    >> ax = axs[0, 0]
    >> ax.imshow(scipy.ndimage.gaussian_filter(a, 3, mode='nearest'), origin='lower')
    >> ax.set_title('scipy version')
    >> ax = axs[0, 1]
    >> ax.imshow(gaussian_filter(a, 3, mode='nearest'), origin='lower')
    >> ax.set_title('OMFIT version')
    >> ax = axs[1, 0]
    >> ax.imshow(gaussian_filter(a, 3, causal=True, mode='nearest'), origin='lower')
    >> ax.set_title('causal True')
    >> ax = axs[1, 1]
    >> ax.imshow(gaussian_filter(a,3, causal=(True, False), mode='nearest'), origin='lower')
    >> ax.set_title('causal True, False')

    """
    input = np.asarray(input)
    # output = _ni_support._get_output(output, input)  # this function's behavior is different for earlier scipys,
    # just hardcore v1.1.0 _get_output below
    shape = input.shape
    if output is None:
        output = np.zeros(shape, dtype=input.dtype.name)
    elif type(output) in [type(type), type(np.zeros((4,)).dtype)]:
        output = np.zeros(shape, dtype=output)
    elif isinstance(output, str):
        output = np.typeDict[output]
        output = np.zeros(shape, dtype=output)
    elif output.shape != shape:
        raise RuntimeError("output shape not correct")

    orders = _ni_support._normalize_sequence(order, input.ndim)
    sigmas = _ni_support._normalize_sequence(sigma, input.ndim)
    modes = _ni_support._normalize_sequence(mode, input.ndim)
    causals = _ni_support._normalize_sequence(causal, input.ndim)
    axes = list(range(input.ndim))
    axes = [(axes[ii], sigmas[ii], orders[ii], modes[ii], causals[ii]) for ii in range(len(axes)) if sigmas[ii] > 1e-15]
    if len(axes) > 0:
        for axis, sigma, order, mode, causal in axes:
            gaussian_filter1d(input, sigma, axis, order, output, mode, cval, truncate, causal)
            input = output
    else:
        output[...] = input[...]
    return output


@_available_to_user_math
def bicoherence(s1, s2=None, fs=1.0, nperseg=None, noverlap=None, **kwargs):
    """
    Compute the bicoherence between two signals of the same lengths s1 and s2
    using the function scipy.signal.spectrogram.

    Sourced from https://stackoverflow.com/questions/4194554/function-for-computing-bicoherence

    :param s1: ndarray. Time series of measurement values

    :param s2: ndarray. Time series of measurement values (default of None uses s1)

    :param fs: Sampling frequency of the x time series. Defaults to 1.0.

    :param nperseg: int. Length of each segment. Defaults to None, but if window is str or tuple, is set to 256, and if window is array_like, is set to the length of the window.

    :param noverlap: int. Number of points to overlap between segments. If None, noverlap = nperseg // 8. Defaults to None.

    :param kwargs: All additional key word arguments are passed to signal.spectrogram

    :return f, bicoherence: array of frequencies and matrix of bicoherence at those frequencies

    """
    # set defaults
    if s2 is None:
        s2 = s1

    # compute the stft
    f1, t1, spec_s1 = scipy.signal.spectrogram(s1, fs=fs, nperseg=nperseg, noverlap=noverlap, mode='complex')
    f2, t2, spec_s2 = scipy.signal.spectrogram(s2, fs=fs, nperseg=nperseg, noverlap=noverlap, mode='complex')

    # transpose (f, t) -> (t, f)
    spec_s1 = np.transpose(spec_s1, [1, 0])
    spec_s2 = np.transpose(spec_s2, [1, 0])

    # compute the bicoherence
    arg = np.arange(f1.size / 2).astype(int)
    sumarg = (arg[:, None] + arg[None, :]).astype(int)
    num = np.abs(np.mean(spec_s1[:, arg, None] * spec_s1[:, None, arg] * np.conjugate(spec_s2[:, sumarg]), axis=0)) ** 2
    denum = np.mean(np.abs(spec_s1[:, arg, None] * spec_s1[:, None, arg]) ** 2, axis=0) * np.mean(
        np.abs(np.conjugate(spec_s2[:, sumarg])) ** 2, axis=0
    )
    bicoh = num / denum

    return f1[arg], bicoh

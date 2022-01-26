"""
main entry point for all time-series reducers (given segment, return value)

Notes
-----
if used on a segment-time-series, you must call transform as the output will be a time-series.

if used on a non-segment-time-series, you must call reduce as the output will be a single value.
"""


#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

def sum():
    """result in the sum of all values

    Returns
    -------
    unary-reducer
        a sum unary-reducer, which applied on a time-series or segment will result in the sum of all values
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.sum()


def average():
    """result in the average of all values

    Returns
    -------
    unary-reducer
        an average unary-reducer, which applied on a time-series or segment will result in the average of all values
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.average()


def correlation():
    """result in the correlation value between both time-series/segments

    Returns
    -------
    binary-reducer
        a correlation binary-reducer, which applied on two time-series or segments will result in the correlation value
        between both time-series/segments
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.correlation()


def cross_correlation():
    """result in the cross correlation values (array) between both time-series/segments

    Returns
    -------
    binary-reducer
        a cross-correlation binary-reducer, which applied on two time-series or segments will result in the cross
        correlation values (array) between both time-series/segments
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.cross_correlation()


def auto_correlation():
    """result in the auto-correlation at all lags

    Returns
    -------
    unary-reducer
        an auto-correlation unary-reducer, which applied on a time-series or segment will result in the auto-correlation
        at all lags
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.auto_correlation()


def convolve():

    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.convolve()


def fft():
    """result in a vector representing the frequency content from fft

    Returns
    -------
    unary-reducer
        an fft unary-reducer, which applied on a time-series or segment will result in a vector representing the
        frequency content
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.fft()


def standard_deviation():
    """result in the standard-deviation computation

    Returns
    -------
    unary-reducer
        a standard-deviation-reducer, which applied on a time-series or segment will result in the standard-deviation
        computation
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.standard_deviation()


def skewness():
    """result in the skewness (a measure of symmetry)

    Returns
    -------
    unary-reducer
        a skewness reducer, which applied on a time-series or segment will result in the skewness (a measure of
        symmetry)
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.skewness()


def kurtosis():
    """result in the kurtosis (a measure of whether the values in the series are heavy-tailed or light tailed relative
    to normal distribution)

    Returns
    -------
    unary-reducer
        a kurtosis reducer, which applied on a time-series or segment will result in the kurtosis (a measure of
        whether the values in the series are heavy-tailed or light tailed relative to normal distribution)
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.kurtosis()


def min():
    """result in the min of the values

    Returns
    -------
    unary-reducer
        a min reducer, which applied on a time-series or segment will result in the min of the values
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.min()


def max():
    """result in the max of the values

    Returns
    -------
    unary-reducer
        a max reducer, which applied on a time-series or segment will result in the max of the values
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.max()


def percentile(quantile):
    """result in the percentile of the values given a quantile

    Parameters
    ----------
    quantile : double
        the quantile to compute percentile at

    Returns
    -------
    unary-reducer
        a percentile reducer, which applied on a time-series or segment will result in the percentile of the values
        given a quantile
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.percentile(quantile)


def describe():
    """result in the basic components of the time-series (~autoai_ts_libs.deps.tspy.data_structures.Stats.Stats)

    Returns
    -------
    unary-reducer
        a describe reducer, which applied on a time-series will return the basic components of the time-series
        (~autoai_ts_libs.deps.tspy.data_structures.Stats.Stats)
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.describe()


def adf(lag=None, p_value=-3.45):
    """test the null hypothesis that a unit root is present in a time-series sample

    Parameters
    ----------
    lag : int, optional
        the lag (default is floor(cubed_root(size-1)))
    p_value : float, optional
        the adf p-value threshold, generally a p-value of less than 5% means you can reject the null hypothesis (default
        is -3.45)

    Returns
    -------
    unary-reducer
        an augmented-dickey-fuller-test reducer, which applied on a time-series or segment, will test the null
        hypothesis that a unit root is present in a time-series sample
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.stat_reducers.adf(lag, p_value)


def granger(lag):
    """test whether one time-series is useful in forecasting another

    Parameters
    ----------
    lag : int
        lag of the other time-series with respect to the calling time-series

    Returns
    -------
    binary-reducer
        a granger-causality-test reducer, which applied on two time-series or segments, will test whether one
        time-series is useful in forecasting another
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.stat_reducers.granger(lag)


def dl(func=None):
    """perform the dl distance

    Parameters
    ----------
    func : func
        a function which given two values, will return a bool for whether the values match

    Returns
    -------
    binary-reducer
        a demerau-levenstein distance reducer, which applied on two time-series or segments, will perform the dl
        distance
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.distance_reducers.dl(func)

def jaro_winkler():
    """perform the jaro winkler distance

    Returns
    -------
    binary-reducer
        a jaro-winkler distance reducer, which applied on two time-series or segments, will perform the jaro winkler
        distance
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.distance_reducers.jaro_winkler()

def sbd():
    """calculate a distance based on time-series shape

    Returns
    -------
    binary-reducer
        a shape-based distance reducer, which applied on two time-series or segments, will calculate a distance based
        on time-series shape
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.distance_reducers.sbd()


def dtw(func):
    """calculate the dtw distance of two time-series of varying speed

    Parameters
    ----------
    func : func
        a function which given two values, will return a value representing the distance

    Returns
    -------
    binary-reducer
        a dynamic-time-warped distance reducer, which applied on two time-series or segments, will calculate the
        dtw distance of two time-series of varying speed
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.distance_reducers.dtw(func)


def sakoe_chiba_dtw(func, constraint):
    """
    todo
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.distance_reducers.sakoe_chiba_dtw(func, constraint)


def itakura_parralelogram_dtw(func, constraint, center_offset_percentage):
    """
    todo
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.distance_reducers.itakura_parralelogram_dtw(func, constraint, center_offset_percentage)


def manhattan(func):
    """calculate the point-wise manhattan distance

    Parameters
    ----------
    func : func
        a function which given two values, will return a value representing the distance

    Returns
    -------
    binary-reducer
        a simple manhattan distance reducer, which applied on two time-series or segments, will calculate the
        point-wise manhattan distance
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.distance_reducers.manhattan(func)

def entropy():
    """calculate the entropy (average level of uncertainty)

    Returns
    -------
    unary-reducer
        a entropy reducer, which applied on a time-series will return the entropy (average level of uncertainty)
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.entropy()

def distance_variance():
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.distance_variance()

def distance_covariance():
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.distance_covariance()

def distance_correlation():
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.distance_correlation()

def mutual_information():
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.mutual_information()

def histogram(min, max, num_divisions, normalize=False):
    """bucket values based on their place with the given range (min/max)

    Parameters
    ----------
    min : float
        lower bound for buckets
    max : float
        upper bound for buckets
    num_divisions : int
        number of buckets to return
    normalize : bool, optional
        if True, will normalize the bucket values, otherwise bucket values will be counts

    Returns
    -------
    unary-reducer
        a histogram reducer, which applied on a time-series or segment will bucket values based on their place with
        the given range (min/max)
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.histogram(min, max, num_divisions, normalize)

def count_by_value():
    """produce a dict of counts of each unique value in the time-series

    Returns
    -------
    unary-reducer
        a count_by_value reducer, which applied on a time-series or segment will return a dict of counts of each unique
        value in the time-series
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.general_reducers.count_by_value()

def median():
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.median()

def integral():
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.integral()

def cdf(min_value, max_value, num_divisions):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.cdf(min_value, max_value, num_divisions)

def abs_energy():
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.abs_energy()


def abs_sum_of_changes():
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.abs_sum_of_changes()

def c3(lag):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.c3(lag)

def energy_ratio(sum_squares):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.energy_ratio(sum_squares)

def regression(approximate_intercept=True):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_reducers.regression(approximate_intercept)

def has_duplicate(duplicate_value=None):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.general_reducers.has_duplicate(duplicate_value)

def count():
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.general_reducers.count()

"""
main entry point for all transformers (given time-series, return new time-series)
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

def z_score(mean=None, sd=None):
    """map each value to a number of standard deviations above/below the mean

    Parameters
    ----------
    mean : float, optional
        the mean to use when performing z-score (default is mean of input series)
    sd : float, optional
        the standard-deviation when performing z-score (default is sd of input series)
    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a Z-Normalization transform which, when applied on a numeric time-series will map each value to a number of
        standard deviations above/below the mean
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.z_score(mean, sd)

def z_score_with_annotation():
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.z_score_with_annotation()

def difference():
    """take the difference between the current observation value and its previous observation value

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a difference transform which, when applied on a numeric time-series will take the difference between the
        current observation value and its previous observation value
    """

    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.difference()


def detect_anomalies(forecasting_model, confidence, update_model=False, info=False):
    """filter for anomalies within the time-series given a forecasting model and its definition of confidence intervals

    Parameters
    ----------
    forecasting_model : ~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel
        the forecasting model to use
    confidence : float
        a number between 0 and 1 (exclusive) which are used to determine the confidence interval
    update_model : bool, optional
        if True, the model will be trained/updated (default is False)
    info : bool, optional
        if True, will give back the bounds/errors/expected values, otherwise no other information will be provided
        (default is False)

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        an anomaly detection transform which, when applied on a time-series filter for anomalies within the time-series
        given a forecasting model and its definition of confidence intervals
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.detect_anomalies(forecasting_model, confidence, update_model, info)


def awgn(mean=None, sd=None):
    """add noise using the following method https://en.wikipedia.org/wiki/Additive_white_Gaussian_noise

    Parameters
    ----------
    mean : float, optional
        the mean around which to add the noise (default is time-series mean)
    sd : float, optional
        the standard deviation to use (default is time-series standard deviation)

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        an additive-white-gaussian noise transform which, when applied on a time-series will add noise using the
        following method https://en.wikipedia.org/wiki/Additive_white_Gaussian_noise
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.awgn(mean, sd)


def mwgn(sd=None):
    """add noise given a standard-deviation

    Parameters
    ----------
    sd : float, optional
        the standard deviation to use (default is time-series standard deviation)

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        an multiplicative-white-gaussian noise transform which, when applied on a time-series will add noise given a
        standard-deviation
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.mwgn(sd)

def ljung_box(window, step, num_lags, period):
    """test for the absence of serial correlation, up to a specified lag

    Parameters
    ----------
    window : int
        length of window
    step : int
        number of steps
    num_lags : int
        number of lags
    period : int
        number to multiply the lag by when getting windows

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a ljung-box transform, which applied on a time-series will test for the absence of serial correlation,
        up to a specified lag
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.stat_transforms.ljung_box(window, step, num_lags, period)

def remove_consecutive_duplicate_values():
    """trim the time-series by removing consecutive duplicate values

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a remove-consecutive-duplicates transform, which applied on a time-series will trim the time-series by removing
        consecutive duplicate values
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.duplicate_transforms.remove_consecutive_duplicate_values()

def combine_duplicate_time_ticks(combine_strategy):
    """combine the observations which have the same time-tick

    Parameters
    ----------
    combine_strategy : func
        a function or lamdba that receives one argument representing the collection of values of the same timestamp and
        returns a single value

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a combine-duplicate-time-ticks transform, which applied on a time-series will combine the observations which
        have the same time-tick
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.duplicate_transforms.combine_duplicate_time_ticks(combine_strategy)

def paa(m):
    """approximate the time-series in a piecewise fashion. This is used to accelerate similarity measures between two
    time-series

    Parameters
    ----------
    m : int
        num buckets

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a piecewise-aggregate-approximation transform, which applied on a time-series will approximate the time-series
        in a piecewise fashion. This is used to accelerate similarity measures between two time-series
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.paa(m)

def sax(min_value, max_value, num_bins):
    """transform the time-series to a time-series of symbols by discretizing the value. Discretization is performed by
    uniformly dividing the values between min_value and max_value into num_bins bins

    Parameters
    ----------
    min_value : float
        min value
    max_value : float
        max value
    num_bins : int
        number of bins

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a symbolic-aggregate-approximation transform, which applied on a time-series will transform the time-series to
        a time-series of symbols by discretizing the value
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.sax(min_value, max_value, num_bins)

def ema(smoothing_constant):
    """smooth the time-series (x) such that the i^th observation on the transformed time-series
    y(t) = y(t-1) + (x(t) - y(t-1)) * (1 - smoothing_constant)

    Parameters
    ----------
    smoothing_constant : float
        a number between 0 and 1, the closer to 0, the faster the number will converge

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a exponentially-weighted-moving-average transform, which applied on a time-series (x) will smooth the
        time-series such that the i^th observation on the transformed time-series y(t) = y(t-1) + (x(t) - y(t-1)) *
        (1 - smoothing_constant)
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.ema(smoothing_constant)

def decompose(samples_per_season, multiplicative):
    """get the residuals, trend, and seasonal components of a time-series

    Parameters
    ----------
    samples_per_season : int
        number of samples in a season
    multiplicative : bool
        if True, use multiplicative method, otherwise use additive

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a decomposition transform, which applied on a time-series will result in the residuals, trend, and seasonal
        components
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.decompose(samples_per_season, multiplicative)

def discrete_cosine():
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.discrete_cosine()

def fit_regression(periodicity):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.fit_regression(periodicity)

def min_max_scaler(min_value=None, max_value=None):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.min_max_scaler(min_value, max_value)

def min_max_scaler_with_annotation():
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.math_transforms.min_max_scaler_with_annotation()


"""
SDQC checks file
"""
import numpy as np


def missing_values(data):
    """
    Checks for missing values on the data.

    Parameters
    ----------
    data: ndarray
        The data to check.

    Returns
    -------
    pass, outs: bool, list
        pass is True if no missing values have been found and False if
        missing values have been found. outs is a list with the number
        of missing values and the total number of values.

    """
    n_nan = int(np.sum(np.isnan(data)))
    n_values = int(np.prod(data.shape))

    if n_nan == 0:
        return True, [0, n_values]

    return False, [n_nan, n_values]


def missing_values_data(data, series, completeness):
    """
    Checks for missing values on the data giving the series.

    Parameters
    ----------
    data: ndarray
        The data to check.
    series: ndarray (1D)
        The series to check.
    completeness: str (optional)
        If completeness is 'any' (Default) the check will not pass
        is there is any missing value for a given series value. If
        completeness is 'all' the check will not pass all the data
        values are missing for a given series value (column).
        It only has effects when data is a matrix (2 or more dimensions).

    Returns
    -------
    pass, outs: bool, list
        pass is True if no missing values have been found and False if
        missing values have been found. outs is a list with a fisrt list
        of the number of missing values and the total number of values
        checked, and a second list with the series values for which the
        missing values where found. Note that the number of missing
        values and the total values depens on the completeness.

    """
    data_nan = np.isnan(data)
    n_nan = int(np.sum(data_nan))
    n_values = int(np.prod(data_nan.shape))

    if len(data.shape) >= 2:
        if completeness == 'all':
            data_nan = np.all(data_nan, axis=tuple(range(1, data_nan.ndim)))
            n_nan = int(np.sum(data_nan))
            n_values = int(np.prod(data_nan.shape))
        elif completeness == 'any':
            data_nan = np.any(data_nan, axis=tuple(range(1, data_nan.ndim)))
        else:
            raise ValueError("Invalid value for completeness argument.")

    if not any(data_nan):
        return True, [[0, n_values], []]

    missing = list(series[data_nan])
    return False, [[n_nan, n_values], missing]


def series_monotony(series):
    """
    Checks if series is monotonous.

    Parameters
    ----------
    series: ndarray (1D)
        The series to check.

    Returns
    -------
    pass, outs: bool, list
        pass is True if series is monotonous and False if not.
        outs is a list with the series range (minimum and maximum).

    """
    if all(np.diff(series) < 0) or all(np.diff(series) > 0):
        return True, [series[0], series[-1]]

    return False, [np.min(series), np.max(series)]


def series_range(series, srange):
    """
    Checks if series range is inside a given range.

    Parameters
    ----------
    series: ndarray (1D)
        The series to check.

    srange: list (len 2)
        The minimum and maximum value of the series.

    Returns
    -------
    pass, outs: bool, list
        pass is True if series is monotonous and False if not.
        outs is a list with the series range (minimum and maximum)
        and a list with the give srange.

    """
    smin, smax = np.min(series), np.max(series)
    if smin < srange[0] or smax > srange[1]:
        return False, [[smin, smax], srange]

    return True, [[smin, smax], srange]


def series_increment_type(series, type):
    """
    Checks if series range is inside a given range.

    Parameters
    ----------
    series: ndarray (1D)
        The series to check.

    type: str
        The series distribution ('linear')

    Returns
    -------
    pass, outs: bool, list
        pass is True if series is monotonous and False if not.
        outs is a list with the series step or the full series.

    """
    # TODO include more distributions ('exponential', 'logarithmic'...)
    if type == 'linear':
        ds = np.diff(series)
        if np.all(ds == ds[0]):
            # return True with the step
            return True, [ds[0]]
    else:
        raise ValueError(
            f"The argument {type} is not supported by series_increment_type.")

    return False, list(series)


def outlier_values(data, method, **kwargs):
    """
    Checks if there are possible outliers in the data using a
    multiple of the standard deviation.

    Parameters
    ----------
    data: ndarray
        The data to check.

    method: str
         The method to be used. Can be 'std' for standard deviation method
         or 'iqr' for interquartile range method.

    **kwargs: see below

    Keyword Args
    ------------
    nstd: float
        For 'std' method, the number of standard deviations
        to define outliers.

    niqr: float
        For 'iqr' method, the number of interquartile ranges
        to define outliers.

    Returns
    -------
    pass, outs: bool, list
        pass is True if series is monotonous and False if not.
        outs is a list with the number of possible outliers and
        the total number of values.

    """

    n_values = int(np.prod(data.shape))

    if method == 'std':
        # standard deviation method
        nstd = kwargs.get('nstd', 2)
        mean = np.nanmean(data)
        std = np.nanstd(data)
        n_outliers = int(np.sum(np.logical_or(data > mean + nstd*std,
                                              data < mean - nstd*std)))
    elif method == 'iqr':
        # interquartile range method
        niqr = kwargs.get('niqr', 1.5)
        q_low, q_up = np.percentile(data, 25), np.percentile(data, 75)
        iqr = q_up - q_low
        n_outliers = int(np.sum(np.logical_or(data > q_up + niqr*iqr,
                                              data < q_low - niqr*iqr)))
    else:
        raise ValueError(
            f"The method {method} is not supported by outlier_values."
        )

    if n_outliers == 0:
        return True, [0, n_values]

    return False, [n_outliers, n_values]

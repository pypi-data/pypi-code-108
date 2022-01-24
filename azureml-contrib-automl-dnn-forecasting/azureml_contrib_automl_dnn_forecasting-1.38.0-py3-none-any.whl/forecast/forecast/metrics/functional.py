"""Standard M4 metrics on which algorithms can be evaluated."""

from typing import List

import numpy as np


def smape(actual: np.ndarray, pred: np.ndarray) -> float:
    """Computes symmetric mean absolute percentage error (sMAPE).

    This is the absolute error normalized by both the actual and predicted values.

    Note: Sometimes, 100 * sMAPE is reported as sMAPE. This version DOES NOT apply this scaling.

    Parameters:
    -----------
    act: np.ndarray
        The target values
    pred: np.ndarray
        The predicted values

    Returns:
    --------
    float
        The sMAPE of the prediction relative to the target values

    """
    actual = np.reshape(actual, (-1,))
    pred = np.reshape(pred, (-1,))
    return np.mean(2.0 * np.abs(actual - pred) / (np.abs(actual) + np.abs(pred))).item()


def mase(insample: np.ndarray, actual: np.ndarray, pred: np.ndarray, samples_per_period: int) -> float:
    """Computes mean absolute scaled error (MASE).

    This is the absolute error normalized by the naive prediction of a 1-period lookback.

    Parameters:
    -----------
    insample: np.ndarray
        The value of the time-series on which the performance of a naive 1-period lookback will be evaluated.
    actual: np.ndarray
        The target values
    pred: np.ndarray
        The predicted values to evaluate
    samples_per_period: int
        The number of samples in a period(e.g., 12 for monthly)

    Returns:
    --------
    float
        The MASE of the prediction relative to the target values

    """
    masep = np.mean(np.abs(insample[samples_per_period:] - insample[:-samples_per_period]))
    return np.mean(np.abs(actual - pred)) / masep


def msis(insample: np.ndarray, actual: np.ndarray, lb: np.ndarray, ub: np.ndarray,
         samples_per_period: int, sig: float = 0.05) -> float:
    """Computes mean scaled interval score (MSIS).

    This penalizes the size of the confidence interval and any actual value that falls outside the interval.
    The penalty is normalized by the naive prediction of a 1-period lookback.

    Parameters:
    -----------
    insample: np.ndarray
        The value of the time-series on which the performance of a naive 1-period lookback will be evaluated.
    actual: np.ndarray
        The target values
    lb: np.ndarray
        The lower bound of (1-sig) prediction interval
    ub: np.ndarray
        The upper bound of (1-sig) prediction interval
    sig: float
        The 2-sided prediction interval

    Returns:
    --------
    float
        The MSIS of the LB/UB relative to the target values

    """
    masep = np.mean(np.abs(insample[samples_per_period:] - insample[:-samples_per_period]))
    pen = np.mean((ub - lb)
                  + 2 / sig * np.maximum(0, lb - actual)
                  + 2 / sig * np.maximum(0, actual - ub))
    return pen / masep


def owa(insample: List[np.ndarray], actual: List[np.ndarray],
        pred: List[np.ndarray], samples_per_pd: List[int]) -> float:
    """Computes the M4 metric OWA, the average of sMAPE and MASE relative to the performance of their Naive2 algorithm.

    Parameters:
    -----------
    insample: np.ndarray
        The value of the time-series on which the performance of a naive 1-period lookback will be evaluated.
    act: np.ndarray
        The target values
    pred: np.ndarray
        The predicted values to evaluate
    samples_per_pd: int
        The number of samples in a period (e.g., 12 for monthly)

    Returns:
    --------
    float
        The OWA of the prediction relative to the target values

    Notes:
    ------
    The magic normalizing constants of .15201 and 1.685 are the sMAPE and MASE of the M4 Naive 2 algorithm. They offer
    no other significant meaning. The Naive 2 algorithm is reproduced below for posterity from the M4 Competitor's
    Guide (current URL: https://www.m4.unic.ac.cy/wp-content/uploads/2018/03/M4-Competitors-Guide.pdf).

    Naïve 1 Ft+I = Yt i = 1, 2, 3, … , m

    Naïve 2 like Naïve 1 but the data is seasonally adjusted, if needed, by applying classical multiplicative
    decomposition (R stats package). A 90% autocorrelation test is performed, when using the R package, to decide
    whether the data is seasonal.

    """
    return 1/2 * (np.mean([smape(a, p) for a, p in zip(actual, pred)]) / .15201
                  + np.mean([mase(i, a, p, s) for i, a, p, s in zip(insample, actual, pred, samples_per_pd)]) / 1.685)


def normalized_quantile_loss(actual: List[np.ndarray], pred: List[np.ndarray], quantile: float) -> float:
    """Computes the quantile loss normalized by magnitude of the time series.

    Parameters
    ----------
    actual: np.ndarray
        The target values
    pred: np.ndarray
        The predicted values to evaluate
    quantile: float
        The quantile to evaluate (between 0 and 1 exclusive)

    Returns
    -------
    float
        The normalized quantile loss

    """
    tot_l = sum((quantile * np.maximum(0, a - p) + (1 - quantile) * (p - a)).sum() for a, p in zip(actual, pred))
    tot = sum(a.sum() for a in actual)
    return 2 * tot_l / tot

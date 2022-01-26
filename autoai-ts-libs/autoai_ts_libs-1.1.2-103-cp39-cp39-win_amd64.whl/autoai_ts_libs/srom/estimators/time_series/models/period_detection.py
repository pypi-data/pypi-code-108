import pandas as pd
import numpy as np
from scipy import stats
import scipy.signal
import scipy
from scipy.interpolate import LSQUnivariateSpline


def generalized_cross_validation_error(data, period):
    """
    Given a candidate period, we evaluate the fitness of it
    """
    cycles = np.zeros(period)
    sum_y2 = np.zeros(period)
    sum_y = np.zeros(period)
    idx = 0
    for yii in data:
        sum_y[idx] += yii
        sum_y2[idx] += yii * yii
        cycles[idx] += 1
        idx = (idx + 1) % period
    seasons = sum_y / cycles  # period-over-period means
    sse = sum_y2 - sum_y ** 2 / cycles  # period-over-period sse
    cv_mse = ((cycles / (cycles - 1.0)) ** 2 * sse).sum() / len(data)
    cv_mse = 0.0 if np.isclose(cv_mse, 0.0) else cv_mse
    return cv_mse, seasons


def guess_period(data, periodogram_thresh=0.5, max_period=512):
    """
     A utility function to get the period using value axis based check
    """
    adj_max_period = min(len(data) // 3, max_period)
    trend_s = fit_median_trend(data, period=adj_max_period)
    peaks = periodogram_peaks(data - trend_s)
    if peaks is None:
        return 0

    # initial guess based on weighted average period
    periods, scores, _, _ = zip(*peaks)
    period = int(round(np.average(periods, weights=scores)))

    # more adjustment
    window = (int(period * 2) // 2) * 2 - 1
    nsegs = len(data) // (window * 2) + 1
    trend = aglet(spline_filter(data, nsegs), window)

    data = data - trend
    var = data.var()
    if np.isclose(var, 0.0):
        return 0

    peaks = periodogram_peaks(data, thresh=periodogram_thresh)
    if peaks is None:
        return 0

    peaks = sorted(peaks)
    cv_mse, cv_seasons = np.inf, []
    cv_period = 0
    period = 0
    for interval in peaks:
        period = max(period, interval[2])
        while period <= interval[3]:
            _mse, _seasons = generalized_cross_validation_error(data, period)
            if _mse < cv_mse:
                cv_mse, cv_seasons = _mse, _seasons
                cv_period = len(cv_seasons)
            period += 1

    if 0.05 <= 1 - cv_mse / var or np.isclose(cv_mse, 0.0):
        return cv_period
    return 0


def fit_median_trend(data, period):
    """
    genenrate median signal
    """
    window = (int(period * 2) // 2) * 2 - 1
    filtered = aglet(median_filter(data, window), window)
    return filtered


def median_filter(data, window):
    filtered = np.copy(data)
    for i in range(window // 2, len(data) - window // 2):
        filtered[i] = np.median(data[max(0, i - window // 2) : i + window // 2 + 1])
    return filtered


def spline_filter(data, nsegs):
    index = np.arange(len(data))
    nknots = max(2, nsegs + 1)
    knots = np.linspace(index[0], index[-1], nknots + 2)[1:-2]
    return LSQUnivariateSpline(index, data, knots)(index)


def aglet(src, window, dst=None):
    # this function is to update the left and right side of the window
    if dst is None:
        dst = np.array(src)
    half = window // 2
    leftslope = stats.theilslopes(src[:window])[0]
    rightslope = stats.theilslopes(src[-window:])[0]
    dst[0:half] = np.arange(-half, 0) * leftslope + src[half]
    dst[-half:] = np.arange(1, half + 1) * rightslope + src[-half - 1]
    return dst


def periodogram_peaks(data, min_period=4, max_period=None, thresh=0.90):
    periods, power = periodogram(data, min_period, max_period)
    if np.all([np.isclose(x, 0.00) for x in power]):
        return None

    result = []
    keep = np.abs(power).max() * thresh
    while True:
        peak_i = np.abs(power).argmax()
        if np.abs(power[peak_i]) < keep:
            break
        min_period = periods[min(peak_i + 1, len(periods) - 1)]
        max_period = periods[max(peak_i - 1, 0)]
        result.append([periods[peak_i], power[peak_i], min_period, max_period])
        power[peak_i] = 0
    return result if len(result) else None


def periodogram(
    data, min_period=4, max_period=None, max_fft_period=512, min_fft_cycles=3.0
):
    if max_period is None:
        max_period = int(min(len(data) / min_fft_cycles, max_fft_period))
    nperseg = min(max_period * 2, len(data) // 2)
    freqs, power = scipy.signal.welch(data, 1.0, scaling="spectrum", nperseg=nperseg)
    periods = np.array([int(round(1.0 / freq)) for freq in freqs[1:]])
    power = power[1:]
    # take the max among frequencies having the same integer part
    idx = 1
    while idx < len(periods):
        if periods[idx] == periods[idx - 1]:
            power[idx - 1] = (
                power[idx - 1]
                if np.abs(power[idx - 1]) > np.abs(power[idx])
                else power[idx]
            )
            periods, power = np.delete(periods, idx), np.delete(power, idx)
        else:
            idx += 1
    power[periods == nperseg] = 0  # disregard the artifact at nperseg
    min_i = len(periods[periods >= max_period]) - 1
    max_i = len(periods[periods < min_period])
    periods, power = periods[min_i:-max_i], power[min_i:-max_i]
    return periods, power

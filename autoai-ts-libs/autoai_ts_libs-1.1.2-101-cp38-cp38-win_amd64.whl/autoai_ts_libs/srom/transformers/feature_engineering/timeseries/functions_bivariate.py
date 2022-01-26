"""
   :synopsis: Functions for feature extraction.
   Some of functions of this module are taken from following repository and modified as per the requirement.
   https://github.com/blue-yonder/tsfresh/blob/master/tsfresh/feature_extraction/feature_calculators.py
   License Information:
   __author__ = "Maximilian Christ, Blue Yonder GmbH"
   __copyright__ = "Maximilian Christ, Blue Yonder GmbH"
   __license__ = "MIT"
   Some of functions  of this module are taken from following repository and modified as per the requirement.
   https://github.com/isadoranun/FATS/blob/master/FATS/FeatureFunctionLib.py
   License Information:
   __author__ = "Isadora Nun"
   __copyright__ = "Isadora Nun"
   __license__ = "MIT"
"""

import math
import numpy as np
import pandas as pd
import warnings
import itertools
import scipy.stats
import statistics
from scipy.stats import linregress
from statsmodels.tsa import stattools
from scipy.stats import anderson
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from statsmodels.tsa.ar_model import AR
from statsmodels.tsa.stattools import acf, adfuller, pacf
from numpy.linalg import LinAlgError
from numpy import cov, corrcoef
from autoai_ts_libs.srom.transformers.utils.feature_engineering_utils import check_single_dimensional_array,remove_nan_single_dimensional_array,remove_zero_single_dimensional_array
from autoai_ts_libs.utils.messages.messages import Messages


def covariance(x, y):
    """
    Computes covariance.
    Parameters:
        x (numpy array, required): array of numbers.
        y (numpy array, required): array of numbers.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    return cov(x, y)[0, 1]


def correlation(x, y):
    """
    Computes correlation.
    Parameters:
        x (numpy array, required): array of numbers.
        y (numpy array, required): array of numbers.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    return corrcoef(x, y)[0, 1]


def max_slope(x, y):
    """
    Computes max slope of x and y.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.        
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    slope = np.abs(x[1:] - x[:-1]) / (y[1:] - y[:-1])
    np.max(slope)
    return np.max(slope)


def linear_trend(x, y):
    """
    Computes linear trend of x and y.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.        
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    regression_slope = linregress(y, x)[0]
    return regression_slope


def eta_e(x, y):
    """
    Computes eta_e.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.        
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    w = 1.0 / np.power(np.subtract(y[1:], y[:-1]), 2)
    w_mean = np.mean(w)
    n = len(y)
    sigma2 = np.var(x)
    s1 = sum(w * (x[1:] - x[:-1]) ** 2)
    s2 = sum(w)
    eta_e = w_mean * np.power(y[n - 1] - y[0], 2) * s1 / (sigma2 * s2 * n ** 2)
    return eta_e


def period_ls(x, y, ofac=6.0):
    """
    Computes period ls.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
        ofac(float): float. Default 6.0.        
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    fx, fy, nout, jmax, prob = __fasper__(y, x, ofac, 100.0)
    period = fx[jmax]
    t = 1.0 / period
    return t


def period_prob(x, y, ofac=6.0):
    """
    Computes period probablitiy.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
        ofac(float): float. Default 6.0.        
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    fx, fy, nout, jmax, prob = __fasper__(y, x, ofac, 100.0)
    return prob


def psi_cs(x, y, ofac=6.0):
    """
    Computes psi cs.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
        ofac(float): float. Default 6.0.        
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    fx, fy, nout, jmax, prob = __fasper__(y, x, ofac, 100.0)
    period = fx[jmax]
    t = 1.0 / period
    new_time = np.mod(y, 2 * t) / (2 * t)
    folded_data = x[np.argsort(new_time)]
    sigma = np.std(folded_data)
    n = len(folded_data)
    m = np.mean(folded_data)
    s = np.cumsum(folded_data - m) * 1.0 / (n * sigma)
    r = np.max(s) - np.min(s)
    return r


def psi_eta(x, y, ofac=6.0):
    """
    Computes psi eta.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
        ofac(float): float. Default 6.0.        
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    fx, fy, nout, jmax, prob = __fasper__(y, x, ofac, 100.0)
    period = fx[jmax]
    t = 1.0 / period
    new_time = np.mod(y, 2 * t) / (2 * t)
    folded_data = x[np.argsort(new_time)]
    n = len(folded_data)
    sigma2 = np.var(folded_data)
    psi_eta = (
        1.0
        / ((n - 1) * sigma2)
        * np.sum(np.power(folded_data[1:] - folded_data[:-1], 2))
    )
    return psi_eta


def __cal_freq_harmonics_amplitude__(x, y):
    y = y - np.min(y)
    a1 = []
    ph = []
    scaled_ph = []

    def model(x, a, b, c, freq):
        return a * np.sin(2 * np.pi * freq * x) + b * np.cos(2 * np.pi * freq * x) + c

    for i in range(3):
        wk1, wk2, nout, jmax, prob = __fasper__(y, x, 6.0, 100.0)
        fundamental_freq = wk1[jmax]

        def yfunc(freq):
            def func(x, a, b, c):
                return (
                    a * np.sin(2 * np.pi * freq * x)
                    + b * np.cos(2 * np.pi * freq * x)
                    + c
                )

            return func

        a_temp = []
        ph_temp = []
        popts = []

        for j in range(4):
            popt, pcov = curve_fit(yfunc((j + 1) * fundamental_freq), y, x)
            a_temp.append(np.sqrt(popt[0] ** 2 + popt[1] ** 2))
            ph_temp.append(np.arctan(popt[1] / popt[0]))
            popts.append(popt)

        a1.append(a_temp)
        ph.append(ph_temp)

        for j in range(4):
            x = np.array(x) - model(
                y, popts[j][0], popts[j][1], popts[j][2], (j + 1) * fundamental_freq
            )

    for ph in ph:
        scaled_ph.append(np.array(ph) - ph[0])

    return a1, ph, scaled_ph


def freq1_harmonics_amplitude_0(x, y):
    """
    Computes freq1_harmonics_amplitude_0.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return a[0][0]


def freq1_harmonics_amplitude_1(x, y):
    """
    Computes freq1_harmonics_amplitude_1.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return a[0][1]


def freq1_harmonics_amplitude_2(x, y):
    """
    Computes freq1_harmonics_amplitude_2.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return a[0][2]


def freq1_harmonics_amplitude_3(x, y):
    """
    Computes freq1_harmonics_amplitude_3.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return a[0][3]


def freq2_harmonics_amplitude_0(x, y):
    """
    Computes freq2_harmonics_amplitude_0.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return a[1][0]


def freq2_harmonics_amplitude_1(x, y):
    """
    Computes freq2_harmonics_amplitude_1.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return a[1][1]


def freq2_harmonics_amplitude_2(x, y):
    """
    Computes freq2_harmonics_amplitude_2.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return a[1][2]


def freq2_harmonics_amplitude_3(x, y):
    """
    Computes freq2_harmonics_amplitude_3.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return a[1][3]


def freq3_harmonics_amplitude_0(x, y):
    """
    Computes freq3_harmonics_amplitude_0.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return a[2][0]


def freq3_harmonics_amplitude_1(x, y):
    """
    Computes freq3_harmonics_amplitude_1.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return a[2][1]


def freq3_harmonics_amplitude_2(x, y):
    """
    Computes freq3_harmonics_amplitude_2.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return a[2][2]


def freq3_harmonics_amplitude_3(x, y):
    """
    Computes freq3_harmonics_amplitude_3.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return a[2][3]


def freq1_harmonics_rel_phase_0(x, y):
    """
    Computes freq1_harmonics_rel_phase_0.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return scaled_ph[0][0]


def freq1_harmonics_rel_phase_1(x, y):
    """
    Computes freq1_harmonics_rel_phase_1.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return scaled_ph[0][1]


def freq1_harmonics_rel_phase_2(x, y):
    """
    Computes freq1_harmonics_rel_phase_2.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return scaled_ph[0][2]


def freq1_harmonics_rel_phase_3(x, y):
    """
    Computes freq1_harmonics_rel_phase_3.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return scaled_ph[0][3]


def freq2_harmonics_rel_phase_0(x, y):
    """
    Computes freq2_harmonics_rel_phase_0.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return scaled_ph[1][0]


def freq2_harmonics_rel_phase_1(x, y):
    """
    Computes freq2_harmonics_rel_phase_1.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return scaled_ph[1][1]


def freq2_harmonics_rel_phase_2(x, y):
    """
    Computes freq2_harmonics_rel_phase_2.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return scaled_ph[1][2]


def freq2_harmonics_rel_phase_3(x, y):
    """
    Computes freq2_harmonics_rel_phase_3.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return scaled_ph[1][3]


def freq3_harmonics_rel_phase_0(x, y):
    """
    Computes freq3_harmonics_rel_phase_0.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return scaled_ph[2][0]


def freq3_harmonics_rel_phase_1(x, y):
    """
    Computes freq3_harmonics_rel_phase_1.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return scaled_ph[2][1]


def freq3_harmonics_rel_phase_2(x, y):
    """
    Computes freq3_harmonics_rel_phase_2.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return scaled_ph[2][2]


def freq3_harmonics_rel_phase_3(x, y):
    """
    Computes freq3_harmonics_rel_phase_3.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    a, ph, scaled_ph = __cal_freq_harmonics_amplitude__(x, y)
    return scaled_ph[2][3]


def __structure_function__(x, y):
    NSF = 100
    NP = 100
    sf1 = np.zeros(NSF)
    sf2 = np.zeros(NSF)
    sf3 = np.zeros(NSF)
    f = interp1d(y, x)
    time_int = np.linspace(np.min(y), np.max(y), NP)
    mag_int = f(time_int)
    for tau in np.arange(1, NSF):
        sf1[tau - 1] = np.mean(
            np.power(np.abs(mag_int[0 : NP - tau] - mag_int[tau:NP]), 1.0)
        )
        sf2[tau - 1] = np.mean(
            np.abs(np.power(np.abs(mag_int[0 : NP - tau] - mag_int[tau:NP]), 2.0))
        )
        sf3[tau - 1] = np.mean(
            np.abs(np.power(np.abs(mag_int[0 : NP - tau] - mag_int[tau:NP]), 3.0))
        )

    sf1_log = np.log10(np.trim_zeros(sf1))
    sf2_log = np.log10(np.trim_zeros(sf2))
    sf3_log = np.log10(np.trim_zeros(sf3))
    m_21, b_21 = np.polyfit(sf1_log, sf2_log, 1)
    m_31, b_31 = np.polyfit(sf1_log, sf3_log, 1)
    m_32, b_32 = np.polyfit(sf2_log, sf3_log, 1)
    return m_21, m_31, m_32


def structure_function_index_21(x, y):
    """
    Computes structure_function_index_21.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    m_21, m_31, m_32 = __structure_function__(x, y)
    return m_21


def structure_function_index_31(x, y):
    """
    Computes structure_function_index_31.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    m_21, m_31, m_32 = __structure_function__(x, y)
    return m_31


def structure_function_index_32(x, y):
    """
    Computes structure_function_index_32.
    Parameters:
        x (numpy array, required): magnitude array.
        y (numpy array, required): time array.
    Return:
        float.
    """
    x = check_single_dimensional_array(x)
    y = check_single_dimensional_array(y)
    m_21, m_31, m_32 = __structure_function__(x, y)
    return m_32


def __fasper__(x, y, ofac, hifac, macc=4):
    """ 
    """
    # Check dimensions of input arrays
    n = len(x)
    if n != len(y):
        raise ValueError(Messages.get_message(message_id='AUTOAITSLIBS0024E'))
        return

    nout = 0.5 * ofac * hifac * n
    nout = int(nout)
    nfreqt = int(ofac * hifac * n * macc)  # Size the FFT as next power
    nfreq = 64  # of 2 above nfreqt.

    while nfreq < nfreqt:
        nfreq = 2 * nfreq

    ndim = int(2 * nfreq)

    # Compute the mean, variance
    ave = y.mean()
    ##sample variance because the divisor is N-1
    var = ((y - y.mean()) ** 2).sum() / (len(y) - 1)
    # and range of the data.
    xmin = x.min()
    xmax = x.max()
    xdif = xmax - xmin

    # extirpolate the data into the workspaces
    wk1 = np.zeros(ndim, dtype="complex")
    wk2 = np.zeros(ndim, dtype="complex")

    fac = ndim / (xdif * ofac)
    fndim = ndim
    ck = ((x - xmin) * fac) % fndim
    ckk = (2.0 * ck) % fndim

    for j in range(0, n):
        __spread__(y[j] - ave, wk1, ndim, ck[j], macc)
        __spread__(1.0, wk2, ndim, ckk[j], macc)

    # Take the Fast Fourier Transforms
    wk1 = np.fft.ifft(wk1) * len(wk1)
    wk2 = np.fft.ifft(wk2) * len(wk1)

    wk1 = wk1[1 : nout + 1]
    wk2 = wk2[1 : nout + 1]
    rwk1 = wk1.real
    iwk1 = wk1.imag
    rwk2 = wk2.real
    iwk2 = wk2.imag

    df = 1.0 / (xdif * ofac)

    # Compute the Lomb value for each frequency
    hypo2 = 2.0 * abs(wk2)
    hc2wt = rwk2 / hypo2
    hs2wt = iwk2 / hypo2
    cwt = np.sqrt(0.5 + hc2wt)
    swt = np.sign(hs2wt) * (np.sqrt(0.5 - hc2wt))
    den = 0.5 * n + hc2wt * rwk2 + hs2wt * iwk2
    cterm = (cwt * rwk1 + swt * iwk1) ** 2.0 / den
    sterm = (cwt * iwk1 - swt * rwk1) ** 2.0 / (n - den)
    wk1 = df * (np.arange(nout, dtype="float") + 1.0)
    wk2 = (cterm + sterm) / (2.0 * var)
    pmax = wk2.max()
    jmax = wk2.argmax()
    # Estimate significance of largest peak value
    expy = np.exp(-pmax)
    effm = 2.0 * (nout) / ofac
    prob = effm * expy
    if prob > 0.01:
        prob = 1.0 - (1.0 - expy) ** effm

    return wk1, wk2, nout, jmax, prob


def __spread__(y, yy, n, x, m):
    """ 
    """
    nfac = [0, 1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880]
    if m > 10.0:
        raise ValueError(Messages.get_message(message_id='AUTOAITSLIBS0025E'))
        return

    ix = int(x)
    if x == float(ix):
        yy[ix] = yy[ix] + y
    else:
        ilo = int(x - 0.5 * float(m) + 1.0)
        ilo = min(max(ilo, 1), n - m + 1)
        ihi = ilo + m - 1
        nden = nfac[m]
        fac = x - ilo
        for j in range(ilo + 1, ihi + 1):
            fac = fac * (x - j)
        yy[ihi] = yy[ihi] + y * fac / (nden * (x - ihi))
        for j in range(ihi - 1, ilo - 1, -1):
            nden = (nden / (j + 1 - ilo)) * (j - ihi)
            yy[j] = yy[j] + y * fac / (nden * (x - j))

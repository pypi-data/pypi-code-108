"""Automatically calculate cavity parameters with data taken from an oscilloscope."""

import logging as log
from typing import List, Optional, Tuple
from warnings import warn

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from numpy import float64, ndarray
from pandas.core.indexes.numeric import Float64Index
from pandas.core.series import Series
from scipy.optimize import least_squares
from scipy.signal import find_peaks, peak_widths, savgol_filter

from openqlab.io.data_container import DataContainer


#
# Modematching methods
#
def modematching(  # pylint: disable=too-many-branches
    data: Series,
    plot: bool = False,
    U_max: Optional[float] = None,
    offset: Optional[float] = None,
    rel_prominence: float = 0.02,
    without_main_peaks: bool = False,
    ax: matplotlib.axes.Axes = None,
) -> float:
    """Calculate the mode matching.

    It assumes a cavity scan bounded by two peaks of the main mode.
    The method looks for the smaller peaks where the detection threshold
    can be adjusted with :obj:`rel_prominence`.

    Offset
        The default method to find out the offset is by calculating the mean value.
        If you have measured it more precisely, use the parameter :obj:`offset`.

    Improve precision
        To get a better resolution for small peaks there is an option to take data
        with a clipped main mode. Use the parameter :obj:`U_max` to manually set
        the measured maximum value.

    Parameters
    ----------
    data : Series
        Measured data (just one column).
    plot : bool
        Make a plot to see, if the correct peaks where detected.
    U_max : Optional[float]
        U_max is the parameter to set the peak voltage of the cropped main peaks.
        If set, it is assumed that the main peaks are not in the data.
    rel_prominence : float
        rel_prominence is the parameter to adjust the threshold for the detection
        of small peaks.
    without_main_peaks : bool
        Deprecated! Is assumed if U_max is set.
    ax (Axes, optional):
        Provide an Axes for advanced figures.

    Returns
    -------
    float
        Calculated mode matching value.
    """
    if len(data.shape) != 1:
        raise ValueError("The DataFrame should only contain one single column.")
    if without_main_peaks:
        warn(
            "DEPRECATED: This flag is not needed anymore. Just set a value for U_max",
            DeprecationWarning,
        )
    if U_max is not None:
        without_main_peaks = True
    if ax is None:
        _, ax = plt.subplots()

    data = data.dropna()

    # Adjust offset
    if offset is None:
        offset = np.median(data)
    data -= offset

    # Make peaks positive if necessary
    _adjust_peak_sign(data)

    # Find highest value
    # U_max is updated later with the average of the both main peaks
    if U_max is None:
        U_max = np.max(data)
    else:
        U_max = abs(U_max - offset)

    peaks, main_mode = _find_peaks(data, rel_prominence, U_max)

    if not without_main_peaks:
        if len(main_mode) != 2:
            raise ValueError(
                "The main mode must occur exactly two times for the algorithm to work,"
                f" but it found {len(main_mode)} main modes."
            )

    # Sum of all different modes (excluding 2nd main mode)
    if without_main_peaks:
        # This version with U_max makes it possible to manually
        # include a clipped value for the main peak
        U_sum = sum(data.iloc[peaks], U_max)  # pylint: disable=invalid-name
    else:
        U_sum = sum(
            data.iloc[peaks[main_mode[0] + 1 : main_mode[1]]], U_max
        )  # pylint: disable=invalid-name

        # Update U_max with the average of the main peaks
        U_max = float(np.mean(data.iloc[peaks[main_mode]]))

    # Main peak voltage
    log.info(f"U_max: {U_max}")
    log.info(f"U_sum: {U_sum}")

    # Mode matching
    mode_matching = U_max / U_sum

    # Plotting
    if plot:
        if without_main_peaks:
            _main_plot(data, peaks=peaks, ax=ax)
        else:
            _main_plot(data, peaks=peaks, main_peaks=peaks[main_mode], ax=ax)
            index_first, index_last = peaks[main_mode]
            ax.axvline(x=data.index[index_first], color="gray")
            ax.axvline(x=data.index[index_last], color="gray")
            ax.axvspan(data.index[0], data.index[index_first], color="gray", alpha=0.5)
            ax.axvspan(data.index[index_last], data.index[-1], color="gray", alpha=0.5)

    print(f"Mode matching: {round(mode_matching*100, 2)}%")

    return mode_matching


def _main_plot(
    data: Series,
    ax: matplotlib.axes.Axes,
    peaks: Optional[np.ndarray] = None,
    main_peaks: Optional[np.ndarray] = None,
):
    data.plot(ax=ax)
    ax.set_xlim(data.index[0], data.index[-1])
    if peaks is not None:
        data.iloc[peaks].plot(style=".", ax=ax)
    if main_peaks is not None:
        data.iloc[main_peaks].plot(style="o", ax=ax)


def _find_peaks(
    data: Series, rel_prominence: float, max_value: Optional[float] = None
) -> Tuple[np.ndarray, np.ndarray]:
    if max_value is None:
        max_value = np.max(data)

    # Find peaks
    peaks, peak_dict = find_peaks(data, prominence=max_value * rel_prominence)
    # Find occurences of the main mode.
    main_mode = np.where(peak_dict["prominences"] >= np.max(data) * 0.9)[0]

    return peaks, main_mode


#
# Finesse methods
#
def finesse(
    data: Series, plot: bool = False, ax: matplotlib.axes.Axes = None
) -> List[float]:
    """Finesse calculation using a cavity scan.

    Parameters
    ----------
    data : Series
        data is the amplitude column with two main modes.
    plot : bool
        plot is giving out a plot to make shure the algorithm has found the correct points.
    ax (Axes, optional):
        Provide an Axes for advanced figures.

    Returns
    -------
    list(float)
        Calculated finesse for both peaks.
    """
    if len(data.shape) != 1:
        raise ValueError("The DataFrame should only contain one single column.")
    if ax is None:
        _, ax = plt.subplots()
    data = data.dropna()
    _adjust_peak_sign(data)

    peaks, main_mode = _find_peaks(data, 0.9)
    result = _calculate_finesse(data, peaks, main_mode, ax, plot)
    print(
        f"Finesse first peak: {round(result[0], 2)}, second peak: {round(result[1], 2)}"
    )
    return result


def _calculate_finesse(
    data: Series,
    peaks: np.ndarray,
    main_mode: np.ndarray,
    ax: matplotlib.axes.Axes,
    plot: bool = False,
) -> List[float]:
    peak_data = peak_widths(data, peaks)
    peak_fwhm = peak_data[0]
    peaks_left = peak_data[2]
    peaks_right = peak_data[3]
    main_width = peak_fwhm[main_mode]
    fsr = peaks[main_mode[1]] - peaks[main_mode[0]]

    if plot:
        _main_plot(data, main_peaks=peaks[main_mode], ax=ax)
        for x in np.concatenate([peaks_left[main_mode], peaks_right[main_mode]]):
            ax.axvline(x=data.index[int(x)], ls=":", color="green")

    return [fsr / main_width[0], fsr / main_width[1]]


def _adjust_peak_sign(data: Series) -> None:
    minimum = np.min(data)
    maximum = np.max(data)

    if abs(minimum) > abs(maximum):
        data *= -1


#
# Linewidth methods
#
def linewidth(
    err: Series,
    aux: Series,
    mod_freq: float,
    plot: bool = False,
    fwhm_guess: float = 1e6,
) -> float64:
    # _adjust_peak_sign(err)
    _adjust_peak_sign(aux)

    data = DataContainer(aux)
    data.columns = ["Airy"]
    data["Error"] = err

    def plotting():
        plot_frequency = time * df / 1e6 - center
        plot_frequency_window = time_window * df / 1e6 - center
        # center_idx = (np.abs(plot_frequency_window)).argmin()
        # dataframe = np.abs(
        #     np.abs(plot_frequency_window - 4 * fwhm).argmin() - center_idx
        # )

        plt.figure()
        plt.plot(
            plot_frequency, data["Error_filtered"], marker="x", label="Error function"
        )
        plt.plot(plot_frequency, data["Error_gradient"], ls="-", label="Gradient")
        plt.plot(
            zc * df / 1e6 - center,
            data["Error_filtered"].loc[zc],
            ls="",
            marker="o",
            label="zero crossings",
        )
        plt.title(f"Error signal, df/dt = {df:.2f}")
        plt.legend()

        plt.figure()  # pylint: disable=unused-variable
        plt.plot(
            plot_frequency_window, data_offset, linestyle=" ", marker=".", label="data"
        )
        plt.plot(plot_frequency_window, fit, label="fit")

        plt.title(fr"Cavity, $\gamma$ = {fwhm:.2f} MHz")
        plt.legend()
        plt.xlabel("Frequency, MHz")
        plt.ylabel("Normalized cavity peak")

    time = data.index
    ### Set offset of the error function to zero
    data["Error_offset"] = data["Error"] - _fit_line(data["Error"])
    data["Error_filtered"] = savgol_filter(
        data["Error_offset"], 11, 3
    )  # get the filtered error function
    data["Error_gradient"] = savgol_filter(
        data["Error_offset"], 11, 8, 1, 1
    )  # get the filtered error function
    zero_crossings = np.where(np.diff(np.sign(data["Error_filtered"])))[
        0
    ]  # find all zero crossings in the data
    gradient_zeros = np.abs(
        data["Error_gradient"].iloc[zero_crossings]
    )  # find the gradient at zero crossings
    zc = gradient_zeros.nlargest(3).index  # select indicies for largest 3 values

    ### Find the time difference between the zero-crossing points as average of left and right
    time_difference = (np.abs(zc[1] - zc[0]) + (np.abs(zc[2] - zc[0]))) / 2.0

    ### Using the modulation frequency find a map from time to frequency
    df = mod_freq / time_difference

    ### Find the peaks in frequency
    peaklabel = data["Airy"].nlargest(1).index.tolist()[0]
    peak_freq = peaklabel * df
    peakind = time.get_loc(peaklabel)

    ### Fit the lorentzian
    (*_, fwhm0) = _fit_lorentzian(
        data["Airy"], time, df, peak_freq, fwhm_guess
    )  # Get preliminary fit
    ind = (
        2 * data.size * fwhm0 * 10 ** 6 / ((time[-1] - time[0]) * df)
    )  # get index window of 2 fwhm
    time_window = time[
        peakind - ind.astype(int) : peakind + ind.astype(int)
    ]  # select a window
    data_offset, fit, center, fwhm = _fit_lorentzian(
        data["Airy"].iloc[peakind - ind.astype(int) : peakind + ind.astype(int)],
        time_window,
        df,
        peak_freq,
        fwhm_guess,
    )

    if plot:
        plotting()

    return fwhm * 1e6


def _line(x: Float64Index, p: ndarray) -> Float64Index:
    """Fit the line in the error signal to find zero."""
    return x + p[0]


def _resid_line(p: ndarray, y: Series, x: Float64Index) -> Series:
    return y - _line(x, p)


def _fit_line(data: Series) -> Float64Index:
    p = [0]

    # optimization #
    pbest = least_squares(_resid_line, p, args=(data, data.index))
    best_parameters = pbest.x
    fit = _line(data.index, best_parameters)
    return fit


def _lorentzian(x: ndarray, p: ndarray) -> ndarray:
    """Define the lorentzian fit."""
    numerator = p[1] ** 2
    denominator = (x - p[0]) ** 2 + p[1] ** 2
    return p[2] * (numerator / denominator) - p[3]


def _residuals(p: ndarray, y: ndarray, x: ndarray) -> ndarray:
    return y - _lorentzian(x, p)


def _fit_lorentzian(
    data: Series,
    time_array: Float64Index,
    df: float64,
    peak: float64,
    fwhm_guess: float,
) -> Tuple[ndarray, ndarray, float64, float64]:
    data = np.array(data)
    freq = np.array(time_array) * df

    # pre set the offset
    offset = np.median(data)
    data_offset = data  # - offset

    p = [peak, fwhm_guess, 1, offset]  # initial guess

    # optimization #
    pbest = least_squares(_residuals, p, args=(data, freq))
    best_parameters = pbest.x
    fwhm = 2 * abs(best_parameters[1] / 1e6)
    center = best_parameters[0] / 1e6
    # print(f'Full width: {fwhm:.2f} MHz')  # print the HWHM

    # fit to data #
    fit = _lorentzian(freq, best_parameters)
    return data_offset, fit, center, fwhm

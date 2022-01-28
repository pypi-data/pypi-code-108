#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021, INRIA
#
# This file is part of Openwind.
#
# Openwind is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Openwind is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openwind.  If not, see <https://www.gnu.org/licenses/>.
#
# For more informations about authors, see the CONTRIBUTORS file

"""Tools for input/output of impedance data, and impedance visualization."""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from openwind.continuous import Physics

def write_impedance(frequencies, impedance, filename, column_sep=' '):
    """
    Write the impedance in a file.

    The file has the format

    .. code-block::

        (frequency)  (real part of impedance)  (imaginary part of impedance)


    Parameters
    ----------
    frequencies : list or np.array of float
        The frequency at which is evaluated the impedance
    impedance : list or np.array of float
        The complexe impedance at each frequency
    filename : string
        The name of the file in which is written the impedance (with the
        extension)
    column_sep : str, optional
        The column separator. Default is ' ' (space)

    """
    f = open(filename, "w")
    assert len(frequencies) == len(impedance)
    for k in range(len(frequencies)):
        f.write('{:e}{sep}{:e}{sep}{:e}{sep}\n'.format(frequencies[k],
                                                       np.real(impedance[k]),
                                                       np.imag(impedance[k]),
                                                       sep=column_sep))


def read_impedance(filename, df_filt=None, column_sep=None):
    """
    Read an impedance file.

    The impedance file must have the following format:

    * first column: the frequency in Hertz
    * second column: the real part of the impedance
    * third column: the imaginary part of the impedance

    .. code-block::

        # any comment
        (frequency)  (real part of impedance)  (imaginary part of impedance)

    The file can contain comments line beginning with a #.
    It is possible to filter the impedance by fixing the cutoff frequency step.
    It is performed by `scipy.signal.butter() <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html>`_
    and `scipy.signal.filtfilt() <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html>`_

    Parameters
    ----------
    filename : string
        The name of the file containing the impedance (with the extension).
    df_filt : float, optional
        The frequency step in Hz use to filter the impedance with a low-pass
        filter. Use `None` (Default value) to not filter the signal.
    column_sep : str, optional
        Column separator. Default is None corresponding to merged whitespace.

    Returns
    -------
    frequencies : np.array of float
        The frequencies at which is evaluated the impedance.
    impedance : np.array of float
        The complexe impedance at each frequency.

    Warnings
    -------
    The NaN values are excluded of the returned arrays

    """
    def parse_line(line):
        # Anything after a '#' is considered to be a comment
        line = line.split('#')[0]
        # Split the lines according to whitespace
        return line.split(column_sep)
    with open(filename) as file:
        lines = file.readlines()
    file_freq = []
    file_imped = []
    for line in lines:
        contents = parse_line(line)
        if len(contents) > 0:
            file_freq.append(float(contents[0]))
            file_imped.append(float(contents[1]) + 1j*float(contents[2]))
    frequencies = np.array(file_freq)
    impedance = np.array(file_imped)
    frequencies = frequencies[~np.isnan(file_imped)]
    impedance = impedance[~np.isnan(impedance)]
    delta_f = np.mean(np.diff(frequencies))

    if not not df_filt:
        ratio = delta_f/df_filt
        b, a = signal.butter(2, ratio)
        impedance = signal.filtfilt(b, a, impedance)

    return frequencies, impedance

def convert_frequencies_temperature(frequencies, temperature_in, temperature_out):
    """
    Convert a frequency axis according to the temperature.

    Only the modification of the sound celerity is accouted:

    .. math::
        f_{out} = f_{in} \\sqrt{\\frac{T_{out}}{T_{in}}}

    with the :math:`T_i=t_i + 273.15` the temperature in Kelvin

    Parameters
    ----------
    frequencies : array of float
        The "input" frequencies in Hz.
    temperature_in : float
        The input temperature in °C.
    temperature_out : float
        The output temperature in °C.

    Returns
    -------
    freq_ref : array of float
        The output frequencies in Hz.

    """
    if temperature_out != temperature_in:
        phys_meas = Physics(temperature_in)
        phys_comp = Physics(temperature_out)
        ratio_temp = np.sqrt(phys_comp.T(0) / phys_meas.T(0))
    else:
        ratio_temp = 1.

    freq_ref = frequencies*ratio_temp
    return freq_ref

def plot_impedance(frequencies, impedance, Zc0=1, dbscale=True, figure=None,
                   label=None, **kwargs):
    """
    Plot the impedance of the instrument.

    Parameters
    ----------
    impedance : array(complex)
        Sequence of impedance values for successive frequencies.
    Zc0 : float
        Characteristic impedance (or 1 if the impedance
        is already nondimensionalized).
    dbscale : bool, optional
        If True, the modulus is plotted with a dB scale, else a linear scale is
        used. The default is True.
    figure : matplotlib.Figure, optional
        Where to plot. By default, opens a new figure.
    label : str, optional
        The label associated to the curve. Default is None
    **kwargs : key word arguments
        Passed to `plt.plot() <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html>`_.
    """
    if not figure:
        fig = plt.figure()
    else:
        fig = figure
    ax = fig.get_axes()

    ylabel = '|Z|'
    if Zc0 != 1:
        ylabel += '/Zc'

    if len(ax) < 2:
        ax = [fig.add_subplot(2, 1, 1)]
        ax.append(fig.add_subplot(2, 1, 2, sharex=ax[0]))
        ax[0].grid()
        ax[1].grid()
    if dbscale:
        ax[0].plot(frequencies, 20*np.log10(np.abs(impedance/Zc0)), label=label, **kwargs)
        ylabel += ' (dB)'

    else:
        ax[0].plot(frequencies, np.abs(impedance/Zc0), label=label, **kwargs)
        ax[0].set_ylabel("|Z|")
    ax[0].set_ylabel(ylabel)
    if label:
        ax[0].legend(loc='upper right')

    ax[1].plot(frequencies, np.angle(impedance), **kwargs)
    ax[1].set_xlabel("Frequency (Hz)")
    ax[1].set_ylabel("angle(Z)")
    ax[1].get_yaxis().set_ticks([-np.pi/2, 0, np.pi/2])
    ax[1].get_yaxis().set_ticklabels(
        ['$-\pi/2$', '0', '$\pi/2$']
    )

def plot_reflection(frequencies, impedance, Zc0,
                    complex_plane=True, figure=None, **kwargs):
    """Plot the reflection function of the instrument.

    Parameters
    ----------
    impedance : array(complex)
        Sequence of impedance values for successive frequencies.
    Zc0 : float
        Characteristic impedance (or 1 if the impedance
        is already nondimensionalized).
    complex_plane : bool, optional
        Whether to plot in the complex plane,
        i.e. with axes (x, y) = (real, imag),
        rather than (x, y) = (freq, unwrapped argument).
        The default is True.
    figure : matplotlib.Figure, optional
        Where to plot. By default, opens a new figure.
    **kwargs : key word arguments
        Passed to `plt.plot() <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html>`_.
    """
    if not figure:
        fig = plt.figure()
    else:
        fig = figure
    ax = fig.get_axes()
    if len(ax) < 1 and complex_plane:
        ax = [fig.add_axes([.1, .1, .8, .8])]
    elif len(ax) < 2 and not complex_plane:
        ax = [fig.add_subplot(2, 1, 1)]
        ax.append(fig.add_subplot(2, 1, 2, sharex=ax[0]))

    Ref = (impedance - Zc0)/(impedance + Zc0)
    if complex_plane:
        ax[0].plot(np.real(Ref), np.imag(Ref), **kwargs)
        ax[0].legend()
        ax[0].set_xlabel("real(R)")
        ax[0].set_ylabel("imag(R)")
    else:
        ax[0].plot(frequencies, (np.abs(Ref)), **kwargs)
        ax[0].set_ylabel("|R|")
        ax[0].legend()
        ax[1].plot(frequencies, (np.unwrap(np.angle(Ref))), **kwargs)
        ax[1].set_xlabel("Frequency (Hz)")
        ax[1].set_ylabel("angle(R)")

def resonance_frequencies(frequencies, impedance, k=5):
    """
    Find the first k resonance frequencies of an impedance without noise.

    We define a resonance frequency as a frequency where the phase is zero
    and decreasing.

    Parameters
    ----------
    k : int, optional
        The number of resonance included. The default is 5.

    Returns
    -------
    list of float
    """
    phase = np.angle(impedance)
    signchange = np.diff(np.sign(phase)) < 0
    no_discontinuity = np.abs(np.diff(phase)) < np.pi
    valid_indices, = np.where(signchange & no_discontinuity)
    indi = valid_indices[:k]

    # Find the zero crossing by linear interpolation
    df = frequencies[indi+1] - frequencies[indi]
    dphi = phase[indi+1] - phase[indi]
    freq_zero_phase = frequencies[indi] - phase[indi] * (df/dphi)

    return freq_zero_phase

def antiresonance_frequencies(frequencies, impedance, k=5):
    """
    Find the first k anti-resonance frequencies of an impedance without noise.

    We define a resonance frequency as a frequency where the phase is zero
    and increasing.

    Parameters
    ----------
    k : int, optional
        The number of resonance included. The default is 5.

    Returns
    -------
    list of float
    """
    return resonance_frequencies(frequencies, np.conjugate(impedance), k)

def find_peaks_measured_impedance(frequencies, impedance, Npeaks=10, fmin=0):
    """
    Find peaks frequency and magnitudes, for data with noise.

    The peaks are found with `signal.find_peaks <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html>`_.
    The magnitudes are estimated by fitting a parabol on the modulus in dB.
    The frequencies are estimated by the zero of the linear regression of the
    imaginary part.

    Parameters
    ----------
    frequencies : np.array
        Frequencies values
    impedance : np.array
        The impedance value at each frequency.
    Npeaks : int, optional
        The number of peaks researched. The default is 10.
    fmin : float, optional
        The minimal frequency considered. The default is 0.

    Returns
    -------
    res_mag : np.array
        Array of the peaks magnitude.
    res_freq : np.array
        Array of peaks frequency.

    """
    impedance_db = 20*np.log10(np.abs(impedance))
    ind_peaks, info = signal.find_peaks(impedance_db, prominence=10, height=0)
    amp_peaks = info['peak_heights']
    f_peaks = frequencies[ind_peaks]

    ind_peaks = ind_peaks[f_peaks > fmin]
    amp_peaks = amp_peaks[f_peaks > fmin]
    f_peaks = f_peaks[f_peaks > fmin]

    if len(f_peaks) > Npeaks:
        f_peaks = f_peaks[:Npeaks]
        amp_peaks = amp_peaks[:Npeaks]
    res_mag = np.zeros(Npeaks)
    res_freq = np.zeros(Npeaks)

    for k, f_peak in enumerate(f_peaks):
        ind_min = max(ind_peaks[k]-2, 0)
        ind_max = min(ind_peaks[k]+2, len(frequencies)-1)
        f1 = np.min([f_peak*2**(-20/1200), frequencies[ind_min]])
        f2 = np.max([f_peak*2**(+20/1200), frequencies[ind_max]])
        ind_fit = np.logical_and(frequencies >= f1, frequencies <= f2)
        x = frequencies[ind_fit] - f_peak
        y = impedance_db[ind_fit] / amp_peaks[k]
        pol = np.polyfit(x, y, 2)
        x0 = - pol[1] / (2*pol[0])
        res_mag[k] = 10**((np.polyval(pol, x0) * amp_peaks[k])/20)

        f1 = np.min([f_peak*2**(-10/1200), frequencies[ind_min]])
        f2 = np.max([f_peak*2**(+10/1200), frequencies[ind_max]])
        ind_fit = np.logical_and(frequencies >= f1, frequencies <= f2)
        x = frequencies[ind_fit]
        y = impedance[ind_fit].imag
        polf = np.polyfit(x, y, 1)
        res_freq[k] = -polf[1]/polf[0]
    return res_mag, res_freq

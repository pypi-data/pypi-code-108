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


"""Methods to properly export temporal simulated data to an audio file."""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter


# ========== SIGNAL PROCESSING ==========

def antialias(signal, dt, cutoff_freq=18000, order=5):
    """
    Decimate high frequencies using a digital Butterworth filter.

    Parameters
    ----------
    signal : array
        the rough signal to treat.
    dt : float
        the step time of the input signal (1/sample rate).
    cutoff_freq : float, optional
        The highest frequency over which the signal is filtered. The default is
        18000.
    order : int, optional
        the filter order. The default is 5.

    Returns
    -------
    array
        The filtered signal.

    """
    """"""
    nyq = 0.5 / dt
    normal_cutoff = cutoff_freq / nyq
    if normal_cutoff > 1:
        # Can't antialias beyond the Nyquist frequency!
        return signal
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, signal)


def resample(signal, dt, samplerate=44100, cutoff_freq=18000):
    """
    Change sampling rate of signal, applying anti-aliasing if needed.

    Parameters
    ----------
    signal : array
        the rough signal to treat.
    dt : float
        the step time of the input signal (1/(old sample rate)).
    samplerate : float, optional
        The *new* sample rate. The default is 44100.
    cutoff_freq : float, optional
        The highest frequency over which the signal is filtered. The default is
        18000.

    Returns
    -------
    array
        The resampled signal.

    """
    signal = antialias(signal, dt)
    Tmax = dt*len(signal)
    ts_before = np.linspace(0, Tmax, len(signal))
    ts_after = np.arange(0, Tmax, 1.0/samplerate)
    return np.interp(ts_after, ts_before, signal)


def export_mono(filename, out, ts, verbose=True):
    """
    Export simulation data to an audio file.

    Resamples with antialiasing, and normalizes amplitude so that the highest
    peak is at 0 dB.

    Parameters
    ----------
    filename : str
        The name of the file in which write the signal.
    out : array(float)
        1D array of data to export.
    ts : array(float)
        1D array of times of the simulation. We assume constant increment.
    """
    dt = ts[1] - ts[0]
    assert np.allclose(ts[1:], ts[:-1] + dt)

    samplerate = 44100
    out_interp = resample(out, dt, samplerate=samplerate)

    out_interp /= np.max(np.abs(out_interp))  # Normalize to [-1,1]
    wavfile.write(filename, samplerate, out_interp)

    if verbose:
        print("Wrote audio to", filename)

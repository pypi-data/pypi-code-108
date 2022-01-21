#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# License: MIT


__all__ = ["load"]

import numpy as npo


def load(filename, Nfreq=801, skiprows=8):
    """Load measurement data.

    Parameters
    ----------
    filename : str
        Name of the file to load.

    Returns
    -------
    freqs: array
        Frequencies (in Hz)

    amplitude: array
        S11 amplitude (in dB)

    phase: array
        S11 phase (in degrees)

    """

    data = npo.loadtxt(filename, skiprows=skiprows, delimiter=",", max_rows=Nfreq)

    freqs, amplitude, phase = data.T[0:3]
    return freqs, amplitude, phase

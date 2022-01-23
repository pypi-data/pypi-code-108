# BSD 3-Clause License
#
# Copyright (c) 2021, Austin Cummings
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# todo: Add folder output and save figures

from enum import IntEnum
import numpy as np
import matplotlib.pyplot as plt
# from matplotlib  import cm
# from labellines import labelLine, labelLines

# from scipy import interpolate
# from scipy.interpolate import griddata
# from scipy.optimize import curve_fit

# from . import atmosphere as atm
# from . import geometry as geo
# from . import constants as const
# from . import fit_func as fitf

plt.rcParams['axes.labelsize'] = 13
plt.rcParams['xtick.labelsize'] = 11
plt.rcParams['ytick.labelsize'] = 11
plt.rcParams['legend.fontsize'] = 11
plt.rcParams.update({'figure.autolayout': True})


class Plot(IntEnum):
    """
    Enum to identify which plots to produce
    """
    none = 0
    basic = 2
    general = 3
    all = 4


###################################################################
# General Plots

def plot_wavelength_distribution(wavelengths, photons):
    """Plots the wavelength distribution.
    Plots the differential wavelength distribution (non-normalized) of the Cherenkov photons arriving on the detection plane
    Because the angles involved are small, the distribution should be largely the same viewing anywhere on the detection plane

    Parameters
    ----------
    wavelengths: [array]
        [description]
    photons : [type]
        [description]

    Returns
    -------
    ArrayLike
        ptical depth (tau: unitless)
    """

    fig = plt.figure()
    plt.plot(wavelengths, photons)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel(r'$\frac{dN_{\gamma}}{d\lambda}$')
    plt.grid(which='both')

    return fig


def plot_3D_spatial_distribution(r_bins, det_array):
    # Plots the 3-Dimensional spatial distribution (per m^2) of the Cherenkov photons arriving on the detection plane

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.set_xlabel('X (km)')
    ax1.set_ylabel('Y (km)')
    im = ax1.imshow(det_array, interpolation='nearest', origin='lower', extent=[r_bins[0], r_bins[-1], r_bins[0], r_bins[-1]])
    fig.colorbar(im, ax=ax1)

    return fig


def plot_photon_time_spread(r_bins, time_bins, time_counts):
    # Plots the time spread within which 90% of the arriving photons arrive (in s), per spatial bin

    # Calculate the upper and lower time bounds which contain the data
    cumulative_counts = np.cumsum(time_counts, axis=1) / np.sum(time_counts, axis=1)[:, None]
    low_bin, high_bin = np.argmax(cumulative_counts >= 0.05, axis=1), np.argmax(cumulative_counts >= 0.95, axis=1)
    time_diffs = time_bins[high_bin] - time_bins[low_bin]

    fig = plt.figure()
    plt.plot(r_bins[:-1], time_diffs)
    plt.yscale('log')
    plt.xlabel('Distance From Shower Axis (km)')
    plt.ylabel('90% Time Spread (ns)')
    plt.grid(which='both')

    return fig


def plot_photon_angular_spread(r_bins, angular_bins, angular_counts):
    # Plots the angular spread within which 90% of the arriving photons arrive (in degrees), per spatial bin

    # Calculate the upper and lower angular bounds which contain the data
    cumulative_counts = np.cumsum(angular_counts, axis=1) / np.sum(angular_counts, axis=1)[:, None]
    low_bin, high_bin = np.argmax(cumulative_counts >= 0.05, axis=1), np.argmax(cumulative_counts >= 0.95, axis=1)
    angular_diffs = angular_bins[high_bin] - angular_bins[low_bin]

    fig = plt.figure()
    plt.plot(r_bins[:-1], angular_diffs)
    plt.yscale('log')
    plt.xlabel('Distance From Shower Axis (km)')
    plt.ylabel('90% Angular Spread (degrees)')
    plt.grid(which='both')

    return fig

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

''' Plotting routines

.. autosummary::
   :toctree:
   :recursive:

   plot_wavelength_distribution
   plot_3D_spatial_distribution
   plot_photon_time_spread
   plot_photon_angular_spread

'''

from enum import IntEnum
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from matplotlib  import cm
from labellines import labelLine, labelLines

params = {'axes.labelsize': 13,
          'xtick.labelsize': 11,
          'ytick.labelsize': 11,
          'legend.fontsize': 11,
          'figure.autolayout': True}
plt.rcParams.update(params)

plot_out_dir = "plots/"


class Plot(IntEnum):
    """
    Enum to identify which plots to produce
    """
    none = 0
    basic = 1
    general = 2
    all = 3


###################################################################
# Basic Plots

def plot_wavelength_distribution(wavelengths, photons):
    """Plots the wavelength distribution.

    Plots the differential wavelength distribution (non-normalized) of the Cherenkov photons arriving on the detection plane
    Because the angles involved are small, the distribution should be largely the same viewing anywhere on the detection plane

    Parameters
    ----------
    wavelengths: ArrayLike
        wavelength bins of Cherenkov photons
    photons : ArrayLike
        photons within each wavelength bin

    Returns
    -------
    matplot.figure
        plot of the wavelength distribution of the arriving Cherenkov photons
    """

    fig = plt.figure()
    plt.plot(wavelengths, photons)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel(r'$\frac{dN_{\gamma}}{d\lambda}$')
    plt.grid(which='both')

    return fig


def plot_3D_spatial_distribution(r_bins, det_array): 
    """Plots the 3-Dimensional spatial distribution

    Plots the 3-Dimensional spatial distribution (per m^2) of the Cherenkov photons arriving on the detection plane.
    Only plots the positive quadrant in 3 dimensions to improve number of samples due to shower symmetry
    
    Parameters
    ----------
    r_bins: ArrayLike
        spatial bins within which to bin the photons
    det_array : ArrayLike
        2-Dimensional histogram of photons within the spatial bins

    Returns
    -------
    matplot.figure
        plot of the 3-Dimensional spatial distribution of the arriving Cherenkov photons
    """

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.set_xlabel('X (km)')
    ax1.set_ylabel('Y (km)')
    im = ax1.imshow(det_array, interpolation='nearest', origin='lower', extent=[r_bins[0], r_bins[-1], r_bins[0], r_bins[-1]])
    fig.colorbar(im, ax=ax1)

    return fig


def plot_photon_time_spread(r_bins, time_bins, time_counts):
    """Plots the time distribution.

    Plots the time spread within which 90% of the arriving Cherenkov photons arrive (in ns), per spatial bin

    Parameters
    ----------
    r_bins: ArrayLike
        spatial bins within which to bin the photons
    time_bins : ArrayLike
        time bins within which to bin the photons
    time_counts : ArrayLike
        photons within each spatial and time bin

    Returns
    -------
    matplot.figure
        plot of the time distribution of the arriving Cherenkov photons
    """

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
    """Plots the angular distribution.

    Plots the angular spread within which 90% of the arriving Cherenkov photons arrive (in degrees), per spatial bin

    Parameters
    ----------
    r_bins: ArrayLike
        spatial bins within which to bin the photons
    angular_bins : ArrayLike
        angular bins within which to bin the photons
    angular_counts : ArrayLike
        photons within each spatial and angular bin

    Returns
    -------
    matplot.figure
        plot of the time distribution of the arriving Cherenkov photons
    """

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

###################################################################
# General Plots

def plot_altitude_profile(Ls, zs):
    """Plots the altitude profile

    Plots the altitude profile for along the shower trajectory

    Parameters
    ----------
    Ls: ArrayLike
        distance along the shower trajectory in km
    zs : ArrayLike
        altitudes of each point in km

    Returns
    -------
    matplot.figure
        plot of the altitude profile along the shower trajectory
    """

    fig = plt.figure()
    plt.plot(Ls, zs)
    plt.yscale('log')
    plt.xlabel('Distance along trajectory (km)')
    plt.ylabel('Altitude (km)')
    plt.grid(which = 'both')
    
    return fig

def plot_slant_depth_profile(Ls, slant_depths):
    """Plots the slant depth profile

    Plots the slant depth profile for along the shower trajectory

    Parameters
    ----------
    Ls: ArrayLike
        distance along the shower trajectory in km
    slant_depths : ArrayLike
        slant depths of each point in g/cm^2

    Returns
    -------
    matplot.figure
        plot of the slant depth profile along the shower trajectory
    """
    
    fig = plt.figure()
    plt.plot(Ls, slant_depths)
    plt.yscale('log')
    plt.xlabel('Distance along trajectory (km)')
    plt.ylabel('Slant depth '+r'$(\mathrm{g} \, \mathrm{cm}^{-2})$')
    plt.grid(which = 'both')
    
    return fig

def plot_charged_particle_longitudinal_profile(slant_depths, charged_particles):
    """Plots the longitudinal profile of charged particles

    Plots the longitudinal charged particle profile of the shower used to generate the Cherenkov emission

    Parameters
    ----------
    slant_depths : ArrayLike
        slant depths of each point in g/cm^2
    charged_particles: ArrayLike
        the number of charged particles at each slant depth

    Returns
    -------
    matplot.figure
        plot of the longitudinal charged particle profile
    """
    
    fig = plt.figure()
    plt.plot(slant_depths, charged_particles)
    plt.yscale('log')
    plt.xlabel('Slant depth '+r'$(\mathrm{g} \, \mathrm{cm}^{-2})$')
    plt.ylabel('Charged Particles')
    plt.grid(which = 'both')
    
    return fig

def plot_Cherenkov_longitudinal_profile(slant_depths, photons, attenuated_photons = None):
    """Plots the longitudinal profile of Cherenkov photons

    Plots the longitudinal profile of the generated Cherenkov emission, both with and without atmospheric atenuation

    Parameters
    ----------
    slant_depths : ArrayLike
        slant depths of each point in g/cm^2
    photons: ArrayLike
        the number of Cherenkov photons at each slant depth
    attenuated_photons: ArrayLike
        the number of Cherenkov photons at each slant depth, corrected for by atmospheric attenuation

    Returns
    -------
    matplot.figure
        plot of the longitudinal profile of Cherenkov photons
    """
    
    fig = plt.figure()
    plt.plot(slant_depths, photons, color = 'red', label = 'No scattering')
    if isinstance(attenuated_photons, np.ndarray):
        plt.plot(slant_depths, attenuated_photons, color = 'blue', linestyle = '--', label = 'With scattering')
    plt.yscale('log')
    plt.xlabel('Slant depth '+r'$(\mathrm{g} \, \mathrm{cm}^{-2})$')
    plt.ylabel('Cherenkov photons')
    plt.grid(which = 'both')
    
    if isinstance(attenuated_photons, np.ndarray):
        plt.legend()
    
    return fig

###################################################################
# All Plots (atmospheric information)

def plot_atmospheric_density(zs, densities):
    """Plots the atmospheric density profile

    Parameters
    ----------
    zs: ArrayLike
        altitudes in km
    densities : ArrayLike
        atmospheric densities in g/cm^3

    Returns
    -------
    matplot.figure
        plot of the atmospheric density profile
    """
    
    fig = plt.figure()
    plt.plot(zs, densities)
    plt.yscale('log')
    plt.xlabel('Altitude (km)')
    plt.ylabel('Atmospheric density '+r'$(\mathrm{g} \, \mathrm{cm}^{-3})$')
    plt.yscale('log')
    plt.grid(which = 'both')
    
    return fig

def plot_extinction_coefficient(alpha):
    """Plots the extinction coefficient as a function of wavelength and altitude

    Parameters
    ----------
    alpha: ArrayLike
        array containing the wavelength, altitude, and extinction coefficient data

    Returns
    -------
    matplot.figure
        plot of the extinction coefficient
    """

    # Loads in data
    zs, wavelengths = np.meshgrid(alpha[1],alpha[0])
    alphas = alpha[2]
    
    # External array to interpolate over
    z_grid = np.linspace(0,50,11)
    w_grid = np.linspace(270,1000,100)
    stretched_z_grid, stretched_w_grid = np.meshgrid(z_grid,w_grid)

    # Interpolating values
    alpha_array = 1000*np.exp(griddata((zs.flatten(), wavelengths.flatten()), alphas.flatten(), (stretched_z_grid, stretched_w_grid), method='cubic', fill_value = 0))

    cm_subsection = np.linspace(0,1,len(z_grid))
    colors = [ cm.jet(x) for x in cm_subsection ]
    
    fig = plt.figure()
    for i in range(0, len(z_grid)):
        if z_grid[i]%5 == 0:
            plt.plot(w_grid, alpha_array[:,i], color = colors[i], label =str(z_grid[i])+'km')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Extinction coefficient '+r'$(\mathrm{km}^{-1})$')
    plt.yscale('log')
    plt.grid(which = 'both')
    labelLines(plt.gca().get_lines(),xvals=(310, 1000),zorder=2.5)
    
    return fig

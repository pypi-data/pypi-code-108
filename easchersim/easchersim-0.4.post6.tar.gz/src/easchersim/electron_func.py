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

''' Electron Functions

.. autosummary::
   :toctree:
   :recursive:

    Lorentz_factor
    particle_velocity
    gyroradius
    geomagnetic_deflection_correction
    Hillas_Energy_Distribution
    Hillas_Angular_Distribution
    Lafebre_Lateral_Distribution
    Lafebre_Lag_Time_Distribution
    Greisen_Longitudinal_Profile
    CORSIKA_interpolation

'''

import numpy as np
from scipy import interpolate
import scipy.stats as st

from . import io_func
from . import constants as const
from . import atmosphere as atm


def Lorentz_factor(energy):
    """Calculate the Lorentz factor of an electron with a given energy in MeV

    Parameters
    ----------
    energy : float
        e- energy in MeV

    Returns
    -------
    float
        Lorentz factor
    """
    gamma = energy / const.electron_mass

    return gamma


def particle_velocity(energy):
    """Calculate the speed of an electron relative to the speed of light with a given energy in MeV

    Parameters
    ----------
    energy : float
        e- energy in MeV

    Returns
    -------
    float
        beta: speed of e- relative to c
    """
    # Calculate the particle's Lorentz factor
    particle_Lorentz_factor = Lorentz_factor(energy)

    beta = np.sqrt(1 - 1 / (particle_Lorentz_factor**2))

    return beta


def gyroradius(electron_energy, electron_zenith, electron_azimuth, magnetic_field_strength, magnetic_field_zenith):
    """Calculates the gyroradius (in km) of an electron with a given energy (in MeV), zenith angle (with respect to trajectory: in degrees)
    and azimuth angle (in degrees) inside a magnetic field with a given strength (in uT) and zenith angle(in degrees)

    Parameters
    ----------
    electron_energy : ArrayLike
        e- energy in MeV
    electron_zenith : ArrayLike
        e- zenith in degrees
    electron_azimuth : ArrayLike
        e- azimuth in degrees
    magnetic_field_strength : float
        magnetic field strength in uT
    magnetic_field_zenith : float
        magnetic field inclination with respect to shower axis in degrees

    Returns
    -------
    ArrayLike
        gyroradius in km
    """
    # Calculates the normalized pointing array of the magnetic field, aligning the incident particle along the z axis
    magnetic_field_zenith = (np.pi / 180) * magnetic_field_zenith
    magnetic_field_direction = np.array([np.sin(magnetic_field_zenith), 0, np.cos(magnetic_field_zenith)])

    # Initializes the normalized velocity vector of the particle (aligned along the z axis)
    electron_zenith = (np.pi / 180) * electron_zenith
    particle_direction = np.array([np.cos(electron_azimuth[None, None, :]) * np.sin(electron_zenith[:, :, None]), np.sin(electron_azimuth[None, None, :]) * np.sin(electron_zenith[:, :, None]), np.cos(electron_zenith[:, :, None] * np.ones(len(electron_azimuth))[None, None, :])])

    # Calculating the Lorentz factor and particle relative velocity
    particle_Lorentz_factor, particle_relative_velocity = Lorentz_factor(electron_energy), particle_velocity(electron_energy)

    particle_gyroradius = particle_Lorentz_factor[None, :, None] * const.electron_mass * const.MeV_to_kg * particle_relative_velocity[None, :, None] * const.cl / (const.electron_charge * np.linalg.norm(np.cross(particle_direction, magnetic_field_strength * 1e-6 * magnetic_field_direction, axis=0), axis=0))

    return particle_gyroradius


def geomagnetic_deflection_correction(Ls, L_detector, electron_energy, electron_zenith, electron_azimuth, magnetic_field_strength, magnetic_field_zenith):
    """Calculates the deflection correction (in km) of an electron with a given energy (in MeV), zenith angle (with respect to trajectory: in degrees)
    and azimuth angle (in degrees) inside a magnetic field with a given strength (in uT) and zenith angle(in degrees)

    TODO: RECONSIDER THIS WHOLE CONCEPT...

    Parameters
    ----------
    Ls : ArrayLike
        distance bins along the shower trajectory in km
    L_detector : float
        distance from the start of the shower to the detector in km
    electron_energy : ArrayLike
        e- energy in MeV
    electron_zenith : ArrayLike
        e- zenith in degrees
    electron_azimuth : ArrayLike
        e- azimuth in degrees
    magnetic_field_strength : float
        magnetic field strength in uT
    magnetic_field_zenith : float
        magnetic field inclination with respect to shower axis in degrees

    Returns
    -------
    float
        deflection correction in km
    """
    # Calculate the gyroradius of the electrons
    particle_gyroradius = gyroradius(electron_energy, electron_zenith, electron_azimuth, magnetic_field_strength, magnetic_field_zenith)

    # Calculate the deflected angle inside the given distance bins and the corresponding projection on the detection plane
    dLs = np.append(np.diff(Ls), Ls[-1] - Ls[-2])
    added_distance = np.reshape(np.random.choice([-1, 1], size=particle_gyroradius.shape), particle_gyroradius.shape) * (L_detector - Ls[None, :, None]) * (dLs[None, :, None] / particle_gyroradius) / np.sqrt(1 - (dLs[None, :, None] / particle_gyroradius)**2)

    return added_distance


def Hillas_Energy_Distribution(electron_energy, shower_age):
    """Calculates the total fraction of electrons present at a given shower age above an energy (in MeV) as given by:
    A.M. Hillas. Air. J. Phys. G, 8:1461-1473, 1982

    Parameters
    ----------
    electron_energy : ArrayLike
        e- energy in MeV
    shower_age : ArrayLike
        shower age

    Returns
    -------
    ArrayLike
        e- fraction above input energy at shower age
    """
    E0 = np.where(shower_age < 0.4, 26, 44 - 17 * (shower_age - 1.46)**2)

    if isinstance(shower_age, np.ndarray):
        part1 = 0.89 * E0 - 1.2
        part2 = E0[:, None] + electron_energy
        part3 = 1 + (electron_energy * shower_age[:, None]) * 1e-4

        electron_fraction = ((part1[:, None] / part2)**shower_age[:, None]) * (part3)**(-2)
    else:
        part1 = 0.89 * E0 - 1.2
        part2 = E0 + electron_energy
        part3 = 1 + (electron_energy * shower_age) * 1e-4

        electron_fraction = ((part1 / part2)**shower_age) * (part3)**(-2)

    return electron_fraction


def Hillas_Angular_Distribution(electron_energy, shower_age, us):
    """e- angular distribution (Hillas)

    Calculates (i) the corresponding angle (in degrees) of the scaled angular bin (u) and
    (ii) the fraction of electrons within the scaled angular bins
    for a given energy (in MeV) and shower age as given by: A.M. Hillas. Air. J. Phys. G, 8:1461-1473, 1982

    Parameters
    ----------
    electron_energy : ArrayLike
        e- energy in MeV
    shower_age : ArrayLike
        shower age
    us : ArrayLike
        scaled angular bins, following Hillas 1982

    Returns
    -------
    list of arrays
        angular distribution of electrons (bins in degrees, fraction of electrons per bin)
    """
    # Calculate the midpoint of the angular bins
    lower_us, upper_us = us[:-1], us[1:]
    mid_us = (lower_us + upper_us) / 2

    # Calculate the corresponding angle of the given bins
    v = electron_energy / (1150 + 454 * np.log(shower_age))
    average_w = 0.0054 * electron_energy * (1 + v) / (1 + 13 * v + 8.3 * v * v)
    w = mid_us[:, None] * average_w[None, :]
    theta = (180 / np.pi) * np.arccos(1 - w / (2 * (electron_energy[None, :] / 21)**2))

    # Calculate the fraction of electrons within each scaled angular bin
    A = np.where(electron_energy < 350, 0.777, 1.318)
    z0 = np.where(electron_energy < 350, 0.59, 0.37)
    z_values = [np.sqrt(lower_us), np.sqrt(upper_us)]
    lambda_ls = [np.where((electron_energy[None, :] < 350) & (z[:, None] < 0.59), 0.478, np.where((electron_energy[None, :] < 350) & (z[:, None] >= 0.59), 0.380, np.where((electron_energy[None, :] >= 350) & (z[:, None] < 0.37), 0.413, 0.380))) for z in z_values]

    # Must consider the bins in z which cross z0 and have different behavior
    [n_lower, n_upper] = [-2 * A[None, :] * np.exp((-z_values[i][:, None] + z0[None, :]) / lambda_ls[i]) * lambda_ls[i] * (lambda_ls[i] + z_values[i][:, None]) for i in (0, 1)]
    [n_z0_lower, n_z0_upper] = [-2 * A[None, :] * lambda_ls[i] * (lambda_ls[i] + z0[None, :]) for i in (0, 1)]

    dn = np.where((z_values[0][:, None] < z0[None, :]) & (z_values[1][:, None] >= z0[None, :]), n_upper - n_z0_upper + n_z0_lower - n_lower, n_upper - n_lower)

    # Do not return NaN values
    NaN_values = np.isnan(theta)
    theta[NaN_values] = 0
    dn[NaN_values] = 0

    return [theta, dn]


def Lafebre_Lateral_Distribution(electron_energies, radiation_lengths, zs, coordinates):
    """Lateral distribution Lafebre

    Randomly samples lateral offsets of electrons (in km) from the shower axis, given their primary energy (in MeV),
    their modified shower age (radiation length measured from shower maximum), their altitudes, and the desired shape of the output array
    as parameterized by: S. Lafebre, R. Engel, H. Falcke, J. Horandel, T. Huege, J. Kuijpers, and R. Ulrich. Astropart. Phys., 31:243-254, 2009

    Parameters
    ----------
    electron_energies : ArrayLike
        e- energy in MeV
    radiation_lengths : ArrayLike
        radiation length (X-Xmax)/X0
    zs : ArrayLike
        altitudes in km
    coordinates : ArrayLike
        coordinates of ellipse about which to sample lateral offsets

    Returns
    -------
    ArrayLike
        sampled lateral offsets for each point about the input ellipse
    """
    # Model is only parameterized within energy range 1MeV-1GeV
    modified_electron_energies = np.copy(electron_energies)
    modified_electron_energies[modified_electron_energies < 1] = 1
    modified_electron_energies[modified_electron_energies > 1000] = 1000

    # Model is only parameterized within shower age range -9-9
    radiation_lengths[radiation_lengths < -9] = -9
    radiation_lengths[radiation_lengths > 9] = 9

    # Model parameters
    logE = np.log(modified_electron_energies)
    x1 = 0.859 - 0.0461 * (logE**2) + 0.00428 * (logE**3)
    Lt = 0.0263 * radiation_lengths
    L0 = Lt + 1.34 + 0.160 * logE - 0.0404 * (logE**2) + 0.00276 * (logE**3)
    L1 = Lt - 4.33

    # Loading the desired shape of the samples
    zenith_shape, azimuth_shape = coordinates.shape[0], coordinates.shape[2]

    # Calculating Moliere Radius
    moliere = atm.moliere_radius(zs)

    # Randomly sample the lateral offsets using a scaled betaprime distribution
    sampled_offsets = np.transpose(np.array([moliere[i] * x1[i] * st.betaprime.rvs(L0[i], -L0[i] - L1[i], size=zenith_shape * azimuth_shape).reshape(zenith_shape, azimuth_shape) for i in range(0, len(modified_electron_energies))]), (1, 0, 2))

    return sampled_offsets


def Lafebre_Lag_Time_Distribution(electron_energies, radiation_lengths, zs, coordinates):
    """Randomly samples lag times of electrons (in s) from an imaginary particle travelling along the shower axis at the speed of light, given their primary energy (in MeV),
    their modified shower age (radiation length measured from shower maximum), their altitudes, and the desired shape of the output array
    as parameterized by: S. Lafebre, R. Engel, H. Falcke, J. Horandel, T. Huege, J. Kuijpers, and R. Ulrich. Astropart. Phys., 31:243-254, 2009

    Parameters
    ----------
    electron_energies : ArrayLike
        e- energies in MeV
    radiation_lengths : ArrayLike
        radiation length (X-Xmax)/X0
    zs : ArrayLike
        altitudes in km
    coordinates : ArrayLike
        coordinates of ellipse about which to sample lateral offsets

    Returns
    -------
    ArrayLike
        sampled lag times of electrons in s for each point about the input ellipse
    """
    # Model is only parameterized within energy range 1MeV-1GeV
    modified_electron_energies = np.copy(electron_energies)
    modified_electron_energies[modified_electron_energies < 1] = 1
    modified_electron_energies[modified_electron_energies > 1000] = 1000

    # Model is only parameterized within shower age range -4.5 to 9
    # lower limit adjusted to respected domains scaled betaprime distribution
    radiation_lengths[radiation_lengths < -4.45] = -4.45
    radiation_lengths[radiation_lengths > 9] = 9

    # Model parameters
    logE = np.log(modified_electron_energies)
    tau1 = np.exp(-2.71 + 0.0823 * logE - 0.114 * (logE**2))
    L0 = 1.70 + 0.160 * radiation_lengths - 0.142 * logE
    L1 = -3.21

    # Loading the desired shape of the samples
    zenith_shape, azimuth_shape = coordinates.shape[0], coordinates.shape[2]

    # Calculating Moliere Radius
    moliere = atm.moliere_radius(zs)

    # Randomly sample the lateral offsets using a scaled betaprime distribution
    sampled_lag_times = (1 / const.cl) * np.transpose(np.array([moliere[i] * tau1[i] * st.betaprime.rvs(L0[i], -L0[i] - L1, size=zenith_shape * azimuth_shape).reshape(zenith_shape, azimuth_shape) for i in range(0, len(modified_electron_energies))]), (1, 0, 2))

    return sampled_lag_times


def Greisen_Longitudinal_Profile(energy, slant_depth):
    """Calculates the number of charged particles for a given slant depth (in g/cm^2) and a given shower energy (in eV)
    as parameterized by Greisen, found in: Cosmic Rays and Particle Physics: 2nd Edition.

    Parameters
    ----------
    energy : float
        primary energy of shower in eV
    slant_depth : float
        slant depth along shower trajectory in g/cm^2

    Returns
    -------
    float
        the number of charged particles at the input slant depth for a shower with a given energy
    """
    # Convert the slant depth to radiation lengths
    radiation_length = slant_depth / 36.7

    # Convert the radiation lengths to shower age
    shower_age = 3 * radiation_length / (radiation_length + 2 * np.log(energy / 87e6))

    # Calculate the number of charged particles and filter out and NaN values
    charged_particles = (0.31 / ((np.log(1e17 / 87e6))**0.5)) * np.exp(radiation_length * (1 - 1.5 * np.log(shower_age)))
    charged_particles[np.isnan(charged_particles)] = 0

    return charged_particles


def CORSIKA_interpolation(energy, slant_depth, filename, simulated_energy):
    """Calculates the number of charged particles for a given slant depth (in g/cm^2) and a given shower energy (in eV)
    interpolating from a given charged particle longitudinal profile generated by CORSIKA and scaled linearly

    Parameters
    ----------
    energy : float
        primary energy of shower in eV
    slant_depth : float
        slant depth along shower trajectory in g/cm^2
    filename : str
        name of CORSIKA file to interpolate
    simulated_energy : float
        shower energy used for CORSIKA simualtion in eV

    Returns
    -------
    ArrayLike
        charged particle profile scaled to shower energy
    """
    # Load in the CORSIKA showers
    CORSIKA_showers = io_func.CORSIKA_Shower_Reader(filename)

    # Calculate the average of these showers
    average_shower = io_func.average_CORSIKA_profile(CORSIKA_showers)
    del CORSIKA_showers

    # Create an interpolation object of the average shower
    charged_particles_from_slant_depth = interpolate.interp1d(average_shower[0], average_shower[1], fill_value='extrapolate')
    del average_shower

    # Calculate the number of charged particles and filter out NaN and negative values
    charged_particles = (energy / simulated_energy) * charged_particles_from_slant_depth(slant_depth)
    charged_particles[np.isnan(charged_particles)] = 0
    charged_particles[charged_particles < 0] = 0

    return charged_particles

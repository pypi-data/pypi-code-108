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

# TODO: calculate X offset based on energy of shower in sim file

''' Spatial Cherenkov Profile

.. autosummary::
   :toctree:
   :recursive:

   cherenkov_from_particle_profile

'''
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

from . import io_func
from . import constants as const
from . import atmosphere as atm
from . import geometry as geo
from . import cher_func as chf
from . import electron_func as elef
from . import fit_func as fitf
from . import plot

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

np.seterr(divide='ignore', invalid='ignore')
np.set_printoptions(threshold=sys.maxsize)


def cherenkov_from_particle_profile(detector_altitude,
                                    energy, theta_D,
                                    L_particle, L_detector, L_atmosphere,
                                    atmo, mag_field, run_set,
                                    plots, save_fig
                                    ):
    """Calculates Spatial Cherenkov Profile given geometric constraints

    Parameters
    ----------
    detector_altitude : float
        Altitude of the detection plane in km
    energy : float
        primary energy of the shower in eV
    theta_D : float
        detector viewing angle in degrees
    L_particle : float
        propagated distance of the particle (in km) before interaction
    L_detector : float
        path length to the detector in km
    L_atmosphere : float
        path length to the top of the atmosphere in km
    atmo : configparse_section Obj
        contains atmospheric settings: scattering, alpha_value file
    mag_field : configparse_section Obj
        contains magnetic field settings: use, strength and angle
    run_set : configparse_section Obj
        contains all run specific settings like filenames, binnings and boundaries
    plots : str
        Description of which type of plots to make: none, general or all
    save_fig : bool
        Should be figures saved to disk

    Returns
    -------
    dict
        Dictionary of simulation results
    """
    # Calculating slant depth profile as a function of propagation distance
    slant_depth_data = atm.slant_X_from_L_table([L_particle, min([L_detector, L_atmosphere])], detector_altitude, theta_D)

    # Creating interpolation objects to get slant depth from propagation distance and vice-versa
    L_from_slant_depth = interpolate.interp1d(slant_depth_data[1], slant_depth_data[0], fill_value='extrapolate')

    ################################################################
    # Initializing Atmosphere

    # Initializing the slant depth bins to calculate photon content
    max_x = float(run_set.getlist('slantDepth')[1])
    x_bins = int(run_set.getlist('slantDepth')[0])
    if max_x > 0:
        slant_depths = np.linspace(0, min(slant_depth_data[1][-1], max_x), x_bins)
    else:
        slant_depths = np.linspace(0, slant_depth_data[1][-1], x_bins)

    dx = slant_depths[1] - slant_depths[0]

    # Deleting the slant depth data object to save memory
    del slant_depth_data

    # Calculating the distance along the trajectory for each slant depth value
    Ls = L_from_slant_depth(slant_depths)

    # Calculating the altitude of each slant depth value
    zs = geo.z_from_L(Ls, theta_D, detector_altitude)

    # Integral calculation for time it takes photon to reach detector plane along shower axis
    # Take points along the path from the emission point to the detection plane
    Ls_t_value_calc = np.array([np.linspace(L_bottom, L_detector, 1000) for L_bottom in Ls])

    # Calculate the index of refraction at these points (using a reference 450nm wavelength)
    zs_t_value_calc = geo.z_from_L(Ls_t_value_calc, theta_D, detector_altitude)
    ns_t_value_calc = np.array([atm.index_of_refraction(zs_t_value_calc[i], 450) for i in range(0, len(Ls))])

    # Integrate the traversal time taking into account the changing speed of light and clear unneeded values
    t0s = np.trapz(ns_t_value_calc / const.cl, Ls_t_value_calc, axis=1)
    del Ls_t_value_calc, zs_t_value_calc, ns_t_value_calc

    # Initialize Wavelength Grid
    wavelength_bins, wavelength_lower, wavelength_upper = run_set.getlist('wavelength')
    wavelengths = np.linspace(float(wavelength_lower), float(wavelength_upper), int(wavelength_bins))

    # Loading in extinction coefficient from external file
    if atmo.get('alphaFile') != '':
        extinction_coefficient_file = atmo.get('alphaFile')
    else:
        extinction_coefficient_file = files("EASCherSim.data") / \
            "alpha_values_typical_atmosphere_updated.txt"
    alpha = atm.atmospheric_extinction_coefficient(extinction_coefficient_file)

    # Calculate the transmission coefficient for each emission point
    if atmo.getboolean('scattering'):
        if Ls[-1] < L_detector:
            extra_scattering = atm.optical_depth(alpha[0], alpha[1], alpha[2],
                                                 wavelengths,
                                                 np.linspace(Ls[-1], L_detector, 1000), detector_altitude,
                                                 theta_D,
                                                 False)[:, 0]

        else:
            extra_scattering = np.zeros(len(wavelengths))

        photon_transmission = np.exp(-atm.optical_depth(alpha[0], alpha[1], alpha[2],
                                     wavelengths,
                                     Ls, detector_altitude,
                                     theta_D,
                                     False) - extra_scattering[:, None])

    else:
        photon_transmission = np.ones((len(wavelengths), len(Ls)))

    # If considering all plot:
    # Plot atmospheric properties: density profile and scattering coefficients
    if plot.Plot[plots] > 2:
        plot.plot_atmospheric_density(np.linspace(0, const.alt_max,200), atm.atmos_density(np.linspace(0, 100,200)))
        if atmo.getboolean('scattering'):
            plot.plot_extinction_coefficient(alpha)

    del alpha

    ################################################################
    # Initializing shower

    # Calculating the number of electrons and positrons for each point in the shower
    if run_set.getboolean('useGreisenParametrization'):
        charged_parts = elef.Greisen_Longitudinal_Profile(energy, slant_depths)
    else:
        if run_set.get('protoShowerPofile') == '':
            filename = str(files("EASCherSim.data") / "Example_CORSIKA_proton_1e17eV.long")
            simulated_energy = 1e17
        else:
            filename = run_set.get('protoShowerPofile')
            simulated_energy = run_set.getfloat('protoShowerEnergy')
        charged_parts = elef.CORSIKA_interpolation(energy, slant_depths, filename, simulated_energy)

    # Calculating the position of the shower maximum, and the corresponding shower ages and radiation lenghts
    shower_xmax = slant_depths[np.argmax(charged_parts)]
    shower_age = 3 / (1 + 2 * shower_xmax / slant_depths)
    radiation_lengths = (slant_depths - shower_xmax) / 36.7

    ################################################################
    # Initializing Cherenkov photons

    # Calculating the threshold energy for Cherenkov production for each point,
    # using a reference 450nm wavelength
    Cherenkov_thresholds = chf.Cherenkov_threshold(zs, 450)

    # Calculating the bins in electron energy within which to generate Cherenkov emission
    # Spaced from the local Cherenkov threshold at each point to 0.1TeV (captures nearly
    # all of the charged particle behavior for all shower ages) in 30 bins
    electron_energy_bins = int(run_set.getlist('elEnergy')[0])
    upper_bound_electron_energy = float(run_set.getlist('elEnergy')[1])
    electron_energy_spacing = np.array([np.logspace(np.log10(thresh),
                                        np.log10(upper_bound_electron_energy),
                                        electron_energy_bins)
                                        for thresh in Cherenkov_thresholds])

    # Calculating the midpoint of the electorn energy bins and the fraction of electrons inside each bin
    electron_energies = electron_energy_spacing[:, :-1] + np.diff(electron_energy_spacing, axis=1) / 2
    electron_fractions = -np.diff(elef.Hillas_Energy_Distribution(electron_energy_spacing, shower_age), axis=1)

    # Calculate the total number of electrons contributing to Cherenkov emission per bin in energy and slant depth
    charged_parts_above_threshold = charged_parts[:, None] * electron_fractions

    # Calculating the total Cherenkov photons produced by electrons above the Cherenkov threshold
    total_Cherenkov_photons = (1 / atm.atmos_density(zs)[:, None, None]) * \
        1e-2 * \
        chf.Cherenkov_photons(zs, wavelengths, elef.particle_velocity(electron_energies)) * \
        charged_parts_above_threshold[:, :, None]

    # Applying atmospheric extinction to the propagated Cherenkov photons
    transmitted_Cherenkov_photons = total_Cherenkov_photons * photon_transmission.T[:, None, :]

    # Sum the Cherenkov photons in energy
    E_integrated_photons = np.sum(transmitted_Cherenkov_photons, axis=1)

    # Integrate the summed Cherenkov photons across slant depth
    X_integrated_photons = np.trapz(E_integrated_photons, slant_depths, axis=0)

    # Integrate the Cherenkov photons across wavelength
    W_integrated_photons = dx * np.trapz(transmitted_Cherenkov_photons, wavelengths * 1e-9, axis=2)

    # If considering general plots, show more shower information:
    # Plotting altitude profile, slant depth profile, charged particle longitudinal profile, and Cherenkov longitudinal profile
    if plot.Plot[plots] > 1:
        plot.plot_altitude_profile(Ls, zs)
        plot.plot_slant_depth_profile(Ls, slant_depths)
        plot.plot_charged_particle_longitudinal_profile(slant_depths, charged_parts)
        if atmo.getboolean('scattering'):
            plot.plot_Cherenkov_longitudinal_profile(slant_depths, np.trapz(np.sum(total_Cherenkov_photons, axis = 1), wavelengths * 1e-9, axis = 1), np.trapz(np.sum(transmitted_Cherenkov_photons, axis = 1), wavelengths * 1e-9, axis = 1))
        else:
            plot.plot_Cherenkov_longitudinal_profile(slant_depths, np.trapz(np.sum(total_Cherenkov_photons, axis = 1), wavelengths * 1e-9, axis = 1))

    ################################################################
    # Initialization for the angular distributions of electrons

    # Initializing the scaled angular bins to use for the electron angular distribution
    bins, start, stop = run_set.getlist('elZenith')
    scaled_angle_u = np.logspace(float(start), float(stop), num=int(bins))

    # Initializing the bins in azimuth about which to calculate photon content
    azimuth_bins = run_set.getint('ringAzimuthNumBin')
    Cherenkov_ring_azimuth = np.linspace(0, 2 * np.pi, azimuth_bins)

    ################################################################
    # Initializing the arrays to be used for the spatial, timing, and angular distributions of the arriving photons

    spatial_counts, time_counts, angle_counts = 0, 0 , 0

    spatial_bins = int(run_set.getlist('phSpatial')[0])
    bins, start, stop = run_set.getlist('phTime')
    time_bins = np.logspace(float(start), float(stop), num=int(bins))
    bins, start, stop = run_set.getlist('phZenith')
    angle_bins = np.logspace(float(start), float(stop), num=int(bins))

    # If generating plots, initialize the 2D spatial array
    if plot.Plot[plots] > 0:
        det_array = 0

    ################################################################
    # Beginning main loop
    # Loop over electron energy bins (start with the bin at the Cherenkov threshold for each altitude and move up to considered upper bound)

    with io_func.get_progress() as progress:
        io_func.flog(f'''Computing the Cherenkov Photon properties at an altitude of '''
                     f'''{detector_altitude}km for one EAS \n''')
        task = progress.add_task(f"1.Shower({energy}eV,{theta_D}deg,{L_particle}km)",
                                 total=electron_energies.shape[1])
        for i in range(0, electron_energies.shape[1]):
            # Selecting the electron energies and the Cherenkov photons emitted at this energy
            electron_energy, transmitted_photons = electron_energies[:, i], W_integrated_photons[:, i]

            # Calculate Lorentz factor and particle relative velocity to the speed of light
            electron_velocity = elef.particle_velocity(electron_energy)

            # Calculate the Cherenkov angle for each point and electron energy for a reference wavelength of 450nm
            Cherenkov_angles = chf.Cherenkov_angle(zs, 450, electron_velocity)

            # Setting NaN values equal to 0
            undefined_Cherenkov_angle = np.isnan(Cherenkov_angles)
            Cherenkov_angles[undefined_Cherenkov_angle] = 0
            transmitted_photons[undefined_Cherenkov_angle] = 0

            # Calculate Zenith angles and dn values at angles
            [electron_zenith_angle, electron_angular_content] = elef.Hillas_Angular_Distribution(electron_energy,
                                                                                                 shower_age,
                                                                                                 scaled_angle_u)

            # Dividing the generated Cherenkov photons into the corresponding bins in zenith angle
            angular_transmitted_photons = transmitted_photons[None, :] * electron_angular_content

            # Calculating the coordinates of the projected Cherenkov ring on the detection plane
            [ellipse_x, ellipse_y] = geo.ellipse_coordinates(Ls, L_detector,
                                                             electron_zenith_angle,
                                                             Cherenkov_angles, Cherenkov_ring_azimuth)

            # Calculating the arrival angle of the photons on the detection plane
            photon_arrival_angles = (180 / np.pi) * \
                np.arctan(np.sqrt(ellipse_x**2 + ellipse_y**2) / (L_detector - Ls[None, :, None]))

            # Randomly sampling lateral offsets and lag times for each Cherenkov photon generated
            lateral_offsets = elef.Lafebre_Lateral_Distribution(electron_energy, radiation_lengths, zs, ellipse_x)
            lag_times = elef.Lafebre_Lag_Time_Distribution(electron_energy, radiation_lengths, zs, ellipse_x)

            # Smearing sampled lateral offsets by randomly sampled azimuth angle
            sampled_angles = np.random.uniform(0, 2 * np.pi, size=ellipse_x.shape)
            x_offsets, y_offsets = lateral_offsets * np.cos(sampled_angles), lateral_offsets * np.sin(sampled_angles)

            del sampled_angles, lateral_offsets

            # Adding the randomly sampled offsets to each point about the Cherenkov ring
            ellipse_x += x_offsets
            ellipse_y += y_offsets

            del x_offsets, y_offsets

            # Calculating the distance from the shower axis for each point (in order to consider azimuthal symmetry)
            r_coordinates = np.sqrt(ellipse_x**2 + ellipse_y**2)

            del ellipse_x, ellipse_y
            total_propagation_times = (Ls[None, :, None] / const.cl + t0s[None, :, None] / np.cos((np.pi / 180) * photon_arrival_angles) + lag_times) / 1e-9
            total_propagation_times -= np.nanmin(total_propagation_times)

            # Calculating the number of Cherenkov photons arriving on the detection plane at each point along the Cherenkov ring
            photons_on_plane = (1 / azimuth_bins) * angular_transmitted_photons[:, :, None] * np.ones(azimuth_bins)[None, None, :]

            # Ignoring points which do not intersect the plane
            nan_indexes = np.isnan(r_coordinates)
            r_coordinates[nan_indexes] = 0
            total_propagation_times[nan_indexes] = 0
            photon_arrival_angles[nan_indexes] = 0
            photons_on_plane[nan_indexes] = 0

            # The first iteration of the loop has the maximum photon content, so at this step, the bounds are determined for the 2D histograms
            # that will be carried out for futher iterations in the loop
            if i == 0:
                # Find r bins such that a certain percentage of the total photon content is captured
                # We recommend 30% for near ring behavior
                pct_cap = float(run_set.getlist('phSpatial')[1])
                r_percentiles = fitf.weighted_percentile(r_coordinates.flatten(), pct_cap, weights=photons_on_plane.flatten())
                r_bins = np.linspace(0, r_percentiles, spatial_bins)

                # Calculate the size of one spatial bin in m^2
                pixel_size = ((r_bins[1] - r_bins[0]) * 1000)**2

                # Initializing the arrays to store the upper and lower bounds for the timing and angular photon distributions
                time_bounds, zenith_bounds = [], []

                # Loop over the spatial bins
                for j in range(0, len(r_bins) - 1):
                    # Find coordinates which are inside each spatial bin
                    r_lower, r_upper = r_bins[j], r_bins[j + 1]
                    in_range = (r_coordinates >= r_lower) & (r_coordinates <= r_upper)
                    in_range_time, in_range_zenith, in_range_photons = total_propagation_times[in_range], photon_arrival_angles[in_range], photons_on_plane[in_range]

                    # Calculate the 1% and 99% weighted percentiles of the arrival time and arrival angle inside the bin
                    time_percentiles = fitf.weighted_percentile(in_range_time.flatten(), np.array([1, 99]), weights=in_range_photons.flatten())
                    zenith_percentiles = fitf.weighted_percentile(in_range_zenith.flatten(), np.array([1, 99]), weights=in_range_photons.flatten())

                    time_bounds.append(time_percentiles)
                    zenith_bounds.append(zenith_percentiles)

                # Calculate the lower bound time and zenith offsets as a function of r (in km)
                time_offset = interpolate.interp1d(r_bins[:-1], np.array(time_bounds)[:, 0], kind='cubic', bounds_error=False, fill_value=0)
                angle_offset = interpolate.interp1d(r_bins[:-1], np.array(zenith_bounds)[:, 0], kind='cubic', bounds_error=False, fill_value=0)

            # Plot the photon intensity (in photons/m^2) in 2 dimensions
            if plot.Plot[plots] > 0:
                # Smear the calculated distances from shower axis about the axis random;y
                random_azimuth_angles = np.random.uniform(0, 2 * np.pi, size=r_coordinates.shape)
                x_coordinates, y_coordinates = r_coordinates * np.cos(random_azimuth_angles), r_coordinates * np.sin(random_azimuth_angles)

                # Shift the x coordinates by the calculated offset due to geomagnetic deflection (axis is arbitrary)
                if mag_field.getboolean('useField'):
                    x_coordinates += elef.geomagnetic_deflection_correction(Ls, L_detector,
                                                                            electron_energy,
                                                                            electron_zenith_angle,
                                                                            Cherenkov_ring_azimuth,
                                                                            mag_field.getfloat('strength'),
                                                                            mag_field.getfloat('angle'))

                # Update the 2D array stored in memory
                current_array = np.histogram2d(np.abs(x_coordinates.flatten()), np.abs(y_coordinates.flatten()), bins=(r_bins, r_bins), weights=photons_on_plane.flatten() / (4 * pixel_size))[0]
                det_array += current_array

                del random_azimuth_angles, x_coordinates, y_coordinates

            # Shifting the calculated values by the lower offset
            total_propagation_times -= time_offset(r_coordinates.flatten()).reshape(total_propagation_times.shape)
            photon_arrival_angles -= angle_offset(r_coordinates.flatten()).reshape(photon_arrival_angles.shape)

            # Calculating the 1D histogram for the spatial counts and the 2D histogram for the arrival times and arrival angles
            spatial_counts += np.histogram(r_coordinates.flatten(), r_bins, weights=photons_on_plane.flatten())[0]
            time_counts += np.histogram2d(r_coordinates.flatten(), total_propagation_times.flatten(), bins=(r_bins, time_bins), weights=photons_on_plane.flatten())[0]
            angle_counts += np.histogram2d(r_coordinates.flatten(), photon_arrival_angles.flatten(), bins=(r_bins, angle_bins), weights=photons_on_plane.flatten())[0]

            del r_coordinates, total_propagation_times, photon_arrival_angles, photons_on_plane
            progress.advance(task)
    io_func.flog("[bold blue]Shower 1 done! :heavy_check_mark:")

    # Plotting Wavelength, Angular, Time, and Spatial Distributions of the arriving Cherenkov photons
    if plot.Plot[plots] > 0:
        wl = plot.plot_wavelength_distribution(wavelengths, X_integrated_photons)
        ph_as = plot.plot_photon_angular_spread(r_bins, angle_bins, angle_counts)
        ph_ts = plot.plot_photon_time_spread(r_bins, time_bins, time_counts)
        ph_3d_sd = plot.plot_3D_spatial_distribution(r_bins, det_array)
        if save_fig:
            wl.savefig(plot.plot_out_dir + "wavelen_dist.png")
            ph_as.savefig(plot.plot_out_dir +"ph_angular_spread.png")
            ph_ts.savefig(plot.plot_out_dir +"ph_time_spread.png")
            ph_3d_sd.savefig(plot.plot_out_dir +"ph_3D_spatial_dist.png")

    # Correcting the spatial counts to account for the area of the ring (photons/m^2)
    ring_area = np.pi * ((r_bins[1:] * 1000)**2 - (r_bins[:-1] * 1000)**2)
    spatial_counts = spatial_counts / (ring_area)

    ################################################################

    cher_res = {
        "wavelengths" : wavelengths,
        "wavelength_counts" : X_integrated_photons[:-1],
        "r_bins" : r_bins,
        "r_counts" : spatial_counts,
        "time_bins" : time_bins,
        "time_counts" : time_counts,
        "lower_times" : np.array(time_bounds)[:, 0],
        "angle_bins" : angle_bins,
        "angle_counts" : angle_counts,
        "lower_angles" : np.array(zenith_bounds)[:, 0],
    }

    if plot.Plot[plots] > 0 and not save_fig:
        plt.show()

    return cher_res

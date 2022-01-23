try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

from omfit_classes.fluxSurface import rz_miller
from omfit_classes.omfit_matlab import OMFITmatlab
from omfit_classes.utils_math import atomic_element
from omas import ODS
import numpy as np

__all__ = ['OMFITcotsim']


class OMFITcotsim(OMFITmatlab):
    def to_omas(self, ods=None, time_index=None):
        if ods is None:
            ods = ODS()
        time = self['outputs']['scalars']['t']
        if time_index is None:
            time_index = range(len(time))

        # shouldn't all these be time dependent
        r, _ = np.meshgrid(self['outputs']['config']['model']['params']['r']['value'], time)
        R0 = self['outputs']['config']['model']['params']['R0']['value']
        B0 = self['outputs']['config']['model']['params']['B0']['value'] * time
        kappa, _ = np.meshgrid(self['outputs']['config']['model']['params']['kappa_prof']['value'], time)
        delta, _ = np.meshgrid(self['outputs']['config']['model']['params']['delta_prof']['value'], time)
        sshaf, _ = np.meshgrid(self['outputs']['config']['model']['params']['sshaf_prof']['value'] * 0.01, time)
        zeta = delta * 0.0
        zmag = delta * 0.0
        rmag = sshaf + R0

        for ktime_index, time_index in enumerate(tolist(time_index)):
            ods[f'core_profiles.profiles_1d.{ktime_index}.electrons.density_thermal'] = ne = self['outputs']['profiles']['ne'][
                time_index, :
            ]
            ods[f'core_profiles.profiles_1d.{ktime_index}.electrons.temperature'] = te = (
                self['outputs']['profiles']['te'][time_index, :] * 1e3
            )
            ods[f'core_profiles.profiles_1d.{ktime_index}.grid.rho_tor_norm'] = rho = self['outputs']['profiles']['rho_norm']
            for kion, ion in enumerate(['D', 'C']):
                ion_info = list(atomic_element(symbol=ion).values())[0]
                ods[f'core_profiles.profiles_1d.{ktime_index}.ion.{kion}.density_thermal'] = self['outputs']['profiles']['n' + ion][
                    time_index, :
                ]
                ods[f'core_profiles.profiles_1d.{ktime_index}.ion.{kion}.element.0.a'] = ion_info['A']
                ods[f'core_profiles.profiles_1d.{ktime_index}.ion.{kion}.element.0.atoms_n'] = 1
                ods[f'core_profiles.profiles_1d.{ktime_index}.ion.{kion}.element.0.z_n'] = ion_info['Z']
                ods[f'core_profiles.profiles_1d.{ktime_index}.ion.{kion}.label'] = ion
                ods[f'core_profiles.profiles_1d.{ktime_index}.ion.{kion}.multiple_states_flag'] = 0
                ods[f'core_profiles.profiles_1d.{ktime_index}.ion.{kion}.temperature'] = ti = (
                    self['outputs']['profiles']['ti'][time_index, :] * 1e3
                )
                ods[f'core_profiles.profiles_1d.{ktime_index}.ion.{kion}.z_ion'] = 1.0
            ods[f'core_profiles.profiles_1d.{ktime_index}.rotation_frequency_tor_sonic'] = self['outputs']['profiles']['omega'][
                time_index, :
            ]
            ods[f'core_profiles.profiles_1d.{ktime_index}.zeff'] = rho * 0.0 + 1.0
            ods.set_time_array('core_profiles.vacuum_toroidal_field.b0', ktime_index, B0[time_index])
            ods[f'core_profiles.vacuum_toroidal_field.r0'] = R0
            ods.set_time_array('core_profiles.time', ktime_index, time[time_index])

            r_boundary, z_boundary = rz_miller(
                r[time_index, -1],
                rmag[time_index, -1],
                kappa=kappa[time_index, -1],
                delta=delta[time_index, -1],
                zeta=zeta[time_index, -1],
                zmag=zmag[time_index, -1],
            )
            ods[f'equilibrium.time_slice.{ktime_index}.boundary.outline.r'] = r_boundary
            ods[f'equilibrium.time_slice.{ktime_index}.boundary.outline.z'] = z_boundary
            ods[f'equilibrium.time_slice.{ktime_index}.global_quantities.ip'] = self['outputs']['scalars']['ip'][time_index] * 1e6
            ods[f'equilibrium.time_slice.{ktime_index}.global_quantities.magnetic_axis.b_field_tor'] = (
                B0[time_index] * R0 / rmag[time_index, 0]
            )
            ods[f'equilibrium.time_slice.{ktime_index}.profiles_1d.centroid.r_max'] = rmag[time_index, :] + r[time_index, :]
            ods[f'equilibrium.time_slice.{ktime_index}.profiles_1d.centroid.r_min'] = rmag[time_index, :] - r[time_index, :]
            ods[f'equilibrium.time_slice.{ktime_index}.profiles_1d.centroid.z'] = zmag[time_index, :]
            ods[f'equilibrium.time_slice.{ktime_index}.profiles_1d.elongation'] = kappa[time_index, :]
            ods[f'equilibrium.time_slice.{ktime_index}.profiles_1d.psi'] = self['outputs']['profiles']['psi'][time_index, :]
            ods[f'equilibrium.time_slice.{ktime_index}.profiles_1d.q'] = self['outputs']['profiles']['q'][time_index, :]
            ods[f'equilibrium.time_slice.{ktime_index}.profiles_1d.rho_tor_norm'] = rho
            ods[f'equilibrium.time_slice.{ktime_index}.profiles_1d.squareness_lower_inner'] = zeta[time_index, :]
            ods[f'equilibrium.time_slice.{ktime_index}.profiles_1d.squareness_lower_outer'] = zeta[time_index, :]
            ods[f'equilibrium.time_slice.{ktime_index}.profiles_1d.squareness_upper_inner'] = zeta[time_index, :]
            ods[f'equilibrium.time_slice.{ktime_index}.profiles_1d.squareness_upper_outer'] = zeta[time_index, :]
            ods[f'equilibrium.time_slice.{ktime_index}.profiles_1d.triangularity_lower'] = delta[time_index, :]
            ods[f'equilibrium.time_slice.{ktime_index}.profiles_1d.triangularity_upper'] = delta[time_index, :]
            ods.set_time_array('equilibrium.vacuum_toroidal_field.b0', ktime_index, B0[time_index])
            ods[f'equilibrium.vacuum_toroidal_field.r0'] = R0
            ods.set_time_array('equilibrium.time', ktime_index, time[time_index])

        # calculate Zeff
        ods.physics_core_profiles_zeff()
        return ods

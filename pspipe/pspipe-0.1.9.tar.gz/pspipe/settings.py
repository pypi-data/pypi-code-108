# Handle setting
#
# Author: F. Mertens

import os

import astropy.units as u

from libpipe import futils
from libpipe.settings import BaseSettings

# Lazy loaded:
# - ps_eor.datacube in Settings.validate_vis_cube()

from . import utils


TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

TEMPLATE_NAMES = ['a12', 'nenufar', 'hba']


class Settings(BaseSettings):

    DEFAULT_SETTINGS = os.path.join(TEMPLATE_DIR, 'default_settings.toml')

    def __init__(self, file, d):
        BaseSettings.__init__(self, file, d)

    def validate_image(self, val_fct):
        val_fct(u.Unit(self.image.scale).is_equivalent((u.rad, u.s)), 'scale')
        val_fct(len(self.image.size.split()) == 2 and all(k.isdigit() for k in self.image.size.split()), 'size')
        val_fct(self.image.channels_out == 'all' or str(self.image.channels_out).startswith(
            'every') or self.image.channels_out.isdigit(), 'channels_out')
        val_fct(isinstance(self.image.umin, (int, float)), 'umin')
        val_fct(isinstance(self.image.umax, (int, float)), 'umax')
        val_fct(utils.all_in_other(set(self.image.stokes), set('IQUV')), 'stokes')
        val_fct(isinstance(self.image.split_even_odd, bool), 'split_even_odd')
        val_fct(isinstance(self.image.time_start_index, int), 'time_start_index')
        val_fct(isinstance(self.image.time_end_index, int), 'time_end_index')
        if self.image.time_end_index or self.image.time_start_index:
            val_fct(self.image.time_end_index >= self.image.time_start_index, 'time_end_index')
        val_fct(isinstance(self.image.lst_bins, list) and len(self.image.lst_bins) in [0, 3], 'lst_bins')
        val_fct(isinstance(self.image.clean_niter, (int, float)), 'clean_niter')
        val_fct(isinstance(self.image.clean_auto_threshold, (int, float)), 'clean_auto_threshold')
        val_fct(isinstance(self.image.clean_mgain, (int, float)), 'clean_mgain')
        val_fct(isinstance(self.image.clean_residual, bool), 'clean_residual')
        val_fct(isinstance(self.image.clean_spectra_fit_nterms, int), 'clean_spectra_fit_nterms')

    def validate_worker(self, val_fct):
        val_fct(isinstance(self.worker.max_concurrent, int), 'max_concurrent')
        val_fct(not self.worker.env_file or futils.is_file(self.worker.env_file), 'env_file')

    def validate_merge_ms(self, val_fct):
        val_fct(isinstance(self.merge_ms.apply_aoflagger, bool), 'apply_aoflagger')
        val_fct(isinstance(self.merge_ms.blmin, (int, float)), 'blmin')
        val_fct(isinstance(self.merge_ms.blmax, (int, float)), 'blmax')
        val_fct(isinstance(self.merge_ms.avg_timestep, int), 'avg_timestep')
        val_fct(isinstance(self.merge_ms.time_start_index, int), 'time_start_index')
        val_fct(isinstance(self.merge_ms.time_end_index, int), 'time_end_index')
        if self.merge_ms.time_end_index or self.merge_ms.time_start_index:
            val_fct(self.merge_ms.time_end_index >= self.merge_ms.time_start_index, 'time_end_index')

    def validate_vis_cube(self, val_fct):
        from ps_eor import datacube

        val_fct(isinstance(self.vis_cube.fov, (int, float, str)), 'fov')
        val_fct(isinstance(self.vis_cube.umin, (int, float)), 'umin')
        val_fct(isinstance(self.vis_cube.umax, (int, float)), 'umax')
        val_fct(len(datacube.get_window(datacube.WindowFunction.parse_winfct_str(self.vis_cube.win_fct), 3)) == 3,
                'win_fct')

    def validate_vis_to_sph(self, val_fct):
        val_fct(futils.is_file(self.vis_to_sph.pre_flag), 'pre_flag')

    def validate_combine(self, val_fct):
        val_fct(isinstance(self.combine.scale_with_noise, bool), 'scale_with_noise')
        val_fct(isinstance(self.combine.inhomogeneous, bool), 'inhomogeneous')
        val_fct(self.combine.weights_mode in ['full', 'uv', 'global'], 'weights_mode')
        val_fct(futils.is_file(self.combine.pre_flag), 'pre_flag')

    def validate_power_spectra(self, val_fct):
        val_fct(futils.is_file(self.power_spectra.eor_bin_list), 'eor_bin_list')
        val_fct(futils.is_file(self.power_spectra.ps_config), 'ps_config')
        val_fct(futils.is_file(self.power_spectra.flagger), 'flagger')

    def validate_gpr(self, val_fct):
        val_fct(futils.is_file(self.gpr.config_i), 'config_i')
        val_fct(futils.is_file(self.gpr.config_v), 'config_v')
        val_fct(isinstance(self.gpr.plot_results, bool), 'plot_results')

    def validate_ssins(self, val_fct):
        val_fct(isinstance(self.ssins.n_time_avg, list), 'n_time_avg')
        for k in ['percentage_freq_full_flag', 'percentage_time_full_flag', 'time_freq_threshold',
                  'baseline_threshold', 'snapshot_threshold']:
            val_fct(isinstance(self.ssins[k], float), k)

    def validate_delay_flagger(self, val_fct):
        for k in ['umin', 'umax', 'n_sigma_i', 'n_sigma_v']:
            val_fct(isinstance(self.delay_flagger[k], (int, float)), k)
        for k in ['n_time_avg', 'n_times']:
            val_fct(isinstance(self.delay_flagger[k], int), k)


def get_template_path(template_name):
    assert template_name in TEMPLATE_NAMES, f'template_name should be one of: {" ".join(TEMPLATE_NAMES)}'   

    return os.path.join(TEMPLATE_DIR, f'default_{template_name}.toml')

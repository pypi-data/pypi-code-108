# Direct access to the data
#
# Author: F. Mertens

import os

from ps_eor import pspec, datacube, flagger, fgfit, ml_gpr


class ObsData(object):

    def __init__(self, vis_rev, obs_id, lst_idx=None):
        self.vis_rev = vis_rev
        self.obs_id = obs_id
        self.lst_idx = lst_idx
        self.settings = self.vis_rev.settings
        self.flag = None
        self.uvrange = None
        self.nfreqs = None
        self.data = {}
        self.all_stokes = {}
        for stokes in ['I', 'Q', 'U', 'V']:
            self.all_stokes[stokes.lower()] = stokes
            self.all_stokes[stokes.lower() + '_even'] = 'even_%s' % stokes
            self.all_stokes[stokes.lower() + '_odd'] = 'odd_%s' % stokes
            self.all_stokes[stokes.lower() + '_dt'] = 'dt_%s' % stokes
        self.ps_builder = pspec.PowerSpectraBuilder(self.settings.power_spectra.get_path('ps_config'),
                                                    self.settings.power_spectra.get_path('eor_bin_list'))

    def __getattr__(self, key):
        assert key in self.all_stokes.keys()
        return self.get_stokes(self.all_stokes[key])

    def __invalid_cache(self):
        self.data = {}

    def set_flag(self, flag):
        self.flag = flag
        self.__invalid_cache()

    def filter_uvrange(self, umin, umax):
        self.uvrange = [umin, umax]
        self.__invalid_cache()

    def average_freqs(self, nfreqs):
        self.nfreqs = nfreqs
        self.__invalid_cache()

    def do_flag(self, flagger_file=None, verbose_flagging=True, plot_flagging=True):
        if flagger_file is None:
            flagger_file = self.settings.power_spectra.get_path('flagger')
        flagger_runner = flagger.FlaggerRunner.load(flagger_file)
        flagger_runner.verbose = verbose_flagging
        flagger_runner.run(self.i, self.v)
        if plot_flagging:
            flagger_runner.plot()
        self.set_flag(flagger_runner.flag)

    def get_h5_file(self, stokes):
        return self.vis_rev.get_h5_file(self.obs_id, stokes, lst_idx=self.lst_idx)

    def get_stokes(self, stokes):
        if stokes not in self.data:
            path = self.get_h5_file(stokes)
            cube = datacube.CartDataCube.load(path)
            if self.uvrange is not None:
                cube.filter_uvrange(self.uvrange[0], self.uvrange[1])
            if self.nfreqs is not None:
                cube = cube.average_freqs(self.nfreqs)
            if self.flag is not None:
                cube = self.flag.apply(cube)
            self.data[stokes] = cube
        return self.data[stokes]

    def get_gpr_res(self, eor_bin, umin=50, umax=250, stokes='I', name=''):
        path = os.path.join(os.path.dirname(self.get_h5_file(stokes)), name, f'eor{eor_bin}_u{umin}-{umax}')
        i_res = fgfit.GprForegroundResult.load(path, f'gpr_res_{stokes}')
        i_noise = datacube.CartDataCube.load(os.path.join(path, 'gpr_res_I.noise.h5'))
        i_res.noise = i_noise

        return i_res

    def get_ml_gpr_res(self, eor_bin, umin=50, umax=250, name=''):
        path = os.path.join(os.path.dirname(self.get_h5_file('I')), name, f'eor{eor_bin}_u{umin}-{umax}')
        return ml_gpr.MLGPRResult.load(path, 'ml_gpr_res_I')

    def get_ps_gen(self, **kargs):
        return self.ps_builder.get(self.i, **kargs)

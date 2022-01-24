'''
Created on 26. 2. 2014

@author: Vancikv
'''

from traits.api import \
    Float, Property, cached_property, Array, Int

import numpy as np

from .reinf_law_base import \
    ReinfLawBase

class ReinfLawPiecewiseLinear(ReinfLawBase):
    '''Effective crack bridge Law using a piecewise linear function.'''

    sig_level_arr = Array(float, input=True)
    def _sig_level_arr_default(self):
        E_eff = self.sig_tex_u / self.eps_u
        return E_eff * self.eps_arr

    sig_tex_u = Float(800.0, enter_set=True, auto_set=False, input=True)
    eps_u = Float(0.01, enter_set=True, auto_set=False, input=True)
    n_eps = Int(2, enter_set=True, auto_set=False, input=True)

    eps_fraction_arr = Property(depends_on='n_eps')
    @cached_property
    def _get_eps_fraction_arr(self):
        return np.linspace(0.0, 1.0, self.n_eps)

    cnames = ['eps_u', 'sig_level_arr']

    u0 = Property(depends_on='eps_u, sig_tex_u, eps_fraction_list')
    @cached_property
    def _get_u0(self):
        return self.sig_level_arr[1:]

    eps_arr = Array(float)
    def _eps_arr_default(self):
        return self.eps_fraction_arr * self.eps_u

    sig_arr = Array(float)
    def _sig_arr_default(self):
        return self.sig_level_arr

    def set_sig_eps_arr(self, eps_arr, sig_arr):
        self.eps_arr = eps_arr
        self.sig_arr = sig_arr

ReinfLawBase.db.constants['piecewise_linear-default'] = ReinfLawPiecewiseLinear()

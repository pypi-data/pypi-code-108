'''
Created on 26. 2. 2014

@author: Vancikv
'''

from traits.api import \
    Float, Property, cached_property

import numpy as np

from .reinf_law_base import \
    ReinfLawBase

class ReinfLawSteel(ReinfLawBase):
    f_yk = Float(500., enter_set=True, auto_set=False, input=True)
    E_s = Float(200000., enter_set=True, auto_set=False, input=True)
    eps_u = Float(0.025, enter_set=True, auto_set=False, input=True)

    eps_y = Property(Float, depends_on='+input')
    @cached_property
    def _get_eps_y(self):
        return self.f_yk / self.E_s

    eps_arr = Property(depends_on='+input')
    @cached_property
    def _get_eps_arr(self):
        return np.array([-self.eps_u, -self.eps_y, 0., self.eps_y, self.eps_u])

    sig_arr = Property(depends_on='+input')
    @cached_property
    def _get_sig_arr(self):
        return np.array([-self.f_yk, -self.f_yk, 0., self.f_yk, self.f_yk])

ReinfLawBase.db.constants['steel-default'] = ReinfLawSteel()

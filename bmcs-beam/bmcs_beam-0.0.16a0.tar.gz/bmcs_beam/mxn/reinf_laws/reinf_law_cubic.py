'''
Created on 26. 2. 2014

@author: Vancikv
'''

from traits.api import \
    Float, Property, cached_property, List

import numpy as np

from .reinf_law_base import \
    ReinfLawBase

class ReinfLawCubic(ReinfLawBase):
    '''Effective crack bridge Law using a cubic polynomial.'''

    sig_tex_u = Float(1216., enter_set=True, auto_set=False, input=True)
    eps_u = Float(0.016, enter_set=True, auto_set=False, input=True)
    var_a = Float(-5e+6, enter_set=True, auto_set=False, input=True)

    cnames = ['eps_u', 'var_a']

    u0 = List([ 0.016, -5000000. ])

    eps_arr = Property(depends_on='+input')
    @cached_property
    def _get_eps_arr(self):
        return np.linspace(0, self.eps_u, num=100.)

    sig_arr = Property(depends_on='+input')
    @cached_property
    def _get_sig_arr(self):
        # for horizontal tangent at eps_u
        sig_tex_u, var_a, eps_u = self.sig_tex_u, self.var_a, self.eps_u
        eps_arr = self.eps_arr
        var_b = -(sig_tex_u + 2. * var_a * eps_u ** 3.) / eps_u ** 2.
        var_c = -3. * var_a * eps_u ** 2. - 2. * var_b * eps_u
        sig_arr = var_a * eps_arr ** 3. + var_b * eps_arr ** 2. + var_c * eps_arr
        return sig_arr

ReinfLawBase.db.constants['cubic-default'] = ReinfLawCubic()

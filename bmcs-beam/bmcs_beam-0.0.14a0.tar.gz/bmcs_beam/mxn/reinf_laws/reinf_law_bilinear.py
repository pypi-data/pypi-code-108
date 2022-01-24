'''
Created on 26. 2. 2014

@author: Vancikv
'''

from traits.api import \
    Float, Property, cached_property, Array, Int, List

from bmcs_beam.mxn.constitutive_law import CLBase

import numpy as np

from math import exp, log

from .reinf_law_base import \
    ReinfLawBase


class ReinfLawBilinear(ReinfLawBase):

    '''Effective crack bridge Law using a cubic polynomial.'''

    sig_tex_u = Float(1216., enter_set=True, auto_set=False, input=True)
    eps_u = Float(0.014, enter_set=True, auto_set=False, input=True)
    var_a = Float(0.8, enter_set=True, auto_set=False, input=True)
    eps_el_fraction = Float(0.0001, enter_set=True, auto_set=False, input=True)

    cnames = ['eps_u', 'var_a']

    u0 = List([0.014, 0.8])

    eps_arr = Property(depends_on='+input')

    @cached_property
    def _get_eps_arr(self):
        return np.hstack([0., self.eps_el_fraction * self.eps_u, self.eps_u])

    sig_arr = Property(depends_on='+input')

    @cached_property
    def _get_sig_arr(self):
        return np.hstack([0., self.var_a * self.sig_tex_u, self.sig_tex_u])

ReinfLawBase.db.constants['bilinear-default'] = ReinfLawBilinear()

'''
Created on 26. 2. 2014

@author: Vancikv
'''

from traits.api import \
    Float, Property, cached_property, List

import numpy as np

from .reinf_law_base import \
    ReinfLawBase

class ReinfLawLinear(ReinfLawBase):
    '''Effective crack bridge Law with linear elastic response.'''

    eps_u = Float(0.01, enter_set=True, auto_set=False, input=True)
    E_tex = Float(80000, enter_set=True, auto_set=False, input=True)
    u0 = List([ 0.01, 80000. ], enter_set=True, auto_set=False)

    sig_tex_u = Property(depends_on='+input')
    @cached_property
    def _get_sig_tex_u(self):
        return self.E_tex * self.eps_u

    cnames = ['eps_u', 'E_tex']

    eps_arr = Property(depends_on='+input')
    @cached_property
    def _get_eps_arr(self):
        return np.array([ 0., self.eps_u])

    sig_arr = Property(depends_on='+input')
    @cached_property
    def _get_sig_arr(self):
        # with limit for eps_tex
        #
        return self.E_tex * self.eps_arr

ReinfLawBase.db.constants['linear-default'] = ReinfLawLinear()

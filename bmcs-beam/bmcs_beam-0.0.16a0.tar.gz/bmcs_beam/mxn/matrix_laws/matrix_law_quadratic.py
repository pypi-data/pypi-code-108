'''
Created on 26. 2. 2014

@author: Vancikv
'''

from traits.api import \
    Property, cached_property

import numpy as np

from bmcs_beam.mxn.mfn import MFnLineArray

from .matrix_law_base import \
    MatrixLawBase


class MatrixLawQuadratic(MatrixLawBase):

    '''Effective crack bridge Law using a cubic polynomial.'''

    mfn = Property(depends_on='+input')

    @cached_property
    def _get_mfn(self):
        '''quadratic stress-strain-diagram of the concrete
        '''
        # (for all concretes up to f_cm=88 N/mm2) #max epislon_c1u
        f_cm = self.f_ck + 8
        E_tan = 22. * (f_cm / 10) ** 0.3 * 1000.
        eps_c1 = min(0.7 * f_cm ** 0.31, 2.8) / 1000.  # EC2
        # @todo: with constant value this yields negative values for strains close to 'eps_c1u'
# eps_c1 = 0.0022 #Brockmann
        E_sec = f_cm / eps_c1

        if self.f_ck <= self.high_strength_level:
            eps_c1u = self.eps_c_u
            eps_arr = np.linspace(0., eps_c1u, num=100.)

        elif self.f_ck > self.high_strength_level:
            eps_c1u = (2.8 + 27. * (((98. - f_cm) / 100.) ** 4.)) / 1000.
            eps_arr = np.linspace(0., eps_c1u, num=100.)

        k = E_tan / E_sec
        sig_c_arr = ((k * eps_arr / eps_c1 - (eps_arr / eps_c1) **
                      2.) / (1. + (k - 2.) * eps_arr / eps_c1)) * f_cm

        xdata = eps_arr
        ydata = sig_c_arr

        return MFnLineArray(xdata=xdata, ydata=ydata)

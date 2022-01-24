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


class MatrixLawLinear(MatrixLawBase):

    '''Effective crack bridge Law based on fiber-bundle-model.'''
    #-----------------------------
    # for bilinear stress-strain-diagram of the concrete (EC2)
    #-----------------------------
    mfn = Property(depends_on='+input')

    @cached_property
    def _get_mfn(self):
        '''bilinear stress-strain-diagram of the concrete
        '''
        # (for standard concrete)
        f_ck = self.f_ck + 8.
        if f_ck <= self.high_strength_level:
            eps_c3 = 0.00175
            eps_cu3 = self.eps_c_u
        # (for high strength concrete)
        else:
            eps_c3 = (1.75 + 0.55 * (f_ck - 50.) / 40.) / 1000.
            eps_cu3 = self.eps_c_u
        # concrete law with limit for eps_c

        xdata = np.hstack([0., eps_c3, eps_cu3])
        ydata = np.hstack([0., (f_ck), (f_ck)])

        return MFnLineArray(xdata=xdata, ydata=ydata)

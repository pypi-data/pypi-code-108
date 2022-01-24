'''
Created on 26. 2. 2014

@author: Vancikv
'''

from traits.api import \
    Property, cached_property

import numpy as np

from bmcs_beam.mxn.mfn import MFnLineArray

import sympy as sp

from .matrix_law_base import \
    MatrixLawBase


class MatrixLawBlock(MatrixLawBase):

    '''Effective crack bridge Law with linear elastic response.'''

    #-----------------------------
    #
    # for simplified constant stress-strain-diagram of the concrete (EC2)
    #-----------------------------
    mfn = Property(depends_on='+input')

    @cached_property
    def _get_mfn(self):
        '''simplified constant stress-strain-diagram of the concrete (EC2)
        '''
        # (for standard concrete)
        f_ck = self.f_ck + 8.
        if f_ck <= 50:
            lamda = 0.8
            eta = 1.0
            eps_cu3 = self.eps_c_u
        # (for high strength concrete)
        #
        else:
            eta = 1.0 - (f_ck / 50.) / 200.
        # factor [-] to calculate the height of the compressive zone
            lamda = 0.8 - (f_ck - 50.) / 400.
            eps_cu3 = (2.6 + 35. * ((90. - f_ck) / 100) ** 4.) / 1000.

        xdata = np.hstack(
            [0., (1. - lamda) * eps_cu3 - 0.00001, (1 - lamda) * eps_cu3, eps_cu3])
        ydata = np.hstack([0., 0., eta * (f_ck), eta * (f_ck), ])

        return MFnLineArray(xdata=xdata, ydata=ydata)

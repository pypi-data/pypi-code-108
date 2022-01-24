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


class MatrixLawBilinear(MatrixLawBase):

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
        eps_c3 = self.f_ck / self.E_c
        xdata = np.array([0.0, eps_c3, self.eps_c_u])
        ydata = np.array([0.0, self.f_ck, self.f_ck])
        return MFnLineArray(xdata=xdata, ydata=ydata, extrapolate='zero')

if __name__ == '__main__':
    MatrixLawBase.db.configure_traits()

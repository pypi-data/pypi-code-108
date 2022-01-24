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

a_, b_, c_, x_ = sp.symbols('a,b,c,x')


class MatrixLawQuad(MatrixLawBase):

    '''Effective crack bridge Law using a cubic polynomial.'''

    mfn = Property(depends_on='+input')

    @cached_property
    def _get_mfn(self):
        '''quadratic stress-strain-diagram of the concrete
        '''

        quad_fn = a_ * x_ ** 2 + b_ * x_ + c_

        eq1 = quad_fn.subs(x_, 0)
        eq2 = quad_fn.subs(x_, self.eps_c_u) - self.f_ck
        eq3 = sp.diff(quad_fn, x_).subs(x_, 0) - self.E_c
        sol = sp.solve([eq1, eq2, eq3], a_, b_, c_)
        sig_eps_fn = sp.lambdify([x_], quad_fn.subs(sol))
        eps_arr = np.linspace(0., self.eps_c_u, num=100.)
        xdata = eps_arr
        ydata = sig_eps_fn(eps_arr)

        return MFnLineArray(xdata=xdata, ydata=ydata)

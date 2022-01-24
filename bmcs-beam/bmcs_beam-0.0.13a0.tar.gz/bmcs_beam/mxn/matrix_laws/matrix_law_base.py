'''
Created on Aug 23, 2012

@author: rch
'''

from bmcs_beam.mxn.constitutive_law import CLBase
from bmcs_beam.mxn.mxn_class_extension import \
    MxNClassExt
from bmcs_beam.mxn.mxn_tree_node import \
    MxNLeafNode
from traits.api import \
    Float, Property, cached_property

from bmcs_beam.mxn.matresdev.db.simdb import \
    SimDBClass, SimDBClassExt
import numpy as np



class MatrixLawBase(CLBase, MxNLeafNode, SimDBClass):

    '''Base class for concrete constitutive laws.'''
    # characteristic compressive stress [MPa]
    #
    f_ck = Float(60.0, simdb=True, enter_set=True, auto_set=False, input=True)
    eps_c_u = Float(
        0.0033, simdb=True, enter_set=True, auto_set=False, input=True)
    E_c = Float(28e+3, simdb=True, enter_set=True, auto_set=False, input=True)
    node_name = 'Constitutive law'

    high_strength_level = Float(
        50.0, simdb=True, enter_set=True, auto_set=False, input=True)

    eps_arr = Property(depends_on='+input')

    @cached_property
    def _get_eps_arr(self):
        return self.mfn.xdata

    sig_arr = Property(depends_on='+input')

    @cached_property
    def _get_sig_arr(self):
        return self.mfn.ydata

MatrixLawBase.db = MxNClassExt(
    klass=MatrixLawBase,
    verbose='io',
    node_name='Matrix law database'
)

if __name__ == '__main__':
    MatrixLawBase.db.configure_traits()

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
    List

from bmcs_beam.mxn.matresdev.db.simdb import \
    SimDBClass, SimDBClassExt


class ReinfLawBase(CLBase, MxNLeafNode, SimDBClass):
    '''Base class for Effective Crack Bridge Laws.'''

    u0 = List([0.0, 0.0])
    node_name = 'Constitutive law'

ReinfLawBase.db = MxNClassExt(
    klass=ReinfLawBase,
    verbose='io',
    node_name='Reinforcement law database'
)

if __name__ == '__main__':
    ReinfLawBase.db.configure_traits()

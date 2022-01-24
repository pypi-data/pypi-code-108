'''
Created on 1. 7. 2014

@author: Vancikv
'''
from traits.api import \
    List, Instance

from bmcs_beam.mxn.mxn_tree_node import \
    MxNTreeNode

from bmcs_beam.mxn.material_types import \
    MTMatrixMixture, MTReinfFabric, MTReinfBar

class UCDatabase(MxNTreeNode):
    node_name = 'Material database'

    tree_node_list = List(Instance(MxNTreeNode), transient=True)
    def _tree_node_list_default(self):
        return [MTMatrixMixture.db,
                      MTReinfFabric.db,
                      MTReinfBar.db]

'''
Created on 1. 7. 2014

@author: Vancikv
'''

from traits.api import \
    HasStrictTraits, List, Str, Button, \
    Trait, Instance

from traitsui.api import \
    View, Item, VGroup, HGroup, UItem, spring

from bmcs_beam.mxn.mxn_tree_node import \
    MxNTreeNode

from .use_case_parametric_study import \
    UCParametricStudy

from bmcs_beam.mxn.mxn_diagram import \
    MxNDiagram

from bmcs_beam.mxn.ecb_calib import \
    ECBCalib

from .use_case_database import \
    UCDatabase

class UseCaseContainer(MxNTreeNode):
    '''Contains MxN diagrams wrapped in MxNDescription classes.
    MxNDescription controls plotting of particular MxNDiagram
    that can added/removed or modified ,e.g. via tree editor.
    '''

    node_name = Str('Use cases')

    use_case_to_add = Trait('pstudy', {'pstudy'      :   UCParametricStudy,
                                       'calibration' :   ECBCalib,
                                       'prediction'   :   MxNDiagram}
                            )

    add_use_case = Button('Add')
    def _add_use_case_fired(self):
        self.tree_node_list.append(self.use_case_to_add_())

    tree_view = View(HGroup(UItem('use_case_to_add', springy=True),
                            UItem('add_use_case')),
                            spring)

    tree_node_list = List(Instance(MxNTreeNode))
    def _tree_node_list_default(self):
        return [UCDatabase()]

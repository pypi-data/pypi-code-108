'''
Created on 6. 4. 2014

@author: Vancikv

Standard tree view with the default database node
and added parametric study node
'''

from bmcs_beam.mxn.use_cases import \
    UseCaseContainer, UCParametricStudy
from bmcs_beam.mxn.view import \
    MxNTreeView


mxn_ps = UCParametricStudy()
mxn_ps.element_to_add = 'mxndiagram'
mxn_ps.add_element = True
mxn_ps.tree_node_list[-1].node_name = 'Study #1'
mxn_ps.add_element = True
mxn_ps.tree_node_list[-1].node_name = 'Study #2'

ucc = UseCaseContainer()
ucc.tree_node_list.append(mxn_ps)

mxn_ps_view = MxNTreeView(root=ucc)
mxn_ps_view.selected_node = mxn_ps
mxn_ps_view.replot = True
mxn_ps_view.configure_traits()

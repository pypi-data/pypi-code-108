'''
Created on 2. 4. 2014

@author: Vancikv

Standard tree view with the default database node
and added mxn_diagram node
'''
print('x12')

from bmcs_beam.mxn.use_cases import \
    UseCaseContainer
from bmcs_beam.mxn.view import \
    MxNTreeView


ucc = UseCaseContainer()
ucc.use_case_to_add = 'prediction'
ucc.add_use_case = True

uc_view = MxNTreeView(root=ucc)
uc_view.configure_traits()
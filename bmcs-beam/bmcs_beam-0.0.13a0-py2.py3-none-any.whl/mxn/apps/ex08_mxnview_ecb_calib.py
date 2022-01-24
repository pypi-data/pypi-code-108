'''
Created on 1. 4. 2014

@author: Vancikv

Standard tree view with the default database node
and added calibration node
'''

from bmcs_beam.mxn.view import \
    MxNTreeView

from bmcs_beam.mxn.use_cases import \
    UseCaseContainer

ucc = UseCaseContainer()
ucc.use_case_to_add = 'calibration'
ucc.add_use_case = True

uc_view = MxNTreeView(root=ucc)
uc_view.configure_traits()

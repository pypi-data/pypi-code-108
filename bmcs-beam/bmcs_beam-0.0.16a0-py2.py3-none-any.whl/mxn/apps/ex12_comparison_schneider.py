'''
Created on 6. 8. 2014

@author: Vancikv

In this example a parametric study of an MxN diagram of a steel_design
reinforced cross section with different reinforcement ratios is
constructed - i.e. a dimensioning diagram that can be
compared with literature, e.g. Schneider Bautabellen.

Specifications:

Geometry:  rectangle 40x40cm
Concrete:  C30/37
steel_design:     B500B
d1/h = 0.1

Reinforcement ratios: 0, 0.5, 1.0, 1.5, 2.0

As_tot = omega_tot * (b * h) / (f_yd / f_cd)
As1 = As_tot / 2    (Reinforcement on one side for certain omega)

For omega_tot = 0.5:
As1 = 1.0 * (0.4 * 0.4) / (435 / 17) / 2 = 15.640e-4 m^2
'''
from bmcs_beam.mxn import \
    CrossSection, MxNDiagram

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoRect

from bmcs_beam.mxn.reinf_layout import \
    RLCBar

from bmcs_beam.mxn.matrix_laws import \
    MatrixLawBlock

from bmcs_beam.mxn.reinf_laws import \
    ReinfLawSteel

from bmcs_beam.mxn.material_types import \
    MTMatrixMixture, MTReinfBar

from bmcs_beam.mxn.view import \
    MxNTreeView

from bmcs_beam.mxn.use_cases import \
    UseCaseContainer, UCParametricStudy

if MTMatrixMixture.db.get('ex12_C30-37', None):
    del MTMatrixMixture.db['ex12_C30-37']
MTMatrixMixture.db['ex12_C30-37'] = MTMatrixMixture(f_ck=9.,
                                                eps_c_u=0.0035,
                                                mtrl_laws={'constant':
                                                            MatrixLawBlock(f_ck=9.,
                                                                           eps_c_u=0.0035,
                                                                           E_c=33e+3),
                                         })

if MTReinfBar.db.get('ex12_bar', None):
    del MTReinfBar.db['ex12_bar']
MTReinfBar.db['ex12_bar'] = MTReinfBar(area=0.001564,
                                          mtrl_laws={'steel_design':
                                                    ReinfLawSteel(f_yk=500 / 1.15)
                                         })
'''Defining materials
'''

ge = MCSGeoRect(height=0.4, width=0.4)
mcs = MatrixCrossSection(geo=MCSGeoRect(height=0.4, width=0.4),
                         n_cj=20,
                         material='ex12_C30-37',
                         material_law='constant')
'''Geometry, matrix
'''

cs00 = CrossSection(reinf=[],
                    matrix_cs=MatrixCrossSection(
                         geo=MCSGeoRect(height=0.4, width=0.4),
                         n_cj=20,
                         material='ex12_C30-37',
                         material_law='constant')
                    )
cs05 = CrossSection(reinf=[RLCBar(x=0.2, z=0.36,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.2, z=0.04,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           ],
                    matrix_cs=MatrixCrossSection(
                         geo=MCSGeoRect(height=0.4, width=0.4),
                         n_cj=20,
                         material='ex12_C30-37',
                         material_law='constant')
                    )
cs10 = CrossSection(reinf=[RLCBar(x=0.1, z=0.36,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.1, z=0.04,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.3, z=0.36,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.3, z=0.04,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           ],
                    matrix_cs=MatrixCrossSection(
                         geo=MCSGeoRect(height=0.4, width=0.4),
                         n_cj=20,
                         material='ex12_C30-37',
                         material_law='constant')
                    )
cs15 = CrossSection(reinf=[RLCBar(x=0.1, z=0.36,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.1, z=0.04,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.2, z=0.36,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.2, z=0.04,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.3, z=0.36,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.3, z=0.04,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           ],
                    matrix_cs=MatrixCrossSection(
                         geo=MCSGeoRect(height=0.4, width=0.4),
                         n_cj=20,
                         material='ex12_C30-37',
                         material_law='constant')
                    )
cs20 = CrossSection(reinf=[RLCBar(x=0.05, z=0.36,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.05, z=0.04,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.15, z=0.36,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.15, z=0.04,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.25, z=0.36,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.25, z=0.04,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.35, z=0.36,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           RLCBar(x=0.35, z=0.04,
                                  material='ex12_bar',
                                  material_law='steel_design'),
                           ],
                    matrix_cs=MatrixCrossSection(
                         geo=MCSGeoRect(height=0.4, width=0.4),
                         n_cj=20,
                         material='ex12_C30-37',
                         material_law='constant')
                    )
'''Defining cross sections with different reinforcement ratios
'''

mxn_ps = UCParametricStudy()
mxn_ps.element_to_add = 'mxndiagram'
mxn_ps.add_element = True
mxn_ps.tree_node_list[-1].node_name = 'omega = 0.0'
mxn_ps.tree_node_list[-1].color = 'blue'
mxn_ps.tree_node_list[-1].content = MxNDiagram(cs=cs00, n_eps=40)
mxn_ps.add_element = True
mxn_ps.tree_node_list[-1].node_name = 'omega = 0.5'
mxn_ps.tree_node_list[-1].linestyle = 'dashed'
mxn_ps.tree_node_list[-1].content = MxNDiagram(cs=cs05, n_eps=40)
mxn_ps.add_element = True
mxn_ps.tree_node_list[-1].node_name = 'omega = 1.0'
mxn_ps.tree_node_list[-1].linestyle = 'dash_dot'
mxn_ps.tree_node_list[-1].content = MxNDiagram(cs=cs10, n_eps=40)
mxn_ps.add_element = True
mxn_ps.tree_node_list[-1].node_name = 'omega = 1.5'
mxn_ps.tree_node_list[-1].linestyle = 'dotted'
mxn_ps.tree_node_list[-1].content = MxNDiagram(cs=cs15, n_eps=40)
mxn_ps.add_element = True
mxn_ps.tree_node_list[-1].node_name = 'omega = 2.0'
mxn_ps.tree_node_list[-1].content = MxNDiagram(cs=cs20, n_eps=40)
'''Defining a parametric study object and feeding it MxN diagrams
with the designated cross sections
'''

ucc = UseCaseContainer()
ucc.tree_node_list.append(mxn_ps)

mxn_ps_view = MxNTreeView(root=ucc)
mxn_ps_view.configure_traits()

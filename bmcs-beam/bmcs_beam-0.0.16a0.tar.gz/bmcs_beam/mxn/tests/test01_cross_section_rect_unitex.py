'''
Created on Nov 21, 2013

@author: rch
'''

from bmcs_beam.mxn.cross_section import \
    CrossSection

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoRect

from bmcs_beam.mxn.reinf_layout import \
    RLCTexUniform

import numpy as np

def test_cross_section_mn():
    '''Test the moment and normal force calculated for a cross section.
    '''
    cp = CrossSection(reinf=[RLCTexUniform(n_layers=3, material='default_fabric', material_law='fbm')],
                         matrix_cs=MatrixCrossSection(geo=MCSGeoRect(width=0.1, height=0.05),
                                                      n_cj=20, material_law='constant', material='default_mixture'),
                         eps_lo=0.014,
                         eps_up=-0.0033,
                         )

    cp.reinf_components_with_state[0].material_law_.set(sig_tex_u=1216., eps_u=0.014, m=0.5)
    cp.reinf_components_with_state[0].material_.set(s_0=0.00416, A_roving=0.461)

    assert np.allclose([cp.M, cp.N], [1.14513592334, -22.1303533699])
    cp.reinf[0].n_layers = 5

    assert np.allclose([cp.M, cp.N], [1.29225385264, -6.60917224146])
    cp.eps_lo = 0.010

    assert np.allclose([cp.M, cp.N], [1.52939155655, -28.4691640432])

if __name__ == '__main__':
    test_cross_section_mn()

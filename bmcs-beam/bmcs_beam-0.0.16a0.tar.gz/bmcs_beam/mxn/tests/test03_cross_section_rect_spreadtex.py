'''
Created on 15. 2. 2014

@author: Vancikv
'''

from bmcs_beam.mxn.cross_section import \
    CrossSection

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoRect

from bmcs_beam.mxn.reinf_layout import \
    RLCTexLayer

import numpy as np

def test_cross_section_mn():
    '''Test the moment and normal force calculated for a cross section.
    Rectangular cross section with spread textile reinforcement.
    '''

    tl1 = RLCTexLayer(z_coord=0.1, material='default_fabric', material_law='fbm')
    tl2 = RLCTexLayer(z_coord=0.05, material='default_fabric', material_law='fbm')
    ge = MCSGeoRect(height=0.5, width=0.3)
    cs = CrossSection(reinf=[tl1, tl2],
                         matrix_cs=MatrixCrossSection(geo=ge,
                                        n_cj=20, material='default_mixture',
                                        material_law='constant'),
                         eps_lo=0.008,
                         eps_up=-0.0033,
                         )

    tl1.material_law_.set(sig_tex_u=1216., eps_u=0.014, m=0.5)
    tl1.material_.set(s_0=0.018, A_roving=0.461)

    assert np.allclose([cs.M, cs.N], [433.45620169134492, -2247.2883277004325])
    tl1.z_coord = 0.4
    assert np.allclose([cs.M, cs.N], [432.39449649331749, -2254.3663623539496])
    ge.width = 0.15
    assert np.allclose([cs.M, cs.N], [216.14717747037844, -1127.4335350583763])
    cs.eps_lo = 0.014
    assert np.allclose([cs.M, cs.N], [156.7097970367976, -734.53214309844532])

if __name__ == '__main__':
    test_cross_section_mn()

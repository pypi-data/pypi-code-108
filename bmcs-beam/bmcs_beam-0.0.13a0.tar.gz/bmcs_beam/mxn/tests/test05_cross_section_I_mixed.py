'''
Created on 15. 2. 2014

@author: Vancikv
'''

from bmcs_beam.mxn.cross_section import \
    CrossSection

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoRect, MCSGeoI

from bmcs_beam.mxn.reinf_layout import \
    RLCBar, RLCTexLayer

import numpy as np

def test_cross_section_mn():
    '''Test the moment and normal force calculated for a cross section.
    I - shaped cross section with mixed reinforcement. Change of geometry
    to rectangular also tested.
    '''
    ge = MCSGeoI(height=0.4, height_up=0.05, width_up=0.25, height_lo=0.05, width_lo=0.35, width_st=0.05)
    mcs = MatrixCrossSection(geo=ge, n_cj=20, material='default_mixture',
                             material_law='constant')
    '''Cross section geometry + matrix
    '''

    bar1 = RLCBar(x=0.025, z=0.025, material='bar_d10')
    bar2 = RLCBar(x=0.125, z=0.025, material='bar_d10')
    bar3 = RLCBar(x=0.225, z=0.025, material='bar_d10')
    bar4 = RLCBar(x=0.325, z=0.025, material='bar_d10')
    bar1.material_.area = 0.00005
    '''Four steel reinforcement bars in lower flange
    '''

    tl1 = RLCTexLayer(z_coord=0.01, material='default_fabric', material_law='fbm')
    tl2 = RLCTexLayer(z_coord=0.39, material='default_fabric', material_law='fbm')
    '''Two layers of textile reinforcement
    '''

    cs = CrossSection(reinf=[tl1, tl2, bar1, bar2, bar3, bar4],
                             matrix_cs=mcs,
                             eps_lo=0.002,
                             eps_up=-0.0033,
                             )

    tl1.material_law_.set(sig_tex_u=1216., eps_u=0.014, m=0.5)
    tl1.material_.set(s_0=0.02, A_roving=0.461)

    assert np.allclose([cs.M, cs.N], [201.35521782599423, -1152.7647363907902])
    bar1.material_.area = 0.0004
    assert np.allclose([cs.M, cs.N], [274.03855115932754, -685.51473639079018])
    ge.height_lo = 0.06
    assert np.allclose([cs.M, cs.N], [279.41793763239417, -685.51473639079018])
    cs.eps_lo = 0.004
    assert np.allclose([cs.M, cs.N], [324.31926663193633, -323.07965392270125])
    mcs.geo = MCSGeoRect(height=0.4, width=0.4)
    assert np.allclose([cs.M, cs.N], [613.20118671511852, -2927.1270652809549])

if __name__ == '__main__':
    test_cross_section_mn()

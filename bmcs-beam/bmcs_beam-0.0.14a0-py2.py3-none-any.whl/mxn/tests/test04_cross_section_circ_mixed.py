'''
Created on 15. 2. 2014

@author: Vancikv
'''

from bmcs_beam.mxn.cross_section import \
    CrossSection

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoCirc

from bmcs_beam.mxn.reinf_layout import \
    RLCBar, RLCTexLayer

import numpy as np

def test_cross_section_mn():
    '''Test the moment and normal force calculated for a cross section.
    Circular cross section with mixed reinforcement.
    '''

    radius = 0.3
    ge = MCSGeoCirc(radius=0.3)
    '''Cross section geometry
    '''

    n_bars = 10
    radius_bars = 0.26
    bar_area = 0.0002
    '''Specifications of bar reinforcement
    '''

    fi_bar_arr = np.arange(0, 2 * np.pi, 2 * np.pi / n_bars, dtype=float)
    x_bar_arr = np.cos(fi_bar_arr) * radius_bars + radius
    z_bar_arr = radius - np.sin(fi_bar_arr) * radius_bars
    '''Positions of bars divided equally across the circumference
    '''

    bar_lst = []
    '''List of bars
    '''
    for i in range(n_bars):
        bar_lst.append(RLCBar(x=x_bar_arr[i], z=z_bar_arr[i], material='bar_d10'))
    bar_lst[0].material_.area = bar_area

    tl1 = RLCTexLayer(z_coord=0.15, material='default_fabric', material_law='fbm')
    tl2 = RLCTexLayer(z_coord=0.16, material='default_fabric', material_law='fbm')
    '''Two layers of textile reinforcement
    '''

    cs = CrossSection(reinf=[tl1, tl2] + bar_lst,
                             matrix_cs=MatrixCrossSection(geo=ge,
                                         n_cj=20, material='default_mixture',
                                         material_law='constant'),
                             eps_lo=0.002,
                             eps_up=-0.0033,
                             )

    tl1.material_law_.set(sig_tex_u=1216., eps_u=0.014, m=0.5)
    tl1.material_.set(s_0=0.0247, A_roving=0.5)

    assert np.allclose([cs.M, cs.N], [1236.3684520623658, -9300.9390846971837])
    bar_lst[0].material_.area = 0.0004
    assert np.allclose([cs.M, cs.N], [1349.182793672938, -9534.1983257666307])
    ge.radius = 0.33
    assert np.allclose([cs.M, cs.N], [1702.868895888816, -11299.173023898555])
    cs.eps_lo = 0.004
    assert np.allclose([cs.M, cs.N], [1626.2468647131818, -6796.3926837363797])

if __name__ == '__main__':
    test_cross_section_mn()

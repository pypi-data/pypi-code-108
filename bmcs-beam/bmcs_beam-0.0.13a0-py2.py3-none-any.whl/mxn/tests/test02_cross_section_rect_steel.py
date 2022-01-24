'''
Created on 15. 2. 2014

@author: Vancikv
'''

from bmcs_beam.mxn.cross_section import \
    CrossSection

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoRect

from bmcs_beam.mxn.reinf_layout import \
    RLCBar

import numpy as np

import pickle

from bmcs_beam.mxn.utils import \
    get_outfile

def test_cross_section_mn():
    '''Test the moment and normal force calculated for a cross section.
    Rectangular cross section with steel reinforcement.
    '''

    bar = RLCBar(x=0.1, z=0.05, material='bar_d10')
    bar.material_.area = 0.0002

    ge = MCSGeoRect(height=0.5, width=0.3)
    cs = CrossSection(reinf=[bar],
                         matrix_cs=MatrixCrossSection(geo=ge,
                                        n_cj=20, material='default_mixture',
                                        material_law='constant'),
                         eps_lo=0.002,
                         eps_up=-0.0033,
                         )

    cs_file = get_outfile(folder_name='.mxn',
                          file_name='test02_cs.pkl')
    assert np.allclose([cs.M, cs.N], [605.63085424909093, -4763.6924315440474])
    pickle.dump(cs, open(cs_file, 'wb'), 1)

    bar.x = 0.15
    bar.z = 0.15
    assert np.allclose([cs.M, cs.N], [595.51085561046102, -4806.0924290168105])
    cs.eps_lo = 0.010
    assert np.allclose([cs.M, cs.N], [393.29047407596528, -1821.7451022853184])

#     loaded_cs = pickle.load(open(cs_file, 'rb'))
#     assert np.allclose([loaded_cs.M, loaded_cs.N], [605.63085424909093, -4763.6924315440474])

if __name__ == '__main__':
    test_cross_section_mn()

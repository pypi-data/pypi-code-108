'''
Created on 26. 2. 2014

@author: Vancikv
'''

from bmcs_beam.mxn.cross_section import \
    CrossSection

from bmcs_beam.mxn.ecb_calib import \
    ECBCalib

from bmcs_beam.mxn.mxn_diagram import \
    MxNDiagram

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoRect

from bmcs_beam.mxn.reinf_layout import \
    RLCTexUniform

import numpy as np

def test_mxn_diagram():
    '''Test the mxn diagram with calibrated crack bridge law.
    '''
    rf = RLCTexUniform(n_layers=12, material='default_fabric', material_law='fbm')
    rf.material_.set(s_0=0.0083, A_roving=0.461)
    rf.material_law_.set(sig_tex_u=1216., eps_u=0.014, m=0.5)

    mx = MatrixCrossSection(geo=MCSGeoRect(width=0.2, \
            height=0.06), n_cj=20, material='default_mixture', material_law='quadratic')
    cs1 = CrossSection(reinf=[rf], matrix_cs=mx)

    c = ECBCalib(Mu=3.49, cs=cs1)
    c.calibrated_ecb_law

    mn = MxNDiagram(cs=cs1, n_eps=5)
    print(mn.MN_arr)
    assert np.allclose(mn.MN_arr, [[  7.10542736e-15, 2.22660238e-01, 1.03819266e+00,
         2.20471968e+00, 3.59406948e+00, 3.59406948e+00,
         5.43778492e+00, 4.74839849e+00, 4.06147239e+00,
         3.49000000e+00, 3.49000000e+00, 2.73072947e+00,
         1.72273968e+00, 8.62726963e-01, 4.15992690e-01,
         4.15992690e-01, 1.60772876e-01, 5.44687855e-02,
         1.09018095e-02, 0.00000000e+00],
        [ -7.61878943e+02, -7.48682299e+02, -6.97670624e+02,
        - 6.21117984e+02, -5.26283708e+02, -5.26283708e+02,
        - 2.26595623e+02, -1.06001638e+02, -4.07893660e+01,
         6.04401862e-10, 6.04401862e-10, 3.60075811e+01,
         7.83184927e+01, 1.12335890e+02, 1.30252734e+02,
         1.30252734e+02, 1.44651518e+02, 1.51158633e+02,
         1.53981001e+02, 1.54718976e+02]])

if __name__ == '__main__':
    test_mxn_diagram()

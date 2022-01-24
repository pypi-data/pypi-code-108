'''
Created on Nov 21, 2013

@author: rch
'''

from bmcs_beam.mxn.cross_section import \
    CrossSection

from bmcs_beam.mxn.ecb_calib import \
    ECBCalib

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoRect

from bmcs_beam.mxn.reinf_layout import \
    RLCTexUniform

import numpy as np

import pickle

from bmcs_beam.mxn.utils import \
    get_outfile

def test_ecb_law_calib():
    '''Test the calibrated crack bridge law.
    '''
    #===============================================================================
    # Input values
    #===============================================================================
    # 23 rovings
    n_rovings = 23
    # roving cross sectional area
    A_rov = 0.461
    # ultimate moment
    Mu = 3.50

    ge = MCSGeoRect(height=0.06, width=0.2)
    mcs = MatrixCrossSection(geo=ge, n_cj=20, material='default_mixture', material_law='constant')

    uni_layers = RLCTexUniform(n_layers=12, material='default_fabric', material_law='fbm')

    uni_layers.material_.set(s_0=0.0083, A_roving=0.461)

    cs = CrossSection(matrix_cs=mcs, reinf=[uni_layers])

    calib = ECBCalib(cs=cs, Mu=Mu)
    test_eps_arr = np.linspace(0.0, 0.005, 10)
    calib_file = get_outfile(folder_name='.mxn',
                             file_name='test06_calib.pkl')

    assert np.allclose(calib.calibrated_ecb_law.mfn_vct(test_eps_arr),
                       np.array([0., 169.56745719, 308.0713995, 426.15150252,
                                 528.22368093, 617.57902395, 696.18106351,
                                 765.44225452, 826.76851637, 881.07603382],
                                dtype=float))

    assert np.allclose(cs.reinf_components_with_state[0].layer_lst[0].material_law_.mfn_vct(test_eps_arr),
                       np.array([0., 169.56745719, 308.0713995, 426.15150252,
                                 528.22368093, 617.57902395, 696.18106351,
                                 765.44225452, 826.76851637, 881.07603382],
                                dtype=float))
    pickle.dump(calib, open(calib_file, 'wb'), 1)

    uni_layers.material_law = 'cubic'

    assert np.allclose(calib.calibrated_ecb_law.mfn_vct(test_eps_arr),
                       np.array([0., 128.33734405, 247.41169038, 357.44885771,
                                 458.78005031, 551.89774542, 636.94074038,
                                 714.45215726, 784.72942118, 848.06386907],
                                dtype=float))

    uni_layers.material_law = 'linear'

    assert np.allclose(calib.calibrated_ecb_law.mfn_vct(test_eps_arr),
                       np.array([0., 51.40222925, 102.8044585, 154.20668775,
                                 205.608917, 257.01114625, 308.41337551,
                                 359.81560476, 411.21783401, 462.62006326],
                                dtype=float))

    uni_layers.material_law = 'bilinear'

    assert np.allclose(calib.calibrated_ecb_law.mfn_vct(test_eps_arr),
                       np.array([0., 858.01243898, 873.058472, 888.10450501,
                                 903.15053803, 918.19657105, 933.24260407,
                                 948.28863708, 963.3346701, 978.38070312],
                                dtype=float))

    mcs.material_law = 'quadratic'
    uni_layers.material_law = 'fbm'
    calib.Mu = 3.49

    assert np.allclose(calib.calibrated_ecb_law.mfn_vct(test_eps_arr),
                       np.array([0., 300.73451126, 489.25642137, 628.66800959,
                                 737.65269075, 825.20174306, 896.67226786,
                                 955.78175683, 1004.84170587, 1045.86868703],
                                dtype=float))

    loaded_calib = pickle.load(open(calib_file, 'rb'))

    assert np.allclose(loaded_calib.calibrated_ecb_law.mfn_vct(test_eps_arr),
                       np.array([0., 169.56745719, 308.0713995, 426.15150252,
                                 528.22368093, 617.57902395, 696.18106351,
                                 765.44225452, 826.76851637, 881.07603382],
                                dtype=float))

if __name__ == '__main__':
    test_ecb_law_calib()

'''
Created on 22. 4. 2014

@author: Vancikv
'''

from bmcs_beam.mxn.cross_section import \
    CrossSection

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoRect

from bmcs_beam.mxn.reinf_layout import \
    RLCTexUniform

from bmcs_beam.mxn.material_types import \
    MTReinfFabric

from bmcs_beam.mxn.reinf_laws import \
    ReinfLawFBM, ReinfLawLinear

import numpy as np

import pickle

from bmcs_beam.mxn.utils import \
    get_outfile

if MTReinfFabric.db.get('fabric-test', None):
    del MTReinfFabric.db['fabric-test']
MTReinfFabric.db['fabric-test'] = MTReinfFabric(A_roving=0.461,
                                                s_0=0.0083,
                                                s_90=0.02,
                                                mtrl_laws=
                                                {'fbm':
                                                ReinfLawFBM(sig_tex_u=1000.,
                                                            eps_u=0.014,
                                                            m=0.5),
                                                'linear':
                                                ReinfLawLinear(eps_u=0.014,
                                                                E_tex=65000.),
                                                }
                                                )

def test_reinf_fabric_states():
    '''Test the moment and normal force calculated for a cross section
    with changing reinforcement law.
    '''
    cp = CrossSection(reinf=[RLCTexUniform(n_layers=6, material='default_fabric', material_law='cubic')],
                         matrix_cs=MatrixCrossSection(geo=MCSGeoRect(width=0.1, height=0.05),
                                                      n_cj=20, material_law='constant',
                                                      material='default_mixture'),
                         eps_lo=0.014,
                         eps_up=-0.0033,
                         )

    MTReinfFabric.db['default_fabric'].mtrl_laws['cubic'].set(sig_tex_u=1216., eps_u=0.016, var_a=-5e+6)
    MTReinfFabric.db['default_fabric'].set(s_0=0.0083, A_roving=0.461)
    MTReinfFabric.db['default_fabric'].mtrl_laws['fbm'].set(sig_tex_u=1216., eps_u=0.014, m=0.5)

    assert np.allclose([cp.M, cp.N], [1.186453793394266, -30.616264285738165])
    cp.reinf_components_with_state[0].material_law = 'fbm'
    assert np.allclose([cp.M, cp.N], [1.1864949677288525, -24.578077501696075])
    cp.reinf_components_with_state[0].material = 'fabric-test'

    object_file = get_outfile(folder_name='.mxn',
                             file_name='test08_reinf_fabric.pkl')
    pickle.dump(cp, open(object_file, 'wb'), 1)
    assert np.allclose([cp.M, cp.N], [1.1604352105840721, -28.960062926594549])
    MTReinfFabric.db['fabric-test'].A_roving = 0.6
    assert np.allclose([cp.M, cp.N], [1.1968125127766132, -22.843167549587157])
    MTReinfFabric.db['fabric-test'].s_0 = 0.004
    assert np.allclose([cp.M, cp.N], [1.3823867162441215, 8.3614001029031542])
    MTReinfFabric.db['fabric-test'].mtrl_laws['fbm'].sig_tex_u = 1200.
    assert np.allclose([cp.M, cp.N], [1.4509064221398169, 19.883086620745736])
    cp.reinf_components_with_state[0].material_law = 'linear'
    assert np.allclose([cp.M, cp.N], [1.3150963500309509, -18.425889629166878])

    loaded_cp = pickle.load(open(object_file, 'rb'))
    assert np.allclose([loaded_cp.M, loaded_cp.N], [1.4509064221398169, 19.883086620745736])
    MTReinfFabric.db['fabric-test'].mtrl_laws['fbm'].sig_tex_u = 1000.
    assert np.allclose([loaded_cp.M, loaded_cp.N], [1.3823867162441215, 8.3614001029031542])
    loaded_cp.reinf_components_with_state[0].material_law = 'linear'
    assert np.allclose([loaded_cp.M, loaded_cp.N], [1.3150963500309509, -18.425889629166878])

if __name__ == '__main__':
    test_reinf_fabric_states()

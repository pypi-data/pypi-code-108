import numpy as np
import pytest

from dkist_processing_pac import Data
from dkist_processing_pac.DKISTDC.data import DCDrawer


def test_dresser(general_cs):
    cs_step_obj_dict = general_cs[0]
    D1 = DCDrawer(cs_step_obj_dict, skip_darks=False, remove_I_trend=False)
    D2 = DCDrawer(cs_step_obj_dict, skip_darks=True, remove_I_trend=False)
    DRSR = Data.Dresser()
    DRSR.add_drawer(D1)
    DRSR.add_drawer(D2)

    assert DRSR.nummod == 3
    assert DRSR.numsteps == 7 + 7 - 2
    np.testing.assert_array_equal(DRSR.pol_in,
                                  [False, False, True, True, True, False, False] + [False, True, True, True, False])
    np.testing.assert_array_equal(DRSR.theta_pol_steps,
                                  [0.0, 0.0, 60.0, 60.0, 120.0, 0.0, 0.0] + [0.0, 60.0, 60.0, 120.0, 0.0])
    np.testing.assert_array_equal(DRSR.ret_in,
                                  [False, False, False, True, False, False, False] + [False, False, True, False, False])
    np.testing.assert_array_equal(DRSR.theta_ret_steps,
                                  [0.0, 0.0, 0.0, 45.0, 0.0, 0.0, 0.0] + [0.0, 0.0, 45.0, 0.0, 0.0])
    np.testing.assert_array_equal(DRSR.dark_in,
                                  [True, False, False, False, False, False, True] + [False, False, False, False, False])
    assert DRSR.shape == (3, 4, 1)
    cc1 = np.ones((3, 7)) * np.arange(7)[None, :] + 100 * np.arange(3)[:, None]
    cc2 = np.ones((3, 5)) * np.arange(1, 6)[None, :] + 100 * np.arange(3)[:, None]
    cc = np.hstack([cc1, cc2])
    for i in range(np.prod(DRSR.shape)):
        np.testing.assert_array_equal(DRSR[np.unravel_index(i, DRSR.shape)][0], cc)

    # Test that uncertainty is correctly computed
    I1 = D1[0, 0, 0]
    I2 = D2[0, 0, 0]
    I, u = DRSR[0, 0, 0]
    np.testing.assert_array_equal(u, np.hstack((D1.get_uncertainty(I1), D2.get_uncertainty(I2))))

def test_wrong_modnum(general_cs):
    DRSR = Data.Dresser()
    DRSR.nummod = 99
    with pytest.raises(ValueError):
        DRSR.add_drawer(DCDrawer(general_cs[0]))

def test_wrong_wave(general_cs):
    DRSR = Data.Dresser()
    DRSR.wavelength = 999
    with pytest.raises(ValueError):
        DRSR.add_drawer(DCDrawer(general_cs[0]))

def test_wrong_instrument(general_cs):
    DRSR = Data.Dresser()
    DRSR.instrument = 'NOTHING'
    with pytest.raises(ValueError):
        DRSR.add_drawer(DCDrawer(general_cs[0]))

def test_wrong_shape(general_cs):
    DRSR = Data.Dresser()
    DRSR.shape = (99,)
    with pytest.raises(ValueError):
        DRSR.add_drawer(DCDrawer(general_cs[0]))

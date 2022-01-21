import unittest

import numpy as np

from magnumapi.matpro.critical_currents import calc_jc_nbti_bottura, calc_jc_nb3sn_bordini, calc_jc_nb3sn_summers, \
    calc_jc_nb3sn_summers_orig
from tests.resource_files import create_resources_path


class Test_critical_currents(unittest.TestCase):
    def test_calc_jc_nbti_bottura(self):
        # arrange
        T_0 = 1.9
        T = np.linspace(T_0, 8, 100)

        # act
        jc_nbti_bottura = calc_jc_nbti_bottura(T, B=1.0)

        # assert
        path = create_resources_path('resources/matpro/critical_currents/jc_nbti_bottura.txt')
        jc_nbti_bottura_ref = np.loadtxt(path)
        np.testing.assert_allclose(jc_nbti_bottura_ref, jc_nbti_bottura)

    def test_calc_jc_nb3sn_bordini(self):
        # arrange
        T_0 = 1.9
        T = np.linspace(T_0, 8, 100)

        # act
        jc_nb3sn_bordini = calc_jc_nb3sn_bordini(T, B=1.0)

        # assert
        path = create_resources_path('resources/matpro/critical_currents/jc_nb3sn_bordini.txt')
        jc_nb3sn_bordini_ref = np.loadtxt(path)
        np.testing.assert_allclose(jc_nb3sn_bordini_ref, jc_nb3sn_bordini)

    def test_calc_jc_nb3sn_summers(self):
        # arrange
        T_0 = 1.9
        T = np.linspace(T_0, 8, 100)

        # act
        jc_nb3sn_summers = calc_jc_nb3sn_summers(T, B=1.0)

        # assert
        path = create_resources_path('resources/matpro/critical_currents/jc_nb3sn_summers.txt')
        jc_nb3sn_summers_ref = np.loadtxt(path)
        np.testing.assert_allclose(jc_nb3sn_summers_ref, jc_nb3sn_summers)

    def test_calc_jc_nb3sn_summers_orig(self):
        # arrange
        T_0 = 1.9
        T = np.linspace(T_0, 8, 100)

        # act
        jc_nb3sn_summers_orig = calc_jc_nb3sn_summers_orig(T, B=1.0)

        # assert
        path = create_resources_path('resources/matpro/critical_currents/jc_nb3sn_summers_orig.txt')
        jc_nb3sn_summers_orig_ref = np.loadtxt(path)
        np.testing.assert_allclose(jc_nb3sn_summers_orig_ref, jc_nb3sn_summers_orig)

if __name__ == '__main__':
    unittest.main()

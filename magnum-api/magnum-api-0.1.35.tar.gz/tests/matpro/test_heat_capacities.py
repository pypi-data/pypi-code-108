import unittest

import numpy as np

from magnumapi.matpro.heat_capacities import calc_cv_cu_nist, calc_cv_nb3sn_nist
from tests.resource_files import create_resources_path


class Test_heat_capacities(unittest.TestCase):
    def test_calc_cv_cu_nist(self):
        # arrange
        T_0 = 1.9
        T = np.linspace(T_0, 300, 100)

        # act
        cv_cu_nist = calc_cv_cu_nist(T)

        # assert
        path = create_resources_path('resources/matpro/heat_capacities/cv_cu_nist.txt')
        cv_cu_nist_ref = np.loadtxt(path)
        np.testing.assert_allclose(cv_cu_nist_ref, cv_cu_nist)

    def test_calc_cv_nb3sn_nist(self):
        # arrange
        T_0 = 1.9
        T = np.linspace(T_0, 300, 100)

        # act
        cv_nb3sn_nist = calc_cv_nb3sn_nist(T, B=5.0)

        # assert
        path = create_resources_path('resources/matpro/heat_capacities/cv_nb3sn_nist.txt')
        cv_nb3sn_nist_ref = np.loadtxt(path)
        np.testing.assert_allclose(cv_nb3sn_nist_ref, cv_nb3sn_nist)


if __name__ == '__main__':
    unittest.main()


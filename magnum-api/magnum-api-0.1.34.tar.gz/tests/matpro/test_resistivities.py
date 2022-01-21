import unittest

import numpy as np

from magnumapi.matpro.resistivities import calc_rho_cu_nist
from tests.resource_files import create_resources_path


class Test_heat_capacities(unittest.TestCase):
    def test_calc_rho_cu_nist(self):
        # arrange
        T_0 = 1.9
        T = np.linspace(T_0, 300, 100)

        # act
        rho_cu_nist = calc_rho_cu_nist(T, B=5, RRR=100)

        # assert
        path = create_resources_path('resources/matpro/resistivities/rho_cu_nist.txt')
        rho_cu_nist_ref = np.loadtxt(path)
        np.testing.assert_allclose(rho_cu_nist_ref, rho_cu_nist)


if __name__ == '__main__':
    unittest.main()


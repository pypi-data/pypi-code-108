"""
A test module for the _sigma_points module.
"""
# Third-party imports
import unittest
from mockito import when
import numpy as np

# Local imports
from veroku.factors import _sigma_points
import veroku.factors.gaussian as gauss


class TestSigmaPoints(unittest.TestCase):
    """
    A test class for the _sigma_points module.
    """

    def setUp(self):
        """
        Run before every test.
        """
        np.random.seed(1)
        self.sps_a_cov = np.array([[4.0, 1.0, 0.5], [1.0, 3.3, 0.1], [0.5, 0.1, 6.5]])
        self.sps_a_mean = np.array([[4.0], [5.0], [8.0]])
        self.sps_a_array = np.array(
            [
                [
                    0.25834261322605867,
                    4.0000000000000000,
                    4.0000000000000000,
                    4.0000000000000000,
                    7.741657386773941,
                    4.000000000000000,
                    4.0000000000000000,
                ],
                [
                    4.06458565330651500,
                    1.7327381494590917,
                    5.0000000000000000,
                    5.0000000000000000,
                    5.935414346693485,
                    8.267261850540908,
                    5.0000000000000000,
                ],
                [
                    7.53229282665325700,
                    8.0267808348405000,
                    3.2533661625436867,
                    8.0000000000000000,
                    8.467707173346742,
                    7.973219165159501,
                    12.746633837456313,
                ],
            ]
        )

    def test_get_sigma_points_array(self):
        """
        Test that the computed sigma points are correct.
        """
        g_1 = gauss.make_random_gaussian(var_names=["a", "b", "c"])
        expected_cov = g_1.get_cov()
        expected_mean = g_1.get_mean()
        sps = _sigma_points.get_sigma_points_array(g_1)
        actual_mean = np.expand_dims(np.mean(sps, axis=1), axis=1)
        actual_cov = np.cov(sps, bias=True)

        self.assertTrue(np.allclose(expected_cov, actual_cov))
        self.assertTrue(np.allclose(expected_mean, actual_mean))

    def test_sigma_point_array_to_gaussian_params(self):
        """
        Test that the sigma_point_array_to_gaussian_params returns the correct result.
        """
        expected_cov = self.sps_a_cov
        expected_mean = self.sps_a_mean
        sps_array = self.sps_a_array
        actual_cov, actual_mean = _sigma_points.sigma_point_array_to_gaussian_params(sps_array)

        self.assertTrue(np.allclose(expected_cov, actual_cov))
        self.assertTrue(np.allclose(expected_mean, actual_mean))

    def test_sigma_points_to_gaussian_params(self):
        """
        Test that the sigma_points_to_gaussian_params returns the correct result.
        """
        expected_cov = self.sps_a_cov
        expected_mean = self.sps_a_mean
        sps = [np.expand_dims(self.sps_a_array[:, i], axis=1) for i in range(self.sps_a_array.shape[1])]
        # TODO: make this more specific by checking the actual numpy array.
        when(_sigma_points).sigma_point_array_to_gaussian_params(...).thenReturn(
            (self.sps_a_cov, self.sps_a_mean)
        )
        actual_cov, actual_mean = _sigma_points.sigma_points_to_gaussian_params(sps)

        self.assertTrue(np.allclose(expected_cov, actual_cov))
        self.assertTrue(np.allclose(expected_mean, actual_mean))

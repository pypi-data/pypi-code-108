"""
Test module for the factor_utils module.
"""

# Standard imports
import unittest

# Third-party imports
import numpy as np

# Local imports
from veroku.factors.experimental.factorised_factor import FactorizedFactor
from veroku.factors.gaussian import Gaussian


def get_gaussian_set_a():
    """
    A helper function for generating a set of Gaussians for tests.
    """
    g_1 = Gaussian(mean=[[1.0], [2.0]], cov=[[5.0, 0.0], [0.0, 4.0]], log_weight=0.0, var_names=["a", "b"])
    g_2 = Gaussian(mean=[[3.0], [5.0]], cov=[[1.0, 0.0], [0.0, 2.0]], log_weight=0.0, var_names=["b", "c"])
    g_3 = Gaussian(mean=[[0.0], [3.0]], cov=[[3.0, 0.0], [0.0, 4.0]], log_weight=0.0, var_names=["d", "e"])
    return g_1, g_2, g_3


class TestFactorisedFactor(unittest.TestCase):
    """
    A class for testing the FactorisedFactor class.
    """

    def setUp(self):
        """
        Run before each test.
        """
        self.gab = Gaussian(cov=[[3, 1], [1, 2]], mean=[1, 2], log_weight=0.0, var_names=["a", "b"])
        self.gcd = Gaussian(cov=[[3, 2], [2, 4]], mean=[3, 4], log_weight=0.0, var_names=["c", "d"])
        self.gef = Gaussian(cov=[[8, 3], [3, 6]], mean=[5, 6], log_weight=0.0, var_names=["e", "f"])

        self.gab2 = Gaussian(cov=[[4, 1], [1, 2]], mean=[1, 2], log_weight=0.0, var_names=["a", "b"])
        self.gbc2 = Gaussian(cov=[[8, 1], [1, 8]], mean=[7, 10], log_weight=0.0, var_names=["b", "c"])

        self.gab3 = Gaussian(prec=[[5, 1], [1, 2]], h_vec=[1, 2], g_val=0.0, var_names=["a", "b"])
        self.ga3 = Gaussian(prec=[[1]], h_vec=[1], g_val=0.0, var_names=["a"])

    def test_multiply_independent(self):
        """
        Test that the joint distribution has been correctly calculated.
        """
        expected_cov = [
            [3, 1, 0, 0, 0, 0],
            [1, 2, 0, 0, 0, 0],
            [0, 0, 3, 2, 0, 0],
            [0, 0, 2, 4, 0, 0],
            [0, 0, 0, 0, 8, 3],
            [0, 0, 0, 0, 3, 6],
        ]
        expected_mean = [[1.0], [2.0], [3.0], [4.0], [5.0], [6.0]]
        expected_joint = Gaussian(
            cov=expected_cov, mean=expected_mean, log_weight=0.0, var_names=["a", "b", "c", "d", "e", "f"]
        )
        actual_joint_ff = FactorizedFactor([self.gab])
        actual_joint_ff = actual_joint_ff.multiply(self.gcd)
        actual_joint_ff = actual_joint_ff.multiply(self.gef)
        actual_joint_distribution = actual_joint_ff.joint_distribution
        self.assertEqual(len(actual_joint_ff.factors), 3)
        self.assertTrue(actual_joint_distribution.equals(expected_joint))

    def test_multiply_dependent(self):
        """
        Test that the joint distribution has been correctly calculated.
        """
        expected_cov = [[3.9, 0.8, 0.1], [0.8, 1.6, 0.2], [0.1, 0.2, 7.9]]
        expected_mean = [[1.5], [3.0], [9.5]]
        expected_log_weight = -3.32023108
        expected_joint = Gaussian(
            cov=expected_cov, mean=expected_mean, log_weight=expected_log_weight, var_names=["a", "b", "c"]
        )
        actual_joint_ff = FactorizedFactor([self.gab2])
        actual_joint_ff = actual_joint_ff.multiply(self.gbc2)
        self.assertEqual(len(actual_joint_ff.factors), 2)
        actual_joint_distribution = actual_joint_ff.joint_distribution
        self.assertTrue(actual_joint_distribution.equals(expected_joint))

    def test_multiply_same_scope(self):
        """
        Test that the joint distribution has been correctly calculated.
        """

        expected_prec = [[0.68571429, -0.34285714], [-0.34285714, 1.17142857]]
        expected_h = [[0.0], [2.0]]
        expected_g = -7.453428163563398

        expected_joint = Gaussian(prec=expected_prec, h_vec=expected_h, g_val=expected_g, var_names=["a", "b"])
        actual_joint_ff = FactorizedFactor([self.gab])
        actual_joint_ff = actual_joint_ff.multiply(self.gab2)
        self.assertEqual(len(actual_joint_ff.factors), 1)
        actual_joint_distribution = actual_joint_ff.joint_distribution
        self.assertTrue(actual_joint_distribution.equals(expected_joint))

    def test_multiply_subset_scope(self):
        """
        Test that the joint distribution has been correctly calculated.
        """
        expected_prec = [[6.0, 1.0], [1.0, 2.0]]
        expected_h = [[2.0], [2.0]]
        expected_g = 0.0

        expected_joint = Gaussian(prec=expected_prec, h_vec=expected_h, g_val=expected_g, var_names=["a", "b"])
        actual_joint_ff = FactorizedFactor([self.gab3])
        actual_joint_ff = actual_joint_ff.multiply(self.ga3)
        self.assertEqual(len(actual_joint_ff.factors), 1)
        actual_joint_distribution = actual_joint_ff.joint_distribution
        self.assertTrue(actual_joint_distribution.equals(expected_joint))

    def test_cancel_absorbed(self):
        """
        Test that the joint distribution has been correctly calculated.
        """
        actual_joint_ff = FactorizedFactor([self.gab])
        actual_joint_ff = actual_joint_ff.multiply(self.gcd)
        actual_joint_ff = actual_joint_ff.divide(self.gcd)
        self.assertEqual(len(actual_joint_ff.factors), 1)
        actual_joint_distribution = actual_joint_ff.joint_distribution
        self.assertTrue(actual_joint_distribution.equals(self.gab))

    def test_marginalise(self):
        """
        Test that the factorised factor is correctly marginalised.
        """
        g_1_vars = ["a", "b"]
        g_2_vars = ["c", "d"]
        g_1_mean = np.zeros([2, 1])
        g_1_cov = np.eye(2)
        g_2_log_weight = 0.1
        g_1 = Gaussian(mean=g_1_mean, cov=g_1_cov, log_weight=0.0, var_names=g_1_vars)
        g_2 = Gaussian(mean=np.zeros([2, 1]), cov=np.eye(2), log_weight=g_2_log_weight, var_names=g_2_vars)
        ff_joint = FactorizedFactor([g_1, g_2])
        actual_marginal = ff_joint.marginalize(g_1_vars, keep=True)
        expected_marginal_comp = Gaussian(
            mean=g_1_mean, cov=g_1_cov, log_weight=g_2_log_weight, var_names=g_1_vars
        )
        expected_marginal = FactorizedFactor([expected_marginal_comp])
        self.assertTrue(expected_marginal.equals(actual_marginal))

    def test_observe(self):
        """
        Test that the observe function returns the correct result.
        """
        # Reduction 1: reduce all vars of an independent factor
        observed_values_1 = [1.0, 2.0]
        observed_vars_1 = ["d", "e"]

        g_1, g_2, g_3 = get_gaussian_set_a()

        expected_g_1 = g_1.copy()
        expected_g_1.log_weight = -3.3719970579700123
        expected_g_2 = g_2.copy()
        expected_reduced_ff_1 = FactorizedFactor([expected_g_1, expected_g_2])

        f_factor = FactorizedFactor([g_1, g_2, g_3])
        actual_reduced_ff_1 = f_factor.observe(vrs=observed_vars_1, values=observed_values_1)
        self.assertTrue(expected_reduced_ff_1.equals(actual_reduced_ff_1))

    def test_observe2(self):
        """
        Test that the observe function returns the correct result.
        """
        # Reduction 2
        observed_values_1 = [1.0, 2.0]
        observed_vars_1 = ["b", "e"]

        g_2_reduced_vars = ["a", "c", "d"]
        g_2_reduced_cov = np.array([[5.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 3.0]])
        g_2_reduced_mean = np.array([[1.0], [5.0], [0.0]])
        g_2_reduced_log_weight = -6.39311
        expected_g_2_reduced_comp = Gaussian(
            cov=g_2_reduced_cov,
            mean=g_2_reduced_mean,
            log_weight=g_2_reduced_log_weight,
            var_names=g_2_reduced_vars,
        )
        g_1, g_2, g_3 = get_gaussian_set_a()
        expected_reduced_ff_2 = FactorizedFactor([expected_g_2_reduced_comp])
        f_factor = FactorizedFactor([g_1, g_2, g_3])
        actual_reduced_ff_2 = f_factor.reduce(vrs=observed_vars_1, values=observed_values_1)
        self.assertTrue(expected_reduced_ff_2.equals(actual_reduced_ff_2))

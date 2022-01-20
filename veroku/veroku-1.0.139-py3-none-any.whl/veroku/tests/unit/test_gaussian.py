"""
Tests for the Gaussian module.
"""

# Standard imports
import unittest
from unittest.mock import patch
import cmath

# Third-party imports
from mockito import when, expect, unstub, verifyNoUnwantedInteractions
import numpy as np
from scipy import integrate
import seaborn as sns

# Local imports
from veroku.factors.gaussian import Gaussian, make_random_gaussian, make_std_gaussian, GaussianTemplate
from veroku.factors.categorical import Categorical
from veroku.factors import _factor_utils


# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=no-self-use


def _update_canform():
    """
    A dummy _update_canform function.
    """
    return


class TestGaussian(unittest.TestCase):  # pylint: disable=protected-access
    """
    A tests class for the Gaussian class.
    """

    def setUp(self):
        """
        Run before every test.
        """
        np.random.seed(0)

    def test_init(self):
        """
        Test that the Gaussian init function does not fail.
        """
        Gaussian(mean=[2, 2], cov=[[2, 1], [1, 6]], log_weight=0.0, var_names=['a', 'b'])

    def test_random_gaussians_differ(self):
        """
        Test that random Gaussians generated sequentially are different.
        """
        var_names = ["a", "b"]
        random_gaussian_0 = make_random_gaussian(var_names)
        random_gaussian_1 = make_random_gaussian(var_names)
        self.assertEqual(random_gaussian_0.var_names, var_names)
        self.assertFalse(random_gaussian_0.equals(random_gaussian_1))

    def test_random_gaussians_same(self):
        """
        Test that random Gaussians generated sequentially with the same random seed are the same.
        """
        var_names = ["a", "b"]
        np.random.seed(0)
        random_gaussian_0 = make_random_gaussian(var_names)
        np.random.seed(0)
        random_gaussian_1 = make_random_gaussian(var_names)
        self.assertTrue(random_gaussian_0.equals(random_gaussian_1))

    def test_make_std_gaussian(self):
        """
        Test that the make_std_gaussian function returns a standard Gaussian.
        """
        var_names = ["a", "b"]
        std_gaussian = make_std_gaussian(var_names=var_names)
        self.assertTrue(np.array_equal(std_gaussian.get_cov(), np.eye(len(var_names))))
        self.assertTrue(np.array_equal(std_gaussian.get_mean(), np.zeros([len(var_names), 1])))
        self.assertEqual(std_gaussian.get_weight(), 1.0)

    def test_constructor_insufficient_parameters(self):
        """
        Test that the constructor raises an exception when insufficient parameters are supplied
        """
        # no var_names
        with self.assertRaises(Exception):
            Gaussian()
        # incomplete covariance form parameters
        with self.assertRaises(ValueError):
            Gaussian(cov=5, var_names=["a"])
        # incomplete canonical form parameters
        with self.assertRaises(ValueError):
            Gaussian(prec=5, var_names=["a"])

    def test_constructor_variable_fail(self):
        """
        Test that the constructor raises a value error when the variables are not unique.
        """
        with self.assertRaises(ValueError):
            Gaussian(cov=[[1, 0], [0, 1]], mean=[1, 1], log_weight=0.0, var_names=["a", "a"])

    def test_covariance_form_constructor(self):
        """
        Test that the constructor constructs an object with the correct covariance parameters.
        """
        cov_mat_list = [[5.0, 1.0], [1.0, 5.0]]
        cov_mat_array = np.array(cov_mat_list)
        mean_vec_list = [[2.0], [4.0]]
        mean_vec_array = np.array(mean_vec_list)
        when(_factor_utils).make_square_matrix(cov_mat_list).thenReturn(cov_mat_array)
        when(_factor_utils).make_column_vector(mean_vec_list).thenReturn(mean_vec_array)

        gaussian_a = Gaussian(cov=cov_mat_list, mean=mean_vec_list, log_weight=0.0, var_names=["a", "b"])
        self.assertEqual(gaussian_a.var_names, ["a", "b"])
        self.assertTrue(np.array_equal(gaussian_a.cov, cov_mat_array))
        self.assertTrue(np.array_equal(gaussian_a.mean, mean_vec_array))
        self.assertEqual(gaussian_a.log_weight, 0.0)
        self.assertEqual(gaussian_a.prec, None)
        self.assertEqual(gaussian_a.h_vec, None)
        self.assertEqual(gaussian_a.g_val, None)
        unstub()

    def test_canonical_form_constructor(self):
        """
        Test that the constructor constructs an object with the correct coninical parameters
        """
        prec_mat_list = [[5.0, 1.0], [1.0, 5.0]]
        prec_mat_array = np.array(prec_mat_list)
        h_vec_list = [[2.0], [4.0]]
        h_vec_array = np.array(h_vec_list)
        when(_factor_utils).make_square_matrix(prec_mat_list).thenReturn(prec_mat_array)
        when(_factor_utils).make_column_vector(h_vec_list).thenReturn(h_vec_array)

        gaussian_a = Gaussian(prec=prec_mat_list, h_vec=h_vec_list, g_val=0.0, var_names=["a", "b"])
        self.assertEqual(gaussian_a.var_names, ["a", "b"])
        self.assertTrue(np.array_equal(gaussian_a.prec, prec_mat_array))
        self.assertTrue(np.array_equal(gaussian_a.h_vec, h_vec_array))
        self.assertEqual(gaussian_a.g_val, 0.0)
        self.assertEqual(gaussian_a.cov, None)
        self.assertEqual(gaussian_a.mean, None)
        self.assertEqual(gaussian_a.log_weight, None)
        unstub()

    def test_get_cov(self):
        """
        Test that the correct covariance is returned.
        """
        gaussian_a = Gaussian(cov=2.0, mean=1.0, log_weight=0.0, var_names=["a"])
        self.assertTrue(np.array_equal(gaussian_a.get_cov(), np.array([[2.0]])))

    @staticmethod
    def test_get_cov_from_canform():
        """
        Test that the _update_covform function is called before returning the covariance parameter.
        """
        gaussian_a = Gaussian(prec=2.0, h_vec=1.0, g_val=0.0, var_names=["a"])
        expect(Gaussian, times=1)._update_covform()
        gaussian_a.get_cov()
        verifyNoUnwantedInteractions()
        unstub()

    def test_get_mean(self):
        """
        Test that the correct mean is returned.
        """
        gaussian_a = Gaussian(cov=2.0, mean=1.0, log_weight=0.0, var_names=["a"])
        self.assertTrue(np.array_equal(gaussian_a.get_mean(), np.array([[1.0]])))

    @staticmethod
    def test_get_mean_from_canform():
        """
        Test that the _update_covform function is called before returning the mean parameter.
        """
        gaussian_a = Gaussian(prec=2.0, h_vec=1.0, g_val=0.0, var_names=["a"])
        expect(Gaussian, times=1)._update_covform()
        gaussian_a.get_mean()
        verifyNoUnwantedInteractions()
        unstub()

    def test_get_log_weight(self):
        """
        Test that the correct log-weight is returned.
        """
        gaussian_a = Gaussian(cov=2.0, mean=1.0, log_weight=0.0, var_names=["a"])
        self.assertEqual(gaussian_a.get_log_weight(), 0.0)

    @staticmethod
    def test_get_log_weight_from_canform():
        """
        Test that the _update_covform function is called before returning the log-weight parameter.
        """
        gaussian_a = Gaussian(prec=2.0, h_vec=1.0, g_val=0.0, var_names=["a"])
        expect(Gaussian, times=1)._update_covform()
        gaussian_a.get_log_weight()
        verifyNoUnwantedInteractions()
        unstub()

    def test_get_prec(self):
        """
        Test that the correct K is returned.
        """
        gaussian_a = Gaussian(prec=2.0, h_vec=1.0, g_val=0.0, var_names=["a"])
        self.assertTrue(np.array_equal(gaussian_a.get_prec(), np.array([[2.0]])))

    @staticmethod
    def test_get_prec_from_covform():
        """
        Test that the _update_canform function is called before returning the K parameter.
        """
        gaussian_a = Gaussian(cov=2.0, mean=1.0, log_weight=0.0, var_names=["a"])
        expect(Gaussian, times=1)._update_canform()
        gaussian_a.get_prec()
        verifyNoUnwantedInteractions()
        unstub()

    def test_impossible_update_canform(self):
        """
        Test that the _update_canform raises a LinAlgError when the covariance matrix is not invertible.
        """
        gaussian = Gaussian(cov=np.zeros([2, 2]), mean=[0.0, 0.0], log_weight=0.0, var_names=["a", "b"])
        with self.assertRaises(np.linalg.LinAlgError):
            gaussian._update_canform()

    def test_impossible_update_covform(self):
        """
        Test that the _update_covform raises a LinAlgError when the precision matrix is not invertible.
        """
        gaussian = Gaussian(prec=np.zeros([2, 2]), h_vec=[0.0, 0.0], g_val=0.0, var_names=["a", "b"])
        with self.assertRaises(Exception):
            gaussian._update_covform()

    def test_get_h(self):
        """
        Test that the correct h is returned.
        """
        gaussian_a = Gaussian(prec=2.0, h_vec=1.0, g_val=0.0, var_names=["a"])
        self.assertTrue(np.array_equal(gaussian_a.get_h(), np.array([[1.0]])))

    @staticmethod
    def test_get_h_from_covform():
        """
        Test that the _update_canform function is called before returning the h parameter.
        """
        gaussian_a = Gaussian(cov=2.0, mean=1.0, log_weight=0.0, var_names=["a"])

        expect(Gaussian, times=1)._update_canform()

        gaussian_a.get_h()
        verifyNoUnwantedInteractions()
        unstub()

    def test_get_g(self):
        """
        Test that the correct g is returned.
        """
        gaussian_a = Gaussian(prec=2.0, h_vec=1.0, g_val=0.0, var_names=["a"])
        self.assertEqual(gaussian_a.get_g(), 0.0)

    @staticmethod
    def test_get_g_from_covform():
        """
        Test that the _update_canform function is called before returning the g parameter.
        """
        gaussian_a = Gaussian(cov=2.0, mean=1.0, log_weight=0.0, var_names=["a"])
        expect(Gaussian, times=1)._update_canform()
        gaussian_a.get_g()
        verifyNoUnwantedInteractions()
        unstub()

    def test_multiply_1d(self):
        """
        Test that the Gaussian multiplication function returns the correct result for one dimensional Gaussians.
        """
        gaussian_a = Gaussian(prec=5.0, h_vec=4.0, g_val=3.0, var_names=["a"])
        gaussian_b = Gaussian(prec=3.0, h_vec=2.0, g_val=1.0, var_names=["a"])
        expected_product = Gaussian(prec=8.0, h_vec=6.0, g_val=4.0, var_names=["a"])
        actual_product = gaussian_a.multiply(gaussian_b)
        self.assertTrue(expected_product.equals(actual_product))

    def test_cancel_1d(self):
        """
        Test that the Gaussian division function returns the correct result for one dimensional Gaussians.
        """
        gaussian_a = Gaussian(prec=6.0, h_vec=4.0, g_val=2.0, var_names=["a"])
        gaussian_b = Gaussian(prec=3.0, h_vec=2.0, g_val=1.0, var_names=["a"])
        expected_quotient = Gaussian(prec=3.0, h_vec=2.0, g_val=1.0, var_names=["a"])
        actual_quotient = gaussian_a.divide(gaussian_b)
        self.assertTrue(expected_quotient.equals(actual_quotient))

    def test_multiply_2d(self):
        """
        Test that the Gaussian multiplication function returns the correct result for two dimensional Gaussians.
        """
        gaussian_a = Gaussian(prec=[[5.0, 2.0], [2.0, 6.0]], h_vec=[1.0, 2.0], g_val=3.0, var_names=["a", "b"])
        gaussian_b = Gaussian(prec=[[4.0, 1.0], [1.0, 4.0]], h_vec=[2.0, 3.0], g_val=2.0, var_names=["a", "b"])
        expected_product = Gaussian(prec=[[9.0, 3.0], [3.0, 10.0]], h_vec=[3.0, 5.0], g_val=5.0, var_names=["a", "b"])
        actual_product = gaussian_a.multiply(gaussian_b)
        self.assertTrue(expected_product.equals(actual_product))

    def test_cancel_2d(self):
        """
        Test that the Gaussian division function returns the correct result for two dimensional Gaussians.
        """
        gaussian_a = Gaussian(prec=[[7.0, 2.0], [2.0, 6.0]], h_vec=[4.0, 3.0], g_val=3.0, var_names=["a", "b"])
        gaussian_b = Gaussian(prec=[[4.0, 1.0], [1.0, 4.0]], h_vec=[1.0, 2.0], g_val=2.0, var_names=["a", "b"])

        expected_quotient = Gaussian(prec=[[3.0, 1.0], [1.0, 2.0]], h_vec=[3.0, 1.0], g_val=1.0, var_names=["a", "b"])
        actual_quotient = gaussian_a.divide(gaussian_b)
        self.assertTrue(expected_quotient.equals(actual_quotient))

        gaussian_a_reordered = Gaussian(prec=[[6.0, 2.0], [2.0, 7.0]], h_vec=[3.0, 4.0], g_val=3.0,
                                        var_names=["b", "a"])
        actual_quotient = gaussian_a_reordered.divide(gaussian_b)

        actual_quotient._reorder_parameters(["a", "b"])

        self.assertTrue(expected_quotient.equals(actual_quotient))

    def test_observe(self):
        """
        Test that the Gaussian reduce function returns the correct result.
        """
        # Note these equations where written independently from the actuall implementation.
        # TODO: consider extending this test and hard-coding the expected parameters

        kmat = np.array([[6, 2, 1], [2, 8, 3], [1, 3, 9]])
        hvec = np.array([[1], [2], [3]])
        g_val = 1.5

        z_observed = np.array([[6]])

        expected_prec = np.array([[6, 2], [2, 8]])
        expeted_h = np.array([[-5], [-16]])
        expected_g = -142.5
        expected_gaussian = Gaussian(prec=expected_prec, h_vec=expeted_h, g_val=expected_g, var_names=["x", "y"])
        gaussian = Gaussian(prec=kmat, h_vec=hvec, g_val=g_val, var_names=["x", "y", "z"])
        actual_gaussian = gaussian.reduce(vrs=["z"], values=z_observed)
        self.assertTrue(actual_gaussian.equals(expected_gaussian))

        # Test that the result is still correct with a different parameter order.

        gaussian_copy = gaussian.copy()
        gaussian_copy._reorder_parameters(["x", "z", "y"])

        actual_gaussian = gaussian_copy.reduce(vrs=["z"], values=z_observed)
        self.assertTrue(actual_gaussian.equals(expected_gaussian))

    def test_reorder_parameters(self):
        """
        Test that _reorder_parameters properly reorders the values in the canonical parameters.
        """
        gaussian_a = Gaussian(prec=[[1.0, 2.0], [2.0, 3.0]], h_vec=[1.0, 2.0], g_val=1.0, var_names=["a", "b"])
        gaussian_b = Gaussian(prec=[[3.0, 2.0], [2.0, 1.0]], h_vec=[2.0, 1.0], g_val=1.0, var_names=["b", "a"])

        gaussian_b._reorder_parameters(["a", "b"])

        self.assertTrue(gaussian_a.equals(gaussian_b))

        gaussian_a = Gaussian(
            cov=[[1.0, 2.0], [2.0, 3.0]], mean=[1.0, 2.0], log_weight=1.0, var_names=["a", "b"]
        )
        gaussian_b = Gaussian(
            cov=[[3.0, 2.0], [2.0, 1.0]], mean=[2.0, 1.0], log_weight=1.0, var_names=["b", "a"]
        )

        gaussian_b._reorder_parameters(["a", "b"])

        self.assertTrue(gaussian_a.equals(gaussian_b))

    def test_marginalise_2d(self):
        """
        Test that the Gaussian marginalisation function returns the correct result for a two dimensional Gaussians.
        """
        gaussian = Gaussian(
            cov=[[7.0, 2.0], [2.0, 1.0]], mean=[4.0, 1.0], log_weight=0.0, var_names=["a", "b"]
        )
        expected_result = Gaussian(cov=7.0, mean=4.0, log_weight=0.0, var_names=["a"])
        actual_result = gaussian.marginalize(vrs=["a"], keep=True)
        self.assertTrue(expected_result.equals(actual_result))

    def test_marginalise_2d_canform(self):
        """
        Test that the Gaussian marginalisation function returns the correct result for a two dimensional Gaussians.
        """
        gaussian = Gaussian(
            cov=[[7.0, 2.0], [2.0, 1.0]], mean=[4.0, 1.0], log_weight=0.0, var_names=["a", "b"]
        )
        expected_result = Gaussian(cov=7.0, mean=4.0, log_weight=0.0, var_names=["a"])
        expected_result._update_canform()
        gaussian._update_canform()
        actual_result = gaussian.marginalize(vrs=["a"], keep=True)
        self.assertTrue(expected_result.equals(actual_result))

    def test_equals(self):
        """
        Test that the equals function can identify Gaussians that differ only in their variables.
        """
        gaussian_1 = Gaussian(cov=1, mean=1, log_weight=1.0, var_names=["a"])
        gaussian_2 = Gaussian(cov=0, mean=1, log_weight=1.0, var_names=["b"])
        self.assertFalse(gaussian_1.equals(gaussian_2))

    def test_equals_different_factor(self):
        """
        Test that the equals function raises a value error when compared to a different type of factor.
        """
        gaussian_1 = Gaussian(cov=1, mean=1, log_weight=1.0, var_names=["a"])
        categorical_factor = Categorical(
            var_names=["a", "b"], probs_table={(0, 0): 0.1}, cardinalities=[2, 2]
        )
        with self.assertRaises(ValueError):
            gaussian_1.equals(categorical_factor)

    def test_equals_different_order(self):
        """
        Test that the equals function can identify identical Gaussians with different order variables.
        """
        gaussian_1 = Gaussian(cov=[[1, 0], [0, 2]], mean=[1, 2], log_weight=1.0, var_names=["a", "b"])
        gaussian_2 = Gaussian(cov=[[2, 0], [0, 1]], mean=[2, 1], log_weight=1.0, var_names=["b", "a"])

        self.assertTrue(gaussian_1.equals(gaussian_2))

    def test_covform_equals(self):
        """
        Test that the _covform_equals function returns false if any of the covariance form parameters differ.
        """
        gaussian_1 = Gaussian(cov=1, mean=1, log_weight=1.0, var_names=["a"])
        gaussian_2 = Gaussian(cov=0, mean=1, log_weight=1.0, var_names=["a"])

        # with different covariances
        self.assertFalse(gaussian_1._covform_equals(gaussian_2, rtol=0.0, atol=0.0))
        # with different means
        gaussian_2 = Gaussian(cov=1, mean=0, log_weight=1.0, var_names=["a"])
        self.assertFalse(gaussian_1._covform_equals(gaussian_2, rtol=0.0, atol=0.0))
        # with different log_weights
        gaussian_2 = Gaussian(cov=1, mean=1, log_weight=0.0, var_names=["a"])
        self.assertFalse(gaussian_1._covform_equals(gaussian_2, rtol=0.0, atol=0.0))

    def test_canform_equals(self):
        """
        Test that the _canform_equals function returns false if any of the canonical form parameters differ.
        """
        gaussian_1 = Gaussian(prec=1, h_vec=1, g_val=1.0, var_names=["a"])
        gaussian_2 = Gaussian(prec=0, h_vec=1, g_val=1.0, var_names=["a"])

        # with different precisions
        self.assertFalse(gaussian_1._canform_equals(gaussian_2, rtol=0.0, atol=0.0))
        # with different hs
        gaussian_2 = Gaussian(prec=1, h_vec=0, g_val=1.0, var_names=["a"])
        self.assertFalse(gaussian_1._canform_equals(gaussian_2, rtol=0.0, atol=0.0))
        # with different gs
        gaussian_2 = Gaussian(prec=1, h_vec=1, g_val=0.0, var_names=["a"])
        self.assertFalse(gaussian_1._canform_equals(gaussian_2, rtol=0.0, atol=0.0))

    def test_equals_covform_true(self):
        """
        Test that the equals function can identify identical and effectively identical Gaussians in covariance form.
        """
        gaussian = Gaussian(
            cov=[[7.0, 2.0], [2.0, 1.0]], mean=[4.0, 1.0], log_weight=0.0, var_names=["a", "b"]
        )
        same_gaussian = Gaussian(
            cov=[[7.0, 2.0], [2.0, 1.0]], mean=[4.0, 1.0], log_weight=0.0, var_names=["a", "b"]
        )
        self.assertTrue(gaussian.equals(same_gaussian))

        # Test approximately equals
        error = 1e-7
        effectively_same_gaussian = Gaussian(
            cov=[[7.0 + error, 2.0 + error], [2.0 + error, 1.0 + error]],
            mean=[4.0 + error, 1.0 + error],
            log_weight=0.0 + error,
            var_names=["a", "b"],
        )
        self.assertTrue(gaussian.equals(effectively_same_gaussian))

    def test_equals_canform_true(self):
        """
        Test that the equals function can identify identical and effectively identical Gaussians in covariance form.
        """
        gaussian = Gaussian(prec=[[7.0, 2.0], [2.0, 1.0]], h_vec=[4.0, 1.0], g_val=0.0, var_names=["a", "b"])
        same_gaussian = Gaussian(prec=[[7.0, 2.0], [2.0, 1.0]], h_vec=[4.0, 1.0], g_val=0.0, var_names=["a", "b"])
        self.assertTrue(gaussian.equals(same_gaussian))

        # Test approximately equals
        error = 1e-7
        effectively_same_gaussian = Gaussian(
            prec=[[7.0 + error, 2.0 + error], [2.0 + error, 1.0 + error]],
            h_vec=[4.0 + error, 1.0 + error],
            g_val=0.0 + error,
            var_names=["a", "b"],
        )
        self.assertTrue(gaussian.equals(effectively_same_gaussian))

    def test_equals_false_covform(self):
        """
        Test that the equals function can identify different Gaussians (with differences in the
        various covariance form parameters).
        """
        gaussian_a = Gaussian(
            cov=[[7.0, 2.0], [2.0, 1.0]], mean=[4.0, 1.0], log_weight=0.0, var_names=["a", "b"]
        )
        gaussian_b = Gaussian(
            cov=[[2.0, 1.0], [1.0, 2.0]], mean=[4.0, 1.0], log_weight=0.0, var_names=["a", "b"]
        )
        self.assertFalse(gaussian_a.equals(gaussian_b))

        gaussian_a = Gaussian(
            cov=[[7.0, 2.0], [2.0, 1.0]], mean=[4.0, 1.0], log_weight=0.0, var_names=["a", "b"]
        )
        gaussian_b = Gaussian(
            cov=[[7.0, 2.0], [2.0, 1.0]], mean=[0.0, 0.0], log_weight=0.0, var_names=["a", "b"]
        )
        self.assertFalse(gaussian_a.equals(gaussian_b))

        gaussian_a = Gaussian(
            cov=[[7.0, 2.0], [2.0, 1.0]], mean=[4.0, 1.0], log_weight=0.0, var_names=["a", "b"]
        )
        gaussian_b = Gaussian(
            cov=[[7.0, 2.0], [2.0, 1.0]], mean=[4.0, 1.0], log_weight=1.0, var_names=["a", "b"]
        )
        self.assertFalse(gaussian_a.equals(gaussian_b))

    def test_equals_false_canform(self):
        """
        Test that the equals function can identify different Gaussians (with differences in the
        various canonical form parameters).
        """
        gaussian_a = Gaussian(prec=[[7.0, 2.0], [2.0, 1.0]], h_vec=[4.0, 1.0], g_val=0.0, var_names=["a", "b"])
        gaussian_b = Gaussian(prec=[[2.0, 1.0], [1.0, 2.0]], h_vec=[4.0, 1.0], g_val=0.0, var_names=["a", "b"])
        self.assertFalse(gaussian_a.equals(gaussian_b))

        gaussian_a = Gaussian(prec=[[7.0, 2.0], [2.0, 1.0]], h_vec=[4.0, 1.0], g_val=0.0, var_names=["a", "b"])
        gaussian_b = Gaussian(prec=[[7.0, 2.0], [2.0, 1.0]], h_vec=[0.0, 0.0], g_val=0.0, var_names=["a", "b"])
        self.assertFalse(gaussian_a.equals(gaussian_b))

        gaussian_a = Gaussian(prec=[[7.0, 2.0], [2.0, 1.0]], h_vec=[4.0, 1.0], g_val=0.0, var_names=["a", "b"])
        gaussian_b = Gaussian(prec=[[7.0, 2.0], [2.0, 1.0]], h_vec=[4.0, 1.0], g_val=1.0, var_names=["a", "b"])
        self.assertFalse(gaussian_a.equals(gaussian_b))

    def test_copy_no_form(self):
        """
        Test that the copy function raises an exception when a Gaussian does not have either of its form updated.
        """
        gaussian_no_form = Gaussian(cov=1.0, mean=0.0, log_weight=0.0, var_names=["a"])
        gaussian_no_form.covform = False
        with self.assertRaises(Exception):
            gaussian_no_form.copy()

    def test_copy_1d_covform(self):
        """
        Test that the copy function returns a identical copy of a one dimensional Gaussian in covariance form.
        """
        gaussian = Gaussian(cov=7.0, mean=4.0, log_weight=0.0, var_names=["a"])
        self.assertTrue(gaussian.equals(gaussian.copy()))

    def test_copy_2d_covform(self):
        """
        Test that the copy function returns a identical copy of a two dimensional Gaussian in covariance form.
        """
        gaussian = Gaussian(
            cov=[[7.0, 2.0], [2.0, 1.0]], mean=[4.0, 1.0], log_weight=0.0, var_names=["a", "b"]
        )
        self.assertTrue(gaussian.equals(gaussian.copy()))

    def test_copy_1d_canform(self):
        """
        Test that the copy function returns a identical copy of a Gaussian in canonical form.
        """
        gaussian = Gaussian(prec=7.0, h_vec=4.0, g_val=0.0, var_names=["a"])
        self.assertTrue(gaussian.equals(gaussian.copy()))

    def test_copy_2d_canform(self):
        """
        Test that the copy function returns a identical copy of a Gaussian in canonical form.
        """
        gaussian = Gaussian(prec=[[7.0, 2.0], [2.0, 1.0]], h_vec=[4.0, 1.0], g_val=0.0, var_names=["a", "b"])
        self.assertTrue(gaussian.equals(gaussian.copy()))

    def test_form_conversion(self):
        """
        Test that conversion from one form to the other and back results in the same Gaussian parameters.
        """
        gaussian_ab = Gaussian(
            cov=[[7.0, 2.0], [2.0, 1.0]], mean=[4.0, 1.0], log_weight=0.0, var_names=["a", "b"]
        )
        gaussian_ab_copy = gaussian_ab.copy()

        gaussian_ab_copy._update_canform()
        gaussian_ab_copy.covform = False
        gaussian_ab_copy._update_covform()

        self.assertTrue(gaussian_ab.equals(gaussian_ab_copy))

    def test_get_complex_log_weight(self):
        """
        Test that the _get_complex_log_weight returns the correct value.
        """
        gaussian_ab = Gaussian(prec=[[-1.0, 0.0], [0.0, 1.0]], h_vec=[0.0, 0.0], g_val=0.0, var_names=["a", "b"])
        actual_complex_weight = gaussian_ab._get_complex_weight()
        expected_complex_weight = cmath.exp(0.5 * cmath.log((-1.0) * (2.0 * np.pi) ** 2))
        self.assertAlmostEqual(actual_complex_weight, expected_complex_weight)

    def test_invert(self):
        """
        Test that the _invert method returns a Gaussian with the negated parameters.
        """
        gaussian = Gaussian(prec=[[1.0, 2.0], [2.0, 3.0]], h_vec=[4.0, 5.0], g_val=6.0, var_names=["a", "b"])
        expected_inv_gaussian = Gaussian(
            prec=[[-1.0, -2.0], [-2.0, -3.0]], h_vec=[-4.0, -5.0], g_val=-6.0, var_names=["a", "b"]
        )
        actual_inv_gaussian = gaussian._invert()
        self.assertTrue(actual_inv_gaussian.equals(expected_inv_gaussian))

    def test_weight_and_integration_1d(self):
        """
        Test that the Gaussian distribution intagrates to the weight.
        """
        weight = 1.0
        gaussian = Gaussian(cov=2.0, mean=4.0, log_weight=np.log(weight), var_names=["a"])
        definite_integral, _ = integrate.quad(gaussian.potential, -100.0, 100.0)
        self.assertAlmostEqual(definite_integral, weight)

        # test another weight and with canonical form
        weight = 2.0
        gaussian = Gaussian(cov=2.0, mean=4.0, log_weight=np.log(weight), var_names=["a"])

        gaussian._update_canform()

        gaussian.covform = False
        definite_integral, _ = integrate.quad(gaussian.potential, -100.0, 100.0)
        self.assertAlmostEqual(definite_integral, weight)

    def test_log_potential_no_form(self):
        """
        Test that the log_potential function raises an exception if the Gaussian has no form.
        """
        gaussian = Gaussian(cov=1.0, mean=1.0, log_weight=np.log(1.0), var_names=["a"])
        gaussian.covform = False
        with self.assertRaises(Exception):
            gaussian.log_potential(x_val=0)

    def test_potential(self):
        """
        Check that the potential method returns the correct value.
        """
        cov = np.array([[2.0, 1.0], [1.0, 2.0]])
        mean = np.array([[4.0], [5.0]])
        gaussian = Gaussian(cov=cov, mean=mean, log_weight=np.log(1.0), var_names=["a", "b"])
        actual_max_potential = gaussian.potential(x_val=mean)
        expected_max_potential = 1.0 / np.sqrt(np.linalg.det(2 * np.pi * cov))
        self.assertEqual(actual_max_potential, expected_max_potential)

    def test_log_potential_different_forms(self):
        """
        Test that the log_potential function returns the same value, regardless of the parameter form.
        """
        gaussian = Gaussian(prec=[[7.0, 2.0], [2.0, 6.0]], h_vec=[4.0, 3.0], g_val=0.0, var_names=["a", "b"])

        x_val = [7, 3]
        vrs = ["a", "b"]
        log_pot_canform = gaussian.log_potential(x_val=x_val, vrs=vrs)
        gaussian._update_covform()
        gaussian.canform = False
        log_pot_covform = gaussian.log_potential(x_val=x_val, vrs=vrs)
        self.assertAlmostEqual(log_pot_canform, log_pot_covform, places=1)

    def test_log_potential_reordered_vars(self):
        """
        Check that the log_potential method returns the correct value, even with reordered variables.
        """
        cov = np.array([[2.0, 1.0], [1.0, 2.0]])
        mean = np.array([[4.0], [5.0]])
        gaussian = Gaussian(cov=cov, mean=mean, log_weight=np.log(1.0), var_names=["a", "b"])
        # test switched variable order
        actual_max_log_potential = gaussian.log_potential(x_val=[5.0, 4.0], vrs=["b", "a"])
        expected_max_log_potential = np.log(1.0 / np.sqrt(np.linalg.det(2 * np.pi * cov)))
        self.assertEqual(actual_max_log_potential, expected_max_log_potential)

        actual_max_log_potential = gaussian.log_potential(x_val=np.array([[5.0], [4.0]]), vrs=["b", "a"])
        self.assertEqual(actual_max_log_potential, expected_max_log_potential)

    def test_weight_and_integration_2d(self):
        """
        Test that the Gaussian distribution integrates to the weight.
        """
        weight = 1.0
        gaussian = Gaussian(
            cov=[[2.0, 1.0], [1.0, 2.0]], mean=[4.0, 5.0], log_weight=np.log(weight), var_names=["a", "b"]
        )
        definite_integral, _ = integrate.dblquad(
            lambda x1, x2: gaussian.potential([x1, x2]), -20.0, 20.0, lambda x: -20.0, lambda x: 20.0
        )
        self.assertAlmostEqual(definite_integral, weight)
        weight = 2.0
        gaussian = Gaussian(
            cov=[[3.0, 2.0], [2.0, 6.0]], mean=[-4.0, 5.0], log_weight=np.log(weight), var_names=["a", "b"]
        )
        definite_integral, _ = integrate.dblquad(
            lambda x1, x2: gaussian.potential([x1, x2]), -20.0, 20.0, lambda x: -20.0, lambda x: 20.0
        )
        self.assertAlmostEqual(definite_integral, weight)

    def test_kl_divergence_between_vacuous_factors(self):
        """
        Test that the distance between two vacuous factors is zero.
        """
        g_1 = Gaussian.make_vacuous(var_names=["a", "b"])
        g_2 = Gaussian.make_vacuous(var_names=["a", "b"])
        self.assertTrue(g_1.kl_divergence(g_2) == 0.0)

    def test_kl_divergence_vac_novac(self):
        """
        Test that the distance between a vacuous and a non-vacuous factor is infinite.
        """
        g_1 = Gaussian.make_vacuous(var_names=["a", "b"])
        g_2 = make_random_gaussian(var_names=["a", "b"])
        self.assertTrue(g_1.kl_divergence(g_2) == np.inf)
        self.assertTrue(g_2.kl_divergence(g_1) == np.inf)

    def test_kl_divergence_between_same_factors(self):
        """
        Test that the distance between two identical factors is zero.
        """
        np.random.seed(0)
        g_1 = make_random_gaussian(var_names=["a", "b"])
        g_2 = g_1.copy()
        self.assertTrue(g_1.kl_divergence(g_2) == 0.0)

    def test_kl_divergence_fails_with_different_dims(self):
        """
        Test that the kl_divergence function fails with a value error when trying to calculate the KL-divergence between
        Gaussians with different dimensionality.
        """
        g_1 = make_random_gaussian(var_names=["a", "b", "c"])
        g_2 = make_random_gaussian(var_names=["a", "b"])
        with self.assertRaises(ValueError) as raises_context:
            g_1.kl_divergence(g_2)
        error_msg = str(raises_context.exception)
        self.assertTrue("dimensionalities" in error_msg)

    def test_vacuous_equals(self):
        """
        Test that vauous gaussians are equal.
        """
        g_1 = Gaussian.make_vacuous(var_names=["a", "b"])
        g_2 = Gaussian.make_vacuous(var_names=["a", "b"])
        self.assertTrue(g_1.equals(g_2))

    def test_is_vacuous_flat_gaussian(self):
        """
        Test that the is_vacuous property function identifies a Gaussian as non-vacuous if all the precision
        matrix entries are close to zero and the matrix is invertible.
        """
        dims = 3
        var_names = [str(i) for i in range(dims)]
        prec = np.eye(dims) * 1e-9
        h_prec = np.zeros([dims, 1])
        g_val = 0.0
        gauss = Gaussian(var_names=var_names, prec=prec, h_vec=h_prec, g_val=g_val)
        self.assertFalse(gauss.is_vacuous)

    def test_is_vacuous_non_psd_precision(self):
        """
        Test that the is_vacuous property function identifies a Gaussian as vacuous if all the precision
        matrix entries are close to zero and the matrix is not invertible.
        """
        dims = 3
        var_names = [str(i) for i in range(dims)]
        prec = np.eye(dims) * 1e-9
        prec[1, 1] = 0.0
        h_vec = np.zeros([dims, 1])
        g_val = 0.0
        gauss = Gaussian(var_names=var_names, prec=prec, h_vec=h_vec, g_val=g_val)
        self.assertTrue(gauss.is_vacuous)

    def test_is_vacuous_vacuous(self):
        """
        Test that the is_vacuous property function identifies a Gaussian as vacuous if the vacuous member variable is
        set to True.
        """
        dims = 3
        var_names = [str(i) for i in range(dims)]
        prec = np.eye(dims) * 1.0
        h_vec = np.zeros([dims, 1])
        g_val = 0.0
        gauss = Gaussian(var_names=var_names, prec=prec, h_vec=h_vec, g_val=g_val)
        gauss._is_vacuous = True
        self.assertTrue(gauss.is_vacuous)

    def test_cov_not_exists(self):
        """
        Check that the _cov_exists function returns False for a Gaussian that has an undefined covariance.
        """
        gaussian = Gaussian(prec=0.0, h_vec=0.0, g_val=0.0, var_names=["a"])
        self.assertFalse(gaussian._cov_exists())

    def test_cov_exists(self):
        """
        Check that the _cov_exists function returns True for a Gaussian that has a well defined covariance.
        """
        gaussian = Gaussian(cov=1.0, mean=0.0, log_weight=0.0, var_names=["a"])
        self.assertTrue(gaussian._cov_exists())

    def test_cov_exists_precision(self):
        """
        Check that the _cov_exists function returns True for a Gaussian that has a covariance that is well defined
        through the precision.
        """
        gaussian = Gaussian(prec=1.0, h_vec=0.0, g_val=0.0, var_names=["a"])
        self.assertTrue(gaussian._cov_exists())

    def test__repr__(self):
        """
        Test that the __repr__ method returns the correct result.
        """
        gaussian = Gaussian(prec=[[1.0, 0.0], [0.0, 1.0]], h_vec=[0.0, 0.0], g_val=0.0, var_names=["a", "b"])
        expected_repr_string = (
                "vars = ['a', 'b']\nprec = \n[[1. 0.]\n [0. 1.]]\nh = \n[[0.]\n [0.]]\ng = \n0.0\n"
                + "is_vacuous: False\ncov        = \n[[1. 0.]\n [0. 1.]]"
                + "\nmean       = \n[[0.]\n [0.]]\nlog_weight = \n1.8378770664093453\n"
        )
        actual_repr_string = gaussian.__repr__()
        self.assertEqual(actual_repr_string, expected_repr_string)

    @patch.object(sns, "heatmap")
    def test_show_vis(self, sns_heatmap_mock):
        """
        Test that the show_vis method does not break.
        """
        # TODO: improve this test.
        g_1 = make_random_gaussian(var_names=["a", "b"])
        g_1.show_vis()
        sns_heatmap_mock.assert_called()

    @patch.object(Gaussian, "_get_can_repr_str")
    @patch.object(Gaussian, "_get_cov_repr_str")
    def test_show(self, _get_can_repr_str_mock, _get_cov_repr_str_mock):
        """
        Test that the correct repr functions are called when show is called.
        """
        g_1 = make_random_gaussian(['a'])
        g_1._update_canform()
        g_1.show()
        _get_can_repr_str_mock.assert_called()
        _get_can_repr_str_mock.assert_called()

    def test_plot(self):
        """
        Test that the plot method does not break.
        """
        # TODO: improve this test.
        g_1 = make_random_gaussian(var_names=["a"])
        g_1.plot()
        g_1.plot(log=True)
        g_2 = make_random_gaussian(var_names=["a", "b"])
        g_2.plot()

    @patch.object(_factor_utils, "plot_2d")
    def test_plot_2d(self, fu_plot_2d_mock):
        """
        Test that the _factor_utils plot_2d function is called
        """
        # TODO: improve this test.
        g_1 = make_random_gaussian(['a', 'b'])
        g_1._plot_2d(log=False, x_lim=[0, 1], y_lim=[0, 1])
        fu_plot_2d_mock.assert_called()
        g_1._plot_2d(log=True, x_lim=[0, 1], y_lim=[0, 1])
        fu_plot_2d_mock.assert_called()

    @patch.object(Gaussian, "_get_limits_for_2d_plot")
    def test__plot_2d_no_limits(self, g_get_limits_for_2d_plot_mock):
        """
        Test that the _factor_utils fu_get_limits_for_2d_plot_mock function is called when no x and y limits are
        provided.
        """
        g_1 = make_random_gaussian(['a', 'b'])
        g_get_limits_for_2d_plot_mock.return_value = ([0, 1], [0, 1])
        g_1._plot_2d(log=False, x_lim=None, y_lim=None)
        g_get_limits_for_2d_plot_mock.assert_called()

    def test_gaussian_template(self):
        """
        Check that the Gaussian template makes the correct factors.
        """
        prec = np.array([[1.2, 0.0], [0.1, 1.2]])
        h_vec = np.array([[0.6], [1.0]])
        parameters = {"prec": prec, "h": h_vec, "g": 0.0}
        gaussian_template = GaussianTemplate(parameters, var_templates=["a_{i}", "b_{i}"])

        actual_factor = gaussian_template.make_factor(var_names=["a", "b"])
        expected_factor = Gaussian(var_names=["a", "b"], prec=prec, h_vec=h_vec, g_val=0.0)
        self.assertTrue(actual_factor.equals(expected_factor))

        actual_factor = gaussian_template.make_factor(format_dict={"i": 2})
        expected_factor = Gaussian(var_names=["a_2", "b_2"], prec=prec, h_vec=h_vec, g_val=0.0)
        self.assertTrue(actual_factor.equals(expected_factor))

    def test_split_gaussian(self):
        """
        Test that the _split_gaussian function splits a gaussian into a mixture with three different components that has
        the same mean an variance.
        """
        g_1 = make_random_gaussian(var_names=["a"])
        gm_1 = g_1._split_gaussian()
        self.assertTrue(len(gm_1.components) == 3)
        g_1_m_projection = gm_1.moment_match_to_single_gaussian()
        self.assertTrue(g_1.equals(g_1_m_projection))

    def test_sample(self):
        """
        Test that the samples drawn from a Gaussian distribution have the correct statistics.
        """
        g_1 = make_random_gaussian(var_names=["a", "b", "c"])
        expected_cov = g_1.get_cov()
        expected_mean = g_1.get_mean()

        samples = g_1.sample(1000000)
        actual_mean = np.expand_dims(np.mean(samples, axis=1), axis=1)
        actual_cov = np.cov(samples)

        self.assertTrue(np.allclose(expected_cov, actual_cov, rtol=1.0e-3, atol=1.0e-2))
        self.assertTrue(np.allclose(expected_mean, actual_mean, rtol=1.0e-3, atol=1.0e-2))

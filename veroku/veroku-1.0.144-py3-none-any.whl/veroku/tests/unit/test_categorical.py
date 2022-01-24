"""
Tests for the SparseLogTable module.
"""

# Standard imports
import unittest
import operator
from unittest import mock

# Third-party imports
import numpy as np
import pandas as pd
import mockito
from mockito import unstub

# Local imports
from veroku.factors.categorical import Categorical, CategoricalTemplate
from veroku.factors.sparse_categorical import (
    SparseCategorical,
    _make_dense,
    _any_scope_binary_operation,
    SparseCategoricalTemplate,
)

# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=no-self-use


def make_abc_factor_1(cat_class):
    """
    A helper function to make a standard test factor.

    :param cat_class: The type of factor to make (SparseCategorical or Categorical).
    :type cat_class: class
    :return: The standard factor of the specified class
    """
    vars_a = ["a", "b", "c"]
    probs_a = {
        (0, 0, 0): np.exp(0.01),
        (0, 0, 1): np.exp(0.02),
        (0, 1, 0): np.exp(0.03),
        (0, 1, 1): np.exp(0.04),
        (1, 0, 0): np.exp(0.05),
        (1, 0, 1): np.exp(0.06),
        (1, 1, 0): np.exp(0.07),
        (1, 1, 1): np.exp(0.08),
    }
    return cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2, 2])


class TestCategorical(unittest.TestCase):
    """
    Tests for Categorical class.
    """

    def __init__(self, *args, **kwargs):
        """
        Set up some variables.
        """
        super().__init__(*args, **kwargs)
        self.cat_class = Categorical

    def setUp(self):
        """
        This runs before every test.
        """
        self.not_a_categorical_factor = mockito.mock()

    def tearDown(self):
        """
        This after every test.
        """
        unstub()

    # Categorical only
    def test_init_fails_params(self):
        """
        Test that the Categorical constructor fails when neither probs_table or log_probs_tensor is given.
        """
        if self.cat_class == Categorical:
            with self.assertRaises(ValueError):
                Categorical(
                    var_names=["a", "b"], cardinalities=[2, 2], probs_table=None, log_probs_tensor=None
                )
            log_probs_tensor = np.random.rand(2, 2)
            # test that it completes successfully when log_probs_tensor is there
            Categorical(var_names=["a", "b"], cardinalities=[2, 2], log_probs_tensor=log_probs_tensor)

    # Categorical only
    def test_init_fails_missing_cards(self):
        """
        Test that the Categorical constructor fails when the cardinalities are not given with the probs_table.
        """
        if self.cat_class == Categorical:
            with self.assertRaises(ValueError):
                Categorical(var_names=["a", "b"], cardinalities=None, probs_table={(0, 0): 1.0})
            log_probs_tensor = np.random.rand(2, 2)
            # test that it completes successfully when cardinalities are there
            Categorical(var_names=["a", "b"], cardinalities=[2, 2], log_probs_tensor=log_probs_tensor)

    def test_init_fails_cards(self):
        """
        Test that the Categorical constructor fails when the number of cardinalities dont match the number of variables.
        """
        with self.assertRaises(ValueError):
            self.cat_class(var_names=["a", "b"], cardinalities=[2, 2, 2])

    # Categorical only
    def test_init_fails_bad_index(self):
        """
        Test that the Categorical constructor fails when the probs_table contains invalid indices.
        """
        if self.cat_class == Categorical:
            with self.assertRaises(IndexError):
                Categorical(var_names=["a", "b"], cardinalities=[2, 2], probs_table={(0, 6): 0.1})

    # Categorical only
    def test_init_fails_bad_shape(self):
        """
        Test that the Categorical constructor fails when the log_probs_tensor's shape does not correspond to the number
        of variables.
        """
        if self.cat_class == Categorical:
            with self.assertRaises(ValueError):
                Categorical(
                    var_names=["a", "b"], cardinalities=[2, 2], log_probs_tensor=np.random.rand(2, 2, 2)
                )

    # Categorical only
    def test_reorder_fails_var_set(self):
        """
        Test that the reorder method fails when the set of new order variables do not match the factors variables.
        of variables.
        """
        if self.cat_class == Categorical:
            cat1 = Categorical(
                var_names=["a", "b"], cardinalities=[2, 2], log_probs_tensor=np.random.rand(2, 2)
            )
            with self.assertRaises(ValueError):
                cat1.reorder(["c", "a"])

    def test_equals_fails_wrong_factor(self):
        """
        Test that the equals method fails when the comparing to another type of factor.
        of variables.
        """
        vars_a = ["a", "b"]
        probs_a = {(0, 0): 0.1,
                   (0, 1): 0.2,
                   (1, 0): 0.3,
                   (1, 1): 0.4}
        sp_table_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])
        with self.assertRaises(TypeError):
            sp_table_a.equals(self.not_a_categorical_factor)

    def test_equals_false_var_set(self):
        """
        Test that the equals method returns false when the comparing to a factor with different var_names.
        """
        vars_a = ["a", "b"]
        vars_b = ["c", "d"]
        probs_a = {(0, 0): 0.1, (0, 1): 0.2, (1, 0): 0.3, (1, 1): 0.4}
        categorical_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])
        categorical_b = self.cat_class(var_names=vars_b, probs_table=probs_a, cardinalities=[2, 2])
        self.assertFalse(categorical_a.equals(categorical_b))

    def test_equals_false_fails(self):
        """
        Test that the equals method returns false when the comparing to a factor with different probs.
        """
        vars_a = ["a", "b"]

        probs_a = {(0, 0): 0.1, (0, 1): 0.2, (1, 0): 0.3, (1, 1): 0.4}
        probs_b = {(0, 0): 0.1001, (0, 1): 0.1999, (1, 0): 0.3, (1, 1): 0.4}
        categorical_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])
        categorical_b = self.cat_class(var_names=vars_a, probs_table=probs_b, cardinalities=[2, 2])
        self.assertFalse(categorical_a.equals(categorical_b))

    def test_equals_false_present_not_default(self):
        """
        Test that the equals method returns false when a (non-default) value present in factor b and the corresponding value
        in the factor a is not the default value of factor b (and vice-versa).
        """
        vars_a = ["a", "b"]

        probs_a = {(0, 0): 0.1}
        probs_b = {(0, 1): 0.1}
        categorical_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])
        categorical_b = self.cat_class(var_names=vars_a, probs_table=probs_b, cardinalities=[2, 2])

        self.assertFalse(categorical_a.equals(categorical_b))
        self.assertFalse(categorical_b.equals(categorical_a))

    def test_equals_false_non_default_not_close(self):
        """
        Test that the equals method returns false when the (non-default) values present in both factors are not close.
        """
        vars_a = ["a", "b"]

        probs_a = {(0, 0): 0.11}
        probs_b = {(0, 0): 0.1}
        categorical_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])
        categorical_b = self.cat_class(var_names=vars_a, probs_table=probs_b, cardinalities=[2, 2])
        self.assertFalse(categorical_a.equals(categorical_b))
        self.assertFalse(categorical_b.equals(categorical_a))

    def test_multiply_same_scope(self):
        """
        Test that the multiply function returns the correct result.
        """
        vars_ex = ["a", "b"]
        probs_ex = {(0, 0): 0.01, (0, 1): 0.04, (1, 0): 0.09, (1, 1): 0.16}
        vars_b = ["a", "b"]
        probs_b = {(0, 0): 0.1, (0, 1): 0.2, (1, 0): 0.3, (1, 1): 0.4}
        sp_table_b = self.cat_class(var_names=vars_b, probs_table=probs_b, cardinalities=[2, 2])

        expected_resulting_factor = self.cat_class(
            var_names=vars_ex, probs_table=probs_ex, cardinalities=[2, 2]
        )
        actual_resulting_factor = sp_table_b.multiply(sp_table_b)
        self.assertTrue(actual_resulting_factor.equals(expected_resulting_factor))

    def test_multiply_fails_invalid_factor(self):
        """
        Test that the multiply function fails when attempting to multiply with a non-categorical factor type.
        """
        categorical_a = make_abc_factor_1(cat_class=self.cat_class)
        with self.assertRaises(TypeError):
            categorical_a.multiply(self.not_a_categorical_factor)

    def test_divide_fails_invalid_factor(self):
        """
        Test that the divide function fails when attempting to multiply with a non-categorical factor type.
        """
        categorical_a = make_abc_factor_1(cat_class=self.cat_class)
        with self.assertRaises(TypeError):
            categorical_a.divide(self.not_a_categorical_factor)

    def test_argmax(self):
        """
        Test that the argmax function returns the correct variable assignment.
        """
        vars_b = ["a", "b"]
        probs_b = {(0, 0): 0.1, (0, 1): 0.2, (1, 0): 0.5, (1, 1): 0.2}
        expected_result = (1, 0)
        categorical_a = self.cat_class(var_names=vars_b, probs_table=probs_b, cardinalities=[2, 2])

        actual_result = categorical_a.argmax()

        self.assertEqual(expected_result, actual_result)

    def test_kl_divergence_small_neg_works(self):
        """
        Test that the kl_divergence function does not fail on a negative KLD as a result of numerical errors.
        """
        vars_names = ["a"]
        epsilon = 1e-12
        probs_table_p = {(0,): 0.2, (1,): 0.8}
        probs_tensor_p = np.array(list(probs_table_p.values()))

        probs_table_q = {(0,): 0.2 + epsilon, (1,): 0.8 - epsilon}
        probs_tensor_q = np.array(list(probs_table_q.values()))

        log_p = np.log(probs_tensor_p)
        log_q = np.log(probs_tensor_q)
        kl_array = np.where(log_p != -np.inf, np.exp(log_p) * (log_p - log_q), 0.0)
        kld = np.sum(kl_array)
        self.assertTrue(kld < 0.0)
        categorical_p = self.cat_class(var_names=vars_names, probs_table=probs_table_p, cardinalities=[2])
        categorical_q = self.cat_class(var_names=vars_names, probs_table=probs_table_q, cardinalities=[2])

        expected_kld = 0.0
        actual_kld = categorical_p.kl_divergence(categorical_q)

        self.assertEqual(actual_kld, expected_kld)

    def test_kl_divergence_large_neg_fails(self):
        """
        Test that the kl_divergence function fails on a negative KLD as a result of numerical errors.
        """
        vars_names = ["a"]
        probs_table_p = {(0,): 1.0}
        categorical_p = self.cat_class(var_names=vars_names, probs_table=probs_table_p, cardinalities=[2])
        categorical_q = self.cat_class(var_names=vars_names, probs_table=probs_table_p, cardinalities=[2])
        categorical_p._raw_kld = mock.MagicMock(return_value=-1.0)

        # categorical_q = mock.Mock()
        # categorical_q.normalize = mock.MagicMock(return_value=categorical_q)
        with self.assertRaises(ValueError):
            categorical_p.kl_divergence(categorical_q)

    def test_multiply_subset_scope(self):
        """
        Test that the multiply function returns the correct result.
        """
        vars_ex = ["a", "b", "c"]
        probs_ex = {
            (0, 0, 0): np.exp(0.11),
            (0, 0, 1): np.exp(0.12),
            (0, 1, 0): np.exp(0.23),
            (0, 1, 1): np.exp(0.24),
            (1, 0, 0): np.exp(0.35),
            (1, 0, 1): np.exp(0.36),
            (1, 1, 0): np.exp(0.47),
            (1, 1, 1): np.exp(0.48),
        }
        expected_resulting_factor = self.cat_class(
            var_names=vars_ex, probs_table=probs_ex, cardinalities=[2, 2, 2]
        )

        sp_table_abc = make_abc_factor_1(cat_class=self.cat_class)

        vars_b = ["a", "b"]
        probs_b = {(0, 0): np.exp(0.1), (0, 1): np.exp(0.2), (1, 0): np.exp(0.3), (1, 1): np.exp(0.4)}
        sp_table_ab = self.cat_class(var_names=vars_b, probs_table=probs_b, cardinalities=[2, 2])
        actual_resulting_factor = sp_table_abc.multiply(sp_table_ab)
        self.assertTrue(actual_resulting_factor.equals(expected_resulting_factor))

    def test_absorb_partially_overlapping(self):
        """
        Test that the absorb method returns the correct result when the two factors have partially overlapping scopes.
        """
        vars_abc = ["a", "b", "c"]
        probs_abc = {
            (0, 0, 0): 0.1,
            (0, 0, 1): 0.2,
            (0, 1, 0): 0.3,
            (0, 1, 1): 0.4,
            (1, 0, 1): 0.6,
            (1, 1, 0): 0.7,
            (1, 1, 1): 0.8,
        }
        factor_abc = self.cat_class(var_names=vars_abc, probs_table=probs_abc, cardinalities=[2, 2, 2])
        vars_dc = ["d", "c"]
        probs_dc = {(0, 0): 1.1, (1, 0): 1.3, (1, 1): 1.4}
        factor_dc = self.cat_class(var_names=vars_dc, probs_table=probs_dc, cardinalities=[2, 2])

        vars_dabc = ["d", "a", "b", "c"]
        probs_dabc = {
            (0, 0, 0, 0): 0.1 * 1.1,
            # (0, 0, 0, 1): 0.2 * 0.0,
            (0, 0, 1, 0): 0.3 * 1.1,
            # (0, 0, 1, 1): 0.4 * 0.0,
            (0, 1, 0, 0): 0.0 * 1.1,
            # (0, 1, 0, 1): 0.6 * 0.0,
            (0, 1, 1, 0): 0.7 * 1.1,
            # (0, 1, 1, 1): 0.8 * 0.0,
            (1, 0, 0, 0): 0.1 * 1.3,
            (1, 0, 0, 1): 0.2 * 1.4,
            (1, 0, 1, 0): 0.3 * 1.3,
            (1, 0, 1, 1): 0.4 * 1.4,
            (1, 1, 0, 0): 0.0 * 1.3,
            (1, 1, 0, 1): 0.6 * 1.4,
            (1, 1, 1, 0): 0.7 * 1.3,
            (1, 1, 1, 1): 0.8 * 1.4,
        }
        expected_factor_dabc = self.cat_class(
            var_names=vars_dabc, probs_table=probs_dabc, cardinalities=[2, 2, 2, 2]
        )
        actual_factor_dabc = factor_abc.absorb(factor_dc)
        self.assertTrue(expected_factor_dabc.equals(actual_factor_dabc))

    def test_multiply_different_scope(self):
        """
        Test that the multiply function returns the correct result.
        """
        vars_ex = ["c", "d", "a", "b"]
        probs_ex = {
            (0, 0, 0, 0): 0.1 * 0.01,
            (0, 0, 0, 1): 0.1 * 0.04,
            (0, 0, 1, 0): 0.1 * 0.09,
            (0, 0, 1, 1): 0.1 * 0.16,
            (0, 1, 0, 0): 0.2 * 0.01,
            (0, 1, 0, 1): 0.2 * 0.04,
            (0, 1, 1, 0): 0.2 * 0.09,
            (0, 1, 1, 1): 0.2 * 0.16,
            (1, 0, 0, 0): 0.3 * 0.01,
            (1, 0, 0, 1): 0.3 * 0.04,
            (1, 0, 1, 0): 0.3 * 0.09,
            (1, 0, 1, 1): 0.3 * 0.16,
            (1, 1, 0, 0): 0.4 * 0.01,
            (1, 1, 0, 1): 0.4 * 0.04,
            (1, 1, 1, 0): 0.4 * 0.09,
            (1, 1, 1, 1): 0.4 * 0.16,
        }

        vars_ab = ["a", "b"]
        probs_ab = {(0, 0): 0.01, (0, 1): 0.04, (1, 0): 0.09, (1, 1): 0.16}
        vars_cd = ["c", "d"]
        probs_cd = {(0, 0): 0.1, (0, 1): 0.2, (1, 0): 0.3, (1, 1): 0.4}

        sp_table_cd = self.cat_class(var_names=vars_cd, probs_table=probs_cd, cardinalities=[2, 2])

        expected_resulting_factor = self.cat_class(
            var_names=vars_ex, probs_table=probs_ex, cardinalities=[2, 2, 2, 2]
        )
        sp_table_ab = self.cat_class(var_names=vars_ab, probs_table=probs_ab, cardinalities=[2, 2])
        actual_resulting_factor = sp_table_cd.multiply(sp_table_ab)
        self.assertTrue(actual_resulting_factor.equals(expected_resulting_factor))

    def test_cancel_divide_different_scope(self):
        """
        Test that the cancel and divide functions return the correct result when the factors have different scopes.
        """
        # TODO: split this into two tests.

        vars_ab = ["a", "b"]
        probs_ab = {(0, 0): 1.0, (0, 1): 2.0, (1, 0): 3.0, (1, 1): 4.0}
        factor_ab = Categorical(var_names=vars_ab, probs_table=probs_ab, cardinalities=[2, 2])

        vars_b = ["b"]
        probs_b = {(0,): 5.0, (1,): 6.0}
        factor_b = Categorical(var_names=vars_b, probs_table=probs_b, cardinalities=[2])

        probs_ab_expected = {(0, 0): 1.0 / 5.0, (0, 1): 2.0 / 6.0, (1, 0): 3.0 / 5.0, (1, 1): 4.0 / 6.0}
        factor_ab_expected = Categorical(
            var_names=vars_ab, probs_table=probs_ab_expected, cardinalities=[2, 2]
        )

        factor_ab_actual = factor_ab.cancel(factor_b)
        self.assertTrue(factor_ab_expected.equals(factor_ab_actual))
        factor_ab_actual = factor_ab.divide(factor_b)
        self.assertTrue(factor_ab_expected.equals(factor_ab_actual))

    def test_cancel_same_scope(self):
        """
        Test the cancel function applied to factors with the same scope.
        """
        vars_a = ["a", "b"]
        probs_a = {(0, 0): 1.0, (0, 1): 2.0, (1, 0): 3.0, (1, 1): 4.0}
        factor_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])

        vars_b = ["a", "b"]
        probs_b = {(0, 0): 5.0, (0, 1): 6.0, (1, 0): 7.0, (1, 1): 8.0}
        factor_b = self.cat_class(var_names=vars_b, probs_table=probs_b, cardinalities=[2, 2])

        vars_c = ["a", "b"]
        probs_c = {(0, 0): 1.0 / 5.0, (0, 1): 2.0 / 6.0, (1, 0): 3.0 / 7.0, (1, 1): 4.0 / 8.0}
        expected_resulting_factor = self.cat_class(var_names=vars_c, probs_table=probs_c, cardinalities=[2, 2])
        actual_resulting_factor = factor_a.cancel(factor_b)
        actual_resulting_factor.show()
        expected_resulting_factor.show()
        self.assertTrue(expected_resulting_factor.equals(actual_resulting_factor))

    def test_cancel_with_zeros(self):
        """
        Test that the cancel method returns the correct result when the two factors have different combinations
        of zeros for corresponding assignments.
        """
        vars_a = ["a", "b"]
        probs_a = {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 1.0, (1, 1): 1.0}
        factor_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])

        vars_b = ["a", "b"]
        probs_b = {(0, 0): 0.0, (0, 1): 1.0, (1, 0): 0.0, (1, 1): 1.0}
        factor_b = self.cat_class(var_names=vars_b, probs_table=probs_b, cardinalities=[2, 2])

        vars_c = ["a", "b"]
        probs_c = {(0, 0): 0.0, (0, 1): 0.0, (1, 0): np.inf, (1, 1): 1.0}
        expected_resulting_factor = self.cat_class(var_names=vars_c, probs_table=probs_c, cardinalities=[2, 2])
        actual_resulting_factor = factor_a.cancel(factor_b)
        actual_resulting_factor.show()
        expected_resulting_factor.show()
        self.assertTrue(expected_resulting_factor.equals(actual_resulting_factor))

    # TODO: change to log form and fix
    def test_marginalise(self):
        """
        Test that the marginalize function returns the correct result.
        """
        vars_a = ["a", "b", "c"]
        probs_a = {
            (0, 0, 0): 0.01,
            (0, 0, 1): 0.02,
            (0, 1, 0): 0.03,
            (0, 1, 1): 0.04,
            (1, 0, 0): 0.05,
            (1, 0, 1): 0.06,
            (1, 1, 0): 0.07,
            (1, 1, 1): 0.08,
        }
        sp_table_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2, 2])
        vars_ex = ["a"]
        probs_ex = {(0,): 0.10, (1,): 0.26}
        expected_resulting_factor = self.cat_class(var_names=vars_ex, probs_table=probs_ex, cardinalities=[2])
        actual_resulting_factor = sp_table_a.marginalize(vrs=["b", "c"], keep=False)
        self.assertTrue(actual_resulting_factor.equals(expected_resulting_factor))

        vars_ex = ["c"]
        probs_ex = {(0,): 0.01 + 0.03 + 0.05 + 0.07, (1,): 0.02 + 0.04 + 0.06 + 0.08}
        expected_resulting_factor = self.cat_class(var_names=vars_ex, probs_table=probs_ex, cardinalities=[2])
        actual_resulting_factor = sp_table_a.marginalize(vrs=["a", "b"], keep=False)
        self.assertTrue(actual_resulting_factor.equals(expected_resulting_factor))

    def test_observe_1(self):
        """
        Test that the reduce function returns the correct result.
        """
        sp_table_abc = make_abc_factor_1(cat_class=self.cat_class)
        vars_ex = ["b", "c"]
        probs_ex = {(0, 0): np.exp(0.01), (0, 1): np.exp(0.02), (1, 0): np.exp(0.03), (1, 1): np.exp(0.04)}
        expected_resulting_factor = self.cat_class(
            var_names=vars_ex, probs_table=probs_ex, cardinalities=[2, 2]
        )
        actual_resulting_factor = sp_table_abc.reduce(vrs=["a"], values=[0])
        self.assertTrue(actual_resulting_factor.equals(expected_resulting_factor))

    def test_observe_2(self):
        """
        Test that the reduce function returns the correct result.
        """
        sp_table_abc = make_abc_factor_1(cat_class=self.cat_class)
        vars_ex = ["a", "c"]
        probs_ex = {(0, 0): np.exp(0.03), (0, 1): np.exp(0.04), (1, 0): np.exp(0.07), (1, 1): np.exp(0.08)}
        expected_resulting_factor = self.cat_class(
            var_names=vars_ex, probs_table=probs_ex, cardinalities=[2, 2]
        )
        actual_resulting_factor = sp_table_abc.reduce(vrs=["b"], values=[1])
        self.assertTrue(actual_resulting_factor.equals(expected_resulting_factor))

    def test_distance_from_vacuous(self):
        """
        Test that the distance from vacuous function returns the correct result.
        """
        var_names = ["a", "c"]
        probs = {(0, 1): 0.4, (1, 0): 0.2, (1, 1): 0.3}
        factor = self.cat_class(var_names=var_names, probs_table=probs, cardinalities=[2, 2])

        correct_kl_p_vac = sum(
            [
                (0.4 / 0.9) * (np.log(0.4 / 0.9) - np.log(0.25)),
                (0.2 / 0.9) * (np.log(0.2 / 0.9) - np.log(0.25)),
                (0.3 / 0.9) * (np.log(0.3 / 0.9) - np.log(0.25)),
            ]
        )
        calculated_kl_p_vac = factor.distance_from_vacuous()
        self.assertAlmostEqual(calculated_kl_p_vac, correct_kl_p_vac)

    def test_distance_from_vacuous_sparse(self):
        """
        Test that the distance from vacuous function returns the correct result.
        """
        var_names = ["a", "c"]
        probs = {(0, 1): 0.5, (1, 0): 0.2, (1, 1): 0.3}
        factor = self.cat_class(var_names=var_names, probs_table=probs, cardinalities=[2, 2])

        correct_kl_p_vac = sum(
            [
                0.5 * (np.log(0.5) - np.log(0.25)),
                0.2 * (np.log(0.2) - np.log(0.25)),
                0.3 * (np.log(0.3) - np.log(0.25)),
            ]
        )
        calculated_kl_p_vac = factor.distance_from_vacuous()
        self.assertAlmostEqual(calculated_kl_p_vac, correct_kl_p_vac)

    def test_kld(self):
        """
        Test that the kld function returns the correct result.
        """
        var_names = ["a"]
        probs = {(2,): 0.2, (3,): 0.8}
        factor_1 = self.cat_class(var_names=var_names, probs_table=probs, cardinalities=[4])

        var_names = ["a"]
        probs = {(2,): 0.3, (3,): 0.7}
        factor_2 = self.cat_class(var_names=var_names, probs_table=probs, cardinalities=[4])
        computed_kld = factor_1.kl_divergence(factor_2)
        correct_kld = 0.2 * (np.log(0.2) - np.log(0.3)) + 0.8 * (np.log(0.8) - np.log(0.7))
        self.assertAlmostEqual(correct_kld, computed_kld)

    def test_kld2(self):
        """
        Test that the kld function returns the correct result.
        """
        var_names = ["a"]
        probs = {(2,): 1.0}
        factor_1 = self.cat_class(var_names=var_names, probs_table=probs, cardinalities=[4])

        var_names = ["a"]
        probs = {(2,): 0.5, (3,): 0.5}
        factor_2 = self.cat_class(var_names=var_names, probs_table=probs, cardinalities=[4])
        computed_kld = factor_1.kl_divergence(factor_2)
        correct_kld = 1.0 * (np.log(1.0) - np.log(0.5))
        self.assertAlmostEqual(computed_kld, correct_kld, places=4)

    def test_kld3(self):
        """
        Test that the kld function returns the correct result.
        """
        var_names = ["a"]
        probs = {(2,): 1.0, (3,): 1e-5}
        factor_1 = self.cat_class(var_names=var_names, probs_table=probs, cardinalities=[4])

        var_names = ["a"]
        probs = {(2,): 1.0, (3,): 1.0}
        factor_2 = self.cat_class(var_names=var_names, probs_table=probs, cardinalities=[4])
        computed_kld = factor_1.kl_divergence(factor_2)
        correct_kld_1 = 1.0 * (np.log(1.0) - np.log(0.5))
        correct_kld_2 = 1e-5 * (np.log(1e-5) - np.log(0.5))
        correct_kld = correct_kld_1 + correct_kld_2
        self.assertAlmostEqual(computed_kld, correct_kld, places=4)

    def test_divide_fails_cards(self):
        """
        Test that the divide function fails on inconsistent cardinalities.
        """
        var_names = ["a"]
        probs = {(0,): 1.0}
        factor_1 = self.cat_class(var_names=var_names, probs_table=probs, cardinalities=[2])

        var_names = ["a"]
        probs = {(2,): 0.0}
        factor_2 = self.cat_class(var_names=var_names, probs_table=probs, cardinalities=[3])

        with self.assertRaises(AssertionError):
            factor_1.divide(factor_2)

    def test_kld_2d_factor(self):
        """
        Test that the kld function returns the correct result.
        """
        vars_a = ["a", "b"]
        probs_a = {(0, 0): 0.2, (0, 1): 0.1, (1, 0): 0.3, (1, 1): 0.4}

        vars_b = ["b", "a"]
        probs_b = {(0, 0): 0.1, (0, 1): 0.4, (1, 0): 0.2, (1, 1): 0.3}

        correct_kld = (
            0.2 * np.log(0.2 / 0.1)
            + 0.1 * np.log(0.1 / 0.2)
            + 0.3 * np.log(0.3 / 0.4)
            + 0.4 * np.log(0.4 / 0.3)
        )
        factor_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])
        factor_b = self.cat_class(var_names=vars_b, probs_table=probs_b, cardinalities=[2, 2])
        computed_kld = factor_a.kl_divergence(factor_b)

        self.assertAlmostEqual(correct_kld, computed_kld)

    def test_kld_with_zeros(self):
        """
        Test that the kl_divergence method returns the correct result when the two factors have different combinations
        of zeros for corresponding assignments.
        """
        vars_a = ["a", "b"]
        probs_a = {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 1.0}
        factor_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])

        vars_b = ["a", "b"]
        probs_b = {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 1.0}
        factor_b = self.cat_class(var_names=vars_b, probs_table=probs_b, cardinalities=[2, 2])

        expected_kld = 0.0
        actual_kld = factor_b.kl_divergence(factor_a)
        self.assertEqual(expected_kld, actual_kld)

    def test_kld_with_zeros_sparse1(self):
        """
        Test that the kl_divergence method returns the correct result when the two factors have different combinations
        of zeros for corresponding assignments.
        """
        vars_a = ["a", "b"]
        probs_a = {(0, 1): 0.0, (1, 0): 0.0, (1, 1): 1.0}
        factor_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])

        vars_b = ["a", "b"]
        probs_b = {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 1.0}
        factor_b = self.cat_class(var_names=vars_b, probs_table=probs_b, cardinalities=[2, 2])

        expected_kld = 0.0
        actual_kld = factor_b.kl_divergence(factor_a)
        self.assertEqual(expected_kld, actual_kld)

    def test_kld_with_zeros_sparse2(self):
        """
        Test that the kl_divergence method returns the correct result when the two factors have different combinations
        of zeros for corresponding assignments.
        """
        vars_a = ["a", "b"]
        probs_a = {(0, 1): 0.0, (1, 0): 0.0, (1, 1): 1.0}
        factor_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])

        vars_b = ["a", "b"]
        probs_b = {(0, 1): 0.0, (1, 0): 0.0, (1, 1): 1.0}
        factor_b = self.cat_class(var_names=vars_b, probs_table=probs_b, cardinalities=[2, 2])
        expected_kld = 0.0
        actual_kld = factor_b.kl_divergence(factor_a)
        self.assertEqual(expected_kld, actual_kld)

    def test_kld_with_zeros_sparse3(self):
        """
        Test that the kl_divergence method returns the correct result when the two factors have different combinations
        of zeros for corresponding assignments.
        """
        vars_a = ["a", "b"]
        probs_a = {  # (0,0): 0.0 #log: -inf
            (0, 1): 0.0,  # log: -inf
            (1, 0): 0.0,  # log: -inf
            (1, 1): 1.0,
        }  # log: 0
        factor_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])

        vars_b = ["a", "b"]
        probs_b = {(0, 0): 0.5, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 0.5}  # log: -inf  # log: -inf
        factor_b = self.cat_class(var_names=vars_b, probs_table=probs_b, cardinalities=[2, 2])
        expected_kld = np.log(2)
        actual_kld = factor_a.kl_divergence(factor_b)
        self.assertEqual(expected_kld, actual_kld)

        expected_kld = np.inf
        actual_kld = factor_b.kl_divergence(factor_a)
        self.assertEqual(expected_kld, actual_kld)

    def test_kld_with_zeros_sparse4(self):
        """
        Test that the kl_divergence method returns the correct result when the two factors have different combinations
        of zeros for corresponding assignments.
        """
        prob = 0.16666666666666669
        vrs = ["24", "25"]
        probs = {(2, 5): prob, (5, 2): prob, (1, 5): prob, (5, 1): prob, (1, 2): prob, (2, 1): prob}
        normalized_self = self.cat_class(var_names=vrs, probs_table=probs, cardinalities=[9, 9])

        probs = {(8, 1): 0.0, (6, 1): 0.0, (1, 3): 0.0, (3, 1): 0.0, (1, 2): 0.5, (2, 1): 0.5, (0, 8): 0.0}

        factor = self.cat_class(var_names=vrs, probs_table=probs, cardinalities=[9, 9])
        actual_kld = normalized_self.kl_divergence(factor)
        expected_kld_list = [
            prob * (np.log(prob) - np.log(0)),    # (2, 5)              =inf
            prob * (np.log(prob) - np.log(0)),    # (5, 2)              =inf
            prob * (np.log(prob) - np.log(0)),    # (1, 5)              =inf
            prob * (np.log(prob) - np.log(0)),    # (5, 1)              =inf
            prob * (np.log(prob) - np.log(0.5)),  # (1, 2)              =-0.1831020481113516
            prob * (np.log(prob) - np.log(0.5)),  # (2, 1)              =-0.1831020481113516
            0 * (np.log(1)),                # (8, 1) (both 0.0)   =0.0
            0 * (np.log(1)),                # (6, 1) (both 0.0)   =0.0
            0 * (np.log(1)),                # (1, 3) (both 0.0)   =0.0
            0 * (np.log(1)),                # (3, 1) (both 0.0)   =0.0
            0 * (np.log(1)),                # (0, 8) (both 0.0)   =0.0
        ]
        expected_kld = sum(expected_kld_list)
        self.assertEqual(expected_kld, actual_kld)

    def test__reorder(self):
        """
        Test that the reorder function reorders teh assignments properly.
        """
        vars_cab = ["c", "a", "b"]
        probs_cab = {
            (0, 0, 0): 0.01,
            (0, 0, 1): 0.03,
            (0, 1, 0): 0.05,
            (0, 1, 1): 0.07,
            (1, 0, 0): 0.02,
            (1, 0, 1): 0.04,
            (1, 1, 0): 0.06,
            (1, 1, 1): 0.08,
        }

        vars_abc = ["a", "b", "c"]
        probs_abc = {
            (0, 0, 0): 0.01,
            (0, 0, 1): 0.02,
            (0, 1, 0): 0.03,
            (0, 1, 1): 0.04,
            (1, 0, 0): 0.05,
            (1, 0, 1): 0.06,
            (1, 1, 0): 0.07,
            (1, 1, 1): 0.08,
        }
        expected_result = self.cat_class(var_names=vars_abc, probs_table=probs_abc, cardinalities=[2, 2, 2])
        factor_cab = self.cat_class(var_names=vars_cab, probs_table=probs_cab, cardinalities=[2, 2, 2])
        actual_result = factor_cab.reorder(vars_abc)
        self.assertTrue(actual_result.equals(expected_result))

    def test__assert_consistent_cardinalities_pass(self):
        """
        Test that the _assert_consistent_cardinalities passes with consistent cardinalities
        """
        vars_a = ["a", "b"]
        probs_a = {(2, 1): 0.0}
        factor_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[3, 2])

        vars_b = ["b", "a"]
        probs_b = {(0, 2): 0.0}
        factor_b = self.cat_class(var_names=vars_b, probs_table=probs_b, cardinalities=[2, 3])
        factor_a._assert_consistent_cardinalities(factor_b)
        factor_b._assert_consistent_cardinalities(factor_a)

    def test__assert_consistent_cardinalities_fails(self):
        """
        Test that the _assert_consistent_cardinalities fails with inconsistent cardinaties
        """
        vars_a = ["a", "b"]
        probs_a = {(2, 1): 0.0}
        factor_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[3, 2])

        vars_b = ["b", "a"]
        probs_b = {(2, 1): 0.0}
        factor_b = self.cat_class(var_names=vars_b, probs_table=probs_b, cardinalities=[3, 2])
        with self.assertRaises(AssertionError):
            factor_a._assert_consistent_cardinalities(factor_b)
        with self.assertRaises(AssertionError):
            factor_b._assert_consistent_cardinalities(factor_a)

    def test_is_vacuous_close_true(self):
        """
        Test that the is_vacuous property is True when the factor is close to vacuous.
        """
        epsilon = 1e-10
        vars_a = ["a", "b"]
        probs_a = {(0, 0): 0.25 + epsilon, (0, 1): 0.25, (1, 0): 0.25 - epsilon, (1, 1): 0.25}
        factor_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])
        self.assertTrue(factor_a.is_vacuous)

    def test_is_vacuous_close_false(self):
        """
        Test that the is_vacuous property is False when the factor is not close to vacuous.
        """
        epsilon = 0.1
        vars_a = ["a", "b"]
        probs_a = {(0, 0): 0.25 + epsilon, (0, 1): 0.25, (1, 0): 0.25 - epsilon, (1, 1): 0.25}
        factor_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])
        self.assertFalse(factor_a.is_vacuous)

    def test___repr__(self):
        """
        Test that the representation magic function returns the correct string.
        """
        vars_a = ["a", "b"]
        probs_a = {(0, 0): 0.1, (0, 1): 0.2, (1, 0): 0.3, (1, 1): 0.4}
        factor_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])
        actual_repr_string = factor_a.__repr__()
        expected_repr_string = (
            "a\tb\tprob\n" + "0\t0\t0.1000\n" + "0\t1\t0.2000\n" + "1\t0\t0.3000\n" + "1\t1\t0.4000\n"
        )
        self.assertTrue(expected_repr_string, actual_repr_string)

    def test_potential(self):
        """
        Test that the potential function returns the correct result.
        """
        vars_a = ["a", "b"]
        probs_a = {(0, 0): 0.1, (0, 1): 0.2}
        factor_a = self.cat_class(var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2])
        actual_potential = factor_a.potential(["a", "b"], [0, 1])
        expected_potential = 0.2
        self.assertEqual(actual_potential, expected_potential)

    def test_template_var_names(self):
        """
        Test that the SparseCategoricalTemplate makes the correct factor when var_names are provided.
        """
        probs_a = {(0, 0): 0.1, (0, 1): 0.2}
        template = CategoricalTemplate(probs_table=probs_a, cardinalities=[2, 2])
        template.make_factor(var_names=["a", "b"])

    def test_template_var_templates(self):
        """
        Test that the SparseCategoricalTemplate makes the correct factor when var_templates are provided.
        """
        probs_a = {(0, 0): 0.1, (0, 1): 0.2}
        expected_factor = self.cat_class(var_names=["a_0", "b_0"], probs_table=probs_a, cardinalities=[2, 2])
        template = CategoricalTemplate(
            var_templates=["a_{i}", "b_{i}"], probs_table=probs_a, cardinalities=[2, 2]
        )
        actual_factor = template.make_factor(format_dict={"i": 0})
        self.assertTrue(actual_factor.equals(expected_factor))


class TestSparseCategorical(TestCategorical):
    """
    A test class for the SparseCategorical class. This class inherits from the TestCategorical class in order to use all
    of the tests in TestCategorical to also test the SparseCategorical class. This is makes sense because the interface
    to the two classes is almost identical, although there are some tests that are specific to a single class.
    """

    def __init__(self, *args, **kwargs):
        """
        The test class initializer.
        """
        super().__init__(*args, **kwargs)
        self.cat_class = SparseCategorical

    def test__make_dense(self):
        """
        Test that the _make_dense method returns the correct dense representation of a SparseCategorical.
        """
        default_log_prob = 0.0
        vars_abc = ["a", "b", "c"]
        sparse_probs_abc = {(0, 1, 0): 2.0, (0, 1, 2): 4.0}
        sparse_factor = SparseCategorical(
            var_names=vars_abc,
            log_probs_table=sparse_probs_abc,
            cardinalities=[2, 2, 3],
            default_log_prob=default_log_prob,
        )
        dense_probs_abc = {
            (0, 0, 0): 0.0,
            (0, 0, 1): 0.0,
            (0, 0, 2): 0.0,
            (0, 1, 0): 2.0,
            (0, 1, 1): 0.0,
            (0, 1, 2): 4.0,
            (1, 0, 0): 0.0,
            (1, 0, 1): 0.0,
            (1, 0, 2): 0.0,
            (1, 1, 0): 0.0,
            (1, 1, 1): 0.0,
            (1, 1, 2): 0.0,
        }

        dense_factor = SparseCategorical(
            var_names=vars_abc,
            log_probs_table=dense_probs_abc,
            cardinalities=[2, 2, 3],
            default_log_prob=default_log_prob,
        )

        self.assertTrue(_make_dense(sparse_factor).equals(dense_factor))

    def test_marginalise_keep_all_swapped(self):
        """
        Test that the cardinality order is correct after doing a mock marginalisation (and swopping
        variables).
        """
        # error recreation
        var_names = ["card4",
                     "card3",
                     "card2"]
        probs_table = {
            (0, 0, 0): 0.9,
            (1, 1, 0): 0.6,
            (2, 2, 1): 0.2,
            (3, 1, 1): 0.7,
            (3, 2, 0): 0.5,
            (3, 2, 1): 0.8}

        cardinalities = [4, 3, 2]

        vars_to_keep = ['card2', 'card3', 'card4']
        categorical = SparseCategorical(var_names=var_names,
                               cardinalities=cardinalities,
                               probs_table=probs_table)
        marginal = categorical.marginalize(vars_to_keep)
        self.assertTrue(marginal.cardinalities == [2, 3, 4])
        self.assertTrue(marginal.var_cards == {'card2':2, 'card3':3, 'card4':4})

    def test_equals_false_non_defaults_not_close(self):
        """
        Test that the equals method returns false when the all the non-default values are the same, but the default
        values differ.
        """
        vars_a = ["a", "b"]

        probs_a = {(0, 0): 0.1}
        probs_b = {(0, 0): 0.1}
        categorical_a = SparseCategorical(
            var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2], default_log_prob=0.0
        )
        categorical_b = SparseCategorical(
            var_names=vars_a, probs_table=probs_b, cardinalities=[2, 2], default_log_prob=0.1
        )
        self.assertFalse(categorical_a.equals(categorical_b))
        self.assertFalse(categorical_b.equals(categorical_a))

    def test_equals_false_non_defaults_not_defaults(self):
        """
        Test that the equals method returns false when the a non-default value that does not exist in the other factor has
        a value that is not equal to the default value.
        """
        default = 0.0
        vars_a = ["a", "b"]

        probs_a = {(0, 0): 0.01, (0, 1): 1.00}
        probs_b = {(0, 1): 1.0}
        categorical_a = SparseCategorical(
            var_names=vars_a, probs_table=probs_a, cardinalities=[2, 2], default_log_prob=default
        )
        categorical_b = SparseCategorical(
            var_names=vars_a, probs_table=probs_b, cardinalities=[2, 2], default_log_prob=default
        )
        self.assertFalse(categorical_a.equals(categorical_b))
        self.assertFalse(categorical_b.equals(categorical_a))

    def test_equals_false_diff_default_but_dense(self):
        """
        Test that the equals method returns false when the all the non-default values are the same, and the default
        values differ, but all the assignments are accounted for with non-default values.
        """
        vars_a = ["a"]

        probs_a = {(0,): 0.6, (1,): 0.4}
        probs_b = {(0,): 0.6, (1,): 0.4}
        categorical_a = SparseCategorical(
            var_names=vars_a, probs_table=probs_a, cardinalities=[2], default_log_prob=0.0
        )
        categorical_b = SparseCategorical(
            var_names=vars_a, probs_table=probs_b, cardinalities=[2], default_log_prob=0.1
        )
        self.assertTrue(categorical_a.equals(categorical_b))
        self.assertTrue(categorical_b.equals(categorical_a))

    def test__any_scope_binary_operation_both(self):
        """
        Test that the _any_scope_binary_operation returns the correct result when performing binary operations on nested
        table dictionaries when the result is only default when both values in the calculation are default.
        """
        default_value = 0.0
        nested_table_dict_a = {(1,): {(0,): 1.0}}
        nested_table_dict_b = {(0,): {(0,): 1.0}}
        expected_probs_table = {(0, 0): {(0,): 1.0}, (1, 0): {(0,): 2.0}, (1, 1): {(0,): 1.0}}
        outer_inner_cards_a = [[2], [2]]
        outer_inner_cards_b = [[2], [2]]
        actual_probs_table = _any_scope_binary_operation(
            ntd_a=nested_table_dict_a,
            outer_inner_cards_a=outer_inner_cards_a,
            ntd_b=nested_table_dict_b,
            outer_inner_cards_b=outer_inner_cards_b,
            func=lambda a, b: a + b,
            default=default_value,
            default_rules="both",
        )
        self.assertEqual(expected_probs_table, actual_probs_table)

    def test__any_scope_binary_operation_invalid_rule(self):
        """
        Test that the _any_scope_binary_operation raises a value error if an default rule is passed.
        """
        with self.assertRaises(ValueError):
            _any_scope_binary_operation(
                ntd_a=mock.Mock(),
                outer_inner_cards_a=mock.Mock(),
                ntd_b=mock.Mock(),
                outer_inner_cards_b=mock.Mock(),
                func=lambda a, b: a + b,
                default=0.0,
                default_rules="there-is-no-such-rule",
            )

    def test_apply_binary_operator(self):
        """
        Test that the apply_binary_operator function returns the correct result.
        """
        default_log_prob = 0.5
        vars_abc = ["a", "b", "c"]
        probs_abc = {  # (0, 0, 0): 0.5,
            # (0, 0, 1): 0.5,
            (0, 1, 0): 0.3,
            (0, 1, 1): 0.4,
        }
        vars_dbc = ["d", "b", "c"]
        probs_dbc = {
          # (0, 0, 0): 0.5,
            (0, 0, 1): 0.2,
          # (0, 1, 0): 0.5,
            (0, 1, 1): 0.4,
        }
        def_lp = default_log_prob

        vars_dabc = ["d", "a", "b", "c"]
        probs_dabc = {
            (0, 0, 0, 0): def_lp - def_lp,
            (0, 0, 0, 1): def_lp - 0.2,
            (0, 0, 1, 0): 0.3 - def_lp,
            (0, 0, 1, 1): 0.4 - 0.4,
            (0, 1, 0, 0): def_lp - def_lp,
            (0, 1, 0, 1): def_lp - 0.2,
            (0, 1, 1, 0): def_lp - def_lp,
            (0, 1, 1, 1): def_lp - 0.4,
            (1, 0, 0, 0): def_lp - def_lp,
            (1, 0, 0, 1): def_lp - def_lp,
            (1, 0, 1, 0): 0.3 - def_lp,
            (1, 0, 1, 1): 0.4 - def_lp,
            (1, 1, 0, 0): def_lp - def_lp,
            (1, 1, 0, 1): def_lp - def_lp,
            (1, 1, 1, 0): def_lp - def_lp,
            (1, 1, 1, 1): def_lp - def_lp,
        }

        expected_result = SparseCategorical(
            var_names=vars_dabc, log_probs_table=probs_dabc, cardinalities=[2, 2, 2, 2], default_log_prob=0.0
        )
        factor_abc = SparseCategorical(
            var_names=vars_abc,
            log_probs_table=probs_abc,
            cardinalities=[2, 2, 2],
            default_log_prob=default_log_prob,
        )
        factor_dbc = SparseCategorical(
            var_names=vars_dbc,
            log_probs_table=probs_dbc,
            cardinalities=[2, 2, 2],
            default_log_prob=default_log_prob,
        )
        actual_result = factor_abc._apply_binary_operator(factor_dbc, operator.sub)
        self.assertTrue(actual_result.equals(expected_result))

    def test_apply_binary_operator_diff_defaults_fails(self):
        """
        Test that the apply_binary_operator function fails with not implemented error if the default values of the two
        factors differ.
        """
        factor_a = make_abc_factor_1(SparseCategorical)
        factor_b = make_abc_factor_1(SparseCategorical)
        factor_a.default_log_prob = 1.0
        factor_b.default_log_prob = 0.1
        with self.assertRaises(NotImplementedError):
            factor_a._apply_binary_operator(factor_b, operator.sub)

    def test_template_var_names(self):
        """
        Test that the SparseCategoricalTemplate makes the correct factor when var_names are provided.
        """
        probs_a = {(0, 0): 0.1, (0, 1): 0.2}
        template = SparseCategoricalTemplate(probs_a, cardinalities=[2, 2])
        template.make_factor(var_names=["a", "b"])

    def test_template_var_templates(self):
        """
        Test that the SparseCategoricalTemplate make_factor makes the correct factor when var_templates are provided.
        """
        probs_a = {(0, 0): 0.1, (0, 1): 0.2}
        expected_factor = SparseCategorical(var_names=["a_0", "b_0"], probs_table=probs_a, cardinalities=[2, 2])
        template = SparseCategoricalTemplate(probs_a, cardinalities=[2, 2], var_templates=["a_{i}", "b_{i}"])
        actual_factor = template.make_factor(format_dict={"i": 0})
        self.assertTrue(actual_factor.equals(expected_factor))

    def test_template_no_var_params_fails(self):
        """
        Test that the SparseCategoricalTemplate make_factor fails when the template has no var_templates and no
        var_names are provided to make the factor.
        """
        probs_a = {(0, 0): 0.1}
        template = SparseCategoricalTemplate(
            probs_a,
            cardinalities=[2, 2],
        )
        with self.assertRaises(ValueError):
            template.make_factor()

    def test_sparse_init_fails_params(self):
        """
        Test that the Categorical constructor fails when neither probs_table or log_probs_tensor is given.
        """
        with self.assertRaises(ValueError):
            print("f")
            SparseCategorical(
                var_names=["a", "b"], cardinalities=[2, 2], probs_table=None, log_probs_table=None
            )

        # test that it completes successfully when probs_table is there
        SparseCategorical(var_names=["a", "b"], cardinalities=[2, 2], probs_table={(0, 0): 1.0})
        # test that it completes successfully when probs_table is there
        SparseCategorical(var_names=["a", "b"], cardinalities=[2, 2], log_probs_table={(0, 0): 0.0})

    def test__apply_to_probs(self):
        """
        Test that the _apply_to_probs function results in the correct factor.
        """
        def func(log_prob, assign):
            if sum(assign):
                return log_prob
            return -np.inf

        probs = {(0, 0): 0.1, (0, 1): 0.2}
        factor = SparseCategorical(var_names=["a", "b"], cardinalities=[2, 2], probs_table=probs)
        factor._apply_to_probs(func, include_assignment=True)

        expected_result_probs = {(0, 0): 0.0, (0, 1): 0.2}
        expected_result = SparseCategorical(
            var_names=["a", "b"], cardinalities=[2, 2], probs_table=expected_result_probs
        )
        self.assertTrue(expected_result.equals(factor))

    def test__to_df(self):
        """
        Test that the _to_df method returns the correct pandas dataframe representation of the factor.
        """
        probs = {(0, 0): 0.1, (0, 1): 0.2}
        factor = SparseCategorical(var_names=["a", "b"], cardinalities=[2, 2], probs_table=probs)
        actual_df = factor._to_df()
        expected_df = pd.DataFrame(
            data=[[0, 0, np.log(0.1)], [0, 1, np.log(0.2)]], columns=["a", "b", "log_prob"]
        )
        self.assertTrue(pd.DataFrame.equals(actual_df, expected_df))

"""
A test module for the _factor_utils module.
"""

import unittest
import mockito
import numpy as np

from veroku.factors import _factor_utils

# pylint: disable=too-many-public-methods


class TestFactorUtils(unittest.TestCase):
    """
    A test class for the _factor_utils module.
    """

    def test_format_list_elements(self):
        """
        Test that the format_list_elements returns a correctly formatted list.
        """
        f_list = ["a_{i}", "b_{i}", "c_{i}"]
        expected_list = ["a_0", "b_0", "c_0"]
        actual_list = _factor_utils.format_list_elements(f_list, {"i": 0})
        self.assertEqual(expected_list, actual_list)

    def test_make_column_vector(self):
        """
        Test that the make_column_vector returns the correct column vector for different inputs.
        """
        values_list = [0, 1, 2]
        expected_column_vector = np.array([[0], [1], [2]])
        actual_column_vector = _factor_utils.make_column_vector(values_list)
        self.assertTrue(np.array_equal(expected_column_vector, actual_column_vector))

        array_1d = np.array([0, 1, 2])
        actual_column_vector = _factor_utils.make_column_vector(array_1d)
        self.assertTrue(np.array_equal(expected_column_vector, actual_column_vector))

        colvector = np.array([[0], [1], [2]])
        actual_column_vector = _factor_utils.make_column_vector(colvector)
        self.assertTrue(np.array_equal(expected_column_vector, actual_column_vector))

        row_vector = np.array([[0, 1, 2]])
        actual_column_vector = _factor_utils.make_column_vector(row_vector)
        self.assertTrue(np.array_equal(expected_column_vector, actual_column_vector))

    def test_remove_duplicate_values(self):
        """
        Test that the test_remove_duplicate_values removes the correct values.
        """
        expected_result = [0, 1, 2]
        actual_result = _factor_utils.remove_duplicate_values([0, 1, 1, 2])
        self.assertEqual(expected_result, actual_result)

    def test_remove_duplicate_values_nz_tol(self):
        """
        Test that the test_remove_duplicate_values removes the correct values with a non-zero tolerance.
        """
        expected_result = [0, 1.0001, 1.1, 2]
        actual_result = _factor_utils.remove_duplicate_values([0, 1.0001, 1.0002, 1.1, 2], tol=0.01)
        self.assertEqual(expected_result, actual_result)

    def test_make_square_matrix(self):
        """
        Test that the make_square_matrix returns the correct square matrix for different inputs.
        """

        values_list = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        expected_matrix = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]])
        actual_matrix = _factor_utils.make_square_matrix(values_list)
        self.assertTrue(np.array_equal(expected_matrix, actual_matrix))

        square_matrix = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]])
        actual_matrix = _factor_utils.make_square_matrix(square_matrix)
        self.assertTrue(np.array_equal(expected_matrix, actual_matrix))

        int_val = 0
        expected_matrix = np.array([[0]])
        actual_matrix = _factor_utils.make_square_matrix(int_val)
        self.assertTrue(np.array_equal(expected_matrix, actual_matrix))

        float_val = 0.0
        expected_matrix = np.array([[0.0]])
        actual_matrix = _factor_utils.make_square_matrix(float_val)
        self.assertTrue(np.array_equal(expected_matrix, actual_matrix))

    def test_make_square_matrix_fails_3d(self):
        """
        Test that the list_to_square_matrix fails with more than 2d array.
        """
        tensor_3d = np.array(np.ones([2, 2, 2]))
        with self.assertRaises(ValueError):
            _factor_utils.make_square_matrix(tensor_3d)

    def test_list_to_square_matrix_fails_not_matrix_like(self):
        """
        Test that the list_to_square_matrix fails with non matrix like input.
        """
        not_matrix_like = mockito.mock()
        with self.assertRaises(ValueError):
            _factor_utils.make_square_matrix(not_matrix_like)

    def test_make_scalar(self):
        """
        Test that the make_scalar returns the correct scalar value for different inputs.
        """

        expected_scalar = 0.0
        input_matrix = np.array([[0.0]])
        actual_scalar = _factor_utils.make_scalar(input_matrix)
        self.assertTrue(np.array_equal(expected_scalar, actual_scalar))

        expected_scalar = 1
        input_matrix = np.array([[1]])
        actual_scalar = _factor_utils.make_scalar(input_matrix)
        self.assertTrue(np.array_equal(expected_scalar, actual_scalar))

        expected_scalar = 0.0
        input_list = [0.0]
        actual_scalar = _factor_utils.make_scalar(input_list)
        self.assertTrue(np.array_equal(expected_scalar, actual_scalar))

    def test_make_scalar_fails_list_len(self):
        """
        Test that the make_scalar fails if the input has more than one value.
        """
        input_list = [0.0, 1.0]
        with self.assertRaises(ValueError):
            _factor_utils.make_scalar(input_list)

    def test_make_scalar_fails_array_len(self):
        """
        Test that the make_scalar fails if the input has more than one value.
        """
        input_list = np.array([0.0, 1.0])
        with self.assertRaises(ValueError):
            _factor_utils.make_scalar(input_list)

    def test_make_scalar_fails_invalid_type(self):
        """
        Test that the make_scalar fails if the input has more than one value.
        """
        not_supported_type = mockito.mock()
        with self.assertRaises(TypeError):
            _factor_utils.make_scalar(not_supported_type)

    def test_indexed_square_matrix_operation(self):
        """
        Test that the indexed_square_matrix_operation uses the correct pairs of values and returns the correct result.
        """
        matrix_a = np.array([[10, 11, 12], [13, 14, 15], [16, 17, 18]])
        #          np.array([[38, 27, 55], [80, 64, 22], [72, 30, 21]])  (matrix_b_same_order_as_a)
        expected = np.array([[48, 38, 67], [93, 78, 37], [88, 47, 39]])
        expected_result_matrix = expected
        matrix_a_vars = ["a", "b", "c"]

        matrix_b = np.array([[21, 30, 72], [22, 64, 80], [55, 27, 38]])
        matrix_b_vars = ["c", "b", "a"]

        expected_result_vars = ["a", "b", "c"]
        actual_result_matrix, actual_result_vars = _factor_utils.indexed_square_matrix_operation(
            matrix_a, matrix_b, matrix_a_vars, matrix_b_vars, lambda a, b: a + b
        )
        self.assertTrue(np.array_equal(expected_result_matrix, actual_result_matrix))
        self.assertEqual(expected_result_vars, actual_result_vars)

    def test_list_to_square_matrix_1d_list(self):
        """
        Test that the list_to_square_matrix returns the correct result with a 1d list.
        """
        expected_result = np.array([[1.0]])
        actual_result = _factor_utils.list_to_square_matrix([1.0])
        self.assertEqual(expected_result, actual_result)

    def test_list_to_square_matrix_2d_list(self):
        """
        Test that the list_to_square_matrix returns the correct result with a 2d list.
        """
        expected_result = np.array([[1.0]])
        actual_result = _factor_utils.list_to_square_matrix([[1.0]])
        self.assertEqual(expected_result, actual_result)

    def test_list_to_square_matrix_fails_empty_list(self):
        """
        Test that the list_to_square_matrix fails with empty list input.
        """
        with self.assertRaises(ValueError):
            _factor_utils.list_to_square_matrix([])

    def test_list_to_square_matrix_fails_3d(self):
        """
        Test that the list_to_square_matrix fails with more than 2d array.
        """
        tensor_3d_list = [[[2, 2], [2, 2]], [[2, 2], [2, 2]]]
        with self.assertRaises(ValueError):
            _factor_utils.list_to_square_matrix(tensor_3d_list)

    def test_list_to_square_matrix_not_square(self):
        """
        Test that the list_to_square_matrix fails with more than 2d array.
        """
        not_square_mat_list = [[2, 3, 5], [2, 3]]
        with self.assertRaises(ValueError):
            _factor_utils.list_to_square_matrix(not_square_mat_list)

    def test_list_to_square_matrix_1d_array(self):
        """
        Test that the list_to_square_matrix fails with a 1d input vector input.
        """
        input_vector = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8])
        with self.assertRaises(ValueError):
            _factor_utils.list_to_square_matrix(input_vector)

    def test_list_to_square_matrix_list_len(self):
        """
        Test that the list_to_square_matrix fails with a list of different length lists
        """
        input_lists = [[0, 1, 2], [3, 4], [5, 6, 7, 8]]
        with self.assertRaises(ValueError):
            _factor_utils.list_to_square_matrix(input_lists)

    def test_list_to_square_matrix_num_lists(self):
        """
        Test that the list_to_square_matrix fails when the number of lists are incorrect
        """
        input_lists = [[0, 1, 2], [3, 4, 5]]
        with self.assertRaises(ValueError):
            _factor_utils.list_to_square_matrix(input_lists)

    def test_list_to_square_matrix_list_len2(self):
        """
        Test that the list_to_square_matrix fails when the number of lists are incorrect
        """
        input_lists = [[0, 1]]
        with self.assertRaises(ValueError):
            _factor_utils.list_to_square_matrix(input_lists)

    def test_log(self):
        """
        Test that the log function raises a warning with input < 0.
        """
        with self.assertRaises(Warning):
            _factor_utils.log(-1.0)

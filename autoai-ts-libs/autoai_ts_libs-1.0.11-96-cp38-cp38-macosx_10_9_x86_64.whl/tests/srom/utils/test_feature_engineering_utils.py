"""Test cases for feature engineering utils. """

import unittest
import pandas as pd
import numpy as np
from autoai_ts_libs.srom.transformers.utils import feature_engineering_utils as ft


class TestFeatureEngineeringUtil(unittest.TestCase):
    """ class for testing the TestFeatureEngineeringUtil model. """

    @classmethod
    def setUp(cls):
        """setup method for the entire class."""
        cls.NotNumpy = [1, 2, 3, 4, 5, 6]
        cls.MultiDim = np.array([[1], [2]])
        cls.X2 = pd.Series([1, 2, 3, 4, 6])
        cls.X = np.ndarray([10])

    def test_check_single_dimensional_array(self):
        """ test the check single dimensional array method. """
        test_class = self.__class__
        self.assertRaises(ValueError, ft.check_single_dimensional_array, test_class.NotNumpy)
        self.assertRaises(ValueError, ft.check_single_dimensional_array, test_class.MultiDim)
        self.assertIsNotNone(ft.check_single_dimensional_array(test_class.X))
        self.assertIsNotNone(ft.check_single_dimensional_array(test_class.X2))

    def test_remove_nan_single_dimensional_array(self):
        """ test for remove_nan_single_dimensional_array method."""
        test_class = self.__class__
        self.assertIsNotNone(ft.remove_nan_single_dimensional_array(test_class.X2))

    def test_remove_zero_single_dimensional_array(self):
        """ Test for remove_zero_single_dimensional_array method."""
        test_class = self.__class__
        self.assertIsNotNone(ft.remove_zero_single_dimensional_array(test_class.X2))

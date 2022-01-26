import unittest
import pandas as pd
import numpy as np
from autoai_ts_libs.srom.imputers.decomposition_imputers import (
    PCAImputer,
    KernelPCAImputer,
    TruncatedSVDImputer,
    NMFImputer,
    IncrementalPCAImputer,
)
from autoai_ts_libs.srom.imputers.interpolators import PreMLImputer


class TestDecompositionImputers(unittest.TestCase):
    """ class for testing different Decomposition Imputers"""

    @classmethod
    def setUp(cls):
        uni_x = pd.DataFrame({"A": [1, 2, 3, 4, 5, None, 7, 8, 9]})
        multi_x = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5, None, 7, 8, 9, 10],
                "B": [101, 102, None, 104, 105, 106, 107, 108, 109, 110],
                "C": [51, 52, None, 54, 55, 56, None, 58, 59, 60],
            }
        )
        imputers = [
            PCAImputer,
            KernelPCAImputer,
            TruncatedSVDImputer,
            NMFImputer,
            IncrementalPCAImputer,
        ]
        cls.uni_x = uni_x
        cls.multi_x = multi_x
        cls.imputers = imputers

    def test_fit_transform(self):
        """
        Test Fit and transform
        """
        test_class = self.__class__
        uni_x = test_class.uni_x
        multi_x = test_class.multi_x

        # Test SimpleImputer with multivariate data
        try:
            for est in test_class.imputers:
                print("testing", est)
                imputer = est(n_components=2)
                imputer.fit(multi_x)
                interpolated = imputer.transform(multi_x)
                self.assertFalse(np.any(np.isnan(interpolated)))
        except Exception as e:
            self.fail("Failed : " + str(est.__name__) + " " + str(e))

        # Test PreMLImputer with univariate timeseries data
        try:
            for est in test_class.imputers:
                print("testing", est)
                imputer = est(n_components=2, base_imputer=PreMLImputer(), order=5)
                imputer.fit(uni_x)
                interpolated = imputer.transform(uni_x)
                self.assertFalse(np.any(np.isnan(interpolated)))
        except Exception as e:
            self.fail("Failed : " + str(est.__name__) + " " + str(e))

        # Test PreMLImputer with multivariate timeseries data
        try:
            for est in test_class.imputers:
                print("testing", est)
                imputer = est(n_components=2, base_imputer=PreMLImputer(), order=5)
                imputer.fit(multi_x)
                interpolated = imputer.transform(multi_x)
                self.assertFalse(np.any(np.isnan(interpolated)))
        except Exception as e:
            self.fail("Failed : " + str(est.__name__) + " " + str(e))

    def test_fit_transform_without_nan(self):
        """
        Test Fit and transform without nan
        """
        test_class = self.__class__
        uni_x = pd.DataFrame({"A": [1, 2, 3, 4, 5, 6, 7, 8, 9]})
        multi_x = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "B": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
                "C": [51, 52, 53, 54, 55, 56, 57, 58, 59, 60],
            }
        )

        # Test SimpleImputer with multivariate data
        try:
            for est in test_class.imputers:
                print("testing", est)
                imputer = est(n_components=2)
                imputer.fit(multi_x)
                interpolated = imputer.transform(multi_x)
                self.assertFalse(np.any(np.isnan(interpolated)))
        except Exception as e:
            self.fail("Failed : " + str(est.__name__) + " " + str(e))

        # Test PreMLImputer with univariate timeseries data
        try:
            for est in test_class.imputers:
                print("testing", est)
                imputer = est(n_components=2, base_imputer=PreMLImputer(), order=5)
                imputer.fit(uni_x)
                interpolated = imputer.transform(uni_x)
                self.assertFalse(np.any(np.isnan(interpolated)))
        except Exception as e:
            self.fail("Failed : " + str(est.__name__) + " " + str(e))

        # Test PreMLImputer with multivariate timeseries data
        try:
            for est in test_class.imputers:
                print("testing", est)
                imputer = est(n_components=2, base_imputer=PreMLImputer(), order=5)
                imputer.fit(multi_x)
                interpolated = imputer.transform(multi_x)
                self.assertFalse(np.any(np.isnan(interpolated)))
        except Exception as e:
            self.fail("Failed : " + str(est.__name__) + " " + str(e))

    def test_set_params(self):
        """
        Test set_params
        """
        test_class = self.__class__
        PARAMS = {
            PCAImputer: {
                "n_components": 12,
            }    ,
            KernelPCAImputer: {
                "n_components": 12,
            },
            TruncatedSVDImputer: {
                "n_components": 12,
            },
            NMFImputer: {
                "n_components": 12,
            },
            IncrementalPCAImputer: {
                "n_components": 12,
            },
        }
        try:
            for est in test_class.imputers[0:1]:
                params = PARAMS[est]
                imputer = est()
                imputer.set_params(**params)
                self.assertEqual(PARAMS[est]["n_components"],imputer.decomposer.get_params()["n_components"])
        except Exception as e:
            self.fail("Failed : " + str(est.__name__) + " " + str(e))

    def test_fit_transform_less_data(self):
        """
        Test Fit and transform less_data
        """
        test_class = self.__class__
        multi_x = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5, None, 7, 8, 9, 10],
                "B": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
                "C": [51, 52, 53, 54, 55, 56, 57, 58, 59, 60],
            }
        )
        test_x = pd.DataFrame(
            {
                "A": [7, 8, 9, 10],
                "B": [107, 108, 109, 110],
                "C": [57, 58, 59, 60],
            }
        )
        # Test PreMLImputer with multivariate timeseries data
        try:
            for est in test_class.imputers:
                print("testing", est)
                imputer = est(n_components=2, base_imputer=PreMLImputer(), order=5)
                imputer.fit(multi_x)
                interpolated = imputer.transform(test_x)
                self.assertFalse(np.any(np.isnan(interpolated)))
        except Exception as e:
            self.fail("Failed : " + str(est.__name__) + " " + str(e))

        test_x = pd.DataFrame(
            {
                "A": [7, None, 9, 10],
                "B": [107, None, 109, 110],
                "C": [57, 58, 59, 60],
            }
        )
        # Test PreMLImputer with multivariate timeseries data
        try:
            for est in test_class.imputers:
                print("testing", est)
                imputer = est(n_components=2, base_imputer=PreMLImputer(), order=5)
                self.assertRaises(Exception,imputer,"transform",test_x)
        except Exception as e:
            self.fail("Failed : " + str(est.__name__) + " " + str(e))

    def test_fit_transform_with_other_missing_value(self):
        """
        Test Fit and transform
        """
        test_class = self.__class__
        uni_x = pd.DataFrame({"A": [1, 2, 3, 4, 5, -999, 7, 8, 9]})
        multi_x = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5, -999, 7, 8, 9, 10],
                "B": [101, 102, -999, 104, 105, 106, 107, 108, 109, 110],
                "C": [51, 52, -999, 54, 55, 56, -999, 58, 59, 60],
            }
        )
        

        # Test SimpleImputer with multivariate data
        try:
            for est in test_class.imputers:
                print("testing", est)
                imputer = est(n_components=2,missing_values=-999)
                imputer.fit(multi_x)
                interpolated = imputer.transform(multi_x)
                self.assertFalse(np.any(np.isnan(interpolated)))
        except Exception as e:
            self.fail("Failed : " + str(est.__name__) + " " + str(e))

        # Test PreMLImputer with univariate timeseries data
        try:
            for est in test_class.imputers:
                print("testing", est)
                imputer = est(n_components=2, base_imputer=PreMLImputer(), order=5,missing_values=-999)
                imputer.fit(uni_x)
                interpolated = imputer.transform(uni_x)
                self.assertFalse(np.any(np.isnan(interpolated)))
        except Exception as e:
            self.fail("Failed : " + str(est.__name__) + " " + str(e))

        # Test PreMLImputer with multivariate timeseries data
        try:
            for est in test_class.imputers:
                print("testing", est)
                imputer = est(n_components=2, base_imputer=PreMLImputer(), order=5,missing_values=-999)
                imputer.fit(multi_x)
                interpolated = imputer.transform(multi_x)
                self.assertFalse(np.any(np.isnan(interpolated)))
        except Exception as e:
            self.fail("Failed : " + str(est.__name__) + " " + str(e))


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)

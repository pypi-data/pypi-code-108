import unittest
import pandas as pd
import numpy as np
from autoai_ts_libs.srom.imputers.predictive_imputer import (
    PredictiveImputer
)
from autoai_ts_libs.srom.imputers.interpolators import PreMLImputer

class TestPredictiveImputers(unittest.TestCase):
    """ class for testing PredictiveImputer"""

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
        cls.uni_x = uni_x
        cls.multi_x = multi_x
        
    def test_fit_transform(self):
        """
        Test fit and transform
        """
        test_class = self.__class__
        uni_x = test_class.uni_x
        multi_x = test_class.multi_x

        #Test multivariate iid
        imputer = PredictiveImputer()
        imputer.fit(multi_x)
        interpolated = imputer.transform(multi_x)
        self.assertFalse(np.any(np.isnan(interpolated)))

        #Test univariate ts
        imputer = PredictiveImputer(order=5,base_imputer=PreMLImputer())
        imputer.fit(uni_x)
        interpolated = imputer.transform(uni_x)
        self.assertFalse(np.any(np.isnan(interpolated)))

        #Test multivariate ts
        imputer = PredictiveImputer(order=5,base_imputer=PreMLImputer())
        imputer.fit(multi_x)
        interpolated = imputer.transform(multi_x)
        self.assertFalse(np.any(np.isnan(interpolated)))

    def test_fit_transform_without_nan(self):
        """
        Test fit and transform without nan
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
        #Test multivariate iid
        imputer = PredictiveImputer()
        imputer.fit(multi_x)
        interpolated = imputer.transform(multi_x)
        self.assertFalse(np.any(np.isnan(interpolated)))

        #Test univariate ts
        imputer = PredictiveImputer(order=5,base_imputer=PreMLImputer())
        imputer.fit(uni_x)
        interpolated = imputer.transform(uni_x)
        self.assertFalse(np.any(np.isnan(interpolated)))

        #Test multivariate ts
        imputer = PredictiveImputer(order=5,base_imputer=PreMLImputer())
        imputer.fit(multi_x)
        interpolated = imputer.transform(multi_x)
        self.assertFalse(np.any(np.isnan(interpolated)))

    def test_fit_transform_with_less_data(self):
        """
        Test fit and transform with less data
        """
        test_class = self.__class__
        multi_x = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
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
        #Test multivariate ts
        imputer = PredictiveImputer(order=5,base_imputer=PreMLImputer())
        imputer.fit(multi_x)
        interpolated = imputer.transform(test_x)
        self.assertFalse(np.any(np.isnan(interpolated)))
        test_x = pd.DataFrame(
            {
                "A": [7, None, 9, 10],
                "B": [107, None, 109, 110],
                "C": [57, 58, 59, 60],
            }
        )
        imputer = PredictiveImputer(order=5,base_imputer=PreMLImputer())
        imputer.fit(multi_x)
        self.assertRaises(Exception,imputer,"transform",test_x)
        
    def test_fit_transform_with_other_missing_values(self):
        """
        Test fit and transform
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

        #Test multivariate iid
        imputer = PredictiveImputer(missing_values=-999)
        imputer.fit(multi_x)
        interpolated = imputer.transform(multi_x)
        self.assertFalse(np.any(np.isnan(interpolated)))

        #Test univariate ts
        imputer = PredictiveImputer(order=5,base_imputer=PreMLImputer(),missing_values=-999)
        imputer.fit(uni_x)
        interpolated = imputer.transform(uni_x)
        self.assertFalse(np.any(np.isnan(interpolated)))

        #Test multivariate ts
        imputer = PredictiveImputer(order=5,base_imputer=PreMLImputer(),missing_values=-999)
        imputer.fit(multi_x)
        interpolated = imputer.transform(multi_x)
        self.assertFalse(np.any(np.isnan(interpolated)))


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)

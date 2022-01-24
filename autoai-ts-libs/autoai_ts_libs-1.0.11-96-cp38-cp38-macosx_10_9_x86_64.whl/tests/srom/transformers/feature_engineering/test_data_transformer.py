# IBM Confidential Materials
# Licensed Materials - Property of IBM
# IBM Smarter Resources and Operation Management
# (C) Copyright IBM Corp. 2019 All Rights Reserved.
# US Government Users Restricted Rights
#  - Use, duplication or disclosure restricted by
#    GSA ADP Schedule Contract with IBM Corp.

import unittest
import numpy as np
from autoai_ts_libs.srom.transformers.feature_engineering.base import DataTransformer


class TestDataTransformer(unittest.TestCase):
    """Test methods for DataTransformer"""

    def test_fit_transform(self):
        """Test fit and transform method"""
        data = np.array([1, 2, 3, 4, 100, 2, 3, 4, 5, 100, 5, 6, 7, 8, 100])
        data = data.astype('float64')
        X = data.reshape(-1, 1)
        tf = DataTransformer()
        fitted = tf.fit(X)
        fitted.transform(X)
        self.assertEqual(fitted.n_features_, X.shape[1])

    def test_fit_exceptions(self):
        """Test fit exceptions"""
        data = np.array([1, 2, 3, 4, 100, 2, 3, 4, 5, 100, 5, 6, 7, 8, 100])
        data = data.astype('float64')
        X = data.reshape(-1, 1)
        data = np.array([1, 2, 3, 4, 100, 2, 3, 4, 5, 100])
        y = data.astype('float64')
        tf = DataTransformer()
        self.assertRaises(Exception, tf.transform)
        X = np.delete(X, 0, axis=0)
        self.assertRaises(Exception, tf.transform)
        tf = DataTransformer()
        tf.fit(X)
        self.assertRaises(ValueError, tf.transform, y)


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)

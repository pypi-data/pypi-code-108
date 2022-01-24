# IBM Confidential Materials
# Licensed Materials - Property of IBM
# IBM Smarter Resources and Operation Management
# (C) Copyright IBM Corp. 2019 All Rights Reserved.
# US Government Users Restricted Rights
#  - Use, duplication or disclosure restricted by
#    GSA ADP Schedule Contract with IBM Corp.

"""Test cases for Timeseries split class"""
import unittest
import pandas as pd
from autoai_ts_libs.srom.joint_optimizers.cv.time_series_splits import TimeSeriesTrainTestSplit


class TestTimeSeriesSplits(unittest.TestCase):
    """Test methods in TimeSeriesSplits class"""

    @classmethod
    def setUpClass(cls):
        """Setup method: Called once before test-cases execution"""
        dataset = pd.read_csv("./tests/data/bcw.csv")
        cols = dataset.columns.values.tolist()
        cols.remove('class')
        cls.cols = cols
        cls.X = dataset[cls.cols]
        cls.y = dataset['class']
        cls.y_array = cls.y.values

    @classmethod
    def tearDownClass(cls):
        """teardown class method: Called once after test-cases execution"""
        pass

    def test_time_series_train_test_split(self):
        """ Test time series kfold sliding split"""
        test_class = self.__class__
        # With n_test_size=10
        tstts = TimeSeriesTrainTestSplit()
        output = list(tstts.split(test_class.X))
        self.assertEqual(len(output), 1)

        # With n_test_size=5
        tstts = TimeSeriesTrainTestSplit(n_test_size=5)
        output = list(tstts.split(test_class.X))
        self.assertEqual(len(output), 1)

        # With n_test_size=650
        tstts = TimeSeriesTrainTestSplit(n_test_size=650)
        output = list(tstts.split(test_class.X))
        self.assertEqual(len(output), 1)

        # With n_test_size=700
        tstts = TimeSeriesTrainTestSplit(n_test_size=700)
        with self.assertRaises(ValueError):
            list(tstts.split(test_class.X))


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)

import unittest
import logging
import pandas as pd

from sklearn.datasets import make_regression
from autoai_ts_libs.sklearn.small_data_standard_row_mean_center_transformers import StandardRowMeanCenter
from autoai_ts_libs.sklearn.small_data_standard_row_mean_center_transformers import WindowStandardRowMeanCenterUTS
from autoai_ts_libs.sklearn.small_data_standard_row_mean_center_transformers import WindowStandardRowMeanCenterMTS

logger = logging.getLogger()


class StandardRowMeanCenterTest(unittest.TestCase):
    def setUp(self):
        infile = "https://vincentarelbundock.github.io/Rdatasets/csv/datasets/AirPassengers.csv"
        cols = ["ID", "time", "AirPassengers"]
        df = pd.read_csv(infile, names=cols, sep=r',', index_col='ID', engine='python', skiprows=1)
        trainnum = 100
        self.trainset = df.iloc[:trainnum, 1].values
        self.trainset = self.trainset.reshape(-1, 1)
        self.testset = df.iloc[trainnum:, 1].values
        self.testset = self.testset.reshape(-1, 1)

        self.lookback_window = 10
        self.prediction_horizon = 1

        # test corner case
        X, y = make_regression(n_features=10, n_informative=2, random_state=0, shuffle=False)
        self.X = X
        self.y = y

    def test_standard_row_mean_center_transformer(self):
        transformer = StandardRowMeanCenter()
        self.assertIsNotNone(transformer)
        X_train, y_train = transformer.fit_transform(self.trainset, self.trainset)
        self.assertTrue(X_train.shape[1] > 0)
        self.assertTrue(y_train.shape[1] > 0)

    def test_window_standard_row_mean_center_transformer_uts(self):
        transformer = WindowStandardRowMeanCenterUTS()
        self.assertIsNotNone(transformer)
        X_train, y_train = transformer.fit_transform(self.trainset, self.trainset)
        self.assertTrue(X_train.shape[1] > 0)
        self.assertTrue(y_train.shape[1] > 0)

    def test_window_standard_row_mean_center_transformer_mts(self):
        transformer = WindowStandardRowMeanCenterMTS()
        self.assertIsNotNone(transformer)

        X_train, y_train = transformer.fit_transform(self.X, self.X)
        self.assertTrue(X_train.shape[1] > 0)
        self.assertTrue(y_train.shape[1] > 0)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()

import unittest
import pandas as pd
import numpy as np
from autoai_ts_libs.srom.transformers.preprocessing.ts_transformer import (
    TimeTensorTransformer,
    Flatten,
    TimeTensorTransformer,
    WaveletFeatures,
    FFTFeatures,
    SummaryStatistics,
    AdvancedSummaryStatistics,
    HigherOrderStatistics,
    RandomTimeSeriesFeatures,
    RandomTimeTensorTransformer,
    TimeSeriesFeatureUnion,
    customTimeSeriesFeatures,
    NormalizedFlatten,
    DifferenceNormalizedFlatten,
    DifferenceFlatten,
    LocalizedFlatten
)
from autoai_ts_libs.srom.transformers.feature_engineering.timeseries.function_map import MAPPING


class TestTsTransformer(unittest.TestCase):
    """Test various ts tranformer classes"""

    @classmethod
    def setUpClass(test_class):
        pass

    @classmethod
    def tearDownClass(test_class):
        pass

    def test_fit_transform_general_transformers(self):
        data = np.array([[1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10]])
        X = data.reshape(-1, 2)
        y = data.reshape(-1, 2)
        X = X.astype(float)
        y = y.astype(float)
        train_size = int(len(X) * 0.8)
        lookback_win = 4
        X_train = X[:train_size]
        y_train = y[:train_size]

        transformers = [
            Flatten,
            WaveletFeatures,
            FFTFeatures,
            SummaryStatistics,
            AdvancedSummaryStatistics,
            HigherOrderStatistics,
            TimeSeriesFeatureUnion,
            RandomTimeSeriesFeatures,
            customTimeSeriesFeatures
        ]

        params = [
            {
                "feature_col_index": [0, 1],
                "target_col_index": [0, 1],
                "lookback_win": lookback_win,
                "pred_win": 1,
            },
            {
                "feature_col_index": [0],
                "target_col_index": [0, 1],
                "lookback_win": lookback_win,
                "pred_win": 1,
            },
            {
                "feature_col_index": [0],
                "target_col_index": [0],
                "lookback_win": lookback_win,
                "pred_win": 1,
            },
            {
                "feature_col_index": [0, 1],
                "target_col_index": [0, 1],
                "lookback_win": lookback_win,
                "pred_win": 3,
            },
            {
                "feature_col_index": [0],
                "target_col_index": [0, 1],
                "lookback_win": lookback_win,
                "pred_win": 3,
            },
            {
                "feature_col_index": [0],
                "target_col_index": [0],
                "lookback_win": lookback_win,
                "pred_win": 3,
            },
        ]

        for est in transformers:
            for param in params:
                print("********************", est, param, "**************************")
                if est == customTimeSeriesFeatures:
                    param["pd_func_list"] = ["mean"]
                    param["func_list"] = ["friedrich_coefficients"]
                estimator = est(**param)
                X_tf, y_tf = estimator.fit(X_train).transform(X_train)
                self.assertEqual(
                    X_tf.shape[0],
                    y_tf.shape[0],
                    "Failed estimator :" + str(est) + str(param),
                )
                self.assertEqual(
                    len(y_tf.shape),
                    2,
                    "Failed estimator :" + str(est) + str(param),
                )
                self.assertEqual(
                    y_tf.shape[1],
                    len(param["target_col_index"]) * param["pred_win"],
                    "Failed estimator :" + str(est) + str(param),
                )

    def test_fit_transform_normal_transformers(self):
        data = np.array([[1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10]])
        X = data.reshape(-1, 2)
        y = data.reshape(-1, 2)
        X = X.astype(float)
        y = y.astype(float)
        train_size = int(len(X) * 0.8)
        lookback_win = 4
        X_train = X[:train_size]
        y_train = y[:train_size]

        transformers = [
            NormalizedFlatten,
            DifferenceNormalizedFlatten,
            DifferenceFlatten,
            LocalizedFlatten
        ]

        params = [
            {
                "feature_col_index": [0, 1],
                "target_col_index": [0, 1],
                "lookback_win": lookback_win,
                "pred_win": 1,
            },
            {
                "feature_col_index": [0],
                "target_col_index": [0],
                "lookback_win": lookback_win,
                "pred_win": 1,
            },
            {
                "feature_col_index": [0, 1],
                "target_col_index": [0, 1],
                "lookback_win": lookback_win,
                "pred_win": 2,
            },
        ]

        for est in transformers:
            for param in params:
                print("********************", est, param, "**************************")
                estimator = est(**param)
                X_tf, y_tf = estimator.fit(X_train).transform(X_train)
                self.assertEqual(
                    X_tf.shape[0],
                    y_tf.shape[0],
                    "Failed estimator :" + str(est) + str(param),
                )
                self.assertEqual(
                    len(y_tf.shape), 2, "Failed estimator :" + str(est) + str(param)
                )
                self.assertEqual(
                    y_tf.shape[1], param["pred_win"], "Failed estimator :" + str(est) + str(param)
                )

    def test_fit_transform_custom_features_transformers(self):
        data = np.array([[1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10]])
        X = data.reshape(-1, 2)
        y = data.reshape(-1, 2)
        X = X.astype(float)
        y = y.astype(float)
        train_size = int(len(X) * 0.8)
        lookback_win = 4
        X_train = X[:train_size]
        y_train = y[:train_size]

        params = [
            {
                "feature_col_index": [0, 1],
                "target_col_index": [0, 1],
                "lookback_win": lookback_win,
                "pred_win": 1,
            },
            {
                "feature_col_index": [0],
                "target_col_index": [0],
                "lookback_win": lookback_win,
                "pred_win": 1,
            }
        ]

        del MAPPING['partial_auto_correlation']

        for func in MAPPING.keys():
            for param in params:
                if func in ["mean", "max", "min", "median", "std", "sum", "count", "skew", "kurt"]:
                    param["pd_func_list"] = [func]
                    param["func_list"] = None
                else:
                    param["pd_func_list"] = None
                    param["func_list"] = [func]
                tf = customTimeSeriesFeatures(**param)
                print("********************", tf, param, "**************************")
                X_tf, y_tf = tf.fit(X_train).transform(X_train)
                self.assertEqual(
                    X_tf.shape[0],
                    y_tf.shape[0],
                    "Failed transformer :" + str(tf) + str(param),
                )
                self.assertEqual(
                    len(y_tf.shape),
                    2,
                    "Failed transformer :" + str(tf) + str(param),
                )

    def test_fit_transform_base_transformers(self):
        data = np.array([[1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10]])
        X = data.reshape(-1, 2)
        y = data.reshape(-1, 2)
        X = X.astype(float)
        y = y.astype(float)
        train_size = int(len(X) * 0.8)
        lookback_win = 4
        X_train = X[:train_size]
        y_train = y[:train_size]

        transformers = [
            RandomTimeTensorTransformer,
            TimeTensorTransformer
        ]

        params = [
            {
                "feature_col_index": [0],
                "target_col_index": [0],
                "lookback_win": lookback_win,
                "pred_win": 1,
            }
        ]

        for est in transformers:
            for param in params:
                print("********************", est, param, "**************************")
                estimator = est(**param)
                X_tf, y_tf = estimator.fit(X_train).transform(X_train)
                self.assertEqual(
                    X_tf.shape[0],
                    y_tf.shape[0],
                    "Failed estimator :" + str(est) + str(param),
                )
                self.assertEqual(
                    len(y_tf.shape), 2, "Failed estimator :" + str(est) + str(param)
                )


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)

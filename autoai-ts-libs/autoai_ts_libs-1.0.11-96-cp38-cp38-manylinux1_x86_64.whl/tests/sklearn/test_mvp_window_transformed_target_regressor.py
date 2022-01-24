################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2020. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################

import unittest
import logging
import numpy as np

logger = logging.getLogger()

from sklearn.datasets import make_regression
from autoai_ts_libs.sklearn.mvp_windowed_transformed_target_estimators import (
    AutoaiWindowTransformedTargetRegressor,
)
from autoai_ts_libs.sklearn.small_data_window_transformers import (
    SmallDataWindowTransformer,
)
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from autoai_ts_libs.sklearn.mvp_windowed_wrapped_regressor import (
    AutoaiWindowedWrappedRegressor,
)

class MVPWindowTransformedTargetRegressorTest(unittest.TestCase):
    def setUp(self):
        X, _ = make_regression(
            n_features=2, n_samples=100, n_informative=1, random_state=0, shuffle=False
        )
        self.X_mv = X
        self.y_mv = X

    def test_mvp_window_transformed_target_regressor_column_subset(self):
        lookback_window=3
        prediction_horizon=2

        steps = [
            ("WTX", SmallDataWindowTransformer(lookback_window=lookback_window)),
            ("imputer", SimpleImputer()),
        ]

        steps.append(
            ("est", AutoaiWindowedWrappedRegressor(regressor=RandomForestRegressor()))
        )

        pipeline = Pipeline(steps=steps)

        mvp = AutoaiWindowTransformedTargetRegressor(
            regressor=pipeline,
            feature_columns=[1],
            target_columns=[1],
            lookback_window=lookback_window,
            prediction_horizon=prediction_horizon,
            time_column=-1,
        )
        f_mvp = mvp.fit(X=self.X_mv, y=self.y_mv)
        self.assertIsNotNone(f_mvp)

        f_mvp.predict(self.X_mv)
        Xp = f_mvp.predict_rowwise_2d(X=self.X_mv)
        self.assertEqual(Xp.shape[0], self.X_mv.shape[0])
        self.assertEqual(Xp.shape[1], prediction_horizon)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()

""" Test T2RForecaster """
import unittest
import pandas as pd
import numpy as np
from autoai_ts_libs.srom.estimators.time_series.models.T2RForecaster import T2RForecaster


class TestT2RForecaster(unittest.TestCase):
    """ class for testing T2RForecaster """

    @classmethod
    def setUp(cls):
        X = np.arange(30)
        X = X.reshape(-1, 1)
        cls.X = X

    def test_fit(self):
        """ method for testing the fit method of T2RForecaster"""
        test_class = self.__class__
        model = T2RForecaster()
        fitted_model = model.fit(test_class.X)
        self.assertEqual(fitted_model, model)

    def test_predict(self):
        """ Tests the predict method of T2RForecaster"""
        test_class = self.__class__
        model = T2RForecaster()
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict(prediction_win=1)
        self.assertEqual(len(ypred), 1)
        model = T2RForecaster()
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict()
        self.assertEqual(len(ypred), 12)
        model = T2RForecaster(trend='Mean')
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict()
        self.assertEqual(len(ypred), 12)
        model = T2RForecaster(trend='Poly')
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict()
        self.assertEqual(len(ypred), 12)

    def test_predict_sliding_window(self):
        """ The tests the sliding window method of T2RForecaster"""
        test_class = self.__class__
        model = T2RForecaster()
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict_sliding_window(test_class.X[test_class.X.shape[0] - 5:])
        self.assertEqual(len(ypred), 5)

    def test_predict_multi_step_sliding_window(self):
        """ The tests predict_multi_step_sliding_window method of T2RForecaster"""
        test_class = self.__class__
        model = T2RForecaster()
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict_multi_step_sliding_window(test_class.X[test_class.X.shape[0] - 5:], 3)
        self.assertEqual(len(ypred), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)

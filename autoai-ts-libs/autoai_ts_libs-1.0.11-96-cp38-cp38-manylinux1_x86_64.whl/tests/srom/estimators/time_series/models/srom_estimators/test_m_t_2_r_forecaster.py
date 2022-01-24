""" Test MT2RForecaster """
import unittest
import pandas as pd
import numpy as np
from autoai_ts_libs.srom.estimators.time_series.models.MT2RForecaster import MT2RForecaster


class TestMT2RForecaster(unittest.TestCase):
    """ class for testing MT2RForecaster """

    @classmethod
    def setUp(cls):
        x = np.arange(30)
        y = np.arange(300, 330)
        X = np.array([x, y])
        X = np.transpose(X)
        cls.target_columns = [0, 1]
        cls.X = X

    def test_fit(self):
        """ method for testing the fit method of MT2RForecaster"""
        test_class = self.__class__
        model = MT2RForecaster(target_columns=test_class.target_columns)
        fitted_model = model.fit(test_class.X)
        self.assertEqual(fitted_model, model)

    def test_predict_multicols(self):
        """ Tests the multivariate predict method of MT2RForecaster"""
        test_class = self.__class__
        model = MT2RForecaster(target_columns=test_class.target_columns, prediction_win=2)
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict()
        self.assertEqual(len(ypred), 2)
        model = MT2RForecaster(target_columns=test_class.target_columns, prediction_win=1)
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict()
        self.assertEqual(len(ypred), 1)
        model = MT2RForecaster(target_columns=test_class.target_columns, trend='Mean')
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict()
        self.assertEqual(len(ypred), 12)
        model = MT2RForecaster(target_columns=test_class.target_columns, trend='Poly')
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict()
        self.assertEqual(len(ypred), 12)

    def test_predict_prob(self):
        """ Tests predict_prob method of MT2RForecaster"""
        test_class = self.__class__
        model = MT2RForecaster(target_columns=[0], prediction_win=2)
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict_proba()
        self.assertEqual(ypred.shape, (2, 1, 2))
        model = MT2RForecaster(target_columns=[0, 1], prediction_win=2)
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict_proba()
        self.assertEqual(ypred.shape, (2, 2, 2))

    def test_predict_uni_cols(self):
        """ Tests the univariate predict method of MT2RForecaster"""
        test_class = self.__class__
        x = np.arange(10)
        X = x.reshape(-1, 1)
        model = MT2RForecaster(target_columns=[0], prediction_win=2)
        fitted_model = model.fit(X)
        ypred = fitted_model.predict()
        self.assertEqual(len(ypred), 2)
        model = MT2RForecaster(target_columns=[0], prediction_win=1)
        fitted_model = model.fit(X)
        ypred = fitted_model.predict()
        self.assertEqual(len(ypred), 1)

    def test_predict_multi_step_sliding_window(self):
        """ The tests multivariate predict_multi_step_sliding_window method of MT2RForecaster"""
        test_class = self.__class__
        model = MT2RForecaster(target_columns=test_class.target_columns)
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict_multi_step_sliding_window(test_class.X[test_class.X.shape[0] - 5:], 3)
        self.assertEqual(len(ypred), 9)
        self.assertEqual(ypred.shape[1], 2)

    def test_predict_sliding_window(self):
        """ The tests multivariate predict_multi_step_sliding_window method of MT2RForecaster"""
        test_class = self.__class__
        model = MT2RForecaster(target_columns=test_class.target_columns)
        fitted_model = model.fit(test_class.X)
        ypred = fitted_model.predict_sliding_window(test_class.X[test_class.X.shape[0] - 5:])
        self.assertEqual(len(ypred), 5)
        self.assertEqual(ypred.shape[1], 2)

    def test_predict_uni_multi_step_sliding_window(self):
        """ The tests univariate predict_multi_step_sliding_window method of MT2RForecaster"""
        test_class = self.__class__
        x = np.arange(30)
        X = x.reshape(-1, 1)
        model = MT2RForecaster(target_columns=[0])
        fitted_model = model.fit(X)
        ypred = fitted_model.predict_multi_step_sliding_window(X[X.shape[0] - 5:], 2)
        self.assertEqual(len(ypred), 8)
        self.assertEqual(ypred.shape[1], 1)

    def test_predict_uni_sliding_window(self):
        """ The tests univariate predict_sliding_window method of MT2RForecaster"""
        test_class = self.__class__
        x = np.arange(30)
        X = x.reshape(-1, 1)
        model = MT2RForecaster(target_columns=[0])
        fitted_model = model.fit(X)
        ypred = fitted_model.predict_sliding_window(X[X.shape[0] - 5:])
        self.assertEqual(len(ypred), 5)
        self.assertEqual(ypred.shape[1], 1)

    def test_lookback_window(self):
        """ Tests the lookback_window attribute of MT2RForecaster"""
        test_class = self.__class__
        
        ## Tests for multivariate
        model = MT2RForecaster(target_columns=test_class.target_columns, prediction_win=2)
        self.assertEqual("auto",model.lookback_window)

        fitted_model = model.fit(test_class.X)
        self.assertEqual(5,fitted_model.lookback_window)
        
        model = MT2RForecaster(target_columns=test_class.target_columns, prediction_win=2,lookback_win=7)
        fitted_model = model.fit(test_class.X)
        self.assertEqual(7,fitted_model.lookback_window)
        
        ## Tests for univariate
        model = MT2RForecaster(target_columns=[0], prediction_win=2)
        self.assertEqual("auto",model.lookback_window)
        
        fitted_model = model.fit(test_class.X)
        self.assertEqual(5,fitted_model.lookback_window)
        
        model = MT2RForecaster(target_columns=[0], prediction_win=2,lookback_win=7)
        fitted_model = model.fit(test_class.X)
        self.assertEqual(7,fitted_model.lookback_window)

        ##Check for exception
        with self.assertRaises(Exception):
            MT2RForecaster(target_columns=test_class.target_columns, prediction_win=2,lookback_win=[1,2])


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)

import unittest
import numpy as np
from ..xstats import *
from ..xchecks import *


class TestXStats(unittest.TestCase):
    def test_x_model_pred_stats(self):
        y_true = np.ones(5)
        y_pred = np.linspace(0.75, .95, len(y_true))
        y_alt = 0.8
        s1 = x_model_pred_stats(y_true, y_pred, y_alt)
        self.assertIsNone(s1.p_value_err_normal)

        y_true = np.ones(20)
        y_pred = np.linspace(0.75, .95, len(y_true))
        y_alt = 0.8
        s2 = x_model_pred_stats(y_true, y_pred, y_alt, k=1)
        s3 = x_model_pred_stats(y_true, y_pred, y_alt, k=5)

        self.assertGreater(s1.p_value, s2.p_value)
        self.assertGreater(s2.r2_adj, s3.r2_adj)
        self.assertIsNotNone(s2.p_value_err_normal)

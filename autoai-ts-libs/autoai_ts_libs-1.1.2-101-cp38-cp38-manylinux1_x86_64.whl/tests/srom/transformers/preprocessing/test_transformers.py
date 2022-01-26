import unittest
import pandas as pd
import numpy as np
from autoai_ts_libs.srom.transformers.preprocessing.ts_transformer import (
    Flatten,
    NormalizedFlatten,
    DifferenceNormalizedFlatten,
    DifferenceFlatten,
)


class TestTransformers(unittest.TestCase):
    """Test various ts tranformer classes"""

    @classmethod
    def setUpClass(test_class):
        pass

    @classmethod
    def tearDownClass(test_class):
        pass

    def test_flatten_transform(self):
        data = pd.DataFrame([2, 3, 5, 8, 13, 21, 34, 55, 89, 144])
        X = data.to_numpy()
        X = X.reshape(-1, 1)
        a = Flatten(feature_col_index=[0], target_col_index=[0], lookback_win=5, pred_win=1)
        a.fit(X)
        out = a.transform(X)
        out1 = np.array([[2, 3, 5, 8, 13],
                         [3, 5, 8, 13, 21],
                         [5, 8, 13, 21, 34],
                         [8, 13, 21, 34, 55],
                         [13, 21, 34, 55, 89]])
        out2 = np.array([[21],
                         [34],
                         [55],
                         [89],
                         [144]])
        self.assertEqual(np.allclose(out[0], out1), True)
        self.assertEqual(np.allclose(out[1], out2), True)

    def test_normalized_flatten_transform(self):
        data = pd.DataFrame([2, 3, 5, 8, 13, 21, 34, 55, 89, 144])
        X = data.to_numpy()
        X = X.reshape(-1, 1)
        a = NormalizedFlatten(feature_col_index=[0], target_col_index=[0], lookback_win=5, pred_win=1)
        a.fit(X)
        out = a.transform(X)
        out1 = np.array([[-1.05796472, -0.80606835, -0.30227563, 0.45341345, 1.71289525],
                         [-1.08530393, -0.77521709, -0.31008684, 0.46513025, 1.7054776],
                         [-1.07493723, -0.78700762, -0.30712492, 0.46068738, 1.70838239],
                         [-1.07890812, -0.78250479, -0.30825946, 0.46238919, 1.70728318],
                         [-1.077393, -0.78422484, -0.30782657, 0.46173986, 1.70770455]])
        out2 = np.array([[3.72806614],
                         [3.72104204],
                         [3.72388969],
                         [3.72282582],
                         [3.72323567]])
        self.assertEqual(np.allclose(out[0], out1), True)
        self.assertEqual(np.allclose(out[1], out2), True)

    def test_difference_flatten_transform(self):
        data = pd.DataFrame([2, 3, 5, 8, 13, 21, 34, 55, 89, 144])
        X = data.to_numpy()
        X = X.reshape(-1, 1)
        a = DifferenceFlatten(feature_col_index=[0], target_col_index=[0], lookback_win=5, pred_win=1)
        a.fit(X)
        out = a.transform(X)
        out1 = np.array([[1, 2, 3, 5],
                         [2, 3, 5, 8],
                         [3, 5, 8, 13],
                         [5, 8, 13, 21],
                         [8, 13, 21, 34]])
        out2 = np.array([[8],
                         [13],
                         [21],
                         [34],
                         [55]])
        self.assertEqual(np.allclose(out[0], out1), True)
        self.assertEqual(np.allclose(out[1], out2), True)

    def test_difference_normalized_flatten_transform(self):
        data = pd.DataFrame([2, 3, 5, 8, 13, 21, 34, 55, 89, 144])
        X = data.to_numpy()
        X = X.reshape(-1, 1)
        a = DifferenceNormalizedFlatten(feature_col_index=[0], target_col_index=[0], lookback_win=5, pred_win=1)
        a.fit(X)
        out = a.transform(X)
        out1 = np.array([[-1.18321596, -0.50709255, 0.16903085, 1.52127766],
                         [-1.09108945, -0.65465367, 0.21821789, 1.52752523],
                         [-1.12832963, -0.59735098, 0.19911699, 1.52656362],
                         [-1.11440926, -0.61911626, 0.20637209, 1.52715344],
                         [-1.11977052, -0.61078392, 0.20359464, 1.5269598]])
        out2 = np.array([[3.54964787],
                         [3.70970413],
                         [3.65047821],
                         [3.67342313],
                         [3.66470351]])
        self.assertEqual(np.allclose(out[0], out1), True)
        self.assertEqual(np.allclose(out[1], out2), True)


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)

import unittest

import numpy as np
from zeef.util.data_util import flatten_data


class TestDataUtil(unittest.TestCase):

    def test_flatten_data(self):
        test_arr = np.array([np.ones(10), np.zeros(10)])
        flatten_test_data = flatten_data(test_arr)
        np.testing.assert_allclose(test_arr, flatten_test_data)
        test_arr_hd = np.random.randint(5, size=(8, 8, 8, 8))
        flatten_test_hd = flatten_data(test_arr_hd)
        self.assertEqual((8, 512), flatten_test_hd.shape)
        self.assertEqual(8, flatten_test_hd.shape[0])
        self.assertEqual(8 * 8 * 8, flatten_test_hd.shape[1])


if __name__ == '__main__':
    unittest.main()

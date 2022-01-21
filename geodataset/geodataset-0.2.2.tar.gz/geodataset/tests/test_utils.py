import unittest

import numpy as np

from geodataset.utils import fill_nan_gaps


class TestsUtils(unittest.TestCase):
    def test_fill_nan_gaps(sefl):
        a = np.array(
            [[np.nan,np.nan,3],[np.nan,5,6],[7,8,9]], float)
        b = fill_nan_gaps(a)
        np.testing.assert_array_equal(b,
            np.array([[5,5,3],[7,5,6],[7,8,9]], float)
        )


if __name__ == "__main__":
    unittest.main()

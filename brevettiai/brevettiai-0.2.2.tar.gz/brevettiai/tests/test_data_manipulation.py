import unittest

import numpy as np
from brevettiai.data.image.utils import tile2d


class TestDataManipulation(unittest.TestCase):
    def test_tile2d(self):
        for tiles in [(4,3), (4,4),(4,5)]:
            data = np.random.random((4,10,16,2))
            b, x, y, c = data.shape
            out = tile2d(data, tiles)

            self.assertEqual(out.shape, (x*tiles[0], y*tiles[1], c), "check ouput shape")

            b_ = 0
            for x_ in np.arange(tiles[0])*x:
                for y_ in np.arange(tiles[1])*y:
                    if b_ < b:
                        np.testing.assert_equal(out[x_:x_+x, y_:y_+y], data[b_], "Data should match")
                    else:
                        np.testing.assert_equal(out[x_:x_+x, y_:y_+y], np.zeros_like(b_), "Excess should be zeros")
                    b_ += 1


if __name__ == '__main__':
    unittest.main()

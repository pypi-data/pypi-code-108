import unittest
from numpy.testing import assert_array_almost_equal, assert_allclose
import numpy, random


class RandomNumberGeneratorTests(unittest.TestCase):

    def test_jsf32_randomgen(self):
        from meadows.rng import RandomNumberGenerator
        rng = RandomNumberGenerator(engine='randomgen')
        assert_array_almost_equal(rng.random(4, 0), [
                0.10393405123613775,
                0.6028600085992366,
                0.9420762336812913,
                0.035197859862819314,
            ],
            decimal=12
        )

    def test_jsf32_pure_python(self):
        from meadows.rng import RandomNumberGenerator
        rng = RandomNumberGenerator(engine='python')
        assert_array_almost_equal(rng.random(4, 0), [
                0.10393405123613775,
                0.6028600085992366,
                0.9420762336812913,
                0.035197859862819314,
            ],
            decimal=12
        )

    def test_sample_indices_fixed_seed(self):
        from meadows.rng import RandomNumberGenerator
        rng = RandomNumberGenerator(engine='randomgen')
        idx = rng.sample_indices(pop_size=1000, n=7, seed=0)
        self.assertEqual(idx, [103, 603, 942, 35, 130, 512, 47])

    def test_sample_indices_will_not_sample_more_than_pop_size(self):
        from meadows.rng import RandomNumberGenerator
        rng = RandomNumberGenerator()
        idx = rng.sample_indices(pop_size=10, n=12, seed=0)
        self.assertEqual(len(idx), 10)

    def test_sample_indices_is_uniform(self):
        from meadows.rng import RandomNumberGenerator
        rng = RandomNumberGenerator(engine='randomgen')
        chosen_count = numpy.zeros([10,])
        s = 100*1000
        for _ in range(s):
            seed = random.randint(294967296, 4294967296)
            idx = rng.sample_indices(pop_size=10, n=5, seed=seed)
            chosen_count[idx] += 1
        assert_allclose(
            chosen_count,
            numpy.ones([10,])*(s/2),
            rtol=0.01
        )

    def test_sample_indices_are_always_unique(self):
        from meadows.rng import RandomNumberGenerator
        rng = RandomNumberGenerator(engine='randomgen')
        s = 1000
        for _ in range(s):
            seed = random.randint(294967296, 4294967296)
            idx = rng.sample_indices(pop_size=10, n=5, seed=seed)
            self.assertEqual(len(idx), len(set(idx)))

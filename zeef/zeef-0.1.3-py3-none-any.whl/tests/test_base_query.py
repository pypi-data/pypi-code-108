import unittest

from zeef.data import Pool
from zeef.strategy import RandomSampling


class TestQuery(unittest.TestCase):
    @staticmethod
    def large_query():
        raw_data = [1] * 100
        pool = Pool(raw_data)
        pool.label_by_ids([0], [0])
        query_num = 101
        strategy = RandomSampling(pool, learner=None)
        strategy.query(query_num)

    def test_query_number(self):
        self.assertRaises(ValueError, self.large_query)


if __name__ == '__main__':
    unittest.main()

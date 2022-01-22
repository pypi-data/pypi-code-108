# -*- coding: utf-8 -*-
import unittest
from context import Resto, RequestError


class TestResto(unittest.TestCase):
    def setUp(self) -> None:
        self.resto1 = Resto('Louvain-la-Neuve')
        self.resto2 = Resto('Genappe')
        self.resto3 = Resto('nimportekoi')

    def test_url(self):
        self.assertEqual(Resto('Louvain-la-Neuve').url_origin,
                         "https://nominatim.openstreetmap.org/search?osmtype=N&addressdetails"
                         "=1&q=restaurant+Louvain-la-Neuve&format=json")
        self.assertEqual(Resto('Genappe').url_origin,
                         "https://nominatim.openstreetmap.org/search?osmtype=N&addressdetails"
                         "=1&q=restaurant+Genappe&format=json")

    def test_get_resto(self):
        self.assertRaises(RequestError, self.resto3.get_resto)
        # self.assertEqual(len(Resto('Genappe').get_resto()), 652) #599--66


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
import unittest
from context import Cine, RequestError


class TestCine(unittest.TestCase):
    def setUp(self) -> None:
        self.cine1 = Cine('Louvain-la-Neuve')
        self.cine2 = Cine('Rixensart')
        self.cine3 = Cine('patate')

    def test_url(self):
        self.assertEqual(Cine('Louvain-la-Neuve').url_origin,
                         "https://nominatim.openstreetmap.org/search?osmtype=N&addressdetails"
                         "=1&q=cinema+Louvain-la-Neuve&format=json", "Mauvais lien")
        self.assertEqual(Cine('Namur').url_origin,
                         "https://nominatim.openstreetmap.org/search?osmtype=N&addressdetails"
                         "=1&q=cinema+Namur&format=json", "Mauvais lien")

    def test_get_cine(self):
        # self.assertRaises(RequestError, self.cine3.get_cine)
        self.assertEqual(len(self.cine2.get_cine()), 83)


if __name__ == '__main__':
    unittest.main()


# -*- coding: utf-8 -*-
from unittest import TestCase
import unittest
# from Module.itinerary.itinerary import Itinerary, ParameterException
from context import Itinerary, ParameterException


class TestItinerary(TestCase):
    def setUp(self) -> None:
        self.itinerary_lln_ottignies = Itinerary(destination_address="ottignies")

        self.itinerary_bruxelle_namur = Itinerary("bruxelle", "namur")

    def test_init(self):
        self.assertRaises(ParameterException, Itinerary, "", "")
        self.assertEqual(self.itinerary_lln_ottignies.origin_address, "louvain-la-neuve")
        self.assertEqual(self.itinerary_bruxelle_namur.destination_address, "namur")

    def test_url_address_origin(self):
        self.assertEqual(self.itinerary_lln_ottignies.url_address_origin,
                         'https://nominatim.openstreetmap.org/search/louvain-la-neuve?format=json', "Mauvais lien")
        self.assertEqual(self.itinerary_bruxelle_namur.url_address_origin,
                         'https://nominatim.openstreetmap.org/search/bruxelle?format=json', "Mauvais Lien")

    def test_url_address_destination(self):
        self.assertEqual(self.itinerary_lln_ottignies.url_address_destination,
                         'https://nominatim.openstreetmap.org/search/ottignies?format=json', "Mauvais lien")
        self.assertEqual(self.itinerary_bruxelle_namur.url_address_destination,
                         'https://nominatim.openstreetmap.org/search/namur?format=json', "Mauvais Lien")

    def test_process_request(self):
        # self.assertEqual(itinerary_lln_ottignies)
        self.assertIsNone(
            self.itinerary_lln_ottignies.process_request("4.6128839", "50.6682012", "4.5690502", "50.666357"))

    def test_get_itinerary(self):
        self.assertEqual(len(self.itinerary_lln_ottignies.get_itinerary()), 1201)
        self.assertEqual(len(self.itinerary_bruxelle_namur.get_itinerary()), 7170)


if __name__ == "__main__":
    unittest.main()

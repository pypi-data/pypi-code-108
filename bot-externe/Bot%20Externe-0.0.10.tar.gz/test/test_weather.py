# -*- coding: utf-8 -*-
import unittest
# from Module.weather.weather import *
from context import Weather


class TestWeather(unittest.TestCase):
    def setUp(self) -> None:
        self.weather1 = Weather()
        self.weather2 = Weather("Brussel")
        self.weather3 = Weather()
        self.weather3.api_link = "lienDown"

    def test__init__(self):
        self.assertEqual(self.weather1.api_link,
                         'http://api.weatherstack.com/current?access_key=4c53b8fcf4818536539b668a0247408c&query'
                         '=louvain-la-neuve')
        self.assertEqual(self.weather2.api_link,
                         'http://api.weatherstack.com/current?access_key=4c53b8fcf4818536539b668a0247408c&query'
                         '=Brussel')

    def test_get_weather(self):
        list_weather1 = self.weather1.get_weather().split(' ')
        self.assertEqual(list_weather1[3], 'louvain-la-neuve')
        list_weather2 = self.weather2.get_weather().split(' ')
        self.assertEqual(list_weather2[3], 'Brussel')
        self.assertEqual(self.weather3.get_weather(), 'Erreur dans le get')


if __name__ == '__main__':
    unittest.main()

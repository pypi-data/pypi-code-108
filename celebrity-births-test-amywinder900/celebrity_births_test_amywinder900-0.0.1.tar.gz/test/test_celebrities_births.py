import unittest
from celebrities_births import Date

class CelebrityBirthsTestCase(unittest.TestCase):
    def setUp(self):
        self.date = Date()


    def test_date_valid(self):
        self.assertRaises(ValueError)


t=(1)

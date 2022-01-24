from unittest import TestCase

from extools import success

class TestExTools(TestCase):

    def test_success(self):
       good = [0, 0, 0]
       bad = [0, 0, 1]

       self.assertTrue(success(0))
       self.assertTrue(not success(1))
       self.assertTrue(success(*good))
       self.assertTrue(not success(*bad))

from unittest import TestCase

class UtilityTest(TestCase):

    def test_iter(self):
        result = [({'test': 1, 'd': 0}, ())]
        for a, b in result:
            self.assertTrue(True)
            print(f'a: {a}, b: {b}')
        self.assertTrue(True)

import ComputationalGraphPrimer
import os
import unittest

class TestInstanceCreation(unittest.TestCase):

    def setUp(self):
        self.cgp = ComputationalGraphPrimer.ComputationalGraphPrimer(expressions = ['xy=ab*xa'],
                                                   dataset_size= 10,
                                                  )

    def test_instance_creation(self):
        print("testing instance creation")
        self.cgp.parse_expressions()
        ind_var = list(self.cgp.independent_vars)[0]
        self.assertEqual(ind_var, 'xa')

def getTestSuites(type):
    return unittest.TestSuite([
            unittest.makeSuite(TestInstanceCreation, type)
                             ])                    
if __name__ == '__main__':
    unittest.main()


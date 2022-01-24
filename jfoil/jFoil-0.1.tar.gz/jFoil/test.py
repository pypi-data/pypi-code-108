import unittest as ut
from jFoil import *

class JFoilTest(ut.TestCase):

    def setUp(self):
        self.test_foil = jFoil(1, 0.9, 5, n=50)

    def testPlotFoil(self):
        self.test_foil.plotFoil()

    def testSaveFoil(self):
        pass
    
    def testPlotCl(self):
        self.test_foil.plotCl()

if __name__ == '__main__':
    ut.main()

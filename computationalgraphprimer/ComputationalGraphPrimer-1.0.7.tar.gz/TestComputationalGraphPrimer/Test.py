#!/usr/bin/env python

import unittest
import TestInstanceCreation

class ComputationalGraphPrimerTestCase( unittest.TestCase ):
    def checkVersion(self):
        import ComputationalGraphPrimer

testSuites = [unittest.makeSuite(ComputationalGraphPrimerTestCase, 'test')] 

for test_type in [
            TestInstanceCreation
    ]:
    testSuites.append(test_type.getTestSuites('test'))


def getTestDirectory():
    try:
        return os.path.abspath(os.path.dirname(__file__))
    except:
        return '.'

import os
os.chdir(getTestDirectory())

runner = unittest.TextTestRunner()
runner.run(unittest.TestSuite(testSuites))

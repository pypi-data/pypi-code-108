#!/usr/bin/env python3
import unittest
from dlpoly.output import Output
import numpy as np


class OutputTest(unittest.TestCase):

    def setUp(self):
        self.output = OutputTest.output

    @classmethod
    def setUpClass(cls):
        super(OutputTest, cls).setUpClass()
        cls.output = Output(source="tests/OUTPUT")

    def test_output_vdw(self):
        self.assertEqual(self.output.vdwEnergy, -0.298721E+04,
                         'incorrect lrc correction energy')

    def test_output_pres(self):
        self.assertAlmostEqual(self.output.pressure, 1.1103E+01,
                               msg="incorrect pressure", delta=0.1)

    def test_output_steps(self):
        self.assertEqual(self.output.steps, 20,
                         'incorrect number of steps')

    def test_output_avcell(self):
        cell = np.array([[112.3847796072, 0.0, 0.0], [0.0, 94.3222490199, 0.0], [0.0, 0.0, 94.2720855812]])
        assert np.allclose(self.output.averageCell, cell)

    def test_output_diff(self):
        self.assertEqual(self.output.diffusion['O'], (4.3873E-02, 1.8640E-02),
                         'incorrect diffusion for oxygen')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(OutputTest('test_output_vdw'))
    suite.addTest(OutputTest('test_output_steps'))
    suite.addTest(OutputTest('test_output_avcell'))
    suite.addTest(OutputTest('test_output_diff'))
    suite.addTest(OutputTest('test_output_pres'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

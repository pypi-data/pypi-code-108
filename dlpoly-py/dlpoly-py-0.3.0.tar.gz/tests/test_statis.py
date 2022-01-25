#!/usr/bin/env python3
import unittest
from dlpoly.statis import Statis


class StatisTest(unittest.TestCase):

    def setUp(self):
        self.statis = StatisTest.statis

    @classmethod
    def setUpClass(cls):
        super(StatisTest, cls).setUpClass()
        cls.statis = Statis(source="tests/STATIS")

    def test_statis_ncolumns(self):
        self.assertEqual(self.statis.columns, 68,
                         'incorrect number of columns')

    def test_statis_nrows(self):
        self.assertEqual(self.statis.rows, 5,
                         'incorrect number of rows')

    def test_statis_steptime(self):
        self.assertListEqual(list(self.statis.data[1, 0:2]),
                             [5, 1.750000E-03],
                             'incorrect cell time/step')

    def test_statis_temperature(self):
        self.assertEqual(self.statis.data[2, 4], 3.000000E+02,
                         'incorrect temperature')

    def test_statis_pressure(self):
        self.assertEqual(self.statis.data[3, 29], 1.170673E+01,
                         'incorrect pressure')

    def test_statis_vpmf(self):
        self.assertEqual(self.statis.data[1, 28], 0.000000E+00,
                         'incorrect virial pmf')

    def test_statis_consQ(self):
        self.assertEqual(self.statis.data[4, 3], 6.565874E+04,
                         'incorrect conserved quantity')

    def test_statis_energies(self):
        self.assertListEqual(list(self.statis.data[2, 5:13]),
                             [float(i) for i in '''6.022616E+03  8.482584E+04
                             -4.086941E+05  1.121753E+04  3.073748E+05  1.129854E+04
                             0.000000E+00  6.577677E+04'''.split()],
                             'incorrect energy terms')

    def test_statis_virial(self):
        self.assertListEqual(list(self.statis.data[1, 14:21]),
                             [float(i) for i in '''-6.506158E+03 -1.808586E+06
                                 4.084056E+05  3.127625E+05  0.000000E+00
                                 1.080912E+06  0.000000E+00'''.split()],
                             'incorrect virial terms')

    def test_statis_angles(self):
        self.assertListEqual(list(self.statis.data[1, 25:28]),
                             [90.0, 90.0, 90.0],
                             'incorrect angles')

    def test_statis_volume(self):
        self.assertEqual(self.statis.data[4, 21], 9.993474E+05,
                         'incorrect volume')

    def test_statis_stress(self):
        self.assertListEqual(list(self.statis.data[4, 31:40]),
                             [float(i) for i in '''8.060310E+00 -2.636976E+00
                              -1.941572E+00 -2.636976E+00  2.316919E+01
                              4.915622E-01 -1.941572E+00  4.915622E-01
                              2.080145E+01'''.split()],
                             'incorrect stress')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(StatisTest('test_statis_ncolumns'))
    suite.addTest(StatisTest('test_statis_nrows'))
    suite.addTest(StatisTest('test_statis_steptime'))
    suite.addTest(StatisTest('test_statis_temperature'))
    suite.addTest(StatisTest('test_statis_pressure'))
    suite.addTest(StatisTest('test_statis_consQ'))
    suite.addTest(StatisTest('test_statis_vpmf'))
    suite.addTest(StatisTest('test_statis_energies'))
    suite.addTest(StatisTest('test_statis_volume'))
    suite.addTest(StatisTest('test_statis_virial'))
    suite.addTest(StatisTest('test_statis_angles'))
    suite.addTest(StatisTest('test_statis_stress'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

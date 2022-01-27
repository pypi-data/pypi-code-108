#!/usr/bin/env python3
import unittest
from dlpoly.statis import Statis


class StatisTest(unittest.TestCase):

    def setUp(self):
        self.statis = StatisTest.statis

    @classmethod
    def setUpClass(cls):
        super(StatisTest, cls).setUpClass()
        cls.statis = Statis(source="tests/statis.yml")

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
        self.assertEqual(self.statis.data[2, 3], 3.000000E+02,
                         'incorrect temperature')

    def test_statis_pressure(self):
        self.assertAlmostEqual(self.statis.data[3, 28], 1.170673E+01,
                               msg='incorrect pressure',
                               delta=0.0001)

    def test_statis_vpmf(self):
        self.assertEqual(self.statis.data[1, 27], 0.000000E+00,
                         'incorrect virial pmf')

    def test_statis_consQ(self):
        self.assertAlmostEqual(self.statis.data[4, 2], 6.565874E+04,
                               msg='incorrect conserved quantity',
                               delta=0.01)

    def test_statis_energies(self):
        ref = list(self.statis.data[2, 4:12])
        d = [float(i) for i in '''6.022616E+03  8.482584E+04
             -4.086941E+05  1.121753E+04  3.073748E+05  1.129854E+04
              0.000000E+00  6.577677E+04'''.split()]
        for i in range(len(d)):
            self.assertAlmostEqual(ref[i], d[i],
                                   msg='incorrect energy terms',
                                   delta=0.1)

    def test_statis_virial(self):
        ref = list(self.statis.data[1, 13:20])
        d = [float(i) for i in '''-6.506158E+03 -1.808586E+06
             4.084056E+05  3.127625E+05  0.000000E+00
             1.080912E+06  0.000000E+00'''.split()]
        for i in range(len(d)):
            self.assertAlmostEqual(ref[i], d[i],
                                   msg='incorrect virial terms',
                                   delta=0.4)

    def test_statis_angles(self):
        self.assertListEqual(list(self.statis.data[1, 24:27]),
                             [90.0, 90.0, 90.0],
                             'incorrect angles')

    def test_statis_volume(self):
        self.assertAlmostEqual(self.statis.data[4, 20], 9.993474E+05,
                               msg='incorrect volume', delta=0.1)

    def test_statis_stress(self):
        d = [float(i) for i in '''8.060310E+00 -2.636976E+00
             -1.941572E+00 -2.636976E+00  2.316919E+01
              4.915622E-01 -1.941572E+00  4.915622E-01
              2.080145E+01'''.split()]
        ref = list(self.statis.data[4, 30:39])
        for i in range(len(d)):
            self.assertAlmostEqual(ref[i], d[i],
                                   msg='incorrect stress',
                                   delta=0.01)


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

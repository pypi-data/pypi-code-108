#!/usr/bin/env python3
import unittest
from dlpoly.msd import msd


class MSDTest(unittest.TestCase):

    def setUp(self):
        self.msd = MSDTest.msd

    @classmethod
    def setUpClass(cls):
        super(MSDTest, cls).setUpClass()
        cls.msd = msd(source="tests/MSDTMP")

    def test_msd_init(self):
        self.assertEqual(self.msd.nAtoms, 99120,
                         'incorrect number of atoms')
        self.assertEqual(self.msd.nFrames, 3,
                         'incorrect number of frames')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(MSDTest('test_msd_init'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

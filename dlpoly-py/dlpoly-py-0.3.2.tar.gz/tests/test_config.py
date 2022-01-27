#!/usr/bin/env python3
import dlpoly as dlp
import unittest


class ConfigTest(unittest.TestCase):

    def setUp(self):
        self.config = ConfigTest.config

    @classmethod
    def setUpClass(cls):
        super(ConfigTest, cls).setUpClass()
        cls.config = dlp.DLPoly(config="tests/CONFIG").config

    def test_config_natoms(self):
        self.assertEqual(self.config.natoms, 99120,
                         'incorrect number of atoms')

    def test_config_level(self):
        self.assertEqual(self.config.level, 2,
                         'incorrect level')

    def test_config_pbc(self):
        self.assertEqual(self.config.pbc, 2,
                         'incorrect pbc')

    def test_config_cell(self):
        self.assertListEqual(list(self.config.cell[0, :]),
                             [112.3843994140, 0.0, 0.0],
                             'incorrect cell a')
        self.assertListEqual(list(self.config.cell[1, :]),
                             [0.0, 94.3219299316, 0.0],
                             'incorrect cell b')
        self.assertListEqual(list(self.config.cell[2, :]),
                             [0.0, 0.0, 94.2717666626],
                             'incorrect cell c')

    def test_config_atom(self):
        self.assertEqual(self.config.atoms[100].element, 'CK',
                         'incorrect element')
        self.assertEqual(self.config.atoms[100].index, 101,
                         'incorrect index')
        self.assertListEqual(list(self.config.atoms[100].pos),
                             [-46.97998686, 8.725645151, -46.70341089],
                             'incorrect positions')
        self.assertListEqual(list(self.config.atoms[100].vel),
                             [6.067870998, -6.202633836, -4.581153286],
                             'incorrect veloctities')
        self.assertListEqual(list(self.config.atoms[100].forces),
                             [-114729.0839, 191994.0141, -110473.8008],
                             'incorrect forces')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(ConfigTest('test_config_natoms'))
    suite.addTest(ConfigTest('test_config_level'))
    suite.addTest(ConfigTest('test_config_pbc'))
    suite.addTest(ConfigTest('test_config_cell'))
    suite.addTest(ConfigTest('test_config_atom'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

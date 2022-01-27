#!/usr/bin/env python3
import unittest
import dlpoly as dlp


class FieldTest(unittest.TestCase):

    def setUp(self):
        self.field = FieldTest.field

    @classmethod
    def setUpClass(cls):
        super(FieldTest, cls).setUpClass()
        cls.field = dlp.DLPoly(field="tests/FIELD").field

    def test_field_units(self):
        self.assertEqual(self.field.units, "kcal",
                         'incorrect units')

    def test_field_mol(self):
        self.assertEqual(self.field.molecules['Gramicidin A'].nMols, 8,
                         'incorrect number of gramidicin')
        self.assertEqual(self.field.molecules['Gramicidin A'].nAtoms, 354,
                         'incorrect number of atoms in gramidicin')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(FieldTest('test_field_units'))
    suite.addTest(FieldTest('test_field_mol'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

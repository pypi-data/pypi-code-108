#!/usr/bin/env python3
import unittest
from dlpoly.rdf import rdf


class RDFTest(unittest.TestCase):

    def setUp(self):
        self.rdf = RDFTest.rdf

    @classmethod
    def setUpClass(cls):
        super(RDFTest, cls).setUpClass()
        cls.rdf = rdf(source="tests/RDFDAT.yml")

    def test_rdf_nrdf(self):
        self.assertEqual(self.rdf.nRDF, 190,
                         'incorrect number of rdfs')

    def test_rdf_npoints(self):
        self.assertEqual(self.rdf.nPoints, 160,
                         'incorrect number of points')

    def test_rdf_label(self):
        self.assertListEqual(self.rdf.labels[1], ['O', 'CS'],
                             'incorrect labels')

    def test_rdf_point(self):
        self.assertListEqual(self.rdf.data[2, 12, :].tolist(),
                             [3.725672E+01, 2.343750E-03],
                             'incorrect point')
        self.assertEqual(self.rdf.x[12], 6.250000E-01,
                         'incorrect grid point')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(RDFTest('test_rdf_nrdf'))
    suite.addTest(RDFTest('test_rdf_npoints'))
    suite.addTest(RDFTest('test_rdf_label'))
    suite.addTest(RDFTest('test_rdf_point'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

"""
Module containing classes for loading rdf data from DL_POLY_4
"""

import numpy as np
from ruamel.yaml import YAML


class rdf():
    """ class for reading RDFDAT

        :param source: Source RDF to read

        """
    __version__ = "0"

    def __init__(self, source=None):
        self.nRDF = 0
        self.nPoints = 0
        self.x = None
        self.data = None
        self.labels = None
        self.is_yaml = False
        if source is not None:
            self.source = source
            self.read(source)

    def read(self, source="RDFDAT"):
        """ Read an RDF file into data

        :param source: File to read

        """
        with open(source, 'r') as f:
            a = f.readline().split()[0]
            if a == "%YAML":
                self.is_yaml = True
        if self.is_yaml:
            y = YAML()
            d = None
            with open(source, 'rb') as f:
                d = y.load(f)
            self.nRDF = d['npairs']
            self.nPoints = d['ngrid']
            self.x = np.array(d['grid'])
            self.labels = [x['name'] for x in d['rdfs']]
            self.data = np.zeros((self.nRDF, self.nPoints, 2))
            for i in range(self.nRDF):
                self.data[i, :, 0] = d['rdfs'][i]['gofr']
                self.data[i, :, 1] = d['rdfs'][i]['nofr']
        else:
            with open(source, 'r') as fileIn:
                # Discard title
                _ = fileIn.readline()
                self.nRDF, self.nPoints = map(int, fileIn.readline().split())

                self.x = np.zeros(self.nPoints)
                self.data = np.zeros((self.nRDF, self.nPoints, 2))
                self.labels = []
                s = True
                for sample in range(self.nRDF):
                    species = fileIn.readline().split()
                    if len(species) == 0:
                        break
                    self.labels.append(species)
                    for point in range(self.nPoints):
                        r, g_r, n_r = map(float, fileIn.readline().split())
                        if s:
                            self.x[point] = r
                        self.data[sample, point, :] = g_r, n_r
                    s = False

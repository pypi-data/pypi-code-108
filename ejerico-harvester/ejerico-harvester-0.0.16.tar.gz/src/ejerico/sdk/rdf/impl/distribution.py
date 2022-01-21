"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class DistributionImpl(object):

    def __init__(self):
        object.__init__(self)
        self.accessURL = None
        self.bytesize = None
        self.created = None
        self.description = None
        self.downloadURL = None
        self.format = None
        self.modified = None
        self.issued = None
        self.license = None
        self.mimetype = None
        self.modified = None
        self.rights = None
        self.title = None
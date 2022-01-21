"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class FacilityImpl(object):

    def __init__(self):
        object.__init__(self)
        self.address = None
        self.description = None
        self.spatial = None
        self.title = None
        self.theme = None
        self.type = None
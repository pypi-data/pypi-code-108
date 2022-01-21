"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class VcardImpl(object):

    def __init__(self):
        object.__init__(self)
        self.address = None
        self.country = None
        self.email = None
        self.fax = None
        self.locality = None
        self.phone = None
        self.postal_code = None
        self.region = None
        self.spatial = None
        self.url = None

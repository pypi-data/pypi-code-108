"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class ApiImpl(object):

    def __init__(self):
        object.__init__(self)
        self.description = None
        self.operation = None
        self.status_code = None
        self.title = None
        self.type = None
        self.url = None
        self.version = None
        
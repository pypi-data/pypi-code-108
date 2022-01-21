"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class WebServiceImpl(object):

    def __init__(self):
        object.__init__(self)
        self.api = None
        self.description = None
        self.keywords = None
        self.license = None
        self.name = None
        self.published = None
        self.spatial = None
        self.temporal = None
        self.type = None
        self.url = None

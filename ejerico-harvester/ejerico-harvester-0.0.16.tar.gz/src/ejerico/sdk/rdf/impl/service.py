"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class ServiceImpl(object):

    def __init__(self):
        object.__init__(self)
        self.description = None
        self.name = None
        self.type = None
        self.software = None
        self.url = None
        self.provider = None
        self.project = None
        self.owner = None
        self.contact = None
        self.terms_of_service = None
        self.service_type = None 


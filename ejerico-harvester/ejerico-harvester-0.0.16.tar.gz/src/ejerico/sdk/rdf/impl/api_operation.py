"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class ApiOperationImpl(object):

    def __init__(self):
        object.__init__(self)
        self.method = None
        self.parameter = None
        self.url = None

class ApiOperationParameterImpl(object):

    def __init__(self):
        object.__init__(self)
        self.method = None

        self.default_value = None
        self.label = None
        self.max_value = None
        self.min_value = None
        self.parameter = None
        self.required = None
        self.range = None
        self.value_pattern = None
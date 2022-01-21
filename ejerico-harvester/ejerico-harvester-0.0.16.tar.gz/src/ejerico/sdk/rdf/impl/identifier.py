"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

from ejerico.sdk.rdf.namespace import EJERICO

class IdentifierImpl(object):

    def __init__(self):
        self.system = None
        self.code = None

    def toString(self):
        return "{}:{}".format(self.system if self.system is not None else EJERICO, self.code)
    
    def fromString(self, string):
        p = string.split(':')
        self.system = p[0]
        self.code = ''.join(p[1:])
"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class AddressImpl(object):

    def __init__(self):
        object.__init__(self)
        self.street_address = None
        self.postal_code = None
        self.locality = None
        self.country = None
        self.region = None
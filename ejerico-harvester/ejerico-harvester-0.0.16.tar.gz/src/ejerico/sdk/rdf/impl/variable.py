"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class VariableImpl(object):

    def __init__(self):
        object.__init__(self)
        self.alternate_name = None
        self.concept = None
        self.description = None
        self.max_value = None
        self.measurement_technique = None
        self.min_value = None
        self.name = None
        self.propertyID = None
        self.unit_code = None
        self.unit_text = None
        self.url = None
        self.value = None
        self.value_reference = None
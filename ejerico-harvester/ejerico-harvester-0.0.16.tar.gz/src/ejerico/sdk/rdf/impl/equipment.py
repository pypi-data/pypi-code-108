"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class EquipmentImpl(object):

    def __init__(self):
        object.__init__(self)
        self.description = None
        self.end_date = None
        self.filter = None
        self.name = None
        self.orientation = None
        self.period = None
        self.range = None
        self.resolution = None
        self.start_date = None
        self.serial = None
        self.spatial = None
        self.theme = None
        self.type = None
        
        
"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class ProjectImpl(object):

    def __init__(self):
        object.__init__(self)
        self.description = None
        self.license = None
        self.name = None
        self.contributor = None
        self.organization = None
        self.owner = None
        self.partner = None
        self.responsible = None
        self.spatial = None
        self.title = None
        self.temporal = None
        self.url = None
        
        

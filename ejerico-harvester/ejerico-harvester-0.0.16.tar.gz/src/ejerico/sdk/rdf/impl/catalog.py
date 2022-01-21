"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class CatalogImpl(object):

    def __init__(self):
        object.__init__(self)
        self.accrual_periodicity = None
        self.author = None
        self.concept = None
        self.contactPoint = None
        self.created = None
        self.creator = None
        self.contributor = None
        self.dataset = None
        self.description = None
        self.distribution = None
        self.document = None
        self.equipment = None
        self.issued = None
        self.keywords = None
        self.landing_page = None
        self.language = None
        self.modified = None
        self.owner = None
        self.project = None
        self.publisher = None
        self.relation = None
        self.resolution = None
        self.spatial = None
        self.service = None
        self.temporal = None
        self.theme = None
        self.title = None
        self.variable = None
        self.url = None
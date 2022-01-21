"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class DatasetImpl(object):

    def __init__(self):
        object.__init__(self)
        self.accrual_periodicity = None
        self.author = None
        self.contactPoint = None
        self.created = None
        self.creator = None
        self.contributor = None
        self.description = None
        self.distribution = None
        self.document = None
        self.editor = None
        self.equipment = None
        self.issued = None
        self.keywords = None
        self.landing_page = None
        self.language = None
        self.modified = None
        self.owner = None
        self.page = None
        self.platform = None
        self.processing_level = None
        self.project = None
        self.provenance = None
        self.publisher = None
        self.relation = None
        self.resolution = None
        self.service = None
        self.software = None
        self.spatial = None
        self.summary = None
        self.temporal = None
        self.theme = None
        self.title = None
        self.type = None
        self.user = None
        self.variable = None
        self.version = None


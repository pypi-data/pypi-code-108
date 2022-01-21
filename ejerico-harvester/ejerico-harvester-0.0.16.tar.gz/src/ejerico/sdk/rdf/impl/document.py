"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class DocumentImpl(object):

    def __init__(self):
        object.__init__(self)
        self.abstract = None
        self.catalog = None
        self.citation = None
        self.created = None
        self.creator = None
        self.contributor = None
        self.dataset = None
        self.description = None
        self.distribution = None
        self.keywords = None
        self.issn = None
        self.language = None
        self.license = None
        self.mimetype = None
        self.owner = None
        self.pages = None
        self.published = None
        self.publisher = None
        self.project = None
        self.software = None
        self.spatial = None
        self.temporal = None
        self.title = None
        self.type = None
        self.url = None
        self.volume = None

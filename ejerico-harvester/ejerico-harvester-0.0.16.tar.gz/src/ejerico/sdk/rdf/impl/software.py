import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class SoftwareImpl(object):

    def __init__(self):
        object.__init__(self)
        self.abstract = None
        self.author = None
        self.created = None
        self.creator = None
        self.contributor = None
        self.concept = None
        self.description = None
        self.distribution = None
        self.downloadURL = None
        self.keywords = None
        self.language = None
        self.license = None
        self.memory_requirements = None
        self.modified = None
        self.name = None
        self.organization = None
        self.owner = None
        self.publisher = None
        self.published = None
        self.operating_system = None
        self.storage_requirements = None
        self.processor_requirements = None
        self.programming_language = None
        self.published = None
        self.runtime= None
        self.size = None
        self.source = None
        self.suite = None
        self.updated = None
        self.url = None
        self.version = None
        
        
        
        
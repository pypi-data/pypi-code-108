"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class RelationImpl(object):

    def __init__(self):
        object.__init__(self)
        self.has_part = None 
        self.is_part_of = None 
        self.conform_to = None 
        self.is_format_of = None  
        self.has_format = None  
        self.is_version_of = None 
        self.hash_version = None  
        self.replaces = None  
        self.is_replaces_by = None  
        self.references = None  
        self.is_reference_by = None  
        self.require = None  
        self.is_required_by = None 
        self.was_derived_from = None  
        self.was_influenced_by =None  
        self.was_quoted_from = None  
        self.was_revision_of = None  
        self.had_primary_source = None  
        self.alternate_of = None  
        self.specialization_of = None 
        
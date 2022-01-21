"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class ConceptSchemeImpl(object):

    def __init__(self):
        object.__init__(self)
        self.alt_label = None
        self.definition = None
        self.description = None
        self.hidden_label = None
        self.notation = None
        self.pref_label = None
        self.title = None
        # self.top_concept = None
        # self.broader_generic = None
        # self.broader_instative = None
        # self.broader_partitive = None
        # self.externalID = None
        # self.narrower_generic = None
        # self.narrower_instantive = None
        # self.narrower_partitive = None
        # self.private_note = None
        # self.related_has_part = None
        # self.related_part_of = None
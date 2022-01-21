"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class ConceptImpl(object):

    def __init__(self):
        object.__init__(self)
        self.alt_label = None
        # self.alt_symbol = None
        self.broader = None
        self.change_note = None
        self.definition = None
        self.editorial_note = None
        self.example = None
        self.hidden_label = None
        self.history_note = None
        self.in_scheme =  None
        # self.is_primary_subject_of = None
        # self.is_subject_of = None
        self.member = None
        self.member_list = None
        self.narrower = None
        self.notation = None
        self.note = None
        self.pref_label = None
        # self.pref_symbol= None
        # self.primary_subject= None
        self.related = None
        self.semantic_relation = None
        self.scope_note = None
        # self.subject = None
        # self.subject_indicator = None
        # self.top_concept = None

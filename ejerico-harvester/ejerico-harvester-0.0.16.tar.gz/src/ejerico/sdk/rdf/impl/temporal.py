"""TODO doc"""

import sys
import logging

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

from ejerico.sdk.utils import parseDatetime

class TemporalImpl(object):

    def __init__(self):
        object.__init__(self)
        self.end_date = None
        self.start_date = None

    def prepare(self):
        logging.debug("[Temporal::prepare] entering method")

        if isinstance(self.start_date, str): 
            self.start_date = parseDatetime(self.start_date)
        if isinstance(self.end_date, str): 
            self.end_date = parseDatetime(self.end_date)
        
        #self.start_date = self.start_date.replace(hour=0, minute=0, second=0, microsecond=0) if self.start_date is not None else self.start_date
        #self.end_date = self.end_date.replace(hour=0, minute=0, second=0, microsecond=0) if self.end_date is not None else self.end_date

        temporalID = "{}_{}".format(self.start_date, self.end_date)
        
        self.alias = [a for a in self.alias if not str(a).startswith(self.entity_domain)]
        self.id = self.__class__.buildURI("{}:{}".format(self.source, temporalID))
        self.alias.append(self.__class__.buildSourceURI(self.source, temporalID))
        self.first_born = True
        

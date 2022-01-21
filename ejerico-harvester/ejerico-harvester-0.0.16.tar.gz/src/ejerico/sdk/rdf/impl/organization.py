"""TODO doc"""

import sys
import logging 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

from ejerico.sdk.utils import format_email

class OrganizationImpl(object):

    def __init__(self):
        object.__init__(self)
        self.address = None
        self.email = None
        self.lei_code = None
        self.name = None
        self.spatial = None
        self.phone = None
        self.url = None
        self.vcard = None

    def prepare(self):
        logging.debug("[Organization::prepare] entering method")

        if self.email is not None:
            self.email = format_email(self.email)
            if self.email not in self.alias: self.alias.append(self.email)
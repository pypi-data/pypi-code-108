"""TODO doc"""

import sys
import logging 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

from ejerico.sdk.utils import format_email
from ejerico.sdk.utils import ORCIDResolver

class PersonImpl(object):

    def __init__(self):
        object.__init__(self)
        self.address = None
        self.affiliation = None
        self.email = None
        self.familyName = None
        self.givenName = None
        self.name = None
        self.nationality = None
        self.phone = None
        self.qualification = None
        self.url = None
    
    def prepare(self):
        logging.debug("[Person::prepare] entering method")

        if self.email is not None:
            self.email = format_email(self.email)
            if self.email not in self.alias: self.alias.append(self.email)

        orcidID = ORCIDResolver.instance().resolve(self.email) if self.email is not None else None
        orcidID = ORCIDResolver.instance().resolve({"family-name": self.familyName, "given-names": self.givenName}) if orcidID and self.familyName is not None and self.givenName is not None else None
        orcidID = ORCIDResolver.instance().resolve(self.name)
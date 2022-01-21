import re
import logging
import sys 

import rdflib
import rdflib.__init__ as rdflib_init__

from pkg_resources import get_distribution

from validator_collection import checkers, errors

from rdflib import URIRef
from rdflib import namespace 
from rdflib.namespace import Namespace, ClosedNamespace

from rdflib import DCTERMS,DOAP
from rdflib import SDO

from ejerico.sdk.config import ConfigManager

__version__ = get_distribution("ejerico-harvester").version


__ADMS = Namespace("http://www.w3.org/ns/adms#")
__BODC = Namespace("http://vocab.nerc.ac.uk/collection/")
__DCT = Namespace("http://purl.org/dc/terms/")
__EJERICO = Namespace(ConfigManager.instance().defaultNAMESPACE)
__DIRECT = Namespace("http://www.direct-mapping.org/ns#")
__SCHEMA = Namespace("https://schema.org/")
__GEO = Namespace("http://www.opengis.net/ont/geosparql#")
__EPOS = Namespace("https://www.epos-eu.org/epos-dcat-ap#")
__HTTP = Namespace("http://www.w3.org/2011/http#")
__HYDRA = Namespace("http://www.w3.org/ns/hydra/core#")
__LOCN = Namespace("http://www.w3.org/ns/locn#")
__SOCIB = Namespace("http://www.socib.es/ns#")
__SPDX = Namespace("http://spdx.org/rdf/terms#")
__VCARD = Namespace("https://www.w3.org/2006/vcard/ns#")


rdflib_init__.__all__.append("ADMS")
setattr(rdflib.namespace, "ADMS",__ADMS)
setattr(rdflib,"ADMS",getattr(rdflib.namespace, "ADMS"))

rdflib_init__.__all__.append("BODC")
setattr(rdflib.namespace, "BODC",__BODC)
setattr(rdflib,"BODC",getattr(rdflib.namespace, "BODC"))

rdflib_init__.__all__.append("DIRECT")
setattr(rdflib.namespace, "DIRECT",__DIRECT)
setattr(rdflib,"DIRECT",getattr(rdflib.namespace, "DIRECT"))

rdflib_init__.__all__.append("EJERICO")
setattr(rdflib.namespace, "EJERICO",__EJERICO)
setattr(rdflib,"EJERICO",getattr(rdflib.namespace, "EJERICO"))

rdflib_init__.__all__.append("EPOS")
setattr(rdflib.namespace, "EPOS",__EPOS)
setattr(rdflib,"EPOS",getattr(rdflib.namespace, "EPOS"))

rdflib_init__.__all__.append("GEO")
setattr(rdflib.namespace, "GEO",__GEO)
setattr(rdflib,"GEO",getattr(rdflib.namespace, "GEO"))

rdflib_init__.__all__.append("HTTP")
setattr(rdflib.namespace, "HTTP",__HTTP)
setattr(rdflib,"HTTP",getattr(rdflib.namespace, "HTTP"))

rdflib_init__.__all__.append("HYDRA")
setattr(rdflib.namespace, "HYDRA",__HYDRA)
setattr(rdflib,"HYDRA",getattr(rdflib.namespace, "HYDRA"))

rdflib_init__.__all__.append("LOCN")
setattr(rdflib.namespace, "LOCN",__LOCN)
setattr(rdflib,"LOCN",getattr(rdflib.namespace, "LOCN"))

rdflib_init__.__all__.append("SOCIB")
setattr(rdflib.namespace, "SOCIB",__SOCIB)
setattr(rdflib,"SOCIB",getattr(rdflib.namespace, "SOCIB"))

rdflib_init__.__all__.append("SPDX")
setattr(rdflib.namespace, "SPDX",__SPDX)
setattr(rdflib,"SPDX",getattr(rdflib.namespace, "SPDX"))

rdflib_init__.__all__.append("DCT")
setattr(rdflib.namespace, "DCT",DCTERMS)
setattr(rdflib,"DCT",getattr(rdflib.namespace, "DCT"))

rdflib_init__.__all__.append("SCHEMA")
setattr(rdflib.namespace, "SCHEMA",SDO)
setattr(rdflib,"SCHEMA",getattr(rdflib.namespace, "SCHEMA"))

rdflib_init__.__all__.append("VCARD")
setattr(rdflib.namespace, "VCARD",__VCARD)
setattr(rdflib,"VCARD",getattr(rdflib.namespace, "VCARD"))

logging.critical("[ejerico:sdk:__init__] harcoded namespace UriRef for vocabulary SCHEMA")
vocab_schema = getattr(rdflib.namespace, "SCHEMA")
vocab_schema._NS = Namespace("https://schema.org/")

checkers.is_sha1 = lambda x: re.match(r"\b[0-9a-f]{40}\b")

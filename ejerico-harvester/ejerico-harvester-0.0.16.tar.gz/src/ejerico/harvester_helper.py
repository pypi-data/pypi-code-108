"""TODO doc"""

import collections
import itertools
import mimetypes
import os
import re
import json
import logging

import atoma
import netCDF4
import numpy as np
import requests

import rdflib

from datetime import datetime
from dateutil.relativedelta import relativedelta

from url_decode import urldecode

from geopy.geocoders import Nominatim

from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE

from ejerico.sdk.utils import isPrimitive, tokenize_name
from ejerico.sdk.rdf.graph_factory import GraphFactory
from ejerico.sdk.rdf.entity import ConceptScheme, Concept
from ejerico.sdk.rdf.entity import Organization
from ejerico.sdk.rdf.entity import Program

class HarvesterHelper(object):

    DEFAULT_MIMETYPE = "application/unknown"

    def __init__(self):
        object.__init__(self)

    def parseDatetime(self, date_string, date_format='%Y-%m-%d %H:%M:%S'):
        return datetime.strptime(date_string, date_format)

    def has_attribute(self, obj, *attributes):
        rst = self.get_attribute(obj, attributes) is not None

    def get_attribute(self, obj, *attributes):
        value = None

        exists = obj is not None and attributes is not None
        if exists: 
            value = obj
            for attribute in attributes:
                if not isinstance(attribute,str): return None

                if isinstance(value, collections.OrderedDict):
                    exists = exists and attribute in value
                    value = value[attribute] if exists else None
                elif isinstance(value, dict):
                    exists = exists and attribute in value
                    value = value[attribute] if exists else None
                else:
                    exists = exists and attribute in value.__dict__
                    value = value.__dict__[attribute] if exists else None

        return value if exists else None

    def nameToID(self, name):
        rst = self.generateIDsFromName(name)
        return rst[0] if rst is not None else None
    
    def generateIDsFromName(self, name, remove_punctuation=True, min_terms=-1, left_coincidences=1):
        return tokenize_name(name, remove_punctuation=remove_punctuation, min_terms=min_terms, left_coincidences=left_coincidences)   

    def guessMimetype(self, url):
        rst = mimetypes.guess_type(urldecode(url.replace('-','_')))
        return self.DEFAULT_MIMETYPE if rst[0] == None else rst[0]

    def getAndParseAtomFile(self, url=None, session=None, headers=None):
        feed = None

        try:
            if url is not None:
                requests_params = {"url": url}
                if headers is not None: requests_params["headers"] = headers

                response = requests.get(**requests_params)
                if requests.codes.ok == response.status_code:
                    feed = atoma.parse_atom_bytes(response.content)
        except Exception as e:
            logging.error("TODO handle exception")
        
        return feed

    def getAndParseRSSFile(self, url=None):
        feed = None

        try:
            response = requests.get(url=url)
            if requests.codes.ok == response.status_code:
                feed = atoma.parse_rss_bytes(response.content)
        except Exception as e:
            logging.error("TODO handle exception")
        
        return feed

    def numpy_to_scalar(self, nc_val):
            for dtype in self.numpy_to_scalar.dtypes:
                if isinstance(nc_val, dtype): 
                    return nc_val.item()

            if isinstance(nc_val, np.ndarray): 
                return nc_val.tolist()

            return nc_val

    numpy_to_scalar.dtypes = (
        np.int8,np.int16,np.int32,np.int64,
        np.uint8,np.uint16,np.uint32,np.uint64,
        np.intp,np.uintp,
        np.float32,np.float64)

    def doResourceAnalysis(self, mimetype=None, url=None):
        logging.info("[HarvesterHelper::doResourceAnalysis] Entering method ({})".format(mimetype))
        if "application/x-netcdf" == mimetype:
            return self._doResourceAnalysis_netcdf(url)
        return {}
    
    def _doResourceAnalysis_netcdf(self, url):
        def nc_process_variable(nc_name, nc_var):
            proc_var = {}
            for nc_attr in nc_var.ncattrs():
                nc_val = nc_var.getncattr(nc_attr)
                proc_var[nc_attr] = self.numpy_to_scalar(nc_val)

            if "actual_range" in proc_var:
                proc_var["{}_min".format(nc_name)] = proc_var["actual_range"][0]
                proc_var["{}_max".format(nc_name)] = proc_var["actual_range"][-1]
            
            return proc_var

        data = {}
        try:
            url = "{}.nc".format(url) if not url.endswith(".nc") else url
            with netCDF4.Dataset(url) as nc:
                for attr in nc.__dict__:
                    if isPrimitive(nc.__dict__[attr]):
                        data[attr] = nc.__dict__[attr]

                nc_variables = {}
                for nc_var_key in nc.variables.keys():
                    nc_var_val = nc.variables[nc_var_key]
                    for d in nc_var_val.dimensions:
                        nc_var_key = re.sub("^{}.".format(d),"",nc_var_key)
                    nc_variables[nc_var_key] = nc_process_variable(nc_var_key, nc_var_val) 
                    
                data["variables"] = nc_variables

                logging.info("[HarvesterHelper::_doResourceAnalysis] TODO process netcdf4 file ({})".format(url))
        except ImportError as e:
            logging.error("[HarvesterHelper::_doResourceAnalysis] error importing netcdf4 file ({}) -> {}".format(url, e))
        except Exception as e:
            logging.error("[HarvesterHelper::_doResourceAnalysis] error processing netcdf4 file ({}) -> {}".format(url, e))
        
        return data

    def doProcessKnowSourceURL(self, url):
        logging.info("[HarvesterHelper::doProcessKnowSourceURL] Entering method ({})".format(url))

        #TODO case: handle.net (https://github.com/EUDAT-B2SAFE/B2HANDLE)
        pass

        #TODO case: ORCID (https://github.com/ORCID/python-orcid)
        pass

        #TODO case: doi.org (https://www.doi.org/factsheets/DOIProx.html#rest-api)
        if re.match(self.doProcessKnowSourceURL_DATACITE.re_DATACITE, url):
            return self.doProcessKnowSourceURL_DATACITE(url)

         #TODO case: csiro (https://www.doi.org/factsheets/DOIProx.html#rest-api)
        if re.match(self.doProcessKnowSourceURL_CSIRO.re_CSIRO, url):
            return self.doProcessKnowSourceURL_CSIRO(url)

        

        #TODO case: BODC (http://vocab.nerc.ac.uk/collection/???/current/???/)
        if re.match(self.doProcessKnowSourceURL.re_BODC_1, url):
            return self.doProcessKnowSourceURL_BODC(url)
        if re.match(self.doProcessKnowSourceURL.re_BODC_2, url):
            return self.doProcessKnowSourceURL_BODC(url)

        #TODO case: EDMO (https://edmo.seadatanet.org/sparql/)
        if re.match(self.doProcessKnowSourceURL.re_EDMO, url):
            return self.doProcessKnowSourceURL_EDMO(url)
        #TODO case: EDMERP (https://edmerp.seadatanet.org/sparql/)
        if re.match(self.doProcessKnowSourceURL.re_EDMERP, url):
            return self.doProcessKnowSourceURL_EDMERP(url)

        #TODO case: WMO (https://cpdb.wmo.int/data/institutionalinformation)
        pass
    doProcessKnowSourceURL.re_BODC_1 = re.compile(r"http://vocab.nerc.ac.uk/collection/(\w)+/current/(\w)+/")
    doProcessKnowSourceURL.re_BODC_2 = re.compile(r"SDN:(?P<scheme>\w+)::(?P<concept>\w+)")
    doProcessKnowSourceURL.re_EDMO = re.compile(r"EDMO:(?P<edmo>\w+)")
    doProcessKnowSourceURL.re_EDMERP = re.compile(r"EDMO:(?P<edmerp>\w+)")
    doProcessKnowSourceURL.re_DATACITE = re.compile(r"DOI:(?P<doi>\w+)")
    doProcessKnowSourceURL.re_CSIRO = re.compile(r"CSIRO:(?P<csiro>\w+)")
    
    def doProcessKnowSourceURL_EDMO(self, url):
        pass
    doProcessKnowSourceURL_EDMO.url_sparql = "https://edmo.seadatanet.org/sparql/"
    doProcessKnowSourceURL_EDMO.uri_pattern = "https://edmo.seadatanet.org/report/{edmo}"
    doProcessKnowSourceURL_EDMO.cache = {}
    doProcessKnowSourceURL_EDMO.namespaces = {}
    doProcessKnowSourceURL_EDMO.map = {}

    def doProcessKnowSourceURL_EDMERP(self, url):
        pass
    doProcessKnowSourceURL_EDMERP.url_sparql = "https://edmerp.seadatanet.org/sparql/"
    doProcessKnowSourceURL_EDMERP.uri_pattern = "https://edmerp.seadatanet.org/report/{edmerp}"
    doProcessKnowSourceURL_EDMERP.cache = {}
    doProcessKnowSourceURL_EDMERP.namespaces = {}
    doProcessKnowSourceURL_EDMERP.map = {}

    def doProcessKnowSourceURL_CSIRO(self, url):
        if url in self.doProcessKnowSourceURL_CSIRO.cache: return doProcessKnowSourceURL_CSIRO.cache[url]
        concept = None
        try:
            url="{}?_format=jsonld".format(url)
            response = requests.get(url)
            if requests.codes.ok == response.status_code:
                data = json.loads(response.text)
                concept_scheme = ConceptScheme(first_born=True)
                concept_scheme.id = url[:url.rfind('/')]
                concept_scheme.title = "CSIRO - {} - Thesaurus".format(url.split('/')[-2])
                concept = Concept(first_born=True)
                concept.in_scheme = concept_scheme
                concept.id = data["@id"]
                concept.definition = data["skos:definition"]
                concept.notation = data["skos:notation"]
                concept.pref_label = data["skos:notation"]
                concept.example = data["skos:example"]
                self.doProcessKnowSourceURL_CSIRO.cache[url] = concept
        except Exception as e: pass

        return concept
    doProcessKnowSourceURL_CSIRO.cache = {}
    doProcessKnowSourceURL_CSIRO.concept_scheme = None 
    
    def doProcessKnowSourceURL_NERC(self, url):
        if url in self.doProcessKnowSourceURL_NERC.cache: return self.doProcessKnowSourceURL_NERC.cache[url]
        concept = None
        query = "SELECT ?p ?o WHERE {<{}> ?p ?o}".format(url)
        response = requests.post(self.doProcessKnowSourceURL_NERC.url)
        if requests.codes.ok == response.status_code:
            data = response.json()
            #TODO convert to Concept
            concept = Concept(first_born=True)
            self.doProcessKnowSourceURL_NERC.cache[url] = concept
        return concept
    doProcessKnowSourceURL_NERC.url = "http://vocab.nerc.ac.uk/sparql/"
    doProcessKnowSourceURL_NERC.cache = {}
     
    def doProcessKnowSourceURL_BODC(self, url, **kwargs):
        if url.startswith("http://vocab.nerc.ac.uk") or url.startswith("https://vocab.nerc.ac.uk"):
            url_parts = url.replace(' ', '').split('/')
            m = (url_parts[4], url_parts[6]) 
        else:
            m = re.match(self.doProcessKnowSourceURL_BODC.re_BODC, url)
            if not m: return None
            url = "http://vocab.nerc.ac.uk/collection/{}/current/{}/".format(m.group("scheme"), m.group("concept"))

        if url in self.doProcessKnowSourceURL_BODC.cache: return self.doProcessKnowSourceURL_BODC.cache[url]
        
        query = "SELECT ?p ?o WHERE { <###URL###> ?p ?o }".replace("###URL###", url)
        sparql = SPARQLWrapper("https://vocab.nerc.ac.uk/sparql/sparql")
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        try :
            data = sparql.query().convert() 
            if "results" in data and "bindings" in data["results"]:
                concept_scheme = ConceptScheme(first_born=True)
                concept_scheme.id = "<http://vocab.nerc.ac.uk/scheme/{}/current/>".format(m[0].upper())
                concept_scheme.title = "NERC - BODC - {} Thesaurus".format(m[0].upper())
                concept = Concept(first_born=True)
                concept.id = url
                concept.in_scheme = concept_scheme
                for item in data["results"]["bindings"]:
                    val_p = item["p"]["value"]
                    val_o = item["o"]["value"]

                    if val_p in self.doProcessKnowSourceURL_BODC.namespaces:
                        qname = self.doProcessKnowSourceURL_BODC.namespaces[val_p]
                    else:
                        qname = self.graph.qname(val_p)
                        self.doProcessKnowSourceURL_BODC.namespaces[val_p] = qname

                    if qname in self.doProcessKnowSourceURL_BODC.map:
                        qname = self.doProcessKnowSourceURL_BODC.map[qname]
                        if hasattr(concept, qname) and getattr(concept,qname) is not None:
                            val_p = getattr(concept,qname)
                            if not isinstance(val_p, list): 
                                val_p = [val_p]
                            if val_o not in val_p:
                                val_p.append(val_o)
                            setattr(concept,qname,val_p)
                            setattr(concept,"_empty", False)
                        else:
                            setattr(concept, qname, val_o)
                            setattr(concept,"_empty", False)
                            
                if hasattr(concept, "_empty") and not concept._empty:
                    self.doProcessKnowSourceURL_BODC.cache[url] = concept
                    concept.inscheme = None
                    concept.related = None
                    return concept
                
                if kwargs:
                    for k,v in kwargs.items(): setattr(concept, k, v)
                    return concept
            else:
                logging.info("[helper:doProcessKnowSourceURL_BODC] empty information for {}".format(url))
        except Exception as e: 
            logging.error(e)
        
        return None
    doProcessKnowSourceURL_BODC.re_BODC = re.compile(r"SDN(:){1,2}(?P<scheme>[\w-]+)(:){1,2}(?P<concept>[\w]+)")
    doProcessKnowSourceURL_BODC.cache = {}
    doProcessKnowSourceURL_BODC.namespaces = {}
    doProcessKnowSourceURL_BODC.map = {
       "skos:related": "related",
       "skos:definition": "definition",
       "skos:note": "note",
       "dcterms:identifier": "alias",
       "dc:identifier": "alias",
       "skos:prefLabel": "pref_label",
       "skos:altLabel": "alt_label",
       "skos:notation": "notation",
    }

    def doProcessKnowSourceURL_DATACITE(self, url):
        if url in self.doProcessKnowSourceURL_DATACITE.cache: return doProcessKnowSourceURL_DATACITE.cache[url]
        document = None
        return concept
    doProcessKnowSourceURL_DATACITE.cache = {}

    def is_edmo_resource(self, value):
        return re.match(self.is_edmo_resource.re_pattern_1) or re.match(self.is_edmo_resource.re_pattern_2)
    is_edmo_resource.re_pattern_1 = re.compile("https://edmo.seadatanet.org/report/[\d]+")
    is_edmo_resource.re_pattern_2 = re.compile("edmo:[\d]+")

    def is_edmerp_resource(self, value):
        return re.match(self.is_edmo_resource.re_pattern_1) or re.match(self.is_edmo_resource.re_pattern_2)
    is_edmerp_resource.re_pattern_1 = re.compile("https://edmerp.seadatanet.org/report/[\d]+")
    is_edmerp_resource.re_pattern_2 = re.compile("edmerp:[\d]+")

    def get_geoLocation(self, location, nominatim="ejerico"):
        if nominatim not in self.get_geoLocation.cache_nominatim:
            self.get_geoLocation.cache_nominatim[nominatim] = Nominatim(user_agent=nominatim)
        app = self.get_geoLocation.cache_nominatim[nominatim]
        location = app.geocode(location)
        return location.raw if location is not None else location
    get_geoLocation.cache_nominatim = {}

    def list_intersection(self, lstA, lstB):
        lstAB = [a for a in lstA for b in lstB if a == b]
        return lstAB
    
    def is_resourceJerico(self, name, kind=None):
        name = name.strip().lower()
        if name in ["jerico-next", "jerico-fp7", "jerico-s3"]: #todo replace hardcoded list with conf var
            return True
        return False

    def get_programJERICO(self):
        program = Program(first_born=True)
        program.id = Program.buildURI("ejerico:{}".format("https://www.jerico-ri.eu"))
        program.alias.append(Program.buildSourceURI("ejerico", "https://www.jerico-ri.eu"))
        program.alias.append("https://www.jerico-ri.eu")
        program.name = "JERICO RI"
        program.description = "JERICO-RI is an integrated pan-European multidisciplinary and multi-platform research infrastructure dedicated to a holistic appraisal of coastal marine system changes"
        program.url = "https://www.jerico-ri.eu"
        return program

    def get_organizationJERICO(self):
        organization = Organization(first_born=True)
        organization.id = Organization.buildURI("ejerico:{}".format("https://www.jerico-ri.eu"))
        organization.alias.append(Organization.builSourcedURI("ejerico", "https://www.jerico-ri.eu"))
        organization.alias.append("https://www.jerico-ri.eu")
        organization.name = "JERICO RI"
        organization.description = "JERICO-RI is an integrated pan-European multidisciplinary and multi-platform research infrastructure dedicated to a holistic appraisal of coastal marine system changes"
        organization.url = "https://www.jerico-ri.eu"
        organization.program = self.get_programJERICO()
        return organization

    @property
    def graph(self):
        return self._graph
    @graph.setter
    def graph(self, value):
        self._graph = value

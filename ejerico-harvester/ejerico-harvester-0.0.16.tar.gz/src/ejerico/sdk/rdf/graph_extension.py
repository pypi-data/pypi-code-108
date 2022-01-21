"""TODO doc"""

import datetime
import inspect
import sys 
import re
import time
import traceback
import logging
import uuid
import hashlib

import nltk
import pycountry
import langdetect
import numpy as np

from functools import reduce

from validator_collection import checkers, errors
from profilehooks import profile, timecall

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import namespace
from rdflib import RDF 
from rdflib.namespace import Namespace, ClosedNamespace
from rdflib.store import Store, VALID_STORE

from ejerico.sdk.rdf.entity import Concept
from ejerico.sdk.rdf.entity import Spatial
from ejerico.sdk.rdf.entity import Entity
from ejerico.sdk.rdf.entity import Identifier
from ejerico.sdk.rdf.entity import EntityMapper

from ejerico.sdk.rdf.namespace import EJERICO

from ejerico.sdk.exceptions import GraphError
from ejerico.sdk.utils import isPrimitive, tokenize_name, parseDatetime, roundTime, geolocate, UnknowRegisterHandler
from ejerico.sdk.rdf.entity import Entity, EntityMetaclass, EntityMapper, Person

from ejerico.sdk.config import ConfigManager

class GraphExtension:

    def __init__(self): 
        self.config = ConfigManager.instance()
        self.collect_stats = self.config.get("collect_stats", default=False)

    def toTurtle(self):
        self._register_namespaces()
        rep_turtle = self.serialize(format="turtle")
        return rep_turtle.decode("utf-8") if  hasattr(rep_turtle, "decode") else rep_turtle

    def toJSONLD(self): 
        self._register_namespaces()
        rep_jsonld = self.serialize(format="json-ld")
        return rep_jsonld.decode("utf-8") if  hasattr(rep_jsonld, "decode") else rep_jsonld

    def toXML(self):
        self._register_namespaces() 
        rep_xml = self.serialize(format="xml")
        return rep_xml.decode("utf-8") if  hasattr(rep_xml, "decode") else rep_xml
    
    def toN3(self):
        self._register_namespaces() 
        rep_n3 = self.serialize(format="n3")
        return rep_n3.decode("utf-8") if  hasattr(rep_n3, "decode") else rep_n3

    def findByURI(self, uri, kind=None):
        logging.debug("[Graph::findByURI] entering method")

        if not isinstance(uri,str):
            logging.info("[find_URI] uri is not a 'str' instance {}")
            return None

        rst = self.findByURIs([uri])
        rst = rst if rst is not None else []
        if 1 < len(rst):
            logging.info("[Graph::findByURI] warnning -multiple entities are binded to uri {} ({})".format(uri, rst))

        return rst[0] if 0 != len(rst) else None

    def findByURIs(self, uris, kind=None):
        #logging.debug("[Graph::findByURIs] entering method")
        
        if not isinstance(uris,list):
            logging.info("[Graph::findByURIs] uris is not a 'list' instance {}")
            return None

        uri = next((self.findByURIs.cache_URI[str(u)] for u in uris if str(u) in self.findByURIs.cache_URI), None)
        if uri is not None:
            logging.info("[Graph::findByURIs] found in cache: {}".format(uri)) 
            return uri

        rst = None

        for uri in uris:
            rst = self._findByURIsOneByOne(uri, kind)
            if rst is not None:
                rst = [rst] 
                break
            
        # try:
        #     if kind is None:
        #         query = _SPARQL_QUERY_FIND_ENTITY_BY_URI
        #         query = query.replace("###prefixes###", self.prefixes) 
        #     else:
        #         kind = kind() if isinstance(kind,EntityMetaclass) else kind
        #         if not isinstance(kind,Entity):
        #             logging.info("[Graph::findByURIs] 'kind' parameter must be a Entity class")
        #             raise GraphError("'kind' parameter must be a Entity class")
                
        #         base = _get_RDFType(kind)
        #         query = _SPARQL_QUERY_FIND_ENTITY_BY_URI_KIND
        #         query = query.replace("###prefixes###", self.prefixes)
        #         query = query.replace("###kind###",base)
        #         logging.debug("[Graph::findByURIs] entering method with param '{}'".format(base))
        
        #     query = query.replace("###values###", " ".join(['(<{}>)'.format(URIRef(u)) for u in uris]))
        #     #logging.info("\t Query: -> {}".format(query))
        #     rows = self.query(query, initNs=self.registered_namespaces)
        #     for row in rows:
        #         if rst is None: rst = [] 
        #         rst.append(str(row[0]))
        # except Exception as e:
        #     logging.error("[Graph::findByURIs] error processing sparql ({})".format(e))
        #     logging.error("\t\tQuery: '{}'".format(query))
        #     raise GraphError(e)
        
        if rst is not None and len(rst) != 0:
            for uri in uris: self.findByURIs.cache_URI[str(uri)] = str(rst[0])
        return rst
    findByURIs.cache_URI = {}

    def _findByURIsOneByOne(self, uri, kind=None):
        try:
            rst = None

            if kind is None:
                query = _SPARQL_QUERY_FIND_ENTITY_BY_URI_KIND_ONE_BY_ONE
            else:
                kind = kind if isinstance(kind,EntityMetaclass) else kind.__class__
                if not isinstance(kind, EntityMetaclass):
                    logging.info("[Graph::findByURIs] 'kind' parameter must be a Entity class")
                    raise GraphError("'kind' parameter must be a Entity class")
                
                base = Entity.getRDFTypeForEntity(kind.base())#_get_RDFType(kind)
                if base is not None:
                    query = _SPARQL_QUERY_FIND_ENTITY_BY_URI_KIND_ONE_BY_ONE
                    query = query.replace("###kind###", base if "<" in base else "<{}>".format(base))
                else: 
                    query = _SPARQL_QUERY_FIND_ENTITY_BY_URI_ONE_BY_ONE
        
            query = query.replace("###value###", '<{}>'.format(str(uri)))
            query = query.replace("###prefixes###", self.prefixes)
    
            rows = self.query(query, initNs=self.registered_namespaces)
            for row in rows:
                if rst is None: rst = [] 
                rst.append(str(row[0]))
        except Exception as e:
            logging.error("[Graph::_findByURIsOneByOne] error processing sparql ({})".format(e))
            logging.error("\t\tQuery: '{}'".format(query))
            logging.error(traceback.format_exc())
            #raise GraphError(e)
            return None
        
        return rst[0] if rst is not None and len(rst) > 0 else None

    def findRelatedURIsByURI(self, uri):
        #logging.debug("[Graph::findRelatedURIsByURI] entering method")
        uris = None
        try:
            my_uri = uri if isinstance(uri, URIRef) else URIRef(uri)
            query = _SPARQL_QUERY_FIND_RELATED_ENTITY_BY_URI.replace("###uri###", my_uri)
            query = query.replace("###prefixes###", self.prefixes)
            data = self.query(query, initNs=self.registered_namespaces)
            for d in data:
                if uris is None: uris = []
                uris.append(d[0])
        except Exception as e:
            logging.error("[Graph::getEntityByURI] error getting entity by uri ({})".format(e))
            raise GraphError(e)
        return uris

    def findURIByURL(self, url, entity_type=None):
        rst = self.findURIsByURL(url,entity_type=entity_type)
        return rst[0] if rst is not None and len(rs) !=0 else None

    def findURIsByURL(self, url, entity_type=None):
        uris = None
        try:
            entity_type = Entity.getRDFTypeForEntity(entity_type.base()) if entity_type is not None else entity_type
            query = _SPARQL_QUERY_FIND_ENTITY_BY_URL
            query = query.replace("###prefixes###", self.prefixes)
            query = query.replace("###value###", url)
            data = self.query(query, initNs=self.registered_namespaces)
            for d in data:
                if uris is None: uris = []
                uris.append(d[0])
        except Exception as e:
            logging.error("[Graph::getEntityByURI] error getting entity by uri ({})".format(e))
            raise GraphError(e)
        return uris
    findURIByURL._cache = {}
    findURIByURL._query = """
    """

    def findURIByName(self, name, entity_type=None, return_all_matches=False, return_score=False, return_class=False, threshold=0.85):
        def _remove_not_working_speech_tags(name, ignored_words=[], lang=None, as_list=False):
            lang = "english" #languageFromISOCode(lang) if 2 == len(lang) else lang    
            stopwords = nltk.corpus.stopwords.words(lang)
            tokens = re.sub(r"[\W]", ' ', name)
            tokens = nltk.tokenize.word_tokenize(tokens.lower())
            tokens = [q for q in tokens if q not in ignored_words]
            tokens = [q for q in tokens if q not in stopwords]
            tokens = [_countryFromISOCode(q.upper()) if 2==len(q) else q for q in tokens]
            tokens = [q[0] for q in nltk.pos_tag(tokens) if q[1] not in _remove_not_working_speech_tags._nltk_speech_tags]
            return tokens if as_list else  ' '.join(tokens)
        _remove_not_working_speech_tags._nltk_speech_tags = ["CC","DT","IN","PRP","PRP$","UH","WDT",]
        def _languageFromISOCode(code):
            lang = "english"
            try:
                lang = pycountry.languages.get(alpha_2=code).name.lower()
            except: 
                lang = code
            return lang
        def _countryFromISOCode(code):
            country = code
            try:
                country = pycountry.countries.get(alpha_2=code).name.lower()
            except: pass
            return country
        def _cosine_similarity(a,b):
            a_set = {w for w in a} 
            b_set = {w for w in b}
            a_vector = []; b_vector = []
            keywords = a_set.union(b_set) 
            for keyword in keywords:
                a_vector.append(1 if keyword in a_set else 0)
                b_vector.append(1 if keyword in b_set else 0)
            a_vector = np.array(a_vector)
            b_vector = np.array(b_vector)
            rst = np.inner(a_vector, b_vector) / (np.linalg.norm(a_vector) * np.linalg.norm(b_vector))
            rst = (rst - (-1)) / (1 - (-1))
            return rst
        def _lang_detect(name):
            try:
                return langdetect.detect(name)
            except Exception: pass
            return "en"
            
        nameID = hashlib.sha1(name.encode("utf-8")).hexdigest()
        if nameID in self.findURIByName._cache is not None: return self.findURIByName._cache[nameID]
        
        matches = []

        query_term = _remove_not_working_speech_tags(name, lang=_lang_detect(name), ignored_words=self.findURIByName._ignored_words)
        query_term = [n for n in query_term.split(' ') if '' != n]
        query_term = ".*".join(query_term[:2])
        query_term = ".*{}.*".format(query_term)
        
        sentence = self.findURIByName._query.format(name=query_term, initNs=self.registered_namespaces)
        sentence = sentence.replace('\n', '')
        results = self.query(sentence)
        
        a = _remove_not_working_speech_tags(name, lang=_lang_detect(name), ignored_words=self.findURIByName._ignored_words, as_list=True)
        for result in results:
            s = str(result[0]); r = str(result[1]); o = str(result[2])
            b = _remove_not_working_speech_tags(o, lang=_lang_detect(o), ignored_words=self.findURIByName._ignored_words, as_list=True)
            current_ratio = _cosine_similarity(a, b)
            if threshold <= current_ratio:
                if return_score: 
                    matches.append((s, Entity.getEntityFromRDFType(r), current_ratio) if return_class else (s, current_ratio))
                else:
                    matches.append((s, Entity.getEntityFromRDFType(r)) if return_class else (s)) 
        
        matches = sorted(matches, key=lambda x: x[2])
        matches = matches[:1] if not return_all_matches and 0 != len(matches) else matches

        if 0 == len(matches) and entity_type is not None:
            ejericoID = UnknowRegisterHandler.instance().resolveUnknown(entity_type.strbase(), name)
            if ejericoID: matches.append(ejericoID, entity_type, 1.0)

        if not return_score and not return_class:
            return matches[0] if 0 != len(matches) else None

        return matches if 0 != len(matches) else None
    findURIByName._cache = {}
    findURIByName._ignored_words = []
    findURIByName._query = """
        SELECT DISTINCT ?s ?r ?o
        WHERE {{
            ?s rdf:type ?r.
            ?s sdo:name ?o. 
            FILTER regex(?o, '{name}', 'i').  
        }}
        order by strlen(str(?o))
    """

    def getEntityByURI(self, uri, depth=None, current_depth=0):
        def _createEntity(uri, rdf_type):
            classname = entity_mapper.unmap_class(rdf_type)
            classname_class = None
            for key in entity_module.__dict__:
                if key.lower() == classname.lower():
                    if not inspect.isclass(entity_module.__dict__[key]): continue
                    if issubclass(entity_module.__dict__[key], Entity):
                        my_entity = entity_module.__dict__[key]()
                        classname_class = my_entity.__class__
            else:
                if classname_class is None:
                    my_entity = type(classname, (Entity))()

            my_entity.id = uri
            my_entity._classname = classname
            my_entity._in = 0
            my_entity._out = 0

            return my_entity
        
        def _loadEntity(uri):
            entity = None

            try:
                entities = {}

                tiplets = [] 
                tiplet_rdf_types = {}

                #STEP 0: get subject for alias (or not) [TODO]
                pass

                #STEP 1: get predicates by subject
                uri = str(uri) if isinstance(uri, URIRef) else uri
                data = self.query("DESCRIBE <{}>".format(uri), initNs=self.registered_namespaces)
                for d in data:
                    if RDF.type == d[1]: 
                        tiplet_rdf_types[str(d[0])] = str(d[2])
                    else:
                        tiplets.append((str(d[0]), d[1], d[2]))
                

                if 0 != len(tiplets):
                    for uri in tiplet_rdf_types:
                        entities[uri] = _createEntity(uri, tiplet_rdf_types[uri])

                        rows =  [(t[1], t[2]) for t in tiplets if t[0] == uri]
                        for row in rows:
                            propertyValue = row[1]
                            propertyName = entity_mapper.unmap_property(row[0], scope=entities[uri]._classname)
                            
                            if propertyName is not None:
                                if "alias" == propertyName and uri == str(propertyValue): continue
                                if "identifier" == propertyName and propertyValue is not None:
                                    my_identifier = propertyValue.toPython()
                                    propertyValue = Identifier()
                                    propertyValue.fromString(my_identifier) 
                                
                                propertyName = reduce(lambda a,b: b if b.lower() == propertyName.lower() else a, entities[uri].attributes(include_empty=True), propertyName)
                                if not hasattr(entities[uri], propertyName): setattr(entities[uri], propertyName, None)
                                
                                propertyEntity = getattr(entities[uri], propertyName)
                                if propertyEntity is not None and not isinstance(propertyEntity, list): propertyEntity = [propertyEntity]

                                if isinstance(propertyValue, URIRef): 
                                    #propertyValue = str(propertyValue)    
                                    
                                    if propertyValue in entities:
                                        entities[str(propertyValue)]._in += 1
                                        entities[uri]._out += 1

                                        if propertyEntity is not None:
                                            propertyEntity.append(entities[propertyValue])
                                        else:
                                            propertyEntity = entities[propertyValue]
                                    else:
                                        if propertyEntity is not None:
                                            propertyEntity.append(propertyValue)
                                        else:
                                            propertyEntity = propertyValue
                                    setattr(entities[uri], propertyName, propertyEntity)
                                elif isinstance(propertyValue, Literal):
                                    if propertyEntity is not None:
                                        propertyEntity.append(propertyValue.toPython())
                                    else:
                                        propertyEntity = propertyValue.toPython()
                                    setattr(entities[uri], propertyName, propertyEntity)
                                elif isinstance(propertyValue, Entity):
                                    if propertyEntity is not None:
                                        propertyEntity.append(propertyValue)
                                    else:
                                        propertyEntity = propertyValue
                                    setattr(entities[uri], propertyName, propertyEntity)
                            elif str(row[0]) in (
                                "{}source".format(ConfigManager.instance().defaultNAMESPACE), 
                                "{}updated".format(ConfigManager.instance().defaultNAMESPACE), 
                                "{}hash".format(ConfigManager.instance().defaultNAMESPACE)):
                                if "{}source".format(ConfigManager.instance().defaultNAMESPACE) == str(row[0]):
                                    setattr(entities[uri], "source", str(row[1]))
                                if "{}updated".format(ConfigManager.instance().defaultNAMESPACE) == str(row[0]):
                                    setattr(entities[uri], "updated", parseDatetime(str(row[1])))
                                if "{}hash".format(ConfigManager.instance().defaultNAMESPACE) == str(row[0]): 
                                    pass
                            else:
                                logging.info("[Graph::getEntityByURI:step_loadEntity] unknown property name '{}'".format(str(row[0])))

                entities = [entities[e] for e in entities if 0 == entities[e]._in or 1 == len(entities) ]
                entity =  entities[0] if 1 == len(entities) else None
            except Exception as e:
                logging.error("[Graph::getEntityByURI:step_loadEntity] error getting entity by uri ({})".format(e))
                print(traceback.format_exc())
            return entity

        logging.debug("[Graph::getEntityByURI] entering method with param: {}".format(uri))

        uri = uri.id if isinstance(uri, Entity) else uri

        entity_mapper = EntityMapper.instance()
        entity_module = inspect.getmodule(entity_mapper)

        entity = _loadEntity(uri)

        if entity is not None:
            setattr(entity, "_original_values", {})
            for key in entity.attributes(): entity._original_values[key] = getattr(entity, key)    

            if depth is not None and current_depth < depth:
                for key in entity.attributes():
                    if "alias" == key: continue
                    if "url" == key: continue 
                    
                    value = getattr(entity, key)
                    if isinstance(value, URIRef) and str(value).startswith(entity.entity_domain):
                        entity_class = Entity.getEntityClassFromURI(value)
                        if entity_class is not None: 
                            setattr(entity, key, self.getEntityByURI(value, depth=depth, current_depth=current_depth+1)) 
                    elif isinstance(value, list):
                        for idx in range(len(value)):
                            if isinstance(value[idx], URIRef) and str(value[idx]).startswith(entity.entity_domain):
                                entity_class = Entity.getEntityClassFromURI(value[idx])
                                if entity_class is not None: 
                                    value[idx] = self.getEntityByURI(value[idx], depth=depth, current_depth=current_depth+1)
                        setattr(entity, key, value)

        return entity

    def __old_getEntityByURI(self, uri, depth=None, current_depth=0):
        #logging.debug("[Graph::getEntityByURI] entering method")
        entity = None
        try:
            graph = Graph()
            my_uri = uri if isinstance(uri, URIRef) else URIRef(uri)
            query = _SPARQL_QUERY_GET_ENTITY_BY_URI.replace("###uri###", my_uri)
            data = self.query(query, initNs=self.registered_namespaces); data_rdftype = []
            for d in data: 
                graph.add((my_uri, d[0], d[1]))
                if RDF.type == d[0]: data_rdftype.append((my_uri, d[1]))
                
            entity = Entity.load(graph, subjects_with_types=data_rdftype)

            if isinstance(entity,Entity):
                #save original values in store to track changes
                setattr(entity, "_original_values", {})
                for key in entity.attributes(): entity._original_values[key] = getattr(entity, key)    

                if depth is not None and current_depth < depth:
                    for key in entity.attributes():
                        if "alias" == key: continue
                        if "url" == key: continue 
                        
                        value = getattr(entity, key)
                        if isinstance(value, URIRef) and str(value).startswith(entity.entity_domain):
                            entity_class = Entity.getEntityClassFromURI(value)
                            if entity_class is not None: 
                                setattr(entity, key, self.getEntityByURI(value, depth=depth, current_depth=current_depth+1)) 
                        elif isinstance(value, list):
                            for idx in range(len(value)):
                                if isinstance(value[idx], URIRef) and str(value[idx]).startswith(entity.entity_domain):
                                    entity_class = Entity.getEntityClassFromURI(value[idx])
                                    if entity_class is not None: 
                                        value[idx] = self.getEntityByURI(value[idx], entity_class, depth=depth, current_depth=current_depth+1)
                            setattr(entity, key, value)
        except Exception as e:
            logging.error("[Graph::getEntityByURI] error getting entity by uri ({})".format(e))
            raise GraphError(e)
        return entity

    def getURISByEntityType(self, clazz):
        def getURISByEntityTypeGenerator(clazz, size=1000):
            logging.debug("[Graph::getURISByEntityType:getURISByEntityTypeGenerator] entering method with param: {}".format(clazz.__name__))
            rdftype = Entity.getRDFTypeForEntity(clazz)
            if rdftype is None: return

            rdftype = str(rdftype)
            stm = _SPARQL_GET_TOTAL_SUBJECTS_BY_RDFTYPE.replace("###rdftype###", rdftype)
            total = self.query(stm, initNs=self.registered_namespaces)
            total = total[0] if 0 != len(total) else 0
            
            for offset in range(0, int(total/size)+1):
                stm = _SPARQL_GET_SUBJECTS_BY_RDFTYPE.replace("###rdftype###", rdftype)
                stm = stm.replace("###size###", str(size))
                stm = stm.replace("###offset###", str(offset))
                uris = self.query(stm, initNs=self.registered_namespaces)
                for u in uris: yield u

        logging.debug("[Graph::getURISByEntityType] entering method with param: {}".format(clazz.__name__))
        rst = []
        for s in getURISByEntityTypeGenerator(clazz): rst.append(s)
        return rst

    def save(self, entity):
        logging.debug("[Graph::save] entering method ")

        if not isinstance(entity,Entity):
            logging.error("[Graph::save] parameter entity must be a instance of 'ejerico.sdk.rdf.entity.Entity'")
            raise GraphError("parameter entity must be a instance of 'ejerico.sdk.rdf.entity.Entity' (found type:{})".format(type(entity)))

        if entity.harvester is None:
            harvester = self._get_callerHarvester()
            if harvester is not None: entity._harvester = harvester

        self.do_before_save(entity, harvester=entity.harvester)

        is_valid = self._validate(entity) 
        if is_valid:
            self.do_callback_on_save(entity)
            tiplets = entity.toGraph()
            if True == self.config.get("save_dummy_mode"):
                logging.warning("[Graph::save] Dummy save mode actived. Entities will not save on repository!!!".format(str(entity.id)))
            else:
                self.__iadd__(tiplets)
                logging.debug("[Graph::save] appending entity '{}'".format(entity.id))
            self.do_callback_on_saved(entity)
            self.do_delegation_request(entity)
            self.do_after_save(entity, harvester=entity.harvester)
        else:
            logging.warning("[Graph::save] entity '{}' is not valid".format(str(entity.id)))

        if self.collect_stats:
            entity.is_valid = is_valid
            stats = self._get_callerStats() if entity.harvester is None else entity.harvester.stats
            stats = entity._stats if stats is None and hasattr(entity, "_stats") else stats
            if stats is not None:
                stats._harvesting_spanID  = spanID=str(uuid.uuid4())
                self.do_compute_entity_stats(stats=stats, entity=entity)

    def delete(self, entity):
        if not isinstance(entity,Entity):
            logging.info("[delete] parameter entity must be a instance of 'ejerico.sdk.rdf.entity.Entity'")
            raise GraphError("parameter entity must be a instance of 'ejerico.sdk.rdf.entity.Entity' (found type:{})".format(type(entity)))
        
        self._prepare(entity)
        self._fixEntityID(entity)

        self.do_callback_on_delete(entity)
        tiplets = entity.toGraph()
        self.do_callback_on_deleted(entity)
        self.remove_graph(tiplets)

    def find(self, entity):
        if not isinstance(entity,Entity):
            logging.info("[find] parameter entity must be a instance of 'ejerico.sdk.rdf.entity.Entity'")
            raise GraphError("parameter entity must be a instance of 'ejerico.sdk.rdf.entity.Entity' (found type:{})".format(type(entity)))
        
        tiplets = entity.toDict()
        logging.info(tiplets)

    @property
    def prefixes(self):
        rst = []
        for k,v in sorted(self.registered_namespaces.items(), key=lambda item: item[1]):
            #rst.append("@prefix {}: <{}>.".format(k,v))
            rst.append("PREFIX {}: <{}>".format(k,v))
        return "\n".join(rst)

    @property
    def registered_namespaces(self):
        import rdflib as my_rdflib
        self.bind("EJERICO".lower(), my_rdflib.EJERICO)
        self.bind("ADMS".lower(), my_rdflib.ADMS)
        self.bind("BODC".lower(), my_rdflib.BODC)
        self.bind("DIRECT".lower(), my_rdflib.DIRECT)
        self.bind("EJERICO".lower(), my_rdflib.EJERICO)
        self.bind("EPOS".lower(), my_rdflib.EPOS)
        self.bind("HTTP".lower(), my_rdflib.HTTP)
        self.bind("HYDRA".lower(), my_rdflib.HYDRA)
        self.bind("LOCN".lower(), my_rdflib.LOCN)
        self.bind("SOCIB".lower(), my_rdflib.SOCIB)
        self.bind("SPDX".lower(), my_rdflib.SPDX)
        self.bind("VCARD".lower(), my_rdflib.VCARD)
        rst = {k:str(v) for k,v in self.namespaces()}
        return dict(sorted(rst.items(), key=lambda item: item[0]))

    def do_before_save(self, entity, harvester=None):
        logging.debug("[Graph::do_before_save] entering method ")

        if not isinstance(entity,Entity):
            logging.info("[Graph::do_before_save] parameter entity must be a instance of 'ejerico.sdk.rdf.entity.Entity'")
            raise GraphError("parameter entity must be a instance of 'ejerico.sdk.rdf.entity.Entity' (found type:{})".format(type(entity)))

        self._buildAliasForIdentifier(entity)
        self._injectPreferredKeyworks(entity, keywords=entity.harvester.config.get("preferred_keywords") if entity.harvester is not None else None)
        self._injectPreferredConcepts(entity, concepts=entity.harvester.config.get("preferred_concepts") if entity.harvester is not None else None)
        self._setSource(entity, entity.source)
        self._geolocate(entity)
        self._entity_timestamp(entity)
        self._prepare(entity)
        self._fixEntityID(entity)
        self._calculate_hash(entity)

    def do_after_save(self, entity, harvester=None):
        logging.debug("[Graph::do_after_save] entering method ")

        if not isinstance(entity,Entity):
            logging.info("[Graph::do_after_save] parameter entity must be a instance of 'ejerico.sdk.rdf.entity.Entity'")
            raise GraphError("parameter entity must be a instance of 'ejerico.sdk.rdf.entity.Entity' (found type:{})".format(type(entity)))
        self._fix_audit_dates(entity)

    def do_callback_on_save(self, entity):
        if hasattr(entity, "on_save"): entity.on_save()
    def do_callback_on_delete(self, entity):
        if hasattr(entity, "on_delete"): entity.on_delete()

    def do_callback_on_saved(self, entity):
        if hasattr(entity, "on_saved"): entity.on_saved()
    def do_callback_on_deleted(self, entity):
        if hasattr(entity, "on_deleted"): entity.on_deleted()

    def do_delegation_request(self, entity, from_harvester=None):
        if entity is None or from_harvester is None: return
        try:
            if from_harvester is None:
                caller = sys._getframe(2)
                caller_locals = caller.f_locals
                if "self" in caller_locals:
                    caller_self = caller_locals["self"]
                    if hasattr(caller_self, "executor"): 
                        from_harvester = caller_self
                    else:
                        return
        except Exception as e: return
         
        for alias in entity.alias:
            alias = str(alias)
            if alias.startswith(entity.entity_domain): continue
            from_harvester.executor.delegate_request(uri=alias, from_harvester=from_harvester)
            for key in entity.attributes():
                value = getattr(entity, key)
                if isinstance(value, list):
                    for value_item in value:
                        if isinstance(value_item, Entity): 
                            self.do_delegation_request(value_item, from_harvester=from_harvester)
                        elif isinstance(value, Entity): 
                            self.do_delegation_request(value, from_harvester=from_harvester)

    def do_compute_entity_stats(self, stats=None, entity=None):
        if stats is None or entity is None: return
        
        #avoid only-reference Entities
        attributes = entity.attributes()
        if len(attributes) == 0: return

        stats.computeEntity(entity)

        for key in entity.attributes():
            value = getattr(entity, key)
            if isinstance(value, list):
                for value_item in value:
                    if isinstance(value_item, Entity): 
                        self.do_compute_entity_stats(stats=stats, entity=value_item)
            elif isinstance(value, Entity): 
                self.do_compute_entity_stats(stats=stats, entity=value)
    
    def do_compute_harvester_stats(self, stats=None, entity=None, is_valid=True):
        if stats is None or entity is None: return

        for key in entity.__dict__:
            if key.startswith('_'): continue
            value = getattr(entity, key)
            if isinstance(value, list):
                setattr(stats, "{}__{}".format(entity.strbase(), key), len(value))
            elif isinstance(value, Entity):
                setattr(stats, "{}__{}".format(entity.strbase(), key), 1)

    def _register_namespaces(self):
        entity = Entity()
        entity._register_namespaces(self)

    def _get_callerHarvester(self, depth=2):
        harvester = None 
        try:
            caller = sys._getframe(2)
            caller_locals = caller.f_locals
            if "self" in caller_locals:
                caller_self = caller_locals["self"]
                if hasattr(caller_self, "stats"): harvester = caller_self
        except Exception as e: 
            logging.error("[graph:_getCallerStat] error getting caller stat property ({})".format(e))
        return harvester

    def _get_callerStats(self):
        stats = None 
        try:
            caller = sys._getframe(2)
            caller_locals = caller.f_locals
            if "self" in caller_locals:
                caller_self = caller_locals["self"]
                if hasattr(caller_self, "stats"): stats = caller_self.stats
        except Exception as e: 
            logging.error("[graph:_getCallerStat] error getting caller stat property ({})".format(e))
        return stats

    def _prepare(self,entity):
        if hasattr(entity,"prepare"): 
            entity_prepare = getattr(entity, "prepare"); super_entity_prepare = None

            entity_super = entity.base()
            if hasattr(entity_super, "prepare"):
                super_entity_prepare = getattr(super(entity_super, entity), "prepare") 
                super_entity_prepare()
            
            if super_entity_prepare is None or entity_prepare != super_entity_prepare:
                entity_prepare()


        # if hasattr(entity,"name") and entity.name is not None:
        #     tokenized_name = tokenize_name(entity.name)
        #     if tokenized_name is not None:
        #         uri_for_name = "{}:{}".format(entity._scope, tokenized_name)
        #         entity.alias.append(uri_for_name)

        if entity.alias is None: entity.alias = []
        if not isinstance(entity.alias, list): entity.alias = [entity.alias]
        #self.alias = [entity.buildURI(a) for a in entity.alias if not checkers.is_url(a) and not checkers.is_email(a)]
        for i in range(len(entity.alias)):
            if not checkers.is_url(entity.alias[i]) and not checkers.is_email(entity.alias[i]):
                entity.alias[i] = entity.buildURI(entity.alias[i])

        if isinstance(entity, Person) and entity.name is not None:
            match = re.match(self._prepare.RE_NAME_EMAIL_PATTERN, entity.name)
            if match:
                entity.name = match.group("name")
                entity.alias.append(match.group("email"))
                entity.email = [] if not hasattr(entity, "email") or entity.email is None else entity.email
                entity.email = [entity.email] if entity is not None and not isinstance(entity.email, list) else entity.email
                entity.email.append(match.group("email"))
        
        for entity_child in entity.__dict__:
            if re.match(r"^[a-zA-Z]+\W*", entity_child):
                    if isinstance(entity.__dict__[entity_child],list):
                        for list_entity in entity.__dict__[entity_child]:
                            if isinstance(list_entity, Entity): self._prepare(list_entity)

                    if isinstance(entity.__dict__[entity_child], Entity): 
                        self._prepare(entity.__dict__[entity_child])

        #fix organizations acting as persons
        #if isinstance(entity,Person): pass
    _prepare.RE_NAME_EMAIL_PATTERN = re.compile("^(?P<name>[áàéèíìóòúùäöü\w\d.-_ ]+){1}([\W])+(<)(?P<email>[\w\d\W]+)+(>)$", re.UNICODE)

    def _calculate_hash(self, entity):
        logging.debug("[Graph::_calculate_hash] '{}' entity has hash: {}".format(entity.strbase(),entity.hash()))

    def _fixEntityID(self,entity):   
        
        if not entity.first_born and entity.strbase() not in ("identifier"):
            entity.alias.append(entity.id)
            my_ID = self.findByURIs(entity.alias, kind=entity)

            if my_ID is not None:
                entity.alias.remove(entity.id) 
                if entity.id != my_ID: entity.id = my_ID[0] if isinstance(my_ID, list) else my_ID

        for entity_child in entity.__dict__:
            if re.match(r"^[a-zA-Z]+\W*", entity_child):
                if isinstance(entity.__dict__[entity_child],list):
                    for list_entity in entity.__dict__[entity_child]:
                        if isinstance(list_entity, Entity):
                            self._fixEntityID(list_entity)

                if isinstance(entity.__dict__[entity_child], Entity): 
                    self._fixEntityID(entity.__dict__[entity_child])
    
    def _delete_on_save(self, entity):
        for entity_child in entity.__dict__: 
            if re.match(r"^[a-zA-Z]+\W*", entity_child):
                if isinstance(entity.__dict__[entity_child],list):
                    for list_entity in entity.__dict__[entity_child]:
                        if isinstance(list_entity, Entity):
                            self._delete_on_save(list_entity)
                elif isinstance(entity.__dict__[entity_child], Entity): 
                    self._delete_on_save(entity.__dict__[entity_child])

        if entity.delete_on_save:
            try:
                logging.info("[Graph::_delete_on_save] deleting entities binded to <{}> as subject".format(entity.id))
                query = _SPARQL_DELETE_ENTITY_BY_URI_AS_SUBJECT.replace("###uri###", entity.id)
                query = query.replace("###prefixes###", self.prefixes)
                data = self.update(query, initNs=self.registered_namespaces)

                logging.info("[Graph::_delete_on_save] deleting entities binded to <{}> as object".format(entity.id))
                query = query.replace("###prefixes###", self.prefixes)
                query = _SPARQL_DELETE_ENTITY_BY_URI_AS_OBJECT.replace("###uri###", entity.id)
                query = query.replace("###prefixes###", self.prefixes)
                data = self.update(query, initNs=self.registered_namespaces)
            except Exception as e: pass

    def _setSource(self,entity, source=None):
        if entity.source is None:
            if source is None:
                for alias in entity.alias:
                    if alias.startswith(entity.entity_domain):
                        alias = alias.replace(entity.entity_domain,"")
                        alias = alias.split("/")
                        if 4 == len(alias): 
                            entity.source = alias[2]
                else:
                    entity.alias = "ejerico" if entity.alias is None else entity.alias
            else:
                entity.source = source
                
        for entity_child in entity.__dict__:
            if re.match(r"^[a-zA-Z]+\W*", entity_child):
                if isinstance(entity.__dict__[entity_child],list):
                    for list_entity in entity.__dict__[entity_child]:
                        if isinstance(list_entity, Entity) and list_entity is None:
                            self._setSource(list_entity, source=source)

                if isinstance(entity.__dict__[entity_child], Entity) and entity.__dict__[entity_child].source is None: 
                    self._setSource(entity.__dict__[entity_child], source=source)

    def _injectPreferredKeyworks(self, entity, keywords=None):
        if entity is None or keywords is None: return
        if entity.strbase() not in self._injectPreferredKeyworks._valid_entities: return

        entity.keywords = keywords if entity.keywords is None else "{}, {}".format(entity.keywords, keywords)

        for entity_child in entity.__dict__:
            if re.match(r"^[a-zA-Z]+\W*", entity_child):
                if isinstance(entity.__dict__[entity_child],list):
                    for list_entity in entity.__dict__[entity_child]:
                        if isinstance(list_entity, Entity) and list_entity is None:
                            self._injectPreferredKeyworks(list_entity, keywords=keywords)

                if isinstance(entity.__dict__[entity_child], Entity) and entity.__dict__[entity_child].source is None: 
                    self._injectPreferredKeyworks(entity.__dict__[entity_child], keywords=keywords)

    _injectPreferredKeyworks._valid_entities = (
        "catalog",
        "dataset", 
        "document",
        "facility", 
        "platform"
        "project", 
        "service", 
        "sensor",
        "software", 
        "webservice", 
    )
        
    def _injectPreferredConcepts(self, entity, concepts=None):
        if entity is None or concepts is None or 0 == len(concepts): return
        if entity.strbase() not in self._injectPreferredConcepts._valid_entities: return

        entity.concept = [] if entity.concept is None else entity.concept
        entity.concept = [entity.concept] if not isinstance(entity.concept, list) else entity.concept

        concepts = [c.strip().upper() for c in concepts.split(',')] if isinstance(concepts, str) else concepts
        for concept in concepts:
            entity.concept.append(Concept.buildURI("ejerico", concept))
            
        for entity_child in entity.__dict__:
            if re.match(r"^[a-zA-Z]+\W*", entity_child):
                if isinstance(entity.__dict__[entity_child],list):
                    for list_entity in entity.__dict__[entity_child]:
                        if isinstance(list_entity, Entity) and list_entity is None:
                            self._injectPreferredConcepts(list_entity, keywords=concepts)

                if isinstance(entity.__dict__[entity_child], Entity) and entity.__dict__[entity_child].source is None: 
                    self._injectPreferredConcepts(entity.__dict__[entity_child], keywords=concepts)
        entity.concept =None
    _injectPreferredConcepts._valid_entities = (
        "catalog",
        "dataset", 
        "document",
        "facility", 
        "platform"
        "project", 
        "service", 
        "sensor",
        "software", 
        "webservice", 
    )

    def _buildAliasForIdentifier(self,entity):
        if entity.identifier is not None and 0 != len(entity.identifier):
            for i in range(len(entity.identifier)):
                my_identifier = entity.identifier[i]
                my_identifier.system = my_identifier.system if my_identifier.system is not None else EJERICO
                if 0 == i  and entity._has_autogenerated_ID:
                    entity.id = entity.base().buildURI(my_identifier.system, my_identifier.code)
                entity.alias.append(entity.base().buildSourceURI(my_identifier.system, my_identifier.code))

        if isinstance(entity.identifier, list) and str(entity.id) in Entity._cache_uri_args:
            my_identifier_values = Entity._cache_uri_args[str(entity.id)].split(':')
            my_identifier = Identifier()
            my_identifier.system = my_identifier_values[0] 
            my_identifier.code = ':'.join(my_identifier_values[1:])
            entity.identifier.append(my_identifier)

        for key in entity.attributes():
            value = getattr(entity, key)
            if isinstance(value, list):
                for value_item in value:
                    if isinstance(value_item,Entity): self._buildAliasForIdentifier(value_item)
            elif isinstance(value,Entity): self._buildAliasForIdentifier(value)     

    def _geolocate(self, entity):
        if hasattr(entity, "country") and (not hasattr(entity, "spatial") or entity.spatial is None):
            geopoint = geolocate(country=entity.country, locality=entity.locality if hasattr(entity, "locality") else None)
            if geopoint is not None:
                spatial = Spatial()
                spatial.id = Spatial.buildURI("{}:{}:spatial".format(entity.source if entity.source is not None else entity.namespace, entity.id))
                spatial.alias.append(Spatial.buildSourceURI(entity.source if entity.source is not None else entity.namespace, entity.id))
                spatial.latitude = geopoint[0]; spatial.longitude = geopoint[1]
                spatial.geometry = "{crs}POINT(({lat:.4f} {lng:.4f}))".format(crs="", lat=spatial.latitude, lng=spatial.longitude)
                if not hasattr(entity, "spatial") or entity.spatial is None:
                    entity.spatial = [spatial] 
                else:    
                    entity.spatial.append(spatial)
        
        for key in entity.attributes():
            value = getattr(entity, key)
            if isinstance(value, list):
                for value_item in value:
                    if isinstance(value_item,Entity): self._geolocate(value_item)
            elif isinstance(value,Entity): self._geolocate(value)            

    def _entity_timestamp(self,entity, modified=None, updated=None):
        modified =  entity.modified if modified is None else modified
        modified =  datetime.datetime.now() if modified is None else modified

        entity.modified = modified if entity.modified is None else entity.modified
        entity.modified = max(entity.modified) if isinstance(entity.modified, list) else entity.modified
        entity.modified = parseDatetime(entity.modified) if isinstance(entity.modified, str) else entity.modified
        entity.modified = entity.modified.replace(hour=0, minute=0, second=0, microsecond=0) if entity.modified is not None else entity.modified

        entity.created = entity.modified if entity.created is None else entity.created
        entity.created = min(entity.created) if isinstance(entity.created, list) else entity.created
        entity.created = parseDatetime(entity.created) if isinstance(entity.created, str) else entity.created
        entity.created = entity.created.replace(hour=0, minute=0, second=0, microsecond=0) if entity.created is not None else entity.created

        updated=datetime.datetime.fromtimestamp(entity.harvester.harvesting_timestamp) if entity.harvester is not None else None
        entity.harvested_timestamp = datetime.datetime.now() if updated is None else updated
        entity.harvested_timestamp.replace(second=0, microsecond=0)

        for entity_child in entity.__dict__:
            if re.match(r"^[a-zA-Z]+\W*", entity_child):
                if isinstance(entity.__dict__[entity_child],list):
                    for list_entity in entity.__dict__[entity_child]:
                        if isinstance(list_entity, Entity):
                            self._entity_timestamp(list_entity, modified=modified, updated=updated)

                if isinstance(entity.__dict__[entity_child], Entity): 
                    self._entity_timestamp(entity.__dict__[entity_child], modified=modified, updated=updated)
    def _fix_audit_dates (self, entity):
        try:
            if entity.empty: return

            my_created = my_modified = my_updated = None
            
            stm = self._fix_audit_dates._fix_sentence_SELECT.format(subject=entity.id)
            rst = self.query(stm)
            for r in rst:
                my_created = r["mc"]; my_modified = r["mm"]; my_updated = r["mu"]
                
            my_created = Literal(datetime.datetime.now()) if my_created is None else my_created
            my_modified = Literal(datetime.datetime.now()) if my_modified is None else my_modified
            my_updated = Literal(datetime.datetime.now()) if my_updated is None else my_updated

            stm = self._fix_audit_dates._fix_sentence_DELETE.format(subject=entity.id)
            self.update(stm)

            stm = self._fix_audit_dates._fix_sentence_INSERT.format(subject=entity.id, created=my_created, modified=my_modified, updated=my_updated)
            self.update(stm)

            for entity_child in entity.__dict__:
                if re.match(r"^[a-zA-Z]+\W*", entity_child):
                    if isinstance(entity.__dict__[entity_child],list):
                        for list_entity in entity.__dict__[entity_child]:
                            if isinstance(list_entity, Entity):
                                self._fix_audit_dates(list_entity)
                    if isinstance(entity.__dict__[entity_child], Entity): 
                        self._fix_audit_dates(entity.__dict__[entity_child])
        except Exception as e:
            logging.error("[graph:_fix_audit_dates] error updating dates ({})".format(e))    
    _fix_audit_dates._fix_sentence_SELECT  = """
    SELECT (min(?c) as ?mc) (max(?m) as ?mm) (max(?u) as ?mu)
    WHERE
    {{
        <{subject}> dcterms:created ?c.
        <{subject}> dcterms:modified ?m.
        OPTIONAL
        {{
            <{subject}> ejerico:updated ?u.
        }}
    }}
    """
    _fix_audit_dates._fix_sentence_DELETE  = """
    DELETE
    {{
        <{subject}> ?p ?o.
    }}
    WHERE
    {{
        VALUES (?p) {{ (dcterms:created) (dcterms:modified) (ejerico:updated) }} 
        <{subject}> ?p ?o.
    }}
    """
    _fix_audit_dates._fix_sentence_INSERT  = """
    INSERT
    {{
        <{subject}> dcterms:created "{created}"^^xsd:dateTime.
        <{subject}> dcterms:modified "{modified}"^^xsd:dateTime.
        <{subject}> ejerico:updated "{updated}"^^xsd:dateTime.
    }}
    WHERE
    {{
        <{subject}> rdf:type ?o.
    }}
    """
    _fix_audit_dates._fix_sentence  = """
    DELETE
    {{
        <{subject}> dcterms:created ?oc.
        <{subject}> dcterms:modified ?om.
        <{subject}> ejerico:updated ?ou.
    }}
    INSERT
    {{
        <{subject}> dcterms:created ?mc.
        <{subject}> dcterms:modified ?mm.
        <{subject}> ejerico:updated ?mu.
    }}
    WHERE
    {{
        SELECT (min(?c) as ?mc) (max(?m) as ?mm) (max(?u) as ?mu)
        WHERE
        {{
            <{subject}> dcterms:created ?c.
            <{subject}> dcterms:modified ?m.
            OPTIONAL
            {{
                <{subject}> ejerico:updated ?u.
            }}
        }}
    }}
    """

    def _validate(self, entity):
        is_valid = not entity.empty
        
        if hasattr(entity,"validate"): 
            entity_validate = getattr(entity, "validate"); super_entity_validate = None
            
            entity_super = entity.base()
            if hasattr(entity_super, "validate"):
                super_entity_validate = getattr(super(entity_super, entity), "validate")
                entity.is_valid = super_entity_validate 
                is_valid = is_valid and super_entity_validate()
                
            if super_entity_validate is None or entity_validate != super_entity_validate:
                self_entity_validate = entity_validate()
                entity.is_valid = self_entity_validate
                is_valid = is_valid and self_entity_validate
        
        for entity_child in entity.__dict__:
            if re.match(r"^[a-zA-Z]+\W*", entity_child):
                    if isinstance(entity.__dict__[entity_child],list):
                        for list_entity in entity.__dict__[entity_child]:
                            if isinstance(list_entity, Entity): 
                                is_valid = is_valid and self._validate(list_entity)

                    if isinstance(entity.__dict__[entity_child], Entity): 
                        is_valid = is_valid and self._validate(entity.__dict__[entity_child])
                        
        return is_valid

def _getBaseClass(obj,return_class=False):
        rst = obj.__class__ if return_class else obj.__class__.__name__
        for cls in inspect.getmro(obj.__class__):
            if cls.__name__ == "Entity": break
            rst = cls if return_class else cls.__name__
        return rst

def _get_RDFType(kind):
    mapper = EntityMapper.instance()
    base = mapper.map_class(scope=_getBaseClass(kind))
    base = str(base)

    import rdflib as my_rdflib

    custom_namespaces = [
        ("EJERICO".lower(), str(my_rdflib.EJERICO)),
        ("ADMS".lower(), str(my_rdflib.ADMS)),
        ("SPDX".lower(), str(my_rdflib.SPDX)),
        ("LOCN".lower(), str(my_rdflib.LOCN)),
    ]
    for a in namespace.__dict__:
        if isinstance(namespace.__dict__[a],Namespace) or isinstance(namespace.__dict__[a],ClosedNamespace):
            custom_namespaces.append((a.lower(), str(namespace.__dict__[a])))

    for key,val in custom_namespaces:
        if val in base:
            base = "{}:{}".format(key, base.replace(val,"")) 

    return base

_SPARQL_QUERY_FIND_ENTITY_BY_URI_KIND = """
    ###prefixes###

    SELECT DISTINCT ?s
    WHERE {
        VALUES (?o) { ###values### }
        ?s adms:identifier ?o.
        ?s rdf:type ###kind###.
    }
"""

_SPARQL_QUERY_FIND_ENTITY_BY_URI = """
    ###prefixes###

    SELECT DISTINCT ?s
    WHERE {
        VALUES (?o) { #values# }
        ?s adms:identifier ?o.
    }
"""
_SPARQL_QUERY_FIND_ENTITY_BY_URI_KIND_ONE_BY_ONE = """
    ###prefixes###

    SELECT DISTINCT ?s
    WHERE {
        ?s adms:identifier ###value###.
        ?s rdf:type ###kind###.
    }
"""

_SPARQL_QUERY_FIND_ENTITY_BY_URI_ONE_BY_ONE = """
    ###prefixes###

    SELECT DISTINCT ?s
    WHERE {
        ?s adms:identifier ###value###.
    }
"""
_SPARQL_QUERY_FIND_RELATED_ENTITY_BY_URI = """
    ###prefixes###

    SELECT DISTINCT ?s
    WHERE {
        ?s ?p <###uri###>.
    }
"""

_SPARQL_QUERY_FIND_ENTITY_BY_URL = """
    ###prefixes###

    SELECT DISTINCT ?s ?o
    WHERE {
        ?s rdf:type ?o.
        ?s sdo:url '###value###'.
    }
"""

_SPARQL_QUERY_GET_ENTITY_BY_URI = """
    ###prefixes###

    SELECT ?p ?o
    WHERE {
        <###uri###> ?p ?o.
    }
"""

_SPARQL_DELETE_ENTITY_BY_URI_AS_SUBJECT = """
    ###prefixes###

    DELETE
    WHERE {
        <###uri###> ?p ?o.
    }
"""
_SPARQL_DELETE_ENTITY_BY_URI_AS_OBJECT = """
    ###prefixes###

    DELETE
    WHERE {
        ?s ?p <###uri###>.
    }
"""

_SPARQL_GET_TOTAL_SUBJECTS_BY_RDFTYPE = """
    ###prefixes###

    SELECT (COUNT ?s) as ?c
    WHERE 
    {
        ?s rdf:type <###rdftype###>.
    }
"""

_SPARQL_GET_SUBJECTS_BY_RDFTYPE = """
    ###prefixes###

    SELECT ?s
    WHERE 
    {
        ?s rdf:type <###rdftype###>.
    }
    LIMIT ###size###
    OFFSET ###offset###
"""
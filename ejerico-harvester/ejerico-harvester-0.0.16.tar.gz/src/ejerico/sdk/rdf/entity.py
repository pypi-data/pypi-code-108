"""TODO doc"""

import ast
import dateutil
import inspect
import hashlib
import json
import os
import re
import sys
from numpy import False_
import pkg_resources
import traceback
import threading
import uuid
import logging

import requests

from pathlib import Path
from datetime import datetime
from functools import reduce,partial, lru_cache
from validator_collection import checkers, errors

from rdflib import plugin
from rdflib import Graph
from rdflib import namespace
from rdflib import Literal, URIRef, BNode
from rdflib.exceptions import Error
from rdflib.namespace import Namespace, ClosedNamespace, DefinedNamespace, URIPattern
from rdflib.store import Store, VALID_STORE

from rdflib.plugins.sparql.processor import SPARQLResult

from ejerico.sdk.rdf.impl.api import ApiImpl
from ejerico.sdk.rdf.impl.api_operation import ApiOperationImpl, ApiOperationParameterImpl
from ejerico.sdk.rdf.impl.address import AddressImpl
from ejerico.sdk.rdf.impl.catalog import CatalogImpl
from ejerico.sdk.rdf.impl.concept import ConceptImpl 
from ejerico.sdk.rdf.impl.concept_scheme import ConceptSchemeImpl
from ejerico.sdk.rdf.impl.contact_point import ContactPointImpl
from ejerico.sdk.rdf.impl.dataset import DatasetImpl
from ejerico.sdk.rdf.impl.distribution import DistributionImpl
from ejerico.sdk.rdf.impl.document import DocumentImpl
from ejerico.sdk.rdf.impl.equipment import EquipmentImpl
from ejerico.sdk.rdf.impl.facility import FacilityImpl
from ejerico.sdk.rdf.impl.frequency import FrequencyImpl
from ejerico.sdk.rdf.impl.identifier import IdentifierImpl
from ejerico.sdk.rdf.impl.organization import OrganizationImpl
from ejerico.sdk.rdf.impl.platform import PlatformImpl
from ejerico.sdk.rdf.impl.person import PersonImpl
from ejerico.sdk.rdf.impl.program import ProgramImpl
from ejerico.sdk.rdf.impl.project import ProjectImpl
from ejerico.sdk.rdf.impl.variable import VariableImpl
from ejerico.sdk.rdf.impl.relation import RelationImpl
from ejerico.sdk.rdf.impl.spatial import SpatialImpl
from ejerico.sdk.rdf.impl.sensor import SensorImpl
from ejerico.sdk.rdf.impl.service import ServiceImpl
from ejerico.sdk.rdf.impl.software import SoftwareImpl
from ejerico.sdk.rdf.impl.software_source import SoftwareSourceImpl
from ejerico.sdk.rdf.impl.temporal import TemporalImpl
from ejerico.sdk.rdf.impl.text import TextImpl
from ejerico.sdk.rdf.impl.vcard import VcardImpl
from ejerico.sdk.rdf.impl.webservice import WebServiceImpl

from ejerico.sdk.exceptions import GraphError
from ejerico.sdk.config import ConfigManager
from ejerico.sdk.utils import isPrimitive, parseDatetime, is_sha1, countWordOcurrences, to_dict_lowercase
from ejerico.sdk.utils import parseDatetime, camelCaseToSnakeCase, snakeCaseToCamelCase, tokenize_name, format_email, geolocate
from ejerico.sdk.annotations import singleton
from ejerico.sdk.exceptions import ValidationError

## INJECT ALL rdflib.namespace (included custom defined)
try:
    for n in dir(namespace):
        o = getattr(namespace, n)
        if isinstance(o, Namespace) or isinstance(o, ClosedNamespace):
            setattr(sys.modules[__name__], n, o)
        if "DefinedNamespaceMeta" == o.__class__.__name__:
            setattr(sys.modules[__name__], n, o)
except Exception as e:
    pass

__all__= [
    "Api",
    "ApiOperation",
    "ApiOperationParameter",
    "Catalog",
    "Concept",
    "ConceptScheme",
    "ContactPoint",
    "Dataset",
    "Distribution",
    "Document",
    "Equipment",
    "Identifier",
    "Facility",
    "Frequency",
    "Organization",
    "Person",
    "Platform",
    "Program",
    "Project",
    "Relation",
    "Spatial",
    "Sensor",
    "Service",
    "Software",
    "SoftwareSource",
    "Temporal",
    "Variable",
    "Vcard",
    "WebService",
]


class EntityMetaclass(type):
    def __new__(cls, name, bases, attributes):
        config = ConfigManager.instance()
        domain = config.get("domain", default=ConfigManager.instance().defaultDOMAIN)
        domain = domain if checkers.is_url(domain) else "http://{}".format(domain)
        
        attributes["__entity_domain"] = domain
        attributes["__entity_type"] = name.lower()
        attributes["__uri_pattern"] = URIPattern("{}/{}".format(domain,"{scope}/{id}"))
        attributes["__source_uri_pattern"] = URIPattern("{}/{}".format(domain,"{scope}/{source}/{id}"))

        get__domain = lambda self: getattr(self, "__entity_domain")
        attributes["entity_domain"] = property(fget=get__domain) 

        get__entity_type = lambda self: getattr(self, "__entity_type")
        attributes["entity_type"] = property(fget=get__entity_type)

        get__uri_pattern = lambda self: getattr(self, "__uri_pattern")
        attributes["uri_pattern"] = property(fget=get__uri_pattern)

        get__source_uri_pattern = lambda self: getattr(self, "__source_uri_pattern")
        attributes["source_uri_pattern"] = property(fget=get__source_uri_pattern)
        
        return type.__new__(cls, name, bases, attributes) 

class Entity(object, metaclass=EntityMetaclass):

    _excluded_attributes = ("mapper","entity_type","scope","rdf_type","uri_pattern", "source_uri_pattern", "entity_domain", "is_raw_id", "is_valid")
    _rdf_types = {}
    _entity_classes = {}
    _metadata = {}
    _scopes = {}
    _cache = {}
    _attributes_cache = {}
    _cache_uri_patters = {}
    _cache_scopes = {}
    _cache_uri_args = {}
    _re_pattern_attributes = re.compile(r"^[a-zA-Z]+\W*")
    _re_pattern_datetime = re.compile(r'\d{2,4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}')

    def __init__(self, id=None, first_born=False, is_raw_id=False, namespace=None, source=None):
        id = str(id) if id is not None and not isinstance(id, str) else id

        s_uid = "{}".format(uuid.uuid4().hex) if id is None else id
        s_uid = s_uid.replace(" ", "%20")
        
        is_raw_id = is_raw_id or s_uid.startswith(self.entity_domain)

        if checkers.is_url(s_uid):
            h_uid = s_uid if is_raw_id else hashlib.sha1(s_uid.encode("utf-8")).hexdigest()
        elif checkers.is_email(id):
            h_uid = "mailto:{}".format(id) if not id.startswith("mailto:") else s_uid
        else:
            h_uid = hashlib.sha1(s_uid.encode("utf-8")).hexdigest() if not re.match(r"\b[0-9a-z]{40}\b", s_uid) else s_uid

        self._scope = self._getBaseClass().lower()

        if is_raw_id:
            self._id = h_uid
        else:                
            self._id = URIRef(self.uri_pattern.format(scope=self._scope, id=h_uid))

        self._first_born = first_born

        self.is_raw_id = is_raw_id
        self.source = source

        self._namespace = namespace if namespace else "ejerico"
        self._delete_on_save = False
        self._has_autogenerated_ID = (id is None)
        
        c = countWordOcurrences(str(self._id), "http")
        if  c > 1: raise ValidationError("not valid uri ({})".format(str(self._id)))
        if not checkers.is_url(str(self._id)) and not checkers.is_email(str(self._id)): 
            raise ValidationError("not valid uri ({})".format(str(self._id)))

        self.alias = []#[self._id] 
        if checkers.is_url(s_uid) or checkers.is_email(s_uid): self.alias.append(s_uid)

        self.identifier = []

        self.mapper = get_mapper()

        self._rdf_type = self.mapper.map_class(self._scope, caller=self.entity_type)

        #common attributes
        self.parent = None
        self.program = None
        self._is_valid = True
        self._harvester = None

        self.concept = None
        self.description = None
        self.name = None
        self.keywords = None
        self.spatial = None
        self.temporal = None
        self.created = None
        self.modified = None
        self.type = None
        self.is_related_to = None
        self.visibility = None
        self.status = None
        self.language = None
        #self.search_terms = None
        
        
        self._valid_attributes = []
        for attr in self.__dict__:
            if attr in self._excluded_attributes: continue
            if attr.startswith('_'): continue
            self._valid_attributes.append(attr)

    @classmethod
    def metadata(cls, schema=None, caller=None):
        config = ConfigManager.instance()
        mapper = EntityMapper.instance()
        
        schema = config.get("mapping_schema", default="ejerico") if schema is None else schema

        scope = cls.base()
        scope = scope.__name__.lower()

        key = "{}:{}".format(schema, scope)
        
        if key in Entity._metadata: return Entity._metadata[key] 
        
        rdf_type = mapper.map_class(scope=scope, caller=cls.__name__, schema=schema)
        rdf_type_redefinitions = []
        for clazz in [clazz for clazz in inspect.getmembers(sys.modules[__name__], inspect.isclass) if issubclass(clazz[1], Entity)]:
            rdf_type_redefinition = mapper.map_class(scope=scope, caller=clazz[1].base().__name__.lower(), schema=schema, strict=True)
            if rdf_type_redefinition  is not None: rdf_type_redefinitions.append((clazz[0], rdf_type_redefinition))

        if rdf_type is None and not len(rdf_type_redefinitions): return None

        rdf_type = rdf_type_redefinitions[0][1] if caller is not None and len(rdf_type_redefinitions) else rdf_type 
        metadata = {"rdf_type": rdf_type, "rdf_type_redefinitions": rdf_type_redefinitions}

        instance = cls()
        for attr in instance.__dict__:
            if not re.match(r"^[a-zA-Z]+\W*", attr): continue
            if attr in instance._excluded_attributes: continue
            metadata[attr] = mapper.map_property(attr, scope=scope, caller=cls.__name__, schema=schema)

        Entity._metadata[key] = metadata
        return metadata 

    @staticmethod
    def rdf_types():
        if not Entity._rdf_types: 
            clazzes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
            for clazz in clazzes:
                if issubclass(clazz[1], Entity): 
                    instance = clazz[1]()
                    Entity._rdf_types[clazz[1]] = {"rdf_type": instance._rdf_type}
                    Entity._rdf_types[clazz[1]].update(instance.rdf_type_for_attributes)
        return Entity._rdf_types
    
    @staticmethod
    def scopes():
        if not Entity._scopes: 
            clazzes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
            for clazz in clazzes:
                if issubclass(clazz[1], Entity) and "Entity" != clazz[0]: 
                    Entity._scopes[clazz[1].strbase()] = clazz[1]
        return Entity._scopes

    
    @classmethod
    def base(cls):
        clazzes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        clazzes = [c[1] for c in clazzes]
        for cls in inspect.getmro(cls):
            if cls in clazzes: return cls
        return Entity

    @classmethod
    def strbase(cls):
        clazz = cls.base()
        return clazz.__name__.lower()

    @classmethod
    def buildURI(cls, *args):
        args = [str(a) for a in args]
        args = [a.strip() for a in args]
        uid = ":".join(args)
        uid = uid if isinstance(uid, str) else str(uid)

        if cls.__name__ not in Entity._cache_uri_patters:
            my_self = cls()
            Entity._cache_uri_patters[cls.__name__] = my_self.uri_pattern
            Entity._cache_scopes[cls.__name__] = my_self.scope
        my_uri = Entity._cache_uri_patters[cls.__name__]
        my_scope = Entity._cache_scopes[cls.__name__]

        if not is_sha1(uid):
            my_uri = my_uri.format(scope=my_scope, id=hashlib.sha1(uid.encode("utf-8")).hexdigest())
        else:
            my_uri = my_uri.format(scope=my_scope, id=uid)

        Entity._cache_uri_args["{}".format(my_uri)] = "{}".format(uid)
        return my_uri

    @classmethod        
    def buildSourceURI(cls, source, *args):
        if isinstance(source, list):
            if args: 
                args.extend(source[1:]) 
            else:
                args = source[1:] 
            source = source[0]

        args = [str(a) for a in args]
        args = [a.strip() for a in args]
        
        uid = ":".join(args)
        uid = uid if isinstance(uid, str) else str(uid)
        
        my_self = cls()
        my_uri = my_self.source_uri_pattern
        my_scope = my_self.scope

        if not is_sha1(uid):
            my_uri = my_uri.format(scope=my_scope, source=source, id=hashlib.sha1(uid.encode("utf-8")).hexdigest())
        else:
            my_uri = my_uri.format(scope=my_scope, source=source, id=uid)
            
        return my_uri

    
    @staticmethod
    def getInstanceFromRDFType(rdf_type, id):
        entity_instance = Entity.getEntityFromRDFType(rdf_type)
        if entity_instance is not None:
            entity_instance = entity_instance()
            entity_instance.id = id if id is not None else entity_instance.id
        return entity_instance
    
    
    @staticmethod
    def getRDFTypeForEntity(entity_class):
        rst = None
        if issubclass(entity_class, Entity):
            if not Entity._rdf_types: Entity.rdf_types()
            return Entity._rdf_types[entity_class]["rdf_type"] if entity_class in Entity._rdf_types and "rdf_type" in Entity._rdf_types[entity_class] else None
        else:
            logging.info("[Entity:getRDFTypeForEntity] {} is not a Entity class", entity_class.__name__)
        return rst

    @staticmethod
    def getEntityFromRDFType(rdf_type, return_as_string=False):
        if rdf_type is None or not isinstance(rdf_type, str): 
            logging.info("[Entity:getEntityFromRDFType] 'rdf_type' must be a string")
            return None

        mapper = get_mapper()

        entity_class = mapper.unmap_class(str(rdf_type))
        if return_as_string:
            return entity_class.capitalize() if entity_class is not None else None

        entity_classes = Entity.__getEntityClasses()

        if entity_class is not None and entity_class in entity_classes: 
            entity_class = entity_classes[entity_class]
        else: 
            logging.info("[Entity:getEntityFromRDFType] not Entity class found for 'rdf_type ({})'".format(rdf_type))

        return entity_class
    
    @classmethod
    def getRDFPredicateFromAtribute(cls, name):
        entity_classes = Entity.__getEntityClasses()
        for key,val in entity_classes.items(): 
            if val == cls:
                mapper = get_mapper()
                rdf_predicate = mapper.map_property(name=str(name))
                return str(rdf_predicate) if rdf_predicate else rdf_predicate
        logging.info("[Entity:getRDFPredicateFromAtribute] not found mapping for {}.{}".format(cls.__name__, name))

    @staticmethod
    def getEntityClassFromURI(uri):
        if uri is None or not isinstance(uri, str): return None
        if not hasattr(Entity, "_z_cache_scopes"): setattr(Entity, "_z_cache_scopes", Entity.scopes())

        my_uri = str(uri)
        for p in (Entity.patternURI(), Entity.patternSourceURI()):
            m = re.match(p, my_uri)
            if m:
                my_scope = m.group("rdftype")
                if my_scope in Entity._z_cache_scopes: 
                    return Entity._z_cache_scopes[my_scope]
        return None

        
    @staticmethod
    def __getEntityClasses():
        if not Entity._entity_classes:
            for clazz in inspect.getmembers(sys.modules[__name__], inspect.isclass):
                if issubclass(clazz[1], Entity): Entity._entity_classes[clazz[0].lower()] = clazz[1]
        return Entity._entity_classes

    @staticmethod
    def isInternalURI(uri):
        if uri is None: return False
        if not isinstance(uri,str) and not isinstance(uri,URIRef): return False
        uri = str(uri)
        return uri.startswith(ConfigManager.instance().get("domain", default=ConfigManager.instance().defaultDOMAIN))

    @staticmethod
    def patternURI():
        entities = '|'.join(sorted([c for c in Entity.scopes()]))
        domain = ConfigManager.instance().get("domain", default=ConfigManager.instance().defaultDOMAIN)
        return re.compile("{domain}/(?P<rdftype>({entities}))/(?P<id>[\w]+)".format(domain=domain, entities=entities))
    @staticmethod
    def patternSourceURI():
        entities = '|'.join(sorted([c for c in Entity.scopes()]))
        domain = ConfigManager.instance().get("domain", default=ConfigManager.instance().defaultDOMAIN)
        return re.compile("{}/(?P<rdftype>({}))/(?P<source>[\w]+)/(?P<id>[\w]+)".format(domain, entities))

    @property
    def scope(self):
        return self._scope

    @property
    def rdf_type(self):
        return self._rdf_type

    @property
    def rdf_type_for_attributes(self):
        rst = {}
        for attr in self.__dict__:
            if not re.match(r"^[a-zA-Z]+\W*", attr): continue
            if attr in self._excluded_attributes: continue

            attr_filter = None
            for attr_suffix in ("_min", "_max", "_like", "_equal", "_not_equal", "_not_exist"):
                if attr.endswith(attr_suffix):
                    attr_filter = attr_suffix[1:]
                    attr = attr[:-len(attr_filter)-1]

            rst[attr] = self.mapper.map_property(attr, scope=self.scope, caller=self.entity_type)

            if "alias" == attr:
                if False and 0 != len(self.__dict__[attr]): logging.info("TODO conditions alias IN")
            elif self.__dict__[attr] is not None:
               rst["{}_equal".format(attr)] = "TODO equals" 

            if attr_filter is not None:
                attr = "{}_{}".format(attr, attr_filter)
                if True: #self.__dict__[attr] is not None:
                    attr_filter_expression = "TODO {}({})".format(attr, self.__dict__[attr])
                    rst[attr] = attr_filter_expression
        return rst

    @property
    def harvester(self):
        return self._harvester
        
    @property
    def id(self):
        return URIRef(self._id)
    @id.setter
    def id(self,value):
        if value is not None and isinstance(value,str):
            value = value.strip()
            self.alias = [a for a in self.alias if str(a) != str(self.id)]
            
            value = value.strip()
            if checkers.is_url(value) or checkers.is_email(value):
                self._id = URIRef(value) 
            else:
                if not re.match(r"\b[0-9a-z]{40}\b", value): value = hashlib.sha1(value.encode("utf-8")).hexdigest()
                self._id = URIRef(self.uri_pattern.format(scope=self._scope, id=value)) 

            self._has_autogenerated_ID = False

            c = countWordOcurrences(str(self._id), "http")
            if  c > 1 or not checkers.is_url(str(self._id)): raise ValidationError("not valid uri ({})".format(str(self._id)))

            self.alias.append(self._id)
              
    @property
    def first_born(self):
        return self._first_born
    @first_born.setter
    def first_born(self, value):
        self._first_born = True if value else False
    
    @property
    def is_valid(self):
        return self._is_valid
    @is_valid.setter
    def is_valid(self, value):
        self._is_valid = value

    @property
    def delete_on_save(self):
        return self._delete_on_save
    @delete_on_save.setter
    def delete_on_save(self, value):
        self._delete_on_save = True if value else False

    @property
    def namespace(self):
        return self._namespace
    @namespace.setter
    def namespace(self, value):
        self._namespace = value

    # @property
    # def source(self):
    #     return self._source
    # @source.setter
    # def source(self, value):
    #     self._source = value

    @property
    def empty(self):
        is_empty = self._has_autogenerated_ID
        for key in self.attributes():
            if "id" == key: continue
            if "alias" == key: is_empty = is_empty and (len([a for a in self.alias if not a.startswith(self.entity_domain)]) == 0); continue
            if "source" == key: continue
            
            value = getattr(self, key)
            if isinstance(value, Entity):
                is_empty = is_empty and value.empty
            elif isinstance(value, list):
                for item in value: 
                    if isinstance(item, Entity):
                        is_empty = is_empty and item.empty
                    else:
                        is_empty = is_empty and False
            else:
                is_empty = is_empty and False

        return is_empty
    
    @property
    def scaffold(self):
        c = self.isInstanceOf()
        i = c()
        i.first_born = self.first_born
        i.is_raw_id = self.is_raw_id
        i.id = self.id
        return i
    
    def setAttributeFromRDFValue(self, rdf_predicate, value, overwrite=True):
        if rdf_predicate is None or not isinstance(rdf_predicate, str):
            logging.info("[Entity:setAttributeFromRDFValue] rdf_predicate must be a string")
        else:
            mapper = get_mapper()
    
            entity_attribute = mapper.unmap_property(rdf_predicate, scope=self._getBaseClass().lower())
            
            if entity_attribute is None:
                logging.info("[Entity:setAttributeFromRDFValue] not found mapping for predicate '{}'".format(rdf_predicate))
            else:
                if isinstance(value, str) or isinstance(value, URIRef):
                    value = str(value)
                    if value.startswith(self.entity_domain):
                        entity_classes = Entity.__getEntityClasses()

                        value_id,value = value, value.replace(self.entity_domain, "").split("/")
                        value = value[1]
                        if value in entity_classes:
                            value = entity_classes[value]()
                            value.id = value_id

                my_entity_attribute = getattr(self, entity_attribute) if hasattr(self, entity_attribute) else None
                
                if overwrite or my_entity_attribute is None:
                    setattr(self, entity_attribute, value)
                elif isinstance(my_entity_attribute, list):
                    if isinstance(value, list):
                        for my_value in value: self.setAttributeFromRDFValue(rdf_predicate, my_value, overwrite=overwrite)
                    else:
                        my_entity_attribute.append(value)
                else:
                    setattr(self, entity_attribute, [my_entity_attribute, value])

    def __str__(self):
        return self.serialize()
        
    def getChildEntityByURI(self,uri):
        if uri is None: return
        if not isinstance(uri, URIRef): return

        child = None
        for attr in self.__dict__:
            value = self.__dict__[attr]
            if isinstance(value, Entity):
                if value.id == uri: return value
                for uri_alias in value.alias:
                    if uri_alias == uri: return value
                child = child or value.getChildEntityBy(uri)
            elif isinstance(value, list): 
                for item in value:
                    if item.id == uri: return item
                    for uri_alias in item.alias:
                        if uri_alias== uri: return item
                    child = child or item.getChildEntityBy(uri)
        return child

    def merge(entity):
        if entity is None: return
        if not isinstance(entity, Entity): return

        base_self = self._getBaseClass()
        base_entity = entity._getBaseClass()
        if base_self != base_entity: return

        if base_self.id != base_entity.id: return

        for entity_attr in entity.__dict__:
            if entity_attr in self.__dict__:
                entity_value = entity.__dict__[entity_attr]
                if isinstance(entity_value, Entity):
                    self.__dict__[entity_attr].merge(entity_value)
                elif isinstance(entity_value, list):
                    entity_found = False
                    for self_value in self.__dict__[entity_attr]:
                        if self_value.id == entity_value: 
                            self_value.merge(entity_value)
                            entity_found = True
                    if not entity_found:
                        self.__dict__[entity_attr].append(entity_value)
                else:
                    self.__dict__[entity_attr] = entity_value
            else:
                self.__dict__[attr] = entity.__dict__[attr]

    def toGraph(self, schema=None):
        g = Graph()
        self._register_namespaces(g)

        tiplets = self._to_tiplets(schema=schema)
        for tiplet in tiplets:
            try:
                g.add(tiplet)
            except:
                logging.info(tiplet)
        return g     

    def toTurtle(self, schema=None): 
        g = self.toGraph(schema=schema) 
        rep_turtle = g.serialize(format="turtle")
        g.close()
        return rep_turtle.decode("utf-8") if  hasattr(rep_turtle, "decode") else rep_turtle

    def toJSONLD(self, schema=None): 
        g = self.toGraph(schema=schema)
        rep_jsonld = g.serialize(format="json-ld")
        g.close()
        return rep_jsonld.decode("utf-8") if  hasattr(rep_jsonld, "decode") else rep_jsonld

    def toXML(self, schema=None): 
        g = self.toGraph(schema=schema)
        rep_xml = g.serialize(format="xml").decode("utf-8")
        g.close()
        return rep_xml.decode("utf-8") if  hasattr(rep_xml, "decode") else rep_xml
    
    def toN3(self, schema=None): 
        g = self.toGraph(schema=schema)
        rep_n3 = g.serialize(format="n3").decode("utf-8")
        g.close()
        return rep_n3.decode("utf-8") if  hasattr(rep_n3, "decode") else rep_n3

    def copyTo(self, entity):
        if entity is None: return None
        for key in self.__dict__:
            if key.startswith('_'): continue
            if key in ("alias","id", "mapper"): continue
            if self.__dict__[key] is None: continue
            setattr(entity, key, self.__dict__[key])
        return entity

    def buildEntityList(self, names, emails, separator=";"):
        lst = []

        entity_names = names.split(separator) if names is not None else []
        entity_emails = emails.split(separator) if emails is not None else []
        
        lst_size = max(len(entity_names), len(entity_emails))
        entity_names = [entity_names[i] if i < len(entity_names) else None for i in range(lst_size)]
        entity_emails = [entity_emails[i] if i < len(entity_emails) else None for i in range(lst_size)]

        for i in range(lst_size):
            if lst is None: lst = []
            entity = self.__class__()
            entity = self.copyTo(entity)
            entity.name = entity_names[i]
            entity.email = entity_emails[i]
            
            if entity.email is not None:
                entity.id = self.buildURI(format_email(entity.email))
                entity.alias.append("mailto:{}".format(format_email(entity.email)))
            elif entity.name is not None: 
                entity.id = self.buildURI(tokenize_name(entity.name))

            lst.append(entity)

        return lst[0] if 1 == len(lst) else lst
    
    def serialize(self, to_jsonld=False):
        return json.dumps(self._serialize(to_jsonld=to_jsonld))

    def _serialize(self, to_jsonld=False):
        serialized = {}

        if to_jsonld:
            serialized["@id"] = self.id
            serialized["@type"] = self._getBaseClass()
            serialized["@context"] = {}
        else:
            serialized["_class"] = self._getBaseClass()

        for attr in self.__dict__:
            if not re.match(r"^[a-zA-Z]+\W*", attr): continue
            if attr in self._excluded_attributes: continue
            
            value = self.__dict__[attr]
            if value is None: continue

            lst = [value] if not isinstance(value, list) else value
            rst = []

            for value in lst:  
                if isinstance(value, Entity) or issubclass(value.__class__, Entity):
                    rst.append(value._serialize())
                    if to_jsonld:
                        serialized["@context"] = {attr: {}}
                        serialized["@context"][attr]["@id"] = value.id
                        serialized["@context"][attr]["@type"] = value._getBaseClass()
                    else:
                        serialized["{}_class".format(attr)] = value._getBaseClass()
                else:
                    if isinstance(value, datetime): 
                        rst.append(value.isoformat())
                    else:
                        rst.append(value)
            
            serialized[attr] = rst[0] if 1 == len(rst) else rst

        return serialized

    
    @classmethod
    def deserialize(clazz, serialized_content, target_class=None, from_jsonld=False):
        deserialized = json.loads(serialized_content)

        if target_class is None and "_class" in deserialized:
            if from_jsonld:
                target_class = deserialized["@type"]
            else: 
                target_class = deserialized["_class"] 
            for c in inspect.getmembers(sys.modules[__name__], inspect.isclass):
                if c[0].lower() == target_class.lower(): 
                    target_class = c[1]
                    break
        if target_class is None: target_class = clazz 

        if not isinstance(target_class, Entity) and not issubclass(target_class, Entity): return None
        
        return target_class._deserialize(deserialized, from_jsonld=from_jsonld)

    
    @classmethod        
    def _deserialize(clazz, data, from_jsonld=False):
        def _deserialize_found_class(clazz): 
            my_module = inspect.getmodule(Entity)
            for key in my_module.__dict__:
                if key == clazz: return my_module.__dict__[key]
            return None
    
        my_object = clazz()
        re_datetime = Entity._re_pattern_datetime

        for key,val in data.items():
            if val is None: continue
            if key.endswith("_class"): continue
            if key.endswith("_namespace"):
                my_object._namespace = val 
                continue
            
            if isinstance(val, list):
                values = []
                
                for my_val in val:
                    #TODO fix it to handle deserilization from json-ld
                    key_class = "{}_class".format(key)
                    if key_class in data:
                        my_clazz = _deserialize_found_class(data[key_class])
                        if my_clazz is not None:
                            my_val = my_clazz._deserialize(my_val)
                            values.append(my_val)
                    else:
                        if isinstance(my_val, dict):
                            if "_class" not in my_val: raise GraphError("not found _class attribute in serialized content")
                            my_clazz = _deserialize_found_class(my_val["_class"])
                            if my_clazz is not None:
                                my_val = my_clazz._deserialize(my_val)
                                setattr(my_object, key, my_val)
                        else:
                            if isinstance(my_val, str)  and re.match(re_datetime, my_val):
                                my_val = parseDatetime(my_val,date_format="%Y-%m-%dT%H:%M:%S")
                        values.append(my_val)
                
                if "alias" == key:
                    my_object.alias.extend(values)
                else:
                    setattr(my_object, key, values)
            else:
                key_class = "{}_class".format(key)
                if key_class in data:
                    my_clazz = _deserialize_found_class(data[key_class])
                    if my_clazz is not None:
                        val = my_clazz._deserialize(val)
                        setattr(my_object, key, val)
                elif isinstance(val, dict):
                    if "_class" not in val: raise GraphError("not found _class attribute in serialized content")
                    my_clazz = _deserialize_found_class(val["_class"])
                    if my_clazz is not None:
                        val = my_clazz._deserialize(val)
                        setattr(my_object, key, val)
                else:
                    if isinstance(val, str)  and re.match(re_datetime, val):
                        my_val = parseDatetime(val,date_format="%Y-%m-%dT%H:%M:%S")
                        val = val if my_val is None else my_val
                    
                    if "alias" == key:
                        my_object.alias.append(val)
                        if not hasattr(my_object, "name") and checkers.is_url(val): my_object.name = val
                    else:
                        setattr(my_object, key, val)
        
        # if "id" in data:
        #     pass
        # elif "alias" in data:
        #     if "id" not in data:
        #         my_object.id = my_object.alias[0] if isinstance(my_object.alias, list) else my_object.alias
        # elif "url" in data:
        #     my_object.id = my_object.url

        if from_jsonld:
            my_object.id = data["@id"]

        return my_object

    
    @staticmethod
    def load(data, format="turtle", subjects_with_types=None):
        graph = None

        if isinstance(data, str):
            graph = Graph()
            graph.parse(data=data, format=format)
        if isinstance(data, SPARQLResult):
            graph = Graph()
            for tiplet in data:
                graph.add((tiplet[0], tiplet[1], tiplet[2]))
        if isinstance(data, Graph):
            graph = data

        if graph is None:
            logging.info("[Entity:load] data must be instance of str, SPARQLResult or Graph")
            return None
            
        entities = {}
        mapper = get_mapper()
        #mapper._fix_unknownMappingIssues()

        my_module = inspect.getmodule(mapper)
        
        #P-1 get entities in graph with type
        rows = graph.query(SPARQL_LOAD_GET_ENTITIES) if subjects_with_types is None else subjects_with_types
        for row in rows:
            classname = mapper.unmap_class(row[1])
            classname_class = None
            for key in my_module.__dict__:
                if key.lower() == classname.lower():
                    my_entity = my_module.__dict__[key]()
                    my_entity.id = str(row[0])
                    my_entity._classname = classname
                    my_entity._in = 0
                    my_entity._out = 0
                    entities[str(row[0])] = my_entity
                    classname_class = my_entity.__class__
            else:
                if classname_class is None:
                    my_entity = type(classname, (Entity))()
                    my_entity.id = str(row[0])
                    my_entity._classname = classname
                    my_entity._in = 0
                    my_entity._out = 0
                    entities[str(row[0])] = my_entity

        #P-2 get entity tiplets by ID (rebuild relations)
        for uri in entities:
            rows = graph.query(SPARQL_LOAD_GET_ENTITY.replace("###URI###", uri)) 
            for row in rows:
                propertyName = mapper.unmap_property(row[0], scope=entities[uri]._classname)
                if propertyName is not None:
                    if hasattr(entities[uri], propertyName): setattr(entities[uri], propertyName, None)
                    my_object = row[1]

                    if "alias" == propertyName and str(uri) == str(my_object): continue
                    if "identifier" == propertyName and propertyValue is not None:
                        my_identifier = propertyValue.toPython()
                        propertyValue = Identifier()
                        propertyValue.fromString(my_identifier) 

                    entity_property = getattr(entities[uri], propertyName, None)
                    if entity_property is not None and not isinstance(entity_property, list):
                        entity_property = [entity_property]
                    if isinstance(my_object, URIRef):
                        my_object = str(my_object)
                        if my_object in entities:
                            entities[my_object]._in += 1
                            entities[uri]._out += 1

                            if entity_property is not None:
                                entity_property.append(entities[my_object])
                            else:
                                entity_property = entities[my_object]
                        else:
                            if entity_property is not None:
                                entity_property.append(my_object)
                            else:
                                entity_property = my_object
                        setattr(entities[uri], propertyName, entity_property)
                    elif isinstance(my_object, Literal):
                        if entity_property is not None:
                            if not isinstance(entity_property, list):
                                entity_property = [entity_property]
                            entity_property.append(my_object.toPython())
                        else:
                            entity_property = my_object.toPython()
                        setattr(entities[uri], propertyName, entity_property)
                    elif isinstance(propertyValue, Entity):
                        if propertyEntity is not None:
                            propertyEntity.append(propertyValue)
                        else:
                            propertyEntity = propertyValue
                            setattr(entities[uri], propertyName, propertyEntity)
                    else:
                        logging.info("[Entity:load] object is not UriRef or Literal ")
                elif str(row[0]) in (
                    "{}source".format(ConfigManager.instance().defaultNAMESPACE), 
                    "{}updated".format(ConfigManager.instance().defaultNAMESPACE),
                    "{}hash".format(ConfigManager.instance().defaultNAMESPACE),
                    ):
                    if "{}source".format(ConfigManager.instance().defaultNAMESPACE) == str(row[0]):
                        setattr(entities[uri], "source", str(row[1]))
                    if "{}updated".format(ConfigManager.instance().defaultNAMESPACE) == str(row[0]):
                        setattr(entities[uri], "updated", parseDatetime(str(row[1])))
                    if "{}hash".format(ConfigManager.instance().defaultNAMESPACE) == str(row[0]): 
                        pass
                elif not row[0].endswith("#type"):
                    logging.info("[Entity:load] unknown property name '{}'".format(str(row[0])))

        #P-3 filter result
        entities = [entities[e] for e in entities if 0 == entities[e]._in or 1 == len(entities) ]
        return entities[0] if 1 == len(entities) else entities

    def _buildURI(self, uid):
        is_uri = uid.startswith("http://") or uid.startswith("https://") or uid.startswith("mailto:")
        if not is_uri:
            h_uid = uid if is_sha1(uid) else hashlib.sha1(uid.encode("utf-8")).hexdigest()
            return URIRef(self.uri_pattern.format(scope=self._scope, id=h_uid))
        else:
            return URIRef(str(uid))
    
    def isInstanceOf(self):
        rst = Entity
        for cls in inspect.getmro(self.__class__):
            if cls.__name__ == "Entity": break
            rst = cls
        return rst

    def attributes(self, include_empty=False):
        if include_empty and self.__class__.__name__ in Entity._attributes_cache:
            return Entity._attributes_cache[self.__class__.__name__ ]
            
        my_attributes = []
        for key in self.__dict__:
            if re.match(Entity._re_pattern_attributes, key):
                if key in self._excluded_attributes: continue
                if self.__dict__[key] is None and False == include_empty: continue
                if isinstance(self.__dict__[key], str) and '' == self.__dict__[key] and False == include_empty: continue
                if isinstance(self.__dict__[key], list) and 0 == len(self.__dict__[key]) and False == include_empty: continue
                my_attributes.append(key)

        if include_empty and self.__class__.__name__ not in Entity._attributes_cache:
            Entity._attributes_cache[self.__class__.__name__ ] = my_attributes

        return my_attributes 

    def clear(self):
        for a in self.attributes():
            setattr(self, a, None)

    def hash(self):
        my_hash = {"@id": str(self.id)}

        attributes = self.attributes()

        for attribute in attributes:
            if attribute in self._excluded_attributes: continue
            if attribute in ("created", "modified"): continue

            value = getattr(self, attribute)
            if isinstance(value, Entity):
                my_hash[attribute] = value.hash()
            elif isinstance(value, list):
                my_hash[attribute] = []
                for item in value: 
                    if isinstance(item, Entity): 
                        my_hash[attribute].append(item.hash())
                    else:
                         my_hash[attribute].append(str(item))
                        
            else:
                my_hash[attribute] =  str(value)
        
        my_hash = json.dumps(my_hash, sort_keys=True)
        setattr(self, "entity_hash", hashlib.sha1(my_hash.encode("utf-8")).hexdigest())
        return self.entity_hash

    def _getBaseClass(self):
        rst = self.__class__.__name__
        for cls in inspect.getmro(self.__class__):
            if cls.__name__ == "Entity": break
            rst = cls.__name__
        return rst

    def _register_namespaces(self, graph):
        if hasattr(graph, "_register_namespaces_done"): return

        import rdflib as my_rdflib

        graph.bind("ADMS".lower(), my_rdflib.ADMS)
        graph.bind("BODC".lower(), my_rdflib.BODC)
        graph.bind("DIRECT".lower(), my_rdflib.DIRECT)
        graph.bind("EJERICO".lower(), my_rdflib.EJERICO)
        graph.bind("EPOS".lower(), my_rdflib.EPOS)
        graph.bind("HTTP".lower(), my_rdflib.HTTP)
        graph.bind("HYDRA".lower(), my_rdflib.HYDRA)
        graph.bind("LOCN".lower(), my_rdflib.LOCN)
        graph.bind("SOCIB".lower(), my_rdflib.SOCIB)
        graph.bind("SPDX".lower(), my_rdflib.SPDX)
        graph.bind("VCARD".lower(), my_rdflib.VCARD)
        
        for n in dir(my_rdflib):
            o = getattr(my_rdflib, n)
            if isinstance(o, Namespace) or isinstance(o, ClosedNamespace):
                graph.bind(n.lower(), o)
            if "DefinedNamespaceMeta" == o.__class__.__name__:
                graph.bind(n.lower(), o)
        setattr(graph, "_register_namespaces_done", True)

    def _to_tiplets(self, entity=None, schema=None):
        try:
            entity = self if entity is None else entity
            scope = entity._getBaseClass()

            if scope in BNODES_CLASSES:
                if "id" in entity.__dict__: entity.id = None

            scope = scope.lower()

            rdf_type_class = self.mapper.map_class(scope=scope, caller=entity.__class__.__name__, schema=schema)
            if rdf_type_class is None: return []

            saved_identifiers = entity.identifier
            entity.identifier = [i.toString() for i in entity.identifier]

            tiplets = [(entity.id, RDF.type, rdf_type_class)]

            my_subject = entity.id

            if entity.source is not None:
                my_predicate = self.mapper.map_property(name="harverted_source", scope=scope, caller=entity.__class__.__name__, schema=schema)
                if my_predicate is not None:
                    tiplets.append((entity.id, my_predicate, Literal(entity.source))) 

            for attr in entity.__dict__:
                if entity.__dict__[attr] is None: continue
                if isinstance(entity.__dict__[attr], str) and '' == entity.__dict__[attr]: continue
                if entity.__dict__[attr] != entity.__dict__[attr]: continue

                if re.match(r"^[a-zA-Z]+\W*", attr):
                    if attr in entity._excluded_attributes: continue
                    #if attr not in entity._valid_attributes:
                        #logging.info("\t- not registered attribute '{}' in class {}".format(attr, self.__class__)) 
                        #continue
                        
                    if "parent" == attr and self.__dict__[attr] is not None:
                        if not isinstance(self.__dict__[attr], Entity): 
                            raise GraphError("{} attribute must be a Entity instance".format(attr))
                    if "is_ejerico" == attr and self.__dict__[attr] is not None:
                        if not isinstance(self.__dict__[attr], bool): 
                            raise GraphError("{} attribute must be boolean".format(attr))

                    try:
                        my_predicate = self.mapper.map_property(name=attr.lower(), scope=scope, caller=entity.__class__.__name__, schema=schema)
                        if my_predicate is None: continue

                        if isinstance(my_predicate,str) and not isinstance(my_predicate,URIRef):
                            my_predicate = eval("EJERICO.{}".format(my_predicate))
                    except Exception as e:
                        logging.error("[Entity:_to_tiplets] Failed to in eval({})".format(my_predicate))
                        continue

                    if isinstance(entity.__dict__[attr], list):
                        for item in entity.__dict__[attr]:
                            if item is None: continue
                            if attr == "alias" and not isinstance(item,URIRef): item=URIRef(item)

                            if isPrimitive(item): 
                                tiplets.append((entity.id, my_predicate, tr(item)))
                            elif isinstance(item,Entity):
                                lst = entity._to_tiplets(entity=item, schema=schema)
                                if 0 != len(lst):
                                    is_bnode = lst[0][0] is None
                                    entity_ID = BNode() if is_bnode else item.id
                                    tiplets.append((my_subject, my_predicate,entity_ID))
                                    tiplets.extend(lst)
                            else:
                                logging.info("unknown type ({})".format(type(item)))

                    elif isPrimitive(entity.__dict__[attr]):
                        if entity.__dict__[attr] is not None:
                            if attr in ("id") and not isinstance(entity.__dict__[attr],URIRef):
                                entity.__dict__[attr] = URIRef(entity.__dict__[attr])
                            tiplets.append((my_subject, my_predicate, tr(entity.__dict__[attr])))
                    else:
                        if isinstance(entity.__dict__[attr],Entity):
                            item = entity.__dict__[attr]
                            lst = entity._to_tiplets(entity=item, schema=schema)
                            if 0 != len(lst):
                                is_bnode = lst[0][0] is None
                                entity_ID = BNode()  if is_bnode else item.id
                                tiplets.append((my_subject, my_predicate, entity_ID))
                                tiplets.extend(lst)

            entity.identifier = saved_identifiers            
            return tiplets
        except Exception as e:
            logging.error("[Entity:_to_tiplets] error converting to tiples ({}".format(e))
            logging.error(traceback.format_exc())
    
    def _set_attribute_for_all(self, name=None, value=None, replace=True):
        if name is not None:
            if replace or getattr(self, name) is None: setattr(self, name, value)

            for key0 in self.__dict__:
                val0 = self.__dict__[key0]
                if isinstance(val0, list):
                    for val1 in val0:
                        if isinstance(val1,Entity): 
                            val1._set_attribute_for_all(name=name, value=value, replace=replace)
                elif isinstance(val0,Entity): 
                    val0._set_attribute_for_all(name=name, value=value, replace=replace)

    def _mark_all_first_born(self, first_born_value=True):
        self._set_attribute_for_all(name="first_born", value=first_born_value)

    def _mark_all_delete_on_save(self, delete_on_save_value=True):
        self._set_attribute_for_all(name="_delete_on_save", value=delete_on_save_value)

    def _drop_all_empty(self):
        for key in self.attributes():
            value = getattr(self, key)
            if isinstance(value, list):
                new_value = []
                for item in value: 
                    if isinstance(item,Entity):
                        item._drop_all_empty()
                        if not item.empty: new_value.append(item)
                    else:
                        new_value.append(item)
                else:
                    setattr(self, key, new_value)
            elif isinstance(value,Entity): 
                setattr(self, key, (None if value.empty else value))  

    def _transformToURI(self, value):
        if value is not None and isinstance(value,str):
            value = value.strip()
            if checkers.is_url(value) or checkers.is_email(value):
                value = URIRef(value)
            elif not re.match(r"\b[0-9a-z]{40}\b", value):
                value = hashlib.sha1(value.encode("utf-8")).hexdigest()
                value = URIRef(self.uri_pattern.format(scope=self._scope, id=value))
            else:
               value = URIRef(self.uri_pattern.format(scope=self._scope, id=value))
            return value  
        else:
            return self._transformToURI(str(value))

################################################################################
##  PUBLIC FUNCTIONS
################################################################################
def get_mapper():
    return EntityMapper.instance()

def short_circuit_term(n,t):
    return URIRef(str(n) + (t if isinstance(t, str) else ""))

def lng(x):
    t = type(x)
    if isinstance(t,str):
        m = re.match(r"(.+)@[a-zA-Z]{2,4}$", x)
        if m:
            logging.info(m)
    return None
def dt(x):
    if isinstance(x, str):
        m = re.match(r"(.+)^^xsd:(.+)", x)
        if m: return None
    t = type(x)
    return XSD_TR_MAP[t] if t in XSD_TR_MAP else None
    
def tr(x):
    if isinstance(x, URIRef):
        return URIRef(str(x).strip())
    if isinstance(x, Literal):
        if isinstance(x, str):
            x = Literal(str(x).strip())
        return x
    my_datatype = dt(x)
    my_lang = lng(x) if isinstance(x,str) else None
    x=x[0:DB_STR_MAXSIZE] if isinstance(x,str) else x

    return Literal(x, datatype=my_datatype,lang=my_lang)

def metadata():
    my_metadata = {}
    clazzes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for clazz in clazzes:
        if issubclass(clazz[1], Entity):
            my_metadata[clazz[1]] = clazz[1].metadata() 
    return my_metadata


################################################################################
##  MAPPER
################################################################################

@singleton
class EntityMapper(object):
    def __init__(self):

        self.schemas = {}
        self.schemasFixIssueUnknownMapping = []

        self.config = ConfigManager.instance()
        self.default_mapping_schema = self.config.get("mapping_schema", default="ejerico")
        self.ignore_unknown = self.config.get("ignore_unknown_mapping_entity", default=True)
        
        ###KLUDGE: Quick fix to avoid DefinedNamespace restrictions
        for c in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            if "DefinedNamespaceMeta" == c[1].__class__.__name__:
                c[1].__class__._warn = False
        
        ###KLUDGE: Quick fix to avoid ClosedNamespace restrictions
        import rdflib as my_rdflib
        for n in [getattr(my_rdflib, k) for k in dir(my_rdflib)]:
            if isinstance(n, ClosedNamespace): 
                setattr(n,"term", partial(short_circuit_term, n))
            if isinstance(n, Namespace):
                n.__class__._warn = False
                setattr(n,"term", partial(short_circuit_term, n))
                        
        self.load_mapping_schema(self.default_mapping_schema)
        if "direct" not in self.schemas: 
            self.schemas["direct"] = EntityMappingSchema("direct", ignore_unknown=False, class_ignored_prefix="", property_ignored_prefix="")

    def map_class(self, scope=None, caller=None, schema=None, strict=False, class_unknown_prefix="class_unknown_"):
        schema = self.default_mapping_schema if schema is None else schema
        if schema in self.schemas:         
            return self.schemas[schema].map_class(scope=scope, caller=caller, strict=strict)
        else:
            return "{}{}".format(scope) if not self.ignore_unknown  else None

    def unmap_class(self, classname, schema=None):
        schema = self.default_mapping_schema if schema is None else schema
        if schema in self.schemas:
            return self.schemas[schema].unmap_class(classname)
        else:
            return None
                 
    def map_property(self, name=None, scope=None, caller=None, schema=None, strict=False, property_unknown_prefix="property_unknown_"):
        schema = self.default_mapping_schema if schema is None else schema
        if schema in self.schemas:
            return self.schemas[schema].map_property(name=name, scope=scope, caller=caller, strict=strict)
        else:
            return "{}{}".format(property_unknown_prefix,name) if not self.ignore_unknown  else None

    def unmap_property(self, name, scope=None, schema=None):
        schema = self.default_mapping_schema if schema is None else schema
        if schema in self.schemas:
            return self.schemas[schema].unmap_property(property_name=name, scope=scope)

        return None
         
    def load_mapping_schema(self, schema):
        if schema is None or not isinstance(schema, str):
            logging.info("[EntityMapper:load_mapping_schema] missing or incorrect mapping schema '{}'".format(schema))
            return

        logging.info("[EntityMapper:load_mapping_schema] processing mapping schema '{}'".format(schema))
        
        mapping_definition = self.__load_mapping_definition(scope="default", schema=schema)
        self.load_mapping_definition(definition=mapping_definition, schema=schema)

        clazzes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        for clazz in clazzes:
            if issubclass(clazz[1], Entity):
                mapping_definition=self.__load_mapping_definition(scope=clazz[0], schema=schema)
                self.load_mapping_definition(definition=mapping_definition, scope=clazz[0], schema=schema)

    def load_mapping_definition(self, definition=None, scope=None, schema=None, cleanup=False):
        try:
            if definition is None: return

            schema = self.default_mapping_schema if schema is None else schema
            if schema not in self.schemas: self.schemas[schema] = EntityMappingSchema(schema, ignore_unknown=self.ignore_unknown)

            section = key = None

            if re.match("[\w./]+_mapping.json$", definition): 
                logging.info("[EntityMapper:load_mapping_definition] processing mapping file '{}'".format(definition))
                definition = open(definition, "r").read()
            
            mapping_dict = json.loads(definition)
            mapping_dict = to_dict_lowercase(mapping_dict)

            scope = mapping_dict["scope"].lower() if "scope" in mapping_dict else scope

            if cleanup: 
                self.schemas[schema].classes.clear()
                self.schemas[schema].properties.clear()
                self.schemas[schema].alias.clear()

            for section in ("classes", "properties", "alias"):
                if section in mapping_dict:
                    my_section = getattr(self.schemas[schema], section)
                    if "alias" != section:
                        for key in mapping_dict[section]:
                            try:
                                values = mapping_dict[section][key].split(':')
                                try:
                                    mapping_dict[section][key] = eval("{}.{}".format(values[0].upper(),values[1]))
                                except AttributeError as e: pass
                                if not isinstance(mapping_dict[section][key], URIRef): 
                                    mapping_dict[section][key] = URIRef("{}{}".format(eval(values[0].upper()), values[1]))
                                    logging.info("[EntityMapper:load_mapping_definition] Forced eval({})".format("{}.{}".format(values[0].upper(),values[1])))
                            except Exception as e:
                                logging.error("[EntityMapper:load_mapping_definition] Failed to in eval({})".format("{}.{}".format(values[0].upper(),values[1])))

                    for key,val in mapping_dict[section].items():
                        key = "{}:{}".format(scope.lower(), key) if scope is not None else key
                        my_section[key] = val
        except Exception as e: 
            logging.info("[EntityMapper:load_mapping_definition] error loading mapping definition ({}, {}) -> {}".format(section, key, e))

    def translateClassMapping(self, uri, from_mapping, to_mapping):
        if uri is None: return None
        if from_mapping is None: return None
        if to_mapping is None: return None
        if from_mapping not in self.schemas: return None
        if to_mapping not in self.schemas: return None
        
        uri = URIRef(str(uri)) if not isinstance(uri, URIRef) else uri

        my_class = [cls for cls in self.schemas[from_mapping].classes if self.schemas[from_mapping].classes[cls] == uri]
        if not my_class: return None

        if my_class[0] not in self.schemas[to_mapping].classes: return None
        return self.schemas[to_mapping].classes[my_class[0]]
        
    def translatePropertyMapping(self, uri, from_mapping, to_mapping):
        if uri is None: return None
        if from_mapping is None: return None
        if to_mapping is None: return None
        if from_mapping not in self.schemas: return None
        if to_mapping not in self.schemas: return None
        
        uri = URIRef(str(uri)) if not isinstance(uri, URIRef) else uri
        
        my_property = [prop for prop in self.schemas[from_mapping].properties if self.schemas[from_mapping].properties[prop] == uri]
        if not my_property: return None

        if my_property[0] not in self.schemas[to_mapping].properties: return None
        return self.schemas[to_mapping].properties[my_property[0]]

    def __load_mapping_definition(self, scope=None, schema=None):
        if not scope or not schema: return None
        if "entity" == scope.lower(): return None

        scope = camelCaseToSnakeCase(scope)
        cache_path = "{}/.ejerico/cache/{}".format(Path.home(), schema)
        mapping_file = "{}/{}_entity_mapping.json".format(schema,scope.lower())
        definition_file = "{}/.ejerico/cache/{}".format(Path.home(), mapping_file)

        # # case: load hardcoded definition mapping file
        definition_file = pkg_resources.resource_filename(__name__, "..{sep}data{sep}{schema}{sep}{scope}_entity_mapping.json".format(sep=os.sep, scope=scope.lower(), schema=schema))
        if os.path.exists(definition_file):
             logging.info("[EntityMapper:_load_mapping_definition] processing mapping file '{}' from package".format("{}_entity_mapping.json".format(scope.lower())))
             return Path(definition_file).read_text() 
        else:
             logging.info("[EntityMapper:_load_mapping_definition] not found mapping file '{}' around".format("{}_entity_mapping.json".format(scope.lower())))
        
        # case: has connection & exists mapping file in remote server
        try:
            url = self.config.get("mapping_definition_url")
            if url is not None:
                url = "{}/{}".format(url, mapping_file)
                response = requests.get(url, timeout=3)
                if requests.codes.ok == response.status_code: 
                    data = response.json()
                    logging.info("[EntityMapper:_load_mapping_definition] processing mapping file '{}:{}' from url".format(schema,"{}_entity_mapping.json".format(scope.lower())))
                    
                    os.makedirs(cache_path, exist_ok=True)
                    with open("{}".format(definition_file), "w") as outfile: json.dump(data, outfile)
                    return json.dumps(data)

                if requests.codes.not_found == response.status_code:
                    os.makedirs(cache_path, exist_ok=True)
                    if os.path.exists(definition_file): return Path(definition_file).unlink()
        except json.JSONDecodeError as e:
            logging.error("[EntityMapper:__load_mapping_definition] error loading mapping definition ({}, {}, {}) -> {}".format(schema, scope, response.status_code))
        except Exception as e: 
            logging.error("[EntityMapper:__load_mapping_definition] error loading mapping definition ({}, {}, {})".format(schema, scope, e))

        # case: exists a copy on local cache
        if os.path.exists(definition_file):
            logging.info("[EntityMapper:_load_mapping_definition] processing mapping file '{}' from cache".format("{}_entity_mapping.json".format(scope.lower())))
            return Path(definition_file).read_text() 
        
        return Path(definition_file).read_text() if os.path.exists(definition_file) else None

    def _fix_unknownMappingIssues(self, schema=None):
        for clazz in [clazz for clazz in inspect.getmembers(sys.modules[__name__], inspect.isclass) if issubclass(clazz[1], Entity)]:
            clazz_name = clazz[0].lower(); clazz_cls = clazz[1]
            map_clazz = self.map_class(scope=clazz_name, schema=schema)
            
            entity = clazz_cls[1]()
            for attribute in entity.attributes(include_empty=True):
                print(attribute)
            #self.schemas[schema].classes.clear()
            #self.schemas[schema].properties.clear()
        self.schemasFixIssueUnknownMapping.append(schema)

class EntityMappingSchema(object):
    def __init__(self, name, ignore_unknown=False, class_ignored_prefix="class_unknown_", property_ignored_prefix="property_unknown_"):
        self.name = name
        self.ignore_unknown = ignore_unknown
        self.class_ignored_prefix = class_ignored_prefix
        self.property_ignored_prefix = property_ignored_prefix
        self.classes = {}
        self.properties = {}
        self.alias = {}

        self.isReversedMappingDone = False_
        
        import rdflib as my_rdflib
        custom_namespaces = {"ejerico":my_rdflib.EJERICO, "epos":my_rdflib.EPOS, "socib":my_rdflib.SOCIB, "direct":my_rdflib.DIRECT}
        if name in custom_namespaces:
            self.namespace = custom_namespaces[name]
        else:
            self.namespace = my_rdflib.EJERICO
        
    @lru_cache
    def map_class(self, scope=None, caller=None, strict=False):
        if scope is None: return None

        scope = scope.lower()
        
        if caller is not None:
            if not strict:
                scope_self = caller.lower()
                if scope_self in self.classes:
                    return self.classes[scope_self]

            scope_class = "{}:{}".format(caller.lower(), scope)
            if scope_class in self.classes:
                return self.classes[scope_class]
            
            if strict: 
                return self.eval_class("{}{}".format(self.class_ignored_prefix,scope)) if not self.ignore_unknown  else None
    
        if scope in self.classes:
            return self.classes[scope] 

        if scope in self.alias:
            scope_alias = self.alias[scope]
            return self.map_class(scope=scope_alias, caller=caller)
        
        if strict: 
            return self.eval_class("{}{}".format(self.class_ignored_prefix,scope)) if not self.ignore_unknown  else None

        return self.eval_class("{}{}".format(self.class_ignored_prefix,scope)) if not self.ignore_unknown  else None

    @lru_cache
    def unmap_class(self, classname):
        classname = str(classname)
        #classname = snakeCaseToCamelCase(classname) 
        if self.class_ignored_prefix in classname: return classname.replace(self.class_ignored_prefix, "")

        keys = [key for key, value in self.classes.items() if str(value).lower() == classname.lower()]
        if len(keys): 
            return keys[0]
        else:
            return None 

    @lru_cache
    def map_property(self, name=None, scope=None, caller=None, strict=False):
        if name is None: return None

        name = name.lower()
        if caller is not None:
            name_self = "{}:{}".format(caller.lower(), name)
            if name_self in self.properties:
                return self.properties[name_self] 

            if strict: 
                return self.eval_property("{}{}".format(self.property_ignored_prefix,name)) if not self.ignore_unknown  else None

        if scope is not None:
            scope = scope.lower()
            name_scope = "{}:{}".format(scope, name)
            if name_scope in self.properties:
                return self.properties[name_scope]

            if strict: 
                return self.eval_property("{}{}".format(self.property_ignored_prefix,name)) if not self.ignore_unknown  else None 

        name = name.lower()
        if name in self.properties:
            return self.properties[name]

        if name in self.alias:
            name_alias = self.alias[name]
            return self.map_property(name=name_alias, scope=scope, caller=caller)

            if strict: 
                return self.eval_property("{}{}".format(self.property_ignored_prefix,name)) if not self.ignore_unknown  else None

        return self.eval_property("{}{}".format(self.property_ignored_prefix,name)) if not self.ignore_unknown  else None

    @lru_cache
    def unmap_property(self, property_name, scope=None):
        property_name = str(property_name) 
        if scope is not None:
            scope = scope.lower()
            keys = [key.replace("{}:".format(scope.lower()),"") for key, value in self.properties.items() if str(value) == property_name and key.startswith(scope.lower())]
            if len(keys): return keys[0]

        keys = [key for key, value in self.properties.items() if str(value) == property_name and ':' not in key]
        if 0 != len(keys): return keys[0] 
        
        #TODO special case "direct"
        property_name = property_name[property_name.rfind('/')+1:] if -1 == property_name.rfind('/') else property_name
        property_name = property_name[property_name.rfind('#')+1:] if -1 == property_name.rfind('#') else property_name
        property_name = str(property_name)
        if self.property_ignored_prefix in property_name:
            return property_name.replace(self.property_ignored_prefix, "") 

        return None

    @lru_cache
    def eval_class(self, class_name):
        try:
            class_name = camelCaseToSnakeCase(class_name)
            class_name = URIRef("{}{}".format(self.namespace, class_name)) 
        except: pass
        return class_name

    @lru_cache
    def eval_property(self, property_name):
        try:
            property_name = camelCaseToSnakeCase(property_name)
            property_name = URIRef("{}{}".format(self.namespace, property_name))
        except: pass
        return property_name
################################################################################
##  STATIC INTERNAL OBJECTS
################################################################################
DB_STR_MAXSIZE = 2712

BNODES_CLASSES = []

XSD_TR_MAP = {
    str: XSD.string,
    bool: XSD.boolean,
    datetime: XSD.dateTime,
    float: XSD.float,
    int: XSD.integer,
}

SPARQL_LOAD_GET_ENTITIES = """
    SELECT DISTINCT ?s ?o
    WHERE {
        ?s rdf:type ?o
    }
"""

SPARQL_LOAD_GET_ENTITY = """
    SELECT DISTINCT ?p ?o
    WHERE {
        <###URI###> ?p ?o
    }
"""

################################################################################
## INTERNAL FUNCTIONS
################################################################################
def _get_caller_attribute(name):
    current_framework = inspect.currentframe()
    for caller_framework in inspect.getouterframes(current_framework, 2):
        try:
            if "self" not in caller_framework.frame.f_locals: continue
            caller_instance = caller_framework.frame.f_locals["self"]
            if hasattr(caller_instance, name) and getattr(caller_instance, name): 
                return getattr(caller_instance, name)
        except Exception as e: pass
    return None
def __constructor__(self, id=None, first_born=False, is_raw_id=False, namespace=None, source=None):
    namespace = namespace if namespace else None #ISSUE time load with _get_caller_attribute("namespace")

    classes = inspect.getmro(self.__class__)
    class_names = [c.__name__ for c in classes]
    classes = reversed(classes[class_names.index("Entity"):])
    for cls in classes:
        if cls.__name__ not in __all__:
            if cls is Entity:
                cls.__init__(self, id=id, first_born=first_born, is_raw_id=is_raw_id, namespace=namespace, source=source)
            else:
                cls.__init__(self)

Api = type("Api",(Entity,ApiImpl),{"__init__": __constructor__})
ApiOperation = type("ApiOperation",(Entity,ApiOperationImpl),{"__init__": __constructor__})
ApiOperationParameter = type("ApiOperationParameter",(Entity,ApiOperationParameterImpl),{"__init__": __constructor__})
Address = type("Address",(Entity,AddressImpl),{"__init__": __constructor__})
Catalog = type("Catalog",(Entity,CatalogImpl),{"__init__": __constructor__})
Concept = type("Concept",(Entity,ConceptImpl),{"__init__": __constructor__})
ConceptScheme = type("ConceptScheme",(Entity,ConceptSchemeImpl),{"__init__": __constructor__})
ContactPoint = type("ContactPoint",(Entity,ContactPointImpl),{"__init__": __constructor__})
Dataset = type("Dataset",(Entity,DatasetImpl),{"__init__": __constructor__})
Distribution = type("Distribution",(Entity,DistributionImpl),{"__init__": __constructor__})
Document = type("Document",(Entity,DocumentImpl),{"__init__": __constructor__})
Equipment = type("Equipment",(Entity,EquipmentImpl),{"__init__": __constructor__})
Facility = type("Facility",(Entity,FacilityImpl),{"__init__": __constructor__})
Frequency = type("Frequency",(Entity,FrequencyImpl),{"__init__": __constructor__})
Identifier = type("Identifier",(Entity,IdentifierImpl),{"__init__": __constructor__})
Organization = type("Organization",(Entity,OrganizationImpl),{"__init__": __constructor__})
Person = type("Person",(Entity,PersonImpl),{"__init__": __constructor__})
Platform = type("Platform",(Entity,PlatformImpl),{"__init__": __constructor__})
Program = type("Program",(Entity,ProgramImpl),{"__init__": __constructor__})
Project = type("Project",(Entity,ProjectImpl),{"__init__": __constructor__})
Relation = type("Relation",(Entity,RelationImpl),{"__init__": __constructor__})
Spatial = type("Spatial",(Entity,SpatialImpl),{"__init__": __constructor__})
Sensor = type("Sensor",(Entity,SensorImpl),{"__init__": __constructor__})
Service = type("Service",(Entity,ServiceImpl),{"__init__": __constructor__})
Software = type("Software",(Entity,SoftwareImpl),{"__init__": __constructor__})
SoftwareSource = type("SoftwareSource",(Entity,SoftwareSourceImpl),{"__init__": __constructor__})
Temporal = type("Temporal",(Entity,TemporalImpl),{"__init__": __constructor__})
Text = type("Text",(Entity,TextImpl),{"__init__": __constructor__})
Variable = type("Variable",(Entity,VariableImpl),{"__init__": __constructor__})
Vcard = type("Vcard",(Entity,VcardImpl),{"__init__": __constructor__})
WebService = type("WebService",(Entity,WebServiceImpl),{"__init__": __constructor__})


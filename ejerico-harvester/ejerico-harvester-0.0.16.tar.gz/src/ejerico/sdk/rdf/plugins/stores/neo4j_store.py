# -*- coding: utf-8 -*-
#

from datetime import datetime
import sys
import os
import argparse
import itertools
import logging
import hashlib
import traceback
import inspect
import json
import uuid
import re

from datetime import datetime, timedelta

from rdflib import Variable
from rdflib import Graph
from rdflib import namespace
from rdflib import Literal
from rdflib import URIRef
from rdflib import BNode
from rdflib import RDF
from rdflib.store import Store
from rdflib.store import VALID_STORE, UNKNOWN, NO_STORE
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from rdflib.namespace import NamespaceManager
from rdflib.term import Node

from rdflib import ADMS
from rdflib import BODC
from rdflib import CSVW
from rdflib import DC, DCAT, DCT, DCTERMS, DOAP, DIRECT
from rdflib import EJERICO, EPOS
from rdflib import FOAF
#from rdflib import GEO
from rdflib import HTTP, HYDRA
from rdflib import LOCN
from rdflib import ODRL2, ORG, OWL
from rdflib import PROF, PROV
#from rdflib import QB
from rdflib import RDF, RDFS
from rdflib import SCHEMA, SDO, SH, SKOS, SOCIB, SOSA, SPDX, SSN
from rdflib import TIME
from rdflib import VOID
from rdflib import XMLNS, XSD
from rdflib import VCARD

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from neo4j.time import DateTime as neo4j_Datetime
from neo4j.spatial import WGS84Point as neo4j_Point

from validator_collection import checkers, errors

from ejerico.sdk.rdf.entity import EntityMapper, Entity
from ejerico.sdk.utils import camelCaseToSnakeCase


class NEO4JStore(Store):

    def __init__(self, url=None, username=None, password=None, domain=None):
        logging.debug("[NEO4JStore:__init__] entering method")
        super(Store, self).__init__()
        self._url = url
        self._username = username
        self._password = password
        self._domain = domain

        self.driver = GraphDatabase.driver(
            self._url, auth=(self._username, self._password))
        self.session = None

        self.ns = {}
        self.mapper = EntityMapper.instance()
        self.module = inspect.getmodule(self.mapper)

    def open(self, configuration, create=False):
        logging.debug("[NEO4JStore:open] entering method")
        if self.session is None:
            self.session = self.driver.session()
        return VALID_STORE

    def close(self, commit_pending_transaction=False):
        logging.debug("[NEO4JStore:close] entering method")
        if self.session is not None:
            self.session.close()
            self.session = None
        return VALID_STORE

    def destroy(self, configuration):
        logging.debug("[NEO4JStore:destroy] entering method")
        if self.session is not None:
            self.close()

    def gc(self):
        logging.debug("[NEO4JStore:gc] entering method")
        super(Store, self).gc()

    def add(self, triple, context, quoted=False):
        logging.debug("[NEO4JStore:add] entering method")
        super(Store, self).add(triple, context, quoted=quoted)

    def addN(self, quads):
        logging.debug("[NEO4JStore:addN] entering method")
        self.open(None)

        nodes, relations = self._do_process_tiplets(
            [(q[0], q[1], q[2]) for q in quads])

        for n in nodes:
            result = self.session.write_transaction(
                self._do_neo4j_createNode, nodes[n]["__label__"], n)
            for row in result:
                logging.debug("[NEO4JStore:addN] created node: {}".format(row))

        for n in nodes:
            result = self.session.write_transaction(
                self._do_neo4j_updateNode, nodes[n])
            for row in result:
                logging.debug("[NEO4JStore:addN] update node: {}".format(row))

        for relation in relations:
            result = self.session.write_transaction(
                self._do_neo4j_createRelation, relation)
            for row in result:
                logging.debug(
                    "Merged relation: ({})-[{}]->({})".format(row['n'], row['r'], row['m']))

    def remove(self, triple, context=None):
        logging.debug("[NEO4JStore:remove] entering method")
        super(Store, self).remove(triple, context=context)

    def triples_choices(self, triple, context=None):
        logging.debug("[NEO4JStore:triples_choices] entering method")
        super(Store, self).triples_choices(triple, context=context)

    def triples(self, triple_pattern, context=None):
        logging.debug("[NEO4JStore:triples] entering method")
        super(Store, self).triples(triple_pattern, context=context)

    def __len__(self, context=None):
        logging.debug("[NEO4JStore:__len__] entering method")
        if True == True:
            raise NotImplementedError

    def contexts(self, triple=None):
        logging.debug("[NEO4JStore:contexts] entering method")
        if True == True:
            raise NotImplementedError

    def query(self, query, initNs, initBindings, queryGraph, **kwargs):
        logging.debug("[NEO4JStore:query] entering method")
        self.open(None)

        rst = None
        query = query[query.index(
            "SELECT"):] if "SELECT" in query else query[query.index("DESCRIBE"):]
        query = query.replace("\t", "").replace("\n", "")
        query = " ".join([s for s in query.split(' ') if '' != s.strip()])

        m = re.match(self.query._re_alias_pattern, query)
        if m:
            my_url = m.group("url")
            my_type = self._do_resolve_entity_class(m.group("type"))
            query = self.query._re_alias_query.format(
                label=my_type, url=my_url)
            rst = self.session.read_transaction(
                self._do_neo4j_generic_query, query)
            print(rst)

        m = re.match(self.query._re_totals_by_rdftype_pattern,
                     query) if m is None else None
        if m:
            my_type = self._do_resolve_entity_class(m.group("type"))
            query = self.query._re_totals_by_rdftype_query.format(
                label=my_type)
            rst = self.session.read_transaction(
                self._do_neo4j_generic_query, query)
            rst = [r['c'] for r in rst]

        m = re.match(self.query._re_uri_by_rdftype_pattern,
                     query) if m is None else None
        if m:
            my_type = self._do_resolve_entity_class(m.group("type"))
            my_offset = m.group("offset")
            my_limit = m.group("limit")
            query = self.query._re_uri_by_rdftype_query.format(
                label=my_type, offset=my_offset, limit=my_limit)
            rst = self.session.read_transaction(
                self._do_neo4j_generic_query, query)
            rst = [r['n'] for r in rst]

        m = re.match(self.query._re_describe_uri_pattern, query)
        if m:
            rst = []
            my_url = m.group("url")

            query = self.query._re_describe_uri_query.format(url=my_url)
            my_rst = self.session.read_transaction(
                self._do_neo4j_generic_query, query)
            for row in my_rst:
                a = scope = row['l'][0] if isinstance(
                    row['l'], list) else row['l']
                s = URIRef(my_url)
                o = self.mapper.map_class(a)
                rst.append((s, RDF.type, o))

                for my_p in row['p']:
                    my_o = row['p'][my_p] if isinstance(
                        row['p'][my_p], list) else [row['p'][my_p]]
                    p = self.mapper.map_property(my_p, scope=a)
                    if p is not None:
                        for o in my_o:
                            o = self._do_create_literal(my_p, o)
                            if o is not None:
                                rst.append((s, p, o))
                    else:
                        logging.warning(
                            "[NEO4JStore:query] error unmapping property: {}".format(my_p))

            query = self.query._re_describe_relation_query.format(url=my_url)
            my_rst = self.session.read_transaction(
                self._do_neo4j_generic_query, query)
            for row in my_rst:
                my_p = scope = row['l'][0] if isinstance(
                    row['l'], list) else row['l']
                p = self.mapper.map_property(my_p, scope=a)
                o = URIRef(row['p']["url"] if "ALIAS" ==
                           p.upper() else row['o'])
                if p is not None:
                    rst.append((s, p, o))
                else:
                    logging.warning(
                        "[NEO4JStore:query] error unmapping property: {}".format(my_p))

        if rst is None:
            logging.warning("[NEO4JStore:query] not handle query")
            rst = []

        return rst
    query._re_alias_pattern = re.compile(
        r"(SELECT DISTINCT \?s WHERE { \?s adms:identifier( ))((<)(?P<url>[\w\W]+)(>))(\. \?s rdf:type (?P<type>[\w\W]+)\. })")
    query._re_alias_query = "MATCH (n:{label})-[r {{url: '{url}' }}]->(n) RETURN n.id"
    query._re_totals_by_rdftype_pattern = re.compile(
        r"SELECT \(COUNT \?s\) as \?c WHERE \{ \?s rdf:type \<(?P<type>[\W\w]+)\>. \}")
    query._re_totals_by_rdftype_query = "MATCH (n:{label}) RETURN COUNT(n) as c"
    query._re_uri_by_rdftype_pattern = re.compile(
        r"SELECT \?s WHERE \{ \?s rdf:type \<(?P<type>[\W\w]+)\>. \} LIMIT (?P<limit>[\d]+) OFFSET (?P<offset>[\d]+)")
    query._re_uri_by_rdftype_query = "MATCH(n:{label}) RETURN n.id as n SKIP {offset} LIMIT {limit}"
    query._re_describe_uri_pattern = re.compile(
        r"DESCRIBE (<)(?P<url>[\w\W]+)(>)")
    query._re_describe_uri_query = "MATCH (n {{id: '{url}' }}) return labels(n) AS l, properties(n) AS p"
    query._re_describe_relation_query = "MATCH (n {{id: '{url}' }})-[r]->(m) RETURN type(r) as l, properties(r) as p, m.id as o"

    def update(self, update, initNs, initBindings, queryGraph, **kwargs):
        logging.debug("[NEO4JStore:update] entering method")
        raise NotImplementedError

    def bind(self, prefix, namespace):
        #logging.debug("[NEO4JStore:bind] entering method")
        self.ns[prefix] = namespace

    def prefix(self, namespace):
        #logging.debug("[NEO4JStore:prefix] entering method")
        return dict([(v, k) for k, v in self.ns.items()]).get(namespace)

    def namespace(self, prefix):
        #logging.debug("[NEO4JStore:namespace] entering method")
        return self.ns.get(prefix)

    def namespaces(self):
        #logging.debug("[NEO4JStore:namespaces] entering method")
        for k, v in self.ns.items():
            yield k, v

    def commit(self):
        logging.debug("[NEO4JStore:commit] entering method")
        raise NotImplementedError

    def rollback(self):
        logging.debug("[NEO4JStore:rollback] entering method")
        raise NotImplementedError

    def add_graph(self, graph):
        logging.debug("[NEO4JStore:add_graph] entering method")
        super(Store, self).add_graph(graph)

    def remove_graph(self, graph):
        logging.debug("[NEO4JStore:remnove_graph] entering method")
        super(Store, self).remove_graph(graph)

    ###################################################################################
    # NEO4J Internal methods
    ###################################################################################

    def _do_neo4j_createNode(self, tx, label, id):
        logging.debug("[NEO4JStore:_do_neo4j_createNode] entering method")

        try:
            query = self._do_neo4j_createNode._stm_create_node.format(
                label=label, id=id)
            result = tx.run(query)
            return [{"n": row["n"]} for row in result]
        except ServiceUnavailable as exception:
            logging.error("[NEO4JStore:_do_neo4j_updateNode] raised an error: \n {exception}".format(
                query=query, exception=exception))
        return []
    _do_neo4j_createNode._stm_create_node = """
        MERGE (n:{label} {{ id: '{id}' }}) 
        ON CREATE
            SET n.created = datetime(),
                n.modified = datetime(),
                n.updated = datetime()
        RETURN id(n) AS n
    """

    def _do_neo4j_updateNode(self, tx, node):
        def _do_neo4j_updateNode_special_cases(p):
            if p.startswith("n.created") or p.startswith("n.modified") or p.startswith("n.updated"):
                tn = [n for n in ("n.created", "n.modified",
                                  "n.updated") if p.startswith(n)][0]
                to = '>' if tn == "n.created" else '<'
                tp = p[p.index('=')+1:]
                return "{n}=CASE {n} WHEN {n}{o}{p} THEN {p} ELSE {n} END".format(n=tn, p=tp, o=to)
            elif p.startswith("n.geometry="):
                p = p.replace("'point", "point")
                p = p.replace("})'", "})")
            return p
        logging.debug("[NEO4JStore:_do_neo4j_updateNode] entering method")

        if node is None or 0 == len(node):
            return []

        self._do_prepare_node(node)
        if hasattr(self, "_do_prepare_node_{}".format(node["__label__"].upper())):
            getattr(self, "_do_prepare_node_{}".format(
                node["__label__"].upper()))(node)

        properties = []
        for k, v in node.items():
            if k.startswith('_'):
                continue

            if isinstance(v, list):
                properties.append("n.{}={}".format(
                    k, [self._do_prepare_node_property(x) for x in v]))
            elif isinstance(v, dict):
                pass
            else:
                properties.append("n.{}={}".format(
                    k, self._do_prepare_node_property(v)))
        else:
            properties = [_do_neo4j_updateNode_special_cases(
                p) for p in properties]
            properties = ',\n'.join(properties)

        try:
            query = self._do_neo4j_updateNode._stm_merge_node.format(id=node["__id__"], label=node["__label__"], properties=properties)
            result = tx.run(query)
            # Capture any errors along with the query and data for traceability
            return [{"n": row["n"]} for row in result]
        except ServiceUnavailable as exception:
            logging.error("[NEO4JStore:_do_neo4j_updateNode] raised an error: \n {exception}".format(
                query=query, exception=exception))
        return []
    _do_neo4j_updateNode._stm_merge_node = """
        MERGE (n:{label} {{ id: '{id}' }}) 
        ON MATCH
            SET {properties} 
        RETURN id(n) AS n
    """

    def _do_neo4j_createRelation(self, tx, relation):
        logging.debug("[NEO4JStore:_do_neo4j_createRelation] entering method")

        try:
            property = "SET r.url='{}'".format(
                relation[3]) if relation[3] is not None else ""
            query = self._do_neo4j_createRelation._stm_merge_relation.format(
                node_from=relation[0], role=relation[1].upper(), property=property, node_to=relation[2])
            result = tx.run(query)
            return [{"n": row["n"], "r": row["r"], "m": row["m"]} for row in result]
        except ServiceUnavailable as exception:
            logging.error("[NEO4JStore:_do_neo4j_createRelation] raised an error: \n {exception}".format(
                query=query, exception=exception))
        return []
    _do_neo4j_createRelation._stm_merge_relation = """
        MATCH (n {{ id: '{node_from}' }}) 
        MATCH (m {{ id: '{node_to}' }}) 
        MERGE (n)-[r:{role}]->(m) {property} 
        RETURN id(n) AS n, id(r) AS r, id(m) AS m
    """

    def _do_neo4j_generic_query(self, tx, query):
        logging.debug("[NEO4JStore:_do_neo4j_createRelation] entering method")

        try:
            result = tx.run(query)
            return [row for row in result]
        except ServiceUnavailable as exception:
            logging.error("[NEO4JStore:_do_neo4j_createRelation] raised an error: \n {exception}".format(
                query=query, exception=exception))
        return []

    ###################################################################################
    # Internal helper methods
    ###################################################################################
    def _do_process_tiplets(self, tiplets):
        nodes = {str(t[0]): {"__id__": str(t[0]), "__label__": Entity.getInstanceFromRDFType(
            t[2], t[0]).__class__.__name__} for t in tiplets if t[1] == RDF.type}
        relations = []

        for t in tiplets:
            s = str(t[0])

            p = EntityMapper.instance().unmap_property(
                t[1], scope=nodes[s]["__label__"])
            if p is None:
                if "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" != str(t[1]):
                    logging.warning(
                        "[do_prepareTipletSet] not resolved mapping for property '{}'".format(str(t[1])))
                continue
            else:
                p = camelCaseToSnakeCase(p)
                if p in self._do_process_tiplets._predicate_renaming_map:
                    p = self._do_process_tiplets._predicate_renaming_map[p]

            o = t[2]
            if isinstance(o, Literal):
                o = o.toPython()
                o = o.replace("'", "\\'") if isinstance(
                    o, str) and "'" in o else o

                if p not in nodes[s]:
                    nodes[s][p] = o
                elif isinstance(nodes[s][p], list):
                    nodes[s][p].append(o)
                else:
                    nodes[s][p] = [nodes[s][p], o]

            elif isinstance(o, URIRef):
                o = o.toPython()
                if "alias" == p:
                    if s != o:
                        relations.append((s, p.upper(), s, o))
                else:
                    relations.append((s, p.upper(), o, None))

        return nodes, relations
    _do_process_tiplets._predicate_renaming_map = {
        "accessurl": "access_url",
        "downloadurl": "download_url",
        "harvested_source": "source",
        "harvested_update": "updated",
        "propertyid": "property_id",
    }

    def _do_prepare_node_property(self, property):
        if isinstance(property, datetime):
            return "datetime('{}')".format(property.strftime("%Y-%m-%dT%H:%M:%S"))
        elif isinstance(property, neo4j_Point):
            return "point({{longitude: {longitude}, latitude: {latitude}}})".format(latitude=property.latitude, longitude=property.longitude)
        elif isinstance(property, str):
            return "'{}'".format(property)
        else:
            return property

    def _do_prepare_node(self, node):
        logging.debug("[NEO4JStore:_do_prepare_node] entering method")

        if "created" in node and isinstance(node["created"], list):
            node["created"] = min(node["created"])
        if "modified" in node and isinstance(node["modified"], list):
            node["modified"] = max(node["modified"])
        if "updated" in node and isinstance(node["updated"], list):
            node["updated"] = max(node["updated"])

        if "keywords" in node:
            value = node["keywords"]
            value = ",".join(value) if isinstance(value, list) else value
            value = [s.strip() for s in set(value.split(','))]
            value = ",".join(value)
            node["keywords"] = list(dict.fromkeys(
                value)) if isinstance(value, list) else value

        if "geometry" in node:
            logging.debug("[NEO4JStore:_do_prepare_node] TODO process WKT string")
            node["wkt"] = node["geometry"]; node["geometry"] = None
        if "latitude" in node and "longitude" in node:
            node["geometry"] = [neo4j_Point((float(node["latitude"]), float(node["longitude"])))]
        if "min_latitude" in node and "min_longitude" in node and "max_latitude" in node and "max_longitude" in node:
            node["geometry"] = [
                neo4j_Point((float(node["min_latitude"]),
                            float(node["min_longitude"]))),
                neo4j_Point((float(node["min_latitude"]),
                            float(node["max_longitude"]))),
                neo4j_Point((float(node["max_latitude"]),
                            float(node["max_longitude"]))),
                neo4j_Point((float(node["min_latitude"]),
                            float(node["max_longitude"]))),
                neo4j_Point((float(node["min_latitude"]),
                            float(node["min_longitude"]))),
            ]

        node["updated"] = datetime.now(
        ) if "updated" not in node else node["updated"]

    def _do_prepare_node_DATASET(self, node):
        logging.debug("[NEO4JStore:_do_prepare_node_DATASET] entering method")

    def _do_resolve_entity_class(self, predicate):
        logging.debug("[NEO4JStore:_do_resolve_entity_class] entering method")

        m = re.match(
            self._do_resolve_entity_class._re_predicate_pattern, str(predicate))
        if m:
            predicate = "{}.{}".format(
                m.group("vocabulary").upper(), m.group("topic"))
            if predicate not in self._do_resolve_entity_class._cache_predicate_qname_to_uri:
                self._do_resolve_entity_class._cache_predicate_qname_to_uri[predicate] = str(
                    eval(predicate))
            predicate = self._do_resolve_entity_class._cache_predicate_qname_to_uri[predicate]

        if predicate not in self._do_resolve_entity_class._cache_predicate_uri_to_label:
            mapped_class = self.mapper.unmap_class(predicate)
            for key in self.module.__dict__:
                if key is None or mapped_class is None:
                    print("STOP!!!")
                if key.lower() == mapped_class.lower():
                    self._do_resolve_entity_class._cache_predicate_uri_to_label[predicate] = key

        return self._do_resolve_entity_class._cache_predicate_uri_to_label[predicate]

    def _do_create_literal(self, predicate, object):
        if isinstance(object, neo4j_Point):
            return None
        if isinstance(object, neo4j_Datetime):
            object = datetime(
                object.year, object.month, object.day,
                object.hour, object.minute, int(object.second),
                int(object.second * 1000000 % 1000000), tzinfo=object.tzinfo)
            return Literal(object, datatype=XSD.datetime)
        if isinstance(object, str):
            return Literal(object, datatype=XSD.string)
        print(type(object))
        return Literal(object, datatype=XSD.string)

    _do_resolve_entity_class._re_predicate_pattern = re.compile(
        r"(?P<vocabulary>[\w]+):(?P<topic>[\w]+)")
    _do_resolve_entity_class._cache_predicate_qname_to_uri = {}
    _do_resolve_entity_class._cache_predicate_uri_to_label = {}

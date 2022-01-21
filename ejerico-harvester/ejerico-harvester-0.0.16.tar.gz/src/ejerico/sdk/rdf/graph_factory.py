"""TODO doc"""
import string 
import logging
import traceback

from typing import DefaultDict

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import namespace 
from rdflib import __init__ as init
from rdflib.namespace import Namespace, ClosedNamespace
from rdflib.store import Store, VALID_STORE

from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.results import jsonresults
from rdflib.plugins.sparql.results import rdfresults

from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

from requests.auth import HTTPDigestAuth

from ejerico.sdk.annotations import singleton
from ejerico.sdk.config import ConfigManager

from ejerico.sdk.rdf.graph import Graph as MyGraph
from ejerico.sdk.rdf.plugins.stores.neo4j_store import NEO4JStore

__all__ = ["GraphFactory"]

class GraphFactory(object):

    @staticmethod
    def createGraph(model=None):
        config = ConfigManager.instance()
        
        mode = config.get("mode", default="unstable")
        logging.warning("[GraphFactory::createGraph] ejerico mode is {}".format(mode.upper()))

        store = config.get("rdf_store")
        if store is None:
            logging.error("[GraphFactory::createGraph] missing RDFLib store plugin ({})")
            raise SystemExit

        if "sparql" == store:
            store = "SPARQLUpdateStore"
        elif "neo4j" == store:
            store = "NEO4JStore"
        elif not store.endswith("Store"):
            store = "{}Store".format(store.upper())
            
        try:
            uri_identifier = URIRef(config.get("domain", default=ConfigManager.instance().defaultDOMAIN)) if model is None else URIRef(model)
            
            if "SPARQLUpdateStore" == store:
                endpoint_query = config.get("sparql_entrypoint_query")
                endpoint_update = config.get("sparql_entrypoint_update")

                if endpoint_query is None or endpoint_update is None:
                    logging.error("[GraphFactory::createGraph] unknown sparql entrypoint ({}, {})".format(endpoint_query, endpoint_update))
                    raise SystemExit

                #if mode not in ("unstable", "testing", "stable"):
                #    logging.error("[GraphFactory::createGraph] unknown development mode ({})".format(mode))
                #    raise SystemExit

                endpoint_query = _fix_sparqlentry_mode(endpoint_query, mode)
                endpoint_update = _fix_sparqlentry_mode(endpoint_update, mode)

                endpoint_auth_username = config.get("sparql_auth_username")
                endpoint_auth_password = config.get("sparql_auth_password")
                endpoint_auth = (endpoint_auth_username, endpoint_auth_password) if endpoint_auth_username or endpoint_auth_password else None

                store = SPARQLUpdateStore(
                    query_endpoint=endpoint_query, 
                    update_endpoint=endpoint_update,
                    auth=endpoint_auth,
                    method="POST"
                )
                   
                graph = MyGraph(store=store, identifier=uri_identifier) 
                #status = graph.open((endpoint_query, endpoint_update), auth=endpoint_auth)
                status = VALID_STORE

            elif "NEO4JStore" == store:
                endpoint_url = config.get("neo4j_url")
                endpoint_username = config.get("neo4j_username")
                endpoint_password = config.get("neo4j_password")

                if endpoint_url is None or endpoint_username is None or endpoint_password is None:
                    logging.error("[GraphFactory::createGraph] missing connection params({}, {}, {})".format(endpoint_url, endpoint_username, endpoint_password))
                    raise SystemExit

                store = NEO4JStore(url=endpoint_url, username=endpoint_username,password=endpoint_password,domain=uri_identifier)
                   
                graph = MyGraph(store=store, identifier=uri_identifier) 
                #status = graph.open((endpoint_query, endpoint_update), auth=endpoint_auth)
                status = VALID_STORE

            elif "EJERICOStore" == store:
                db_con = config.get("db_connection")

                if db_con is not None:
                    db_params = {}
                    for key in [arg[1] for arg in string.Formatter().parse(db_con) if arg[1] is not None]:
                        val = config.get(key)
                        if val is None:
                            logging.error("[GraphFactory::createGraph] missing RDFLib db parameter ({})".format(key))
                            raise SystemExit
                        db_params[key] = val
                else:
                    logging.error("[GraphFactory::createGraph] missing RDFLib connection ({})")
                    raise SystemExit                

                graph = MyGraph(store=store, identifier=uri_identifier)
                uri_db = Literal(db_con.format(**db_params))
                status = graph.open(uri_db, create=True)
            else:
                logging.error("[GraphFactory::createGraph] missing or unknown plugin store ({})".format(store))
                raise SystemExit                

            if status != VALID_STORE:
                logging.error("[GraphFactory::createGraph] error opening rdf graph store")
                raise SystemExit
            
            graph._register_namespaces()
            
            return graph
        except plugin.PluginException as e:
            logging.error("[GraphFactory::createGraph] unknown RDFLib store plugin ({})".format(store))
            raise SystemExit
        except Exception as e:
            logging.error("[GraphFactory::createGraph] error opening rdf graph store ({}) error -> {}".format(store, e))
            #print(traceback.format_exc())
            raise SystemExit


def _fix_sparqlentry_mode(url, mode):
    url = url.split('/')
    if url[-1] == "query" or url[-1] == "update":
        ##[CASE] Jena Fuseki
        if mode.startswith('/'):
            url[-2] = mode[1:]
        else:
            url[-2] = url[-2] if mode in url[-2] else "{}_{}".format(url[-2], mode)
    return '/'.join(url)

"""
# We are using Digest auth. Remember, additional kwargs are passed on to the Requests library.
store = SPARQLUpdateStore(
    queryEndpoint=config.SPARQL_ENDPOINT, 
    update_endpoint=config.SPARQL_UPDATE_ENDPOINT,
    auth=HTTPDigestAuth(config.AUTH_USER, config.AUTH_PASS), 
    context_aware=True,
    postAsEncoded=False)
# Default is 'GET'. We want to send 'POST' requests in this instance.
store.method = 'POST'
"""
"""TODO doc"""
import inspect
import rdflib
import logging

from ejerico.sdk.rdf.graph_extension import GraphExtension

class Graph(rdflib.Graph, GraphExtension): 

    def __init__(self, store="default", identifier=None, namespace_manager=None, base=None):
        rdflib.Graph.__init__(self, store=store, identifier=identifier, namespace_manager=namespace_manager, base=base)
        GraphExtension.__init__(self)
    
    @staticmethod
    def getSPARQLPrefixes():
        prefixes = ["PREFIX {}: <{}>".format(name.lower(), str(value)) for name, value  in inspect.getmembers(rdflib) if isinstance(value,rdflib.namespace.Namespace) or isinstance(value,rdflib.namespace.ClosedNamespace)]
        return "\n".join(prefixes)

    @staticmethod
    def getRDFTypePredicate():
        return str(rdflib.RDF.type)


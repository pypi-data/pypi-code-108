# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom Authors. All Rights Reserved.
from typing import Optional

from rdflib import Graph, RDF, RDFS, OWL

from knowledge.base.ontology import Ontology, OntologyClass, OntologyClassReference, OntologyPropertyReference, \
    OntologyProperty, PropertyType, INVERSE_DATA_PROPERTY_TYPE_MAPPING, DataPropertyType


def ontology_import(rdf_content: str, tenant_id: str = '', context: str = '') -> Ontology:
    """Import Ontology from RDF ontology file.

    Parameters
    ----------
    rdf_content: str
        Content of the RDF content file.
    tenant_id: str (default:= '')
        Tenant ID.
    context: str (default:= '')
        Context file.

    Returns
    -------
    ontology: Ontology
        Instance of ontology.
    """
    rdf_graph: Graph = Graph().parse(data=rdf_content, format='xml')
    ontology: Ontology = Ontology()
    # Parse classes
    for cls_iri in [s for s, p, o in rdf_graph.triples((None, RDF.type, RDFS.Class))]:
        subclass_of: Optional[OntologyClassReference] = None
        for _, _, o in rdf_graph.triples((cls_iri, RDFS.subClassOf, None)):
            subclass_of = OntologyClassReference.parse(o)
        ontology.add_class(OntologyClass(tenant_id=tenant_id, context=context,
                                         reference=OntologyClassReference.parse(cls_iri),
                                         subclass_of=subclass_of))
    # Parse data properties
    for data_property_iri in [s for s, p, o in rdf_graph.triples((None, RDF.type, OWL.DatatypeProperty))]:
        subproperty_of: Optional[OntologyPropertyReference] = None
        range_prop: Optional[DataPropertyType] = None
        domain_prop: Optional[OntologyClassReference] = None
        inverse_prop: Optional[OntologyPropertyReference] = None
        for _, _, o in rdf_graph.triples((data_property_iri, RDFS.range, None)):
            range_prop = INVERSE_DATA_PROPERTY_TYPE_MAPPING[str(o)]
        for _, _, o in rdf_graph.triples((data_property_iri, RDFS.domain, None)):
            domain_prop = OntologyClassReference.parse(o)
        for _, _, o in rdf_graph.triples((data_property_iri, OWL.inverseOf, None)):
            inverse_prop = OntologyPropertyReference.parse(o)
        for _, _, o in rdf_graph.triples((data_property_iri, RDFS.subPropertyOf, None)):
            subproperty_of = OntologyPropertyReference.parse(o)
        ontology.add_properties(OntologyProperty(kind=PropertyType.DATA_PROPERTY, tenant_id=tenant_id, context=context,
                                                 name=OntologyPropertyReference.parse(data_property_iri),
                                                 property_range=range_prop, property_domain=domain_prop,
                                                 subproperty_of=subproperty_of, inverse_property_of=inverse_prop))
    # Parse object properties
    for object_property_iri in [s for s, p, o in rdf_graph.triples((None, RDF.type, OWL.ObjectProperty))]:
        subproperty_of: Optional[OntologyPropertyReference] = None
        obj_range_prop: Optional[OntologyClassReference] = None
        domain_prop: Optional[OntologyPropertyReference] = None
        inverse_prop: Optional[OntologyPropertyReference] = None
        for _, _, o in rdf_graph.triples((object_property_iri, RDFS.range, None)):
            obj_range_prop = OntologyClassReference.parse(o)
        for _, _, o in rdf_graph.triples((object_property_iri, RDFS.domain, None)):
            domain_prop = OntologyClassReference.parse(o)
        for _, _, o in rdf_graph.triples((object_property_iri, OWL.inverseOf, None)):
            inverse_prop = OntologyPropertyReference.parse(o)
        for _, _, o in rdf_graph.triples((object_property_iri, RDFS.subPropertyOf, None)):
            subproperty_of = OntologyPropertyReference.parse(o)
        ontology.add_properties(OntologyProperty(kind=PropertyType.OBJECT_PROPERTY, tenant_id=tenant_id,
                                                 context=context,
                                                 name=OntologyPropertyReference.parse(object_property_iri),
                                                 property_range=obj_range_prop, property_domain=domain_prop,
                                                 subproperty_of=subproperty_of, inverse_property_of=inverse_prop))
    return ontology

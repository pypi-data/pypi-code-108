# -----------------------------------------------------------------------
# Copyright 2020 Mina Pêcheux

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at the root of the repo.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------

import importlib
import inspect
from typing import Any, Dict, List, Tuple, Union
from datetime import datetime

from pydantic import create_model
from neomodel import (StructuredNode,
                      StructuredRel,
                      StringProperty,
                      IntegerProperty,
                      BooleanProperty,
                      FloatProperty,
                      ArrayProperty,
                      DateTimeProperty,
                      RelationshipTo,
                      RelationshipFrom,
                      RelationshipManager,
                      Traversal,
                      One,
                      OneOrMore,
                      ZeroOrMore,
                      ZeroOrOne)
from pydantic.main import BaseModel

from cobblestone.helpers.types import get_real_type
from cobblestone.helpers.utils import (apply_hooks,
                                       clean_up_class_name,
                                       inflector,
                                       get_class,
                                       make_rel_field,
                                       is_multi_rel,
                                       AUTO_DEFAULT_DATES,
                                       PRIMARY_KEY,
                                       RETURN_RELATIONSHIP_PROPERTIES)


DIRECT_TABLES = {}

PYDANTIC_TO_NEO4J_TYPES = {
    str: StringProperty,
    int: IntegerProperty,
    float: FloatProperty,
    bool: BooleanProperty,
    list: ArrayProperty,
    datetime: DateTimeProperty,
    List: ArrayProperty,

    'relationship_to': RelationshipTo,
    'relationship_from': RelationshipFrom,
}

CARDINALITIES = {
    'One': One,
    'OneOrMore': OneOrMore,
    'ZeroOrMore': ZeroOrMore,
    'ZeroOrOne': ZeroOrOne,
}


class BaseAbstractRel(StructuredNode):

    __abstract_node__ = True
    uid = StringProperty(required=True)


def get_raw_reference(
    instance: StructuredNode,
    targets: List[Dict],
    rel: StructuredRel,
    single: bool
) -> Union[Tuple[StructuredNode, StructuredRel], List[Tuple[StructuredNode, StructuredRel]]]:
    init_traversal_def = rel._new_traversal().definition.copy()
    traversal_def = rel._new_traversal().definition
    results = []
    for target in targets:
        k = get_class(target)
        traversal_def['node_class'] = k
        traversal = Traversal(instance, k.__label__, traversal_def)
        results.extend([(item, rel.relationship(item))
                        for item in traversal.all()])
    rel._new_traversal().definition = init_traversal_def
    if single:
        return results[0]
    else:
        return results


def rel_to_json(d: dict, label: dict) -> dict:
    d.pop('id', None)
    return {**d, **label}


def to_json(schema: dict, relationships: dict) -> dict:
    def _to_json(instance: StructuredNode, populate: bool = True, ignored_values: list = []) -> dict:
        props = {k: v for k, v in instance.__dict__.items()
                 if not k.startswith('_')}
        data = {}
        for k, v in props.items():
            if isinstance(v, RelationshipManager):
                l = {'label': relationships[k]['label']}
                t = relationships[k]['target']
                if is_multi_rel(relationships[k]):
                    if isinstance(t, (tuple, list)):
                        linked = get_raw_reference(
                            instance, t, v, single=False)
                        if RETURN_RELATIONSHIP_PROPERTIES:
                            processed = [{'item': item,
                                          'rel': rel_to_json(_to_json(rel), l)}
                                         for item, rel in linked]
                        else:
                            processed = linked
                    else:
                        linked = v.all()
                        if RETURN_RELATIONSHIP_PROPERTIES:
                            processed = [{'item': item,
                                          'rel': rel_to_json(_to_json(v.relationship(item)), l)}
                                         for item in linked]
                        else:
                            processed = linked
                else:
                    if isinstance(t, (tuple, list)):
                        linked, rel = get_raw_reference(
                            instance, t, v, single=True)
                    else:
                        linked = v.single()
                        rel = v.relationship(linked)
                    if RETURN_RELATIONSHIP_PROPERTIES:
                        processed = {'item': linked,
                                     'rel': rel_to_json(_to_json(rel), l)}
                    else:
                        processed = linked
                data[k] = processed
            else:
                data[k] = v
        if populate:
            data = retrieve_referenced_instances(
                schema, data, ignored_values=ignored_values)
        return data
    return _to_json


def retrieve_referenced_instances(cur_schema: dict, data: Any, ignored_values: list = []) -> Any:
    if isinstance(data, (tuple, list)):
        return [retrieve_referenced_instances(cur_schema, i, ignored_values=ignored_values)
                for i in data]
    elif isinstance(data, dict):
        return {k: retrieve_referenced_instances(cur_schema, v, ignored_values=ignored_values)
                for k, v in data.items()}
    elif isinstance(data, StructuredNode):
        return data.to_json()
    else:
        return data


def PydanticToNeo4jParams(schema: dict, klass_params: dict) -> dict:
    required = schema.get('required', [])
    klass_props = {}
    for pname, pdata in schema['properties'].items():
        t = get_real_type(klass_params[pname].annotation)
        poptions = {}
        if pname in required:
            poptions['required'] = True
            if 'default' in pdata:
                poptions['default'] = pdata['default']
            elif t == datetime and AUTO_DEFAULT_DATES:
                poptions['default'] = datetime.utcnow
        if t in PYDANTIC_TO_NEO4J_TYPES:
            klass_props[pname] = PYDANTIC_TO_NEO4J_TYPES[t](**poptions)
    return klass_props


def PydanticToStructuredRel(klass: BaseModel) -> StructuredRel:
    schema = klass.schema()
    klass_params = inspect.signature(klass).parameters
    klass_props = PydanticToNeo4jParams(schema, klass_params)
    rel_klass = type(schema['title'], (StructuredRel,), klass_props)
    return rel_klass


def PydanticToORM(
    klass: BaseModel,
    collection: str = None,
    constructors: dict = {},
    relationships: dict = {},
    additional_fields: dict = {},
    hooks: dict = {},
    return_class: str = None
) -> StructuredNode:
    base_klass_name = clean_up_class_name(klass.schema()['title'])
    klass_name = base_klass_name + 'InDB'
    # prepare the "return class" friend-class for JSON response
    # payloads formatting
    if return_class is None:
        schemas_module = importlib.import_module(
            '.' + base_klass_name.lower(), 'cobblestone.models')
        if hasattr(schemas_module, base_klass_name + 'Full'):
            return_class = getattr(schemas_module, base_klass_name + 'Full')
        else:
            return_class = getattr(schemas_module, base_klass_name)

    # if relationships have properties: automatically wrap relationship fields
    # in additional "item" and "rel" keys
    # -> this will update the return class with fields that have the rel() wrapper
    if RETURN_RELATIONSHIP_PROPERTIES:
        props = {}
        f = klass.__fields__
        for r in relationships:
            props[r] = (make_rel_field(f[r]), ...)
        return_class = create_model('RelWrapped' + base_klass_name,
                                    __base__=return_class, **props)

    schema = klass.schema()

    # extract base parameters from the factory class
    klass_params = inspect.signature(klass).parameters
    klass_props = PydanticToNeo4jParams(schema, klass_params)
    if collection is None:
        collection = inflector.plural(base_klass_name.lower())
    klass_props['__label__'] = collection

    # if there are relationships: for each, create the corresponding Neo4j
    # RelationshipManager (with optionally a virtual AbstractRelClass in case
    # of multiple relationship target types)
    abstract_klasses_count = 0
    for pname, pdata in relationships.items():
        rel_klass = pdata['target']
        if isinstance(rel_klass, (tuple, list)):
            abstract_klass_name = f'{klass_name}AbstractRel{abstract_klasses_count}'
            abstract_klass = type(abstract_klass_name, (BaseAbstractRel,), {})
            abstract_klasses_count += 1
            for k in rel_klass:
                c = get_class(k)
                bases = list(c.__bases__)
                if StructuredNode in bases:
                    bases.remove(StructuredNode)
                bases.append(abstract_klass)
                c.__bases__ = tuple(bases)
            rel_klass = abstract_klass
        rel_type = PYDANTIC_TO_NEO4J_TYPES['relationship_' +
                                           pdata.get('direction', 'to')]
        rel_opts = {}
        if (m := pdata.get('model')):
            rel_opts['model'] = PydanticToStructuredRel(m)
        if (c := pdata.get('cardinality')):
            rel_opts['cardinality'] = CARDINALITIES[c]
        klass_props[pname] = rel_type(rel_klass, pdata['label'], **rel_opts)

    # add primary key field
    klass_props[PRIMARY_KEY] = PYDANTIC_TO_NEO4J_TYPES[str](required=True)

    # add the custom to_json() encoder
    klass_props['to_json'] = to_json(
        base_klass_name.replace('Full', ''),
        relationships,
    )

    # add util info for further processing
    klass_props['_constructors'] = constructors
    klass_props['_relationships'] = relationships
    klass_props['_additional_fields'] = additional_fields
    klass_props['response_model'] = return_class
    # create the actual database ORM class
    neo4j_klass = type(klass_name, (StructuredNode,), klass_props)

    # apply hooks by injecting "klass" or "instance"
    apply_hooks(neo4j_klass, hooks)

    DIRECT_TABLES[klass_name] = neo4j_klass
    return neo4j_klass


def wrap_additional_fields(schemas):
    for schema in schemas:
        db_schema = DIRECT_TABLES[schema + 'InDB']

        # add any supplementary fields
        for pname, pdata in db_schema._additional_fields.items():
            ptype = pdata['type']
            poptions = {}
            if pdata.get('required', True):
                poptions['required'] = True
            if (d := pdata.get('default', None)) is not None:
                poptions['default'] = d
            if isinstance(ptype, str) and ptype.startswith('$'):
                pklass = get_class(ptype.lstrip('$'))
                if pklass.__class__.__name__.endswith('InDB'):
                    ptype = getattr(pklass, 'response_model')
                else:
                    ptype = pklass
            else:
                ptype = get_real_type(ptype)
            if ptype in PYDANTIC_TO_NEO4J_TYPES:
                setattr(db_schema, pname, PYDANTIC_TO_NEO4J_TYPES[ptype](**poptions))

        # remove "_additional_fields" property from class
        # since it is not useful anymore
        delattr(db_schema, '_additional_fields')

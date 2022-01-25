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
import typing
from datetime import datetime

from pydantic import create_model
from mongoengine import (Document,
                         StringField,
                         IntField,
                         FloatField,
                         BooleanField,
                         ListField,
                         DictField,
                         DateTimeField,
                         LazyReferenceField,
                         GenericLazyReferenceField,
                         NULLIFY)
from pydantic.main import BaseModel

from cobblestone.helpers.types import get_real_type
from cobblestone.helpers.utils import (apply_hooks,
                                       clean_up_class_name,
                                       inflector,
                                       format_ref_uid,
                                       format_ref_rel,
                                       get_class,
                                       make_rel_field,
                                       is_multi_rel,
                                       AUTO_DEFAULT_DATES,
                                       HAS_RELATIONSHIP_PROPERTIES,
                                       PRIMARY_KEY,
                                       RETURN_RELATIONSHIP_PROPERTIES)


DIRECT_TABLES = {}

PYDANTIC_TO_MONGO_TYPES = {
    'object': DictField,
    str: StringField,
    int: IntField,
    float: FloatField,
    bool: BooleanField,
    dict: DictField,
    datetime: DateTimeField,
    typing.List: ListField,
    typing.Dict: DictField,
}

MONGO_TO_PYDANTIC_CONVERTERS = {
    DateTimeField: lambda v: v.isoformat()
}

REVERSE_DELETE_RULE = NULLIFY


def raw_to_json(instance: Document) -> dict:
    data = {}
    fields = instance._fields
    for prop in fields:
        val = getattr(instance, prop)
        if (converter := MONGO_TO_PYDANTIC_CONVERTERS.get(type(fields[prop]))):
            val = converter(val)
        data[prop] = val
    return data


def to_json(relationships: dict) -> dict:
    def _to_json(instance: Document, populate: bool = True) -> dict:
        data = instance.raw_to_json()
        if populate:
            for pname, pdata in relationships.items():
                a = getattr(instance, format_ref_uid(pname))
                if is_multi_rel(pdata):
                    if RETURN_RELATIONSHIP_PROPERTIES:
                        data[pname] = [{
                            'item': x.fetch().to_json(populate=populate),
                            'rel': data[format_ref_rel(pname)].get(x.pk, {}),
                        } for x in a]
                    else:
                        data[pname] = [x.fetch().to_json(populate=populate)
                                       for x in a]
                else:
                    if RETURN_RELATIONSHIP_PROPERTIES:
                        data[pname] = {
                            'item': a.fetch().to_json(populate=populate),
                            'rel': data[format_ref_rel(pname)],
                        }
                    else:
                        data[pname] = a.fetch().to_json(populate=populate)
        return data
    return _to_json


def PydanticToMongoParams(schema: dict, klass_params: dict) -> dict:
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
        if t in PYDANTIC_TO_MONGO_TYPES:
            klass_props[pname] = PYDANTIC_TO_MONGO_TYPES[t](**poptions)
    return klass_props


def PydanticToORM(
    klass: BaseModel,
    collection: str = None,
    constructors: dict = {},
    relationships: dict = {},
    additional_fields: dict = {},
    hooks: dict = {},
    return_class: str = None
) -> Document:
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
    if collection is None:
        collection = inflector.plural(base_klass_name.lower())
    klass_props = {'meta': {'collection': collection}}
    klass_props.update(PydanticToMongoParams(schema, klass_params))

    # if there are relationships: for each, create the corresponding Mongo
    # RelationshipManager (custom lists or dicts to hold the relationship
    # target and data)
    for pname, pdata in relationships.items():
        rel_klass = pdata['target']
        if is_multi_rel(pdata):  # list of references
            if isinstance(rel_klass, str):
                klass_props[format_ref_uid(pname)] = ListField(LazyReferenceField(
                    get_class(rel_klass), reverse_delete_rule=REVERSE_DELETE_RULE))
            elif isinstance(rel_klass, (tuple, list)):
                klass_props[format_ref_uid(pname)] = ListField(GenericLazyReferenceField(
                    choices=[get_class(k) for k in rel_klass]))
            if HAS_RELATIONSHIP_PROPERTIES:
                klass_props[format_ref_rel(pname)] = DictField()
        else:  # unique reference
            if isinstance(rel_klass, str):
                klass_props[format_ref_uid(pname)] = LazyReferenceField(
                    get_class(rel_klass), reverse_delete_rule=REVERSE_DELETE_RULE)
            elif isinstance(rel_klass, (tuple, list)):
                klass_props[format_ref_uid(pname)] = GenericLazyReferenceField(
                    choices=[get_class(k) for k in rel_klass])
            if HAS_RELATIONSHIP_PROPERTIES:
                klass_props[format_ref_rel(pname)] = DictField()
        klass_props.pop(pname, None)

    # add primary key field
    klass_props[PRIMARY_KEY] = PYDANTIC_TO_MONGO_TYPES[str](required=True)

    # add the custom to_json() encoder
    klass_props['raw_to_json'] = raw_to_json
    klass_props['to_json'] = to_json(relationships)

    # add util info for further processing
    klass_props['_constructors'] = constructors
    klass_props['_relationships'] = relationships
    klass_props['_additional_fields'] = additional_fields
    klass_props['response_model'] = return_class
    # create the actual database ORM class
    mongo_klass = type(klass_name, (Document,), klass_props)

    # apply hooks by injecting "klass" or "instance"
    apply_hooks(mongo_klass, hooks)

    DIRECT_TABLES[klass_name] = mongo_klass
    return mongo_klass


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
            if ptype in PYDANTIC_TO_MONGO_TYPES:
                setattr(db_schema, pname, PYDANTIC_TO_MONGO_TYPES[ptype](**poptions))

        # remove "_additional_fields" property from class
        # since it is not useful anymore
        delattr(db_schema, '_additional_fields')

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
import json
from datetime import datetime

from pydantic import create_model
from pydantic.main import BaseModel
from sqlalchemy import (Boolean,
                        Column,
                        DateTime,
                        Float,
                        ForeignKey,
                        Integer,
                        String,
                        Text)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.automap import AutomapBase
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import DeclarativeMeta

from cobblestone.database import Base
from cobblestone.helpers.types import get_real_type
from cobblestone.helpers.utils import (apply_hooks,
                                       clean_up_class_name,
                                       get_class,
                                       inflector,
                                       is_multi_rel,
                                       make_rel_field,
                                       PRIMARY_KEY,
                                       HAS_RELATIONSHIP_PROPERTIES,
                                       RETURN_RELATIONSHIP_PROPERTIES,
                                       DEFAULT_STRING_LENGTH,
                                       AUTO_DEFAULT_DATES)


DIRECT_TABLES = {}
ASSOCIATION_TABLES = {}

PYDANTIC_TO_SQL_TYPES = {
    str: String,
    int: Integer,
    float: Float,
    bool: Boolean,
    # list: ArrayProperty,
    datetime: DateTime,
    # typing.List: ArrayProperty,
}


def new_alchemy_encoder(session: Session, my_uid: str, populate: bool) -> json.JSONEncoder:
    '''
    From: https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
    Script by: Sasha B

    Encodes a SQLAlchemy object with recursive relationships; if a cycle is detected then it is
    ignored and replaced by None.
    '''
    _visited_objs = []
    _context = {'inverted_rels_mapping': {}}

    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don't re-visit self
                if obj in _visited_objs:
                    return None
                if not populate:
                    return None
                _visited_objs.append(obj)

                # an SQLAlchemy class
                # if it is a relationship, get the other object
                if obj.__class__.__name__.endswith('Rel'):
                    mappings = _context['inverted_rels_mapping']
                    pk_suffix = f'_{PRIMARY_KEY}'
                    pks = list(filter(lambda k: k.endswith(
                        pk_suffix), obj.__dict__.keys()))
                    my_key = list(
                        filter(lambda pk: getattr(obj, pk) == my_uid, pks))[0]
                    other_key = list(
                        filter(lambda pk: getattr(obj, pk) != my_uid, pks))[0]
                    other_uid = getattr(obj, other_key)
                    if id(obj) in mappings:
                        db_schema = DIRECT_TABLES[mappings[id(obj)]]
                    else:
                        other_klass = other_key.replace(pk_suffix, '')
                        schemas_module = importlib.import_module(
                            '.' + other_klass, 'cobblestone.models')
                        db_schema = getattr(
                            schemas_module, other_klass.title() + 'InDB')
                    other_item = session.query(
                        db_schema).filter_by(uid=other_uid).first()
                    if other_item is not None:
                        rel_data = json.loads(obj.data)
                        for k, v in obj.__dict__.items():
                            if not k.startswith('_') and k not in ['metadata', 'data', my_key, other_key]:
                                rel_data[k] = v
                        return {'item': other_item, 'rel': rel_data}
                    return None
                # else JSONify the object itself
                fields = {}
                obj_fields = [
                    x for x in dir(obj)
                    if not x.startswith('_') and x != 'metadata'
                ]
                # store the current object fields
                _context['inverted_rels_mapping'] = {}
                for field in obj_fields:
                    field_value = getattr(obj, field)
                    if hasattr(field_value, '__call__'):
                        continue
                    if '__rel__' in field:
                        field_name, rel_type = field.split('__rel__')
                        _context['inverted_rels_mapping'][id(field_value)] = rel_type
                    else:
                        field_name = field
                    if field_name not in fields or fields[field_name] is None:
                        fields[field_name] = field_value
                # a json-encodable dict
                return fields

            if isinstance(obj, datetime):
                return obj.isoformat()

            return json.JSONEncoder.default(self, obj)

    return AlchemyEncoder


def to_json() -> dict:
    def _to_json(instance: AutomapBase, session: Session, populate: bool = True) -> dict:
        data = json.loads(json.dumps(
            instance,
            cls=new_alchemy_encoder(session, instance.uid, populate),
            check_circular=False
        ))
        return data
    return _to_json


def to_repr(instance: AutomapBase) -> str:
    cols = {c.name: getattr(instance, c.name)
            for c in instance.__table__.columns}
    cols = ', '.join([f'{k} = {v}' for k, v in cols.items()])
    return f'{instance.__class__.__name__}({cols})'


def PydanticParamsToSQLColumns(schema: dict, params: dict) -> dict:
    required = schema.get('required', [])
    klass_props = {}
    for pname, pdata in schema['properties'].items():
        t = get_real_type(params[pname].annotation)
        poptions = {}
        if pname in required:
            poptions['nullable'] = False
        if 'default' in pdata:
            poptions['default'] = pdata['default']
        elif t == datetime and AUTO_DEFAULT_DATES:
            poptions['default'] = datetime.utcnow
        if t in PYDANTIC_TO_SQL_TYPES:
            # (specific case: for string columns, some SQL databases require
            # an explicit string length: initialize to the given default)
            _t = PYDANTIC_TO_SQL_TYPES[t]
            if isinstance(_t, String):
                klass_props[pname] = Column(
                    _t(DEFAULT_STRING_LENGTH), **poptions)
            else:
                klass_props[pname] = Column(_t, **poptions)
    return klass_props


def PydanticClassToSQLColumns(klass: BaseModel) -> dict:
    schema = klass.schema()
    klass_params = inspect.signature(klass).parameters
    return PydanticParamsToSQLColumns(schema, klass_params)


def PydanticToORM(
    klass: BaseModel,
    collection: str = None,
    constructors: dict = {},
    relationships: dict = {},
    additional_fields: dict = {},
    hooks: dict = {},
    return_class: str = None
) -> AutomapBase:
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
    klass_props = {'__tablename__': collection}
    klass_props.update(PydanticParamsToSQLColumns(schema, klass_params))

    # automatically check for+add an integer auto-increment
    # primary key column if necessary
    klass_props[PRIMARY_KEY] = Column(
        String(40),
        primary_key=True,
        index=True)

    # if there are relationships: for each, create the corresponding
    # association objects and relationship fields (association objects
    # allow for relationship properties)
    for pname, pdata in relationships.items():
        rel_klasses = pdata['target']
        if not isinstance(rel_klasses, (tuple, list)):
            rel_klasses = [rel_klasses]
        for rel_klass in rel_klasses:
            rel_klass_name = rel_klass.split('.')[-1]
            clean_klass_name = clean_up_class_name(base_klass_name).title()
            clean_rel_klass_name = clean_up_class_name(rel_klass_name).title()
            association_name = f'{clean_klass_name}_to_{clean_rel_klass_name}'
            association_klass_name = f'{association_name}Rel'
            uselist = is_multi_rel(pdata)
            if association_name not in ASSOCIATION_TABLES:
                association_table_props = {
                    '__tablename__': association_name,
                    f'{clean_klass_name.lower()}_{PRIMARY_KEY}': Column(
                        String(40),
                        ForeignKey(f'{clean_klass_name}.{PRIMARY_KEY}'),
                        primary_key=True
                    ),
                    f'{clean_rel_klass_name.lower()}_{PRIMARY_KEY}': Column(
                        String(40),
                        ForeignKey(f'{clean_rel_klass_name}.{PRIMARY_KEY}'),
                        primary_key=True
                    ),
                    clean_klass_name.lower(): relationship(
                        f'{clean_klass_name}InDB',
                        uselist=uselist,
                        back_populates=f'{pname}__rel__{rel_klass_name}'
                    ),
                }
                # if relationships have properties, store the JSON
                # data as a stringified text column
                if HAS_RELATIONSHIP_PROPERTIES:
                    association_table_props['data'] = Column(Text)
                if (m := pdata.get('model')):
                    association_table_props.update(PydanticClassToSQLColumns(m))
                association_table_props['__repr__'] = to_repr
                association_table = type(
                    association_klass_name, (Base,), association_table_props)
                ASSOCIATION_TABLES[association_name] = association_table
            klass_props[f'{pname}__rel__{rel_klass_name}'] = relationship(
                association_klass_name,
                uselist=uselist
            )

    # add the custom to_json() encoder
    klass_props['to_json'] = to_json()

    # add util info for further processing
    klass_props['_constructors'] = constructors
    klass_props['_relationships'] = relationships
    klass_props['_additional_fields'] = additional_fields
    klass_props['response_model'] = return_class
    klass_props['__repr__'] = to_repr
    # create the actual database ORM class
    sql_klass = type(klass_name, (Base,), klass_props)

    # apply hooks by injecting "klass" or "instance"
    apply_hooks(sql_klass, hooks)

    DIRECT_TABLES[klass_name] = sql_klass
    return sql_klass


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
            if ptype in PYDANTIC_TO_SQL_TYPES:
                setattr(db_schema, pname, PYDANTIC_TO_SQL_TYPES[ptype](**poptions))

        # remove "_additional_fields" property from class
        # since it is not useful anymore
        delattr(db_schema, '_additional_fields')

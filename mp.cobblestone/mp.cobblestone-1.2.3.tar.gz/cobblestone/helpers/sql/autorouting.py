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
import json
from typing import Dict, List, Literal, Optional, Union

from fastapi import Depends, HTTPException
from fastapi.applications import FastAPI

from cobblestone.security import oauth2_scheme
from cobblestone.tokens import check_token
from cobblestone.database import session_scope
from cobblestone.helpers.converters import ASSOCIATION_TABLES
from cobblestone.helpers.utils import (clean_up_class_name,
                                       create_uid,
                                       inflector,
                                       invalid_input_data_exception,
                                       is_multi_rel,
                                       format_ref_uid,
                                       format_ref_rel,
                                       get_class,
                                       PRIMARY_KEY,
                                       HAS_RELATIONSHIP_PROPERTIES)
from cobblestone.helpers.tools import find_by_id


OrderingDirections = Union[Literal['asc'], Literal['desc']]


def create_handlers(schema: str, raw_name: str):
    schemas_module = importlib.import_module(
        '.' + raw_name, 'cobblestone.models')
    full_schema = getattr(schemas_module, schema + 'Full')
    db_schema = getattr(schemas_module, schema + 'InDB')

    # .. create
    def create_instance_handler(data: dict) -> dict:
        if hasattr(db_schema, 'before_create'):
            db_schema.before_create()

        data = data.dict()
        data[PRIMARY_KEY] = create_uid()
        for k, v in getattr(db_schema, '_constructors').items():
            data[k] = v(data)
        linked_instances = []
        for k, v in getattr(db_schema, '_relationships').items():
            linked_schema = full_schema.schema()['properties'][k]
            linked_uid = data.get(format_ref_uid(k))
            cardinality = v.get('cardinality', 'ZeroOrMore')
            rel_model = v.get('model', None)
            uselist = is_multi_rel(v)
            if not linked_uid:
                dft = linked_schema.get('default')
                if dft is None:
                    raise invalid_input_data_exception
                else:
                    linked_uid = dft
            if isinstance(linked_uid, (list, tuple)) and len(linked_uid) == 0:
                continue
            linked_klass = v['target']
            if isinstance(linked_klass, str):
                linked_klass = [get_class(linked_klass)]
            elif isinstance(linked_klass, (tuple, list)):
                linked_klass = [get_class(k) for k in linked_klass]
            if isinstance(linked_uid, list):
                props = [] if not HAS_RELATIONSHIP_PROPERTIES else data.get(
                    format_ref_rel(k), [])
                for linked_k in linked_klass:
                    other_klass = clean_up_class_name(
                        linked_k.__name__).title()
                    link_klass_name = \
                        f'{clean_up_class_name(schema).title()}' + \
                        '_to_' + \
                        f'{other_klass}'
                    link_klass = ASSOCIATION_TABLES[link_klass_name]
                    with session_scope() as session:
                        for i, x in enumerate(session.query(linked_k).filter(linked_k.uid.in_(linked_uid)).all()):
                            p = props[i] if i < len(props) else {}
                            p['label'] = v.get('label', '')
                            if rel_model is not None:
                                p.update(rel_model(**p).dict())
                            linked_instances.append(
                                (k, x.uid, other_klass, link_klass, uselist, p))
            else:
                props = {} if not HAS_RELATIONSHIP_PROPERTIES else data.get(
                    format_ref_rel(k), {})
                props['label'] = v.get('label', '')
                if rel_model is not None:
                    props.update(rel_model(**props).dict())
                other = None
                with session_scope() as session:
                    other = find_by_id(session, linked_klass, linked_uid)
                    if other is not None:
                        other_klass = other.__class__.__name__
                        link_klass_name = \
                            f'{clean_up_class_name(schema).title()}' + \
                            '_to_' + \
                            f'{clean_up_class_name(other_klass)}'
                        link_klass = ASSOCIATION_TABLES[link_klass_name]
                        linked_instances.append(
                            (k, getattr(other, PRIMARY_KEY), other_klass, link_klass, uselist, props))
            if len(linked_instances) == 0 and cardinality.startswith('One'):
                raise invalid_input_data_exception
            data.pop(format_ref_uid(k), None)
            data.pop(format_ref_rel(k), None)
        instance = db_schema(**data)
        with session_scope() as session:
            for k, uid, other_klass, link_klass, uselist, props in linked_instances:
                link_props = {}
                if HAS_RELATIONSHIP_PROPERTIES:
                    link_props['data'] = json.dumps(props)
                link = link_klass(**link_props)
                link_uid = format_ref_uid(clean_up_class_name(schema).lower())
                rel_link_uid = format_ref_uid(clean_up_class_name(other_klass).lower())
                setattr(link, link_uid, getattr(instance, PRIMARY_KEY))
                setattr(link, rel_link_uid, uid)
                if uselist:
                    getattr(instance, f'{k}__rel__{other_klass}').append(link)
                else:
                    setattr(instance, f'{k}__rel__{other_klass}', link)
            session.add(instance)
            if hasattr(db_schema, 'after_create'):
                instance.after_create()
            return instance.to_json(session)

    # .. read
    def list_instances_handler(
        skip: int,
        limit: int,
        sort_by: Optional[str] = None,
        sort_dir: OrderingDirections = 'asc'
    ) -> List[Dict]:
        if hasattr(db_schema, 'before_read'):
            db_schema.before_read(multiple=True)
        results = []
        with session_scope() as session:
            req = session.query(db_schema)
            if sort_by is not None:
                order_clause = getattr(db_schema, sort_by)
                if sort_dir == 'desc':
                    order_clause = order_clause.desc()
                req = req.order_by(order_clause)
            for instance in req.offset(skip).limit(limit):
                results.append(instance.to_json(session))
                if hasattr(db_schema, 'after_read'):
                    instance.after_read()
        return results

    def get_instance_by_uid_handler(uid: str) -> dict:
        if hasattr(db_schema, 'before_read'):
            db_schema.before_read(multiple=False)
        with session_scope() as session:
            instance = session.query(db_schema).filter_by(uid=uid).first()
            if instance:
                if hasattr(db_schema, 'after_read'):
                    instance.after_read()
                return instance.to_json(session)
            else:
                return None

    # .. update
    def patch_at_uid_handler(uid: str, update: dict) -> dict:
        if hasattr(db_schema, 'before_update'):
            db_schema.before_update()
        with session_scope() as session:
            instance = session.query(db_schema).filter_by(uid=uid).first()
            if instance:
                for k, v in update.items():
                    setattr(instance, k, v)
                if hasattr(db_schema, 'after_update'):
                    instance.after_update()
                return instance.to_json(session)
            else:
                return None

    # .. delete
    def delete_all_instances_handler():
        if hasattr(db_schema, 'before_delete'):
            db_schema.before_delete(multiple=True)
        with session_scope() as session:
            session.query(db_schema).delete()
        if hasattr(db_schema, 'after_delete'):
            db_schema.after_delete()

    def delete_instance_by_uid_handler(uid: str):
        if hasattr(db_schema, 'before_delete'):
            db_schema.before_delete(multiple=False)
        with session_scope() as session:
            instance = session.query(db_schema).filter_by(uid=uid).first()
            if instance:
                session.delete(instance)
                if hasattr(db_schema, 'after_delete'):
                    instance.after_delete()
            else:
                return None

    return {
        'create_instance_handler': create_instance_handler,
        'list_instances_handler': list_instances_handler,
        'get_instance_by_uid_handler': get_instance_by_uid_handler,
        'patch_at_uid_handler': patch_at_uid_handler,
        'delete_all_instances_handler': delete_all_instances_handler,
        'delete_instance_by_uid_handler': delete_instance_by_uid_handler,
    }


def create_router(app: FastAPI, schema: str, raw_name: str, handlers: dict):
    schemas_module = importlib.import_module(
        '.' + raw_name, 'cobblestone.models')
    base_schema = getattr(schemas_module, schema)
    payload_schema = getattr(schemas_module, schema + 'Payload', base_schema)
    return_schema = getattr(schemas_module, schema + 'InDB').response_model

    # (some special cases are handled by hand)
    if raw_name == 'notes':
        raw_name_plural = 'notes'
    else:
        raw_name_plural = inflector.plural(raw_name)

    # .. create
    @app.post(
        '/{}'.format(raw_name_plural),
        response_model=return_schema,
        tags=[raw_name_plural],
        status_code=201,
    )
    async def create_instance(instance_data: payload_schema, token: str = Depends(oauth2_scheme)) -> dict:
        check_token(token)
        return handlers['create_instance_handler'](instance_data)

    # .. read
    @app.get(
        '/{}'.format(raw_name_plural),
        response_model=List[return_schema],
        tags=[raw_name_plural],
    )
    async def list_instances(
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_dir: OrderingDirections = 'asc',
        token: str = Depends(oauth2_scheme)
    ) -> List[Dict]:
        check_token(token)
        return handlers['list_instances_handler'](skip, limit, sort_by, sort_dir)

    @app.get(
        '/{}/{{uid}}'.format(raw_name_plural),
        response_model=return_schema,
        tags=[raw_name_plural],
    )
    def get_instance_by_uid(uid: str, token: str = Depends(oauth2_scheme)) -> dict:
        check_token(token)
        return handlers['get_instance_by_uid_handler'](uid)

    # .. update

    @app.patch(
        '/{}/{{uid}}'.format(raw_name_plural),
        response_model=return_schema,
        tags=[raw_name_plural],
    )
    def patch_at_uid(uid: str, update: dict, token: str = Depends(oauth2_scheme)) -> dict:
        check_token(token)
        return handlers['patch_at_uid_handler'](uid, update)

    # .. delete

    @app.delete(
        '/{}'.format(raw_name_plural),
        tags=[raw_name_plural],
    )
    def delete_all_instances(token: str = Depends(oauth2_scheme)):
        check_token(token)
        return handlers['delete_all_instances_handler']()

    @app.delete(
        '/{}/{{uid}}'.format(raw_name_plural),
        tags=[raw_name_plural],
    )
    def delete_instance_by_uid(uid: str, token: str = Depends(oauth2_scheme)):
        check_token(token)
        return handlers['delete_instance_by_uid_handler'](uid)

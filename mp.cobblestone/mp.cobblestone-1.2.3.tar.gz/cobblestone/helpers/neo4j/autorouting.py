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
from typing import Dict, List, Literal, Optional, Union

from fastapi import Depends
from fastapi.applications import FastAPI

from cobblestone.security import oauth2_scheme
from cobblestone.tokens import check_token
from cobblestone.helpers.utils import (create_uid,
                                       inflector,
                                       invalid_input_data_exception,
                                       format_ref_uid,
                                       format_ref_rel,
                                       get_class,
                                       PRIMARY_KEY,
                                       HAS_RELATIONSHIP_PROPERTIES)


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
            if not linked_uid:
                dft = linked_schema.get('default')
                # error if we need at least one connection and we don't
                # have any (provided by the user or by the class defaults)
                if not cardinality.startswith('Zero') and dft is None:
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
                    for i, x in enumerate(linked_k.nodes.filter(uid__in=linked_uid).all()):
                        p = props[i] if i < len(props) else {}
                        if rel_model is not None:
                            p.update(rel_model(**p).dict())
                        linked_instances.append((k, x, p))
            else:
                props = {} if not HAS_RELATIONSHIP_PROPERTIES else data.get(
                    format_ref_rel(k), {})
                if rel_model is not None:
                    props.update(rel_model(**props).dict())
                for linked_k in linked_klass:
                    linked_instance = linked_k.nodes.get_or_none(
                        uid=linked_uid)
                    if linked_instance is not None:
                        linked_instances.append((k, linked_instance, props))
            if len(linked_instances) == 0 and cardinality.startswith('One'):
                raise invalid_input_data_exception
            data.pop(format_ref_rel(k), None)
        instance = db_schema(**data).save()
        for k, i, props in linked_instances:
            getattr(instance, k).connect(i, props)
        instance.refresh()
        if hasattr(db_schema, 'after_create'):
            instance.after_create()
        return instance.to_json()

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
        req = db_schema.nodes
        if sort_by is not None:
            order = ('' if sort_dir == 'asc' else '-') + sort_by
            req = req.order_by(order)
        else:
            req = req.all()
        for instance in req[skip:skip + limit]:
            results.append(instance.to_json())
            if hasattr(db_schema, 'after_read'):
                instance.after_read()
        return results

    def get_instance_by_uid_handler(uid: str) -> dict:
        if hasattr(db_schema, 'before_read'):
            db_schema.before_read(multiple=False)
        instance = db_schema.nodes.get_or_none(uid=uid)
        if instance:
            if hasattr(db_schema, 'after_read'):
                instance.after_read()
            return instance.to_json()
        else:
            return None

    # .. update
    def patch_at_uid_handler(uid: str, update: dict) -> dict:
        if hasattr(db_schema, 'before_update'):
            db_schema.before_update()
        instance = db_schema.nodes.get_or_none(uid=uid)
        if instance:
            for k, v in update.items():
                setattr(instance, k, v)
            instance.save()
            if hasattr(db_schema, 'after_update'):
                instance.after_update()
            return instance.to_json()
        else:
            return None

    # .. delete
    def delete_all_instances_handler():
        if hasattr(db_schema, 'before_delete'):
            db_schema.before_delete(multiple=True)
        for instance in db_schema.nodes.all():
            instance.delete()
        if hasattr(db_schema, 'after_delete'):
            db_schema.after_delete()

    def delete_instance_by_uid_handler(uid: str):
        if hasattr(db_schema, 'before_delete'):
            db_schema.before_delete(multiple=False)
        instance = db_schema.nodes.get_or_none(uid=uid)
        if instance:
            instance.delete()
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

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

from fastapi import FastAPI, Depends
from mongoengine import DoesNotExist, MultipleObjectsReturned

from cobblestone.security import oauth2_scheme
from cobblestone.tokens import check_token
from cobblestone.helpers.tools import create_relationship
from cobblestone.helpers.utils import (create_uid,
                                       format_ref_uid,
                                       format_ref_rel,
                                       inflector,
                                       invalid_input_data_exception,
                                       get_class,
                                       is_multi_rel,
                                       PRIMARY_KEY,
                                       HAS_RELATIONSHIP_PROPERTIES)


OrderingDirections = Union[Literal['asc'], Literal['desc']]


def create_handlers(schema: str, raw_name: str):
    schemas_module = importlib.import_module(
        '.' + raw_name, 'cobblestone.models')
    db_schema = getattr(schemas_module, schema + 'InDB')

    # .. create
    def create_instance_handler(data: dict) -> dict:
        if hasattr(db_schema, 'before_create'):
            db_schema.before_create()

        data = data.dict()
        data[PRIMARY_KEY] = create_uid()
        for k, v in getattr(db_schema, '_constructors').items():
            data[k] = v(data)
        for k, v in getattr(db_schema, '_relationships').items():
            rel_key = format_ref_uid(k)
            rel_val = data.get(rel_key)
            rel_klass = v['target']
            if isinstance(rel_klass, (tuple, list)):
                # Mongo specificity: in case of a multi-targets link (i.e. multiple
                # types of documents are valid for the relationship), we use a
                # GenericLazyReferenceField: this does not accept direct IDs but requires
                # the full Mongo object from the database
                got_result = False
                for rel_k in rel_klass:
                    c = get_class(rel_k)
                    try:
                        if is_multi_rel(v):
                            rel_instance = c.objects(pk__in=rel_val).all()
                        else:
                            rel_instance = c.objects(pk=rel_val).get()
                        if rel_instance:
                            got_result = True
                            data[rel_key] = rel_instance
                            break
                    except (DoesNotExist, MultipleObjectsReturned):
                        pass
                if not got_result:
                    raise invalid_input_data_exception
            else:
                try:
                    rel_instance = c = get_class(rel_klass).objects(pk=rel_val).get()
                    if rel_instance:
                        data[rel_key] = rel_instance
                except (DoesNotExist, MultipleObjectsReturned):
                    raise invalid_input_data_exception
            if HAS_RELATIONSHIP_PROPERTIES:
                ref_rel = format_ref_rel(k)
                props = data.pop(ref_rel, {})
                rel_data = create_relationship(schema, rel_val, k, v, **props)
                if rel_data:
                    data[ref_rel] = rel_data
        instance = db_schema(**data).save()
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
        req = db_schema.objects
        if sort_by is not None:
            order = ('' if sort_dir == 'asc' else '-') + sort_by
            req = req().order_by(order)
        for instance in req[skip:skip + limit]:
            results.append(instance.to_json())
            if hasattr(db_schema, 'after_read'):
                instance.after_read()
        return results

    def get_instance_by_uid_handler(uid: str) -> dict:
        if hasattr(db_schema, 'before_read'):
            db_schema.before_read(multiple=False)
        try:
            instance = db_schema.objects(pk=uid).get()
            if hasattr(db_schema, 'after_read'):
                instance.after_read()
            return instance.to_json()
        except (DoesNotExist, MultipleObjectsReturned):
            return None

    # .. update
    def patch_at_uid_handler(uid: str, update: dict) -> dict:
        if hasattr(db_schema, 'before_update'):
            db_schema.before_update()
        try:
            instance = db_schema.objects(pk=uid).get()
        except (DoesNotExist, MultipleObjectsReturned):
            return None
        for k, v in update.items():
            setattr(instance, k, v)
        instance.save()
        if hasattr(db_schema, 'after_update'):
            instance.after_update()
        return instance.to_json()

    # .. delete
    def delete_all_instances_handler():
        if hasattr(db_schema, 'before_delete'):
            db_schema.before_delete(multiple=True)
        for instance in db_schema.objects:
            instance.delete()
        if hasattr(db_schema, 'after_delete'):
            db_schema.after_delete()

    def delete_instance_by_uid_handler(uid: str):
        if hasattr(db_schema, 'before_delete'):
            db_schema.before_delete(multiple=False)
        try:
            instance = db_schema.objects(pk=uid).get()
            instance.delete()
            if hasattr(db_schema, 'after_delete'):
                instance.after_delete()
        except (DoesNotExist, MultipleObjectsReturned):
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

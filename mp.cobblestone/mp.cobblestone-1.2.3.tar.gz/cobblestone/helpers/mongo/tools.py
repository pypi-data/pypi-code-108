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

from typing import Union
from mongoengine import DoesNotExist, MultipleObjectsReturned
from mongoengine.document import Document
from pydantic.main import BaseModel

from cobblestone.helpers.utils import (clean_up_class_name,
                                       format_ref_rel,
                                       format_ref_uid,
                                       get_class,
                                       invalid_input_data_exception,
                                       is_multi_rel,
                                       HAS_RELATIONSHIP_PROPERTIES)


def create_relationship(
    schema: BaseModel,
    other_pk: str,
    prop_name: str,
    rel: dict,
    **props
) -> dict:
    if not HAS_RELATIONSHIP_PROPERTIES:
        return None
    full_schema = get_class(
        f'cobblestone.models.{schema.lower()}.{schema}Full')
    linked_schema = full_schema.schema()['properties'][prop_name]
    if not other_pk:
        dft = linked_schema.get('default')
        if dft is None:
            raise invalid_input_data_exception
        else:
            other_pk = dft
    if isinstance(other_pk, (list, tuple)) and len(other_pk) == 0:
        return None
    rel_data = {'label': rel.get('label', None)}
    if (m := rel.get('model')):
        rel_data.update(m(**props).dict())
    return rel_data


def find(klasses: Union[tuple, list], **query) -> Document:
    if not isinstance(klasses, (tuple, list)):
        klasses = [klasses]
    for klass in klasses:
        try:
            instance = klass.objects(**query).get()
            return instance
        except (DoesNotExist, MultipleObjectsReturned):
            pass
    return None


def find_by_id(klasses: Union[tuple, list], id: str) -> Document:
    if not isinstance(klasses, (tuple, list)):
        klasses = [klasses]
    return find(klasses, pk=id)


def is_connected(instance: Document, other_pk: str, prop_name: str) -> bool:
    p_uid = format_ref_uid(prop_name)
    rel = instance._relationships[prop_name]
    if is_multi_rel(rel):
        return other_pk in [x.pk for x in getattr(instance, p_uid)]
    else:
        return getattr(instance, p_uid).pk == other_pk


def connect(instance: Document, other_pk: str, prop_name: str, prop_data: dict = {}, force: bool = False):
    # avoid recreating the connection, unless it is forced
    if is_connected(instance, other_pk, prop_name) and not force:
        return
    schema = clean_up_class_name(instance.__class__.__name__)
    p_uid = format_ref_uid(prop_name)
    p_rel = format_ref_rel(prop_name)
    rel = instance._relationships[prop_name]
    rel_data = create_relationship(
        schema, other_pk, prop_name, rel, **prop_data)
    if is_multi_rel(rel):
        getattr(instance, p_uid).append(other_pk)
    else:
        setattr(instance, p_uid, other_pk)
        if HAS_RELATIONSHIP_PROPERTIES and rel_data:
            setattr(instance, p_rel, rel_data)


def disconnect(instance: Document, other_pk: str, prop_name: str):
    # ignore disconnection if there is already no connection!
    if not is_connected(instance, other_pk, prop_name):
        return
    p_uid = format_ref_uid(prop_name)
    p_rel = format_ref_rel(prop_name)
    rel = instance._relationships[prop_name]
    if is_multi_rel(rel):
        pks = [x.pk for x in getattr(instance, p_uid)]
        getattr(instance, p_uid).pop(pks.index(other_pk))
        if HAS_RELATIONSHIP_PROPERTIES:
            getattr(instance, p_rel).pop(other_pk, None)
    else:
        setattr(instance, p_uid, None)
        if HAS_RELATIONSHIP_PROPERTIES:
            setattr(instance, p_rel, {})


def save_and_update(instance: Document):
    instance.save()

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

import json
from typing import Union
from sqlalchemy.ext.automap import AutomapBase
from sqlalchemy.orm.session import Session

from cobblestone.helpers.utils import (clean_up_class_name,
                                       format_ref_uid,
                                       is_multi_rel,
                                       PRIMARY_KEY)
from cobblestone.helpers.converters import ASSOCIATION_TABLES


def find(session: Session, klasses: Union[tuple, list], **query) -> AutomapBase:
    if not isinstance(klasses, (tuple, list)):
        klasses = [klasses]
    for klass in klasses:
        instance = session.query(klass).filter_by(**query).first()
        if instance is not None:
            return instance
    return None


def find_by_id(session: Session, klasses: Union[tuple, list], id: str) -> AutomapBase:
    if not isinstance(klasses, (tuple, list)):
        klasses = [klasses]
    query = {PRIMARY_KEY: id}
    return find(session, klasses, **query)


def is_connected(instance: AutomapBase, other: AutomapBase, prop_name: str) -> bool:
    other_pk = getattr(other, PRIMARY_KEY)
    rel = instance._relationships[prop_name]
    other_klass_name = other.__class__.__name__
    other_schema = clean_up_class_name(other_klass_name)
    other_rel_uid = format_ref_uid(other_schema.lower())
    pname = f'{prop_name}__rel__{other_klass_name}'
    if is_multi_rel(rel):
        current_rel = list(filter(
            lambda r: getattr(r, other_rel_uid) == other_pk,
            getattr(instance, pname)
        ))
        if len(current_rel) > 0:
            return True
    else:
        current_rel = getattr(instance, pname)
        if current_rel is None:
            return False
        connected_pk = [
            v for k, v in current_rel.__dict__.items()
            if k.endswith(f'_{PRIMARY_KEY}') and v != getattr(instance, PRIMARY_KEY)
        ][0]
        if connected_pk == other_pk:
            return True
    return False


def connect(
    session: Session,
    instance: AutomapBase,
    other: AutomapBase,
    prop_name: str,
    prop_data: dict = {},
    force: bool = False
):
    # avoid recreating the connection, unless it is forced
    if is_connected(instance, other, prop_name) and not force:
        return
    rel = instance._relationships[prop_name]
    schema = clean_up_class_name(instance.__class__.__name__)
    other_klass_name = other.__class__.__name__
    other_schema = clean_up_class_name(other_klass_name)
    rel_class = ASSOCIATION_TABLES[f'{schema}_to_{other_schema}']
    pname = f'{prop_name}__rel__{other_klass_name}'
    # (add "label" key in relationship data)
    prop_data['label'] = rel['label']
    new_rel = rel_class(data=json.dumps(prop_data))
    setattr(new_rel, format_ref_uid(schema.lower()),
            getattr(instance, PRIMARY_KEY))
    setattr(new_rel, format_ref_uid(other_schema.lower()), getattr(other, PRIMARY_KEY))
    if is_multi_rel(rel):
        getattr(instance, pname).append(new_rel)
    else:
        # (remove previous connection first)
        rel_targets = rel['target']
        if not isinstance(rel_targets, (tuple, list)):
            rel_targets = [rel_targets]
        for rel_target in rel_targets:
            k = rel_target.split('.')[-1]
            if (r := getattr(instance, f'{prop_name}__rel__{k}')) != None:
                session.delete(r)
                break
        setattr(instance, pname, new_rel)


def disconnect(session: Session, instance: AutomapBase, other: AutomapBase, prop_name: str):
    # ignore disconnection if there is already no connection!
    if not is_connected(instance, other, prop_name):
        return
    rel = instance._relationships[prop_name]
    other_klass_name = other.__class__.__name__
    other_schema = clean_up_class_name(other_klass_name)
    other_rel_uid = format_ref_uid(other_schema.lower())
    pname = f'{prop_name}__rel__{other_klass_name}'
    current_rel = list(filter(
        lambda r: getattr(r, other_rel_uid) == getattr(other, PRIMARY_KEY),
        getattr(instance, pname)
    ))
    if is_multi_rel(rel):
        session.delete(current_rel[0])
    else:
        setattr(instance, pname, None)


def save_and_update(session: Session):
    session.commit()

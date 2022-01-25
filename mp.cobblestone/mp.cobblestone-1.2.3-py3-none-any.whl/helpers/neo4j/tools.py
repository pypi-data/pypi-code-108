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

from neomodel.core import StructuredNode
from cobblestone.helpers.utils import is_multi_rel, PRIMARY_KEY


def find(klasses: Union[tuple, list], **query) -> StructuredNode:
    if not isinstance(klasses, (tuple, list)):
        klasses = [klasses]
    for klass in klasses:
        instance = klass.nodes.get_or_none(**query)
        if instance is not None:
            return instance
    return None


def find_by_id(klasses: Union[tuple, list], id: str) -> StructuredNode:
    if not isinstance(klasses, (tuple, list)):
        klasses = [klasses]
    query = {PRIMARY_KEY: id}
    return find(klasses, **query)


def is_connected(instance: StructuredNode, other: StructuredNode, prop_name: str) -> bool:
    return getattr(instance, prop_name).is_connected(other)


def connect(
    instance: StructuredNode,
    other: StructuredNode,
    prop_name: str,
    prop_data: dict = {},
    force: bool = False
):
    # avoid recreating the connection, unless it is forced
    if is_connected(instance, other, prop_name) and not force:
        return
    rel = instance._relationships[prop_name]
    if is_multi_rel(rel):
        getattr(instance, prop_name).connect(other, prop_data)
    else:
        old = getattr(instance, prop_name).single()
        getattr(instance, prop_name).reconnect(old, other)


def disconnect(instance: StructuredNode, other: StructuredNode, prop_name: str):
    # ignore disconnection if there is already no connection!
    if not is_connected(instance, other, prop_name):
        return
    getattr(instance, prop_name).disconnect(other)


def save_and_update(instance: StructuredNode):
    instance.refresh()

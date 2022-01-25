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

import os
import importlib
import uuid
from typing import Callable, Dict, List, Union, get_args

import inflect
from fastapi import HTTPException

from cobblestone.helpers.types import is_union


inflector = inflect.engine()

HAS_RELATIONSHIP_PROPERTIES = os.getenv(
    'HAS_RELATIONSHIP_PROPERTIES') == 'True'
RETURN_RELATIONSHIP_PROPERTIES = HAS_RELATIONSHIP_PROPERTIES \
    and os.getenv('RETURN_RELATIONSHIP_PROPERTIES', 'False') == 'True'
DEFAULT_STRING_LENGTH = os.getenv(
    'DEFAULT_STRING_LENGTH', 64)
AUTO_DEFAULT_DATES = os.getenv(
    'AUTO_DEFAULT_DATES', 'True') == 'True'
PRIMARY_KEY = os.getenv('PRIMARY_KEY', 'uid')
PRIMARY_KEY_SUFFIX = '_' + PRIMARY_KEY
REF_REL_SUFFIX = '_' + os.getenv('REF_REL', 'rel')

CLASS_HOOKS = ['before_create', 'before_read', 'before_update', 'before_delete', 'after_delete']
INSTANCE_HOOKS = ['after_create', 'after_read', 'after_update']

invalid_input_data_exception = HTTPException(
    status_code=400,
    detail='invalid-input-data',
    headers={'WWW-Authenticate': 'Bearer'},
)


def create_uid() -> str:
    return str(uuid.uuid4())


def format_ref_uid(ref: str) -> str:
    return ref + PRIMARY_KEY_SUFFIX


def format_ref_rel(ref: str) -> str:
    return ref + REF_REL_SUFFIX


def get_class(import_path: str):
    try:
        *m, n, c = import_path.split('.')
        return getattr(importlib.import_module('.' + n, '.'.join(m)), c)
    except:
        return None


def rel(klass: type) -> Dict:
    return Dict[str, Union[klass, dict]]


def make_rel_field(field) -> Dict:
    t = field.outer_type_
    args = get_args(t)
    if len(args) > 0:
        new_t = Union if is_union(t) else List
        return new_t[tuple(rel(x) for x in args)]
    return rel(t)


def is_multi_rel(rel: dict) -> bool:
    c = rel.get('cardinality', 'ZeroOrMore')
    return c.endswith('OrMore')


def clean_up_class_name(name: str) -> str:
    return name.replace('Full', '').replace('Protected', '').replace('InDB', '')


def create_instance_method(func: Callable) -> Callable:
    def _method(instance):
        return func(instance)
    return _method


def apply_hooks(klass: type, hooks: dict):
    # apply hooks by injecting "klass" or "instance"
    for hook_name, hook_func in hooks.items():
        # ("before" hooks pass in the klass)
        if hook_name in CLASS_HOOKS:
            setattr(klass, hook_name, classmethod(hook_func))
        # ("after" hooks pass in the instance)
        elif hook_name in INSTANCE_HOOKS:
            setattr(klass, hook_name, create_instance_method(hook_func))

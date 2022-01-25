# SPDX-License-Identifier: Apache-2.0
# Copyright © 2021 Wrangle Ltd

import json
import re
import typing

import attr


def to_camel_case(s):
    components = s.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


word_break_pattern = re.compile(r'([a-z])([A-Z])')


def to_snake_case(s):
    return word_break_pattern.sub(r'\1_\2', s).lower()


def none_field_transformer(cls, fields):
    return [
        field if field.default != attr.NOTHING else field.evolve(
            default=None)
        for field in fields
    ]


def field_transformer(namespace):
    def transform(cls, fields):
        results = []
        attr.resolve_types(
            cls, globalns=namespace, localns={cls.__name__: cls}, attribs=fields)
        for field in fields:
            original_type = getattr(field.type, '__origin__', None)
            if type(field.type) is str and field.type == cls.__name__:
                field = field.evolve(type=cls)
            if type(field.type) is type:
                validator = attr.validators.instance_of(field.type)
            elif original_type is list or original_type is typing.List:
                validator = attr.validators.deep_iterable(
                    member_validator=attr.validators.instance_of(
                        field.type.__args__[0])
                )
            elif original_type is dict or original_type is typing.Dict:
                validator = attr.validators.deep_mapping(
                    key_validator=attr.validators.instance_of(
                        field.type.__args__[0]),
                    value_validator=attr.validators.instance_of(
                        field.type.__args__[1])
                )
            else:
                raise TypeError(
                    'unanticipated type %s (%s)' % (field.type, getattr(field.type, '__origin__')))
            validator = attr.validators.optional(validator)
            validator = (
                validator if field.validator is None
                else attr.validators.and_(field.validator, validator)
            )
            results.append(field.evolve(
                default=None,
                validator=validator
            ))
        return results
    return transform


class _JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if attr.has(obj.__class__):
            fields = attr.fields(obj.__class__)
            return {
                to_camel_case(field.name): getattr(obj, field.name)
                for field in fields if getattr(obj, field.name) is not None
            }
        return super().default(obj)


def json_dumps(inst, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, indent=None, separators=None, default=None, sort_keys=False, **kwargs):
    return json.dumps(
        inst, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, allow_nan=allow_nan,
        cls=_JSONEncoder, indent=indent, separators=separators, default=default, sort_keys=sort_keys, **kwargs
    )


def json_loads(s, serializer_cls):
    data = json.loads(s)
    return _deserialize(data, serializer_cls)


def _deserialize(data, serializer_cls):
    kwargs = dict()
    fields_dict = attr.fields_dict(serializer_cls)
    data = [
        (to_snake_case(k), v) for k, v in data.items()
    ]
    data_stack = [
        (kwargs, k, fields_dict[k], v)
        for k, v in data if k in fields_dict and k != 'meta'
    ]
    while len(data_stack) > 0:
        parent, name, field, value = data_stack.pop()
        if value is None:
            parent[name] = None
            continue
        if type(field.type) is type:
            if attr.has(field.type):
                parent[name] = _deserialize(value, field.type)
            else:
                parent[name] = value
        elif field.type.__origin__ is list or field.type.__origin__ is typing.List:
            el_cls = field.type.__args__[0]
            if type(value) is not list:
                raise TypeError(
                    'keyword argument "%s" should be a list of %s' % (name, el_cls))
            if attr.has(el_cls):
                parent[name] = [
                    _deserialize(e, el_cls) for e in value
                ]
            else:
                parent[name] = value
        elif field.type.__origin__ is dict or field.type.__origin__ is typing.Dict:
            el_cls = field.type.__args__[1]
            if type(value) is not dict:
                raise TypeError(
                    'keyword argument "%s" should be a dict of %s' % (
                        name, el_cls)
                )
            if attr.has(el_cls):
                parent[name] = {
                    k: _deserialize(e, el_cls) for k, e in value.items()
                }
            else:
                parent[name] = value
        else:
            raise TypeError('unanticipated field type %s' % field.type)
    return serializer_cls(**kwargs)

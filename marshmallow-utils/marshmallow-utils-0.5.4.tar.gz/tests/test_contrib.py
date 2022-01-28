# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test the marshmallow contrib."""

import pytest
from marshmallow import Schema, ValidationError

from marshmallow_utils.fields import Function, Method


def serialize_foo(obj, context):
    return {'serialize_args': {'obj': 1, 'context': 2}}


def deserialize_foo(value, context, data):
    return {'deserialize_args': {
        'value': 3, 'context': 4, 'data': 5}}


class MySchema(Schema):
    f = Function(serialize_foo, deserialize_foo)


def test_contrib_function_field_dump():
    assert MySchema().dump({'f': 12123}) == {'f': {'serialize_args':
                                             {'context': 2, 'obj': 1}}}


def test_contrib_function_field_load():
    assert MySchema().load({'f': 12123}) == {'f': {'deserialize_args': {
                                            'value': 3, 'context': 4,
                                            'data': 5}}}


class BarSchema(Schema):
    bar = Method('serialize_bar', 'deserialize_bar')

    def serialize_bar(self, obj):
        return {'serialize_args': {'obj': 1}}

    def deserialize_bar(self, value, data):
        return {'deserialize_args': {'value': 23, 'data': 24}}


def test_contrib_method_field_dump():
    assert BarSchema().dump({'bar': 12123}) == {'bar': {'serialize_args':
                                                {'obj': 1}}}


def test_contrib_method_field_load():
    assert BarSchema().load({'bar': 12123}) == {'bar': {'deserialize_args':
                                                {'value': 23, 'data': 24}}}

# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test the marshmallow fields."""

from datetime import date, datetime

import pytest
from marshmallow import EXCLUDE, Schema, ValidationError, missing

from marshmallow_utils import fields


def test_trimmed():
    """Test trimmed string field."""
    class ASchema(Schema):
        f = fields.TrimmedString()

    assert ASchema().load({'f': '   '}) == {'f': ''}
    assert ASchema().load({'f': '  ad sf '}) == {'f': 'ad sf'}


def test_sanitized_unicode():
    """Test sanitized unicode field."""
    class ASchema(Schema):
        f = fields.SanitizedUnicode()

    assert ASchema().load({'f': ' \u200b\u000b\u001b\u0018 '}) == {'f': ''}


def test_sanitized_html():
    """Test sanitized html field."""
    class ASchema(Schema):
        f = fields.SanitizedHTML()

    assert ASchema().load({'f': 'an <script>evil()</script> example'}) == {
        'f': 'an evil() example'}

    # Ensure empty lists to tags/attrs removes all tags.
    class ASchema(Schema):
        f = fields.SanitizedHTML(tags=[], attrs=[])

    assert ASchema().load({'f': '<script>evil()</script><b>Hello</b>'}) == {
        'f': 'evil()Hello'}


def test_stripped_html():
    """Test stripped html field."""
    class ASchema(Schema):
        f = fields.StrippedHTML()

    assert ASchema().dump(
        {'f': 'an <div><span>evil()</span> example</div>'}) == {
        'f': 'an evil() example'}

    # Ensure already escaped HTML is returned unescaped.
    assert ASchema().dump(
        {'f': 'an <div>&lt;span&gt;example&lt;/span&gt;</div>'}) == {
        'f': 'an <span>example</span>'}

    # Unwanted unicode chars from HTML entities should also be removed.
    assert ASchema().dump(
        {'f': 'an &#8203;&quot;example&quot;'}) == {
        'f': 'an "example"'}


def test_isodate():
    """Test ISO date formatted string."""
    class ASchema(Schema):
        f = fields.ISODateString()

    assert ASchema().dump({'f': '1999-10-27'}) == {'f': '1999-10-27'}
    assert ASchema().dump({'f': 'invalid'}) == {}
    assert ASchema().dump({'f': None}) == {}
    assert ASchema().dump({'f': ''}) == {}

    assert ASchema().load({'f': '1999-10-27'}) == {'f': '1999-10-27'}
    pytest.raises(ValidationError, ASchema().load, {'f': 'invalid'})


def test_tzdatetime():
    """Test ISO date formatted string with timezone."""
    class ASchema(Schema):
        f = fields.TZDateTime()

    example_date = datetime(2017, 11, 28, 23, 55, 59, 342380)
    expected_date = '2017-11-28T23:55:59.342380+00:00'
    assert ASchema().dump({'f': example_date}) == {'f': expected_date}

    # Test serialization of None values
    assert ASchema().dump({'f': None}) == {'f': None}


def test_generated():
    """Test fields.generated fields."""

    def serialize_func(obj, ctx):
        return ctx.get('func-foo', obj.get('func-bar', missing))

    def deserialize_func(value, ctx, data):
        return ctx.get('func-foo', data.get('func-bar', missing))

    class GeneratedFieldsSchema(Schema):
        """Test schema."""
        class Meta:
            """Meta attributes for the schema."""

            unknown = EXCLUDE

        gen_function = fields.GenFunction(
            serialize=serialize_func,
            deserialize=deserialize_func,
        )

        gen_method = fields.GenMethod(
            serialize='_serialize_gen_method',
            deserialize='_deserialize_gen_method',
            missing='raises-warning',
        )

        def _serialize_gen_method(self, obj):
            # "meth-foo" from context or "meth-bar" from the object
            return self.context.get(
                'meth-foo', obj.get('meth-bar', missing))

        def _deserialize_gen_method(self, value, data):
            # "meth-foo" from context or "meth-bar" from the data
            return self.context.get(
                'meth-foo', data.get('meth-bar', missing))

    ctx = {
        'func-foo': 'ctx-func-value',
        'meth-foo': 'ctx-meth-value',
    }
    data = {
        'func-bar': 'data-func-value',
        'meth-bar': 'data-meth-value',
        'gen_function': 'original-func-value',
        'gen_method': 'original-meth-value',
    }

    # No context, no data
    assert GeneratedFieldsSchema().load({}) == {}
    assert GeneratedFieldsSchema().dump({}) == {}

    # Only context
    assert GeneratedFieldsSchema(context=ctx).load({}) == {
        'gen_function': 'ctx-func-value',
        'gen_method': 'ctx-meth-value',
    }
    assert GeneratedFieldsSchema(context=ctx).dump({}) == {
        'gen_function': 'ctx-func-value',
        'gen_method': 'ctx-meth-value',
    }

    # Only data
    assert GeneratedFieldsSchema().load(data) == {
        'gen_function': 'data-func-value',
        'gen_method': 'data-meth-value',
    }
    assert GeneratedFieldsSchema().dump(data) == {
        'gen_function': 'data-func-value',
        'gen_method': 'data-meth-value',
    }

    # Context and data
    assert GeneratedFieldsSchema(context=ctx).load(data) == {
        'gen_function': 'ctx-func-value',
        'gen_method': 'ctx-meth-value',
    }
    assert GeneratedFieldsSchema(context=ctx).dump(data) == {
        'gen_function': 'ctx-func-value',
        'gen_method': 'ctx-meth-value',
    }

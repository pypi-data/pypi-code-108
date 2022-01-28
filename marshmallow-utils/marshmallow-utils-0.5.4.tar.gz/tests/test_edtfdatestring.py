# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test the localization of EDTF string."""

import pytest
from marshmallow import Schema, ValidationError

from marshmallow_utils.fields import EDTFDateString


class TestSchema(Schema):
    date = EDTFDateString()


def test_dump():
    assert TestSchema().dump({'date': '2020-09/2020-10'}) == {
        'date': '2020-09/2020-10',
    }


def test_load():
    s = TestSchema()
    assert s.load({'date': '2020-09/2020-10'})
    # Invalid
    pytest.raises(ValidationError, s.load, {'date': '2020-09-21garbage'})
    # Not chronological
    pytest.raises(ValidationError, s.load, {'date': '2021/2020'})
    # Not date or interval
    pytest.raises(ValidationError, s.load, {'date': '2020-01-01T10:00:00'})

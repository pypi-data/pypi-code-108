# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for marshmallow GeoJSON MultiPoint schema."""

import pytest
from marshmallow import ValidationError

from marshmallow_utils.schemas import MultiPointSchema


@pytest.mark.parametrize("coordinates", [
    ([[-32.94682, -60.63932], [-32.94682, -60.63932, 10.0]]),
    ([[-32.99, -60.63], [-32.94, -60.63], [-32.92, -60.32, 10.0]]),
])
def test_multipoint(coordinates):
    valid_full = {
        "type": "MultiPoint",
        "coordinates": coordinates
    }
    loaded = MultiPointSchema().load(valid_full)
    # NOTE: Since the schemas return the dict itself, the loaded object
    # is the same than the input and dumped objects (dicts)
    assert valid_full == loaded == MultiPointSchema().dump(loaded)


@pytest.mark.parametrize("coordinates", [
    ("-32.94682,-60.63932, -32.94682, -60.63932, 10.0"),
    (["-32.94682,-60.63932", "-32.94682, -60.63932, 10.0"]),
    ([-32.94682, -60.63932, 10.0, 10.0]),
    ([[-32.99, -60.63], [-32.94], [-32.92, -60.32, 10.0]])
])
def test_multipoint_fail(coordinates):
    invalid_point = {
        "type": "MultiPoint",
        "coordinates": coordinates
    }
    pytest.raises(ValidationError, MultiPointSchema().load, invalid_point)

# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for marshmallow GeoJSON Polygon schema."""

import pytest
from marshmallow import ValidationError

from marshmallow_utils.schemas import PolygonSchema


@pytest.mark.parametrize("coordinates", [
    ([[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]]]),
])
def test_polygon(coordinates):
    print(coordinates)
    valid_full = {
        "type": "Polygon",
        "coordinates": coordinates
    }

    loaded = PolygonSchema().load(valid_full)
    # NOTE: Since the schemas return the dict itself, the loaded object
    # is the same than the input and dumped objects (dicts)
    assert valid_full == loaded == PolygonSchema().dump(loaded)


@pytest.mark.parametrize("coordinates", [
    ([2.38, 57.322, -120.43, 19.15]),
    ([[2.38, 57.322], [-120.43, 19.15]]),
    ([[[2.38, 57.322], [23.194, -20.28], [24.194, -19.2]]]),
    ([[[2.38, 57.322], [2.38, 57.322]]]),
    ([[[2.38, 57.322], [23.194, -20.28], [2.38, 57.322]]]),
])
def test_polygon_fail(coordinates):
    invalid_point = {
        "type": "Polygon",
        "coordinates": coordinates
    }
    pytest.raises(ValidationError, PolygonSchema().load, invalid_point)

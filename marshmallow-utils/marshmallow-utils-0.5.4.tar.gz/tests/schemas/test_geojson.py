# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for marshmallow GeoJSON schema."""

import pytest
from marshmallow import ValidationError

from marshmallow_utils.schemas import GeometryObjectSchema


def test_point():
    valid_full = {
        "type": "Point",
        "coordinates": [-32.94682, -60.63932]
    }

    point = GeometryObjectSchema().load(valid_full)
    assert valid_full == point == GeometryObjectSchema().dump(point)


def test_point_fail():
    invalid_input = {
        "type": "Point",
        "coordinates": [-32.94682]
    }
    pytest.raises(ValidationError, GeometryObjectSchema().load, invalid_input)


def test_multipoint():
    valid_full = {
        "type": "MultiPoint",
        "coordinates": [[-32.94682, -60.63932], [-32.94682, -60.63932, 10.0]]
    }

    multipoint = GeometryObjectSchema().load(valid_full)
    assert valid_full == multipoint == GeometryObjectSchema().dump(multipoint)


def test_multipoint_fail():
    invalid_input = {
        "type": "MultiPoint",
        "coordinates": [-32.94682, -60.63932]
    }
    pytest.raises(ValidationError, GeometryObjectSchema().load, invalid_input)


def test_polygon():
    valid_full = {
        "type": "Polygon",
        "coordinates": [[
            [2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]
        ]]
    }

    polygon = GeometryObjectSchema().load(valid_full)
    assert valid_full == polygon == GeometryObjectSchema().dump(polygon)


def test_polygon_fail():
    invalid_input = {
        "type": "Polygon",
        "coordinates": [[[2.38, 57.322], [23.194, -20.28], [2.38, 57.322]]]
    }
    pytest.raises(ValidationError, GeometryObjectSchema().load, invalid_input)


@pytest.mark.parametrize("geotype", [("Point"), ("MultiPoint")])
def test_point_no_coordinates_fail(geotype):
    invalid_point = {"type": geotype}

    pytest.raises(ValidationError, GeometryObjectSchema().load, invalid_point)


def test_not_supported_type_fail():
    invalid_type = {"type": "invalid"}

    pytest.raises(ValidationError, GeometryObjectSchema().load, invalid_type)


def test_no_type_fail():
    invalid_no_type = {
        "coordinates": [-32.94682, -60.63932]
    }

    pytest.raises(
        ValidationError, GeometryObjectSchema().load, invalid_no_type)

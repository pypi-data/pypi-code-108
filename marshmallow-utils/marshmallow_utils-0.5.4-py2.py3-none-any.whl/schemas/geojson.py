# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""GeoJSON Schema."""

from geojson import MultiPoint, Point, Polygon
from marshmallow import Schema, ValidationError
from marshmallow.fields import Constant, Float, List
from marshmallow.validate import Validator
from marshmallow_oneofschema import OneOfSchema


class GeometryValidator(Validator):
    """Validator for GeoJSON geometry objects."""

    def __init__(self, geometry_cls):
        """Initialize the validator.

        :param geometry_cls: The GeoJSON geometry class to validate against.
        """
        self.geometry_cls = geometry_cls

    def __call__(self, value):
        """Validate a geometry object."""
        obj = self.geometry_cls(value)
        if not obj.is_valid:
            errors = obj.errors()
            raise ValidationError({"geojson": {"coordinates": errors}})
        return value


class PointSchema(Schema):
    """GeoJSON Point schema.

    See https://tools.ietf.org/html/rfc7946#section-3.1.2
    """

    coordinates = List(Float, required=True, validate=GeometryValidator(Point))
    type = Constant('Point')


class MultiPointSchema(Schema):
    """GeoJSON MultiPoint schema.

    See https://tools.ietf.org/html/rfc7946#section-3.1.3
    """

    coordinates = List(
        List(Float), required=True, validate=GeometryValidator(MultiPoint))
    type = Constant('MultiPoint')


class PolygonSchema(Schema):
    """GeoJSON Polygon schema.

    See https://tools.ietf.org/html/rfc7946#section-3.1.6
    """

    coordinates = List(
        List(List(Float)), required=True, validate=GeometryValidator(Polygon))
    type = Constant('Polygon')


class GeometryObjectSchema(OneOfSchema):
    """A GeoJSON Geometry Object schema.

    See https://tools.ietf.org/html/rfc7946#section-3.1

    Only Point, MultiPoint and Polygon are supported.
    """

    type_schemas = {
        "Point": PointSchema,
        "MultiPoint": MultiPointSchema,
        "Polygon": PolygonSchema,
    }

    def get_obj_type(self, obj):
        """Finds the object type in the dictionary.

        This function is needed because the schemas return the dict itself.
        Not a geojson object.
        """
        obj_type = obj.get("type")
        if not obj_type or obj_type not in self.type_schemas.keys():
            raise Exception(f"Unknown GeoJSON object type: {obj_type}")

        return obj_type

# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Marshmallow schemas."""

from .geojson import GeometryObjectSchema, MultiPointSchema, PointSchema, \
    PolygonSchema
from .identifier import IdentifierSchema

__all__ = (
    'GeometryObjectSchema',
    'IdentifierSchema',
    'MultiPointSchema',
    'PointSchema',
    'PolygonSchema',
)

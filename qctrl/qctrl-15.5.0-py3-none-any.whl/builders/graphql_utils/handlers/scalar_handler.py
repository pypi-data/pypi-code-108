# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#     https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
# pylint:disable=missing-module-docstring,too-many-ancestors
import json

from .base import BaseHandler
from .mixins import ScalarMixin


class FloatScalarHandler(ScalarMixin, BaseHandler):
    """Handler for GraphQL Float scalar type."""

    _scalar_name = "Float"
    _scalar_encoder = str
    _scalar_allowed_type = [float, int]
    scalar_type_hint = float


class IntScalarHandler(ScalarMixin, BaseHandler):
    """Handler for GraphQL Int scalar type."""

    _scalar_name = "Int"
    _scalar_encoder = str
    _scalar_allowed_type = int
    scalar_type_hint = int


class BooleanScalarHandler(ScalarMixin, BaseHandler):
    """Handler for GraphQL Boolean scalar type."""

    _scalar_name = "Boolean"
    _scalar_encoder = json.dumps
    _scalar_allowed_type = bool
    scalar_type_hint = bool


class StringScalarHandler(ScalarMixin, BaseHandler):
    """Handler for GraphQL String scalar type."""

    _scalar_name = "String"
    _scalar_encoder = json.dumps
    _scalar_allowed_type = str
    scalar_type_hint = str


class IDScalarHandler(ScalarMixin, BaseHandler):
    """Handler for GraphQL ID scalar type."""

    _scalar_name = "ID"
    _scalar_encoder = json.dumps
    _scalar_allowed_type = str
    scalar_type_hint = str

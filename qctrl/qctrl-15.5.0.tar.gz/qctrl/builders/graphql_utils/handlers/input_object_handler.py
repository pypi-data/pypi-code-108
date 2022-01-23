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
# pylint:disable=missing-module-docstring
from typing import (
    Any,
    Dict,
)

from graphql import GraphQLInputObjectType

from qctrl.utils import abstract_property

from .base import BaseHandler
from .mixins import PayloadMixin


class InputObjectHandler(BaseHandler, PayloadMixin):
    """Handler for GraphQLInputObject types."""

    _field_type = GraphQLInputObjectType

    def _format_payload(self, field_type, data):
        values = {}

        for field_name, field in field_type.fields.items():
            nested_value = self._env.get_nested_value(data, field_name)

            if nested_value is not None:
                values[field_name] = self._env.format_payload(field.type, nested_value)

        return self._env.format_query_payload_dict(values)


class NamedInputObjectHandler(InputObjectHandler):
    """Handler for overriding specific GraphQLInputObject
    types by name.
    """

    _input_object_name = None

    @abstract_property
    def input_object_name(self):  # pylint:disable=missing-function-docstring
        return self._input_object_name

    def get_input_object_values(self, data: Any) -> Dict[str, Any]:
        """Given some object, return a dictionary
        of the required fields and their values.
        """
        raise NotImplementedError

    def _format_payload(self, field_type, data):
        values = self.get_input_object_values(data)

        for field_name, value in values.items():
            try:
                field = field_type.fields[field_name]
            except KeyError as error:
                raise KeyError(f"unknown field: {field_name}") from error

            values[field_name] = self._env.format_payload(field.type, value)

        return self._env.format_query_payload_dict(values)

    def can_handle_format_payload(self, field_type):
        return (
            super().can_handle_format_payload(field_type)
            and field_type.name  # pylint:disable=comparison-with-callable
            == self.input_object_name
        )

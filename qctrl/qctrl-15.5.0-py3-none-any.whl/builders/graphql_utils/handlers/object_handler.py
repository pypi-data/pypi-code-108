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
import logging
from typing import (
    Any,
    Dict,
    Optional,
)

from graphql import (
    GraphQLObjectType,
    GraphQLType,
    is_object_type,
)

from qctrl.utils import abstract_property

from .base import BaseHandler
from .mixins import (
    DataMixin,
    SelectionMixin,
)

LOGGER = logging.getLogger(__name__)


class ObjectHandler(BaseHandler, SelectionMixin, DataMixin):
    """Handler for GraphQLObject types."""

    _field_type = GraphQLObjectType

    def _get_selection(self, field_type, overrides=None):
        fields = []

        for field_name, field in field_type.fields.items():

            nested_overrides = self._env.get_nested_selection_override(
                overrides, field_name
            )

            if isinstance(nested_overrides, str):
                nested_fields = nested_overrides
            else:
                nested_fields = self._env.get_selection(field.type, nested_overrides)

            if nested_fields:
                fields.append(f"{field_name} {nested_fields}")
            else:
                fields.append(field_name)

        return self._env.format_query_selection_fields(fields)

    def load_data(self, field_type: GraphQLType, data: Optional[Dict[str, Any]]) -> Any:
        """Public method for loading the given data according to
        the field type. If the data is None, no formatting is
        performed.
        """
        if data is None and not is_object_type(field_type):
            return data

        return self._load_data(field_type, data)

    def _get_nested_data(self, field_name: str, data: Dict[str, Any]):
        if field_name in data:
            return data[field_name]
        if self._env.field_to_attr(field_name) in data:
            return data[self._env.field_to_attr(field_name)]
        return None

    def _load_data(self, field_type, data):
        cls = self._env.type_registry.get_type(field_type.name)
        kwargs = {}

        for field_name, field in field_type.fields.items():

            if data is not None:
                nested_data = self._get_nested_data(field_name, data)
                if nested_data is None:
                    continue
            else:
                nested_data = None

            nested_value = self._env.load_data(field.type, nested_data)

            if nested_value is not None:
                kwargs[self._env.field_to_attr(field_name)] = nested_value

        return cls(**kwargs)

    def _update_data(self, field_type, obj, data):

        for field_name, field in field_type.fields.items():

            nested_data = self._get_nested_data(field_name, data)

            if nested_data is None:
                continue

            attr = self._env.field_to_attr(field_name)

            current_attr_value = getattr(obj, attr, None)
            if current_attr_value:
                nested_value = self._env.update_data(
                    field.type, current_attr_value, nested_data
                )
            else:
                nested_value = self._env.load_data(field.type, nested_data)

            if nested_value is not None:
                setattr(obj, attr, nested_value)

        return obj


class NamedObjectHandler(ObjectHandler):
    """Handler for overriding specific GraphQLObject types
    by name.
    """

    _object_name = None

    @abstract_property
    def object_name(self):  # pylint:disable=missing-function-docstring
        return self._object_name

    def can_handle_get_selection(self, field_type):
        return (
            super().can_handle_get_selection(field_type)
            and field_type.name  # pylint:disable=comparison-with-callable
            == self.object_name
        )

    def can_handle_data(self, field_type):
        return (
            super().can_handle_data(field_type)
            and field_type.name  # pylint:disable=comparison-with-callable
            == self.object_name
        )

    def process_loaded_data(  # pylint:disable=no-self-use
        self, data: Dict[str, Any]
    ) -> Any:
        """Override to perform any custom processing on
        loaded data. The data provided will be a dictionary
        of each sub field and its value. By default, no
        processing is done on the data.
        """
        return data

    def load_data(self, field_type: GraphQLType, data: Optional[Dict[str, Any]]) -> Any:
        """Public method for loading the given data according to
        the field type. If the data is None, no formatting is
        performed.
        """
        if data is None:
            return data

        return self._load_data(field_type, data)

    def _load_data(self, field_type, data) -> dict:

        result = {}

        for field_name, field in field_type.fields.items():

            try:
                nested_data = data[field_name]
            except KeyError:
                continue

            nested_value = self._env.load_data(field.type, nested_data)

            if nested_value is not None:
                result[field_name] = nested_value

        return self.process_loaded_data(result)

    def _update_data(self, field_type, obj, data):
        return self.load_data(field_type, data)

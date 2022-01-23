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
from functools import lru_cache
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Union,
)

from graphql import GraphQLType

from .base_type_registry import BaseTypeRegistry
from .handlers import (
    BooleanScalarHandler,
    EnumHandler,
    FloatScalarHandler,
    IDScalarHandler,
    InputObjectHandler,
    IntScalarHandler,
    ListHandler,
    NonNullHandler,
    ObjectHandler,
    StringScalarHandler,
    UnionHandler,
)
from .handlers.base import BaseHandler
from .handlers.mixins import (
    DataMixin,
    PayloadMixin,
    SelectionMixin,
)

LOGGER = logging.getLogger(__name__)


class GraphQLEnvironment:
    """Defines an environment for using GraphQL
    type handlers.
    """

    _fallback_handlers = [
        NonNullHandler,
        FloatScalarHandler,
        IntScalarHandler,
        IDScalarHandler,
        BooleanScalarHandler,
        StringScalarHandler,
        ListHandler,
        InputObjectHandler,
        UnionHandler,
        ObjectHandler,
        EnumHandler,
    ]

    def __init__(
        self,
        type_registry_cls: BaseTypeRegistry = None,
        custom_handlers: List[BaseHandler] = None,
    ):
        self._type_registry = None

        if type_registry_cls:
            self._type_registry = type_registry_cls(self)

        custom_handlers = custom_handlers or []
        self._handlers = []

        for cls in custom_handlers + self._fallback_handlers:

            if not issubclass(cls, BaseHandler):
                raise TypeError(f"invalid handler class: {cls}")

            self._handlers.append(cls(self))

    @property
    def type_registry(self):  # pylint:disable=missing-function-docstring
        if self._type_registry is None:
            raise RuntimeError("No type registry defined")

        return self._type_registry

    def field_to_attr(self, field_name: str) -> str:  # pylint:disable=no-self-use
        """Converts a GraphQL field name into the
        corresponding attribute name if using objects
        when loading or updating data. By default, the
        attribute name is the same as the field name.
        """
        return field_name

    @lru_cache()
    def get_handler(self, base: type, field_type: GraphQLType) -> BaseHandler:
        """
        Finds the correct handler for the field_type based on the base class
        provided.
        """
        for handler in self._handlers:
            if base.can_handle(handler, field_type):
                LOGGER.debug("using handler: %s", handler)
                return handler

        raise TypeError(f"unhandled type: {type(field_type)} ({field_type})")

    def iter_handlers(self, base: type) -> Iterator:
        """Iterates through the configured handlers
        that are instances of the base class provided.
        """
        for handler in self._handlers:
            if isinstance(handler, base):
                yield handler

    def format_payload(self, field_type: GraphQLType, data: Any) -> str:
        """Formats the given payload data for use in a query
        or mutation request.
        """
        LOGGER.debug("format_payload: %s, %s", field_type, data)

        handler = self.get_handler(PayloadMixin, field_type)
        return handler.format_payload(field_type, data)

    def get_selection(
        self, field_type: GraphQLType, overrides: Optional[Dict[str, str]] = None
    ) -> str:
        """Returns the selection query string for the given field type.
        By default, all nested fields will be included. Overrides can be
        provided to restrict which nested fields are selected.
        """
        LOGGER.debug("get_selection: %s", field_type)

        handler = self.get_handler(SelectionMixin, field_type)
        return handler.get_selection(field_type, overrides)

    def load_data(self, field_type: GraphQLType, data: Any) -> Any:
        """Loads the data from a GraphQL response into objects using
        the type registry.
        """
        LOGGER.debug("load_data: %s", field_type)

        handler = self.get_handler(DataMixin, field_type)
        return handler.load_data(field_type, data)

    def update_data(self, field_type: GraphQLType, obj: Any, data: Any) -> Any:
        """Updates an existing object (from the type registry) with
        response data.
        """
        LOGGER.debug("update_data: %s", field_type)

        handler = self.get_handler(DataMixin, field_type)
        return handler.update_data(field_type, obj, data)

    @staticmethod
    def get_nested_selection_override(
        overrides: Optional[Dict[str, str]], field_name: str
    ) -> Optional[Union[str, Dict[str, str]]]:
        """
        Returns the nested selection override for the
        given field name, if any.
        """
        result = None

        if isinstance(overrides, dict):
            try:
                result = overrides[field_name]
            except KeyError:
                pass

        return result

    def get_nested_value(self, obj: Any, field_name: str) -> Any:
        """Returns the nested value from the object
        for the given field name.
        """
        attr_name = self.field_to_attr(field_name)

        if isinstance(obj, dict):
            if field_name in obj:
                return obj[field_name]

            if attr_name in obj:
                return obj[attr_name]

        return getattr(obj, attr_name, None)

    @staticmethod
    def format_query_payload_dict(data: Dict[str, Any]) -> str:
        """Formats a key-value dictionary for a query."""

        values = [f"{key} : {value}" for key, value in data.items()]
        string_values = " ".join(values)

        return f"{{ {string_values} }}"

    @staticmethod
    def format_query_selection_fields(fields: List[str]) -> str:
        """Formats a list of values for a query."""
        # e.g '{ modelId name status errors progress }'
        string_fields = " ".join(fields)
        return f"{{ {string_fields} }}"

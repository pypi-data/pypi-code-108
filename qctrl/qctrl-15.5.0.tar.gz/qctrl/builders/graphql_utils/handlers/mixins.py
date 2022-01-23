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
from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
    Dict,
    Optional,
)

from graphql import (
    GraphQLScalarType,
    GraphQLType,
)

from qctrl.utils import abstract_property


class BaseHandlerMixin(ABC):
    """
    Base Handler mixing for query or mutation types.
    """

    @staticmethod
    @abstractmethod
    def _can_handle(handler, field_type: GraphQLType) -> bool:
        """
        Private static method to be overridden by the mixin definition class.
        """

        raise NotImplementedError

    @classmethod
    def can_handle(cls, handler, field_type: GraphQLType) -> bool:
        """
        Checks if the handler is allowed for the given field type using static
        methods to allow dynamic checking.
        """

        return isinstance(handler, cls) and cls._can_handle(handler, field_type)


class PayloadMixin(BaseHandlerMixin):
    """Handler mixin for types that format a payload to
    be sent as a query/mutation request.
    """

    def can_handle_format_payload(self, field_type: GraphQLType) -> bool:
        """Checks if the handler is allowed for the given
        field type.
        """
        return self._is_expected_type(field_type)

    def format_payload(self, field_type: GraphQLType, data: Any) -> str:
        """Public method for formatting the given payload
        data for use in the query/mutation.
        """
        return self._format_payload(field_type, data)

    @abstractmethod
    def _format_payload(self, field_type: GraphQLType, data: Any) -> str:
        """Private method to be overridden for formatting
        the payload data.
        """
        raise NotImplementedError

    @staticmethod
    def _can_handle(handler, field_type: GraphQLType) -> bool:
        return handler.can_handle_format_payload(field_type)


class SelectionMixin(BaseHandlerMixin):
    """Handler mixin for types that are used for the selection
    part of a query or mutation selection.
    """

    def can_handle_get_selection(self, field_type: GraphQLType) -> bool:
        """Checks if the handler is allowed for the given
        field type.
        """
        return self._is_expected_type(field_type)

    def get_selection(
        self, field_type: GraphQLType, overrides: Optional[Dict[str, str]] = None
    ) -> str:
        """Public method for returning the selection query
        for the given field type. By default, all nested fields
        will be included. Overrides can be provided to restrict
        which nested fields are selected.
        """
        return self._get_selection(field_type, overrides)

    @abstractmethod
    def _get_selection(
        self, field_type: GraphQLType, overrides: Optional[Dict[str, str]]
    ) -> str:
        """Private method to be overridden for returning the
        query selection.
        """
        raise NotImplementedError

    @staticmethod
    def _can_handle(handler, field_type: GraphQLType) -> bool:
        return handler.can_handle_get_selection(field_type)


class DataMixin(BaseHandlerMixin):
    """Handler mixin for types that consume data returned by a
    query or mutation.
    """

    def can_handle_data(self, field_type: GraphQLType) -> bool:
        """Checks if the handler is allowed for the given
        field type.
        """
        return self._is_expected_type(field_type)

    def load_data(self, field_type: GraphQLType, data: Optional[Dict[str, Any]]) -> Any:
        """Public method for loading the given data according to
        the field type. If the data is None, no formatting is
        performed.
        """
        if data is None:
            return data

        return self._load_data(field_type, data)

    @abstractmethod
    def _load_data(self, field_type: GraphQLType, data: Dict[str, Any]) -> Any:
        """Private method to be overridden for loading the data."""
        raise NotImplementedError

    @staticmethod
    def _can_handle(handler, field_type: GraphQLType) -> bool:
        return handler.can_handle_data(field_type)

    def update_data(
        self, field_type: GraphQLType, obj: Any, data: Optional[Dict[str, Any]]
    ) -> Any:
        """Public method for updating an object with the given
        data according to the field type. If the data is None,
        no formatting is performed.
        """
        if data is None:
            return data

        return self._update_data(field_type, obj, data)

    @abstractmethod
    def _update_data(
        self, field_type: GraphQLType, obj: Any, data: Dict[str, Any]
    ) -> Any:
        """Private method to be overridden for updating the object
        with the data.
        """
        raise NotImplementedError


class ScalarMixin(PayloadMixin, SelectionMixin, DataMixin):
    """Handler mixin for all GraphQLScalar types."""

    _field_type = GraphQLScalarType
    _scalar_name = None
    _scalar_encoder = None
    _scalar_decoder = None
    _scalar_allowed_type = None
    scalar_type_hint = None

    @abstract_property
    def scalar_name(self):  # pylint:disable=missing-function-docstring
        return self._scalar_name

    @abstract_property
    def scalar_encoder(self):  # pylint:disable=missing-function-docstring
        return self.__class__._scalar_encoder  # pylint:disable=protected-access

    @property
    def scalar_decoder(self):  # pylint:disable=missing-function-docstring
        return self.__class__._scalar_decoder  # pylint:disable=protected-access

    @abstract_property
    def scalar_allowed_type(self):  # pylint:disable=missing-function-docstring
        return self._scalar_allowed_type

    def _is_expected_scalar_name(self, field_type: GraphQLType) -> bool:
        """Checks if field type name is expected
        for this handler.
        """
        return (
            field_type.name  # pylint:disable=comparison-with-callable
            == self.scalar_name
        )

    def _check_type(self, data: Any) -> bool:
        """Checks that the data type is expected."""
        allowed = self.scalar_allowed_type

        if not isinstance(allowed, list):
            allowed = [allowed]

        # pylint: disable=isinstance-second-argument-not-valid-type
        if not any(isinstance(data, _type) for _type in allowed):
            raise TypeError(
                f"scalar {self.scalar_name} expected object of "
                f"type: {self.scalar_allowed_type}; got {type(data)} ({data})"
            )

    # overridden methods

    def can_handle_format_payload(self, field_type):
        return super().can_handle_format_payload(
            field_type
        ) and self._is_expected_scalar_name(field_type)

    def _format_payload(self, field_type, data):
        self._check_type(data)
        return self.scalar_encoder(data)  # pylint:disable=too-many-function-args

    def can_handle_get_selection(self, field_type):
        return super().can_handle_get_selection(
            field_type
        ) and self._is_expected_scalar_name(field_type)

    def _get_selection(self, field_type, overrides=None):
        return None

    def can_handle_data(self, field_type):
        return super().can_handle_data(field_type) and self._is_expected_scalar_name(
            field_type
        )

    def _load_data(self, field_type, data):
        if self.scalar_decoder:
            data = self.scalar_decoder(data)  # pylint:disable=not-callable

        self._check_type(data)
        return data

    def _update_data(self, field_type, obj, data):
        # refresh query data is already decoded, so we can return the data directly.
        self._check_type(data)
        return data

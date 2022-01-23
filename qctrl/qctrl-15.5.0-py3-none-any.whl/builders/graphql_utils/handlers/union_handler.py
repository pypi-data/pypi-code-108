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

from graphql import (
    GraphQLType,
    GraphQLUnionType,
)

from .base import BaseHandler
from .mixins import (
    DataMixin,
    SelectionMixin,
)


def _get_union_type_by_name(
    union_type: GraphQLUnionType, type_name: str
) -> GraphQLType:
    """
    Returns the type from a union by the name.

    Parameters
    ----------
    union_type: GraphQLUnionType
        A graphql union.
    type_name: str
        The name of the expected type to return.

    Raises
    ------
    TypeError
        When no type is found with the provided name.

    Returns
    -------
    GraphQLType
        The sub type from the union that matches the type name.
    """

    for sub_type in union_type.types:
        if sub_type.name == type_name:
            return sub_type

    raise TypeError(f"unhandled type {type_name} by {type(union_type)}")


class UnionHandler(
    BaseHandler,
    SelectionMixin,
    DataMixin,
):
    """
    Handler for GraphQLUnionType types.
    """

    _field_type = GraphQLUnionType

    def _get_selection(self, field_type, overrides=None):
        fields = ["__typename"]

        for field in field_type.types:
            nested_fields = self._env.get_selection(field)
            fields.append(f"... on {field.name} {nested_fields}")

        return self._env.format_query_selection_fields(fields)

    def _load_data(self, field_type, data):
        type_name = None

        if "__typename" not in data:
            type_name = self._find_type(field_type.name, data)
        else:
            type_name = data.pop("__typename")

        if type_name is None:
            raise TypeError(f"unresolved union type for field {field_type.name}")

        union_type = _get_union_type_by_name(field_type, type_name)
        return self._env.load_data(union_type, data)

    @staticmethod
    def _find_type(field_type: str, data: Dict[str, Any]):
        if field_type == "ComplexArray":
            if "dense_entries" in data:
                return "ComplexDenseArray"

            if "sparse_entries" in data:
                return "ComplexSparseArray"

        return None

    def _update_data(self, field_type, obj, data):
        union_type = _get_union_type_by_name(field_type, obj.__class__.__name__)
        return self._env.update_data(union_type, obj, data)

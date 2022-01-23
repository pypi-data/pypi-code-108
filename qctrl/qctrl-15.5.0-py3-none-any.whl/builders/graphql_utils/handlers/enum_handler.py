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
from enum import Enum

from graphql import GraphQLEnumType

from .base import BaseHandler
from .mixins import (
    DataMixin,
    PayloadMixin,
)


class EnumHandler(BaseHandler, DataMixin, PayloadMixin):
    """Handler for GraphQLEnum types."""

    _field_type = GraphQLEnumType

    @staticmethod
    def _check_valid_value(field_type, data):
        if data not in field_type.values:
            raise ValueError(f"invalid enum value: {data}")

    def _load_data(self, field_type, data):
        self._check_valid_value(field_type, data)
        return data

    def _update_data(self, field_type, obj, data):
        self._check_valid_value(field_type, data)
        return data

    def _format_payload(self, field_type, data) -> str:
        # Accept either string or enum data.
        if isinstance(data, str):
            value = data
        elif isinstance(data, Enum):
            value = data.name
        else:
            raise ValueError(f"invalid enum value: {data}")

        return value

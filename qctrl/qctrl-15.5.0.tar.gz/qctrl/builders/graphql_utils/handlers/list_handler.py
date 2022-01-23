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
import numpy as np
from graphql import GraphQLList

from .base import BaseHandler
from .mixins import (
    DataMixin,
    PayloadMixin,
    SelectionMixin,
)


class ListHandler(BaseHandler, PayloadMixin, SelectionMixin, DataMixin):
    """Handler for GraphQLList types."""

    _field_type = GraphQLList

    def _format_payload(self, field_type, data):
        if not isinstance(data, (list, tuple, np.ndarray)):
            raise TypeError(
                f"{data} is of type {type(data)}, but expected a list, tuple, or array instead."
            )

        result = []

        for nested_data in data:
            result.append(self._env.format_payload(field_type.of_type, nested_data))

        return f"[ {', '.join(result)} ]"

    def _get_selection(self, field_type, overrides=None):
        return self._env.get_selection(field_type.of_type)

    def _load_data(self, field_type, data):
        result = []

        for nested_data in data:
            result.append(self._env.load_data(field_type.of_type, nested_data))

        return result

    def _update_data(self, field_type, obj, data):
        return self.load_data(field_type, data)

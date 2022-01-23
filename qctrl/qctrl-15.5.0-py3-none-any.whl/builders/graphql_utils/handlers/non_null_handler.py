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
from graphql import GraphQLNonNull

from .base import BaseHandler
from .mixins import (
    DataMixin,
    PayloadMixin,
    SelectionMixin,
)


class NonNullHandler(BaseHandler, PayloadMixin, SelectionMixin, DataMixin):
    """Handler for GraphQLNonNull types."""

    _field_type = GraphQLNonNull

    def _format_payload(self, field_type, data):
        result = self._env.format_payload(field_type.of_type, data)

        if result is None:
            # IMPROVEMENT: catch this error and include field
            # name in error message
            raise ValueError("non-null value expected")

        return result

    def _get_selection(self, field_type, overrides=None):
        return self._env.get_selection(field_type.of_type, overrides)

    def _load_data(self, field_type, data):
        return self._env.load_data(field_type.of_type, data)

    def _update_data(self, field_type, obj, data):
        return self._env.update_data(field_type.of_type, obj, data)

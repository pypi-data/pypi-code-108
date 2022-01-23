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
from abc import ABC

from graphql import GraphQLType

from qctrl.utils import abstract_property


class BaseHandler(ABC):  # pylint:disable=too-few-public-methods
    """Base class for a GraphQL type handler."""

    _field_type = None

    def __init__(self, env: "GraphQLEnvironment"):
        self._env = env

    @abstract_property
    def field_type(self):  # pylint:disable=missing-function-docstring
        return self._field_type

    def _is_expected_type(
        self,
        field_type: GraphQLType,
    ) -> bool:
        """Checks if the given field type is of
        the expected type.
        """
        return isinstance(  # pylint:disable=isinstance-second-argument-not-valid-type
            field_type,
            self.field_type,
        )

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

import numpy as np
from graphql import GraphQLType
from inflection import underscore
from qctrlcommons.serializers import read_numpy_array

from qctrl.builders.graphql_utils.handlers import NamedObjectHandler
from qctrl.builders.type_registry import TypeOverrideMixin


class ComplexArrayHandler(
    NamedObjectHandler, TypeOverrideMixin
):  # pylint:disable=too-many-ancestors
    """
    Custom handler for ComplexArray.
    """

    _type_hint = np.ndarray
    _object_name = "ComplexArray"

    def process_loaded_data(self, data: Dict[str, Any]) -> np.ndarray:
        return read_numpy_array(
            **{underscore(key): value for key, value in data.items()}
        )

    def _load_data(self, field_type: GraphQLType, data: Dict[str, Any]) -> Any:
        return self.process_loaded_data(data)


class ComplexDenseArrayHandler(
    ComplexArrayHandler
):  # pylint:disable=too-many-ancestors
    """
    Custom handler for ComplexDenseArray.
    """

    _object_name = "ComplexDenseArray"


class ComplexSparseArrayHandler(
    ComplexArrayHandler
):  # pylint:disable=too-many-ancestors
    """
    Custom handler for ComplexSparseArray.
    """

    _object_name = "ComplexSparseArray"

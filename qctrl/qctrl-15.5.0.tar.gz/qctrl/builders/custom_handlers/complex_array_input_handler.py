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
# pylint:disable=missing-module-docstring,too-many-ancestors
from typing import (
    Any,
    Dict,
)

import inflection
import numpy as np
from qctrlcommons.serializers import write_numpy_array

from qctrl.builders.graphql_utils.handlers import NamedInputObjectHandler
from qctrl.builders.type_registry import TypeOverrideMixin


class ComplexArrayInputHandler(NamedInputObjectHandler, TypeOverrideMixin):
    """Custom handler for ComplexArrayInput."""

    _type_hint = np.ndarray
    _input_object_name = "ComplexArrayInput"

    def get_input_object_values(self, data: Dict[str, Any]):
        serialized_data = write_numpy_array(data)
        return {
            inflection.camelize(key, False): value
            for key, value in serialized_data.items()
        }

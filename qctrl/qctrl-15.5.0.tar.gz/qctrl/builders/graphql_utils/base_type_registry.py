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


class BaseTypeRegistry(ABC):  # pylint:disable=too-few-public-methods
    """Base class for a type registry which can be used
    for loading and updating data from a GraphQL response
    into objects.
    """

    def __init__(self, env: "GraphQLEnvironment"):
        self.env = env

    @abstractmethod
    def get_type(self, type_name: str) -> type:
        """Returns the corresponding class for the
        GraphQL field type name. To be overridden by
        the subclass.
        """
        raise NotImplementedError

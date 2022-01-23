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
from typing import Union

from gql import gql

from .base import StaticQuery

LOGGER = logging.getLogger(__name__)


class GetMutationNameQuery(StaticQuery):  # pylint:disable=too-few-public-methods
    """This class is used to retrieve the results of a previously run `function`.
    If the function is still running it will wait until it's finished
    before returning the results."""

    query = gql(
        """
        query getMutationName($modelId: String!) {
            action(modelId: $modelId) {
                action {
                    ... on CoreAction {
                        mutationName
                    }
                }
                errors {
                    message
                }
            }
        }
    """
    )

    def _get_variable_values(
        self, action_id: Union[str, int]
    ):  # pylint:disable=arguments-differ
        return {"modelId": str(action_id)}

    def _format_response(self, response: dict, *_) -> str:
        return response["action"]["action"]["mutationName"]

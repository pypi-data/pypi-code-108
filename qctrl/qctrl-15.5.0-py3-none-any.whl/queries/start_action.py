# Copyright 2020 Q-CTRL Pty Ltd & Q-CTRL Inc. All rights reserved.
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
import json
from copy import deepcopy
from typing import Any

from gql import Client
from graphql import (
    DocumentNode,
    GraphQLType,
)
from qctrlcommons.exceptions import QctrlGqlException
from qctrlcommons.serializers import DataTypeDecoder

from .base import PatternQuery
from .multi import (
    MultiQuery,
    _suffix_document,
)
from .refresh_action import RefreshActionQuery


def _format_action_result(data: dict):
    """
    Decodes the `result` from the given action data, and promotes it to the top-level response.
    """
    if data["action"].get("result") is not None:
        result_data = json.loads(data["action"].pop("result"), cls=DataTypeDecoder)
        data.update(result_data)


class StartActionQuery(PatternQuery):  # pylint:disable=too-few-public-methods
    """
    Query used to start an action.

    The per-mutation result fields are not currently populated by the API, so to handle the case
    where the result is computed immediately, this query fetches the generic action `result` dict
    instead. To make this work with the logic for loading the response into data classes, we decode
    that `result` dict and promote its contents to the top-level response, which is where the
    response loading logic expects it.
    """

    query_pattern = """
        mutation startAction {
            %(mutation_name)s(input: %(payload)s) {
                action {
                    modelId
                    name
                    status
                    errors {
                        exception
                    }
                    progress
                    result
                }
                errors {
                    fields
                    message
                }
             }
        }
    """

    def __init__(
        self,
        client: Client,
        env: "GraphQLCustomEnvironment",
        mutation_name: str,
        input_type: GraphQLType,
        result_type: GraphQLType,
        data: Any,
    ):
        payload = env.format_payload(input_type, data)

        super().__init__(
            client,
            mutation_name=mutation_name,
            payload=payload,
        )

        self._env = env
        self._result_type = result_type
        self._mutation_name = mutation_name

    def create_result_object(self, data: Any) -> Any:
        """Creates a result object to store the response data."""
        result = self._env.load_data(self._result_type, data)

        if result.errors:
            raise QctrlGqlException(result.errors)

        return result

    def get_refresh_query(self) -> RefreshActionQuery:
        """Get the corresponding refresh query."""
        return self._env.build_refresh_query(self._result_type)

    def _format_response(self, response, *_) -> dict:
        _format_action_result(response[self._mutation_name])
        return response


class MultiStartActionQuery(MultiQuery):
    """Starts multiple actions."""

    name = "startActions"

    def _transform_sub_query_document(
        self, index: int, document: DocumentNode
    ) -> DocumentNode:
        document = deepcopy(document)
        _suffix_document(document, str(index + 1))
        return document

    def _format_response(self, response, *args):
        response = super()._format_response(response, *args)

        # for each response, format the data for updating
        for sub_response in response:
            _format_action_result(sub_response)

        return response

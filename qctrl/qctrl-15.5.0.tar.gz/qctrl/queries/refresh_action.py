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
import json
from copy import deepcopy
from typing import Union

from gql import Client
from graphql import (
    DocumentNode,
    GraphQLNonNull,
    GraphQLType,
)
from qctrlcommons.serializers import DataTypeDecoder

from .base import PatternQuery
from .multi import (
    MultiQuery,
    _suffix_document,
)


def _format_action_result(data: dict):
    """Prepares data for updating a Result object. If the
    action result is included in the data, it is decoded
    and promoted to the top level of the data."""

    # if result data included in response
    if data["action"].get("result") is not None:

        # decode result data
        result_data = json.loads(data["action"].pop("result"), cls=DataTypeDecoder)

        # move to top level
        data.update(result_data)


class RefreshActionQuery(PatternQuery):  # pylint:disable=too-few-public-methods
    """Query used to check action completion."""

    query_pattern = """
        query refreshAction($modelId: String!) {
            coreAction(modelId: $modelId) {
                coreAction {
                    ... on %(field_type)s {
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
                errors {
                    message
                    fields
                }
            }
        }
    """

    def __init__(self, client: Client, field_type: GraphQLType):

        if isinstance(field_type, GraphQLNonNull):
            field_type = field_type.of_type

        self.field_type = field_type
        super().__init__(client, field_type=field_type.name)

    def _get_variable_values(
        self, action_id: Union[str, int]
    ):  # pylint:disable=arguments-differ
        return {"modelId": str(action_id)}

    def _format_response(self, response, *_) -> dict:
        # retrieve and format the update data
        data = response["coreAction"]["coreAction"]
        _format_action_result(data)
        return data


class MultiRefreshActionQuery(MultiQuery):
    """Check completion for multiple actions."""

    name = "refreshActions"

    def _transform_sub_query_document(
        self, index: int, document: DocumentNode
    ) -> DocumentNode:
        document = deepcopy(document)
        _suffix_document(document, str(index + 1))
        return document

    def _get_variable_values(
        self, *action_ids: Union[str, int]
    ):  # pylint:disable=arguments-differ
        values = {}

        for index, action_id in enumerate(action_ids):
            key = f"modelId_{index+1}"
            values.update({key: action_id})

        return values

    def _format_response(self, response, *args):
        response = super()._format_response(response, *args)

        # for each response, format the data for updating
        for index, sub_response in enumerate(response):
            data = sub_response["coreAction"]
            _format_action_result(data)
            response[index] = data

        return response

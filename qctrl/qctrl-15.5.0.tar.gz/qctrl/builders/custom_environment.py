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
from functools import lru_cache
from typing import (
    Any,
    List,
    Union,
)

import inflection
from gql import Client
from graphql import GraphQLType
from tqdm.auto import tqdm

from ..queries import (
    MultiRefreshActionQuery,
    RefreshActionQuery,
    StartActionQuery,
)
from .async_result import (
    AsyncResult,
    AsyncResultCollection,
)
from .custom_handlers import (
    ComplexArrayEntryHandler,
    ComplexArrayHandler,
    ComplexArrayInputHandler,
    ComplexDenseArrayHandler,
    ComplexNumberHandler,
    ComplexNumberInputHandler,
    ComplexSparseArrayHandler,
    DateTimeScalarHandler,
    GraphScalarHandler,
    JsonDictScalarHandler,
    UnixTimeScalarHandler,
)
from .graphql_utils import (
    BaseHandler,
    GraphQLEnvironment,
)
from .type_registry import TypeRegistry
from .wait import Wait

LOGGER = logging.getLogger(__name__)


class QctrlGraphQLEnvironment(GraphQLEnvironment):
    """
    Custom GraphQLEnvironment class.
    """

    _action_selection_override = {
        "action": r"{ modelId name status errors { exception } progress }"
    }

    def __init__(
        self,
        gql_client: Client,
        type_registry_cls: type = None,
        custom_handlers: List[BaseHandler] = None,
    ):
        self._gql_client = gql_client
        super().__init__(type_registry_cls, custom_handlers)

    @lru_cache()
    def field_to_attr(self, field_name: str) -> str:
        """Uses inflection to convert a GraphQL
        field name to an attribute name.

        Parameters
        ----------
        field_name : str
            The name of the GraphQL field.

        Returns
        -------
        str
            attribute name
        """
        return inflection.underscore(field_name)

    def build_mutation_query(
        self,
        mutation_name: str,
        input_type: GraphQLType,
        result_type: GraphQLType,
        data: Any,
    ) -> StartActionQuery:
        """Returns the corresponding StartActionQuery object."""
        query = StartActionQuery(
            self._gql_client, self, mutation_name, input_type, result_type, data
        )

        return query

    def wait_for_completion(
        self,
        refresh_query: Union[RefreshActionQuery, MultiRefreshActionQuery],
        *async_results: AsyncResult
    ):
        """Waits until the corresponding actions are completed on the server."""
        promise = AsyncResultCollection(*async_results)
        if promise.is_completed:
            promise.finalize()
            return

        _wait = Wait()

        with tqdm(total=100, leave=False) as progress_bar:

            while not promise.is_completed:

                promise.update_progress(progress_bar)

                _wait()

                # check completion
                response = refresh_query(*promise.get_action_ids())
                promise.update_data(self, response, progress_bar)

            progress_bar.update(max(0, progress_bar.total - progress_bar.n))

        promise.finalize()

    def build_refresh_query(self, field_type: GraphQLType) -> RefreshActionQuery:
        """Returns a RefreshActionQuery object for
        refreshing an object populated with response data.
        """
        return RefreshActionQuery(self._gql_client, field_type)


def create_environment(gql_client: Client) -> QctrlGraphQLEnvironment:
    """Creates the custom environment object with
    all custom handlers.
    """
    return QctrlGraphQLEnvironment(
        gql_client=gql_client,
        type_registry_cls=TypeRegistry,
        custom_handlers=[
            ComplexArrayEntryHandler,
            ComplexArrayHandler,
            ComplexArrayInputHandler,
            ComplexDenseArrayHandler,
            ComplexNumberHandler,
            ComplexNumberInputHandler,
            ComplexSparseArrayHandler,
            DateTimeScalarHandler,
            GraphScalarHandler,
            JsonDictScalarHandler,
            UnixTimeScalarHandler,
        ],
    )

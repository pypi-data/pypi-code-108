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
from typing import List

from .builders import AsyncResult
from .queries import (
    MultiRefreshActionQuery,
    MultiStartActionQuery,
    StartActionQuery,
)

LOGGER = logging.getLogger(__name__)


class ParallelExecutionCollector:
    """Collects function calls and executes them in parallel."""

    def __init__(self, qctrl: "Qctrl"):
        self._qctrl = qctrl
        self._queries: List[StartActionQuery] = []
        self._async_results: List[AsyncResult] = []

    def add(self, query: StartActionQuery, async_result: AsyncResult):
        """Collect a function call as a query and the result object."""
        self._queries.append(query)
        self._async_results.append(async_result)

    def __enter__(self):
        self._qctrl.start_collection_mode(self)

    def __exit__(self, exc_type, exc_value, traceback):
        self._qctrl.stop_collection_mode()

        # dont try to call any functions upon an exception
        if isinstance(exc_value, Exception):
            return False

        if not self._queries:
            LOGGER.warning("No functions collected. Nothing to do.")
            return True

        assert len(self._queries) == len(self._async_results)

        multi_query = MultiStartActionQuery(self._qctrl.gql_api, *self._queries)
        response = multi_query()

        LOGGER.debug("response:%s", response)

        if len(self._queries) != len(response):
            raise RuntimeError(
                f"Unexpected responses ({len(response)}) for queries ({len(self._queries)})"
            )

        # update results with initial data
        for index, async_result in enumerate(self._async_results):
            response_data = response[index]
            async_result.update(self._qctrl.gql_env, response_data)

        # build refresh query
        refresh_queries = []

        for query in self._queries:
            refresh_queries.append(query.get_refresh_query())

        refresh_query = MultiRefreshActionQuery(self._qctrl.gql_api, *refresh_queries)

        # wait for completion of all function calls
        self._qctrl.gql_env.wait_for_completion(refresh_query, *self._async_results)

        return True

# Copyright 2020 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""GraphAQL request handler module."""
from .graphql_queries import TEST_SUITE_STARTED


def request(etos, query):
    """Request graphql in a generator.

    :param etos: ETOS client instance.
    :type etos: :obj:`etos_lib.etos.Etos`
    :param query: Query to send to graphql.
    :type query: str
    :return: Generator
    :rtype: generator
    """
    wait_generator = etos.utils.wait(etos.graphql.execute, query=query)
    yield from wait_generator


def request_test_suite_started(etos, activity_id):
    """Request test suite started from graphql.

    :param etos: ETOS client instance.
    :type etos: :obj:`etos_lib.etos.Etos`
    :param activity_id: ID of activity in which the test suites started
    :type activity_id: str
    :return: Iterator of test suite started graphql responses.
    :rtype: iterator
    """
    for response in request(etos, TEST_SUITE_STARTED % activity_id):
        if response:
            for _, test_suite_started in etos.graphql.search_for_nodes(
                response, "testSuiteStarted"
            ):
                yield test_suite_started
            return None  # StopIteration
    return None  # StopIteration

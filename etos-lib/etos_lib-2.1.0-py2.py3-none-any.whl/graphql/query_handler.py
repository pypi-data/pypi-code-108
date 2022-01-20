# Copyright 2020-2021 Axis Communications AB.
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
"""ETOS Library GraphQL query handler module."""
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from etos_lib.lib.utils import Utils
from etos_lib.lib.debug import Debug


class GraphQLQueryHandler:
    """Create and send GraphQL queries."""

    __client = None

    def __init__(self):
        """Graphql query handler."""
        self.transport_protocol = RequestsHTTPTransport
        self.utils = Utils()
        self.debug = Debug()

    @property
    def transport(self):
        """Transport protocol used for graphql."""
        return self.transport_protocol(self.debug.graphql_server)

    @property
    def client(self):
        """Graphql client."""
        if self.__client is None:
            self.__client = Client(transport=self.transport)
        return self.__client

    @staticmethod
    def query(query):
        """Create a query for graphql.

        :param query: Query to make.
        :type query: str
        :return: Graphql formatted query.
        :rtype: :obj:`gql`
        """
        return gql(query)

    def execute(self, query):
        """Execute query against graphql.

        :param query: Query to make.
        :type query: str
        :return: Result from query.
        :rtype: dict
        """
        return self.client.execute(self.query(query))

    def search_for_nodes(self, response, *nodes):
        """Search for nodes in a GraphQL response. Iterator.

        :param response: GraphQL response dictionary.
        :type response: dict
        :param nodes: Nodes to search for.
                      They are represented as keys in the response dict.
        :type nodes: list
        :return: Node name and node dictionary.
        :rtype: tuple
        """
        for node_name, edge in self.utils.search(response, *nodes):
            if edge.get("edges") is not None:
                for node in edge.get("edges"):
                    yield node_name, node["node"]
            else:
                yield node_name, edge

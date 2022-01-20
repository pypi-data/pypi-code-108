"""
Extension of the GraphQL supporting retries for data processing use cases
"""
import logging

import requests
from gqlclient.base import GraphQLClientBase
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class GraphQLClient(GraphQLClientBase):
    """
    Helper class for formatting and executing synchronous GraphQL queries and mutations
    """

    adapter = HTTPAdapter(
        max_retries=Retry(
            total=5,
            status_forcelist=[502, 503, 404],
            method_whitelist=["POST"],
        )
    )

    def execute_gql_call(self, query: dict, **kwargs) -> dict:
        """
        Executes a GraphQL query or mutation using requests.

        :param query: Dictionary formatted graphql query

        :param kwargs: Optional arguments that `requests` takes. e.g. headers

        :return: Dictionary containing the response from the GraphQL endpoint
        """
        logger.debug(f"Executing graphql call: host={self.gql_uri}")
        with requests.sessions.Session() as http:
            http.mount("http://", self.adapter)
            response = http.post(url=self.gql_uri, json=query, **kwargs)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error executing graphql call: status_code={e.response.status_code}, detail={e.response.text}"
            )
            raise e
        return response.json()

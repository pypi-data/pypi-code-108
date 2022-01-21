import uuid
from typing import Optional, Union, Dict

from box import Box, BoxList
from sgqlc.endpoint.requests import RequestsEndpoint

from pycarlo.common import get_logger, settings
from pycarlo.common.errors import GqlError
from pycarlo.common.settings import MCD_API_ENDPOINT, DEFAULT_MCD_API_ID_HEADER, DEFAULT_MCD_API_TOKEN_HEADER, \
    DEFAULT_MCD_SESSION_ID, DEFAULT_MCD_TRACE_ID, DEFAULT_MCD_USER_ID_HEADER
from pycarlo.core.operations import Query, Mutation
from pycarlo.core.session import Session

logger = get_logger(__name__)


class Client:
    def __init__(self, session: Optional[Session] = None):
        """
        Create a client for making requests to the MCD API.

        :param session: Specify a session. Otherwise a session is created using the default profile.
        """
        self._session = session or Session()

    @property
    def session_id(self) -> str:
        """
        Retrieves the MCD API ID from the client's current session. For helping identifying requester client-side.
        """
        return self._session.id

    @property
    def session_name(self) -> str:
        """
        Retrieves the session name from the client's current session. For helping trace requests downstream.
        """
        return self._session.session_name

    def _get_headers(self) -> Dict:
        """
        Gets headers from session for using the MCD API.

        Generates a trace ID to help trace (e.g debug) specific requests downstream. Enable verbose logging to echo.
        """
        headers = {
            DEFAULT_MCD_API_ID_HEADER: self.session_id,
            DEFAULT_MCD_API_TOKEN_HEADER: self._session.token,
            DEFAULT_MCD_SESSION_ID: self.session_name,
            DEFAULT_MCD_TRACE_ID: str(uuid.uuid4()),
        }

        if settings.MCD_USER_ID_HEADER:
            headers[DEFAULT_MCD_USER_ID_HEADER] = settings.MCD_USER_ID_HEADER

        return headers

    def __call__(self,
                 query: Union[Query, Mutation, str],
                 variables: Optional[Dict] = None,
                 operation_name: Optional[str] = None,
                 timeout_in_seconds: Optional[int] = 30) -> Union[Query, Mutation, Box, BoxList]:
        """
        Make a request to the MCD API.

        :param query: GraphQL query or mutation to execute. Can pass a string or Query/Mutation object.
        :param variables: Any variables to use with the query.
        :param operation_name: Name of the operation.
        :param timeout_in_seconds: Set timeout of request. Requests cannot exceed 30 seconds.

        :return: Returns a Query or Mutation object with the response if the input query was a Query or Mutation object.
            If the input was a string a Box object containing the response is returned.
            Raises GqlError if any errors are found in the response.

        Box is a transparent replacement for a dictionary - converting CamelCase to snake_case and allowing using dot
        notation in lookups. Can use .to_dict() to get a regular dictionary.
        """
        headers = self._get_headers()
        logger.info(f"Sending request to '{MCD_API_ENDPOINT}' with trace ID '{headers[DEFAULT_MCD_TRACE_ID]}' "
                    f"in named session '{headers[DEFAULT_MCD_SESSION_ID]}'.")

        request = RequestsEndpoint(url=MCD_API_ENDPOINT, base_headers=headers, timeout=timeout_in_seconds)
        response = request(query, variables=variables, operation_name=operation_name)

        if 'errors' in response:
            raise GqlError(response['errors'])

        if not isinstance(query, str):
            return query + response
        return Box(response, camel_killer_box=True).data

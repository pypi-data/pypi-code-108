# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from typing import Any
from typing import AsyncGenerator
from typing import Dict
from typing import Generic
from typing import NoReturn
from typing import Optional
from typing import Type
from typing import TypeVar

import httpx
from gql.transport import AsyncTransport
from gql.transport import Transport
from gql.transport.exceptions import TransportAlreadyConnected
from gql.transport.exceptions import TransportClosed
from gql.transport.exceptions import TransportProtocolError
from gql.transport.exceptions import TransportServerError
from graphql import DocumentNode
from graphql import ExecutionResult
from graphql import print_ast
from structlog import get_logger

from raclients.graph.util import graphql_error_from_dict

logger = get_logger()

AnyHTTPXClient = TypeVar("AnyHTTPXClient", httpx.Client, httpx.AsyncClient)


class BaseHTTPXTransport(Generic[AnyHTTPXClient]):
    """
    This class is inspired heavily by GQL's AIOHTTPTransport and RequestsHTTPTransport,
    encapsulating the logic in smaller functions to allow for greater reuse.
    """

    def __init__(
        self,
        url: str,
        client_cls: Type[AnyHTTPXClient],
        client_args: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        HTTPX Transport for GQL.

        Args:
            url: The GraphQL server URL. Example: 'http://mo:5000/graphql'.
            client_cls: The HTTPX client class to instantiate.
            client_args: Dict of extra args passed to the HTTPX client.
        """
        self.url = url
        self.client_cls: Type[AnyHTTPXClient] = client_cls
        self.client_args = client_args
        self.client: Optional[AnyHTTPXClient] = None

    @property
    def session(self) -> Optional[AnyHTTPXClient]:
        """
        GQL is hardcoded to access 'session', but we prefer to work with 'client', as is
        custom with HTTPX.

        Returns: HTTPX client.
        """
        return self.client

    def _connect(self) -> None:
        """
        Create a HTTPX client as self.client. Should be cleaned with a call to close().
        """
        if self.client is not None:
            raise TransportAlreadyConnected("Transport is already connected")
        self.client = self.client_cls(**(self.client_args or {}))

    @staticmethod
    def _construct_payload(
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Construct the GraphQL payload to be sent to the server.

        Args:
            document: GQL document.
            variable_values: Optional variable values to be used in the query.
            operation_name: Optional name of the query.

        Returns: The GraphQL payload.
        """
        query_str = print_ast(document)
        payload: Dict[str, Any] = {
            "query": query_str,
        }

        if variable_values:
            payload["variables"] = variable_values
        if operation_name:
            payload["operationName"] = operation_name

        logger.debug({"payload": json.dumps(payload)})

        return payload

    def _decode_response(
        self, response: httpx.Response, query: Optional[str] = None
    ) -> ExecutionResult:
        """
        Decodes raw GraphQL response from the server.

        Args:
            response: Raw HTTPX response.
            query: Optional request query. Used for better output in case of errors.

        Returns: graphql ExecutionResult, containing the result and potential errors.
        """
        logger.debug({"response": response.text})

        try:
            result = response.json()
        except Exception:  # noqa
            self._raise_response_error(response, "Not a JSON answer")

        if "errors" not in result and "data" not in result:
            self._raise_response_error(response, "No 'data' or 'errors' keys in answer")

        errors = None
        if "errors" in result:
            errors = [graphql_error_from_dict(e, query) for e in result["errors"]]

        return ExecutionResult(
            data=result.get("data"),
            errors=errors,
            extensions=result.get("extensions"),
        )

    @staticmethod
    def _raise_response_error(resp: httpx.Response, reason: str) -> NoReturn:
        """
        Raise the TransportError subclass corresponding to the exception encountered.
        Raises TransportServerError if the http status code is 400 or higher, and
        TransportProtocolError in all other cases.

        Args:
            resp: Raw HTTPX response.
            reason: Error message for protocol errors.

        Raises: Subclass of TransportError.
        """
        try:
            resp.raise_for_status()  # raises a HTTPError if response status is >400
        except httpx.HTTPStatusError as e:
            raise TransportServerError(str(e), e.response.status_code) from e

        raise TransportProtocolError(
            f"Server did not return a GraphQL result: {reason}: {resp.text}"
        )


class HTTPXTransport(BaseHTTPXTransport[httpx.Client], Transport):
    def __init__(
        self,
        url: str,
        client_cls: Type[httpx.Client] = httpx.Client,
        client_args: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(url, client_cls, client_args)

    def connect(self) -> None:
        """
        Create a HTTPX Client as self.client. Should be cleaned with a call to close().
        """
        return super()._connect()

    def close(self) -> None:
        """
        Close the client. GQL automatically calls this.
        """
        if self.client is not None:
            self.client.close()
        self.client = None

    def execute(
        self,
        document: DocumentNode,
        *args: Any,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        extra_args: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> ExecutionResult:
        """
        Execute the provided document AST against the configured remote server using the
        current client.

        Args:
            document: GQL document.
            variable_values: Optional variable values to be used in the query.
            operation_name: Optional name of the query.
            extra_args: Extra arguments, passed through to the request.

        Returns: graphql ExecutionResult, containing the result and potential errors.
        """
        if self.client is None:
            raise TransportClosed("Transport is not connected")

        payload = self._construct_payload(document, variable_values, operation_name)
        response = self.client.post(url=self.url, json=payload, **(extra_args or {}))
        return self._decode_response(response, query=payload["query"])


class AsyncHTTPXTransport(BaseHTTPXTransport[httpx.AsyncClient], AsyncTransport):
    def __init__(
        self,
        url: str,
        client_cls: Type[httpx.AsyncClient] = httpx.AsyncClient,
        client_args: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(url, client_cls, client_args)

    async def connect(self) -> None:
        """
        Create a HTTPX AsyncClient as self.client. Should be cleaned with a call to
        close(). Wraps sync function since GQL expects a coroutine for AsyncTransport.
        """
        return super()._connect()

    async def close(self) -> None:
        """
        Close the client. GQL automatically calls this.
        """
        if self.client is not None:
            await self.client.aclose()
        self.client = None

    async def execute(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        extra_args: Dict[str, Any] = None,
    ) -> ExecutionResult:
        """
        Execute the provided document AST against the configured remote server using the
        current client.

        Args:
            document: GQL document.
            variable_values: Optional variable values to be used in the query.
            operation_name: Optional name of the query.
            extra_args: Extra arguments, passed through to the request.

        Returns: graphql ExecutionResult, containing the result and potential errors.
        """
        if self.client is None:
            raise TransportClosed("Transport is not connected")

        payload = self._construct_payload(document, variable_values, operation_name)
        response = await self.client.post(
            url=self.url, json=payload, **(extra_args or {})
        )
        return self._decode_response(response, query=payload["query"])

    def subscribe(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> AsyncGenerator[ExecutionResult, None]:
        """
        Subscribe is not supported on HTTP.

        Raises: NotImplementedError.
        """
        raise NotImplementedError("The HTTP transport does not support subscriptions")

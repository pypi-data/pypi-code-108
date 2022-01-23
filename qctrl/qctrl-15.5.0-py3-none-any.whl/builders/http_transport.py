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

import gzip
from typing import (
    Any,
    Dict,
    Optional,
)

import requests
from gql import Client
from gql.transport.exceptions import (
    TransportClosed,
    TransportProtocolError,
    TransportServerError,
)
from gql.transport.requests import RequestsHTTPTransport
from graphql import (
    DocumentNode,
    ExecutionResult,
    print_ast,
)
from requests.compat import json as complexjson


class QctrlRequestsHTTPTransport(RequestsHTTPTransport):
    """ Custom GQL requests class to enable compression of requests."""

    def execute(  # pylint:disable=arguments-differ
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        timeout: Optional[str] = None,
        disable_result_cache: bool = False,
    ) -> ExecutionResult:
        """Execute GraphQL query.

        Execute the provided document AST against the configured remote server. This
        uses the requests library to perform a HTTP POST request to the remote server.

        Parameters
        ----------
        document : DocumentNode
            GraphQL query as AST Node object.
        variable_values : Optional[Dict[str, Any]]
            Dictionary of input parameters (Default value = None).
        operation_name : Optional[str]
            Name of the operation that shall be executed.
            Only required in multi-operation documents (Default value = None).
        timeout : Optional[str]
            Specifies a default timeout for requests (Default value = None).
        disable_result_cache: bool
            disable cache layer usage when retrieve result(Default value = False).


        Returns
        -------
        ExecutionResult
            The result of execution.
            `data` is the result of executing the query, `errors` is null
            if no errors occurred, and is a non-empty array if an error occurred.

        Raises
        ------
        TransportServerError
            if the status code is 400 or higher
        TransportProtocolError
            in the other cases
        TransportClosed
            if gql client session is closed.
        """

        if not self.session:
            raise TransportClosed("Transport is not connected")

        query_str = print_ast(document)
        payload: Dict[str, Any] = {"query": query_str}
        if variable_values:
            payload["variables"] = variable_values
        if operation_name:
            payload["operationName"] = operation_name

        data_key = "json" if self.use_json else "data"

        # compress the payload
        json_payload = complexjson.dumps(payload)
        gzip_payload = gzip.compress(bytes(json_payload, "utf-8"))

        if disable_result_cache is not None:
            self.headers.update({"disable_result_cache": str(disable_result_cache)})

        post_args = {
            "headers": self.headers,
            "auth": self.auth,
            "cookies": self.cookies,
            "timeout": timeout or self.default_timeout,
            "verify": self.verify,
            data_key: gzip_payload,
        }

        # Pass kwargs to requests post method
        post_args.update(self.kwargs)

        # Using the created session to perform requests
        response = self.session.request(
            self.method, self.url, **post_args  # type: ignore
        )

        try:
            response.raise_for_status()
            result = response.json()

        except requests.HTTPError as error:
            # We raise a TransportServerError if the status code is 400 or higher
            raise TransportServerError(str(error)) from error

        except Exception as exception:
            # We raise a TransportProtocolError in the other cases
            raise TransportProtocolError(
                "Server did not return a GraphQL result"
            ) from exception

        if "errors" not in result and "data" not in result:
            raise TransportProtocolError("Server did not return a GraphQL result")

        return ExecutionResult(errors=result.get("errors"), data=result.get("data"))


class QctrlGqlClient(Client):
    """
    Custom gql client class
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # force the fetch schema for validating client and client version
        with self as session:
            session.fetch_schema()

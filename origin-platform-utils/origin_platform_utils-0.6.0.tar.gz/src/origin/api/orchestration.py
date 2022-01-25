from dataclasses import is_dataclass

import flask
import serpyco
import rapidjson
from abc import abstractmethod
from functools import cached_property
from typing import List, Dict, Any, Optional, Type

from origin.tokens import TokenEncoder
from origin.serialize import simple_serializer
from origin.models.auth import InternalToken

from .context import Context
from .flask import FlaskContext
from .endpoint import Endpoint
from .guards import EndpointGuard, bouncer
from .responses import HttpResponse, BadRequest


# -- Request data ------------------------------------------------------------


class RequestDataProvider(object):
    """
    Provides request parameters.
    """
    @abstractmethod
    def get(self) -> Optional[Dict[str, Any]]:
        """
        TODO
        """
        raise NotImplementedError


class JsonBodyProvider(RequestDataProvider):
    """
    Reads request data from request body JSON.
    """
    def get(self) -> Optional[Dict[str, Any]]:
        """
        TODO
        """
        if not flask.request.data:
            return None

        try:
            return rapidjson.loads(flask.request.data.decode('utf8'))
        except rapidjson.JSONDecodeError:
            raise BadRequest('Invalid JSON body provided')


class QueryStringProvider(RequestDataProvider):
    """
    Reads request data from query parameters.
    """
    def get(self) -> Optional[Dict[str, Any]]:
        """
        TODO
        """
        return dict(flask.request.args)


# -- Orchestrator ------------------------------------------------------------


class RequestOrchestrator(object):
    """
    Orchestrates handling of HTTP requests on behalf of an endpoint.

    Behaves as a Flask endpoint, ie. it is callable without taking any
    parameters, so it plugs into Flask seamlessly.
    """
    def __init__(
            self,
            endpoint: Endpoint,
            data: RequestDataProvider,
            secret: str,
            guards: List[EndpointGuard] = None,
    ):
        self.endpoint = endpoint
        self.data = data
        self.secret = secret
        self.guards = guards

    def __call__(self) -> flask.Response:
        """
        Invoked by Flask to handle a HTTP request.
        """
        try:
            return self._invoke_endpoint()
        except HttpResponse as e:
            return self._handle_http_error(e)
        except Exception as e:
            raise
            return self._handle_exception(e)

    @cached_property
    def _internal_token_encoder(self) -> TokenEncoder[InternalToken]:
        """
        TODO
        """
        return TokenEncoder(
            schema=InternalToken,
            secret=self.secret,
        )

    def _build_context(self) -> Context:
        """
        Creates a new request context.
        """
        return FlaskContext(
            token_encoder=self._internal_token_encoder,
        )

    def _invoke_endpoint(self) -> flask.Response:
        """
        TODO
        """
        context = self._build_context()

        if self.guards:
            bouncer.validate(context, self.guards)

        # -- Define arguments for handler ------------------------------------

        handler_kwargs = {}

        if self.endpoint.requires_context:
            handler_kwargs['context'] = context

        # Deserialize request data (if necessary)
        if self.endpoint.should_parse_request_data:
            # Defaulting to an empty dictionary makes it possible to omit
            # request data for models where all fields are optional
            handler_kwargs['request'] = self._parse_request_data(
                data=self.data.get() or {},
                schema=self.endpoint.request_schema,
            )

        # -- Invoke endpoint -------------------------------------------------

        return_value = self.endpoint.handle_request(**handler_kwargs)

        # -- Parse return value ----------------------------------------------

        if isinstance(return_value, HttpResponse):
            response = return_value
        elif is_dataclass(return_value):
            response = HttpResponse(status=200, model=return_value)
        elif isinstance(return_value, (str, bytes)):
            response = HttpResponse(status=200, body=return_value)
        elif isinstance(return_value, dict):
            response = HttpResponse(status=200, json=return_value)
        elif return_value is None:
            response = HttpResponse(status=200)
        else:
            # TODO Handle this
            raise RuntimeError('ENDPOINT RETURNED INVALID RESPONSE?!?!?')

        # -- Create Flask response -------------------------------------------

        flask_response = flask.Response(
            status=response.status,
            mimetype=response.actual_mimetype,
            headers=response.actual_headers,
            response=response.actual_body,
        )

        for cookie in response.cookies:
            flask_response.set_cookie(
                key=cookie.name,
                value=cookie.value,
                expires=cookie.expires,
                path=cookie.path,
                domain=cookie.domain,
                secure=cookie.secure,
                httponly=cookie.http_only,
                samesite='Strict' if cookie.same_site else 'None',
            )

        return flask_response

    def _handle_http_error(self, e: HttpResponse) -> flask.Response:
        """
        TODO
        """
        return flask.Response(
            status=e.status,
            response=e.body,
            mimetype='text/html',  # TODO
            headers=e.headers,
        )

    def _handle_exception(self, e: Exception) -> flask.Response:
        """
        TODO
        """
        return flask.Response(
            status=500,
            response='Internal Server Error',
            mimetype='text/html',
        )

    def _parse_request_data(
            self,
            data: Dict[str, Any],
            schema: Type[Any],
    ) -> Any:
        """
        TODO
        """
        try:
            return simple_serializer.deserialize(
                data=data,
                schema=schema,
            )
        except serpyco.exception.ValidationError as e:
            # JSON schema validation failed for request data
            # TODO Parse ValidationError to something useful
            # TODO Format body properly
            raise BadRequest(body=str(e))

    # def _parse_response_object(self, response: Any) -> str:
    #     """
    #     TODO
    #     """
    #     return self.endpoint.response_serializer.dump_json(response)

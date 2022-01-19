import os
import copy
import json

from inspect import signature
from typing import Any, List, Callable

from werkzeug.wrappers import Request, Response, BaseResponse
from werkzeug.test import Client

from graphql.type.schema import GraphQLSchema
from graphql import format_error as format_error_default
from graphql.execution.execute import ExecutionContext

from graphql_http_server.helpers import (
    HttpQueryError,
    encode_execution_results,
    json_encode,
    load_json_body,
    run_http_query
)


def run_simple(
    schema,
    root_value: Any = None,
    middleware: List[Callable[[Callable, Any], Any]] = None,
    hostname: str = None,
    port: int = None,
    **kwargs
):
    return GraphQLHTTPServer.from_schema(
        schema=schema,
        root_value=root_value,
        middleware=middleware,
        **kwargs
    ).run_app(
        hostname=hostname,
        port=port,
        **kwargs
    )


graphiql_dir = os.path.join(os.path.dirname(__file__), 'graphiql')


class GraphQLHTTPServer:

    @classmethod
    def from_api(
        cls,
        api,
        root_value: Any = None,
        middleware: List[Callable[[Callable, Any], Any]] = None,
        middleware_on_introspection: bool = False,
        **kwargs
    ) -> 'GraphQLHTTPServer':
        try:
            from graphql_api import GraphQLAPI, GraphQLExecutor
            from graphql_api.context import GraphQLContext

        except ImportError:
            raise ImportError(
                'GraphQLAPI is not installed.'
            )

        api: GraphQLAPI = api

        executor = api.executor(
            root_value=root_value,
            middleware=middleware,
            middleware_on_introspection=middleware_on_introspection
        )

        schema: GraphQLSchema = executor.schema
        meta = executor.meta
        root_value = executor.root_value

        middleware = GraphQLExecutor.adapt_middleware(executor.middleware)
        context = GraphQLContext(schema=schema, meta=meta, executor=executor)

        return GraphQLHTTPServer(
            schema=schema,
            root_value=root_value,
            middleware=middleware,
            context=context,
            **kwargs
        )

    def __init__(
        self,
        schema: GraphQLSchema,
        root_value: Any = None,
        middleware: List[Callable[[Callable, Any], Any]] = None,
        context: Any = None,
        serve_graphiql: bool = True,
        graphiql_default_query: str = None,
        graphiql_default_variables: str = None,
        allow_cors: bool = False
    ):

        if middleware is None:
            middleware = []

        self.schema = schema
        self.root_value = root_value
        self.middleware = middleware
        self.context = context
        self.serve_graphiql = serve_graphiql
        self.graphiql_default_query = graphiql_default_query
        self.graphiql_default_variables = graphiql_default_variables
        self.allow_cors = allow_cors

    def create_context(self):
        return copy.copy(self.context)

    format_error = staticmethod(format_error_default)
    encode = staticmethod(json_encode)

    def dispatch(
        self,
        request: Request,
        context=None,
        execution_context_class: ExecutionContext = None
    ) -> Response:
        headers = {}

        try:
            request_method = request.method.lower()
            data = self.parse_body(request=request)

            if context is None:
                context = self.create_context()

            is_get = request_method == 'get'
            should_serve = self.should_serve_graphiql(request=request)

            show_graphiql = is_get and should_serve
            if show_graphiql:
                graphiql_path = os.path.join(
                    graphiql_dir,
                    'index.html'
                )
                if self.graphiql_default_query:
                    default_query = json.dumps(self.graphiql_default_query)
                else:
                    default_query = 'undefined'

                if self.graphiql_default_variables:
                    default_variables = json.dumps(
                        self.graphiql_default_variables
                    )
                else:
                    default_variables = 'undefined'

                html = open(graphiql_path, 'r').read()
                html = html.replace('"DEFAULT_QUERY"', default_query)
                html = html.replace('"DEFAULT_VARIABLES"', default_variables)

                return Response(html, content_type='text/html')

            if self.allow_cors:
                headers = {
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "GET, POST"
                }
                origin = request.headers.get('ORIGIN')
                if origin:
                    headers["Access-Control-Allow-Origin"] = origin

                if request_method == "options":
                    return Response(response="OK", headers=headers)

            execution_results, all_params = run_http_query(
                self.schema,
                request_method,
                data,
                query_data=request.args,
                root_value=self.root_value,
                middleware=self.middleware,
                context_value=context,
                execution_context_class=execution_context_class
            )
            result, status_code = encode_execution_results(
                execution_results,
                is_batch=isinstance(data, list),
                format_error=self.format_error,
                encode=self.encode
            )

            return Response(
                result,
                status=status_code,
                content_type='application/json',
                headers=headers
            )

        except HttpQueryError as e:
            return Response(
                self.encode({
                    'errors': [str(e)]
                }),
                status=e.status_code,
                headers={**e.headers, **headers} if e.headers else headers,
                content_type='application/json'
            )

    def parse_body(self, request):
        content_type = request.mimetype
        if content_type == 'application/graphql':
            return {'query': request.data.decode('utf8')}

        elif content_type == 'application/json':
            return load_json_body(request.data.decode('utf8'))

        elif content_type in (
                'application/x-www-form-urlencoded',
                'multipart/form-data'
        ):
            return request.form

        return {}

    def should_serve_graphiql(self, request):
        if not self.serve_graphiql or 'raw' in request.args:
            return False

        return self.request_wants_html(request=request)

    def request_wants_html(self, request):
        best = request.accept_mimetypes \
            .best_match(['application/json', 'text/html'])

        if best == 'text/html':
            accept_best = request.accept_mimetypes[best]
            accept_json = request.accept_mimetypes['application/json']
            return accept_best > accept_json

        return False

    def app(
        self,
        main: Callable[[Request], Response] = None
    ):

        @Request.application
        def app(request):
            if main is not None:
                return main(request)
            return self.dispatch(request=request)

        return app

    def client(self, main=None):
        return Client(self.app(main=main), BaseResponse)

    def run(
        self,
        main: Callable[[Request], Response] = None,
        hostname: str = None,
        port: int = None,
        **kwargs
    ):
        if hostname is None:
            hostname = 'localhost'

        if port is None:
            port = 5000

        from werkzeug.serving import run_simple

        valid_arg_names = list(signature(run_simple).parameters)

        kwargs = {k: v for k, v in kwargs.items() if k in valid_arg_names}

        run_simple(
            hostname=hostname,
            port=port,
            application=self.app(main=main),
            **kwargs
        )

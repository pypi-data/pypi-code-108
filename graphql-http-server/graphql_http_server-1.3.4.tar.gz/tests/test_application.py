import threading
import time
import urllib

import pytest
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from graphql_http_server import GraphQLHTTPServer


def is_graphql_api_installed():
    try:
        import graphql_api
    except ImportError:
        return False

    return True


class TestApplication:

    def test_dispatch(self, schema):
        server = GraphQLHTTPServer(schema=schema)

        builder = EnvironBuilder(method='GET', query_string="query={hello}")

        request = Request(builder.get_environ())
        response = server.dispatch(request=request)

        assert response.status_code == 200
        assert response.data == b'{"data":{"hello":"world"}}'

    def test_app(self, schema):
        server = GraphQLHTTPServer(schema=schema)
        response = server.client().get('/?query={hello}')

        assert response.status_code == 200
        assert response.data == b'{"data":{"hello":"world"}}'

    def test_graphiql(self, schema):
        server = GraphQLHTTPServer(schema=schema)
        response = server.client().get('/', headers={"Accept": "text/html"})

        assert response.status_code == 200
        assert b'GraphiQL' in response.data

    def test_no_graphiql(self, schema):
        server = GraphQLHTTPServer(schema=schema, serve_graphiql=False)
        response = server.client().get('/', headers={"Accept": "text/html"})

        assert response.status_code == 400

    def test_run_app_graphiql(self, schema):
        server = GraphQLHTTPServer(schema=schema)

        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()

        time.sleep(0.5)

        req = urllib.request.Request(
            "http://localhost:5000",
            headers={"Accept": "text/html"}
        )
        response = urllib.request.urlopen(req).read()

        assert b'GraphiQL' in response

    @pytest.mark.skipif(
        not is_graphql_api_installed(),
        reason="GraphQL-API is not installed"
    )
    def test_graphql_api(self):

        from graphql_api import GraphQLAPI

        api = GraphQLAPI()

        @api.type(root=True)
        class RootQueryType:

            @api.field
            def hello(self, name: str) -> str:
                return f"hey {name}"

        server = GraphQLHTTPServer.from_api(api=api)

        response = server.client().get('/?query={hello(name:"rob")}')

        assert response.status_code == 200
        assert response.data == b'{"data":{"hello":"hey rob"}}'

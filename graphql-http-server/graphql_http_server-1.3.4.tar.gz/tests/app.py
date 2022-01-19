from graphql_api import GraphQLAPI
from graphql_http_server import GraphQLHTTPServer

api = GraphQLAPI()


@api.type(root=True)
class HelloWorld:

    @api.field
    def hello_world(self) -> str:
        return "Hello world!"


server = GraphQLHTTPServer.from_api(
    api=api,
    graphiql_default_query="test_query",
    graphiql_default_variables="test_variables"
)


def main(request):
    return server.dispatch(request=request)


if __name__ == "__main__":
    server.run(port=3501)

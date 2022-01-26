from gql import Client
from gql.transport.requests import RequestsHTTPTransport
import requests

from relycomply_client.exceptions import RelyComplyClientException
from .gql_generator import GQLGenerator
from gql import gql
from gql.transport.exceptions import TransportProtocolError, TransportQueryError
from .credential_sources import StandardCredentials
from littleutils import only
import logging

log = logging.getLogger(__name__)


class RelyComplyGQLClient:
    """
    A flexible and intelligent GraphQL client for RelyComply. This client will create methods
    that match the mutation sand queries of the RelyComply API, and expose them with familiar
    calling conventions. It also handles paging as well as simplifying the returned structures.

    Queries can be called with their lowerCase field name and any filter arguments as kwargs, e.g.:

        client.products(nameContain="ZA") # Will return a list of products
        client.products(nameContain="ZA", _iter=True) # Will return a lazy generator
        client.products(name="retailZA", _only=True) # Will return only the first object or None

    Mutations can be called in a similar way, but arguments will be lifted into the $input variable

        client.createProduct(name="retailZA", label="South African Retail) # Returns the created product

    The interface is automatically generated from the GQL schema as well as the CLI support templates.
    Thus it should always be in sync.

    """

    def __init__(self, **kwargs):
        credentials = StandardCredentials(**kwargs)

        log.debug(
            f"Credentials: {', '.join([f'{k}={v}' for k,v in credentials.credentials().items()])}"
        )
        # Normalise the url to deal with older config files
        url = credentials.get("url")
        url = url.rstrip("/").rstrip("/graphql")

        # Setup a GQL client, pull creds from env
        transport = RequestsHTTPTransport(
            url=url + "/graphql/",
            verify=True,
            retries=3,
            headers={
                "IMPERSONATE": credentials.get("impersonate"),
                "Authorization": f"Bearer {credentials.require('token')}",
            },
        )
        try:
            self.client = Client(transport=transport, fetch_schema_from_transport=True)
            with self.client as session:
                # This forces the system to grab the schema
                # GQL v3 lazily fetches teh schema, but that is no help because we need the schema
                # to setup the object dynamically
                pass
        except TransportProtocolError:
            raise RelyComplyClientException(
                f"Could not retrieve schema from the given url: {url}"
            )
        except requests.exceptions.ConnectionError:
            raise RelyComplyClientException(
                f"Could not connect to the given url: {url}"
            )
        except TypeError:
            raise RelyComplyClientException(
                "The server could not authenticate you, are you sure your token is correct."
            )

        # Pull support templates
        self.templates = requests.get(url + "/cli/v1/support_templates/").json()

        self.schema = self.client.schema

        self.generator = GQLGenerator(self.schema, self.templates)
        self.mutation_fields = []
        self.query_fields = []

        self._attach_mutations()
        self._attach_queries()

    def _attach_mutations(self):
        for field in self.schema.mutation_type.fields.keys():
            self._attach_mutation(field)

    def _attach_mutation(self, field):
        def mutation(**variables):
            return self.execute_mutation(field, variables)

        self.mutation_fields.append(field)
        setattr(self, field, mutation)

    def _attach_queries(self):
        for field in self.schema.query_type.fields.keys():
            self._attach_query(field)

    def _attach_query(self, field):
        def query(_iter=False, _only=False, **variables):
            return self.execute_query(field, variables, _iter, _only)

        self.query_fields.append(field)
        setattr(self, field, query)

    def _collapse_edges(self, value):

        if isinstance(value, list):
            return [self._collapse_edges(child) for child in value]

        if isinstance(value, dict):
            replacement = {}
            for key, child in value.items():
                if (
                    isinstance(child, dict)
                    and len(child) == 1
                    and "edges" in child
                    and isinstance(child["edges"], list)
                ):
                    replacement[key] = [
                        self._collapse_edges(edge["node"]) for edge in child["edges"]
                    ]
                else:
                    replacement[key] = self._collapse_edges(child)
            return replacement
        else:
            return value

    def _only_value(self, result):
        return only(result.values())

    def _execute(self, query, variables):
        result = self.client.execute(query, variable_values=variables)
        return self._only_value(result)

    def _endpoint_graphql(self, action, endpoint):
        return self.generator.generate_endpoint(action, endpoint)

    def _endpoint_table_graphql(self, action, endpoint):
        return self.generator.generate_table_endpoint(action, endpoint)

    def _execute_endpoint(self, action, endpoint, variables, table_mode=False):
        if table_mode:
            graphql = self._endpoint_table_graphql(action, endpoint)
        else:
            graphql = self._endpoint_graphql(action, endpoint)

        query = gql(graphql)
        try:
            return self._execute(query, variables)
        except TransportQueryError as e:
            errors = e.errors
            raise RelyComplyClientException(str(errors[0]["message"])) from e

    def execute_query(self, endpoint, variables, _iter=False, _only=False):
        if _only:
            try:
                return next(self._execute_query_iter(endpoint, variables))
            except StopIteration:
                return None

        if _iter:
            return self._execute_query_iter(endpoint, variables)
        else:
            return list(self._execute_query_iter(endpoint, variables))

    def execute_query_for_table(self, endpoint, variables):
        return self.generator.filter_list_fields(
            endpoint, self._execute_query_iter(endpoint, variables, table_mode=True)
        )

    def _execute_query_iter(self, endpoint, variables, table_mode=False):
        after = None
        hasNextPage = True

        while hasNextPage:
            result = self._execute_endpoint(
                "query", endpoint, variables, table_mode=table_mode
            )
            hasNextPage = result["pageInfo"]["hasNextPage"]

            for edge in result["edges"]:
                node = edge["node"]
                yield self._collapse_edges(node)

            if not hasNextPage:
                break
            else:
                after = result["pageInfo"]["endCursor"]
                variables["after"] = after

    def execute_mutation(self, endpoint, variables):
        result = self._execute_endpoint("mutation", endpoint, dict(input=variables))
        return self._only_value(self._collapse_edges(result))

    def graphql(self, graphql_query, variables, **kwargs):
        """
        Execute a raw graphql query with the underlying client. No postprocessing will be done.

        This is useful because authentication credentials will be sorted out. kwargs will be passed
        through to the execute call of the raw client.
        """
        query = gql(graphql_query)
        return self.client.execute(query, variable_values=variables, **kwargs)

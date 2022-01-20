from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.modules.queries.query import Query
from cnvrgv2.config import error_messages, routes
from cnvrgv2.utils.api_list_generator import api_list_generator


class QueriesClient:
    def __init__(self, context=None):
        self._context = Context(context=context)
        scope = self._context.get_scope(SCOPE.DATASET)

        self._proxy = Proxy(context=self._context)
        self._route = routes.QUERIES_BASE.format(scope["organization"], scope["dataset"])

    def list(self, sort="-id"):
        """
        List all queries in a specific query
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields query objects
        """
        return api_list_generator(
            context=self._context,
            route=self._route,
            object=Query,
            sort=sort
        )

    def get(self, slug):
        """
        Retrieves a query by the given slug
        @param slug: The slug of the requested dataset
        @return: Query object
        """
        if not slug or not isinstance(slug, str):
            raise CnvrgArgumentsError(error_messages.QUERY_GET_FAULTY_SLUG)

        return Query(context=self._context, slug=slug)

    def create(self, name, query, commit_sha1=None):
        """
        Creates a new query with the given name
        @param name: Name of the new query
        @param query: Query string of the new query
        @param commit_sha1: Sha1 of the query commit
        @return: The newly created query object
        """
        if not name or not isinstance(name, str):
            raise CnvrgArgumentsError(error_messages.QUERY_CREATE_FAULTY_NAME)

        if not query or not isinstance(query, str):
            raise CnvrgArgumentsError(error_messages.QUERY_CREATE_FAULTY_QUERY)

        attributes = {
            "name": name,
            "query_raw": query,
            "commit_sha1": commit_sha1
        }
        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type="query", attributes=attributes)
        )

        slug = response.attributes['slug']
        return Query(context=self._context, slug=slug, attributes=response.attributes)

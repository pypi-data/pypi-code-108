from cnvrgv2.proxy import Proxy
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.config import error_messages, routes
from cnvrgv2.utils.api_list_generator import api_list_generator
from cnvrgv2.modules.resources.cluster import Cluster


class ClustersClient:
    def __init__(self, organization):
        self._context = Context(context=organization._context)
        scope = self._context.get_scope(SCOPE.ORGANIZATION)

        self._proxy = Proxy(context=self._context)
        self._route = routes.CLUSTERS_BASE.format(scope["organization"])

    def list(self, sort="-id"):
        """
        List all clusters in a specific resource
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields cluster objects
        """
        return api_list_generator(
            context=self._context,
            route=self._route,
            object=Cluster,
            sort=sort,
        )

    def get(self, slug):
        """
        Retrieves a cluster by the given slug
        @param slug: The slug of the requested cluster
        @return: Cluster object
        """
        if not slug or not isinstance(slug, str):
            raise CnvrgArgumentsError(error_messages.CLUSTER_GET_FAULTY_SLUG)

        return Cluster(context=self._context, slug=slug)

    # TODO: Add create function

from cnvrgv2.context import SCOPE, Context
from cnvrgv2.config import routes, error_messages
from cnvrgv2.errors import CnvrgArgumentsError

from cnvrgv2.modules.flows.flow_version.flow_version import FlowVersion
from cnvrgv2.proxy import Proxy
from cnvrgv2.utils.api_list_generator import api_list_generator


class FlowVersionsClient:
    def __init__(self, context=None):
        self._context = Context(context=context)
        scope = self._context.get_scope(SCOPE.FLOW)

        self._proxy = Proxy(context=self._context)
        self._route = routes.FLOW_VERSIONS_BASE.format(scope["organization"], scope["project"], scope["flow"])

    def get(self, slug):
        """
        Retrieves a flows version by the given title
        @param slug: The slug or title of the requested flow version
        @return: FlowVersion object
        """
        if not slug or not isinstance(slug, str):
            raise CnvrgArgumentsError(error_messages.FLOW_VERSION_GET_FAULTY_SLUG)

        return FlowVersion(context=self._context, slug=slug)

    def list(self, sort="-id"):
        """
        List all flow versions of a specific flows
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @return: Generator that yields flows version objects
        """
        return api_list_generator(
            context=self._context,
            route=self._route,
            object=FlowVersion,
            sort=sort
        )

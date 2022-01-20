
from cnvrgv2.context import SCOPE, Context
from cnvrgv2.config import routes, error_messages
from cnvrgv2.errors import CnvrgArgumentsError

from cnvrgv2.modules.flows.flow import Flow
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.utils.api_list_generator import api_list_generator
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.utils.url_utils import urljoin


class FlowsClient:
    def __init__(self, context=None):
        self._context = Context(context=context)
        scope = self._context.get_scope(SCOPE.PROJECT)

        self._proxy = Proxy(context=self._context)
        self._route = routes.FLOWS_BASE.format(scope["organization"], scope["project"])

    def _create_with_yaml(self, yaml_path):
        """
        Creates a flow from a predefined yaml file
        @param yaml_path: path of the yaml file
        @return: Flow object
        """
        create_with_yaml_url = urljoin(self._route, routes.CREATE_WITH_YAML)
        files_list = [("file", yaml_path)]

        response = self._proxy.call_api(
            route=create_with_yaml_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type="flows", attributes={}),
            files_list=files_list
        )

        slug = response.attributes['slug']
        return Flow(context=self._context, slug=slug)

    def get(self, slug):
        """
        Retrieves a flows by the given slug
        @param slug: The slug of the requested flows
        @return: Flow object
        """
        # TODO: Something is returning when getting a deleted flows. It fucks things up, check in tests
        if not slug or not isinstance(slug, str):
            raise CnvrgArgumentsError(error_messages.FLOW_GET_FAULTY_SLUG)

        return Flow(context=self._context, slug=slug)

    def create(self, yaml_path=None):
        """
        Creates a new flows with the given name
        @param yaml_path: Path to yaml file to create flows with
        @return: Flow object
        """
        # TODO: Missing in server, Add support for custom name
        # if not name or not isinstance(name, str):
        #     raise CnvrgError(error_messages.PROJECT_CREATE_FAULTY_NAME)

        # attributes = {"title": name}
        if yaml_path is not None:
            return self._create_with_yaml(yaml_path)

        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type="flows", attributes={})
        )

        slug = response.attributes['slug']
        return Flow(context=self._context, slug=slug)

    def list(self, sort="-id"):
        """
        List all flows in a specific project
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @return: Flow object generator
        """

        return api_list_generator(
            context=self._context,
            route=self._route,
            object=Flow,
            sort=sort
        )

    # DEV-10527: Currently disable. Missing full implementation in the server
    # def delete(self, slugs):
    #    """
    #    Deleting multiple flows
    #    @param slugs: List of flows slugs to be deleted
    #    @return: None
    #    """
    #
    #    attributes = {
    #        "slugs": slugs
    #    }
    #
    #    self._proxy.call_api(
    #        route=self._route,
    #        http_method=HTTP.DELETE,
    #        payload=JAF.serialize(type="flows", attributes=attributes)
    #    )

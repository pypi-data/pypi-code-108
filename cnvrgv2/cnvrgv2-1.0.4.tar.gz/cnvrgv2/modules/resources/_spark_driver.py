from cnvrgv2.config import routes, error_messages
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.modules.resources.templates.spark_templates_client import SparkTemplatesClient
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes


class SparkDriver(DynamicAttributes):
    available_attributes = {
        # TODO: Add relevant attributes
        "slug": str,
    }

    def __init__(self, context=None, slug=None, attributes=None):
        self._context = Context(context=context)

        # Set current context scope to current spark driver
        if slug:
            self._context.set_scope(SCOPE.RESOURCE, slug)

        scope = self._context.get_scope(SCOPE.RESOURCE)

        self._proxy = Proxy(context=self._context)
        self._route = routes.SPARK_DRIVER_BASE.format(scope["organization"], scope["resource"])
        self._attributes = attributes or {}
        self.slug = scope["resource"]
        self._init_clients()

    def save(self):
        pass

    def delete(self):
        """
        Deletes the current spark driver
        @return: None
        """
        self._proxy.call_api(route=self._route, http_method=HTTP.DELETE)

    def _init_clients(self):
        """
        Sets up the clients that are exposed to user user via machine
        @return: Void
        """
        try:
            self.templates = SparkTemplatesClient(context=self._context)
        except CnvrgArgumentsError:
            raise CnvrgArgumentsError(error_messages.FAILED_TO_INIT_CLIENT.format('templates'))

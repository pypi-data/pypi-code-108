from datetime import datetime
from dateutil import tz, parser
from cnvrgv2.config import routes
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.utils.url_utils import urljoin


class FlowVersion(DynamicAttributes):

    available_attributes = {
        "title": str,
        "slug": str,
        "id": int,
        "href": str,
        "state": str,
        "created_at": datetime,
        "start_time": datetime,
        "end_time": datetime,
        "schedule_time": datetime
    }

    def __init__(self, context=None, slug=None, attributes=None):
        self._context = Context(context=context)

        if slug:
            self._context.set_scope(SCOPE.FLOW_VERSION, slug)

        scope = self._context.get_scope(SCOPE.FLOW_VERSION)

        self._proxy = Proxy(context=self._context)
        self._route = routes.FLOW_VERSION_BASE.format(scope["organization"], scope["project"],
                                                      scope["flow"], scope["flow-version"])
        self._attributes = attributes or {}

        self.convert_time()
        self._type = "FlowVersion"
        self.slug = scope["flow-version"]

    def info(self):
        """
        Get info of the current flow version
        @return: info of the flow version
        """
        info_url = urljoin(self._route, routes.FLOW_VERSION_INFO)

        response = self._proxy.call_api(
            route=info_url,
            http_method=HTTP.GET
        )
        return response.attributes

    def stop(self):
        """
        Stops the current flow version, in case it's running
        @return: None
        """
        stop_url = urljoin(self._route, routes.FLOW_VERSION_STOP)

        self._proxy.call_api(
            route=stop_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes={})
        )

    def convert_time(self):
        """
        Internal conversion of schedule time
        """
        if not self._attributes.get("schedule_time", None):
            return

        self._attributes["schedule_time"] = parser.parse(self._attributes["schedule_time"])
        self._attributes["schedule_time"] = self._attributes["schedule_time"].astimezone(tz.tzlocal()).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ")

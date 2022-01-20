from cnvrgv2.config import routes
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes
from cnvrgv2.proxy import HTTP, Proxy
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.utils.url_utils import urljoin


class Ssh(DynamicAttributes):
    available_attributes = {
        "ssh_status": str,
        "pod_name": str,
        "namespace": str,
        "username": str,
        "password": str
    }

    def __init__(self, context, job_id):
        self._context = Context(context=context)
        scope = self._context.get_scope(SCOPE.ORGANIZATION)
        self._job_id = job_id
        self._proxy = Proxy(context=self._context)
        self._attributes = {}

        # Split into two routes so that dynamic attributes will work (depends on self._route)
        self._base_route = routes.SSH_BASE.format(scope["organization"], self._job_id)
        self._route = urljoin(self._base_route, routes.SSH_STATUS_SUFFIX)

    def start(self, username, password):
        start_ssh_route = urljoin(self._base_route, routes.SSH_START_SUFFIX)

        attributes = {
            "username": username,
            "password": password
        }

        self._proxy.call_api(
            route=start_ssh_route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type="sdk_v2_ssh", attributes=attributes)
        )

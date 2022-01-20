from cnvrgv2.config import routes
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes
from cnvrgv2.utils.validators import attributes_validator


class OrganizationSettings(DynamicAttributes):

    available_attributes = {
        "default_computes": list,
        "install_dependencies": bool,
        "slack_webhook_url": str,
        "debug_time": int,
        "email_on_error": bool,
        "email_on_success": bool,
        "queued_compute_wait_time": int,
        "idle_enabled": bool,
        "idle_time": int,
        "max_duration_workspaces": int,
        "max_duration_experiments": int,
        "max_duration_endpoints": int,
        "max_duration_webapps": int,
        "automatically_clear_cached_commits": int
    }

    def __init__(self, organization):
        self._context = Context(context=organization._context)
        scope = self._context.get_scope(SCOPE.ORGANIZATION)

        self._proxy = Proxy(context=self._context)
        self._route = routes.ORGANIZATION_SETTINGS.format(scope["organization"])

        self._attributes = {}

    def save(self):
        """
        Save the local settings in the current organization
        @return: None
        """
        self.update(**self._attributes)

    def update(self, **kwargs):
        """
        Updates current organization's settings with the given params
        @param kwargs: any param out of the available attributes can be sent
        @return: None
        """

        attributes_validator(
            available_attributes=OrganizationSettings.available_attributes,
            attributes=kwargs,
        )

        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.PUT,
            payload=JAF.serialize(type="settings", attributes={**self._attributes, **kwargs})
        )

        self._attributes = response.attributes

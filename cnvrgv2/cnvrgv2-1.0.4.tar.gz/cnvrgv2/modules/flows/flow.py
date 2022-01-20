from datetime import datetime
from cnvrgv2.config import routes, error_messages
from cnvrgv2.config.error_messages import NOT_A_DATASET_OBJECT
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes
from cnvrgv2.modules.dataset import Dataset
from cnvrgv2.modules.flows.flow_version.flow_versions_client import FlowVersionsClient
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.cron import Cron
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.utils.url_utils import urljoin
from cnvrgv2.utils.validators import validate_types_in_list


class Flow(DynamicAttributes):
    available_attributes = {
        "title": str,
        "slug": str,
        "created_at": datetime,
        "updated_at": datetime,
        "cron_syntax": str,
        "webhook_url": str,
        "trigger_dataset": str
    }

    def __init__(self, context=None, slug=None, attributes=None):
        self._context = Context(context=context)

        if slug:
            self._context.set_scope(SCOPE.FLOW, slug)

        scope = self._context.get_scope(SCOPE.FLOW)

        self._proxy = Proxy(context=self._context)
        self._route = routes.FLOW_BASE.format(scope["organization"], scope["project"], scope["flow"])
        self._attributes = attributes or {}
        self._type = "Flow"
        self.slug = scope["flow"]

        self._init_clients()

    def run(self):
        """
        Runs the current flow
        @return: None
        """

        run_url = urljoin(self._route, routes.RUN_FLOW)
        self._proxy.call_api(
            route=run_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes={})
        )

    def update(self, **kwargs):
        """
        Updates the current flows
        @param kwargs: Dictionary of attributes to update.
        supported attributes: title
        @return: The updated flows
        """

        if not kwargs:
            raise CnvrgArgumentsError(error_messages.EMPTY_ARGUMENT.format("kwargs"))

        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.PUT,
            payload=JAF.serialize(type=self._type, attributes=kwargs)
        )

        self._attributes = response.attributes
        return self

    def set_schedule(self, cron_expression):
        """
        Schedule the latest version of the current flows to run on a recurring basis
        @param cron_expression: A string in cron format. You can use Cron helper class
        @return:None
        """
        Cron.validate_cron_syntax(cron_expression)
        set_schedule_url = urljoin(self._route, routes.FLOW_SET_SCHEDULE)
        attributes = {
            "cron_syntax": cron_expression
        }

        self._proxy.call_api(
            route=set_schedule_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

    def clear_schedule(self):
        """
        Clears the recurring schedule, if exists
        @return:None
        """
        set_schedule_url = urljoin(self._route, routes.FLOW_STOP_SCHEDULE)

        self._proxy.call_api(
            route=set_schedule_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes={})
        )

    def toggle_webhook(self, toggle):
        """
        Toggles webhook on/off
        @param toggle: Boolean. Turn webhook on or off
        @return: None
        """
        if not isinstance(toggle, bool):
            error_message = error_messages.ARGUMENT_BAD_TYPE.format(bool.__name__, type(toggle).__name__)
            raise CnvrgArgumentsError(error_message)

        toggle_webhook_url = urljoin(self._route, routes.FLOW_TOGGLE_WEBHOOK)
        attributes = {
            "toggle": toggle
        }

        self._proxy.call_api(
            route=toggle_webhook_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

    def toggle_dataset_update(self, toggle, dataset=None):
        """
        Toggle a trigger that will run flow upon a dataset update
        @param toggle: Turn flow trigger upon dataset update
        @param dataset: The dataset that will trigger the flow upon update (dataset object)
        @return: None
        """
        argument_errors = {}
        if not isinstance(toggle, bool):
            error_message = error_messages.ARGUMENT_BAD_TYPE.format(bool.__name__, type(toggle).__name__)
            argument_errors["toggle"] = error_message

        if toggle and not (dataset and validate_types_in_list([dataset], Dataset)):
            argument_errors["dataset"] = NOT_A_DATASET_OBJECT

        if argument_errors:
            raise CnvrgArgumentsError(argument_errors)

        toggle_dataset_update_url = urljoin(self._route, routes.FLOW_TOGGLE_DATASET_UPDATE)
        attributes = {}

        if toggle:
            attributes = {
                "dataset_slug": dataset.slug
            }

        self._proxy.call_api(
            route=toggle_dataset_update_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

    def delete(self):
        """
        Deletes the current flow
        @return: None
        """
        self._proxy.call_api(
           route=self._route,
           http_method=HTTP.DELETE
        )

    def _init_clients(self):
        self.flow_versions = FlowVersionsClient(self._context)

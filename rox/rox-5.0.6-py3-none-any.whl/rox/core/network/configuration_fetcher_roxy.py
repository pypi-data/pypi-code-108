from requests.compat import urljoin

from rox.core.network.configuration_fetcher_base import ConfigurationFetcherBase
from rox.core.network.configuration_result import ConfigurationSource
from rox.core.consts.environment import Environment
from rox.core.network.request import RequestData
from rox.core.utils.http_status_code_helper import is_success_status_code

class ConfigurationFetcherRoxy(ConfigurationFetcherBase):
    def __init__(self, device_properties, request, configuration_fetched_invoker, error_reporter, roxy_url):
        super(ConfigurationFetcherRoxy, self).__init__(device_properties, request, configuration_fetched_invoker, error_reporter)
        self.roxy_url = roxy_url

    def fetch_from_roxy(self):
        roxy_endpoint = urljoin(self.roxy_url, Environment.ROXY_INTERNAL_PATH)
        query_params = {}

        for key, value in self.device_properties.get_all_properties().items():
            if key not in query_params:
                query_params[key] = value

        roxy_request = RequestData(roxy_endpoint, query_params)
        return self.request.send_get(roxy_request)

    def fetch(self):
        source = ConfigurationSource.ROXY
        try:
            fetch_roxy = self.fetch_from_roxy()
            if is_success_status_code(fetch_roxy):
                return super(ConfigurationFetcherRoxy, self).createResult(fetch_roxy, source)
            else:
                self.write_fetch_error_to_log_and_invoke_fetch_handler(source, fetch_roxy)
        except Exception as ex:
            self.write_fetch_exception_to_log_and_invoke_fetch_handler(source, ex)

        return None

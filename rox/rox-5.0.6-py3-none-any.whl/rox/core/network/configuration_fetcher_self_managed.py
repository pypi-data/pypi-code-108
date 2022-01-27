from requests import status_codes

from rox.core.network.configuration_fetcher_base import ConfigurationFetcherBase
from rox.core.network.configuration_result import ConfigurationSource
from rox.core.consts.property_type import CACHE_MISS_RELATIVE_URL, DISTINCT_ID, APP_KEY, BUID
from rox.core.consts.environment import Environment
from rox.core.network.request import RequestData
from rox.core.utils.http_status_code_helper import is_success_status_code

class ConfigurationFetcherSelfManaged(ConfigurationFetcherBase):
    def __init__(self, device_properties, request, configuration_fetched_invoker, error_reporter, buid):
        super(ConfigurationFetcherSelfManaged, self).__init__(device_properties, request, configuration_fetched_invoker, error_reporter)
        self.buid = buid

    def fetch(self):
        try:
            properties = self.prepare_properties()
            api_request = RequestData(self.get_api_path(properties), properties)
            fetch_result = self.request.send_post(api_request)
            if is_success_status_code(fetch_result):
                return super(ConfigurationFetcherSelfManaged, self).createResult(fetch_result, ConfigurationSource.API)
            self.write_fetch_error_to_log_and_invoke_fetch_handler(ConfigurationSource.API, fetch_result)
        except Exception as ex:
            self.write_fetch_exception_to_log_and_invoke_fetch_handler(ConfigurationSource.API, ex)

        return None

    def prepare_properties(self):
        query_params = {}

        for key, value in self.buid.get_query_string_parts().items():
            if key not in query_params:
                query_params[key] = value

        for key, value in self.device_properties.get_all_properties().items():
            if key not in query_params:
                query_params[key] = value

        query_params[CACHE_MISS_RELATIVE_URL.name] = self.get_relative_path(query_params)

        return query_params

    def get_relative_path(self, properties):
        return '%s/%s' % (properties[APP_KEY.name], properties[BUID.name])

    def get_api_path(self, properties):
        server_url = self.device_properties.rox_options.self_managed_options.server_url
        return '%s/%s' % (
            Environment.API_PATH(server_url),
            self.get_relative_path(properties)
        )

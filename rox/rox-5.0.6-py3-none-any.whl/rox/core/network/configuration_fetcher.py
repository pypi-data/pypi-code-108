from requests import status_codes

from rox.core.network.configuration_fetcher_base import ConfigurationFetcherBase
from rox.core.network.configuration_result import ConfigurationSource, ConfigurationFetchResult
from rox.core.consts.property_type import CACHE_MISS_RELATIVE_URL, DISTINCT_ID, APP_KEY, BUID
from rox.core.consts.environment import Environment
from rox.core.network.request import RequestData
from rox.core.utils.http_status_code_helper import is_success_status_code

class ConfigurationFetcher(ConfigurationFetcherBase):
    def __init__(self, device_properties, request, configuration_fetched_invoker, error_reporter, buid):
        super(ConfigurationFetcher, self).__init__(device_properties, request, configuration_fetched_invoker, error_reporter)
        self.buid = buid

    def fetch(self):
        source = ConfigurationSource.CDN
        try:
            properties = self.prepare_properties()
            fetch_result = self.fetch_from_cdn(properties)
            should_try_api = False

            if is_success_status_code(fetch_result):
                json_result = super(ConfigurationFetcher, self).createResult(fetch_result, source)
                if json_result is None or json_result.json_data is None:
                    return None

                if 'result' in json_result.json_data and json_result.json_data['result'] == 404:
                    should_try_api = True

                if not should_try_api:
                    return json_result

            if should_try_api or fetch_result.status_code in (status_codes.codes.forbidden, status_codes.codes.not_found):
                self.write_fetch_error_to_log_and_invoke_fetch_handler(source, fetch_result, raise_configuration_handler=False, next_source=ConfigurationSource.API)
                source = ConfigurationSource.API
                fetch_result = self.fetch_from_api(properties)
                if is_success_status_code(fetch_result):
                    return super(ConfigurationFetcher, self).createResult(fetch_result, source)

            self.write_fetch_error_to_log_and_invoke_fetch_handler(source, fetch_result)
        except Exception as ex:
            self.write_fetch_exception_to_log_and_invoke_fetch_handler(source, ex)

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

    def get_cdn_path(self, properties):
        return '%s/%s' % (Environment.CDN_PATH, self.get_relative_path(properties))

    def get_api_path(self, properties):
        return '%s/%s' % (Environment.API_PATH(), self.get_relative_path(properties))

    def fetch_from_cdn(self, properties):
        cdn_request = RequestData(self.get_cdn_path(properties), {DISTINCT_ID.name: properties[DISTINCT_ID.name]})
        return self.request.send_get(cdn_request)

    def fetch_from_api(self, properties):
        api_request = RequestData(self.get_api_path(properties), properties)
        return self.request.send_post(api_request)

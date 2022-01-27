import json
from requests import status_codes
from collections import OrderedDict
import sys
import traceback

from rox.core.logging.logging import Logging
from rox.core.network.configuration_result import ConfigurationSource
from rox.core.consts.environment import Environment
from rox.core.network.request import RequestData
from rox.core.consts import property_type
from rox.core.utils import md5_generator
from rox.core.utils.debounce import debounce
from rox.core.utils.http_status_code_helper import is_success_status_code
from collections import OrderedDict

class StateSender:
    RELEVANT_API_PROPERTIES = [
        property_type.PLATFORM,
        property_type.CUSTOM_PROPERTIES,
        property_type.FEATURE_FLAGS,
        property_type.DEV_MODE_SECRET
    ]

    MD5_STATE_GENERATORS = [
        property_type.PLATFORM,
        property_type.APP_KEY,
        property_type.CUSTOM_PROPERTIES,
        property_type.FEATURE_FLAGS,
        property_type.DEV_MODE_SECRET
    ]

    def __init__(self, device_properties, request, flag_repository, custom_property_repository, error_reporter):
        self.device_properties = device_properties
        self.flag_repository = flag_repository
        self.custom_property_repository = custom_property_repository
        self.request = request
        self.error_reporter = error_reporter

        # register to repositories
        self.flag_repository.register_flag_added_handler(self.flag_repository_flag_added)
        self.custom_property_repository.register_custom_property_added_handler(self.property_repository_property_added)

    def flag_repository_flag_added(self, variant):
        self.send_debounce()

    def property_repository_property_added(self, prop):
        self.send_debounce()

    @debounce(seconds=3)
    def send_debounce(self):
        self.send()

    def send_cdn(self, properties):
        send_result = self.send_to_cdn(properties)
        if send_result.status_code in (status_codes.codes.forbidden, status_codes.codes.not_found):
            return True

        if is_success_status_code(send_result):
            json_result = json.loads(send_result.text)
            if 'result' in json_result and json_result['result'] == 404:
                return True

            # success - every 2xx that doesn't have result=404
            self.log_send_state_succeed(ConfigurationSource.CDN)
            return False

        self.log_send_state_error(ConfigurationSource.CDN, send_result)
        return False

    def send_api(self, properties):
        send_api_result = self.send_to_api(properties)
        if is_success_status_code(send_api_result):
            self.log_send_state_succeed(ConfigurationSource.API)
            return

        # error sending to api
        self.log_send_state_error(ConfigurationSource.API, send_api_result)

    def send(self):
        source = ConfigurationSource.CDN
        try:
            properties = self.prepare_properties()
            should_try_api = True
            if not self.device_properties.rox_options.is_self_managed():
                should_try_api = self.send_cdn(properties)
            if should_try_api:
                if not self.device_properties.rox_options.is_self_managed():
                    Logging.get_logger().debug('State not exists on CDN, Trying to send to API')
                source = ConfigurationSource.API
                self.send_api(properties)

        except Exception as ex:
            self.log_send_state_exception(source, ex)

    def serialize_feature_flags(self):
        flags = []

        def by_name(flag):
            return flag['name']

        for v in self.flag_repository.get_all_flags().values():
            # regualr dictionaries are different between python versions, making sure it says the same
            f = OrderedDict()
            f['defaultValue'] = v.default_value
            f['name'] = v.name
            f['options'] = v.options
            flags.append(f)

        flags.sort(key=by_name)

        return flags

    def serialize_custom_properties(self):
        properties = []

        def by_name(flag):
            return flag['name']

        for v in self.custom_property_repository.get_all_custom_properties().values():
            # regualr dictionaries are different between python versions, making sure it says the same
            p = OrderedDict()
            p['externalType'] = v.type.external_type
            p['name'] = v.name
            p['type'] = v.type.type
            properties.append(p)

        properties.sort(key=by_name)

        return properties

    def prepare_properties(self):
        properties = self.device_properties.get_all_properties()
        properties[property_type.FEATURE_FLAGS.name] = self.serialize_feature_flags()
        properties[property_type.CUSTOM_PROPERTIES.name] = self.serialize_custom_properties()
        state_md5 = md5_generator.generate(properties, StateSender.MD5_STATE_GENERATORS)
        properties[property_type.STATE_MD5.name] = state_md5
        return properties

    def get_relative_path(self, properties):
        return '%s/%s' % (properties[property_type.APP_KEY.name], properties[property_type.STATE_MD5.name])

    def get_cdn_path(self, properties):
        return '%s/%s' % (Environment.CDN_STATE_PATH, self.get_relative_path(properties))

    def get_api_path(self, properties):
        rox_options = self.device_properties.rox_options
        if rox_options.is_self_managed():
            api_state_path = Environment.API_STATE_PATH(rox_options.self_managed_options.server_url)
        else:
            api_state_path = Environment.API_STATE_PATH()

        return '%s/%s' % (api_state_path, self.get_relative_path(properties))

    def send_to_cdn(self, properties):
        cdn_request = RequestData(self.get_cdn_path(properties), None)
        return self.request.send_get(cdn_request)

    def send_to_api(self, properties):
        query_params = {}
        for pt in StateSender.RELEVANT_API_PROPERTIES:
            if pt.name in properties:
                query_params[pt.name] = properties[pt.name]

        api_request = RequestData(self.get_api_path(properties), query_params)
        return self.request.send_post(api_request)

    def log_send_state_succeed(self, source):
        Logging.get_logger().debug('Send state succeeded. source %s' % source)

    def log_send_state_error(self, source, response):
        Logging.get_logger().debug('Failed to send state to %s. http error code: %s' % (source, response.status_code))

    def log_send_state_exception(self, source, exception):
        Logging.get_logger().error('Failed to send state with exception. source %s' % (source), exception)
        _, _, exc_traceback = sys.exc_info()
        self.error_reporter.report('Failed to send state with exception. source %s' % (source), exception, traceback.extract_tb(exc_traceback))

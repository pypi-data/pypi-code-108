from abc import abstractmethod

import sys
import traceback

from rox.core.configuration.configuration_fetched_invoker import FetcherError
from rox.core.logging.logging import Logging
from rox.core.network.configuration_result import ConfigurationSource, ConfigurationFetchResult

import json

class ConfigurationFetcherBase(object):
    def __init__(self, device_properties, request, configuration_fetched_invoker, error_reporter):
        self.device_properties = device_properties
        self.request = request
        self.configuration_fetched_invoker = configuration_fetched_invoker
        self.error_reporter = error_reporter

    def createResult(self, fetch_result, source):
        if fetch_result is None or not fetch_result.text:
            Logging.get_logger().debug('Failed to parse JSON configuration from %s - Null Or Empty' % (source))
            self.configuration_fetched_invoker.invoke_error(FetcherError.EMPTY_JSON)
            self.error_reporter.report('Failed to parse JSON configuration - Null Or Empty', ValueError('data'), traceback.extract_stack())
            return None

        try:
            json_obj = ConfigurationFetchResult(fetch_result.text, source)
        except Exception as ex:
            _, _, exc_traceback = sys.exc_info()
            Logging.get_logger().debug('Failed to parse JSON configuration from %s - Corrupted' % (source), ex)
            self.configuration_fetched_invoker.invoke_error(FetcherError.CORRUPTED_JSON)
            self.error_reporter.report('Failed to parse JSON configuration', ex, traceback.extract_tb(exc_traceback))
            return None

        return json_obj

    def write_fetch_error_to_log_and_invoke_fetch_handler(self, source, response, raise_configuration_handler=True, next_source=None):
        retry_msg = '' if next_source is None else 'Trying from %s. ' % next_source

        Logging.get_logger().debug('Failed to fetch from %s. %shttp error code: %s' % (source, retry_msg, response.status_code))

        if raise_configuration_handler:
            self.configuration_fetched_invoker.invoke_error(FetcherError.NETWORK_ERROR)

    def write_fetch_exception_to_log_and_invoke_fetch_handler(self, source, ex):
        Logging.get_logger().error('Failed to fetch configuration. Source: %s.' % (source), ex)
        _, _, exc_traceback = sys.exc_info()
        self.error_reporter.report('Failed to fetch configuration. Source: %s.' % (source), ex, traceback.extract_tb(exc_traceback))
        self.configuration_fetched_invoker.invoke_error(FetcherError.NETWORK_ERROR)

    @abstractmethod
    def fetch(self):
        pass

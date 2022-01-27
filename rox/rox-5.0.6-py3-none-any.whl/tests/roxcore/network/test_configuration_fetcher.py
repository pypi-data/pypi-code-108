import unittest

from rox.core.configuration.configuration_fetched_invoker import ConfigurationFetchedInvoker, FetcherError
from rox.core.network.configuration_fetcher import ConfigurationFetcher
from rox.core.network.configuration_result import ConfigurationSource
from rox.core.network.request import RequestData
from rox.core.logging.logging import Logging
from rox.core.consts import property_type

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

class ConfigurationFetcherTests(unittest.TestCase):
    def setUp(self):
        self.error_reporter = Mock()

        self.logger = Mock()

        self.device_props = Mock()
        self.device_props.distinct_id = 'id'
        self.device_props.get_all_properties.return_value = {
            'app_key': 'key',
            'api_version': '4.0.0',
            'distinct_id': 'id'
        }

        self.buid = Mock()
        self.buid.get_value.return_value = 'bid'
        self.buid.get_query_string_parts.return_value = {'buid': 'bid'}

        Logging.set_logger(self.logger)
        self.conf_fetch_invoker = Mock()

    def validate_cdn_request_params(self, request):
        self.assertEqual(request.url, 'https://conf.rollout.io/key/bid')
        self.assertEqual(len(request.query_params), 1)
        self.assertEqual(request.query_params['distinct_id'], 'id')

    def validate_api_request_params(self, request):
        self.assertEqual(request.url, 'https://x-api.rollout.io/device/get_configuration/key/bid')
        self.assertEqual(len(request.query_params), 5)
        self.assertEqual(request.query_params['distinct_id'], 'id')
        self.assertEqual(request.query_params['api_version'], '4.0.0')
        self.assertEqual(request.query_params['app_key'], 'key')
        self.assertEqual(request.query_params['buid'], 'bid')

    def test_will_return_cdn_data_when_successful(self):
        response = Mock()
        response.status_code = 200
        response.text = '{"a":"harti"}'

        request = Mock()
        request.send_get.return_value = response
        
        conf_fetcher = ConfigurationFetcher(self.device_props, request, self.conf_fetch_invoker, self.error_reporter, self.buid)
        result = conf_fetcher.fetch()

        args, _ = request.send_get.call_args_list[0]
        actual_request = args[0]

        self.validate_cdn_request_params(actual_request)

        self.assertEqual('harti', result.json_data['a'])
        self.assertEqual(ConfigurationSource.CDN, result.source)
        self.conf_fetch_invoker.assert_not_called()

        self.assertEqual(0, len(self.logger.debug.call_args_list))
        self.assertEqual(0, len(self.logger.error.call_args_list))

        self.error_reporter.report.assert_not_called()
        
    def test_will_return_null_when_cdn_fails_with_exception(self):

        buid = Mock()
        buid.get_value.return_value = 'bid'
        buid.get_query_string_parts.return_value = {'buid': 'bid'}

        response = Mock()
        response.status_code = 200
        response.text = '{"a":"harto"}'

        requests = {}
        def send_get(request_data):
            requests['cdn'] = request_data
            raise Exception('not found')

        request = Mock()
        request.send_get = send_get

        conf_fetcher = ConfigurationFetcher(self.device_props, request, self.conf_fetch_invoker, self.error_reporter, self.buid)
        result = conf_fetcher.fetch()

        self.validate_cdn_request_params(requests['cdn'])

        self.assertIsNone(result)
        self.conf_fetch_invoker.invoke_error.assert_called_once_with(FetcherError.NETWORK_ERROR)

        self.assertEqual(0, len(self.logger.debug.call_args_list))
        self.assertEqual(1, len(self.logger.error.call_args_list))
        args, _ = self.logger.error.call_args_list[0]
        self.assertTrue(args[0].startswith('Failed to fetch configuration'))
        self.assertTrue(isinstance(args[1], Exception))

        self.assertEqual(self.error_reporter.report.call_count, 1)

    def test_will_return_null_when_cdn_succeed_empty_response(self):
        response = Mock()
        response.status_code = 200
        response.text = ''

        requests = {}
        def send_get(request_data):
            requests['cdn'] = request_data
            return response

        request = Mock()
        request.send_get = send_get

        conf_fetcher = ConfigurationFetcher(self.device_props, request, self.conf_fetch_invoker, self.error_reporter, self.buid)
        result = conf_fetcher.fetch()

        self.validate_cdn_request_params(requests['cdn'])
        
        self.assertIsNone(result)
        self.conf_fetch_invoker.invoke_error.assert_called_once_with(FetcherError.EMPTY_JSON)

        request.send_post.assert_not_called()

        self.assertEqual(1, len(self.logger.debug.call_args_list))
        args, _ = self.logger.debug.call_args_list[0]
        self.assertEqual(1, len(args))
        self.assertTrue(args[0].startswith('Failed to parse JSON configuration from CDN - Null Or Empty'))

        self.assertEqual(self.error_reporter.report.call_count, 1)

    def test_will_return_null_when_cdn_succeed_corrupted_response(self):
        response = Mock()
        response.status_code = 200
        response.text = '{pah'

        requests = {}
        def send_get(request_data):
            requests['cdn'] = request_data
            return response

        request = Mock()
        request.send_get = send_get

        conf_fetcher = ConfigurationFetcher(self.device_props, request, self.conf_fetch_invoker, self.error_reporter, self.buid)
        result = conf_fetcher.fetch()

        self.validate_cdn_request_params(requests['cdn'])
        
        self.assertIsNone(result)
        self.conf_fetch_invoker.invoke_error.assert_called_once_with(FetcherError.CORRUPTED_JSON)

        request.send_post.assert_not_called()

        self.assertEqual(1, len(self.logger.debug.call_args_list))
        args, _ = self.logger.debug.call_args_list[0]
        self.assertTrue(args[0].startswith('Failed to parse JSON configuration from CDN - Corrupted'))
        self.assertTrue(isinstance(args[1], Exception))

        self.assertEqual(self.error_reporter.report.call_count, 1)

    def test_will_return_null_when_cdn_fails_404_api_with_exception(self):
        response = Mock()
        response.status_code = 404

        requests = {}
        def send_get(request_data):
            requests['cdn'] = request_data
            return response

        def send_post(request_data):
            requests['api'] = request_data
            raise Exception('not found')

        request = Mock()
        request.send_get = send_get
        request.send_post = send_post

        conf_fetcher = ConfigurationFetcher(self.device_props, request, self.conf_fetch_invoker, self.error_reporter, self.buid)
        result = conf_fetcher.fetch()

        self.validate_cdn_request_params(requests['cdn'])
        self.validate_api_request_params(requests['api'])

        self.assertIsNone(result)
        self.conf_fetch_invoker.invoke_error.assert_called_once_with(FetcherError.NETWORK_ERROR)

        self.assertEqual(1, len(self.logger.debug.call_args_list))
        log_first_args, _ = self.logger.debug.call_args_list[0]
        self.assertTrue(log_first_args[0].startswith('Failed to fetch from CDN'))
        self.assertEqual(1, len(self.logger.error.call_args_list))
        log_second_args, _ = self.logger.error.call_args_list[0]
        self.assertTrue(log_second_args[0].startswith('Failed to fetch configuration'))

        self.assertEqual(self.error_reporter.report.call_count, 1)

    def test_will_return_api_data_when_cdn_fails_404_api_ok(self):
        response = Mock()
        response.status_code = 200
        response.text = '{"a":"harto"}'

        response_cdn = Mock()
        response_cdn.status_code = 404

        requests = {}

        def send_get(request_data):
            requests['cdn'] = request_data
            return response_cdn

        def send_post(request_data):
            requests['api'] = request_data
            return response

        request = Mock()
        request.send_get = send_get
        request.send_post = send_post

        conf_fetcher = ConfigurationFetcher(self.device_props, request, self.conf_fetch_invoker, self.error_reporter, self.buid)
        result = conf_fetcher.fetch()

        self.validate_cdn_request_params(requests['cdn'])
        self.validate_api_request_params(requests['api'])

        self.assertEqual('harto', result.json_data['a'])
        self.assertEqual(ConfigurationSource.API, result.source)
        self.conf_fetch_invoker.invoke.assert_not_called()
        self.conf_fetch_invoker.invoke_error.assert_not_called()


        self.assertEqual(1, len(self.logger.debug.call_args_list))
        log_first_args, _ = self.logger.debug.call_args_list[0]
        self.assertTrue(log_first_args[0].startswith('Failed to fetch from CDN'))

        self.error_reporter.report.assert_not_called()

    def test_will_return_api_data_when_cdn_succeed_result_404_api_ok(self):
        response = Mock()
        response.status_code = 200
        response.text = '{"a":"harto"}'

        response_cdn = Mock()
        response_cdn.status_code = 200
        response_cdn.text = '{"result":404}'
        
        requests = {}

        def send_get(request_data):
            requests['cdn'] = request_data
            return response_cdn

        def send_post(request_data):
            requests['api'] = request_data
            return response

        request = Mock()
        request.send_get = send_get
        request.send_post = send_post

        conf_fetcher = ConfigurationFetcher(self.device_props, request, self.conf_fetch_invoker, self.error_reporter, self.buid)
        result = conf_fetcher.fetch()

        self.validate_cdn_request_params(requests['cdn'])
        self.validate_api_request_params(requests['api'])

        self.assertEqual('harto', result.json_data['a'])
        self.assertEqual(ConfigurationSource.API, result.source)
        self.conf_fetch_invoker.invoke.assert_not_called()
        self.conf_fetch_invoker.invoke_error.assert_not_called()


        self.assertEqual(1, len(self.logger.debug.call_args_list))
        log_first_args, _ = self.logger.debug.call_args_list[0]
        self.assertTrue(log_first_args[0].startswith('Failed to fetch from CDN'))

        self.error_reporter.report.assert_not_called()

    def test_will_return_null_data_when_both_not_found(self):
        response = Mock()
        response.status_code = 404

        response_cdn = Mock()
        response_cdn.status_code = 404

        requests = {}

        def send_get(request_data):
            requests['cdn'] = request_data
            return response_cdn

        def send_post(request_data):
            requests['api'] = request_data
            return response

        request = Mock()
        request.send_get = send_get
        request.send_post = send_post

        conf_fetcher = ConfigurationFetcher(self.device_props, request, self.conf_fetch_invoker, self.error_reporter, self.buid)
        result = conf_fetcher.fetch()

        self.validate_cdn_request_params(requests['cdn'])
        self.validate_api_request_params(requests['api'])

        self.assertIsNone(result)
        self.conf_fetch_invoker.invoke_error.assert_called_once_with(FetcherError.NETWORK_ERROR)

        self.assertEqual(2, len(self.logger.debug.call_args_list))
        log_first_args, _ = self.logger.debug.call_args_list[0]
        self.assertTrue(log_first_args[0].startswith('Failed to fetch from CDN'))
        log_second_args, _ = self.logger.debug.call_args_list[1]
        self.assertTrue(log_second_args[0].startswith('Failed to fetch from API'))

        self.error_reporter.report.assert_not_called()

    def test_prepare_configurations_props(self):
        device_props = Mock()
        device_props.distinct_id = 'id'
        device_props.get_all_properties.return_value = {
            property_type.APP_KEY.name: 'dvalue1',
            'dkey2': 'dvalue2'
        }

        buid = Mock()
        buid.get_value.return_value = 'bid'
        buid.get_query_string_parts.return_value = {
            property_type.BUID.name: 'value1',
            'key2': 'value2'
        }

        conf_fetcher = ConfigurationFetcher(device_props, None, self.conf_fetch_invoker, self.error_reporter, buid)
        params = conf_fetcher.prepare_properties()

        self.assertEqual(len(params), 5)
        self.assertEqual(params[property_type.APP_KEY.name], 'dvalue1')
        self.assertEqual(params['dkey2'], 'dvalue2')
        self.assertEqual(params[property_type.CACHE_MISS_RELATIVE_URL.name], '%s/%s' % (params[property_type.APP_KEY.name], params[property_type.BUID.name]))
        self.assertEqual(params[property_type.BUID.name], 'value1')
        self.assertEqual(params['key2'], 'value2')


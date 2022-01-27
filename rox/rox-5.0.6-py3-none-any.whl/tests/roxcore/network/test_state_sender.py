import unittest

from rox.core.network.state_sender import StateSender
from rox.core.network.request import RequestData
from rox.core.logging.logging import Logging
from rox.core.repositories.flag_repository import FlagRepository
from rox.core.repositories.custom_property_repository import CustomPropertyRepository
from rox.core.consts import property_type
from rox.core.entities.flag import Flag
from rox.core.custom_properties.custom_property import CustomProperty
from rox.core.custom_properties.custom_property_type import CustomPropertyType
from rox.server.rox_options import RoxOptions

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

class StateSenderTests(unittest.TestCase):
    def setUp(self):
        self.error_reporter = Mock()

        self.logger = Mock()

        self.device_props = Mock(
            distinct_id='id',
            rox_options=RoxOptions()
        )
        self.device_props.get_all_properties.return_value = {
            'app_key': 'key',
            'api_version': '4.0.0',
            'distinct_id': 'id',
            'platform': 'plat',
            'devModeSecret': 'hush',
            'ignoreThis': 'please'
        }

        Logging.set_logger(self.logger)
        self.fr = FlagRepository()
        self.cpr = CustomPropertyRepository()

    def validate_cdn_request_params(self, request):
        self.assertEqual(request.url, 'https://statestore.rollout.io/key/9E54FB56A9CE9BF1210460DA9EA8221A')

    def validate_empty_list(self, obj):
        self.assertTrue(type(obj) == list)
        self.assertEqual(0, len(obj))

    def compareListWithDictionaries(self, list1, list2):
        return self.assertEqual(str(list1), str(list2))

    def validate_api_request_params(self, request, key=None, md5=None, flags=None, props=None):
        if key is None:
            key = 'key'

        if md5 is None:
            md5 = '9E54FB56A9CE9BF1210460DA9EA8221A'
        self.assertEqual(request.url, 'https://x-api.rollout.io/device/update_state_store/%s/%s' % (key, md5))
        self.assertEqual(len(request.query_params), 4)
        self.assertEqual(request.query_params[property_type.PLATFORM.name], 'plat')
        self.assertEqual(request.query_params[property_type.DEV_MODE_SECRET.name], 'hush')

        if (flags is None):
            self.validate_empty_list(request.query_params[property_type.FEATURE_FLAGS.name])
        else:
            self.compareListWithDictionaries(request.query_params[property_type.FEATURE_FLAGS.name], flags)

        if (props is None):
            self.validate_empty_list(request.query_params[property_type.CUSTOM_PROPERTIES.name])
        else:
            self.compareListWithDictionaries(request.query_params[property_type.CUSTOM_PROPERTIES.name], props)

    def test_send_state_to_cdn_successful(self):
        response = Mock()
        response.status_code = 200
        response.text = '{"result":200}'

        request = Mock()
        request.send_get.return_value = response

        state_sender = StateSender(self.device_props, request, self.fr, self.cpr, self.error_reporter)
        state_sender.send()

        self.assertEqual(request.send_get.call_count, 1)
        args, _ = request.send_get.call_args_list[0]
        actual_request = args[0]

        self.validate_cdn_request_params(actual_request)

        self.assertEqual(1, len(self.logger.debug.call_args_list))
        args, _ = self.logger.debug.call_args_list[0]
        self.assertEqual(args[0], 'Send state succeeded. source CDN')
        self.assertEqual(0, len(self.logger.error.call_args_list))

        self.error_reporter.report.assert_not_called()

    def test_send_state_md5_changes_on_added_flag(self):
        response = Mock()
        response.status_code = 200
        response.text = '{"result":200}'

        request = Mock()
        request.send_get.return_value = response

        state_sender = StateSender(self.device_props, request, self.fr, self.cpr, self.error_reporter)
        self.fr.add_flag(Flag(), 'f1')
        state_sender.send()

        self.assertEqual(request.send_get.call_count, 1)
        args, _ = request.send_get.call_args_list[0]
        actual_request = args[0]
        self.assertEqual(actual_request.url, 'https://statestore.rollout.io/key/1F19A52D0ACE940A78CB7B3143F84AD6')

        self.fr.add_flag(Flag(), 'f2')
        state_sender.send()

        self.assertEqual(2, len(request.send_get.call_args_list))
        args, _ = request.send_get.call_args_list[1]
        second_request = args[0]
        self.assertEqual(second_request.url, 'https://statestore.rollout.io/key/285E249B571EB2E728EA59EF15883230')

    def test_send_state_md5_same_flag_order_ignored(self):
        response = Mock()
        response.status_code = 200
        response.text = '{"result":200}'

        request = Mock()
        request.send_get.return_value = response

        state_sender = StateSender(self.device_props, request, self.fr, self.cpr, self.error_reporter)
        self.fr.add_flag(Flag(), 'f1')
        self.fr.add_flag(Flag(), 'f2')
        state_sender.send()

        self.assertEqual(request.send_get.call_count, 1)
        args, _ = request.send_get.call_args_list[0]
        actual_request = args[0]
        self.assertEqual(actual_request.url, 'https://statestore.rollout.io/key/285E249B571EB2E728EA59EF15883230')

        cpr2 = CustomPropertyRepository()
        fr2 = FlagRepository()
        state_sender = StateSender(self.device_props, request, fr2, cpr2, self.error_reporter)
        fr2.add_flag(Flag(), 'f1')
        fr2.add_flag(Flag(), 'f2')

        state_sender.send()

        self.assertEqual(2, len(request.send_get.call_args_list))
        args, _ = request.send_get.call_args_list[1]
        second_request = args[0]
        self.assertEqual(second_request.url, 'https://statestore.rollout.io/key/285E249B571EB2E728EA59EF15883230')

    def test_send_state_md5_changes_on_added_custom_property(self):
        response = Mock()
        response.status_code = 200
        response.text = '{"result":200}'

        request = Mock()
        request.send_get.return_value = response

        state_sender = StateSender(self.device_props, request, self.fr, self.cpr, self.error_reporter)
        self.cpr.add_custom_property(CustomProperty('cp1', CustomPropertyType.STRING, 'val'))
        state_sender.send()

        self.assertEqual(request.send_get.call_count, 1)
        args, _ = request.send_get.call_args_list[0]
        actual_request = args[0]
        self.assertEqual(actual_request.url, 'https://statestore.rollout.io/key/5211008CC445D8F90808F6323BA26FA8')

        self.cpr.add_custom_property(CustomProperty('cp2', CustomPropertyType.BOOL, 'val2'))
        state_sender.send()

        self.assertEqual(2, len(request.send_get.call_args_list))
        args, _ = request.send_get.call_args_list[1]
        second_request = args[0]
        self.assertEqual(second_request.url, 'https://statestore.rollout.io/key/27057E0BFB02E237D7ED9890C7F43FA6')

    def test_send_state_md5_same_custom_property_order_ignored(self):
        response = Mock()
        response.status_code = 200
        response.text = '{"result":200}'

        request = Mock()
        request.send_get.return_value = response

        state_sender = StateSender(self.device_props, request, self.fr, self.cpr, self.error_reporter)
        self.cpr.add_custom_property(CustomProperty('cp1', CustomPropertyType.STRING, 'val'))
        self.cpr.add_custom_property(CustomProperty('cp2', CustomPropertyType.BOOL, 'val2'))
        state_sender.send()

        self.assertEqual(request.send_get.call_count, 1)

        args, _ = request.send_get.call_args_list[0]
        actual_request = args[0]
        self.assertEqual(actual_request.url, 'https://statestore.rollout.io/key/27057E0BFB02E237D7ED9890C7F43FA6')

        cpr2 = CustomPropertyRepository()
        fr2 = FlagRepository()
        state_sender = StateSender(self.device_props, request, fr2, cpr2, self.error_reporter)
        cpr2.add_custom_property(CustomProperty('cp2', CustomPropertyType.BOOL, 'val2'))
        cpr2.add_custom_property(CustomProperty('cp1', CustomPropertyType.STRING, 'val'))

        state_sender.send()

        self.assertEqual(2, len(request.send_get.call_args_list))
        args, _ = request.send_get.call_args_list[1]
        second_request = args[0]
        self.assertEqual(second_request.url, 'https://statestore.rollout.io/key/27057E0BFB02E237D7ED9890C7F43FA6')

    def test_send_state_to_cdn_exception(self):
        requests = {}
        def send_get(request_data):
            requests['cdn'] = request_data
            raise Exception

        request = Mock()
        request.send_get = send_get

        state_sender = StateSender(self.device_props, request, self.fr, self.cpr, self.error_reporter)
        state_sender.send()

        self.validate_cdn_request_params(requests['cdn'])

        self.assertEqual(0, len(self.logger.debug.call_args_list))
        self.assertEqual(1, len(self.logger.error.call_args_list))
        args, _ = self.logger.error.call_args_list[0]
        self.assertEqual(2, len(args))
        self.assertEqual(args[0], 'Failed to send state with exception. source CDN')

        self.assertEqual(self.error_reporter.report.call_count, 1)

    def test_send_state_cdn_succeed_corrupted_response(self):
        response = Mock()
        response.status_code = 200
        response.text = '{fdf'

        requests = {}
        def send_get(request_data):
            requests['cdn'] = request_data
            return response

        request = Mock()
        request.send_get = send_get

        state_sender = StateSender(self.device_props, request, self.fr, self.cpr, self.error_reporter)
        state_sender.send()

        self.validate_cdn_request_params(requests['cdn'])

        self.assertEqual(0, len(self.logger.debug.call_args_list))
        self.assertEqual(1, len(self.logger.error.call_args_list))
        args, _ = self.logger.error.call_args_list[0]
        self.assertEqual(2, len(args))
        self.assertEqual(args[0], 'Failed to send state with exception. source CDN')

        self.assertEqual(self.error_reporter.report.call_count, 1)

    def test_send_state_cdn_succeed_empty_response(self):
        response = Mock()
        response.status_code = 200
        response.text = ''

        requests = {}
        def send_get(request_data):
            requests['cdn'] = request_data
            return response

        request = Mock()
        request.send_get = send_get

        state_sender = StateSender(self.device_props, request, self.fr, self.cpr, self.error_reporter)
        state_sender.send()

        self.validate_cdn_request_params(requests['cdn'])

        self.assertEqual(0, len(self.logger.debug.call_args_list))
        self.assertEqual(1, len(self.logger.error.call_args_list))
        args, _ = self.logger.error.call_args_list[0]
        self.assertEqual(2, len(args))
        self.assertEqual(args[0], 'Failed to send state with exception. source CDN')

        self.assertEqual(self.error_reporter.report.call_count, 1)

    def test_send_state_cdn_fails_404_api_with_exception(self):
        response = Mock()
        response.status_code = 404

        requests = {}
        def send_get(request_data):
            requests['cdn'] = request_data
            return response

        def send_post(request_data):
            requests['api'] = request_data
            raise Exception

        request = Mock()
        request.send_get = send_get
        request.send_post = send_post

        state_sender = StateSender(self.device_props, request, self.fr, self.cpr, self.error_reporter)

        self.fr.add_flag(Flag(), 'f1')
        self.cpr.add_custom_property(CustomProperty('cp1', CustomPropertyType.STRING, 'val'))

        state_sender.send()

        self.assertEqual(requests['cdn'].url, 'https://statestore.rollout.io/key/FCEBC71CC396E817C4F31F9830D3CBCE')

        self.assertEqual(1, len(self.logger.debug.call_args_list))
        args, _ = self.logger.debug.call_args_list[0]
        self.assertEqual(1, len(args))
        self.assertEqual(args[0], 'State not exists on CDN, Trying to send to API')

        sent_props = "[OrderedDict([('externalType', 'String'), ('name', 'cp1'), ('type', 'string')])]"
        sent_flags = "[OrderedDict([('defaultValue', 'false'), ('name', 'f1'), ('options', ['false', 'true'])])]"
        self.validate_api_request_params(requests['api'], None, 'FCEBC71CC396E817C4F31F9830D3CBCE', sent_flags, sent_props)

        self.assertEqual(1, len(self.logger.error.call_args_list))
        args, _ = self.logger.error.call_args_list[0]
        self.assertEqual(2, len(args))
        self.assertEqual(args[0], 'Failed to send state with exception. source API')
        self.assertTrue(isinstance(args[1], Exception))

        self.assertEqual(self.error_reporter.report.call_count, 1)

    def test_will_return_api_data_when_cdn_fails_404_api_ok(self):
        response_cdn = Mock()
        response_cdn.status_code = 404

        response = Mock()
        response.status_code = 200
        response.text = '{"a":"harto"}'

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

        state_sender = StateSender(self.device_props, request, self.fr, self.cpr, self.error_reporter)

        state_sender.send()

        self.assertEqual(requests['cdn'].url, 'https://statestore.rollout.io/key/9E54FB56A9CE9BF1210460DA9EA8221A')

        self.assertEqual(2, len(self.logger.debug.call_args_list))
        args, _ = self.logger.debug.call_args_list[0]
        self.assertEqual(1, len(args))
        self.assertEqual(args[0], 'State not exists on CDN, Trying to send to API')

        args, _ = self.logger.debug.call_args_list[1]
        self.assertEqual(1, len(args))
        self.assertEqual(args[0], 'Send state succeeded. source API')

        self.validate_api_request_params(requests['api'], None, '9E54FB56A9CE9BF1210460DA9EA8221A')

        self.assertEqual(0, len(self.logger.error.call_args_list))

        self.error_reporter.report.assert_not_called()

    def test_will_return_api_data_when_cdn_succeed_result_404_api_ok(self):
        response_cdn = Mock()
        response_cdn.status_code = 200
        response_cdn.text = '{"result":404}'

        response = Mock()
        response.status_code = 200
        response.text = '{"a":"harto"}'

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

        state_sender = StateSender(self.device_props, request, self.fr, self.cpr, self.error_reporter)

        state_sender.send()

        self.assertEqual(requests['cdn'].url, 'https://statestore.rollout.io/key/9E54FB56A9CE9BF1210460DA9EA8221A')

        self.assertEqual(2, len(self.logger.debug.call_args_list))
        args, _ = self.logger.debug.call_args_list[0]
        self.assertEqual(1, len(args))
        self.assertEqual(args[0], 'State not exists on CDN, Trying to send to API')

        args, _ = self.logger.debug.call_args_list[1]
        self.assertEqual(1, len(args))
        self.assertEqual(args[0], 'Send state succeeded. source API')

        self.validate_api_request_params(requests['api'], None, '9E54FB56A9CE9BF1210460DA9EA8221A')

        self.assertEqual(0, len(self.logger.error.call_args_list))

        self.error_reporter.report.assert_not_called()

    def test_will_return_null_data_when_both_not_found(self):
        response_cdn = Mock()
        response_cdn.status_code = 200
        response_cdn.text = '{"result":404}'

        response = Mock()
        response.status_code = 404

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

        state_sender = StateSender(self.device_props, request, self.fr, self.cpr, self.error_reporter)

        state_sender.send()

        self.assertEqual(requests['cdn'].url, 'https://statestore.rollout.io/key/9E54FB56A9CE9BF1210460DA9EA8221A')

        self.assertEqual(2, len(self.logger.debug.call_args_list))
        args, _ = self.logger.debug.call_args_list[0]
        self.assertEqual(1, len(args))
        self.assertEqual(args[0], 'State not exists on CDN, Trying to send to API')

        args, _ = self.logger.debug.call_args_list[1]
        self.assertEqual(1, len(args))
        self.assertEqual(args[0], 'Failed to send state to API. http error code: 404')

        self.validate_api_request_params(requests['api'], None, '9E54FB56A9CE9BF1210460DA9EA8221A')

        self.assertEqual(0, len(self.logger.error.call_args_list))

        self.error_reporter.report.assert_not_called()

    # repositories order (flags, custom_property) might be checked in this method, but already checking it on the request above, so...
    def test_prepare_send_state_props(self):
        device_props = Mock()
        device_props.distinct_id = 'id'
        device_props.get_all_properties.return_value = {
          property_type.APP_KEY.name: 'app',
          property_type.PLATFORM.name: 'pp',
          property_type.CUSTOM_PROPERTIES.name: 'cp',
          property_type.FEATURE_FLAGS.name: 'ff',
          property_type.DEV_MODE_SECRET.name: 'dv',
          'yetAnother': '1'
        }
        request = Mock()

        state_sender = StateSender(device_props, request, self.fr, self.cpr, self.error_reporter)

        params = state_sender.prepare_properties()

        self.assertEqual(len(params), 7) # all device props + md5
        self.assertEqual(params[property_type.APP_KEY.name], 'app')
        self.assertEqual(params[property_type.PLATFORM.name], 'pp')
        self.assertEqual(str(params[property_type.CUSTOM_PROPERTIES.name]), '[]')
        self.assertEqual(str(params[property_type.FEATURE_FLAGS.name]), '[]')
        self.assertEqual(params[property_type.DEV_MODE_SECRET.name], 'dv')
        self.assertEqual(params['yetAnother'], '1')
        self.assertEqual(params[property_type.STATE_MD5.name], 'BF517CB710F287766E69703460C69850')

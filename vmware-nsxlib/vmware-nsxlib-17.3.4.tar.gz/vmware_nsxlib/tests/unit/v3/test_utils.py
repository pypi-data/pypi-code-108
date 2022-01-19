# Copyright (c) 2015 OpenStack Foundation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import mock

from vmware_nsxlib.tests.unit.v3 import nsxlib_testcase
from vmware_nsxlib.v3 import exceptions
from vmware_nsxlib.v3 import nsx_constants
from vmware_nsxlib.v3 import utils


class TestNsxV3Utils(nsxlib_testcase.NsxClientTestCase):

    def setUp(self, *args, **kwargs):
        super(TestNsxV3Utils, self).setUp(with_mocks=True)

    def test_build_v3_tags_payload(self):
        result = self.nsxlib.build_v3_tags_payload(
            {'id': 'fake_id',
             'project_id': 'fake_proj_id'},
            resource_type='os-net-id',
            project_name='fake_proj_name')
        expected = [{'scope': 'os-net-id', 'tag': 'fake_id'},
                    {'scope': 'os-project-id', 'tag': 'fake_proj_id'},
                    {'scope': 'os-project-name', 'tag': 'fake_proj_name'},
                    {'scope': 'os-api-version',
                     'tag': nsxlib_testcase.PLUGIN_VER}]
        self.assertEqual(expected, result)

    def test_build_v3_tags_payload_internal(self):
        result = self.nsxlib.build_v3_tags_payload(
            {'id': 'fake_id',
             'project_id': 'fake_proj_id'},
            resource_type='os-net-id',
            project_name=None)
        expected = [{'scope': 'os-net-id', 'tag': 'fake_id'},
                    {'scope': 'os-project-id', 'tag': 'fake_proj_id'},
                    {'scope': 'os-project-name',
                     'tag': nsxlib_testcase.PLUGIN_TAG},
                    {'scope': 'os-api-version',
                     'tag': nsxlib_testcase.PLUGIN_VER}]
        self.assertEqual(expected, result)

    def test_build_v3_tags_payload_invalid_length(self):
        self.assertRaises(exceptions.NsxLibInvalidInput,
                          self.nsxlib.build_v3_tags_payload,
                          {'id': 'fake_id',
                           'project_id': 'fake_proj_id'},
                          resource_type='os-longer-maldini-rocks-id',
                          project_name='fake')

    def test_build_v3_api_version_tag(self):
        result = self.nsxlib.build_v3_api_version_tag()
        expected = [{'scope': nsxlib_testcase.PLUGIN_SCOPE,
                     'tag': nsxlib_testcase.PLUGIN_TAG},
                    {'scope': 'os-api-version',
                     'tag': nsxlib_testcase.PLUGIN_VER}]
        self.assertEqual(expected, result)

    def test_build_v3_api_version_project_tag(self):
        proj = 'project_x'
        result = self.nsxlib.build_v3_api_version_project_tag(proj)
        expected = [{'scope': nsxlib_testcase.PLUGIN_SCOPE,
                     'tag': nsxlib_testcase.PLUGIN_TAG},
                    {'scope': 'os-api-version',
                     'tag': nsxlib_testcase.PLUGIN_VER},
                    {'scope': 'os-project-name',
                     'tag': proj}]
        self.assertEqual(expected, result)

    def test_build_v3_api_version_project_id_tag(self):
        proj = 'project_x'
        proj_id = 'project_id'
        result = self.nsxlib.build_v3_api_version_project_tag(
            proj, project_id=proj_id)
        expected = [{'scope': nsxlib_testcase.PLUGIN_SCOPE,
                     'tag': nsxlib_testcase.PLUGIN_TAG},
                    {'scope': 'os-api-version',
                     'tag': nsxlib_testcase.PLUGIN_VER},
                    {'scope': 'os-project-name',
                     'tag': proj},
                    {'scope': 'os-project-id',
                     'tag': proj_id}]
        self.assertEqual(expected, result)

    def test_is_internal_resource(self):
        project_tag = self.nsxlib.build_v3_tags_payload(
            {'id': 'fake_id',
             'project_id': 'fake_proj_id'},
            resource_type='os-net-id',
            project_name=None)
        internal_tag = self.nsxlib.build_v3_api_version_tag()

        expect_false = self.nsxlib.is_internal_resource({'tags': project_tag})
        self.assertFalse(expect_false)

        expect_true = self.nsxlib.is_internal_resource({'tags': internal_tag})
        self.assertTrue(expect_true)

    def test_get_name_and_uuid(self):
        uuid = 'afc40f8a-4967-477e-a17a-9d560d1786c7'
        suffix = '_afc40...786c7'
        expected = 'maldini%s' % suffix
        short_name = utils.get_name_and_uuid('maldini', uuid)
        self.assertEqual(expected, short_name)

        name = 'X' * 255
        expected = '%s%s' % ('X' * (80 - len(suffix)), suffix)
        short_name = utils.get_name_and_uuid(name, uuid)
        self.assertEqual(expected, short_name)

    def test_get_name_short_uuid(self):
        uuid = 'afc40f8a-4967-477e-a17a-9d560d1786c7'
        suffix = '_afc40...786c7'
        short_uuid = utils.get_name_short_uuid(uuid)
        self.assertEqual(suffix, short_uuid)

    def test_build_v3_tags_max_length_payload(self):
        result = self.nsxlib.build_v3_tags_payload(
            {'id': 'X' * 255,
             'project_id': 'X' * 255},
            resource_type='os-net-id',
            project_name='X' * 255)
        expected = [{'scope': 'os-net-id', 'tag': 'X' * 40},
                    {'scope': 'os-project-id', 'tag': 'X' * 40},
                    {'scope': 'os-project-name', 'tag': 'X' * 40},
                    {'scope': 'os-api-version',
                     'tag': nsxlib_testcase.PLUGIN_VER}]
        self.assertEqual(expected, result)

    def test_add_v3_tag(self):
        result = utils.add_v3_tag([], 'fake-scope', 'fake-tag')
        expected = [{'scope': 'fake-scope', 'tag': 'fake-tag'}]
        self.assertEqual(expected, result)

    def test_add_v3_tag_max_length_payload(self):
        result = utils.add_v3_tag([], 'fake-scope', 'X' * 255)
        expected = [{'scope': 'fake-scope', 'tag': 'X' * 40}]
        self.assertEqual(expected, result)

    def test_add_v3_tag_invalid_scope_length(self):
        self.assertRaises(exceptions.NsxLibInvalidInput,
                          utils.add_v3_tag,
                          [],
                          'fake-scope-name-is-far-too-long',
                          'fake-tag')

    def test_update_v3_tags_addition(self):
        tags = [{'scope': 'os-net-id', 'tag': 'X' * 40},
                {'scope': 'os-project-id', 'tag': 'Y' * 40},
                {'scope': 'os-project-name', 'tag': 'Z' * 40},
                {'scope': 'os-api-version',
                 'tag': nsxlib_testcase.PLUGIN_VER}]
        resources = [{'scope': 'os-instance-uuid',
                      'tag': 'A' * 40}]
        tags = utils.update_v3_tags(tags, resources)
        expected = [{'scope': 'os-net-id', 'tag': 'X' * 40},
                    {'scope': 'os-project-id', 'tag': 'Y' * 40},
                    {'scope': 'os-project-name', 'tag': 'Z' * 40},
                    {'scope': 'os-api-version',
                     'tag': nsxlib_testcase.PLUGIN_VER},
                    {'scope': 'os-instance-uuid',
                     'tag': 'A' * 40}]
        self.assertEqual(sorted(expected, key=lambda x: x.get('tag')),
                         sorted(tags, key=lambda x: x.get('tag')))

    def test_update_v3_tags_removal(self):
        tags = [{'scope': 'os-net-id', 'tag': 'X' * 40},
                {'scope': 'os-project-id', 'tag': 'Y' * 40},
                {'scope': 'os-project-name', 'tag': 'Z' * 40},
                {'scope': 'os-api-version',
                 'tag': nsxlib_testcase.PLUGIN_VER}]
        resources = [{'scope': 'os-net-id',
                      'tag': ''}]
        tags = utils.update_v3_tags(tags, resources)
        expected = [{'scope': 'os-project-id', 'tag': 'Y' * 40},
                    {'scope': 'os-project-name', 'tag': 'Z' * 40},
                    {'scope': 'os-api-version',
                     'tag': nsxlib_testcase.PLUGIN_VER}]
        self.assertEqual(sorted(expected, key=lambda x: x.get('tag')),
                         sorted(tags, key=lambda x: x.get('tag')))

    def test_update_v3_tags_update(self):
        tags = [{'scope': 'os-net-id', 'tag': 'X' * 40},
                {'scope': 'os-project-id', 'tag': 'Y' * 40},
                {'scope': 'os-project-name', 'tag': 'Z' * 40},
                {'scope': 'os-api-version',
                 'tag': nsxlib_testcase.PLUGIN_VER}]
        resources = [{'scope': 'os-project-id',
                      'tag': 'A' * 40}]
        tags = utils.update_v3_tags(tags, resources)
        expected = [{'scope': 'os-net-id', 'tag': 'X' * 40},
                    {'scope': 'os-project-id', 'tag': 'A' * 40},
                    {'scope': 'os-project-name', 'tag': 'Z' * 40},
                    {'scope': 'os-api-version',
                     'tag': nsxlib_testcase.PLUGIN_VER}]
        self.assertEqual(sorted(expected, key=lambda x: x.get('tag')),
                         sorted(tags, key=lambda x: x.get('tag')))

    def test_update_v3_tags_repetitive_scopes(self):
        tags = [{'scope': 'os-net-id', 'tag': 'X' * 40},
                {'scope': 'os-project-id', 'tag': 'Y' * 40},
                {'scope': 'os-project-name', 'tag': 'Z' * 40},
                {'scope': 'os-security-group', 'tag': 'SG1'},
                {'scope': 'os-security-group', 'tag': 'SG2'}]
        tags_update = [{'scope': 'os-security-group', 'tag': 'SG3'},
                       {'scope': 'os-security-group', 'tag': 'SG4'}]
        tags = utils.update_v3_tags(tags, tags_update)
        expected = [{'scope': 'os-net-id', 'tag': 'X' * 40},
                    {'scope': 'os-project-id', 'tag': 'Y' * 40},
                    {'scope': 'os-project-name', 'tag': 'Z' * 40},
                    {'scope': 'os-security-group', 'tag': 'SG3'},
                    {'scope': 'os-security-group', 'tag': 'SG4'}]
        self.assertEqual(sorted(expected, key=lambda x: x.get('tag')),
                         sorted(tags, key=lambda x: x.get('tag')))

    def test_update_v3_tags_repetitive_scopes_remove(self):
        tags = [{'scope': 'os-net-id', 'tag': 'X' * 40},
                {'scope': 'os-project-id', 'tag': 'Y' * 40},
                {'scope': 'os-project-name', 'tag': 'Z' * 40},
                {'scope': 'os-security-group', 'tag': 'SG1'},
                {'scope': 'os-security-group', 'tag': 'SG2'}]
        tags_update = [{'scope': 'os-security-group', 'tag': None}]
        tags = utils.update_v3_tags(tags, tags_update)
        expected = [{'scope': 'os-net-id', 'tag': 'X' * 40},
                    {'scope': 'os-project-id', 'tag': 'Y' * 40},
                    {'scope': 'os-project-name', 'tag': 'Z' * 40}]
        self.assertEqual(sorted(expected, key=lambda x: x.get('tag')),
                         sorted(tags, key=lambda x: x.get('tag')))

    def test_build_extra_args_positive(self):
        extra_args = ['fall_count', 'interval', 'monitor_port',
                      'request_body', 'request_method', 'request_url',
                      'request_version', 'response_body',
                      'response_status_codes', 'rise_count', 'timeout']
        body = {'display_name': 'httpmonitor1',
                'description': 'my http monitor'}
        expected = {'display_name': 'httpmonitor1',
                    'description': 'my http monitor',
                    'interval': 5,
                    'rise_count': 3,
                    'fall_count': 3}
        resp = utils.build_extra_args(body, extra_args, interval=5,
                                      rise_count=3, fall_count=3)
        self.assertEqual(resp, expected)

    def test_build_extra_args_negative(self):
        extra_args = ['cookie_domain', 'cookie_fallback', 'cookie_garble',
                      'cookie_mode', 'cookie_name', 'cookie_path',
                      'cookie_time']
        body = {'display_name': 'persistenceprofile1',
                'description': 'my persistence profile',
                'resource_type': 'LoadBalancerCookiePersistenceProfile'}
        expected = {'display_name': 'persistenceprofile1',
                    'description': 'my persistence profile',
                    'resource_type': 'LoadBalancerCookiePersistenceProfile',
                    'cookie_mode': 'INSERT',
                    'cookie_name': 'ABC',
                    'cookie_fallback': True}
        resp = utils.build_extra_args(body, extra_args, cookie_mode='INSERT',
                                      cookie_name='ABC', cookie_fallback=True,
                                      bogus='bogus')
        self.assertEqual(resp, expected)

    def test_retry(self):
        max_retries = 5
        total_count = {'val': 0}

        @utils.retry_upon_exception(exceptions.NsxLibInvalidInput,
                                    max_attempts=max_retries)
        def func_to_fail(x):
            total_count['val'] = total_count['val'] + 1
            raise exceptions.NsxLibInvalidInput(error_message='foo')

        self.assertRaises(exceptions.NsxLibInvalidInput, func_to_fail, 99)
        self.assertEqual(max_retries, total_count['val'])

    def test_retry_random(self):
        max_retries = 5
        total_count = {'val': 0}

        @utils.retry_random_upon_exception(exceptions.NsxLibInvalidInput,
                                           max_attempts=max_retries)
        def func_to_fail(x):
            total_count['val'] = total_count['val'] + 1
            raise exceptions.NsxLibInvalidInput(error_message='foo')

        self.assertRaises(exceptions.NsxLibInvalidInput, func_to_fail, 99)
        self.assertEqual(max_retries, total_count['val'])

    def test_retry_random_tuple(self):
        max_retries = 5
        total_count = {'val': 0}

        @utils.retry_random_upon_exception(
            (exceptions.NsxLibInvalidInput, exceptions.APITransactionAborted),
            max_attempts=max_retries)
        def func_to_fail(x):
            total_count['val'] = total_count['val'] + 1
            raise exceptions.NsxLibInvalidInput(error_message='foo')

        self.assertRaises(exceptions.NsxLibInvalidInput, func_to_fail, 99)
        self.assertEqual(max_retries, total_count['val'])

    def test_retry_random_upon_exception_result_retry(self):
        total_count = {'val': 0}
        max_retries = 3

        @utils.retry_random_upon_exception_result(max_retries)
        def func_to_fail():
            total_count['val'] = total_count['val'] + 1
            return exceptions.NsxLibInvalidInput(error_message='foo')

        self.assertRaises(exceptions.NsxLibInvalidInput, func_to_fail)
        self.assertEqual(max_retries, total_count['val'])

    def test_retry_random_upon_exception_result_no_retry(self):
        total_count = {'val': 0}

        @utils.retry_random_upon_exception_result(3)
        def func_to_fail():
            total_count['val'] = total_count['val'] + 1
            raise exceptions.NsxLibInvalidInput(error_message='foo')

        self.assertRaises(exceptions.NsxLibInvalidInput, func_to_fail)
        # should not retry since exception is raised, and not returned
        self.assertEqual(1, total_count['val'])

    def test_retry_random_upon_exception_result_no_retry2(self):
        total_count = {'val': 0}
        ret_val = 42

        @utils.retry_random_upon_exception_result(3)
        def func_to_fail():
            total_count['val'] = total_count['val'] + 1
            return ret_val

        self.assertEqual(ret_val, func_to_fail())
        # should not retry since no exception is returned
        self.assertEqual(1, total_count['val'])

    @mock.patch.object(utils, '_update_max_nsgroups_criteria_tags')
    @mock.patch.object(utils, '_update_max_tags')
    @mock.patch.object(utils, '_update_tag_length')
    @mock.patch.object(utils, '_update_resource_length')
    def test_update_limits(self, _update_resource_length,
                           _update_tag_length, _update_max_tags,
                           _update_msx_nsg_criteria):
        limits = utils.TagLimits(1, 2, 3)
        utils.update_tag_limits(limits)
        _update_resource_length.assert_called_with(1)
        _update_tag_length.assert_called_with(2)
        _update_max_tags.assert_called_with(3)
        _update_msx_nsg_criteria.assert_called_with(3)


class NsxFeaturesTestCase(nsxlib_testcase.NsxLibTestCase):

    def test_v2_features(self, current_version='2.0.0'):
        self.nsxlib.nsx_version = current_version
        self.assertTrue(self.nsxlib.feature_supported(
            nsx_constants.FEATURE_ROUTER_FIREWALL))
        self.assertTrue(self.nsxlib.feature_supported(
            nsx_constants.FEATURE_EXCLUDE_PORT_BY_TAG))

    def test_v2_features_plus(self):
        self.test_v2_features(current_version='2.0.1')

    def test_v2_features_minus(self):
        self.nsxlib.nsx_version = '1.9.9'
        self.assertFalse(self.nsxlib.feature_supported(
            nsx_constants.FEATURE_ROUTER_FIREWALL))
        self.assertFalse(self.nsxlib.feature_supported(
            nsx_constants.FEATURE_EXCLUDE_PORT_BY_TAG))
        self.assertTrue(self.nsxlib.feature_supported(
            nsx_constants.FEATURE_MAC_LEARNING))


class APIRateLimiterTestCase(nsxlib_testcase.NsxLibTestCase):

    def setUp(self, *args, **kwargs):
        super(APIRateLimiterTestCase, self).setUp(with_mocks=False)
        self.rate_limiter = utils.APIRateLimiter

    @mock.patch('time.time')
    def test_calc_wait_time_no_wait(self, mock_time):
        mock_time.return_value = 2.0
        rate_limiter = self.rate_limiter(max_calls=2, period=1.0)
        rate_limiter._max_calls = 2
        # no wait when no prev calls
        self.assertEqual(rate_limiter._calc_wait_time(), 0)
        # no wait when prev call in period window is less than max_calls
        rate_limiter._call_time.append(0.9)
        rate_limiter._call_time.append(1.5)
        self.assertEqual(rate_limiter._calc_wait_time(), 0)
        # timestamps out of current window should be removed
        self.assertListEqual(list(rate_limiter._call_time), [1.5])

    @mock.patch('time.time')
    def test_calc_wait_time_need_wait(self, mock_time):
        mock_time.return_value = 2.0

        # At rate limit
        rate_limiter = self.rate_limiter(max_calls=2, period=1.0)
        rate_limiter._max_calls = 2
        rate_limiter._call_time.append(0.9)
        rate_limiter._call_time.append(1.2)
        rate_limiter._call_time.append(1.5)
        self.assertAlmostEqual(rate_limiter._calc_wait_time(), 0.2)
        # timestamps out of current window should be removed
        self.assertListEqual(list(rate_limiter._call_time), [1.2, 1.5])

        # Over rate limit. Enforce no compensation wait.
        rate_limiter = self.rate_limiter(max_calls=2, period=1.0)
        rate_limiter._max_calls = 2
        rate_limiter._call_time.append(0.9)
        rate_limiter._call_time.append(1.2)
        rate_limiter._call_time.append(1.5)
        rate_limiter._call_time.append(1.8)
        self.assertAlmostEqual(rate_limiter._calc_wait_time(), 0.5)
        # timestamps out of current window should be removed
        self.assertListEqual(list(rate_limiter._call_time), [1.2, 1.5, 1.8])

    @mock.patch('vmware_nsxlib.v3.utils.APIRateLimiter._calc_wait_time')
    @mock.patch('time.sleep')
    @mock.patch('time.time')
    def test_context_manager_no_wait(self, mock_time, mock_sleep, mock_calc):
        mock_time.return_value = 2.0
        rate_limiter = self.rate_limiter(max_calls=2, period=1.0)
        mock_calc.return_value = 0
        with rate_limiter as wait_time:
            self.assertEqual(wait_time, 0)
            mock_sleep.assert_not_called()
        self.assertListEqual(list(rate_limiter._call_time), [2.0])

    @mock.patch('vmware_nsxlib.v3.utils.APIRateLimiter._calc_wait_time')
    @mock.patch('time.sleep')
    def test_context_manager_disabled(self, mock_sleep, mock_calc):
        rate_limiter = self.rate_limiter(max_calls=None)
        with rate_limiter as wait_time:
            self.assertEqual(wait_time, 0)
            mock_sleep.assert_not_called()
            mock_calc.assert_not_called()

    @mock.patch('vmware_nsxlib.v3.utils.APIRateLimiter._calc_wait_time')
    @mock.patch('time.sleep')
    @mock.patch('time.time')
    def test_context_manager_need_wait(self, mock_time, mock_sleep, mock_calc):
        mock_time.return_value = 0.0
        rate_limiter = self.rate_limiter(max_calls=2, period=1.0)
        mock_time.side_effect = [2.0, 2.5]
        mock_calc.return_value = 0.5
        with rate_limiter as wait_time:
            self.assertEqual(wait_time, 0.5)
            mock_sleep.assert_called_once_with(wait_time)
        self.assertListEqual(list(rate_limiter._call_time), [2.5])


class APIRateLimiterAIMDTestCase(APIRateLimiterTestCase):

    def setUp(self, *args, **kwargs):
        super(APIRateLimiterAIMDTestCase, self).setUp(with_mocks=False)
        self.rate_limiter = utils.APIRateLimiterAIMD

    @mock.patch('time.time')
    def test_adjust_rate_increase(self, mock_time):
        mock_time.side_effect = [0.0, 2.0, 4.0, 6.0]
        rate_limiter = self.rate_limiter(max_calls=10)
        rate_limiter._max_calls = 8
        # normal period increases rate by 1, even for non-200 normal codes
        rate_limiter.adjust_rate(wait_time=1.0, status_code=404)
        self.assertEqual(rate_limiter._max_calls, 9)
        # max calls limited by top limit
        rate_limiter.adjust_rate(wait_time=1.0, status_code=200)
        rate_limiter.adjust_rate(wait_time=1.0, status_code=200)
        self.assertEqual(rate_limiter._max_calls, 10)

    @mock.patch('time.time')
    def test_adjust_rate_decrease(self, mock_time):
        mock_time.side_effect = [0.0, 2.0, 4.0, 6.0]
        rate_limiter = self.rate_limiter(max_calls=10)
        rate_limiter._max_calls = 4
        # 429 or 503 should decrease rate by half
        rate_limiter.adjust_rate(wait_time=1.0, status_code=429)
        self.assertEqual(rate_limiter._max_calls, 2)
        rate_limiter.adjust_rate(wait_time=0.0, status_code=503)
        self.assertEqual(rate_limiter._max_calls, 1)
        # lower bound should be 1
        rate_limiter.adjust_rate(wait_time=1.0, status_code=503)
        self.assertEqual(rate_limiter._max_calls, 1)

    @mock.patch('time.time')
    def test_adjust_rate_no_change(self, mock_time):
        mock_time.side_effect = [0.0, 2.0, 2.5, 2.6]
        rate_limiter = self.rate_limiter(max_calls=10)
        rate_limiter._max_calls = 4
        # non blocked successful calls should not change rate
        rate_limiter.adjust_rate(wait_time=0.001, status_code=200)
        self.assertEqual(rate_limiter._max_calls, 4)

        # too fast calls should not change rate
        rate_limiter.adjust_rate(wait_time=1.0, status_code=200)
        self.assertEqual(rate_limiter._max_calls, 4)
        rate_limiter.adjust_rate(wait_time=1.0, status_code=429)
        self.assertEqual(rate_limiter._max_calls, 4)

    def test_adjust_rate_disabled(self):
        rate_limiter = self.rate_limiter(max_calls=None)
        rate_limiter.adjust_rate(wait_time=0.001, status_code=200)
        self.assertFalse(hasattr(rate_limiter, '_max_calls'))


class APICallCollectorTestCase(nsxlib_testcase.NsxLibTestCase):
    def setUp(self, *args, **kwargs):
        super(APICallCollectorTestCase, self).setUp(with_mocks=False)
        self.api_collector = utils.APICallCollector('1.2.3.4', max_entry=2)

    def test_add_record(self):
        record1 = utils.APICallRecord('ts1', 'get', 'uri_1', 200)
        record2 = utils.APICallRecord('ts2', 'post', 'uri_2', 404)
        self.api_collector.add_record(record1)
        self.api_collector.add_record(record2)
        self.assertListEqual(list(self.api_collector._api_log_store),
                             [record1, record2])

    def test_add_record_overflow(self):
        record1 = utils.APICallRecord('ts1', 'get', 'uri_1', 200)
        record2 = utils.APICallRecord('ts2', 'post', 'uri_2', 404)
        record3 = utils.APICallRecord('ts3', 'delete', 'uri_3', 429)
        self.api_collector.add_record(record1)
        self.api_collector.add_record(record2)
        self.api_collector.add_record(record3)
        self.assertListEqual(list(self.api_collector._api_log_store),
                             [record2, record3])

    def test_pop_record(self):
        record1 = utils.APICallRecord('ts1', 'get', 'uri_1', 200)
        record2 = utils.APICallRecord('ts2', 'post', 'uri_2', 404)
        self.api_collector.add_record(record1)
        self.api_collector.add_record(record2)
        self.assertEqual(self.api_collector.pop_record(), record1)
        self.assertEqual(self.api_collector.pop_record(), record2)

    def test_pop_all_records(self):
        record1 = utils.APICallRecord('ts1', 'get', 'uri_1', 200)
        record2 = utils.APICallRecord('ts2', 'post', 'uri_2', 404)
        self.api_collector.add_record(record1)
        self.api_collector.add_record(record2)
        self.assertListEqual(self.api_collector.pop_all_records(),
                             [record1, record2])

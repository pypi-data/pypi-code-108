# Copyright 2017 VMware, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import copy
from unittest import mock

from vmware_nsxlib.tests.unit.v3 import nsxlib_testcase
from vmware_nsxlib.tests.unit.v3.policy import test_resources
from vmware_nsxlib.v3 import exceptions as nsxlib_exc
from vmware_nsxlib.v3 import nsx_constants
from vmware_nsxlib.v3.policy import constants
from vmware_nsxlib.v3.policy import lb_defs
TEST_TENANT = 'test'


class TestPolicyLBClientSSLProfileApi(test_resources.NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBClientSSLProfileApi, self).setUp()
        self.resourceApi = self.policy_lib.load_balancer.client_ssl_profile

    def test_create_with_id(self):
        name = 'd1'
        description = 'desc'
        obj_id = '111'
        protocols = ['TLS_V1_1']
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                client_ssl_profile_id=obj_id,
                description=description,
                protocols=protocols,
                tenant=TEST_TENANT)
            expected_def = lb_defs.LBClientSslProfileDef(
                client_ssl_profile_id=obj_id,
                name=name,
                description=description,
                protocols=protocols,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result)

    def test_create_without_id(self):
        name = 'd1'
        description = 'desc'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                tenant=TEST_TENANT)
            expected_def = lb_defs.LBClientSslProfileDef(
                client_ssl_profile_id=mock.ANY,
                name=name,
                description=description,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, tenant=TEST_TENANT)
            expected_def = lb_defs.LBClientSslProfileDef(
                client_ssl_profile_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = lb_defs.LBClientSslProfileDef(
                client_ssl_profile_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'd1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = lb_defs.LBClientSslProfileDef(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = lb_defs.LBClientSslProfileDef(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        obj_id = '111'
        name = 'new name'
        description = 'new desc'
        with self.mock_get(obj_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(obj_id,
                                    name=name,
                                    description=description,
                                    tenant=TEST_TENANT)
            expected_def = lb_defs.LBClientSslProfileDef(
                client_ssl_profile_id=obj_id,
                name=name,
                description=description,
                tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)


class TestPolicyLBServerSSLProfileApi(test_resources.NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBServerSSLProfileApi, self).setUp()
        self.resourceApi = self.policy_lib.load_balancer.server_ssl_profile

    def test_create_with_id(self):
        name = 'd1'
        description = 'desc'
        obj_id = '111'
        protocols = ['TLS_V1_1']
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                server_ssl_profile_id=obj_id,
                description=description,
                protocols=protocols,
                tenant=TEST_TENANT)
            expected_def = lb_defs.LBServerSslProfileDef(
                server_ssl_profile_id=obj_id,
                name=name,
                description=description,
                protocols=protocols,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result)

    def test_create_without_id(self):
        name = 'd1'
        description = 'desc'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                tenant=TEST_TENANT)
            expected_def = lb_defs.LBServerSslProfileDef(
                server_ssl_profile_id=mock.ANY,
                name=name,
                description=description,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, tenant=TEST_TENANT)
            expected_def = lb_defs.LBServerSslProfileDef(
                server_ssl_profile_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = lb_defs.LBServerSslProfileDef(
                server_ssl_profile_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'd1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = lb_defs.LBServerSslProfileDef(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = lb_defs.LBServerSslProfileDef(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        obj_id = '111'
        name = 'new name'
        description = 'new desc'
        with self.mock_get(obj_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(obj_id,
                                    name=name,
                                    description=description,
                                    tenant=TEST_TENANT)
            expected_def = lb_defs.LBServerSslProfileDef(
                server_ssl_profile_id=obj_id,
                name=name,
                description=description,
                tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)


class TestPolicyLBPersistenceProfile(
    test_resources.NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBPersistenceProfile, self).setUp()
        self.resourceApi = (
            self.policy_lib.load_balancer.lb_persistence_profile)

    def test_delete(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, tenant=TEST_TENANT)
            expected_def = (
                self.resourceApi.entry_def(
                    persistence_profile_id=obj_id,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = (
                self.resourceApi.entry_def(
                    persistence_profile_id=obj_id,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'd1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = (
                self.resourceApi.entry_def(
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = (
                self.resourceApi.entry_def(
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_wait_until_realized_fail(self):
        pers_id = 'test_pers'
        info = {'state': constants.STATE_UNREALIZED,
                'realization_specific_identifier': pers_id}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.wait_until_realized,
                              pers_id, max_attempts=5, sleep=0.1,
                              tenant=TEST_TENANT)

    def test_wait_until_realized_succeed(self):
        pers_id = 'test_pers'
        info = {'state': constants.STATE_REALIZED,
                'realization_specific_identifier': pers_id,
                'entity_type': 'LbPersistenceProfileDto'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            actual_info = self.resourceApi.wait_until_realized(
                pers_id, entity_type='LbPersistenceProfileDto', max_attempts=5,
                sleep=0.1, tenant=TEST_TENANT)
            self.assertEqual(info, actual_info)


class TestPolicyLBCookiePersistenceProfile(
    test_resources.NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBCookiePersistenceProfile, self).setUp()
        self.resourceApi = (
            self.policy_lib.load_balancer.lb_cookie_persistence_profile)

    def test_create_with_id(self):
        name = 'd1'
        description = 'desc'
        obj_id = '111'
        cookie_garble = 'test_garble'
        cookie_name = 'test_name'
        cookie_mode = 'INSERT'
        cookie_path = 'path'
        cookie_time = 'time'
        persistence_shared = False
        with self.mock_create_update() as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                persistence_profile_id=obj_id,
                description=description,
                cookie_name=cookie_name,
                cookie_garble=cookie_garble,
                cookie_mode=cookie_mode,
                cookie_path=cookie_path,
                cookie_time=cookie_time,
                persistence_shared=persistence_shared,
                tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBCookiePersistenceProfileDef(
                    persistence_profile_id=obj_id,
                    name=name,
                    description=description,
                    cookie_name=cookie_name,
                    cookie_garble=cookie_garble,
                    cookie_mode=cookie_mode,
                    cookie_path=cookie_path,
                    cookie_time=cookie_time,
                    persistence_shared=persistence_shared,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result)

    def test_create_without_id(self):
        name = 'd1'
        description = 'desc'
        with self.mock_create_update() as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBCookiePersistenceProfileDef(
                    persistence_profile_id=mock.ANY,
                    name=name,
                    description=description,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBCookiePersistenceProfileDef(
                    persistence_profile_id=obj_id,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBCookiePersistenceProfileDef(
                    persistence_profile_id=obj_id,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'd1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [
                {'resource_type': self.resourceApi.entry_def.resource_type(),
                 'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = (
                lb_defs.LBCookiePersistenceProfileDef(
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [
                {'resource_type': self.resourceApi.entry_def.resource_type(),
                 'display_name': 'profile1'},
                {'resource_type': 'wrong_type',
                 'display_name': 'profile2'}]}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBCookiePersistenceProfileDef(
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(1, len(result))

    def test_update(self):
        obj_id = '111'
        name = 'new name'
        description = 'new desc'
        cookie_garble = 'test_garble'
        cookie_name = 'test_name'
        cookie_mode = 'INSERT'
        cookie_path = 'path'
        cookie_time = 'time'
        persistence_shared = False
        with self.mock_get(obj_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(obj_id,
                                    name=name,
                                    description=description,
                                    cookie_name=cookie_name,
                                    cookie_garble=cookie_garble,
                                    cookie_mode=cookie_mode,
                                    cookie_path=cookie_path,
                                    cookie_time=cookie_time,
                                    persistence_shared=persistence_shared,
                                    tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBCookiePersistenceProfileDef(
                    persistence_profile_id=obj_id,
                    name=name,
                    description=description,
                    cookie_name=cookie_name,
                    cookie_garble=cookie_garble,
                    cookie_mode=cookie_mode,
                    cookie_path=cookie_path,
                    cookie_time=cookie_time,
                    persistence_shared=persistence_shared,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(update_call, expected_def)


class TestPolicyLBSourceIpProfileApi(test_resources.NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBSourceIpProfileApi, self).setUp()
        self.resourceApi = (
            self.policy_lib.load_balancer.lb_source_ip_persistence_profile)

    def test_create_with_id(self):
        name = 'd1'
        description = 'desc'
        obj_id = '111'
        ha = 'ha'
        persistence_shared = True
        purge = 'purge'
        timeout = 100
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                persistence_profile_id=obj_id,
                description=description,
                ha_persistence_mirroring_enabled=ha,
                persistence_shared=persistence_shared,
                purge=purge,
                timeout=timeout,
                tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBSourceIpPersistenceProfileDef(
                    persistence_profile_id=obj_id,
                    name=name,
                    description=description,
                    ha_persistence_mirroring_enabled=ha,
                    persistence_shared=persistence_shared,
                    purge=purge,
                    timeout=timeout,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result)

    def test_create_without_id(self):
        name = 'd1'
        description = 'desc'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBSourceIpPersistenceProfileDef(
                    persistence_profile_id=mock.ANY,
                    name=name,
                    description=description,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBSourceIpPersistenceProfileDef(
                    persistence_profile_id=obj_id,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBSourceIpPersistenceProfileDef(
                    persistence_profile_id=obj_id,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'd1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [
                {'resource_type': self.resourceApi.entry_def.resource_type(),
                 'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = (
                lb_defs.LBSourceIpPersistenceProfileDef(
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        profiles = [{'resource_type': 'LBSourceIpPersistenceProfile',
                     'id': 'default-source-ip-lb-persistence-profile',
                     'display_name': 'default-source-ip-profile'}]
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': profiles}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBSourceIpPersistenceProfileDef(
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(profiles, result)

    def test_list_different_type(self):
        profiles = [{'resource_type': 'LBSourceCookiePersistenceProfile',
                     'id': 'default-source-ip-lb-persistence-profile',
                     'display_name': 'default-source-ip-profile'}]
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': profiles}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBSourceIpPersistenceProfileDef(
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_list_empty(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBSourceIpPersistenceProfileDef(
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        obj_id = '111'
        name = 'new name'
        description = 'new desc'
        ha = False
        persistence_shared = False
        purge = 'no purge'
        timeout = 101
        with self.mock_get(obj_id, name), \
            self.mock_create_update() as update_call:

            self.resourceApi.update(obj_id,
                                    name=name,
                                    description=description,
                                    ha_persistence_mirroring_enabled=ha,
                                    persistence_shared=persistence_shared,
                                    purge=purge,
                                    timeout=timeout,
                                    tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBSourceIpPersistenceProfileDef(
                    persistence_profile_id=obj_id,
                    name=name,
                    description=description,
                    ha_persistence_mirroring_enabled=ha,
                    persistence_shared=persistence_shared,
                    purge=purge,
                    timeout=timeout,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(update_call, expected_def)


class TestPolicyLBApplicationProfile(test_resources.NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBApplicationProfile, self).setUp()
        self.resourceApi = self.policy_lib.load_balancer.lb_http_profile

    def test_create_with_id(self):
        name = 'd1'
        description = 'desc'
        obj_id = '111'
        http_redirect_to_https = False
        http_redirect_to = "sample-url"
        idle_timeout = 100
        ntlm = False
        request_body_size = 1025
        request_header_size = 10
        response_header_size = 10
        response_timeout = 10
        x_forwarded_for = 'INSERT'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                lb_app_profile_id=obj_id,
                description=description,
                http_redirect_to_https=http_redirect_to_https,
                http_redirect_to=http_redirect_to,
                idle_timeout=idle_timeout,
                ntlm=ntlm,
                request_body_size=request_body_size,
                request_header_size=request_header_size,
                response_header_size=response_header_size,
                response_timeout=response_timeout,
                x_forwarded_for=x_forwarded_for,
                tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBHttpProfileDef(
                    lb_app_profile_id=obj_id,
                    name=name,
                    description=description,
                    http_redirect_to_https=http_redirect_to_https,
                    http_redirect_to=http_redirect_to,
                    idle_timeout=idle_timeout,
                    ntlm=ntlm,
                    request_body_size=request_body_size,
                    request_header_size=request_header_size,
                    response_header_size=response_header_size,
                    response_timeout=response_timeout,
                    x_forwarded_for=x_forwarded_for,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result)

    def test_fast_tcp_profile_def(self):
        obj_dict = {'close_timeout': 8,
                    'ha_flow_mirroring_enabled': False,
                    'idle_timeout': 100}
        fast_tcp_profile_def = lb_defs.LBFastTcpProfile(**obj_dict)
        self.assertDictContainsSubset(obj_dict,
                                      fast_tcp_profile_def.get_obj_dict())

    def test_fast_udp_profile_def(self):
        obj_dict = {'flow_mirroring_enabled': False,
                    'idle_timeout': 100}
        fast_udp_profile_def = lb_defs.LBFastUdpProfile(**obj_dict)
        self.assertDictContainsSubset(obj_dict,
                                      fast_udp_profile_def.get_obj_dict())

    def test_http_profile_def(self):
        obj_dict = {'http_redirect_to_https': False,
                    'http_redirect_to': "sample-url",
                    'idle_timeout': 100,
                    'ntlm': False,
                    'request_body_size': 1025,
                    'request_header_size': 10,
                    'response_header_size': 10,
                    'response_timeout': 10,
                    'x_forwarded_for': 'INSERT'}
        http_profile_def = lb_defs.LBHttpProfileDef(**obj_dict)
        self.assertDictContainsSubset(obj_dict,
                                      http_profile_def.get_obj_dict())

    def test_create_without_id(self):
        name = 'd1'
        description = 'desc'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBHttpProfileDef(
                    lb_app_profile_id=mock.ANY,
                    name=name,
                    description=description,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBHttpProfileDef(
                    lb_app_profile_id=obj_id,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBHttpProfileDef(
                    lb_app_profile_id=obj_id,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'd1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = (
                lb_defs.LBHttpProfileDef(tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBHttpProfileDef(tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        obj_id = '111'
        name = 'new name'
        description = 'new desc'
        with self.mock_get(obj_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(obj_id,
                                    name=name,
                                    description=description,
                                    tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBHttpProfileDef(
                    lb_app_profile_id=obj_id,
                    name=name,
                    description=description,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(update_call, expected_def)


class TestPolicyLBService(test_resources.NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBService, self).setUp()
        self.resourceApi = self.policy_lib.load_balancer.lb_service

    def test_create_with_id(self):
        name = 'd1'
        description = 'desc'
        obj_id = '111'
        size = 'SMALL'
        connectivity_path = 'path'
        relax_scale_validation = True
        with self.mock_create_update() as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                lb_service_id=obj_id,
                description=description,
                size=size,
                connectivity_path=connectivity_path,
                relax_scale_validation=relax_scale_validation,
                tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBServiceDef(
                    nsx_version=self.policy_lib.get_version(),
                    lb_service_id=obj_id,
                    name=name,
                    description=description,
                    size=size,
                    connectivity_path=connectivity_path,
                    relax_scale_validation=relax_scale_validation,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result)

    def test_create_without_id(self):
        name = 'd1'
        description = 'desc'
        with self.mock_create_update() as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBServiceDef(lb_service_id=mock.ANY,
                                     name=name,
                                     description=description,
                                     tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_create_with_unsupported_attribute(self):
        name = 'd1'
        description = 'desc'
        relax_scale_validation = True

        with self.mock_create_update() as api_call, \
                mock.patch.object(self.resourceApi, 'version', '0.0.0'):
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                relax_scale_validation=relax_scale_validation,
                tenant=TEST_TENANT)
            expected_def = (
                lb_defs.LBServiceDef(lb_service_id=mock.ANY,
                                     name=name,
                                     description=description,
                                     tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, tenant=TEST_TENANT)
            expected_def = lb_defs.LBServiceDef(
                lb_service_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = lb_defs.LBServiceDef(
                lb_service_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'd1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = lb_defs.LBServiceDef(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def _test_list(self, silent=False, silent_if_empty=False):
        s1 = {'id': 'xxx', 'display_name': 'yyy'}
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': [s1]}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT, silent=silent,
                                           silent_if_empty=silent_if_empty)
            expected_def = lb_defs.LBServiceDef(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([s1], result)

    def test_list(self):
        self._test_list()

    def test_list_total_silence(self):
        self._test_list(silent=True)

    def test_list_silent_if_empty(self):
        self._test_list(silent_if_empty=True)

    def test_update(self):
        obj_id = '111'
        name = 'new name'
        description = 'new desc'
        size = 'SMALL'
        connectivity_path = 'path'
        relax_scale_validation = True
        with self.mock_get(obj_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(
                obj_id,
                name=name,
                description=description,
                tenant=TEST_TENANT,
                size=size,
                connectivity_path=connectivity_path,
                relax_scale_validation=relax_scale_validation)
            expected_def = lb_defs.LBServiceDef(
                nsx_version=self.policy_lib.get_version(),
                lb_service_id=obj_id,
                name=name,
                description=description,
                tenant=TEST_TENANT,
                size=size,
                connectivity_path=connectivity_path,
                relax_scale_validation=relax_scale_validation)
            self.assert_called_with_def(update_call, expected_def)

    def test_update_customized(self):
        obj_id = '111'
        name = 'name'
        tags = [{'tag': '1', 'scope': '2'}]

        def update_callback(body):
            body['tags'] = tags

        with self.mock_get(obj_id, name), \
            mock.patch.object(self.policy_api.client, "update") as update_call:
            self.resourceApi.update_customized(
                obj_id, update_callback)

            update_call.assert_called_once_with(
                'infra/lb-services/%s' % obj_id,
                {'id': obj_id, 'display_name': name,
                 'resource_type': 'LBService',
                 'tags': tags})

    def test_get_status(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get") as api_call:
            self.resourceApi.get_status(obj_id, tenant=TEST_TENANT)
            expected_def = lb_defs.LBServiceStatusDef(
                lb_service_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get_statistics(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get") as api_call:
            self.resourceApi.get_statistics(obj_id, tenant=TEST_TENANT)
            expected_def = lb_defs.LBServiceStatisticsDef(
                lb_service_id=obj_id,
                realtime=False,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual('%s/lb-services/%s/statistics/',
                             expected_def.path_pattern)

    def test_get_statistics_realtime(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get") as api_call:
            self.resourceApi.get_statistics(obj_id, realtime=True,
                                            tenant=TEST_TENANT)
            expected_def = lb_defs.LBServiceStatisticsDef(
                lb_service_id=obj_id,
                realtime=True,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual('%s/lb-services/%s/statistics?source=realtime',
                             expected_def.path_pattern)

    def test_get_virtual_server_status(self):
        obj_id = '111'
        vs_id = '222'
        with mock.patch.object(self.policy_api, "get") as api_call:
            self.resourceApi.get_virtual_server_status(
                obj_id, vs_id, tenant=TEST_TENANT)
            expected_def = lb_defs.LBVirtualServerStatusDef(
                lb_service_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get_usage(self):
        lbs_id = 'test_vs'
        with mock.patch.object(self.policy_api, "get") as api_call:
            self.resourceApi.get_usage(
                lbs_id, realtime=True, tenant=TEST_TENANT)
            expected_def = lb_defs.LBServiceUsageDef(
                lb_service_id=lbs_id,
                realtime=True,
                tenant=TEST_TENANT)
            expected_path = '%s/lb-services/%s/service-usage?source=realtime'
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(expected_def.path_pattern, expected_path)

    def test_wait_until_realized_fail(self):
        lbs_id = 'test_lbs'
        info = {'state': constants.STATE_UNREALIZED,
                'realization_specific_identifier': lbs_id,
                'entity_type': 'LbServiceDto'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.wait_until_realized,
                              lbs_id, max_attempts=5, sleep=0.1,
                              tenant=TEST_TENANT)

    def test_wait_until_realized_error(self):
        lbs_id = 'test_lbs'
        error_code = 23500
        related_error_code = 23707
        error_msg = 'Found errors in the request.'
        related_error_msg = 'Exceed maximum number of load balancer.'
        info = {'state': constants.STATE_ERROR,
                'realization_specific_identifier': lbs_id,
                'entity_type': 'LbServiceDto',
                'alarms': [{
                    'message': error_msg,
                    'error_details': {
                        'related_errors': [{
                            'error_code': related_error_code,
                            'module_name': 'LOAD-BALANCER',
                            'error_message': related_error_msg
                        }],
                        'error_code': error_code,
                        'module_name': 'LOAD-BALANCER',
                        'error_message': error_msg
                    }
                }]}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            with self.assertRaises(nsxlib_exc.RealizationErrorStateError) as e:
                self.resourceApi.wait_until_realized(
                    lbs_id, tenant=TEST_TENANT)
            error_msg_tail = "%s: %s" % (error_msg, related_error_msg)
            self.assertTrue(e.exception.msg.endswith(error_msg_tail))
            self.assertEqual(e.exception.error_code, error_code)
            self.assertEqual(e.exception.related_error_codes,
                             [related_error_code])

    def test_wait_until_realized_succeed(self):
        lbs_id = 'test_lbs'
        info = {'state': constants.STATE_REALIZED,
                'realization_specific_identifier': lbs_id,
                'entity_type': 'LbServiceDto'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            actual_info = self.resourceApi.wait_until_realized(
                lbs_id, max_attempts=5, sleep=0.1, tenant=TEST_TENANT)
            self.assertEqual(info, actual_info)


class TestPolicyLBVirtualServer(test_resources.NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBVirtualServer, self).setUp()
        self.resourceApi = self.policy_lib.load_balancer.virtual_server

    def test_create_with_id(self):
        name = 'd1'
        description = 'desc'
        obj_id = '111'
        waf_profile_id = 'waf'
        waf_profile_path = self.policy_lib.waf_profile.get_path(
            profile_id=waf_profile_id, tenant=TEST_TENANT)
        waf_profile_binding = lb_defs.WAFProfileBindingDef(
            waf_profile_path=waf_profile_path)
        lb_acl = self.resourceApi.build_access_list_control(
            constants.ACTION_ALLOW, 'fake_group_path', True)
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                virtual_server_id=obj_id,
                waf_profile_binding=waf_profile_binding,
                description=description,
                access_list_control=lb_acl,
                tenant=TEST_TENANT)
            expected_def = lb_defs.LBVirtualServerDef(
                nsx_version=self.policy_lib.get_version(),
                virtual_server_id=obj_id, name=name, description=description,
                waf_profile_binding=waf_profile_binding,
                access_list_control=lb_acl.get_obj_dict(),
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result)

    def test_create_without_id(self):
        name = 'd1'
        description = 'desc'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                tenant=TEST_TENANT)
            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=mock.ANY, name=name, description=description,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, tenant=TEST_TENANT)
            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'd1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = lb_defs.LBVirtualServerDef(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = lb_defs.LBVirtualServerDef(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        obj_id = '111'
        name = 'new name'
        description = 'new desc'
        vs_name = 'name-name'
        with self.mock_get(obj_id, vs_name), \
            self.mock_create_update() as update_call:

            self.resourceApi.update(obj_id,
                                    name=name,
                                    description=description,
                                    tenant=TEST_TENANT)
            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=obj_id, name=name,
                description=description,
                tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)

    def test_update_log_parameters(self):
        obj_id = '111'
        name = 'new name'
        description = 'new desc'
        vs_name = 'name-name'
        with self.mock_get(obj_id, vs_name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(obj_id,
                                    name=name,
                                    description=description,
                                    tenant=TEST_TENANT,
                                    access_log_enabled=True,
                                    log_significant_event_only=True)
            expected_def = lb_defs.LBVirtualServerDef(
                nsx_version=nsx_constants.NSX_VERSION_3_0_0,
                virtual_server_id=obj_id, name=name,
                description=description,
                tenant=TEST_TENANT, access_log_enabled=True,
                log_significant_event_only=True)
            self.assert_called_with_def(update_call, expected_def)

    def test_log_parameters_for_version(self):
        obj_id = '111'
        name = 'new name'
        description = 'new desc'

        expected_def = lb_defs.LBVirtualServerDef(
            nsx_version=nsx_constants.NSX_VERSION_2_5_0,
            virtual_server_id=obj_id, name=name,
            description=description,
            tenant=TEST_TENANT, access_log_enabled=True,
            log_significant_event_only=True)
        self.assertFalse('access_log_enabled' in expected_def.get_obj_dict())
        self.assertFalse('log_significant_event_only' in
                         expected_def.get_obj_dict())

        expected_def = lb_defs.LBVirtualServerDef(
            nsx_version=nsx_constants.NSX_VERSION_3_0_0,
            virtual_server_id=obj_id, name=name,
            description=description,
            tenant=TEST_TENANT, access_log_enabled=True,
            log_significant_event_only=True)
        self.assertTrue('access_log_enabled' in expected_def.get_obj_dict())
        self.assertTrue('log_significant_event_only' in
                        expected_def.get_obj_dict())

    def test_non_partial_update(self):
        obj_id = '111'
        vs_name = 'name-name'
        with self.mock_get(obj_id, vs_name, max_concurrent_connections=80), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(obj_id,
                                    max_concurrent_connections=None,
                                    tenant=TEST_TENANT,
                                    allow_partial_updates=False)
            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=obj_id, name=vs_name,
                max_concurrent_connections=None,
                tenant=TEST_TENANT)
            update_call.assert_called_with(mock.ANY, partial_updates=False,
                                           force=False)
            self.assert_called_with_def(update_call, expected_def)

    def test_add_lb_rule(self):
        vs_obj_id = '111'
        vs_name = 'name-name'
        rule_actions = 'test1'
        rule_match_conditions = 'test2'
        rule_name = 'dummy_rule'
        rule_match_strategy = 'test3'
        rule_phase = 'test4'
        with self.mock_get(vs_obj_id, vs_name), \
            self.mock_create_update() as update_call:
            self.resourceApi.add_lb_rule(
                vs_obj_id, actions=rule_actions, name=rule_name,
                match_conditions=rule_match_conditions,
                match_strategy=rule_match_strategy, phase=rule_phase)
            lb_rule = lb_defs.LBRuleDef(
                rule_actions, rule_match_conditions, rule_name,
                rule_match_strategy, rule_phase)

            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=vs_obj_id,
                rules=[lb_rule])
            self.assert_called_with_def(update_call, expected_def)

    def test_add_lb_rule_first(self):
        vs_obj_id = '111'
        vs_name = 'name-name'
        rule_actions = 'test1'
        rule_match_conditions = 'test2'
        rule_name = 'dummy_rule'
        rule_match_strategy = 'test3'
        rule_phase = 'test4'
        with self.mock_get(vs_obj_id, vs_name,
                           rules=[{'display_name': 'xx'},
                                  {'display_name': 'yy'}]), \
            self.mock_create_update() as update_call:

            self.resourceApi.add_lb_rule(
                vs_obj_id, actions=rule_actions, name=rule_name,
                match_conditions=rule_match_conditions,
                match_strategy=rule_match_strategy, phase=rule_phase,
                position=0)
            lb_rule = lb_defs.LBRuleDef(
                rule_actions, rule_match_conditions, rule_name,
                rule_match_strategy, rule_phase)

            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=vs_obj_id,
                rules=[lb_rule,
                       {'display_name': 'xx'},
                       {'display_name': 'yy'}])
            self.assert_called_with_def(update_call, expected_def)

    def test_add_lb_rule_last(self):
        vs_obj_id = '111'
        vs_name = 'name-name'
        rule_actions = 'test1'
        rule_match_conditions = 'test2'
        rule_name = 'dummy_rule'
        rule_match_strategy = 'test3'
        rule_phase = 'test4'
        with self.mock_get(vs_obj_id, vs_name,
                           rules=[{'display_name': 'xx'},
                                  {'display_name': 'yy'}]), \
            self.mock_create_update() as update_call:
            self.resourceApi.add_lb_rule(
                vs_obj_id, actions=rule_actions, name=rule_name,
                match_conditions=rule_match_conditions,
                match_strategy=rule_match_strategy, phase=rule_phase)
            lb_rule = lb_defs.LBRuleDef(
                rule_actions, rule_match_conditions, rule_name,
                rule_match_strategy, rule_phase)

            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=vs_obj_id,
                rules=[{'display_name': 'xx'},
                       {'display_name': 'yy'},
                       lb_rule])
            self.assert_called_with_def(update_call, expected_def)

    def test_add_lb_rule_last_over(self):
        vs_obj_id = '111'
        vs_name = 'name-name'
        rule_actions = 'test1'
        rule_match_conditions = 'test2'
        rule_name = 'dummy_rule'
        rule_match_strategy = 'test3'
        rule_phase = 'test4'
        with self.mock_get(vs_obj_id, vs_name,
                           rules=[{'display_name': 'xx'},
                                  {'display_name': 'yy'}]), \
            self.mock_create_update() as update_call:

            self.resourceApi.add_lb_rule(
                vs_obj_id, actions=rule_actions, name=rule_name,
                match_conditions=rule_match_conditions,
                match_strategy=rule_match_strategy, phase=rule_phase,
                position=999)
            lb_rule = lb_defs.LBRuleDef(
                rule_actions, rule_match_conditions, rule_name,
                rule_match_strategy, rule_phase)

            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=vs_obj_id,
                rules=[{'display_name': 'xx'},
                       {'display_name': 'yy'},
                       lb_rule])
            self.assert_called_with_def(update_call, expected_def)

    def test_add_lb_rule_mid(self):
        vs_obj_id = '111'
        vs_name = 'name-name'
        rule_actions = 'test1'
        rule_match_conditions = 'test2'
        rule_name = 'dummy_rule'
        rule_match_strategy = 'test3'
        rule_phase = 'test4'
        with self.mock_get(vs_obj_id, vs_name,
                           rules=[{'display_name': 'xx'},
                                  {'display_name': 'yy'}]), \
            self.mock_create_update() as update_call:
            self.resourceApi.add_lb_rule(
                vs_obj_id, actions=rule_actions, name=rule_name,
                match_conditions=rule_match_conditions,
                match_strategy=rule_match_strategy, phase=rule_phase,
                position=1)
            lb_rule = lb_defs.LBRuleDef(
                rule_actions, rule_match_conditions, rule_name,
                rule_match_strategy, rule_phase)

            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=vs_obj_id,
                rules=[{'display_name': 'xx'},
                       lb_rule,
                       {'display_name': 'yy'}])
            self.assert_called_with_def(update_call, expected_def)

    def test_update_lb_rule(self):
        vs_obj_id = '111'
        vs_name = 'name-name'
        with self.mock_get(
                vs_obj_id, vs_name,
                rules=[{'display_name': 'xx', 'actions': '11'},
                       {'display_name': 'yy'}]), \
            self.mock_create_update() as update_call:
            self.resourceApi.update_lb_rule(vs_obj_id, 'xx', actions='22')

            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=vs_obj_id,
                rules=[{'display_name': 'xx', 'actions': '22'},
                       {'display_name': 'yy'}])
            self.assert_called_with_def(update_call, expected_def)

    def test_update_lb_rule_position(self):
        vs_obj_id = '111'
        vs_name = 'name-name'
        with self.mock_get(
                vs_obj_id, vs_name,
                rules=[{'display_name': 'xx', 'actions': '11'},
                       {'display_name': 'yy'}]), \
            self.mock_create_update() as update_call:
            self.resourceApi.update_lb_rule(vs_obj_id, 'xx', actions='22',
                                            position=1)

            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=vs_obj_id,
                rules=[{'display_name': 'yy'},
                       {'display_name': 'xx', 'actions': '22'}])
            self.assert_called_with_def(update_call, expected_def)

    def test_update_lb_rule_suffix(self):
        vs_obj_id = '111'
        vs_name = 'name-name'
        with self.mock_get(
                vs_obj_id, vs_name,
                rules=[{'display_name': 'xx_with_suffix', 'actions': '11'},
                       {'display_name': 'yy'}]), \
            self.mock_create_update() as update_call:
            self.resourceApi.update_lb_rule(
                vs_obj_id, 'xx', actions='22',
                compare_name_suffix='suffix')

            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=vs_obj_id,
                rules=[{'display_name': 'xx', 'actions': '22'},
                       {'display_name': 'yy'}])
            self.assert_called_with_def(update_call, expected_def)

    def test_update_lb_rule_wrong_suffix(self):
        vs_obj_id = '111'
        vs_name = 'name-name'
        with self.mock_get(
                vs_obj_id, vs_name,
                rules=[{'display_name': 'xx_with_suffix', 'actions': '11'},
                       {'display_name': 'yy'}]):
            self.assertRaises(nsxlib_exc.ResourceNotFound,
                              self.resourceApi.update_lb_rule,
                              vs_obj_id, 'xx', actions='22',
                              compare_name_suffix='bad')

    def test_remove_lb_rule(self):
        vs_obj_id = '111'
        vs_name = 'name-name'
        with self.mock_get(vs_obj_id, vs_name,
                           rules=[{'display_name': 'xx'},
                                  {'display_name': 'yy'}]), \
            self.mock_create_update() as update_call:
            self.resourceApi.remove_lb_rule(vs_obj_id, 'xx')

            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=vs_obj_id,
                rules=[{'display_name': 'yy'}])
            self.assert_called_with_def(update_call, expected_def)

    def test_remove_lb_rule_by_suffix(self):
        vs_obj_id = '111'
        vs_name = 'name-name'
        with self.mock_get(vs_obj_id, vs_name,
                           rules=[{'display_name': 'xx_with_suffix'},
                                  {'display_name': 'yy'}]), \
            self.mock_create_update() as update_call:
            self.resourceApi.remove_lb_rule(vs_obj_id, 'with_suffix',
                                            check_name_suffix=True)

            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=vs_obj_id,
                rules=[{'display_name': 'yy'}])
            self.assert_called_with_def(update_call, expected_def)

    def test_remove_lb_rule_wrong_suffix(self):
        vs_obj_id = '111'
        vs_name = 'name-name'
        with self.mock_get(vs_obj_id, vs_name,
                           rules=[{'display_name': 'xx_with_suffix'},
                                  {'display_name': 'yy'}]),\
            self.mock_create_update() as update_call:
            self.resourceApi.remove_lb_rule(vs_obj_id, 'wrong_suffiX',
                                            check_name_suffix=True)

            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=vs_obj_id,
                rules=[{'display_name': 'xx_with_suffix'},
                       {'display_name': 'yy'}])
            self.assert_called_with_def(update_call, expected_def)

    def test_build_access_list_control(self):
        lb_acl = self.resourceApi.build_access_list_control(
            constants.ACTION_ALLOW, 'fake_group_path', True)
        expected_acl_dict = {
            'action': constants.ACTION_ALLOW,
            'enabled': True,
            'group_path': 'fake_group_path'
        }
        self.assertDictEqual(lb_acl.get_obj_dict(), expected_acl_dict)

    def test_wait_until_realized_fail(self):
        vs_id = 'test_vs'
        info = {'state': constants.STATE_UNREALIZED,
                'realization_specific_identifier': vs_id}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.wait_until_realized,
                              vs_id, max_attempts=5, sleep=0.1,
                              tenant=TEST_TENANT)

    def test_wait_until_realized_succeed(self):
        vs_id = 'test_vs'
        info = {'state': constants.STATE_REALIZED,
                'realization_specific_identifier': vs_id,
                'entity_type': 'LbVirtualServerDto'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            actual_info = self.resourceApi.wait_until_realized(
                vs_id, entity_type='LbVirtualServerDto', max_attempts=5,
                sleep=0.1, tenant=TEST_TENANT)
            self.assertEqual(info, actual_info)

    def test_remove_virtual_server_client_ssl_profile_binding(self):
        vs_id = 'test-id'
        vs_name = 'test-name'
        client_binding = {
            'default_certificate_path': '/infra/certificates/test-cert',
            'client_ssl_profile_path': '/infra/lb-client-ssl-profiles/default'}
        server_binding = {
            'ssl_profile_path': '/infra/lb-server-ssl-profiles/test'}
        with self.mock_get(
                vs_id, vs_name, client_ssl_profile_binding=client_binding,
                server_ssl_profile_binding=server_binding), \
            self.mock_create_update() as update_call:
            self.resourceApi.remove_virtual_server_client_ssl_profile_binding(
                vs_id)
            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=vs_id, name=vs_name)
            self.assert_called_with_def(update_call, expected_def)

    def test_remove_dlb_virtual_server_persistence_profile(self):
        vs_id = 'test-id'
        vs_name = 'test-name'
        with self.mock_get(
                vs_id, vs_name, lb_persistence_profile_path='test-profile'), \
                self.mock_create_update() as update_call:
            self.resourceApi.remove_dlb_virtual_server_persistence_profile(
                vs_id)
            expected_def = lb_defs.LBVirtualServerDef(
                virtual_server_id=vs_id, name=vs_name)
            self.assert_called_with_def(update_call, expected_def)


class TestPolicyLBPoolApi(test_resources.NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBPoolApi, self).setUp()
        self.resourceApi = self.policy_lib.load_balancer.lb_pool

    def test_create_with_id(self):
        name = 'd1'
        description = 'desc'
        obj_id = '111'
        members = [
            lb_defs.LBPoolMemberDef(ip_address='10.0.0.1')]
        algorithm = 'algo'
        active_monitor_paths = 'path1'
        member_group = 'group1'
        snat_translation = False
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                lb_pool_id=obj_id,
                description=description,
                members=members,
                active_monitor_paths=active_monitor_paths,
                algorithm=algorithm,
                member_group=member_group,
                snat_translation=snat_translation,
                tcp_multiplexing_enabled=True,
                tcp_multiplexing_number=10,
                tenant=TEST_TENANT)
            expected_def = lb_defs.LBPoolDef(
                lb_pool_id=obj_id,
                name=name,
                description=description,
                members=members,
                active_monitor_paths=active_monitor_paths,
                algorithm=algorithm,
                member_group=member_group,
                snat_translation=snat_translation,
                tcp_multiplexing_enabled=True,
                tcp_multiplexing_number=10,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result)

    def test_create_without_id(self):
        name = 'd1'
        description = 'desc'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                tenant=TEST_TENANT)
            expected_def = lb_defs.LBPoolDef(
                lb_pool_id=mock.ANY,
                name=name,
                description=description,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_create_with_retry_stale_revision(self):
        name = 'd1'
        description = 'desc'
        obj_id = '111'
        members = [
            lb_defs.LBPoolMemberDef(ip_address='10.0.0.1')]
        algorithm = 'algo'
        active_monitor_paths = 'path1'
        member_group = 'group1'
        snat_translation = False
        with mock.patch.object(self.policy_api, "create_or_update",
                               side_effect=nsxlib_exc.StaleRevision
                               ) as api_call:
            with self.assertRaises(nsxlib_exc.StaleRevision):
                self.resourceApi.create_or_overwrite(
                    name,
                    lb_pool_id=obj_id,
                    description=description,
                    members=members,
                    active_monitor_paths=active_monitor_paths,
                    algorithm=algorithm,
                    member_group=member_group,
                    snat_translation=snat_translation,
                    tenant=TEST_TENANT)
                self.assertEqual(nsxlib_testcase.NSX_MAX_ATTEMPTS,
                                 api_call.call_count)

    def test_create_with_retry_pending_delete(self):
        name = 'd1'
        description = 'desc'
        obj_id = '111'
        members = [
            lb_defs.LBPoolMemberDef(ip_address='10.0.0.1')]
        algorithm = 'algo'
        active_monitor_paths = 'path1'
        member_group = 'group1'
        snat_translation = False
        with mock.patch.object(self.policy_api, "create_or_update",
                               side_effect=nsxlib_exc.NsxPendingDelete
                               ) as api_call:
            with self.assertRaises(nsxlib_exc.NsxPendingDelete):
                self.resourceApi.create_or_overwrite(
                    name,
                    lb_pool_id=obj_id,
                    description=description,
                    members=members,
                    active_monitor_paths=active_monitor_paths,
                    algorithm=algorithm,
                    member_group=member_group,
                    snat_translation=snat_translation,
                    tenant=TEST_TENANT)
                self.assertEqual(nsxlib_testcase.NSX_MAX_ATTEMPTS,
                                 api_call.call_count)

    def test_delete(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, tenant=TEST_TENANT)
            expected_def = lb_defs.LBPoolDef(
                lb_pool_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = lb_defs.LBPoolDef(
                lb_pool_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'd1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = lb_defs.LBPoolDef(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = lb_defs.LBPoolDef(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        obj_id = '111'
        name = 'new name'
        description = 'new desc'
        members = [{'ip_address': '10.0.0.1'}]
        algorithm = 'algo'
        active_monitor_paths = ['path1']
        member_group = 'group1'
        snat_translation = False
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}), \
            mock.patch.object(self.policy_api,
                              "create_or_update") as update_call:
            self.resourceApi.update(obj_id,
                                    name=name,
                                    description=description,
                                    members=members,
                                    active_monitor_paths=active_monitor_paths,
                                    algorithm=algorithm,
                                    member_group=member_group,
                                    snat_translation=snat_translation,
                                    tcp_multiplexing_enabled=True,
                                    tcp_multiplexing_number=10,
                                    tenant=TEST_TENANT)
            expected_def = lb_defs.LBPoolDef(
                lb_pool_id=obj_id,
                name=name,
                description=description,
                members=members,
                active_monitor_paths=active_monitor_paths,
                algorithm=algorithm,
                member_group=member_group,
                snat_translation=snat_translation,
                tcp_multiplexing_enabled=True,
                tcp_multiplexing_number=10,
                tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)

    def test_update_without_partial_patch(self):
        obj_id = '111'
        name = 'new name'
        description = 'new desc'
        members = [{'ip_address': '10.0.0.1'}]
        algorithm = 'algo'
        active_monitor_paths = ['path1']
        member_group = 'group1'
        snat_translation = False
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}), \
            mock.patch.object(self.policy_api,
                              "create_or_update") as update_call:
            self.resourceApi.update(obj_id,
                                    name=name,
                                    description=description,
                                    members=members,
                                    active_monitor_paths=active_monitor_paths,
                                    algorithm=algorithm,
                                    member_group=member_group,
                                    snat_translation=snat_translation,
                                    tenant=TEST_TENANT,
                                    allow_partial_updates=False)
            expected_def = lb_defs.LBPoolDef(
                lb_pool_id=obj_id,
                name=name,
                description=description,
                members=members,
                active_monitor_paths=active_monitor_paths,
                algorithm=algorithm,
                member_group=member_group,
                snat_translation=snat_translation,
                tenant=TEST_TENANT)
            update_call.assert_called_with(mock.ANY, partial_updates=False,
                                           force=False)
            self.assert_called_with_def(update_call, expected_def)

    def test_add_monitor_to_pool(self):
        obj_id = '111'
        active_monitor_paths = ['path1']
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}), \
            mock.patch.object(self.policy_api,
                              "create_or_update") as update_call:
            self.resourceApi.add_monitor_to_pool(
                obj_id,
                active_monitor_paths,
                tenant=TEST_TENANT)
            expected_def = lb_defs.LBPoolDef(
                lb_pool_id=obj_id,
                active_monitor_paths=active_monitor_paths,
                tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)

    def test_remove_monitor_from_pool(self):
        obj_id = '111'
        removed_monitor_path = 'path1'
        stay_monitor_path = 'path2'
        active_monitors = [removed_monitor_path, stay_monitor_path]
        with mock.patch.object(
            self.policy_api, "get", return_value={
                'id': obj_id, 'active_monitor_paths': active_monitors}), \
            mock.patch.object(self.policy_api,
                              "create_or_update") as update_call:
            self.resourceApi.remove_monitor_from_pool(
                obj_id,
                removed_monitor_path,
                tenant=TEST_TENANT)
            expected_def = lb_defs.LBPoolDef(
                lb_pool_id=obj_id,
                active_monitor_paths=[stay_monitor_path],
                tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)

    def test_create_pool_member_and_add_to_pool(self):
        obj_id = '111'
        ip_address = '1.1.1.1'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}), \
            mock.patch.object(self.policy_api,
                              "create_or_update") as update_call:
            self.resourceApi.create_pool_member_and_add_to_pool(
                obj_id, ip_address,
                tenant=TEST_TENANT)
            mem_def = lb_defs.LBPoolMemberDef(ip_address)
            expected_def = lb_defs.LBPoolDef(
                lb_pool_id=obj_id,
                members=[mem_def],
                tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)

    def test_update_pool_member(self):
        obj_id = '111'
        ip_address = '1.1.1.1'
        port = '80'
        new_name = 'mem1'
        member = {'ip_address': ip_address, 'port': port,
                  'backup_member': True}
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id,
                                             'members': [member]}), \
            mock.patch.object(self.policy_api,
                              "create_or_update") as update_call:
            self.resourceApi.update_pool_member(
                obj_id, ip_address, port=port, display_name=new_name,
                backup_member=False, tenant=TEST_TENANT)
            new_member = copy.copy(member)
            new_member['display_name'] = new_name
            new_member['backup_member'] = False
            expected_def = lb_defs.LBPoolDef(
                lb_pool_id=obj_id,
                members=[new_member],
                tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)

    def test_wait_until_realized_fail(self):
        pool_id = 'test_pool'
        info = {'state': constants.STATE_UNREALIZED,
                'realization_specific_identifier': pool_id}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.wait_until_realized,
                              pool_id, max_attempts=5, sleep=0.1,
                              tenant=TEST_TENANT)

    def test_wait_until_realized_succeed(self):
        pool_id = 'test_pool'
        info = {'state': constants.STATE_REALIZED,
                'realization_specific_identifier': pool_id,
                'entity_type': 'LbPoolDto'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            actual_info = self.resourceApi.wait_until_realized(
                pool_id, entity_type='LbPoolDto', max_attempts=5,
                sleep=0.1, tenant=TEST_TENANT)
            self.assertEqual(info, actual_info)


class TestPolicyLBMonitorProfileHttpApi(test_resources.NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBMonitorProfileHttpApi, self).setUp()
        self.resourceApi = (
            self.policy_lib.load_balancer.lb_monitor_profile_http)
        self.obj_def = lb_defs.LBHttpMonitorProfileDef

    def test_create_with_id(self):
        name = 'd1'
        obj_id = '111'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                lb_monitor_profile_id=obj_id,
                name=name,
                tenant=TEST_TENANT)
            expected_def = self.obj_def(
                lb_monitor_profile_id=obj_id,
                name=name,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result)

    def test_create_without_id(self):
        name = 'd1'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name=name,
                tenant=TEST_TENANT)
            expected_def = self.obj_def(
                lb_monitor_profile_id=mock.ANY,
                name=name,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, tenant=TEST_TENANT)
            expected_def = self.obj_def(
                lb_monitor_profile_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = self.obj_def(
                lb_monitor_profile_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'd1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = self.obj_def(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = self.obj_def(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        obj_id = '111'
        name = 'new name'
        with self.mock_get(obj_id, name), \
            self.mock_create_update() as update_call:

            self.resourceApi.update(obj_id,
                                    name=name,
                                    tenant=TEST_TENANT)
            expected_def = self.obj_def(
                lb_monitor_profile_id=obj_id,
                name=name,
                tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)


class TestPolicyLBMonitorProfileHttpsApi(TestPolicyLBMonitorProfileHttpApi):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBMonitorProfileHttpsApi, self).setUp()
        self.resourceApi = (
            self.policy_lib.load_balancer.lb_monitor_profile_https)
        self.obj_def = lb_defs.LBHttpsMonitorProfileDef


class TestPolicyLBMonitorProfileUdpApi(TestPolicyLBMonitorProfileHttpApi):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBMonitorProfileUdpApi, self).setUp()
        self.resourceApi = (
            self.policy_lib.load_balancer.lb_monitor_profile_udp)
        self.obj_def = lb_defs.LBUdpMonitorProfileDef


class TestPolicyLBMonitorProfileIcmpApi(TestPolicyLBMonitorProfileHttpApi):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBMonitorProfileIcmpApi, self).setUp()
        self.resourceApi = (
            self.policy_lib.load_balancer.lb_monitor_profile_icmp)
        self.obj_def = lb_defs.LBIcmpMonitorProfileDef


class TestPolicyLBMonitorProfileTcpApi(TestPolicyLBMonitorProfileHttpApi):

    def setUp(self, *args, **kwargs):
        super(TestPolicyLBMonitorProfileTcpApi, self).setUp()
        self.resourceApi = (
            self.policy_lib.load_balancer.lb_monitor_profile_tcp)
        self.obj_def = lb_defs.LBTcpMonitorProfileDef

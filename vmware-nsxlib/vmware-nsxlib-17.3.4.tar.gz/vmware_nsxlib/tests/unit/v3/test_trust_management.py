# Copyright 2019 VMware, Inc.
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

from unittest import mock

from vmware_nsxlib.tests.unit.v3 import nsxlib_testcase
from vmware_nsxlib.tests.unit.v3 import test_constants as consts


class TestNsxLibTrustManagement(nsxlib_testcase.NsxClientTestCase):

    def test_create_cert_list(self):
        fake_cert_list = consts.FAKE_CERT_LIST
        fake_pem = (fake_cert_list[0]['pem_encoded'] +
                    fake_cert_list[1]['pem_encoded'])
        fake_private_key = 'fake_key'
        cert_api = self.nsxlib.trust_management
        body = {
            'pem_encoded': fake_pem,
            'private_key': fake_private_key,
            'tags': consts.FAKE_TAGS
        }
        with mock.patch.object(self.nsxlib.client, 'create') as create:
            cert_api.create_cert_list(
                cert_pem=fake_pem,
                private_key=fake_private_key,
                tags=consts.FAKE_TAGS)
            create.assert_called_with(
                'trust-management/certificates?action=import',
                body)

    def test_find_cert_with_pem_empty(self):
        pem = 'abc'
        with mock.patch.object(self.nsxlib.client, 'get',
                               return_value={'results': []}):
            results = self.nsxlib.trust_management.find_cert_with_pem(pem)
            self.assertEqual(0, len(results))

    def test_find_cert_with_pem_found(self):
        pem = consts.FAKE_CERT_PEM
        with mock.patch.object(
            self.nsxlib.client, 'get',
            return_value={'results': consts.FAKE_CERT_LIST}):
            results = self.nsxlib.trust_management.find_cert_with_pem(pem)
            self.assertEqual(1, len(results))

    def test_find_cert_with_pem_rn_found(self):
        pem = consts.FAKE_CERT_PEM.replace('\n', '\r\n')
        with mock.patch.object(
            self.nsxlib.client, 'get',
            return_value={'results': consts.FAKE_CERT_LIST}):
            results = self.nsxlib.trust_management.find_cert_with_pem(pem)
            self.assertEqual(1, len(results))

    def test_create_identity_with_cert(self):
        fake_pem = consts.FAKE_CERT_PEM
        name = "test-identity"
        cert_api = self.nsxlib.trust_management
        body = {
            'name': name,
            'certificate_pem': fake_pem,
            'node_id': 'test_node_id',
            'role': 'enterprise_admin',
            'is_protected': True
        }
        with mock.patch.object(self.nsxlib.client, 'create') as create:
            cert_api.create_identity_with_cert(
                name=name,
                cert_pem=fake_pem,
                node_id='test_node_id',
                role='enterprise_admin')
            create.assert_called_with(
                'trust-management/principal-identities/with-certificate',
                body)

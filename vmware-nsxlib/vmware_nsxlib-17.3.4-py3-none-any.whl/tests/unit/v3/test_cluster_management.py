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


class TestNsxLibClusterManagement(nsxlib_testcase.NsxClientTestCase):

    def test_get_restore_status(self):
        cluster_api = self.nsxlib.cluster_management
        with mock.patch.object(self.nsxlib.client, 'get') as get:
            cluster_api.get_restore_status()
            get.assert_called_with('cluster/restore/status')

# Copyright 2020 Antoine Musso
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import collections
from unittest import mock

from tests.base import BaseTestCase
from zuul.lib.ansible import AnsibleManager


class TestLibAnsibleManager(BaseTestCase):

    @mock.patch('zuul.lib.ansible.AnsibleManager.load_ansible_config')
    @mock.patch('zuul.lib.ansible.AnsibleManager._validate_packages')
    @mock.patch('zuul.lib.ansible.AnsibleManager._validate_ansible')
    def test_validate_remembers_failures(self,
                                         mock_validate_ansible,
                                         mock_validate_packages, _):

        okish = mock.Mock(
            'subprocess.CompletedProcess',
            returncode=0, stdout=b'Some valid ansible infos\n')
        okish.returncode

        am = AnsibleManager()
        am._supported_versions = collections.OrderedDict([
            ('1.0', False),
            ('2.8', True),
        ])

        mock_validate_packages.side_effect = am._supported_versions.values()
        mock_validate_ansible.side_effect = am._supported_versions.values()
        self.assertFalse(
            am.validate(),
            'A valid ansible should not mask a previous failure')

        self.assertEquals(
            [mock.call('1.0'),
             mock.call('2.8')
            ],
            mock_validate_ansible.mock_calls)

        self.assertEquals(
            [mock.call('2.8')],
            mock_validate_packages.mock_calls)

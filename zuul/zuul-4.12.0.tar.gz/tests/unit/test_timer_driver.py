# Copyright 2021 Acme Gating, LLC
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

from tests.base import ZuulTestCase, iterate_timeout


class TestTimerTwoTenants(ZuulTestCase):
    tenant_config_file = 'config/timer-two-tenant/main.yaml'

    def test_timer_two_tenants(self):
        # The pipeline triggers every second.  Wait until we have 4
        # jobs (2 from each tenant).
        for _ in iterate_timeout(60, 'jobs started'):
            if len(self.history) >= 4:
                break

        tenant_one_projects = set()
        tenant_two_projects = set()
        for h in self.history:
            if h.parameters['zuul']['tenant'] == 'tenant-one':
                tenant_one_projects.add((h.parameters['items'][0]['project']))
            if h.parameters['zuul']['tenant'] == 'tenant-two':
                tenant_two_projects.add((h.parameters['items'][0]['project']))

        # Verify that the right job ran in the right tenant
        self.assertEqual(tenant_one_projects, {'org/project1'})
        self.assertEqual(tenant_two_projects, {'org/project2'})

        # Stop running timer jobs so the assertions don't race.
        self.commitConfigUpdate('common-config', 'layouts/no-timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

# Copyright 2017 Red Hat, Inc.
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

import base64
import os

from zuul.lib import yamlutil as yaml

from tests.base import AnsibleZuulTestCase
from tests.base import ZuulTestCase


class TestInventoryBase(ZuulTestCase):

    config_file = 'zuul-gerrit-github.conf'
    tenant_config_file = 'config/inventory/main.yaml'
    use_gerrit = True

    def setUp(self, python_path=None, shell_type=None):
        super(TestInventoryBase, self).setUp()
        if python_path:
            self.fake_nodepool.python_path = python_path
        if shell_type:
            self.fake_nodepool.shell_type = shell_type
        self.executor_server.hold_jobs_in_build = True
        self.hold_jobs_in_queue = True

        if self.use_gerrit:
            A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
            self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        else:
            A = self.fake_github.openFakePullRequest(
                'org/project3', 'master', 'A')
            self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.change_A = A

        self.waitUntilSettled()

    def tearDown(self):
        self.cancelExecutorJobs()
        self.waitUntilSettled()
        super(TestInventoryBase, self).tearDown()

    def _get_build_inventory(self, name):
        self.runJob(name)

        build = self.getBuildByName(name)
        inv_path = os.path.join(build.jobdir.root, 'ansible', 'inventory.yaml')
        inventory = yaml.safe_load(open(inv_path, 'r'))
        return inventory

    def _get_setup_inventory(self, name):
        self.runJob(name)

        build = self.getBuildByName(name)
        setup_inv_path = build.jobdir.setup_playbook.inventory
        return yaml.ansible_unsafe_load(open(setup_inv_path, 'r'))

    def runJob(self, name):
        self.hold_jobs_in_queue = False
        self.executor_api.release(f'^{name}$')
        self.waitUntilSettled()

    def cancelExecutorJobs(self):
        if self.use_gerrit:
            self.fake_gerrit.addEvent(
                self.change_A.getChangeAbandonedEvent())
        else:
            self.fake_github.emitEvent(
                self.change_A.getPullRequestClosedEvent())


class TestInventoryGithub(TestInventoryBase):

    use_gerrit = False

    def test_single_inventory(self):

        inventory = self._get_build_inventory('single-inventory')

        all_nodes = ('ubuntu-xenial',)
        self.assertIn('all', inventory)
        self.assertIn('hosts', inventory['all'])
        self.assertIn('vars', inventory['all'])
        for node_name in all_nodes:
            self.assertIn(node_name, inventory['all']['hosts'])
            node_vars = inventory['all']['hosts'][node_name]
            self.assertEqual(
                'auto', node_vars['ansible_python_interpreter'])
        self.assertIn('zuul', inventory['all']['vars'])
        self.assertIn('attempts', inventory['all']['vars']['zuul'])
        self.assertEqual(1, inventory['all']['vars']['zuul']['attempts'])
        z_vars = inventory['all']['vars']['zuul']
        self.assertIn('executor', z_vars)
        self.assertIn('src_root', z_vars['executor'])
        self.assertIn('job', z_vars)
        self.assertIn('event_id', z_vars)
        self.assertEqual(z_vars['job'], 'single-inventory')
        self.assertEqual(z_vars['message'], 'QQ==')
        self.assertEqual(z_vars['change_url'],
                         'https://github.com/org/project3/pull/1')

        self.executor_server.release()
        self.waitUntilSettled()


class TestInventoryPythonPath(TestInventoryBase):

    def setUp(self):
        super(TestInventoryPythonPath, self).setUp(python_path='fake-python')

    def test_single_inventory(self):
        inventory = self._get_build_inventory('single-inventory')

        all_nodes = ('ubuntu-xenial',)
        self.assertIn('all', inventory)
        self.assertIn('hosts', inventory['all'])
        self.assertIn('vars', inventory['all'])
        for node_name in all_nodes:
            self.assertIn(node_name, inventory['all']['hosts'])
            node_vars = inventory['all']['hosts'][node_name]
            self.assertEqual(
                'fake-python', node_vars['ansible_python_interpreter'])

        self.assertIn('zuul', inventory['all']['vars'])
        z_vars = inventory['all']['vars']['zuul']
        self.assertIn('executor', z_vars)
        self.assertIn('src_root', z_vars['executor'])
        self.assertIn('job', z_vars)
        self.assertEqual(z_vars['job'], 'single-inventory')
        self.assertEqual(z_vars['message'], 'QQ==')

        self.executor_server.release()
        self.waitUntilSettled()


class TestInventoryShellType(TestInventoryBase):

    def setUp(self):
        super(TestInventoryShellType, self).setUp(shell_type='cmd')

    def test_single_inventory(self):
        inventory = self._get_build_inventory('single-inventory')

        all_nodes = ('ubuntu-xenial',)
        self.assertIn('all', inventory)
        self.assertIn('hosts', inventory['all'])
        self.assertIn('vars', inventory['all'])
        for node_name in all_nodes:
            self.assertIn(node_name, inventory['all']['hosts'])
            node_vars = inventory['all']['hosts'][node_name]
            self.assertEqual(
                'cmd', node_vars['ansible_shell_type'])

        self.assertIn('zuul', inventory['all']['vars'])
        z_vars = inventory['all']['vars']['zuul']
        self.assertIn('executor', z_vars)
        self.assertIn('src_root', z_vars['executor'])
        self.assertIn('job', z_vars)
        self.assertEqual(z_vars['job'], 'single-inventory')
        self.assertEqual(z_vars['message'], 'QQ==')

        self.executor_server.release()
        self.waitUntilSettled()


class TestInventoryAutoPython(TestInventoryBase):

    def test_auto_python_ansible28_inventory(self):
        inventory = self._get_build_inventory('ansible-version28-inventory')

        all_nodes = ('ubuntu-xenial',)
        self.assertIn('all', inventory)
        self.assertIn('hosts', inventory['all'])
        self.assertIn('vars', inventory['all'])
        for node_name in all_nodes:
            self.assertIn(node_name, inventory['all']['hosts'])
            node_vars = inventory['all']['hosts'][node_name]
            self.assertEqual(
                'auto', node_vars['ansible_python_interpreter'])

        self.assertIn('zuul', inventory['all']['vars'])
        z_vars = inventory['all']['vars']['zuul']
        self.assertIn('executor', z_vars)
        self.assertIn('src_root', z_vars['executor'])
        self.assertIn('job', z_vars)
        self.assertEqual(z_vars['job'], 'ansible-version28-inventory')
        self.assertEqual(z_vars['message'], 'QQ==')

        self.executor_server.release()
        self.waitUntilSettled()


class TestInventory(TestInventoryBase):

    def test_single_inventory(self):

        inventory = self._get_build_inventory('single-inventory')

        all_nodes = ('ubuntu-xenial',)
        self.assertIn('all', inventory)
        self.assertIn('hosts', inventory['all'])
        self.assertIn('vars', inventory['all'])
        for node_name in all_nodes:
            self.assertIn(node_name, inventory['all']['hosts'])
            node_vars = inventory['all']['hosts'][node_name]
            self.assertEqual(
                'auto', node_vars['ansible_python_interpreter'])
            self.assertNotIn(
                'ansible_shell_type', node_vars)
        self.assertIn('zuul', inventory['all']['vars'])
        self.assertIn('attempts', inventory['all']['vars']['zuul'])
        self.assertEqual(1, inventory['all']['vars']['zuul']['attempts'])
        z_vars = inventory['all']['vars']['zuul']
        self.assertIn('executor', z_vars)
        self.assertIn('src_root', z_vars['executor'])
        self.assertIn('job', z_vars)
        self.assertEqual(z_vars['job'], 'single-inventory')
        self.assertEqual(z_vars['message'], 'QQ==')

        self.executor_server.release()
        self.waitUntilSettled()

    def test_single_inventory_list(self):

        inventory = self._get_build_inventory('single-inventory-list')

        all_nodes = ('compute', 'controller')
        self.assertIn('all', inventory)
        self.assertIn('hosts', inventory['all'])
        self.assertIn('vars', inventory['all'])
        for node_name in all_nodes:
            self.assertIn(node_name, inventory['all']['hosts'])
        self.assertIn('zuul', inventory['all']['vars'])
        z_vars = inventory['all']['vars']['zuul']
        self.assertIn('executor', z_vars)
        self.assertIn('src_root', z_vars['executor'])
        self.assertIn('job', z_vars)
        self.assertEqual(z_vars['job'], 'single-inventory-list')

        self.executor_server.release()
        self.waitUntilSettled()

    def test_executor_only_inventory(self):
        inventory = self._get_build_inventory('executor-only-inventory')

        self.assertIn('all', inventory)
        self.assertIn('hosts', inventory['all'])
        self.assertIn('vars', inventory['all'])

        # Should be blank; i.e. rely on the implicit localhost
        self.assertEqual(0, len(inventory['all']['hosts']))

        self.assertIn('zuul', inventory['all']['vars'])
        z_vars = inventory['all']['vars']['zuul']
        self.assertIn('executor', z_vars)
        self.assertIn('src_root', z_vars['executor'])
        self.assertIn('job', z_vars)
        self.assertEqual(z_vars['job'], 'executor-only-inventory')
        self.assertEqual(z_vars['message'], 'QQ==')

        self.executor_server.release()
        self.waitUntilSettled()

    def test_group_inventory(self):

        inventory = self._get_build_inventory('group-inventory')

        all_nodes = ('controller', 'compute1', 'compute2')
        self.assertIn('all', inventory)
        self.assertIn('children', inventory['all'])
        self.assertIn('hosts', inventory['all'])
        self.assertIn('vars', inventory['all'])
        for group_name in ('ceph-osd', 'ceph-monitor'):
            self.assertIn(group_name, inventory['all']['children'])
        for node_name in all_nodes:
            self.assertIn(node_name, inventory['all']['hosts'])
            self.assertIn(node_name,
                          inventory['all']['children']
                          ['ceph-monitor']['hosts'])
        self.assertEqual(
            'auto',
            inventory['all']['hosts']['controller']
            ['ansible_python_interpreter'])
        self.assertEqual(
            'ceph',
            inventory['all']['hosts']['controller']
            ['ceph_var'])
        self.assertEqual(
            'auto',
            inventory['all']['hosts']['compute1']
            ['ansible_python_interpreter'])
        self.assertNotIn(
            'ceph_var',
            inventory['all']['hosts']['compute1'])
        self.assertIn('zuul', inventory['all']['vars'])
        z_vars = inventory['all']['vars']['zuul']
        self.assertIn('executor', z_vars)
        self.assertIn('src_root', z_vars['executor'])
        self.assertIn('job', z_vars)
        self.assertEqual(z_vars['job'], 'group-inventory')

        self.executor_server.release()
        self.waitUntilSettled()

    def test_hostvars_inventory(self):

        inventory = self._get_build_inventory('hostvars-inventory')

        all_nodes = ('default', 'fakeuser')
        self.assertIn('all', inventory)
        self.assertIn('hosts', inventory['all'])
        self.assertIn('vars', inventory['all'])
        for node_name in all_nodes:
            self.assertIn(node_name, inventory['all']['hosts'])
            # check if the nodes use the correct username
            if node_name == 'fakeuser':
                username = 'fakeuser'
            else:
                username = 'zuul'
            self.assertEqual(
                inventory['all']['hosts'][node_name]['ansible_user'], username)

            # check if the nodes use the correct or no ansible_connection
            if node_name == 'windows':
                self.assertEqual(
                    inventory['all']['hosts'][node_name]['ansible_connection'],
                    'winrm')
            else:
                self.assertEqual(
                    'local',
                    inventory['all']['hosts'][node_name]['ansible_connection'])

            self.assertEqual(
                'auto',
                inventory['all']['hosts'][node_name]
                ['ansible_python_interpreter'])
            self.assertEqual(
                'all',
                inventory['all']['hosts'][node_name]
                ['all_var'])
        self.assertNotIn(
            'ansible_python_interpreter',
            inventory['all']['vars'])

        self.executor_server.release()
        self.waitUntilSettled()

    def test_setup_inventory(self):

        setup_inventory = self._get_setup_inventory('hostvars-inventory')
        inventory = self._get_build_inventory('hostvars-inventory')

        self.assertIn('all', inventory)
        self.assertIn('hosts', inventory['all'])

        self.assertIn('default', setup_inventory['all']['hosts'])
        self.assertIn('fakeuser', setup_inventory['all']['hosts'])
        self.assertIn('windows', setup_inventory['all']['hosts'])
        self.assertNotIn('network', setup_inventory['all']['hosts'])
        self.assertIn('default', inventory['all']['hosts'])
        self.assertIn('fakeuser', inventory['all']['hosts'])
        self.assertIn('windows', inventory['all']['hosts'])
        self.assertIn('network', inventory['all']['hosts'])

        self.executor_server.release()
        self.waitUntilSettled()


class TestAnsibleInventory(AnsibleZuulTestCase):

    config_file = 'zuul-gerrit-github.conf'
    tenant_config_file = 'config/inventory/main.yaml'

    def _get_file(self, build, path):
        p = os.path.join(build.jobdir.root, path)
        with open(p) as f:
            return f.read()

    def _jinja2_message(self, expected_message):

        # This test runs a bit long and needs extra time.
        self.wait_timeout = 120
        # Keep the jobdir around to check inventory
        self.executor_server.keep_jobdir = True
        # Output extra ansible info so we might see errors.
        self.executor_server.verbose = True
        A = self.fake_gerrit.addFakeChange(
            'org/project2', 'master', expected_message)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='jinja2-message', result='SUCCESS', changes='1,1')])

        build = self.history[0]
        inv_path = os.path.join(build.jobdir.root, 'ansible', 'inventory.yaml')
        inventory = yaml.safe_load(open(inv_path, 'r'))

        zv_path = os.path.join(build.jobdir.root, 'ansible', 'zuul_vars.yaml')
        zv = yaml.safe_load(open(zv_path, 'r'))

        # TODO(corvus): zuul vars aren't really stored here anymore;
        # rework these tests to examine them separately.
        inventory['all']['vars'] = {'zuul': zv['zuul']}

        decoded_message = base64.b64decode(
            inventory['all']['vars']['zuul']['message']).decode('utf-8')
        self.assertEqual(decoded_message, expected_message)

        obtained_message = self._get_file(self.history[0],
                                          'work/logs/commit-message.txt')

        self.assertEqual(obtained_message, expected_message)

    def test_jinja2_message_brackets(self):
        self._jinja2_message("This message has {{ jinja2 }} in it ")

    def test_jinja2_message_raw(self):
        self._jinja2_message("This message has {% raw %} in {% endraw %} it ")


class TestWindowsInventory(TestInventoryBase):
    config_file = 'zuul-winrm.conf'

    def test_windows_inventory(self):

        inventory = self._get_build_inventory('hostvars-inventory')
        windows_host = inventory['all']['hosts']['windows']
        self.assertEqual(windows_host['ansible_connection'], 'winrm')
        self.assertEqual(
            windows_host['ansible_winrm_operation_timeout_sec'],
            '120')
        self.assertEqual(
            windows_host['ansible_winrm_read_timeout_sec'],
            '180')

        self.executor_server.release()
        self.waitUntilSettled()

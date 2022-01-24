# Copyright 2014 Hewlett-Packard Development Company, L.P.
# Copyright 2014 Rackspace Australia
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

import os
import urllib.parse
import socket
import textwrap
import time
import jwt
import sys
import subprocess
import threading
from unittest import skip

import requests

import zuul.web
import zuul.rpcclient

from tests.base import ZuulTestCase, AnsibleZuulTestCase
from tests.base import ZuulWebFixture, FIXTURE_DIR, iterate_timeout
from tests.base import simple_layout


class FakeConfig(object):

    def __init__(self, config):
        self.config = config or {}

    def has_option(self, section, option):
        return option in self.config.get(section, {})

    def get(self, section, option):
        return self.config.get(section, {}).get(option)


class BaseWithWeb(ZuulTestCase):
    config_ini_data = {}

    def startWebServer(self):
        self.zuul_ini_config = FakeConfig(self.config_ini_data)
        # Start the web server
        self.web = self.useFixture(
            ZuulWebFixture(self.changes, self.config,
                           self.additional_event_queues, self.upstream_root,
                           self.rpcclient, self.poller_events,
                           self.git_url_with_auth, self.addCleanup,
                           self.test_root,
                           info=zuul.model.WebInfo.fromConfig(
                               self.zuul_ini_config)))

        self.executor_server.hold_jobs_in_build = True

        self.host = 'localhost'
        self.port = self.web.port
        # Wait until web server is started
        while True:
            try:
                with socket.create_connection((self.host, self.port)):
                    break
            except ConnectionRefusedError:
                pass
        self.base_url = "http://{host}:{port}".format(
            host=self.host, port=self.port)

    def get_url(self, url, *args, **kwargs):
        return requests.get(
            urllib.parse.urljoin(self.base_url, url), *args, **kwargs)

    def post_url(self, url, *args, **kwargs):
        return requests.post(
            urllib.parse.urljoin(self.base_url, url), *args, **kwargs)

    def delete_url(self, url, *args, **kwargs):
        return requests.delete(
            urllib.parse.urljoin(self.base_url, url), *args, **kwargs)

    def options_url(self, url, *args, **kwargs):
        return requests.options(
            urllib.parse.urljoin(self.base_url, url), *args, **kwargs)


class BaseTestWeb(BaseWithWeb):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def setUp(self):
        super(BaseTestWeb, self).setUp()
        self.startWebServer()

    def add_base_changes(self):
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

    def tearDown(self):
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        super(BaseTestWeb, self).tearDown()


class TestWeb(BaseTestWeb):

    def test_web_index(self):
        "Test that we can retrieve the index page"
        resp = self.get_url('api')
        data = resp.json()
        # no point checking the whole thing; just make sure _something_ we
        # expect is here
        self.assertIn('info', data)

    def test_web_status(self):
        "Test that we can retrieve JSON status info"
        self.add_base_changes()
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.executor_server.release('project-merge')
        self.waitUntilSettled()

        resp = self.get_url("api/tenant/tenant-one/status")
        self.assertIn('Content-Length', resp.headers)
        self.assertIn('Content-Type', resp.headers)
        self.assertEqual(
            'application/json; charset=utf-8', resp.headers['Content-Type'])
        self.assertIn('Access-Control-Allow-Origin', resp.headers)
        self.assertIn('Cache-Control', resp.headers)
        self.assertIn('Last-Modified', resp.headers)
        self.assertTrue(resp.headers['Last-Modified'].endswith(' GMT'))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        data = resp.json()
        status_jobs = []
        self.assertEqual(
            data["connection_event_queues"]["gerrit"]["length"], 0)

        for p in data['pipelines']:
            self.assertEqual(p["trigger_events"], 0)
            self.assertEqual(p["result_events"], 0)
            self.assertEqual(p["management_events"], 0)
            self.assertIn('manager', p, p)
            self.assertTrue(len(p.get('triggers', [])) > 0, p)
            for q in p['change_queues']:
                if p['name'] in ['gate', 'conflict']:
                    self.assertEqual(q['window'], 20)
                else:
                    self.assertEqual(q['window'], 0)
                # This test uses unbranched queues so validate that the branch
                # information is missing.
                self.assertIsNone(q['branch'])
                for head in q['heads']:
                    for change in head:
                        self.assertIn(
                            'review.example.com/org/project',
                            change['project_canonical'])
                        self.assertTrue(change['active'])
                        self.assertIn(change['id'], ('1,1', '2,1', '3,1'))
                        for job in change['jobs']:
                            status_jobs.append(job)
        self.assertEqual('project-merge', status_jobs[0]['name'])
        # TODO(mordred) pull uuids from self.builds
        self.assertEqual(
            'stream/{uuid}?logfile=console.log'.format(
                uuid=status_jobs[0]['uuid']),
            status_jobs[0]['url'])
        self.assertEqual(
            'finger://{hostname}/{uuid}'.format(
                hostname=self.executor_server.hostname,
                uuid=status_jobs[0]['uuid']),
            status_jobs[0]['finger_url'])
        self.assertEqual(
            'https://zuul.example.com/t/tenant-one/build/{uuid}'.format(
                uuid=status_jobs[0]['uuid']),
            status_jobs[0]['report_url'])
        self.assertEqual('project-test1', status_jobs[1]['name'])
        self.assertEqual(
            'stream/{uuid}?logfile=console.log'.format(
                uuid=status_jobs[1]['uuid']),
            status_jobs[1]['url'])
        self.assertEqual(
            'finger://{hostname}/{uuid}'.format(
                hostname=self.executor_server.hostname,
                uuid=status_jobs[1]['uuid']),
            status_jobs[1]['finger_url'])
        self.assertEqual(
            'https://zuul.example.com/t/tenant-one/build/{uuid}'.format(
                uuid=status_jobs[1]['uuid']),
            status_jobs[1]['report_url'])

        self.assertEqual('project-test2', status_jobs[2]['name'])
        self.assertEqual(
            'stream/{uuid}?logfile=console.log'.format(
                uuid=status_jobs[2]['uuid']),
            status_jobs[2]['url'])
        self.assertEqual(
            'finger://{hostname}/{uuid}'.format(
                hostname=self.executor_server.hostname,
                uuid=status_jobs[2]['uuid']),
            status_jobs[2]['finger_url'])
        self.assertEqual(
            'https://zuul.example.com/t/tenant-one/build/{uuid}'.format(
                uuid=status_jobs[2]['uuid']),
            status_jobs[2]['report_url'])

        # check job dependencies
        self.assertIsNotNone(status_jobs[0]['dependencies'])
        self.assertIsNotNone(status_jobs[1]['dependencies'])
        self.assertIsNotNone(status_jobs[2]['dependencies'])
        self.assertEqual(len(status_jobs[0]['dependencies']), 0)
        self.assertEqual(len(status_jobs[1]['dependencies']), 1)
        self.assertEqual(len(status_jobs[2]['dependencies']), 1)
        self.assertIn('project-merge', status_jobs[1]['dependencies'])
        self.assertIn('project-merge', status_jobs[2]['dependencies'])

    def test_web_components(self):
        "Test that we can retrieve the list of connected components"
        resp = self.get_url("api/components")
        data = resp.json()

        # The list should contain one of each kind: executor, scheduler, web
        self.assertEqual(len(data), 3)
        self.assertEqual(len(data["executor"]), 1)
        self.assertEqual(len(data["scheduler"]), self.scheduler_count)
        self.assertEqual(len(data["web"]), 1)

        # Each component should contain hostname and state information
        for key in ["hostname", "state", "version"]:
            self.assertIn(key, data["executor"][0])
            self.assertIn(key, data["scheduler"][0])
            self.assertIn(key, data["web"][0])

    def test_web_tenants(self):
        "Test that we can retrieve JSON status info"
        self.add_base_changes()
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.executor_server.release('project-merge')
        self.waitUntilSettled()

        resp = self.get_url("api/tenants")
        self.assertIn('Content-Length', resp.headers)
        self.assertIn('Content-Type', resp.headers)
        self.assertEqual(
            'application/json; charset=utf-8', resp.headers['Content-Type'])
        # self.assertIn('Access-Control-Allow-Origin', resp.headers)
        # self.assertIn('Cache-Control', resp.headers)
        # self.assertIn('Last-Modified', resp.headers)
        data = resp.json()

        self.assertEqual('tenant-one', data[0]['name'])
        self.assertEqual(3, data[0]['projects'])
        self.assertEqual(3, data[0]['queue'])

        # release jobs and check if the queue size is 0
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        data = self.get_url("api/tenants").json()
        self.assertEqual('tenant-one', data[0]['name'])
        self.assertEqual(3, data[0]['projects'])
        self.assertEqual(0, data[0]['queue'])

        # test that non-live items are not counted
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B.setDependsOn(A, 1)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        data = self.get_url("api/tenants").json()

        self.assertEqual('tenant-one', data[0]['name'])
        self.assertEqual(3, data[0]['projects'])
        self.assertEqual(1, data[0]['queue'])

    def test_web_connections_list(self):
        data = self.get_url('api/connections').json()
        connection = {
            'driver': 'gerrit',
            'name': 'gerrit',
            'baseurl': 'https://review.example.com',
            'canonical_hostname': 'review.example.com',
            'server': 'review.example.com',
            'port': 29418,
        }
        self.assertEqual([connection], data)

    def test_web_bad_url(self):
        # do we redirect to index.html
        resp = self.get_url("status/foo")
        self.assertEqual(200, resp.status_code)

    def test_web_find_change(self):
        # can we filter by change id
        self.add_base_changes()
        data = self.get_url("api/tenant/tenant-one/status/change/1,1").json()

        self.assertEqual(1, len(data), data)
        self.assertEqual("org/project", data[0]['project'])

        data = self.get_url("api/tenant/tenant-one/status/change/2,1").json()

        self.assertEqual(1, len(data), data)
        self.assertEqual("org/project1", data[0]['project'], data)

    def test_web_find_job(self):
        # can we fetch the variants for a single job
        data = self.get_url('api/tenant/tenant-one/job/project-test1').json()

        common_config_role = {
            'implicit': True,
            'project_canonical_name': 'review.example.com/common-config',
            'target_name': 'common-config',
            'type': 'zuul',
        }
        source_ctx = {
            'branch': 'master',
            'path': 'zuul.yaml',
            'project': 'common-config',
        }
        run = [{
            'path': 'playbooks/project-test1.yaml',
            'roles': [{
                'implicit': True,
                'project_canonical_name': 'review.example.com/common-config',
                'target_name': 'common-config',
                'type': 'zuul'
            }],
            'secrets': [],
            'source_context': source_ctx,
        }]

        self.assertEqual([
            {
                'name': 'project-test1',
                'abstract': False,
                'ansible_version': None,
                'attempts': 4,
                'branches': [],
                'dependencies': [],
                'description': None,
                'files': [],
                'intermediate': False,
                'irrelevant_files': [],
                'match_on_config_updates': True,
                'final': False,
                'nodeset': {
                    'groups': [],
                    'name': '',
                    'nodes': [{'comment': None,
                               'hold_job': None,
                               'id': None,
                               'label': 'label1',
                               'name': 'controller',
                               'aliases': [],
                               'state': 'unknown',
                               'user_data': None}],
                },
                'override_checkout': None,
                'parent': 'base',
                'post_review': None,
                'protected': None,
                'provides': [],
                'required_projects': [],
                'requires': [],
                'roles': [common_config_role],
                'run': run,
                'pre_run': [],
                'post_run': [],
                'cleanup_run': [],
                'semaphores': [],
                'source_context': source_ctx,
                'tags': [],
                'timeout': None,
                'variables': {},
                'extra_variables': {},
                'group_variables': {},
                'host_variables': {},
                'variant_description': '',
                'voting': True,
                'workspace_scheme': 'golang'
            }, {
                'name': 'project-test1',
                'abstract': False,
                'ansible_version': None,
                'attempts': 3,
                'branches': ['stable'],
                'dependencies': [],
                'description': None,
                'files': [],
                'intermediate': False,
                'irrelevant_files': [],
                'match_on_config_updates': True,
                'final': False,
                'nodeset': {
                    'groups': [],
                    'name': '',
                    'nodes': [{'comment': None,
                               'hold_job': None,
                               'id': None,
                               'label': 'label2',
                               'name': 'controller',
                               'aliases': [],
                               'state': 'unknown',
                               'user_data': None}],
                },
                'override_checkout': None,
                'parent': 'base',
                'post_review': None,
                'protected': None,
                'provides': [],
                'required_projects': [],
                'requires': [],
                'roles': [common_config_role],
                'run': run,
                'pre_run': [],
                'post_run': [],
                'cleanup_run': [],
                'semaphores': [],
                'source_context': source_ctx,
                'tags': [],
                'timeout': None,
                'variables': {},
                'extra_variables': {},
                'group_variables': {},
                'host_variables': {},
                'variant_description': 'stable',
                'voting': True,
                'workspace_scheme': 'golang'
            }], data)

        data = self.get_url('api/tenant/tenant-one/job/test-job').json()
        run[0]['path'] = 'playbooks/project-merge.yaml'
        self.assertEqual([
            {
                'abstract': False,
                'ansible_version': None,
                'attempts': 3,
                'branches': [],
                'dependencies': [],
                'description': None,
                'files': [],
                'final': False,
                'intermediate': False,
                'irrelevant_files': [],
                'match_on_config_updates': True,
                'name': 'test-job',
                'override_checkout': None,
                'parent': 'base',
                'post_review': None,
                'protected': None,
                'provides': [],
                'required_projects': [
                    {'override_branch': None,
                     'override_checkout': None,
                     'project_name': 'review.example.com/org/project'}],
                'requires': [],
                'roles': [common_config_role],
                'run': run,
                'pre_run': [],
                'post_run': [],
                'cleanup_run': [],
                'semaphores': [],
                'source_context': source_ctx,
                'tags': [],
                'timeout': None,
                'variables': {},
                'extra_variables': {},
                'group_variables': {},
                'host_variables': {},
                'variant_description': '',
                'voting': True,
                'workspace_scheme': 'golang'
            }], data)

    def test_find_job_complete_playbooks(self):
        # can we fetch the variants for a single job
        data = self.get_url('api/tenant/tenant-one/job/complete-job').json()

        def expected_pb(path):
            return {
                'path': path,
                'roles': [{
                    'implicit': True,
                    'project_canonical_name':
                    'review.example.com/common-config',
                    'target_name': 'common-config',
                    'type': 'zuul'
                }],
                'secrets': [],
                'source_context': {
                    'branch': 'master',
                    'path': 'zuul.yaml',
                    'project': 'common-config',
                }
            }
        self.assertEqual([
            expected_pb("playbooks/run.yaml")
        ], data[0]['run'])
        self.assertEqual([
            expected_pb("playbooks/pre-run.yaml")
        ], data[0]['pre_run'])
        self.assertEqual([
            expected_pb("playbooks/post-run-01.yaml"),
            expected_pb("playbooks/post-run-02.yaml")
        ], data[0]['post_run'])
        self.assertEqual([
            expected_pb("playbooks/cleanup-run.yaml")
        ], data[0]['cleanup_run'])

    def test_web_nodes_list(self):
        # can we fetch the nodes list
        self.add_base_changes()
        data = self.get_url('api/tenant/tenant-one/nodes').json()
        self.assertGreater(len(data), 0)
        self.assertEqual("test-provider", data[0]["provider"])
        self.assertEqual("label1", data[0]["type"])

    def test_web_labels_list(self):
        # can we fetch the labels list
        data = self.get_url('api/tenant/tenant-one/labels').json()
        expected_list = [{'name': 'label1'}]
        self.assertEqual(expected_list, data)

    def test_web_pipeline_list(self):
        # can we fetch the list of pipelines
        data = self.get_url('api/tenant/tenant-one/pipelines').json()

        gerrit_trigger = {'name': 'gerrit', 'driver': 'gerrit'}
        timer_trigger = {'name': 'timer', 'driver': 'timer'}
        expected_list = [
            {'name': 'check', 'triggers': [gerrit_trigger]},
            {'name': 'gate', 'triggers': [gerrit_trigger]},
            {'name': 'post', 'triggers': [gerrit_trigger]},
            {'name': 'periodic', 'triggers': [timer_trigger]},
        ]
        self.assertEqual(expected_list, data)

    def test_web_project_list(self):
        # can we fetch the list of projects
        data = self.get_url('api/tenant/tenant-one/projects').json()

        expected_list = [
            {'name': 'common-config', 'type': 'config'},
            {'name': 'org/project', 'type': 'untrusted'},
            {'name': 'org/project1', 'type': 'untrusted'},
            {'name': 'org/project2', 'type': 'untrusted'}
        ]
        for p in expected_list:
            p["canonical_name"] = "review.example.com/%s" % p["name"]
            p["connection_name"] = "gerrit"
        self.assertEqual(expected_list, data)

    def test_web_project_get(self):
        # can we fetch project details
        data = self.get_url(
            'api/tenant/tenant-one/project/org/project1').json()

        jobs = [[{'abstract': False,
                  'ansible_version': None,
                  'attempts': 3,
                  'branches': [],
                  'dependencies': [],
                  'description': None,
                  'files': [],
                  'final': False,
                  'intermediate': False,
                  'irrelevant_files': [],
                  'match_on_config_updates': True,
                  'name': 'project-merge',
                  'override_checkout': None,
                  'parent': 'base',
                  'post_review': None,
                  'protected': None,
                  'provides': [],
                  'required_projects': [],
                  'requires': [],
                  'roles': [],
                  'run': [],
                  'pre_run': [],
                  'post_run': [],
                  'cleanup_run': [],
                  'semaphores': [],
                  'source_context': {
                      'branch': 'master',
                      'path': 'zuul.yaml',
                      'project': 'common-config'},
                  'tags': [],
                  'timeout': None,
                  'variables': {},
                  'extra_variables': {},
                  'group_variables': {},
                  'host_variables': {},
                  'variant_description': '',
                  'voting': True,
                  'workspace_scheme': 'golang'}],
                [{'abstract': False,
                  'ansible_version': None,
                  'attempts': 3,
                  'branches': [],
                  'dependencies': [{'name': 'project-merge',
                                    'soft': False}],
                  'description': None,
                  'files': [],
                  'final': False,
                  'intermediate': False,
                  'irrelevant_files': [],
                  'match_on_config_updates': True,
                  'name': 'project-test1',
                  'override_checkout': None,
                  'parent': 'base',
                  'post_review': None,
                  'protected': None,
                  'provides': [],
                  'required_projects': [],
                  'requires': [],
                  'roles': [],
                  'run': [],
                  'pre_run': [],
                  'post_run': [],
                  'cleanup_run': [],
                  'semaphores': [],
                  'source_context': {
                      'branch': 'master',
                      'path': 'zuul.yaml',
                      'project': 'common-config'},
                  'tags': [],
                  'timeout': None,
                  'variables': {},
                  'extra_variables': {},
                  'group_variables': {},
                  'host_variables': {},
                  'variant_description': '',
                  'voting': True,
                  'workspace_scheme': 'golang'}],
                [{'abstract': False,
                  'ansible_version': None,
                  'attempts': 3,
                  'branches': [],
                  'dependencies': [{'name': 'project-merge',
                                    'soft': False}],
                  'description': None,
                  'files': [],
                  'final': False,
                  'intermediate': False,
                  'irrelevant_files': [],
                  'match_on_config_updates': True,
                  'name': 'project-test2',
                  'override_checkout': None,
                  'parent': 'base',
                  'post_review': None,
                  'protected': None,
                  'provides': [],
                  'required_projects': [],
                  'requires': [],
                  'roles': [],
                  'run': [],
                  'pre_run': [],
                  'post_run': [],
                  'cleanup_run': [],
                  'semaphores': [],
                  'source_context': {
                      'branch': 'master',
                      'path': 'zuul.yaml',
                      'project': 'common-config'},
                  'tags': [],
                  'timeout': None,
                  'variables': {},
                  'extra_variables': {},
                  'group_variables': {},
                  'host_variables': {},
                  'variant_description': '',
                  'voting': True,
                  'workspace_scheme': 'golang'}],
                [{'abstract': False,
                  'ansible_version': None,
                  'attempts': 3,
                  'branches': [],
                  'dependencies': [{'name': 'project-merge',
                                    'soft': False}],
                  'description': None,
                  'files': [],
                  'final': False,
                  'intermediate': False,
                  'irrelevant_files': [],
                  'match_on_config_updates': True,
                  'name': 'project1-project2-integration',
                  'override_checkout': None,
                  'parent': 'base',
                  'post_review': None,
                  'protected': None,
                  'provides': [],
                  'required_projects': [],
                  'requires': [],
                  'roles': [],
                  'run': [],
                  'pre_run': [],
                  'post_run': [],
                  'cleanup_run': [],
                  'semaphores': [],
                  'source_context': {
                      'branch': 'master',
                      'path': 'zuul.yaml',
                      'project': 'common-config'},
                  'tags': [],
                  'timeout': None,
                  'variables': {},
                  'extra_variables': {},
                  'group_variables': {},
                  'host_variables': {},
                  'variant_description': '',
                  'voting': True,
                  'workspace_scheme': 'golang'}]]

        self.assertEqual(
            {
                'canonical_name': 'review.example.com/org/project1',
                'connection_name': 'gerrit',
                'name': 'org/project1',
                'configs': [{
                    'source_context': {'branch': 'master',
                                       'path': 'zuul.yaml',
                                       'project': 'common-config'},
                    'templates': [],
                    'default_branch': 'master',
                    'queue_name': 'integrated',
                    'merge_mode': 'merge-resolve',
                    'pipelines': [{
                        'name': 'check',
                        'queue_name': None,
                        'jobs': jobs,
                    }, {
                        'name': 'gate',
                        'queue_name': 'integrated-overridden',
                        'jobs': jobs,
                    }, {'name': 'post',
                        'queue_name': None,
                        'jobs': [[
                            {'abstract': False,
                             'ansible_version': None,
                             'attempts': 3,
                             'branches': [],
                             'dependencies': [],
                             'description': None,
                             'files': [],
                             'final': False,
                             'intermediate': False,
                             'irrelevant_files': [],
                             'match_on_config_updates': True,
                             'name': 'project-post',
                             'override_checkout': None,
                             'parent': 'base',
                             'post_review': None,
                             'post_run': [],
                             'cleanup_run': [],
                             'pre_run': [],
                             'protected': None,
                             'provides': [],
                             'required_projects': [],
                             'requires': [],
                             'roles': [],
                             'run': [],
                             'semaphores': [],
                             'source_context': {'branch': 'master',
                                                'path': 'zuul.yaml',
                                                'project': 'common-config'},
                             'tags': [],
                             'timeout': None,
                             'variables': {},
                             'extra_variables': {},
                             'group_variables': {},
                             'host_variables': {},
                             'variant_description': '',
                             'voting': True,
                             'workspace_scheme': 'golang'}
                        ]],
                    }
                    ]
                }]
            }, data)

    def test_web_keys(self):
        with open(os.path.join(FIXTURE_DIR, 'public.pem'), 'rb') as f:
            public_pem = f.read()

        resp = self.get_url("api/tenant/tenant-one/key/org/project.pub")
        self.assertEqual(resp.content, public_pem)
        self.assertIn('text/plain', resp.headers.get('Content-Type'))

        resp = self.get_url("api/tenant/non-tenant/key/org/project.pub")
        self.assertEqual(404, resp.status_code)

        resp = self.get_url("api/tenant/tenant-one/key/org/no-project.pub")
        self.assertEqual(404, resp.status_code)

        with open(os.path.join(FIXTURE_DIR, 'ssh.pub'), 'rb') as f:
            public_ssh = f.read()

        resp = self.get_url("api/tenant/tenant-one/project-ssh-key/"
                            "org/project.pub")
        self.assertEqual(resp.content, public_ssh)
        self.assertIn('text/plain', resp.headers.get('Content-Type'))

    def test_web_404_on_unknown_tenant(self):
        resp = self.get_url("api/tenant/non-tenant/status")
        self.assertEqual(404, resp.status_code)

    def test_autohold_info_404_on_invalid_id(self):
        resp = self.get_url("api/tenant/tenant-one/autohold/12345")
        self.assertEqual(404, resp.status_code)

    def test_autohold_delete_404_on_invalid_id(self):
        resp = self.delete_url("api/tenant/tenant-one/autohold/12345")
        self.assertEqual(404, resp.status_code)

    def test_autohold_info(self):
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1)
        self.assertTrue(r)

        # Use autohold-list API to retrieve request ID
        resp = self.get_url(
            "api/tenant/tenant-one/autohold")
        self.assertEqual(200, resp.status_code, resp.text)
        autohold_requests = resp.json()
        self.assertNotEqual([], autohold_requests)
        self.assertEqual(1, len(autohold_requests))
        request_id = autohold_requests[0]['id']

        # Now try the autohold-info API
        resp = self.get_url("api/tenant/tenant-one/autohold/%s" % request_id)
        self.assertEqual(200, resp.status_code, resp.text)
        request = resp.json()

        self.assertEqual(request_id, request['id'])
        self.assertEqual('tenant-one', request['tenant'])
        self.assertIn('org/project', request['project'])
        self.assertEqual('project-test2', request['job'])
        self.assertEqual(".*", request['ref_filter'])
        self.assertEqual(1, request['max_count'])
        self.assertEqual(0, request['current_count'])
        self.assertEqual("reason text", request['reason'])
        self.assertEqual([], request['nodes'])

        # Scope the request to tenant-two, not found
        resp = self.get_url("api/tenant/tenant-two/autohold/%s" % request_id)
        self.assertEqual(404, resp.status_code, resp.text)

    def test_autohold_list(self):
        """test listing autoholds through zuul-web"""
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1)
        self.assertTrue(r)
        resp = self.get_url(
            "api/tenant/tenant-one/autohold")
        self.assertEqual(200, resp.status_code, resp.text)
        autohold_requests = resp.json()

        self.assertNotEqual([], autohold_requests)
        self.assertEqual(1, len(autohold_requests))
        ah_request = autohold_requests[0]

        self.assertEqual('tenant-one', ah_request['tenant'])
        self.assertIn('org/project', ah_request['project'])
        self.assertEqual('project-test2', ah_request['job'])
        self.assertEqual(".*", ah_request['ref_filter'])
        self.assertEqual(1, ah_request['max_count'])
        self.assertEqual(0, ah_request['current_count'])
        self.assertEqual("reason text", ah_request['reason'])
        self.assertEqual([], ah_request['nodes'])

        # filter by project
        resp = self.get_url(
            "api/tenant/tenant-one/autohold?project=org/project2")
        self.assertEqual(200, resp.status_code, resp.text)
        autohold_requests = resp.json()
        self.assertEqual([], autohold_requests)
        resp = self.get_url(
            "api/tenant/tenant-one/autohold?project=org/project")
        self.assertEqual(200, resp.status_code, resp.text)
        autohold_requests = resp.json()

        self.assertNotEqual([], autohold_requests)
        self.assertEqual(1, len(autohold_requests))
        ah_request = autohold_requests[0]

        self.assertEqual('tenant-one', ah_request['tenant'])
        self.assertIn('org/project', ah_request['project'])
        self.assertEqual('project-test2', ah_request['job'])
        self.assertEqual(".*", ah_request['ref_filter'])
        self.assertEqual(1, ah_request['max_count'])
        self.assertEqual(0, ah_request['current_count'])
        self.assertEqual("reason text", ah_request['reason'])
        self.assertEqual([], ah_request['nodes'])

    def test_admin_routes_404_by_default(self):
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/autohold",
            json={'job': 'project-test1',
                  'count': 1,
                  'reason': 'because',
                  'node_hold_expiration': 36000})
        self.assertEqual(404, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            json={'trigger': 'gerrit',
                  'change': '2,1',
                  'pipeline': 'check'})
        self.assertEqual(404, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            json={'trigger': 'gerrit',
                  'ref': 'abcd',
                  'newrev': 'aaaa',
                  'oldrev': 'bbbb',
                  'pipeline': 'check'})
        self.assertEqual(404, resp.status_code)

    def test_jobs_list(self):
        jobs = self.get_url("api/tenant/tenant-one/jobs").json()
        self.assertEqual(len(jobs), 10)

        resp = self.get_url("api/tenant/non-tenant/jobs")
        self.assertEqual(404, resp.status_code)

    def test_jobs_list_variants(self):
        resp = self.get_url("api/tenant/tenant-one/jobs").json()
        for job in resp:
            if job['name'] in ["base", "noop"]:
                variants = None
            elif job['name'] == 'project-test1':
                variants = [
                    {'parent': 'base'},
                    {'branches': ['stable'], 'parent': 'base'},
                ]
            else:
                variants = [{'parent': 'base'}]
            self.assertEqual(variants, job.get('variants'))

    def test_jobs_list_tags(self):
        resp = self.get_url("api/tenant/tenant-one/jobs").json()

        post_job = None
        for job in resp:
            if job['name'] == 'project-post':
                post_job = job
                break
        self.assertIsNotNone(post_job)
        self.assertEqual(['post'], post_job.get('tags'))

    def test_web_job_noop(self):
        job = self.get_url("api/tenant/tenant-one/job/noop").json()
        self.assertEqual("noop", job[0]["name"])

    def test_freeze_jobs(self):
        # Test can get a list of the jobs for a given project+pipeline+branch.
        resp = self.get_url(
            "api/tenant/tenant-one/pipeline/check"
            "/project/org/project1/branch/master/freeze-jobs")

        freeze_jobs = [{
            'name': 'project-merge',
            'dependencies': [],
        }, {
            'name': 'project-test1',
            'dependencies': [{
                'name': 'project-merge',
                'soft': False,
            }],
        }, {
            'name': 'project-test2',
            'dependencies': [{
                'name': 'project-merge',
                'soft': False,
            }],
        }, {
            'name': 'project1-project2-integration',
            'dependencies': [{
                'name': 'project-merge',
                'soft': False,
            }],
        }]
        self.assertEqual(freeze_jobs, resp.json())

    def test_freeze_jobs_set_includes_all_jobs(self):
        # When freezing a job set we want to include all jobs even if they
        # have certain matcher requirements (such as required files) since we
        # can't otherwise evaluate them.

        resp = self.get_url(
            "api/tenant/tenant-one/pipeline/gate"
            "/project/org/project/branch/master/freeze-jobs")
        expected = {
            'name': 'project-testfile',
            'dependencies': [{
                'name': 'project-merge',
                'soft': False,
            }],
        }
        self.assertIn(expected, resp.json())

    def test_freeze_job(self):

        resp = self.get_url(
            "api/tenant/tenant-one/pipeline/check"
            "/project/org/project1/branch/master/freeze-job/"
            "project-test1")

        job_params = {
            'job': 'project-test1',
            'ansible_version': '2.9',
            'timeout': None,
            'post_timeout': None,
            'items': [],
            'projects': [],
            'branch': 'master',
            'cleanup_playbooks': [],
            'nodeset': {
                'groups': [],
                'name': '',
                'nodes': [
                    {'aliases': [],
                     'comment': None,
                     'hold_job': None,
                     'id': None,
                     'label': 'label1',
                     'name': 'controller',
                     'state': 'unknown',
                     'user_data': None}]},
            'override_branch': None,
            'override_checkout': None,
            'merge_repo_state_ref': None,
            'extra_repo_state_ref': None,
            'playbooks': [{
                'connection': 'gerrit',
                'project': 'common-config',
                'branch': 'master',
                'trusted': True,
                'roles': [{
                    'target_name': 'common-config',
                    'type': 'zuul',
                    'project_canonical_name':
                        'review.example.com/common-config',
                    'implicit': True,
                    'project_default_branch': 'master',
                    'connection': 'gerrit',
                    'project': 'common-config',
                }],
                'secrets': {},
                'path': 'playbooks/project-test1.yaml',
            }],
            'pre_playbooks': [],
            'post_playbooks': [],
            'ssh_keys': [],
            'vars': {},
            'extra_vars': {},
            'host_vars': {},
            'group_vars': {},
            'secret_vars': None,
            'zuul': {
                '_inheritance_path': [
                    '<Job base branches: None source: '
                    'common-config/zuul.yaml@master#53>',
                    '<Job project-test1 branches: None source: '
                    'common-config/zuul.yaml@master#66>',
                    '<Job project-test1 branches: None source: '
                    'common-config/zuul.yaml@master#138>'],
                'build': '00000000000000000000000000000000',
                'buildset': None,
                'branch': 'master',
                'ref': None,
                'pipeline': 'check',
                'post_review': False,
                'job': 'project-test1',
                'voting': True,
                'project': {
                    'name': 'org/project1',
                    'short_name': 'project1',
                    'canonical_hostname': 'review.example.com',
                    'canonical_name': 'review.example.com/org/project1',
                    'src_dir': 'src/review.example.com/org/project1',
                },
                'tenant': 'tenant-one',
                'timeout': None,
                'jobtags': [],
                'branch': 'master',
                'projects': {},
                'items': [],
                'change_url': None,
                'child_jobs': [],
                'event_id': None,
            },
            'workspace_scheme': 'golang',
        }

        self.assertEqual(job_params, resp.json())

    @simple_layout('layouts/noop-job.yaml')
    def test_freeze_noop_job(self):

        resp = self.get_url(
            "api/tenant/tenant-one/pipeline/gate"
            "/project/org/noop-project/branch/master/freeze-job/"
            "noop")

        job_params = {
            'ansible_version': '2.9',
            'branch': 'master',
            'extra_vars': {},
            'group_vars': {},
            'host_vars': {},
            'items': [],
            'job': 'noop',
            'nodeset': {'groups': [], 'name': '', 'nodes': []},
            'override_branch': None,
            'override_checkout': None,
            'post_timeout': None,
            'projects': [],
            'merge_repo_state_ref': None,
            'extra_repo_state_ref': None,
            'secret_vars': None,
            'ssh_keys': [],
            'timeout': None,
            'vars': {},
            'workspace_scheme': 'golang',
            'zuul': {
                '_inheritance_path': [
                    '<Job noop branches: None source: None#0>',
                    '<Job noop branches: None source: '
                    'org/common-config/zuul.yaml@master#22>'],
                'branch': 'master',
                'build': '00000000000000000000000000000000',
                'buildset': None,
                'change_url': None,
                'child_jobs': [],
                'event_id': None,
                'items': [],
                'job': 'noop',
                'jobtags': [],
                'pipeline': 'gate',
                'post_review': False,
                'project': {
                    'canonical_hostname': 'review.example.com',
                    'canonical_name': 'review.example.com/org/noop-project',
                    'name': 'org/noop-project',
                    'short_name': 'noop-project',
                    'src_dir': 'src/review.example.com/org/noop-project'},
                'projects': {},
                'ref': None,
                'tenant': 'tenant-one',
                'timeout': None,
                'voting': True}}

        self.assertEqual(job_params, resp.json())


class TestWebStatusDisplayBranch(BaseTestWeb):
    tenant_config_file = 'config/change-queues/main.yaml'

    def add_changes(self):
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        B = self.fake_gerrit.addFakeChange('org/project2', 'master', 'B')
        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        C = self.fake_gerrit.addFakeChange('org/project3', 'master', 'C')
        C.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        D = self.fake_gerrit.addFakeChange('org/project4', 'master', 'D')
        D.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(D.addApproval('Approved', 1))

    def test_web_status_display_branch(self):
        "Test that we can retrieve JSON status info with branch name"
        self.add_changes()
        self.waitUntilSettled()
        resp = self.get_url("api/tenant/tenant-one/status")
        self.executor_server.release()
        data = resp.json()

        for p in data['pipelines']:
            if p['name'] == 'gate':
                for q in p['change_queues']:
                    # 'per-branch: true' is configured for all gate queues
                    self.assertEqual(q['branch'], 'master')


class TestWebMultiTenant(BaseTestWeb):
    tenant_config_file = 'config/multi-tenant/main.yaml'

    def test_web_labels_allowed_list(self):
        labels = ["tenant-one-label", "fake", "tenant-two-label"]
        self.fake_nodepool.registerLauncher(labels, "FakeLauncher2")
        # Tenant-one has label restriction in place on tenant-two
        res = self.get_url('api/tenant/tenant-one/labels').json()
        self.assertEqual([{'name': 'fake'}, {'name': 'tenant-one-label'}], res)
        # Tenant-two has label restriction in place on tenant-one
        expected = ["label1", "fake", "tenant-two-label"]
        res = self.get_url('api/tenant/tenant-two/labels').json()
        self.assertEqual(
            list(map(lambda x: {'name': x}, sorted(expected))), res)


class TestWebSecrets(BaseTestWeb):
    tenant_config_file = 'config/secrets/main.yaml'

    def test_web_find_job_secret(self):
        data = self.get_url('api/tenant/tenant-one/job/project1-secret').json()
        run = data[0]['run']
        secret = {'name': 'project1_secret', 'alias': 'secret_name'}
        self.assertEqual([secret], run[0]['secrets'])

    def test_freeze_job_redacted(self):
        # Test that ssh_keys and secrets are redacted
        resp = self.get_url(
            "api/tenant/tenant-one/pipeline/check"
            "/project/org/project1/branch/master/freeze-job/"
            "project1-secret").json()
        self.assertEqual(
            {'secret_name': 'REDACTED'}, resp['playbooks'][0]['secrets'])
        self.assertEqual('REDACTED', resp['ssh_keys'][0])


class TestInfo(BaseTestWeb):

    config_file = 'zuul-sql-driver-mysql.conf'

    def setUp(self):
        super(TestInfo, self).setUp()
        web_config = self.config_ini_data.get('web', {})
        self.websocket_url = web_config.get('websocket_url')
        self.stats_url = web_config.get('stats_url')
        statsd_config = self.config_ini_data.get('statsd', {})
        self.stats_prefix = statsd_config.get('prefix')

    def _expected_info(self):
        return {
            "info": {
                "capabilities": {
                    "job_history": True,
                    "auth": {
                        "realms": {},
                        "default_realm": None
                    }
                },
                "stats": {
                    "url": self.stats_url,
                    "prefix": self.stats_prefix,
                    "type": "graphite",
                },
                "websocket_url": self.websocket_url,
            }
        }

    def test_info(self):
        info = self.get_url("api/info").json()
        self.assertEqual(
            info, self._expected_info())

    def test_tenant_info(self):
        info = self.get_url("api/tenant/tenant-one/info").json()
        expected_info = self._expected_info()
        expected_info['info']['tenant'] = 'tenant-one'
        self.assertEqual(
            info, expected_info)


class TestWebCapabilitiesInfo(TestInfo):

    config_file = 'zuul-admin-web-oidc.conf'

    def _expected_info(self):
        info = super(TestWebCapabilitiesInfo, self)._expected_info()
        info['info']['capabilities']['auth'] = {
            'realms': {
                'myOIDC1': {
                    'authority': 'http://oidc1',
                    'client_id': 'zuul',
                    'type': 'JWT',
                    'scope': 'openid profile',
                    'driver': 'OpenIDConnect',
                },
                'myOIDC2': {
                    'authority': 'http://oidc2',
                    'client_id': 'zuul',
                    'type': 'JWT',
                    'scope': 'openid profile email special-scope',
                    'driver': 'OpenIDConnect',
                },
                'zuul.example.com': {
                    'authority': 'zuul_operator',
                    'client_id': 'zuul.example.com',
                    'type': 'JWT',
                    'driver': 'HS256',
                }
            },
            'default_realm': 'myOIDC1'
        }
        return info


class TestTenantAuthRealmInfo(TestWebCapabilitiesInfo):

    tenant_config_file = 'config/authorization/rules-templating/main.yaml'

    def test_tenant_info(self):
        expected_info = self._expected_info()
        info = self.get_url("api/tenant/tenant-zero/info").json()
        expected_info['info']['tenant'] = 'tenant-zero'
        expected_info['info']['capabilities']['auth']['default_realm'] =\
            'myOIDC1'
        self.assertEqual(expected_info,
                         info,
                         info)
        info = self.get_url("api/tenant/tenant-one/info").json()
        expected_info['info']['tenant'] = 'tenant-one'
        expected_info['info']['capabilities']['auth']['default_realm'] =\
            'myOIDC1'
        self.assertEqual(expected_info,
                         info,
                         info)
        info = self.get_url("api/tenant/tenant-two/info").json()
        expected_info['info']['tenant'] = 'tenant-two'
        expected_info['info']['capabilities']['auth']['default_realm'] =\
            'myOIDC2'
        self.assertEqual(expected_info,
                         info,
                         info)


class TestTenantInfoConfigBroken(BaseTestWeb):

    tenant_config_file = 'config/broken/main.yaml'

    def test_tenant_info_broken_config(self):
        config_errors = self.get_url(
            "api/tenant/tenant-broken/config-errors").json()
        self.assertEqual(
            len(config_errors), 2)

        self.assertEqual(
            config_errors[0]['source_context']['project'], 'org/project3')
        self.assertIn('Zuul encountered an error while accessing the repo '
                      'org/project3',
                      config_errors[0]['error'])

        self.assertEqual(
            config_errors[1]['source_context']['project'], 'org/project2')
        self.assertEqual(
            config_errors[1]['source_context']['branch'], 'master')
        self.assertEqual(
            config_errors[1]['source_context']['path'], '.zuul.yaml')
        self.assertIn('Zuul encountered a syntax error',
                      config_errors[1]['error'])

        resp = self.get_url("api/tenant/non-tenant/config-errors")
        self.assertEqual(404, resp.status_code)


class TestBrokenConfigCache(BaseWithWeb):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def test_broken_config_cache(self):
        # Delete the cached config files from ZK to simulate a
        # scheduler encountering an error in reconfiguration.
        path = '/zuul/config/cache/review.example.com%2Forg%2Fproject'
        self.assertIsNotNone(self.zk_client.client.exists(path))
        self.zk_client.client.delete(path, recursive=True)
        self.startWebServer()
        config_errors = self.get_url(
            "api/tenant/tenant-one/config-errors").json()
        self.assertIn('Configuration files missing',
                      config_errors[0]['error'])


class TestWebSocketInfo(TestInfo):

    config_ini_data = {
        'web': {
            'websocket_url': 'wss://ws.example.com'
        }
    }


class TestGraphiteUrl(TestInfo):

    config_ini_data = {
        'statsd': {
            'prefix': 'example'
        },
        'web': {
            'stats_url': 'https://graphite.example.com',
        }
    }


class TestBuildInfo(BaseTestWeb):
    config_file = 'zuul-sql-driver-mysql.conf'
    tenant_config_file = 'config/sql-driver/main.yaml'

    def test_web_list_builds(self):
        # Generate some build records in the db.
        self.add_base_changes()
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        builds = self.get_url("api/tenant/tenant-one/builds").json()
        self.assertEqual(len(builds), 6)

        uuid = builds[0]['uuid']
        build = self.get_url("api/tenant/tenant-one/build/%s" % uuid).json()
        self.assertEqual(build['job_name'], builds[0]['job_name'])

        resp = self.get_url("api/tenant/tenant-one/build/1234")
        self.assertEqual(404, resp.status_code)

        builds_query = self.get_url("api/tenant/tenant-one/builds?"
                                    "project=org/project&"
                                    "project=org/project1").json()
        self.assertEqual(len(builds_query), 6)
        self.assertEqual(builds_query[0]['nodeset'], 'test-nodeset')

        resp = self.get_url("api/tenant/non-tenant/builds")
        self.assertEqual(404, resp.status_code)

        extrema = [int(builds[-1]['_id']), int(builds[0]['_id'])]
        idx_min = min(extrema)
        idx_max = max(extrema)
        builds_query = self.get_url("api/tenant/tenant-one/builds?"
                                    "idx_max=%i" % idx_min).json()
        self.assertEqual(len(builds_query), 1, builds_query)
        builds_query = self.get_url("api/tenant/tenant-one/builds?"
                                    "idx_min=%i" % idx_min).json()
        self.assertEqual(len(builds_query), len(builds), builds_query)
        builds_query = self.get_url("api/tenant/tenant-one/builds?"
                                    "idx_max=%i" % idx_max).json()
        self.assertEqual(len(builds_query), len(builds), builds_query)
        builds_query = self.get_url("api/tenant/tenant-one/builds?"
                                    "idx_min=%i" % idx_max).json()
        self.assertEqual(len(builds_query), 1, builds_query)

    def test_web_badge(self):
        # Generate some build records in the db.
        self.add_base_changes()
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        # Now request badge for the buildsets
        result = self.get_url("api/tenant/tenant-one/badge")

        self.log.error(result.content)
        result.raise_for_status()
        self.assertTrue(result.text.startswith('<svg '))
        self.assertIn('passing', result.text)

        # Generate a failing record
        self.executor_server.hold_jobs_in_build = True
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        C.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.executor_server.failJob('project-merge', C)
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        # Request again badge for the buildsets
        result = self.get_url("api/tenant/tenant-one/badge")
        self.log.error(result.content)
        result.raise_for_status()
        self.assertTrue(result.text.startswith('<svg '))
        self.assertIn('failing', result.text)

    def test_web_list_buildsets(self):
        # Generate some build records in the db.
        self.add_base_changes()
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        buildsets = self.get_url("api/tenant/tenant-one/buildsets").json()
        self.assertEqual(2, len(buildsets))
        project_bs = [x for x in buildsets if x["project"] == "org/project"][0]

        buildset = self.get_url(
            "api/tenant/tenant-one/buildset/%s" % project_bs['uuid']).json()
        self.assertEqual(3, len(buildset["builds"]))

        project_test1_build = [x for x in buildset["builds"]
                               if x["job_name"] == "project-test1"][0]
        self.assertEqual('SUCCESS', project_test1_build['result'])

        project_test2_build = [x for x in buildset["builds"]
                               if x["job_name"] == "project-test2"][0]
        self.assertEqual('SUCCESS', project_test2_build['result'])

        project_merge_build = [x for x in buildset["builds"]
                               if x["job_name"] == "project-merge"][0]
        self.assertEqual('SUCCESS', project_merge_build['result'])

        extrema = [int(buildsets[-1]['_id']), int(buildsets[0]['_id'])]
        idx_min = min(extrema)
        idx_max = max(extrema)
        buildsets_query = self.get_url("api/tenant/tenant-one/buildsets?"
                                       "idx_max=%i" % idx_min).json()
        self.assertEqual(len(buildsets_query), 1, buildsets_query)
        buildsets_query = self.get_url("api/tenant/tenant-one/buildsets?"
                                       "idx_min=%i" % idx_min).json()
        self.assertEqual(len(buildsets_query), len(buildsets), buildsets_query)
        buildsets_query = self.get_url("api/tenant/tenant-one/buildsets?"
                                       "idx_max=%i" % idx_max).json()
        self.assertEqual(len(buildsets_query), len(buildsets), buildsets_query)
        buildsets_query = self.get_url("api/tenant/tenant-one/buildsets?"
                                       "idx_min=%i" % idx_max).json()
        self.assertEqual(len(buildsets_query), 1, buildsets_query)

    @simple_layout('layouts/empty-check.yaml')
    def test_build_error(self):
        conf = textwrap.dedent(
            """
            - job:
                name: test-job
                run: playbooks/dne.yaml

            - project:
                name: org/project
                check:
                  jobs:
                    - test-job
            """)

        file_dict = {'.zuul.yaml': conf}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        builds = self.get_url("api/tenant/tenant-one/builds").json()
        self.assertIn('Unable to find playbook',
                      builds[0]['error_detail'])


class TestArtifacts(BaseTestWeb, AnsibleZuulTestCase):
    config_file = 'zuul-sql-driver-mysql.conf'
    tenant_config_file = 'config/sql-driver/main.yaml'

    def test_artifacts(self):
        # Generate some build records in the db.
        self.add_base_changes()
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        build_query = self.get_url("api/tenant/tenant-one/builds?"
                                   "project=org/project&"
                                   "job_name=project-test1").json()
        self.assertEqual(len(build_query), 1)
        self.assertEqual(len(build_query[0]['artifacts']), 3)
        arts = build_query[0]['artifacts']
        arts.sort(key=lambda x: x['name'])
        self.assertEqual(build_query[0]['artifacts'], [
            {'url': 'http://example.com/docs',
             'name': 'docs'},
            {'url': 'http://logs.example.com/build/relative/docs',
             'name': 'relative',
             'metadata': {'foo': 'bar'}},
            {'url': 'http://example.com/tarball',
             'name': 'tarball'},
        ])

    def test_buildset_artifacts(self):
        self.add_base_changes()
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        buildsets = self.get_url("api/tenant/tenant-one/buildsets").json()
        project_bs = [x for x in buildsets if x["project"] == "org/project"][0]
        buildset = self.get_url(
            "api/tenant/tenant-one/buildset/%s" % project_bs['uuid']).json()
        self.assertEqual(3, len(buildset["builds"]))

        test1_build = [x for x in buildset["builds"]
                       if x["job_name"] == "project-test1"][0]
        arts = test1_build['artifacts']
        arts.sort(key=lambda x: x['name'])
        self.assertEqual([
            {'url': 'http://example.com/docs',
             'name': 'docs'},
            {'url': 'http://logs.example.com/build/relative/docs',
             'name': 'relative',
             'metadata': {'foo': 'bar'}},
            {'url': 'http://example.com/tarball',
             'name': 'tarball'},
        ], test1_build['artifacts'])


class TestTenantScopedWebApi(BaseTestWeb):
    config_file = 'zuul-admin-web.conf'

    def test_admin_routes_no_token(self):
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/autohold",
            json={'job': 'project-test1',
                  'count': 1,
                  'reason': 'because',
                  'node_hold_expiration': 36000})
        self.assertEqual(401, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            json={'trigger': 'gerrit',
                  'change': '2,1',
                  'pipeline': 'check'})
        self.assertEqual(401, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            json={'trigger': 'gerrit',
                  'ref': 'abcd',
                  'newrev': 'aaaa',
                  'oldrev': 'bbbb',
                  'pipeline': 'check'})
        self.assertEqual(401, resp.status_code)

    def test_bad_key_JWT_token(self):
        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ],
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='OnlyZuulNoDana',
                           algorithm='HS256')
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/autohold",
            headers={'Authorization': 'Bearer %s' % token},
            json={'job': 'project-test1',
                  'count': 1,
                  'reason': 'because',
                  'node_hold_expiration': 36000})
        self.assertEqual(401, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            headers={'Authorization': 'Bearer %s' % token},
            json={'trigger': 'gerrit',
                  'change': '2,1',
                  'pipeline': 'check'})
        self.assertEqual(401, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            headers={'Authorization': 'Bearer %s' % token},
            json={'trigger': 'gerrit',
                  'ref': 'abcd',
                  'newrev': 'aaaa',
                  'oldrev': 'bbbb',
                  'pipeline': 'check'})
        self.assertEqual(401, resp.status_code)

    def test_expired_JWT_token(self):
        authz = {'iss': 'zuul_operator',
                 'sub': 'testuser',
                 'aud': 'zuul.example.com',
                 'zuul': {
                     'admin': ['tenant-one', ]
                 },
                 'exp': time.time() - 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/autohold",
            headers={'Authorization': 'Bearer %s' % token},
            json={'job': 'project-test1',
                  'count': 1,
                  'reason': 'because',
                  'node_hold_expiration': 36000})
        self.assertEqual(401, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            headers={'Authorization': 'Bearer %s' % token},
            json={'trigger': 'gerrit',
                  'change': '2,1',
                  'pipeline': 'check'})
        self.assertEqual(401, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            headers={'Authorization': 'Bearer %s' % token},
            json={'trigger': 'gerrit',
                  'ref': 'abcd',
                  'newrev': 'aaaa',
                  'oldrev': 'bbbb',
                  'pipeline': 'check'})
        self.assertEqual(401, resp.status_code)

    def test_valid_JWT_bad_tenants(self):
        authz = {'iss': 'zuul_operator',
                 'sub': 'testuser',
                 'aud': 'zuul.example.com',
                 'zuul': {
                     'admin': ['tenant-six', 'tenant-ten', ]
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/autohold",
            headers={'Authorization': 'Bearer %s' % token},
            json={'job': 'project-test1',
                  'count': 1,
                  'reason': 'because',
                  'node_hold_expiration': 36000})
        self.assertEqual(403, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            headers={'Authorization': 'Bearer %s' % token},
            json={'trigger': 'gerrit',
                  'change': '2,1',
                  'pipeline': 'check'})
        self.assertEqual(403, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            headers={'Authorization': 'Bearer %s' % token},
            json={'trigger': 'gerrit',
                  'ref': 'abcd',
                  'newrev': 'aaaa',
                  'oldrev': 'bbbb',
                  'pipeline': 'check'})
        self.assertEqual(403, resp.status_code)

        # For autohold-delete, we first must make sure that an autohold
        # exists before the delete attempt.
        good_authz = {'iss': 'zuul_operator',
                      'aud': 'zuul.example.com',
                      'sub': 'testuser',
                      'zuul': {'admin': ['tenant-one', ]},
                      'exp': time.time() + 3600}
        args = {"reason": "some reason",
                "count": 1,
                'job': 'project-test2',
                'change': None,
                'ref': None,
                'node_hold_expiration': None}
        good_token = jwt.encode(good_authz, key='NoDanaOnlyZuul',
                                algorithm='HS256')
        req = self.post_url(
            'api/tenant/tenant-one/project/org/project/autohold',
            headers={'Authorization': 'Bearer %s' % good_token},
            json=args)
        self.assertEqual(200, req.status_code, req.text)
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        autohold_requests = client.autohold_list()
        self.assertNotEqual([], autohold_requests)
        self.assertEqual(1, len(autohold_requests))
        request = autohold_requests[0]
        resp = self.delete_url(
            "api/tenant/tenant-one/autohold/%s" % request['id'],
            headers={'Authorization': 'Bearer %s' % token})
        self.assertEqual(403, resp.status_code)

    def test_autohold(self):
        """Test that autohold can be set through the admin web interface"""
        args = {"reason": "some reason",
                "count": 1,
                'job': 'project-test2',
                'change': None,
                'ref': None,
                'node_hold_expiration': None}
        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ]
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        req = self.post_url(
            'api/tenant/tenant-one/project/org/project/autohold',
            headers={'Authorization': 'Bearer %s' % token},
            json=args)
        self.assertEqual(200, req.status_code, req.text)
        data = req.json()
        self.assertEqual(True, data)

        # Check result in rpc client
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        autohold_requests = client.autohold_list()
        self.assertNotEqual([], autohold_requests)
        self.assertEqual(1, len(autohold_requests))
        request = autohold_requests[0]
        self.assertEqual('tenant-one', request['tenant'])
        # The matcher expects a canonical project name
        self.assertEqual('review.example.com/org/project', request['project'])
        self.assertEqual('project-test2', request['job'])
        self.assertEqual(".*", request['ref_filter'])
        self.assertEqual("some reason", request['reason'])
        self.assertEqual(1, request['max_count'])

    def _init_autohold_delete(self, authz):
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1)
        self.assertTrue(r)

        # Use autohold-list API to retrieve request ID
        resp = self.get_url(
            "api/tenant/tenant-one/autohold")
        self.assertEqual(200, resp.status_code, resp.text)
        autohold_requests = resp.json()
        self.assertNotEqual([], autohold_requests)
        self.assertEqual(1, len(autohold_requests))
        request_id = autohold_requests[0]['id']
        return client, request_id, token

    def test_autohold_delete_wrong_tenant(self):
        """Make sure authorization rules are applied"""
        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ]
                 },
                 'exp': time.time() + 3600}
        client, request_id, _ = self._init_autohold_delete(authz)
        # now try the autohold-delete API
        bad_authz = {'iss': 'zuul_operator',
                     'aud': 'zuul.example.com',
                     'sub': 'testuser',
                     'zuul': {
                         'admin': ['tenant-two', ]
                     },
                     'exp': time.time() + 3600}
        bad_token = jwt.encode(bad_authz, key='NoDanaOnlyZuul',
                               algorithm='HS256')
        resp = self.delete_url(
            "api/tenant/tenant-one/autohold/%s" % request_id,
            headers={'Authorization': 'Bearer %s' % bad_token})
        # Throw a "Forbidden" error, because user is authenticated but not
        # authorized for tenant-one
        self.assertEqual(403, resp.status_code, resp.text)
        # clean up
        r = client.autohold_delete(request_id)
        self.assertTrue(r)

    def test_autohold_delete(self):
        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ]
                 },
                 'exp': time.time() + 3600}
        client, request_id, token = self._init_autohold_delete(authz)
        resp = self.delete_url(
            "api/tenant/tenant-one/autohold/%s" % request_id,
            headers={'Authorization': 'Bearer %s' % token})
        self.assertEqual(204, resp.status_code, resp.text)
        # autohold-list should be empty now
        resp = self.get_url(
            "api/tenant/tenant-one/autohold")
        self.assertEqual(200, resp.status_code, resp.text)
        autohold_requests = resp.json()
        self.assertEqual([], autohold_requests)

    def _test_enqueue(self, use_trigger=False):
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        A.addApproval('Approved', 1)

        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ]
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        path = "api/tenant/%(tenant)s/project/%(project)s/enqueue"
        enqueue_args = {'tenant': 'tenant-one',
                        'project': 'org/project', }
        change = {'change': '1,1',
                  'pipeline': 'gate', }
        if use_trigger:
            change['trigger'] = 'gerrit'
        req = self.post_url(path % enqueue_args,
                            headers={'Authorization': 'Bearer %s' % token},
                            json=change)
        # The JSON returned is the same as the client's output
        self.assertEqual(200, req.status_code, req.text)
        data = req.json()
        self.assertEqual(True, data)
        self.waitUntilSettled()

    def test_enqueue_with_deprecated_trigger(self):
        """Test that the admin web interface can enqueue a change"""
        # TODO(mhu) remove in a few releases
        self._test_enqueue(use_trigger=True)

    def test_enqueue(self):
        """Test that the admin web interface can enqueue a change"""
        self._test_enqueue()

    def _test_enqueue_ref(self, use_trigger=False):
        """Test that the admin web interface can enqueue a ref"""
        p = "review.example.com/org/project"
        upstream = self.getUpstreamRepos([p])
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.setMerged()
        A_commit = str(upstream[p].commit('master'))
        self.log.debug("A commit: %s" % A_commit)

        path = "api/tenant/%(tenant)s/project/%(project)s/enqueue"
        enqueue_args = {'tenant': 'tenant-one',
                        'project': 'org/project', }
        ref = {'ref': 'master',
               'oldrev': '90f173846e3af9154517b88543ffbd1691f31366',
               'newrev': A_commit,
               'pipeline': 'post', }
        if use_trigger:
            ref['trigger'] = 'gerrit'
        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ]
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        req = self.post_url(path % enqueue_args,
                            headers={'Authorization': 'Bearer %s' % token},
                            json=ref)
        self.assertEqual(200, req.status_code, req.text)
        # The JSON returned is the same as the client's output
        data = req.json()
        self.assertEqual(True, data)
        self.waitUntilSettled()

    def test_enqueue_ref_with_deprecated_trigger(self):
        """Test that the admin web interface can enqueue a ref"""
        # TODO(mhu) remove in a few releases
        self._test_enqueue_ref(use_trigger=True)

    def test_enqueue_ref(self):
        """Test that the admin web interface can enqueue a ref"""
        self._test_enqueue_ref()

    def test_dequeue(self):
        """Test that the admin web interface can dequeue a change"""
        start_builds = len(self.builds)
        self.create_branch('org/project', 'stable')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project', 'stable'))
        self.executor_server.hold_jobs_in_build = True
        self.commitConfigUpdate('common-config', 'layouts/timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        for _ in iterate_timeout(30, 'Wait for a build on hold'):
            if len(self.builds) > start_builds:
                break
        self.waitUntilSettled()

        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ]
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        path = "api/tenant/%(tenant)s/project/%(project)s/dequeue"
        dequeue_args = {'tenant': 'tenant-one',
                        'project': 'org/project', }
        change = {'ref': 'refs/heads/stable',
                  'pipeline': 'periodic', }
        req = self.post_url(path % dequeue_args,
                            headers={'Authorization': 'Bearer %s' % token},
                            json=change)
        # The JSON returned is the same as the client's output
        self.assertEqual(200, req.status_code, req.text)
        data = req.json()
        self.assertEqual(True, data)
        self.waitUntilSettled()

        self.commitConfigUpdate('common-config',
                                'layouts/no-timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 1)

    def test_OPTIONS(self):
        """Ensure that protected endpoints handle CORS preflight requests
        properly"""
        # Note that %tenant, %project are not relevant here. The client is
        # just checking what the endpoint allows.
        endpoints = [
            {'action': 'promote',
             'path': 'api/tenant/my-tenant/promote',
             'allowed_methods': ['POST', ]},
            {'action': 'enqueue',
             'path': 'api/tenant/my-tenant/project/my-project/enqueue',
             'allowed_methods': ['POST', ]},
            {'action': 'enqueue_ref',
             'path': 'api/tenant/my-tenant/project/my-project/enqueue',
             'allowed_methods': ['POST', ]},
            {'action': 'autohold',
             'path': 'api/tenant/my-tenant/project/my-project/autohold',
             'allowed_methods': ['GET', 'POST', ]},
            {'action': 'autohold_by_request_id',
             'path': 'api/tenant/my-tenant/autohold/123',
             'allowed_methods': ['GET', 'DELETE', ]},
            {'action': 'dequeue',
             'path': 'api/tenant/my-tenant/project/my-project/enqueue',
             'allowed_methods': ['POST', ]},
            {'action': 'authorizations',
             'path': 'api/tenant/my-tenant/authorizations',
             'allowed_methods': ['GET', ]},
            # TODO (mhu) deprecated, remove in next version
            {'action': 'authorizations',
             'path': 'api/user/authorizations',
             'allowed_methods': ['GET', ]},
        ]
        for endpoint in endpoints:
            preflight = self.options_url(
                endpoint['path'],
                headers={'Access-Control-Request-Method': 'GET',
                         'Access-Control-Request-Headers': 'Authorization'})
            self.assertEqual(
                204,
                preflight.status_code,
                "%s failed: %s" % (endpoint['action'], preflight.text))
            self.assertEqual(
                '*',
                preflight.headers.get('Access-Control-Allow-Origin'),
                "%s failed: %s" % (endpoint['action'], preflight.headers))
            self.assertEqual(
                'Authorization, Content-Type',
                preflight.headers.get('Access-Control-Allow-Headers'),
                "%s failed: %s" % (endpoint['action'], preflight.headers))
            allowed_methods = preflight.headers.get(
                'Access-Control-Allow-Methods').split(', ')
            self.assertTrue(
                'OPTIONS' in allowed_methods,
                "%s has allowed methods: %s" % (endpoint['action'],
                                                allowed_methods))
            for method in endpoint['allowed_methods']:
                self.assertTrue(
                    method in allowed_methods,
                    "%s has allowed methods: %s,"
                    " expected: %s" % (endpoint['action'],
                                       allowed_methods,
                                       endpoint['allowed_methods']))

    def test_promote(self):
        """Test that a change can be promoted via the admin web interface"""
        # taken from test_client_promote in test_scheduler
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))

        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        items = tenant.layout.pipelines['gate'].getAllItems()
        enqueue_times = {}
        for item in items:
            enqueue_times[str(item.change)] = item.enqueue_time

        # REST API
        args = {'pipeline': 'gate',
                'changes': ['2,1', '3,1']}
        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ],
                 },
                 'exp': time.time() + 3600,
                 'iat': time.time()}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        req = self.post_url(
            'api/tenant/tenant-one/promote',
            headers={'Authorization': 'Bearer %s' % token},
            json=args)
        self.assertEqual(200, req.status_code, req.text)
        data = req.json()
        self.assertEqual(True, data)

        # ensure that enqueue times are durable
        items = tenant.layout.pipelines['gate'].getAllItems()
        for item in items:
            self.assertEqual(
                enqueue_times[str(item.change)], item.enqueue_time)

        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 6)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test2')
        self.assertEqual(self.builds[2].name, 'project-test1')
        self.assertEqual(self.builds[3].name, 'project-test2')
        self.assertEqual(self.builds[4].name, 'project-test1')
        self.assertEqual(self.builds[5].name, 'project-test2')

        self.assertTrue(self.builds[0].hasChanges(B))
        self.assertFalse(self.builds[0].hasChanges(A))
        self.assertFalse(self.builds[0].hasChanges(C))

        self.assertTrue(self.builds[2].hasChanges(B))
        self.assertTrue(self.builds[2].hasChanges(C))
        self.assertFalse(self.builds[2].hasChanges(A))

        self.assertTrue(self.builds[4].hasChanges(B))
        self.assertTrue(self.builds[4].hasChanges(C))
        self.assertTrue(self.builds[4].hasChanges(A))

        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(C.reported, 2)

    def test_tenant_authorizations_override(self):
        """Test that user gets overriden tenant authz if allowed"""
        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one'],
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        req = self.get_url(
            'api/tenant/tenant-one/authorizations',
            headers={'Authorization': 'Bearer %s' % token})
        self.assertEqual(200, req.status_code, req.text)
        data = req.json()
        self.assertTrue('zuul' in data)
        self.assertTrue(data['zuul']['admin'], data)
        self.assertTrue(data['zuul']['scope'] == ['tenant-one'], data)
        # change tenant
        authz['zuul']['admin'] = ['tenant-whatever', ]
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        req = self.get_url(
            'api/tenant/tenant-one/authorizations',
            headers={'Authorization': 'Bearer %s' % token})
        self.assertEqual(200, req.status_code, req.text)
        data = req.json()
        self.assertTrue('zuul' in data)
        self.assertTrue(data['zuul']['admin'] is False, data)
        self.assertTrue(data['zuul']['scope'] == ['tenant-one'], data)


class TestTenantScopedWebApiWithAuthRules(BaseTestWeb):
    config_file = 'zuul-admin-web-no-override.conf'
    tenant_config_file = 'config/authorization/single-tenant/main.yaml'

    def test_override_not_allowed(self):
        """Test that authz cannot be overriden if config does not allow it"""
        args = {"reason": "some reason",
                "count": 1,
                'job': 'project-test2',
                'change': None,
                'ref': None,
                'node_hold_expiration': None}
        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ],
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        req = self.post_url(
            'api/tenant/tenant-one/project/org/project/autohold',
            headers={'Authorization': 'Bearer %s' % token},
            json=args)
        self.assertEqual(401, req.status_code, req.text)

    def test_tenant_level_rule(self):
        """Test that authz rules defined at tenant level are checked"""
        path = "api/tenant/%(tenant)s/project/%(project)s/enqueue"

        def _test_project_enqueue_with_authz(i, project, authz, expected):
            f_ch = self.fake_gerrit.addFakeChange(project, 'master',
                                                  '%s %i' % (project, i))
            f_ch.addApproval('Code-Review', 2)
            f_ch.addApproval('Approved', 1)
            change = {'trigger': 'gerrit',
                      'change': '%i,1' % i,
                      'pipeline': 'gate', }
            enqueue_args = {'tenant': 'tenant-one',
                            'project': project, }

            token = jwt.encode(authz, key='NoDanaOnlyZuul',
                               algorithm='HS256')
            req = self.post_url(path % enqueue_args,
                                headers={'Authorization': 'Bearer %s' % token},
                                json=change)
            self.assertEqual(expected, req.status_code, req.text)
            self.waitUntilSettled()

        i = 0
        for p in ['org/project', 'org/project1', 'org/project2']:
            i += 1
            # Authorized sub
            authz = {'iss': 'zuul_operator',
                     'aud': 'zuul.example.com',
                     'sub': 'venkman',
                     'exp': time.time() + 3600}
            _test_project_enqueue_with_authz(i, p, authz, 200)
            i += 1
            # Unauthorized sub
            authz = {'iss': 'zuul_operator',
                     'aud': 'zuul.example.com',
                     'sub': 'vigo',
                     'exp': time.time() + 3600}
            _test_project_enqueue_with_authz(i, p, authz, 403)
            i += 1
            # unauthorized issuer
            authz = {'iss': 'columbia.edu',
                     'aud': 'zuul.example.com',
                     'sub': 'stantz',
                     'exp': time.time() + 3600}
            _test_project_enqueue_with_authz(i, p, authz, 401)
        self.waitUntilSettled()

    def test_group_rule(self):
        """Test a group rule"""
        A = self.fake_gerrit.addFakeChange('org/project2', 'master', 'A')
        A.addApproval('Code-Review', 2)
        A.addApproval('Approved', 1)

        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'melnitz',
                 'groups': ['ghostbusters', 'secretary'],
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        path = "api/tenant/%(tenant)s/project/%(project)s/enqueue"
        enqueue_args = {'tenant': 'tenant-one',
                        'project': 'org/project2', }
        change = {'trigger': 'gerrit',
                  'change': '1,1',
                  'pipeline': 'gate', }
        req = self.post_url(path % enqueue_args,
                            headers={'Authorization': 'Bearer %s' % token},
                            json=change)
        self.assertEqual(200, req.status_code, req.text)
        self.waitUntilSettled()

    def test_depth_claim_rule(self):
        """Test a rule based on a complex claim"""
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        A.addApproval('Approved', 1)

        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'zeddemore',
                 'vehicle': {
                     'car': 'ecto-1'},
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        path = "api/tenant/%(tenant)s/project/%(project)s/enqueue"
        enqueue_args = {'tenant': 'tenant-one',
                        'project': 'org/project', }
        change = {'trigger': 'gerrit',
                  'change': '1,1',
                  'pipeline': 'gate', }
        req = self.post_url(path % enqueue_args,
                            headers={'Authorization': 'Bearer %s' % token},
                            json=change)
        self.assertEqual(200, req.status_code, req.text)
        self.waitUntilSettled()

    def test_user_actions_action_override(self):
        """Test that user with 'zuul.admin' claim does NOT get it back"""
        admin_tenants = ['tenant-zero', ]
        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {'admin': admin_tenants},
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        # TODO(mhu) deprecated, remove after next release
        req = self.get_url('/api/user/authorizations',
                           headers={'Authorization': 'Bearer %s' % token})
        self.assertEqual(401, req.status_code, req.text)
        req = self.get_url('/api/tenant/tenant-one/authorizations',
                           headers={'Authorization': 'Bearer %s' % token})
        self.assertEqual(401, req.status_code, req.text)

    def test_user_actions(self):
        """Test that users get the right 'zuul.actions' trees"""
        users = [
            {'authz': {'iss': 'zuul_operator',
                       'aud': 'zuul.example.com',
                       'sub': 'vigo'},
             'zuul.admin': []},
            {'authz': {'iss': 'zuul_operator',
                       'aud': 'zuul.example.com',
                       'sub': 'venkman'},
             'zuul.admin': ['tenant-one', ]},
            {'authz': {'iss': 'zuul_operator',
                       'aud': 'zuul.example.com',
                       'sub': 'stantz'},
             'zuul.admin': []},
            {'authz': {'iss': 'zuul_operator',
                       'aud': 'zuul.example.com',
                       'sub': 'zeddemore',
                       'vehicle': {
                           'car': 'ecto-1'
                       }},
             'zuul.admin': ['tenant-one', ]},
            {'authz': {'iss': 'zuul_operator',
                       'aud': 'zuul.example.com',
                       'sub': 'melnitz',
                       'groups': ['secretary', 'ghostbusters']},
             'zuul.admin': ['tenant-one', ]},
        ]

        for test_user in users:
            authz = test_user['authz']
            authz['exp'] = time.time() + 3600
            token = jwt.encode(authz, key='NoDanaOnlyZuul',
                               algorithm='HS256')
            # TODO(mhu) deprecated, remove after next release
            req = self.get_url('/api/user/authorizations',
                               headers={'Authorization': 'Bearer %s' % token})
            self.assertEqual(200, req.status_code, req.text)
            data = req.json()
            self.assertTrue('zuul' in data,
                            "%s got %s" % (authz['sub'], data))
            self.assertTrue('admin' in data['zuul'],
                            "%s got %s" % (authz['sub'], data))
            self.assertEqual(test_user['zuul.admin'],
                             data['zuul']['admin'],
                             "%s got %s" % (authz['sub'], data))

            req = self.get_url('/api/tenant/tenant-one/authorizations',
                               headers={'Authorization': 'Bearer %s' % token})
            self.assertEqual(200, req.status_code, req.text)
            data = req.json()
            self.assertTrue('zuul' in data,
                            "%s got %s" % (authz['sub'], data))
            self.assertTrue('admin' in data['zuul'],
                            "%s got %s" % (authz['sub'], data))
            self.assertEqual('tenant-one' in test_user['zuul.admin'],
                             data['zuul']['admin'],
                             "%s got %s" % (authz['sub'], data))
            self.assertEqual(['tenant-one', ],
                             data['zuul']['scope'],
                             "%s got %s" % (authz['sub'], data))

            req = self.get_url('/api/tenant/tenant-two/authorizations',
                               headers={'Authorization': 'Bearer %s' % token})
            self.assertEqual(200, req.status_code, req.text)
            data = req.json()
            self.assertTrue('zuul' in data,
                            "%s got %s" % (authz['sub'], data))
            self.assertTrue('admin' in data['zuul'],
                            "%s got %s" % (authz['sub'], data))
            self.assertEqual('tenant-two' in test_user['zuul.admin'],
                             data['zuul']['admin'],
                             "%s got %s" % (authz['sub'], data))
            self.assertEqual(['tenant-two', ],
                             data['zuul']['scope'],
                             "%s got %s" % (authz['sub'], data))

    def test_authorizations_no_header(self):
        """Test that missing Authorization header results in HTTP 401"""
        req = self.get_url('/api/tenant/tenant-one/authorizations')
        self.assertEqual(401, req.status_code, req.text)
        # TODO(mhu) deprecated, remove after next release
        req = self.get_url('/api/user/authorizations')
        self.assertEqual(401, req.status_code, req.text)


class TestTenantScopedWebApiTokenWithExpiry(BaseTestWeb):
    config_file = 'zuul-admin-web-token-expiry.conf'

    def test_iat_claim_mandatory(self):
        """Test that the 'iat' claim is mandatory when
        max_validity_time is set"""
        authz = {'iss': 'zuul_operator',
                 'sub': 'testuser',
                 'aud': 'zuul.example.com',
                 'zuul': {
                     'admin': ['tenant-one', ]
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/autohold",
            headers={'Authorization': 'Bearer %s' % token},
            json={'job': 'project-test1',
                  'count': 1,
                  'reason': 'because',
                  'node_hold_expiration': 36000})
        self.assertEqual(401, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            headers={'Authorization': 'Bearer %s' % token},
            json={'trigger': 'gerrit',
                  'change': '2,1',
                  'pipeline': 'check'})
        self.assertEqual(401, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            headers={'Authorization': 'Bearer %s' % token},
            json={'trigger': 'gerrit',
                  'ref': 'abcd',
                  'newrev': 'aaaa',
                  'oldrev': 'bbbb',
                  'pipeline': 'check'})
        self.assertEqual(401, resp.status_code)

    def test_token_from_the_future(self):
        authz = {'iss': 'zuul_operator',
                 'sub': 'testuser',
                 'aud': 'zuul.example.com',
                 'zuul': {
                     'admin': ['tenant-one', ],
                 },
                 'exp': time.time() + 7200,
                 'iat': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/autohold",
            headers={'Authorization': 'Bearer %s' % token},
            json={'job': 'project-test1',
                  'count': 1,
                  'reason': 'because',
                  'node_hold_expiration': 36000})
        self.assertEqual(401, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            headers={'Authorization': 'Bearer %s' % token},
            json={'trigger': 'gerrit',
                  'change': '2,1',
                  'pipeline': 'check'})
        self.assertEqual(401, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            headers={'Authorization': 'Bearer %s' % token},
            json={'trigger': 'gerrit',
                  'ref': 'abcd',
                  'newrev': 'aaaa',
                  'oldrev': 'bbbb',
                  'pipeline': 'check'})
        self.assertEqual(401, resp.status_code)

    def test_token_expired(self):
        authz = {'iss': 'zuul_operator',
                 'sub': 'testuser',
                 'aud': 'zuul.example.com',
                 'zuul': {
                     'admin': ['tenant-one', ],
                 },
                 'exp': time.time() + 3600,
                 'iat': time.time()}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        time.sleep(10)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/autohold",
            headers={'Authorization': 'Bearer %s' % token},
            json={'job': 'project-test1',
                  'count': 1,
                  'reason': 'because',
                  'node_hold_expiration': 36000})
        self.assertEqual(401, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            headers={'Authorization': 'Bearer %s' % token},
            json={'trigger': 'gerrit',
                  'change': '2,1',
                  'pipeline': 'check'})
        self.assertEqual(401, resp.status_code)
        resp = self.post_url(
            "api/tenant/tenant-one/project/org/project/enqueue",
            headers={'Authorization': 'Bearer %s' % token},
            json={'trigger': 'gerrit',
                  'ref': 'abcd',
                  'newrev': 'aaaa',
                  'oldrev': 'bbbb',
                  'pipeline': 'check'})
        self.assertEqual(401, resp.status_code)

    def test_autohold(self):
        """Test that autohold can be set through the admin web interface"""
        args = {"reason": "some reason",
                "count": 1,
                'job': 'project-test2',
                'change': None,
                'ref': None,
                'node_hold_expiration': None}
        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ],
                 },
                 'exp': time.time() + 3600,
                 'iat': time.time()}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        req = self.post_url(
            'api/tenant/tenant-one/project/org/project/autohold',
            headers={'Authorization': 'Bearer %s' % token},
            json=args)
        self.assertEqual(200, req.status_code, req.text)
        data = req.json()
        self.assertEqual(True, data)

        # Check result in rpc client
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        autohold_requests = client.autohold_list()
        self.assertNotEqual([], autohold_requests)
        self.assertEqual(1, len(autohold_requests))

        ah_request = autohold_requests[0]
        self.assertEqual('tenant-one', ah_request['tenant'])
        self.assertIn('org/project', ah_request['project'])
        self.assertEqual('project-test2', ah_request['job'])
        self.assertEqual(".*", ah_request['ref_filter'])
        self.assertEqual("some reason", ah_request['reason'])


class TestHeldAttributeInBuildInfo(BaseTestWeb):
    config_file = 'zuul-sql-driver-mysql.conf'
    tenant_config_file = 'config/sql-driver/main.yaml'

    def test_autohold_and_retrieve_held_build_info(self):
        """Ensure the "held" attribute can be used to filter builds"""
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1)
        self.assertTrue(r)

        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        self.executor_server.failJob('project-test2', B)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        all_builds_resp = self.get_url("api/tenant/tenant-one/builds?"
                                       "project=org/project")
        held_builds_resp = self.get_url("api/tenant/tenant-one/builds?"
                                        "project=org/project&"
                                        "held=1")
        self.assertEqual(200,
                         all_builds_resp.status_code,
                         all_builds_resp.text)
        self.assertEqual(200,
                         held_builds_resp.status_code,
                         held_builds_resp.text)
        all_builds = all_builds_resp.json()
        held_builds = held_builds_resp.json()
        self.assertEqual(len(held_builds), 1, all_builds)
        held_build = held_builds[0]
        self.assertEqual('project-test2', held_build['job_name'], held_build)
        self.assertEqual(True, held_build['held'], held_build)


class TestWebMulti(BaseTestWeb):
    config_file = 'zuul-gerrit-github.conf'

    def test_web_connections_list_multi(self):
        data = self.get_url('api/connections').json()
        gerrit_connection = {
            'driver': 'gerrit',
            'name': 'gerrit',
            'baseurl': 'https://review.example.com',
            'canonical_hostname': 'review.example.com',
            'server': 'review.example.com',
            'port': 29418,
        }
        github_connection = {
            'baseurl': 'https://api.github.com',
            'canonical_hostname': 'github.com',
            'driver': 'github',
            'name': 'github',
            'server': 'github.com',
        }
        self.assertEqual([gerrit_connection, github_connection], data)


# TODO Remove this class once REST support is removed from Zuul CLI, or
# switch to the gearman client
class TestCLIViaWebApi(BaseTestWeb):
    config_file = 'zuul-admin-web.conf'

    def test_autohold(self):
        """Test that autohold can be set with the CLI through REST"""
        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ]
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '--zuul-url', self.base_url, '--auth-token', token,
             'autohold', '--reason', 'some reason',
             '--tenant', 'tenant-one', '--project', 'org/project',
             '--job', 'project-test2', '--count', '1'],
            stdout=subprocess.PIPE)
        output = p.communicate()
        self.assertEqual(p.returncode, 0, output[0])
        # Check result in rpc client
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        autohold_requests = client.autohold_list()
        self.assertNotEqual([], autohold_requests)
        self.assertEqual(1, len(autohold_requests))
        request = autohold_requests[0]
        self.assertEqual('tenant-one', request['tenant'])
        self.assertIn('org/project', request['project'])
        self.assertEqual('project-test2', request['job'])
        self.assertEqual(".*", request['ref_filter'])
        self.assertEqual("some reason", request['reason'])
        self.assertEqual(1, request['max_count'])

    def test_enqueue(self):
        """Test that the CLI can enqueue a change via REST"""
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        A.addApproval('Approved', 1)

        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ]
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '--zuul-url', self.base_url, '--auth-token', token,
             'enqueue', '--tenant', 'tenant-one',
             '--project', 'org/project',
             '--pipeline', 'gate', '--change', '1,1'],
            stdout=subprocess.PIPE)
        output = p.communicate()
        self.assertEqual(p.returncode, 0, output[0])
        self.waitUntilSettled()

    def test_enqueue_ref(self):
        """Test that the CLI can enqueue a ref via REST"""
        p = "review.example.com/org/project"
        upstream = self.getUpstreamRepos([p])
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.setMerged()
        A_commit = str(upstream[p].commit('master'))
        self.log.debug("A commit: %s" % A_commit)

        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ]
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '--zuul-url', self.base_url, '--auth-token', token,
             'enqueue-ref', '--tenant', 'tenant-one',
             '--project', 'org/project',
             '--pipeline', 'post', '--ref', 'master',
             '--oldrev', '90f173846e3af9154517b88543ffbd1691f31366',
             '--newrev', A_commit],
            stdout=subprocess.PIPE)
        output = p.communicate()
        self.assertEqual(p.returncode, 0, output[0])
        self.waitUntilSettled()

    def test_dequeue(self):
        """Test that the CLI can dequeue a change via REST"""
        start_builds = len(self.builds)
        self.create_branch('org/project', 'stable')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project', 'stable'))
        self.executor_server.hold_jobs_in_build = True
        self.commitConfigUpdate('common-config', 'layouts/timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        for _ in iterate_timeout(30, 'Wait for a build on hold'):
            if len(self.builds) > start_builds:
                break
        self.waitUntilSettled()

        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ]
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '--zuul-url', self.base_url, '--auth-token', token,
             'dequeue', '--tenant', 'tenant-one', '--project', 'org/project',
             '--pipeline', 'periodic', '--ref', 'refs/heads/stable'],
            stdout=subprocess.PIPE)
        output = p.communicate()
        self.assertEqual(p.returncode, 0, output[0])
        self.waitUntilSettled()

        self.commitConfigUpdate('common-config',
                                'layouts/no-timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 1)

    def test_promote(self):
        "Test that the RPC client can promote a change"
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))

        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        items = tenant.layout.pipelines['gate'].getAllItems()
        enqueue_times = {}
        for item in items:
            enqueue_times[str(item.change)] = item.enqueue_time

        # Promote B and C using the cli
        authz = {'iss': 'zuul_operator',
                 'aud': 'zuul.example.com',
                 'sub': 'testuser',
                 'zuul': {
                     'admin': ['tenant-one', ]
                 },
                 'exp': time.time() + 3600}
        token = jwt.encode(authz, key='NoDanaOnlyZuul',
                           algorithm='HS256')
        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '--zuul-url', self.base_url, '--auth-token', token,
             'promote', '--tenant', 'tenant-one',
             '--pipeline', 'gate', '--changes', '2,1', '3,1'],
            stdout=subprocess.PIPE)
        output = p.communicate()
        self.assertEqual(p.returncode, 0, output[0])
        self.waitUntilSettled()

        # ensure that enqueue times are durable
        items = tenant.layout.pipelines['gate'].getAllItems()
        for item in items:
            self.assertEqual(
                enqueue_times[str(item.change)], item.enqueue_time)

        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 6)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test2')
        self.assertEqual(self.builds[2].name, 'project-test1')
        self.assertEqual(self.builds[3].name, 'project-test2')
        self.assertEqual(self.builds[4].name, 'project-test1')
        self.assertEqual(self.builds[5].name, 'project-test2')

        self.assertTrue(self.builds[0].hasChanges(B))
        self.assertFalse(self.builds[0].hasChanges(A))
        self.assertFalse(self.builds[0].hasChanges(C))

        self.assertTrue(self.builds[2].hasChanges(B))
        self.assertTrue(self.builds[2].hasChanges(C))
        self.assertFalse(self.builds[2].hasChanges(A))

        self.assertTrue(self.builds[4].hasChanges(B))
        self.assertTrue(self.builds[4].hasChanges(C))
        self.assertTrue(self.builds[4].hasChanges(A))

        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(C.reported, 2)


class TestWebStartup(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'
    config_ini_data = {}

    def _start_web(self):
        # Start the web server
        self.web = ZuulWebFixture(
            self.changes, self.config, self.additional_event_queues,
            self.upstream_root, self.rpcclient, self.poller_events,
            self.git_url_with_auth, self.addCleanup, self.test_root,
            info=zuul.model.WebInfo.fromConfig(self.zuul_ini_config))
        self.useFixture(self.web)

    def get_url(self, url, *args, **kwargs):
        return requests.get(
            urllib.parse.urljoin(self.base_url, url), *args, **kwargs)

    def createScheduler(self):
        pass

    def realCreateScheduler(self):
        super().createScheduler()

    @skip("This test is not reliable in the gate")
    def test_web_startup(self):
        self.zuul_ini_config = FakeConfig(self.config_ini_data)
        self.web = None
        t = threading.Thread(target=self._start_web)
        t.daemon = True
        t.start()

        for _ in iterate_timeout(30, 'Wait for web to begin startup'):
            if self.web and getattr(self.web, 'web', None):
                break

        self.web.web.system_config_cache_wake_event.wait()

        self.realCreateScheduler()
        self.scheds.execute(
            lambda app: app.start(self.validate_tenants))

        t.join()

        self.host = 'localhost'
        # Wait until web server is started
        while True:
            if self.web is None:
                time.sleep(0.1)
                continue
            self.port = self.web.port
            try:
                with socket.create_connection((self.host, self.port)):
                    break
            except ConnectionRefusedError:
                pass
        self.base_url = "http://{host}:{port}".format(
            host=self.host, port=self.port)

        # If the config didn't load correctly, we won't have the jobs
        jobs = self.get_url("api/tenant/tenant-one/jobs").json()
        self.assertEqual(len(jobs), 10)

# Copyright 2012 Hewlett-Packard Development Company, L.P.
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

import configparser
import gc
import json
import os
import re
import shutil
import socket
import textwrap
import threading
import time
from collections import namedtuple
from unittest import mock, skip
from kazoo.exceptions import NoNodeError

import git
import testtools
from testtools.matchers import AfterPreprocessing, MatchesRegex
import fixtures

import zuul.change_matcher
from zuul.driver.gerrit import gerritreporter
import zuul.scheduler
import zuul.rpcclient
import zuul.model
import zuul.merger.merger

from tests.base import (
    SSLZuulTestCase,
    ZuulTestCase,
    repack_repo,
    simple_layout,
    iterate_timeout,
    RecordingExecutorServer,
    TestConnectionRegistry,
    FIXTURE_DIR,
    skipIfMultiScheduler,
)
from zuul.zk.change_cache import ChangeKey
from zuul.zk.layout import LayoutState

EMPTY_LAYOUT_STATE = LayoutState("", "", 0, None, {})


class TestSchedulerSSL(SSLZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def test_jobs_executed(self):
        "Test that jobs are executed and a change is merged"
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(self.getJobFromHistory('project-test1').node,
                         'label1')
        self.assertEqual(self.getJobFromHistory('project-test2').node,
                         'label1')


class TestSchedulerZone(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def setUp(self):
        super(TestSchedulerZone, self).setUp()
        self.fake_nodepool.attributes = {'executor-zone': 'test-provider.vpn'}

        # Create an unzoned executor
        config = configparser.ConfigParser()
        config.read_dict(self.config)
        config.remove_option('executor', 'zone')
        config.set('executor', 'command_socket',
                   os.path.join(self.test_root, 'executor2.socket'))
        executor_connections = TestConnectionRegistry(
            self.changes, self.config, self.additional_event_queues,
            self.upstream_root, self.rpcclient, self.poller_events,
            self.git_url_with_auth, self.addCleanup)
        executor_connections.configure(self.config,
                                       source_only=True)
        self.executor_server_unzoned = RecordingExecutorServer(
            config,
            connections=executor_connections,
            jobdir_root=self.jobdir_root,
            _run_ansible=self.run_ansible,
            _test_root=self.test_root,
            log_console_port=self.log_console_port)
        self.executor_server_unzoned.start()
        self.addCleanup(self._shutdown_executor)

    def _shutdown_executor(self):
        self.executor_server_unzoned.hold_jobs_in_build = False
        self.executor_server_unzoned.release()
        self.executor_server_unzoned.stop()
        self.executor_server_unzoned.join()

    def setup_config(self, config_file: str):
        config = super(TestSchedulerZone, self).setup_config(config_file)
        config.set('executor', 'zone', 'test-provider.vpn')
        return config

    def test_jobs_executed(self):
        "Test that jobs are executed and a change is merged per zone"

        # Validate that the reported executor stats are correct. There must
        # be two executors online (one unzoned and one zoned)
        # TODO(corvus): remove deprecated top-level stats in 5.0
        self.assertReportedStat(
            'zuul.executors.online', value='2', kind='g')
        self.assertReportedStat(
            'zuul.executors.unzoned.online', value='1', kind='g')
        self.assertReportedStat(
            'zuul.executors.zone.test-provider_vpn.online',
            value='1', kind='g')

        self.hold_jobs_in_queue = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        queue = list(self.executor_api.queued())
        self.assertEqual(len(self.builds), 0)
        self.assertEqual(len(queue), 1)
        self.assertEqual('test-provider.vpn', queue[0].zone)

        self.hold_jobs_in_queue = False
        self.executor_api.release()
        self.waitUntilSettled()

        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(self.getJobFromHistory('project-test1').node,
                         'label1')
        self.assertEqual(self.getJobFromHistory('project-test2').node,
                         'label1')

        # Validate that both (zoned and unzoned) executors are accepting work
        self.assertReportedStat(
            'zuul.executors.accepting', value='2', kind='g')
        self.assertReportedStat(
            'zuul.executors.unzoned.accepting', value='1', kind='g')
        self.assertReportedStat(
            'zuul.executors.zone.test-provider_vpn.accepting',
            value='1', kind='g')

    def test_executor_disconnect(self):
        "Test that jobs are completed after an executor disconnect"

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        # Forcibly disconnect the executor from ZK
        self.executor_server.zk_client.client.stop()
        self.executor_server.zk_client.client.start()

        # Find the build in the scheduler so we can check its status
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        items = tenant.layout.pipelines['gate'].getAllItems()
        builds = items[0].current_build_set.getBuilds()
        build = builds[0]

        # Clean up the build
        self.scheds.first.sched.executor.cleanupLostBuildRequests()
        # Wait for the build to be reported as lost
        for x in iterate_timeout(30, 'retry build'):
            if build.result == 'RETRY':
                break

        # If we didn't timeout, then it worked; we're done
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        # There is a test-only race in the recording executor class
        # where we may record a successful first build, even though
        # the executor didn't actually send a build complete event.
        # This could probabyl be improved, but for now, it's
        # sufficient to verify that the job was retried.  So we omit a
        # result classifier on the first build.
        self.assertHistory([
            dict(name='project-merge', changes='1,1'),
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
        ], ordered=False)


class TestSchedulerZoneFallback(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def setup_config(self, config_file: str):
        config = super().setup_config(config_file)
        config.set('executor', 'zone', 'test-provider.vpn')
        config.set('executor', 'allow_unzoned', 'true')
        return config

    def test_jobs_executed(self):
        "Test that jobs are executed and a change is merged per zone"
        self.hold_jobs_in_queue = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        queue = list(self.executor_api.queued())
        self.assertEqual(len(self.builds), 0)
        self.assertEqual(len(queue), 1)
        self.assertEqual(None, queue[0].zone)

        self.hold_jobs_in_queue = False
        self.executor_api.release()
        self.waitUntilSettled()

        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(self.getJobFromHistory('project-test1').node,
                         'label1')
        self.assertEqual(self.getJobFromHistory('project-test2').node,
                         'label1')


class TestSchedulerAutoholdHoldExpiration(ZuulTestCase):
    '''
    This class of tests validates the autohold node expiration values
    are set correctly via zuul config or from a custom value.
    '''
    config_file = 'zuul-hold-expiration.conf'
    tenant_config_file = 'config/single-tenant/main.yaml'

    @simple_layout('layouts/autohold.yaml')
    def test_autohold_max_hold_default(self):
        '''
        Test that the hold request node expiration will default to the
        value specified in the configuration file.
        '''
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        # Add a autohold with no hold expiration.
        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1)
        self.assertTrue(r)

        # There should be a record in ZooKeeper
        request_list = self.sched_zk_nodepool.getHoldRequests()
        self.assertEqual(1, len(request_list))
        request = self.sched_zk_nodepool.getHoldRequest(
            request_list[0])
        self.assertIsNotNone(request)
        self.assertEqual('tenant-one', request.tenant)
        self.assertEqual('review.example.com/org/project', request.project)
        self.assertEqual('project-test2', request.job)
        self.assertEqual('reason text', request.reason)
        self.assertEqual(1, request.max_count)
        self.assertEqual(0, request.current_count)
        self.assertEqual([], request.nodes)
        # This should be the default value from the zuul config file.
        self.assertEqual(1800, request.node_expiration)

    @simple_layout('layouts/autohold.yaml')
    def test_autohold_max_hold_custom(self):
        '''
        Test that the hold request node expiration will be set to the custom
        value specified in the request.
        '''
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        # Add a autohold with a custom hold expiration.
        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1, 500)
        self.assertTrue(r)

        # There should be a record in ZooKeeper
        request_list = self.sched_zk_nodepool.getHoldRequests()
        self.assertEqual(1, len(request_list))
        request = self.sched_zk_nodepool.getHoldRequest(
            request_list[0])
        self.assertIsNotNone(request)
        self.assertEqual('tenant-one', request.tenant)
        self.assertEqual('review.example.com/org/project', request.project)
        self.assertEqual('project-test2', request.job)
        self.assertEqual('reason text', request.reason)
        self.assertEqual(1, request.max_count)
        self.assertEqual(0, request.current_count)
        self.assertEqual([], request.nodes)
        # This should be the value from the user request.
        self.assertEqual(500, request.node_expiration)

    @simple_layout('layouts/autohold.yaml')
    def test_autohold_max_hold_custom_invalid(self):
        '''
        Test that if the custom hold request node expiration is higher than our
        configured max, it will be lowered to the max.
        '''
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        # Add a autohold with a custom hold expiration that is higher than our
        # configured max.
        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1, 10000)
        self.assertTrue(r)

        # There should be a record in ZooKeeper
        request_list = self.sched_zk_nodepool.getHoldRequests()
        self.assertEqual(1, len(request_list))
        request = self.sched_zk_nodepool.getHoldRequest(
            request_list[0])
        self.assertIsNotNone(request)
        self.assertEqual('tenant-one', request.tenant)
        self.assertEqual('review.example.com/org/project', request.project)
        self.assertEqual('project-test2', request.job)
        self.assertEqual('reason text', request.reason)
        self.assertEqual(1, request.max_count)
        self.assertEqual(0, request.current_count)
        self.assertEqual([], request.nodes)
        # This should be the max value from the zuul config file.
        self.assertEqual(3600, request.node_expiration)


class TestScheduler(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def test_jobs_executed(self):
        "Test that jobs are executed and a change is merged"

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(self.getJobFromHistory('project-test1').node,
                         'label1')
        self.assertEqual(self.getJobFromHistory('project-test2').node,
                         'label1')

        # TODOv3(jeblair): we may want to report stats by tenant (also?).
        # Per-driver
        self.assertReportedStat('zuul.event.gerrit.comment-added', value='1',
                                kind='c')
        # Per-driver per-connection
        self.assertReportedStat('zuul.event.gerrit.gerrit.comment-added',
                                value='1', kind='c')
        self.assertReportedStat(
            'zuul.tenant.tenant-one.trigger_events', value='0', kind='g')
        self.assertReportedStat(
            'zuul.tenant.tenant-one.management_events', value='0', kind='g')
        self.assertReportedStat(
            'zuul.tenant.tenant-one.pipeline.gate.current_changes',
            value='1', kind='g')
        self.assertReportedStat(
            'zuul.tenant.tenant-one.pipeline.gate.project.review_example_com.'
            'org_project.master.job.project-merge.SUCCESS', kind='ms')
        self.assertReportedStat(
            'zuul.tenant.tenant-one.pipeline.gate.project.review_example_com.'
            'org_project.master.job.project-merge.SUCCESS', value='1',
            kind='c')
        self.assertReportedStat(
            'zuul.tenant.tenant-one.pipeline.gate.resident_time', kind='ms')
        self.assertReportedStat(
            'zuul.tenant.tenant-one.pipeline.gate.total_changes', value='1',
            kind='c')
        self.assertReportedStat(
            'zuul.tenant.tenant-one.pipeline.gate.trigger_events',
            value='0', kind='g')
        self.assertReportedStat(
            'zuul.tenant.tenant-one.pipeline.gate.result_events',
            value='0', kind='g')
        self.assertReportedStat(
            'zuul.tenant.tenant-one.pipeline.gate.management_events',
            value='0', kind='g')
        self.assertReportedStat(
            'zuul.tenant.tenant-one.pipeline.gate.project.review_example_com.'
            'org_project.master.resident_time', kind='ms')
        self.assertReportedStat(
            'zuul.tenant.tenant-one.pipeline.gate.project.review_example_com.'
            'org_project.master.total_changes', value='1', kind='c')
        exec_key = 'zuul.executor.%s' % self.executor_server.hostname.replace(
            '.', '_')
        self.assertReportedStat(exec_key + '.builds', value='1', kind='c')
        self.assertReportedStat(exec_key + '.starting_builds', kind='g')
        self.assertReportedStat(exec_key + '.starting_builds', kind='ms')
        self.assertReportedStat(
            'zuul.nodepool.requests.requested.total', value='1', kind='c')
        self.assertReportedStat(
            'zuul.nodepool.requests.requested.label.label1',
            value='1', kind='c')
        self.assertReportedStat(
            'zuul.nodepool.requests.fulfilled.label.label1',
            value='1', kind='c')
        self.assertReportedStat(
            'zuul.nodepool.requests.requested.size.1', value='1', kind='c')
        self.assertReportedStat(
            'zuul.nodepool.requests.fulfilled.size.1', value='1', kind='c')
        # just check for existence, since we can not know if a request is
        # in-flight during the sched._stats_inverval
        self.assertReportedStat(
            'zuul.nodepool.current_requests', kind='g')
        self.assertReportedStat(
            'zuul.nodepool.tenant.tenant-one.current_requests', kind='g')
        self.assertReportedStat(
            'zuul.executors.online', value='1', kind='g')
        self.assertReportedStat(
            'zuul.executors.accepting', value='1', kind='g')
        self.assertReportedStat(
            'zuul.mergers.online', value='1', kind='g')
        self.assertReportedStat('zuul.scheduler.eventqueues.connection.gerrit',
                                value='0', kind='g')

        # Catch time / monotonic errors
        val = self.assertReportedStat(
            'zuul.tenant.tenant-one.event_enqueue_processing_time',
            kind='ms')
        self.assertTrue(0.0 < float(val) < 60000.0)
        val = self.assertReportedStat(
            'zuul.tenant.tenant-one.event_enqueue_time', kind='ms')
        self.assertTrue(0.0 < float(val) < 60000.0)

        for build in self.history:
            self.assertTrue(build.parameters['zuul']['voting'])

    def test_initial_pipeline_gauges(self):
        "Test that each pipeline reported its length on start"
        self.assertReportedStat('zuul.tenant.tenant-one.pipeline.gate.'
                                'current_changes',
                                value='0', kind='g')
        self.assertReportedStat('zuul.tenant.tenant-one.pipeline.check.'
                                'current_changes',
                                value='0', kind='g')

    def test_job_branch(self):
        "Test the correct variant of a job runs on a branch"
        self.create_branch('org/project', 'stable')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project', 'stable'))
        self.waitUntilSettled()

        A = self.fake_gerrit.addFakeChange('org/project', 'stable', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2,
                         "A should report start and success")
        self.assertIn('gate', A.messages[1],
                      "A should transit gate")
        self.assertEqual(self.getJobFromHistory('project-test1').node,
                         'label2')

    @simple_layout('layouts/branch-deletion.yaml')
    def test_branch_deletion(self):
        "Test the correct variant of a job runs on a branch"

        # Start a secondary merger so this test exercises branch
        # deletion on both a merger and a separate executor.
        self.executor_server._merger_running = False
        self.executor_server.merger_loop_wake_event.set()
        self.executor_server.merger_thread.join()
        self._startMerger()

        self.create_branch('org/project', 'stable')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project', 'stable'))
        self.waitUntilSettled()
        A = self.fake_gerrit.addFakeChange('org/project', 'stable', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')

        self.delete_branch('org/project', 'stable')
        path = os.path.join(self.executor_src_root, 'review.example.com')
        shutil.rmtree(path)

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        build = self.builds[0]

        # Make sure there is no stable branch in the checked out git repo.
        pname = 'review.example.com/org/project'
        work = build.getWorkspaceRepos([pname])
        work = work[pname]
        heads = set([str(x) for x in work.heads])
        self.assertEqual(heads, set(['master']))
        self.executor_server.hold_jobs_in_build = False
        build.release()
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')

    def test_parallel_changes(self):
        "Test that changes are tested in parallel and merged in series"

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
        self.assertEqual(len(self.builds), 1)
        self.assertEqual(self.builds[0].name, 'project-merge')
        self.assertTrue(self.builds[0].hasChanges(A))

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 3)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertTrue(self.builds[0].hasChanges(A))
        self.assertEqual(self.builds[1].name, 'project-test2')
        self.assertTrue(self.builds[1].hasChanges(A))
        self.assertEqual(self.builds[2].name, 'project-merge')
        self.assertTrue(self.builds[2].hasChanges(A, B))

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 5)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertTrue(self.builds[0].hasChanges(A))
        self.assertEqual(self.builds[1].name, 'project-test2')
        self.assertTrue(self.builds[1].hasChanges(A))

        self.assertEqual(self.builds[2].name, 'project-test1')
        self.assertTrue(self.builds[2].hasChanges(A, B))
        self.assertEqual(self.builds[3].name, 'project-test2')
        self.assertTrue(self.builds[3].hasChanges(A, B))

        self.assertEqual(self.builds[4].name, 'project-merge')
        self.assertTrue(self.builds[4].hasChanges(A, B, C))

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 6)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertTrue(self.builds[0].hasChanges(A))
        self.assertEqual(self.builds[1].name, 'project-test2')
        self.assertTrue(self.builds[1].hasChanges(A))

        self.assertEqual(self.builds[2].name, 'project-test1')
        self.assertTrue(self.builds[2].hasChanges(A, B))
        self.assertEqual(self.builds[3].name, 'project-test2')
        self.assertTrue(self.builds[3].hasChanges(A, B))

        self.assertEqual(self.builds[4].name, 'project-test1')
        self.assertTrue(self.builds[4].hasChanges(A, B, C))
        self.assertEqual(self.builds[5].name, 'project-test2')
        self.assertTrue(self.builds[5].hasChanges(A, B, C))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 0)

        self.assertEqual(len(self.history), 9)
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)

    def test_failed_changes(self):
        "Test that a change behind a failed change is retested"
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)

        self.executor_server.failJob('project-test1', A)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertBuilds([dict(name='project-merge', changes='1,1')])

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        # A/project-merge is complete
        self.assertBuilds([
            dict(name='project-test1', changes='1,1'),
            dict(name='project-test2', changes='1,1'),
            dict(name='project-merge', changes='1,1 2,1'),
        ])

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        # A/project-merge is complete
        # B/project-merge is complete
        self.assertBuilds([
            dict(name='project-test1', changes='1,1'),
            dict(name='project-test2', changes='1,1'),
            dict(name='project-test1', changes='1,1 2,1'),
            dict(name='project-test2', changes='1,1 2,1'),
        ])

        # Release project-test1 for A which will fail.  This will
        # abort both running B jobs and reexecute project-merge for B.
        self.builds[0].release()
        self.waitUntilSettled()

        self.orderedRelease()
        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-merge', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-test1', result='FAILURE', changes='1,1'),
            dict(name='project-test1', result='ABORTED', changes='1,1 2,1'),
            dict(name='project-test2', result='ABORTED', changes='1,1 2,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
            dict(name='project-merge', result='SUCCESS', changes='2,1'),
            dict(name='project-test1', result='SUCCESS', changes='2,1'),
            dict(name='project-test2', result='SUCCESS', changes='2,1'),
        ], ordered=False)

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)

        # Make sure that after a reset of the buildset the files state is
        # updated correctly and the schedulers is not resolving the list
        # of changed files via the merger.
        self.assertIsNone(
            self.scheds.first.sched.merger.merger_api.history.get(
                "fileschanges"))

    def test_independent_queues(self):
        "Test that changes end up in the right queues"

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project2', 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        # There should be one merge job at the head of each queue running
        self.assertBuilds([
            dict(name='project-merge', changes='1,1'),
            dict(name='project-merge', changes='2,1'),
        ])

        # Release the current merge builds
        self.builds[0].release()
        self.waitUntilSettled()
        self.builds[0].release()
        self.waitUntilSettled()
        # Release the merge job for project2 which is behind project1
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        # All the test builds should be running:
        self.assertBuilds([
            dict(name='project-test1', changes='1,1'),
            dict(name='project-test2', changes='1,1'),
            dict(name='project-test1', changes='2,1'),
            dict(name='project-test2', changes='2,1'),
            dict(name='project1-project2-integration', changes='2,1'),
            dict(name='project-test1', changes='2,1 3,1'),
            dict(name='project-test2', changes='2,1 3,1'),
            dict(name='project1-project2-integration', changes='2,1 3,1'),
        ])

        self.orderedRelease()
        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-merge', result='SUCCESS', changes='2,1'),
            dict(name='project-merge', result='SUCCESS', changes='2,1 3,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='SUCCESS', changes='2,1'),
            dict(name='project-test2', result='SUCCESS', changes='2,1'),
            dict(
                name='project1-project2-integration',
                result='SUCCESS',
                changes='2,1'),
            dict(name='project-test1', result='SUCCESS', changes='2,1 3,1'),
            dict(name='project-test2', result='SUCCESS', changes='2,1 3,1'),
            dict(name='project1-project2-integration',
                 result='SUCCESS',
                 changes='2,1 3,1'),
        ])

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)

    def test_failed_change_at_head(self):
        "Test that if a change at the head fails, jobs behind it are canceled"

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        self.executor_server.failJob('project-test1', A)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))

        self.waitUntilSettled()

        self.assertBuilds([
            dict(name='project-merge', changes='1,1'),
        ])

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        self.assertBuilds([
            dict(name='project-test1', changes='1,1'),
            dict(name='project-test2', changes='1,1'),
            dict(name='project-test1', changes='1,1 2,1'),
            dict(name='project-test2', changes='1,1 2,1'),
            dict(name='project-test1', changes='1,1 2,1 3,1'),
            dict(name='project-test2', changes='1,1 2,1 3,1'),
        ])

        self.release(self.builds[0])
        self.waitUntilSettled()

        # project-test2, project-merge for B
        self.assertBuilds([
            dict(name='project-test2', changes='1,1'),
            dict(name='project-merge', changes='2,1'),
        ])
        # Unordered history comparison because the aborts can finish
        # in any order.
        self.assertHistory([
            dict(name='project-merge', result='SUCCESS',
                 changes='1,1'),
            dict(name='project-merge', result='SUCCESS',
                 changes='1,1 2,1'),
            dict(name='project-merge', result='SUCCESS',
                 changes='1,1 2,1 3,1'),
            dict(name='project-test1', result='FAILURE',
                 changes='1,1'),
            dict(name='project-test1', result='ABORTED',
                 changes='1,1 2,1'),
            dict(name='project-test2', result='ABORTED',
                 changes='1,1 2,1'),
            dict(name='project-test1', result='ABORTED',
                 changes='1,1 2,1 3,1'),
            dict(name='project-test2', result='ABORTED',
                 changes='1,1 2,1 3,1'),
        ], ordered=False)

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.orderedRelease()

        self.assertBuilds([])
        self.assertHistory([
            dict(name='project-merge', result='SUCCESS',
                 changes='1,1'),
            dict(name='project-merge', result='SUCCESS',
                 changes='1,1 2,1'),
            dict(name='project-merge', result='SUCCESS',
                 changes='1,1 2,1 3,1'),
            dict(name='project-test1', result='FAILURE',
                 changes='1,1'),
            dict(name='project-test1', result='ABORTED',
                 changes='1,1 2,1'),
            dict(name='project-test2', result='ABORTED',
                 changes='1,1 2,1'),
            dict(name='project-test1', result='ABORTED',
                 changes='1,1 2,1 3,1'),
            dict(name='project-test2', result='ABORTED',
                 changes='1,1 2,1 3,1'),
            dict(name='project-merge', result='SUCCESS',
                 changes='2,1'),
            dict(name='project-merge', result='SUCCESS',
                 changes='2,1 3,1'),
            dict(name='project-test2', result='SUCCESS',
                 changes='1,1'),
            dict(name='project-test1', result='SUCCESS',
                 changes='2,1'),
            dict(name='project-test2', result='SUCCESS',
                 changes='2,1'),
            dict(name='project-test1', result='SUCCESS',
                 changes='2,1 3,1'),
            dict(name='project-test2', result='SUCCESS',
                 changes='2,1 3,1'),
        ], ordered=False)

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)

    def test_failed_change_in_middle(self):
        "Test a failed change in the middle of the queue"

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        self.executor_server.failJob('project-test1', B)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))

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

        self.release(self.builds[2])
        self.waitUntilSettled()

        # project-test1 and project-test2 for A
        # project-test2 for B
        # project-merge for C (without B)
        self.assertEqual(len(self.builds), 4)
        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 2)

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        # project-test1 and project-test2 for A
        # project-test2 for B
        # project-test1 and project-test2 for C
        self.assertEqual(len(self.builds), 5)

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        items = tenant.layout.pipelines['gate'].getAllItems()
        builds = items[0].current_build_set.getBuilds()
        self.assertEqual(self.countJobResults(builds, 'SUCCESS'), 1)
        self.assertEqual(self.countJobResults(builds, None), 2)
        builds = items[1].current_build_set.getBuilds()
        self.assertEqual(self.countJobResults(builds, 'SUCCESS'), 1)
        self.assertEqual(self.countJobResults(builds, 'FAILURE'), 1)
        self.assertEqual(self.countJobResults(builds, None), 1)
        builds = items[2].current_build_set.getBuilds()
        self.assertEqual(self.countJobResults(builds, 'SUCCESS'), 1)
        self.assertEqual(self.countJobResults(builds, None), 2)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)
        self.assertEqual(len(self.history), 12)
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)

    def test_failed_change_at_head_with_queue(self):
        "Test that if a change at the head fails, queued jobs are canceled"

        def get_name(params):
            return params.get('job_ref', '').split('/')[-1]

        self.hold_jobs_in_queue = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        self.executor_server.failJob('project-test1', A)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))

        self.waitUntilSettled()
        queue = list(self.executor_api.queued())
        self.assertEqual(len(self.builds), 0)
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0].zone, None)
        params = self.executor_server.executor_api.getParams(queue[0])
        self.assertEqual(get_name(params), 'project-merge')
        self.assertEqual(params['items'][0]['number'], '%d' % A.number)

        self.executor_api.release('.*-merge')
        self.waitUntilSettled()
        self.executor_api.release('.*-merge')
        self.waitUntilSettled()
        self.executor_api.release('.*-merge')
        self.waitUntilSettled()
        queue = list(self.executor_api.queued())
        params = [self.executor_server.executor_api.getParams(item)
                  for item in queue]

        self.assertEqual(len(self.builds), 0)
        self.assertEqual(len(queue), 6)

        self.assertEqual(get_name(params[0]), 'project-test1')
        self.assertEqual(get_name(params[1]), 'project-test2')
        self.assertEqual(get_name(params[2]), 'project-test1')
        self.assertEqual(get_name(params[3]), 'project-test2')
        self.assertEqual(get_name(params[4]), 'project-test1')
        self.assertEqual(get_name(params[5]), 'project-test2')

        self.executor_api.release(queue[0])
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)
        queue = list(self.executor_api.queued())
        self.assertEqual(len(queue), 2)  # project-test2, project-merge for B
        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 0)

        self.hold_jobs_in_queue = False
        self.executor_api.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)
        self.assertEqual(len(self.history), 11)
        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)

    def _test_time_database(self, iteration):
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        time.sleep(2)

        found_job = None
        pipeline = self.scheds.first.sched.abide.tenants[
            'tenant-one'].layout.pipelines['gate']
        pipeline_status = pipeline.formatStatusJSON(
            self.scheds.first.sched.globals.websocket_url)
        for queue in pipeline_status['change_queues']:
            for head in queue['heads']:
                for item in head:
                    for job in item['jobs']:
                        if job['name'] == 'project-merge':
                            found_job = job
                            break

        self.assertIsNotNone(found_job)
        if iteration == 1:
            self.assertIsNotNone(found_job['estimated_time'])
            self.assertIsNone(found_job['remaining_time'])
        else:
            self.assertIsNotNone(found_job['estimated_time'])
            self.assertTrue(found_job['estimated_time'] >= 2)
            self.assertIsNotNone(found_job['remaining_time'])

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    def test_time_database(self):
        "Test the time database"

        self._test_time_database(1)
        self._test_time_database(2)

    def test_two_failed_changes_at_head(self):
        "Test that changes are reparented correctly if 2 fail at head"

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        self.executor_server.failJob('project-test1', A)
        self.executor_server.failJob('project-test1', B)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
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

        self.assertTrue(self.builds[0].hasChanges(A))
        self.assertTrue(self.builds[2].hasChanges(A))
        self.assertTrue(self.builds[2].hasChanges(B))
        self.assertTrue(self.builds[4].hasChanges(A))
        self.assertTrue(self.builds[4].hasChanges(B))
        self.assertTrue(self.builds[4].hasChanges(C))

        # Fail change B first
        self.release(self.builds[2])
        self.waitUntilSettled()

        # restart of C after B failure
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 5)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test2')
        self.assertEqual(self.builds[2].name, 'project-test2')
        self.assertEqual(self.builds[3].name, 'project-test1')
        self.assertEqual(self.builds[4].name, 'project-test2')

        self.assertTrue(self.builds[1].hasChanges(A))
        self.assertTrue(self.builds[2].hasChanges(A))
        self.assertTrue(self.builds[2].hasChanges(B))
        self.assertTrue(self.builds[4].hasChanges(A))
        self.assertFalse(self.builds[4].hasChanges(B))
        self.assertTrue(self.builds[4].hasChanges(C))

        # Finish running all passing jobs for change A
        self.release(self.builds[1])
        self.waitUntilSettled()
        # Fail and report change A
        self.release(self.builds[0])
        self.waitUntilSettled()

        # restart of B,C after A failure
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 4)
        self.assertEqual(self.builds[0].name, 'project-test1')  # B
        self.assertEqual(self.builds[1].name, 'project-test2')  # B
        self.assertEqual(self.builds[2].name, 'project-test1')  # C
        self.assertEqual(self.builds[3].name, 'project-test2')  # C

        self.assertFalse(self.builds[1].hasChanges(A))
        self.assertTrue(self.builds[1].hasChanges(B))
        self.assertFalse(self.builds[1].hasChanges(C))

        self.assertFalse(self.builds[2].hasChanges(A))
        # After A failed and B and C restarted, B should be back in
        # C's tests because it has not failed yet.
        self.assertTrue(self.builds[2].hasChanges(B))
        self.assertTrue(self.builds[2].hasChanges(C))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)
        self.assertEqual(len(self.history), 21)
        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)

    def test_patch_order(self):
        "Test that dependent patches are tested in the right order"
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        M2 = self.fake_gerrit.addFakeChange('org/project', 'master', 'M2')
        M1 = self.fake_gerrit.addFakeChange('org/project', 'master', 'M1')
        M2.setMerged()
        M1.setMerged()

        # C -> B -> A -> M1 -> M2
        # M2 is here to make sure it is never queried.  If it is, it
        # means zuul is walking down the entire history of merged
        # changes.

        C.setDependsOn(B, 1)
        B.setDependsOn(A, 1)
        A.setDependsOn(M1, 1)
        M1.setDependsOn(M2, 1)

        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))

        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(C.data['status'], 'NEW')

        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))

        self.waitUntilSettled()
        self.assertEqual(M2.queried, 0)
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)

    def test_needed_changes_enqueue(self):
        "Test that a needed change is enqueued ahead"
        #          A      Given a git tree like this, if we enqueue
        #         / \     change C, we should walk up and down the tree
        #        B   G    and enqueue changes in the order ABCDEFG.
        #       /|\       This is also the order that you would get if
        #     *C E F      you enqueued changes in the order ABCDEFG, so
        #     /           the ordering is stable across re-enqueue events.
        #    D

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        D = self.fake_gerrit.addFakeChange('org/project', 'master', 'D')
        E = self.fake_gerrit.addFakeChange('org/project', 'master', 'E')
        F = self.fake_gerrit.addFakeChange('org/project', 'master', 'F')
        G = self.fake_gerrit.addFakeChange('org/project', 'master', 'G')
        B.setDependsOn(A, 1)
        C.setDependsOn(B, 1)
        D.setDependsOn(C, 1)
        E.setDependsOn(B, 1)
        F.setDependsOn(B, 1)
        G.setDependsOn(A, 1)

        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        D.addApproval('Code-Review', 2)
        E.addApproval('Code-Review', 2)
        F.addApproval('Code-Review', 2)
        G.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))

        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(C.data['status'], 'NEW')
        self.assertEqual(D.data['status'], 'NEW')
        self.assertEqual(E.data['status'], 'NEW')
        self.assertEqual(F.data['status'], 'NEW')
        self.assertEqual(G.data['status'], 'NEW')

        # We're about to add approvals to changes without adding the
        # triggering events to Zuul, so that we can be sure that it is
        # enqueing the changes based on dependencies, not because of
        # triggering events.  Since it will have the changes cached
        # already (without approvals), we need to clear the cache
        # first.
        for connection in self.scheds.first.connections.connections.values():
            if hasattr(connection, '_change_cache'):
                connection.maintainCache([], max_age=0)

        self.executor_server.hold_jobs_in_build = True
        A.addApproval('Approved', 1)
        B.addApproval('Approved', 1)
        D.addApproval('Approved', 1)
        E.addApproval('Approved', 1)
        F.addApproval('Approved', 1)
        G.addApproval('Approved', 1)
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))

        for x in range(8):
            self.executor_server.release('.*-merge')
            self.waitUntilSettled()
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(D.data['status'], 'MERGED')
        self.assertEqual(E.data['status'], 'MERGED')
        self.assertEqual(F.data['status'], 'MERGED')
        self.assertEqual(G.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)
        self.assertEqual(D.reported, 2)
        self.assertEqual(E.reported, 2)
        self.assertEqual(F.reported, 2)
        self.assertEqual(G.reported, 2)
        self.assertEqual(self.history[6].changes,
                         '1,1 2,1 3,1 4,1 5,1 6,1 7,1')

    def test_source_cache(self):
        "Test that the source cache operates correctly"
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        X = self.fake_gerrit.addFakeChange('org/project', 'master', 'X')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)

        M1 = self.fake_gerrit.addFakeChange('org/project', 'master', 'M1')
        M1.setMerged()

        B.setDependsOn(A, 1)
        A.setDependsOn(M1, 1)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(X.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        for build in self.builds:
            if build.pipeline == 'check':
                build.release()
        self.waitUntilSettled()
        for build in self.builds:
            if build.pipeline == 'check':
                build.release()
        self.waitUntilSettled()

        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        cached_changes = list(self.fake_gerrit._change_cache)
        self.log.debug("len %s", [c.cache_key for c in cached_changes])
        # there should still be changes in the cache
        self.assertNotEqual(len(cached_changes), 0)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(A.queried, 2)  # Initial and isMerged
        self.assertEqual(B.queried, 3)  # Initial A, refresh from B, isMerged

    def test_connection_cache_cleanup(self):
        "Test that cached changes are correctly cleaned up"
        sched = self.scheds.first.sched

        def _getCachedChanges():
            cached = set()
            for source in sched.connections.getSources():
                cached.update(source.getCachedChanges())
            return cached

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        B.setDependsOn(A, 1)
        self.hold_jobs_in_queue = True
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        C.setMerged()
        self.fake_gerrit.addEvent(C.getRefUpdatedEvent())
        self.waitUntilSettled()

        self.assertEqual(len(_getCachedChanges()), 3)
        sched.maintainConnectionCache()
        self.assertEqual(len(_getCachedChanges()), 3)

        # Test this method separately to make sure we are getting
        # cache keys of the correct type, since we don't do run-time
        # validation.
        relevant = sched._gatherConnectionCacheKeys()
        self.assertEqual(len(relevant), 2)
        for k in relevant:
            if not isinstance(k, ChangeKey):
                raise RuntimeError("Cache key %s is not a ChangeKey" % repr(k))

        self.hold_jobs_in_queue = False
        self.executor_api.release()
        self.waitUntilSettled()

        self.assertEqual(len(_getCachedChanges()), 3)
        sched.maintainConnectionCache()
        self.assertEqual(len(_getCachedChanges()), 3)

        # Test that outdated but still relevant changes are not cleaned up
        for connection in sched.connections.connections.values():
            connection.maintainCache(
                set([c.cache_stat.key for c in _getCachedChanges()]),
                max_age=0)
        self.assertEqual(len(_getCachedChanges()), 3)

        change1 = None
        change2 = None
        for c in _getCachedChanges():
            if c.cache_stat.key.stable_id == '1':
                change1 = c
            if c.cache_stat.key.stable_id == '2':
                change2 = c
        # Make change1 eligible for cleanup, but not change2
        change1.cache_stat = zuul.model.CacheStat(change1.cache_stat.key,
                                                  change1.cache_stat.uuid,
                                                  change1.cache_stat.version,
                                                  0.0)
        # We should not delete change1 since it's needed by change2
        # which we want to keep.
        for connection in sched.connections.connections.values():
            connection.maintainCache([], max_age=7200)
        self.assertEqual(len(_getCachedChanges()), 3)

        # Make both changes eligible for deletion
        change2.cache_stat = zuul.model.CacheStat(change2.cache_stat.key,
                                                  change2.cache_stat.uuid,
                                                  change2.cache_stat.version,
                                                  0.0)
        for connection in sched.connections.connections.values():
            connection.maintainCache([], max_age=7200)
        # The master branch change remains
        self.assertEqual(len(_getCachedChanges()), 1)

        # Test that we can remove changes once max_age has expired
        for connection in sched.connections.connections.values():
            connection.maintainCache([], max_age=0)
        self.assertEqual(len(_getCachedChanges()), 0)

    def test_can_merge(self):
        "Test whether a change is ready to merge"
        # TODO: move to test_gerrit (this is a unit test!)
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        (trusted, project) = tenant.getProject('org/project')
        source = project.source

        # TODO(pabelanger): As we add more source / trigger APIs we should make
        # it easier for users to create events for testing.
        event = zuul.model.TriggerEvent()
        event.trigger_name = 'gerrit'
        event.change_number = '1'
        event.patch_number = '2'

        a = source.getChange(event)
        mgr = tenant.layout.pipelines['gate'].manager
        self.assertFalse(source.canMerge(a, mgr.getSubmitAllowNeeds()))

        A.addApproval('Code-Review', 2)
        a = source.getChange(event, refresh=True)
        self.assertFalse(source.canMerge(a, mgr.getSubmitAllowNeeds()))

        A.addApproval('Approved', 1)
        a = source.getChange(event, refresh=True)
        self.assertTrue(source.canMerge(a, mgr.getSubmitAllowNeeds()))

        A.setWorkInProgress(True)
        a = source.getChange(event, refresh=True)
        self.assertFalse(source.canMerge(a, mgr.getSubmitAllowNeeds()))

    def test_project_merge_conflict(self):
        "Test that gate merge conflicts are handled properly"

        self.hold_jobs_in_queue = True
        A = self.fake_gerrit.addFakeChange('org/project',
                                           'master', 'A',
                                           files={'conflict': 'foo'})
        B = self.fake_gerrit.addFakeChange('org/project',
                                           'master', 'B',
                                           files={'conflict': 'bar'})
        C = self.fake_gerrit.addFakeChange('org/project',
                                           'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 1)
        self.assertEqual(C.reported, 1)

        self.executor_api.release('project-merge')
        self.waitUntilSettled()
        self.executor_api.release('project-merge')
        self.waitUntilSettled()
        self.executor_api.release('project-merge')
        self.waitUntilSettled()

        self.hold_jobs_in_queue = False
        self.executor_api.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertIn('Merge Failed', B.messages[-1])
        self.assertEqual(C.reported, 2)

        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
            dict(name='project-merge', result='SUCCESS', changes='1,1 3,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1 3,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1 3,1'),
        ], ordered=False)

    def test_delayed_merge_conflict(self):
        "Test that delayed check merge conflicts are handled properly"

        # Hold jobs in the ZooKeeper queue so that we can test whether
        # the executor sucesfully merges a change based on an old
        # repo state (frozen by the scheduler) which would otherwise
        # conflict.
        self.hold_jobs_in_queue = True
        A = self.fake_gerrit.addFakeChange('org/project',
                                           'master', 'A',
                                           files={'conflict': 'foo'})
        B = self.fake_gerrit.addFakeChange('org/project',
                                           'master', 'B',
                                           files={'conflict': 'bar'})
        C = self.fake_gerrit.addFakeChange('org/project',
                                           'master', 'C')
        C.setDependsOn(B, 1)

        # A enters the gate queue; B and C enter the check queue
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 1)
        self.assertEqual(B.reported, 0)  # Check does not report start
        self.assertEqual(C.reported, 0)  # Check does not report start

        # A merges while B and C are queued in check
        # Release A project-merge
        queue = list(self.executor_api.queued())
        self.executor_api.release(queue[0])
        self.waitUntilSettled()

        # Release A project-test*
        # gate has higher precedence, so A's test jobs are added in
        # front of the merge jobs for B and C
        queue = list(self.executor_api.queued())
        self.executor_api.release(queue[0])
        self.executor_api.release(queue[1])
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(C.data['status'], 'NEW')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 0)
        self.assertEqual(C.reported, 0)
        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
        ], ordered=False)

        # B and C report merge conflicts
        # Release B project-merge
        queue = list(self.executor_api.queued())
        self.executor_api.release(queue[0])
        self.waitUntilSettled()

        # Release C
        self.hold_jobs_in_queue = False
        self.executor_api.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(C.data['status'], 'NEW')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 1)
        self.assertEqual(C.reported, 1)

        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
            dict(name='project-merge', result='SUCCESS', changes='2,1'),
            dict(name='project-test1', result='SUCCESS', changes='2,1'),
            dict(name='project-test2', result='SUCCESS', changes='2,1'),
            dict(name='project-merge', result='SUCCESS', changes='2,1 3,1'),
            dict(name='project-test1', result='SUCCESS', changes='2,1 3,1'),
            dict(name='project-test2', result='SUCCESS', changes='2,1 3,1'),
        ], ordered=False)

    def test_post(self):
        "Test that post jobs run"
        p = "review.example.com/org/project"
        upstream = self.getUpstreamRepos([p])
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.setMerged()
        A_commit = str(upstream[p].commit('master'))
        self.log.debug("A commit: %s" % A_commit)

        e = {
            "type": "ref-updated",
            "submitter": {
                "name": "User Name",
            },
            "refUpdate": {
                "oldRev": "90f173846e3af9154517b88543ffbd1691f31366",
                "newRev": A_commit,
                "refName": "master",
                "project": "org/project",
            }
        }
        self.fake_gerrit.addEvent(e)
        self.waitUntilSettled()

        job_names = [x.name for x in self.history]
        self.assertEqual(len(self.history), 1)
        self.assertIn('project-post', job_names)

    def test_post_ignore_deletes(self):
        "Test that deleting refs does not trigger post jobs"

        e = {
            "type": "ref-updated",
            "submitter": {
                "name": "User Name",
            },
            "refUpdate": {
                "oldRev": "90f173846e3af9154517b88543ffbd1691f31366",
                "newRev": "0000000000000000000000000000000000000000",
                "refName": "master",
                "project": "org/project",
            }
        }
        self.fake_gerrit.addEvent(e)
        self.waitUntilSettled()

        job_names = [x.name for x in self.history]
        self.assertEqual(len(self.history), 0)
        self.assertNotIn('project-post', job_names)

    @simple_layout('layouts/dont-ignore-ref-deletes.yaml')
    def test_post_ignore_deletes_negative(self):
        "Test that deleting refs does trigger post jobs"
        e = {
            "type": "ref-updated",
            "submitter": {
                "name": "User Name",
            },
            "refUpdate": {
                "oldRev": "90f173846e3af9154517b88543ffbd1691f31366",
                "newRev": "0000000000000000000000000000000000000000",
                "refName": "testbranch",
                "project": "org/project",
            }
        }
        self.fake_gerrit.addEvent(e)
        self.waitUntilSettled()

        job_names = [x.name for x in self.history]
        self.assertEqual(len(self.history), 1)
        self.assertIn('project-post', job_names)

    @skip("Disabled for early v3 development")
    def test_build_configuration_branch_interaction(self):
        "Test that switching between branches works"
        self.test_build_configuration()
        self.test_build_configuration_branch()
        # C has been merged, undo that
        path = os.path.join(self.upstream_root, "org/project")
        repo = git.Repo(path)
        repo.heads.master.commit = repo.commit('init')
        self.test_build_configuration()

    def test_dependent_changes_rebase(self):
        # Test that no errors occur when we walk a dependency tree
        # with an unused leaf node due to a rebase.
        # Start by constructing: C -> B -> A
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        B.setDependsOn(A, 1)

        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        C.setDependsOn(B, 1)

        # Then rebase to form: D -> C -> A
        C.addPatchset()  # C,2
        C.setDependsOn(A, 1)

        D = self.fake_gerrit.addFakeChange('org/project', 'master', 'D')
        D.setDependsOn(C, 2)

        # Walk the entire tree
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertEqual(len(self.history), 3)

        # Verify that walking just part of the tree still works
        self.fake_gerrit.addEvent(D.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertEqual(len(self.history), 6)

    def test_dependent_changes_dequeue(self):
        "Test that dependent patches are not needlessly tested"

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        M1 = self.fake_gerrit.addFakeChange('org/project', 'master', 'M1')
        M1.setMerged()

        # C -> B -> A -> M1

        C.setDependsOn(B, 1)
        B.setDependsOn(A, 1)
        A.setDependsOn(M1, 1)

        self.executor_server.failJob('project-merge', A)

        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))

        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.data['status'], 'NEW')
        self.assertIn('This change depends on a change that failed to merge.',
                      C.messages[-1])
        self.assertEqual(len(self.history), 1)

    def test_failing_dependent_changes(self):
        "Test that failing dependent patches are taken out of stream"
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        D = self.fake_gerrit.addFakeChange('org/project', 'master', 'D')
        E = self.fake_gerrit.addFakeChange('org/project', 'master', 'E')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        D.addApproval('Code-Review', 2)
        E.addApproval('Code-Review', 2)

        # E, D -> C -> B, A

        D.setDependsOn(C, 1)
        C.setDependsOn(B, 1)

        self.executor_server.failJob('project-test1', B)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(D.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(E.addApproval('Approved', 1))

        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        for build in self.builds:
            if build.parameters['zuul']['change'] != '1':
                build.release()
                self.waitUntilSettled()

        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertIn('Build succeeded', A.messages[1])
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(B.reported, 2)
        self.assertIn('Build failed', B.messages[1])
        self.assertEqual(C.data['status'], 'NEW')
        self.assertEqual(C.reported, 2)
        self.assertIn('depends on a change', C.messages[1])
        self.assertEqual(D.data['status'], 'NEW')
        self.assertEqual(D.reported, 2)
        self.assertIn('depends on a change', D.messages[1])
        self.assertEqual(E.data['status'], 'MERGED')
        self.assertEqual(E.reported, 2)
        self.assertIn('Build succeeded', E.messages[1])
        self.assertEqual(len(self.history), 18)

    def test_head_is_dequeued_once(self):
        "Test that if a change at the head fails it is dequeued only once"
        # If it's dequeued more than once, we should see extra
        # aborted jobs.

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        self.executor_server.failJob('project-test1', A)
        self.executor_server.failJob('project-test2', A)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))

        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 1)
        self.assertEqual(self.builds[0].name, 'project-merge')
        self.assertTrue(self.builds[0].hasChanges(A))

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

        self.release(self.builds[0])
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 2)  # test2, merge for B
        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 4)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)
        self.assertEqual(len(self.history), 15)

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)

    @simple_layout('layouts/nonvoting-job-approval.yaml')
    def test_nonvoting_job_approval(self):
        "Test that non-voting jobs don't vote but leave approval"

        A = self.fake_gerrit.addFakeChange('org/nonvoting-project',
                                           'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.executor_server.failJob('nonvoting-project-test2', A)

        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(A.reported, 1)

        self.assertEqual(
            self.getJobFromHistory('nonvoting-project-test1').result,
            'SUCCESS')
        self.assertEqual(
            self.getJobFromHistory('nonvoting-project-test2').result,
            'FAILURE')

        self.assertFalse(self.getJobFromHistory('nonvoting-project-test1').
                         parameters['zuul']['voting'])
        self.assertFalse(self.getJobFromHistory('nonvoting-project-test2').
                         parameters['zuul']['voting'])
        self.assertEqual(A.patchsets[0]['approvals'][0]['value'], "1")

    @simple_layout('layouts/nonvoting-job.yaml')
    def test_nonvoting_job(self):
        "Test that non-voting jobs don't vote."

        A = self.fake_gerrit.addFakeChange('org/nonvoting-project',
                                           'master', 'A')
        A.addApproval('Code-Review', 2)
        self.executor_server.failJob('nonvoting-project-test2', A)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))

        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(
            self.getJobFromHistory('nonvoting-project-merge').result,
            'SUCCESS')
        self.assertEqual(
            self.getJobFromHistory('nonvoting-project-test1').result,
            'SUCCESS')
        self.assertEqual(
            self.getJobFromHistory('nonvoting-project-test2').result,
            'FAILURE')

        self.assertTrue(self.getJobFromHistory('nonvoting-project-merge').
                        parameters['zuul']['voting'])
        self.assertTrue(self.getJobFromHistory('nonvoting-project-test1').
                        parameters['zuul']['voting'])
        self.assertFalse(self.getJobFromHistory('nonvoting-project-test2').
                         parameters['zuul']['voting'])

    def test_check_queue_success(self):
        "Test successful check queue jobs."

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(A.reported, 1)
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')

    def test_check_queue_failure(self):
        "Test failed check queue jobs."

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.executor_server.failJob('project-test2', A)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(A.reported, 1)
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'FAILURE')

    @simple_layout('layouts/autohold.yaml')
    def test_autohold(self):
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1)
        self.assertTrue(r)

        # There should be a record in ZooKeeper
        request_list = self.sched_zk_nodepool.getHoldRequests()
        self.assertEqual(1, len(request_list))
        request = self.sched_zk_nodepool.getHoldRequest(
            request_list[0])
        self.assertIsNotNone(request)
        self.assertEqual('tenant-one', request.tenant)
        self.assertEqual('review.example.com/org/project', request.project)
        self.assertEqual('project-test2', request.job)
        self.assertEqual('reason text', request.reason)
        self.assertEqual(1, request.max_count)
        self.assertEqual(0, request.current_count)
        self.assertEqual([], request.nodes)

        # Some convenience variables for checking the stats.
        tenant_ram_stat = 'zuul.nodepool.resources.tenant.tenant-one.ram'
        project_ram_stat = ('zuul.nodepool.resources.project.'
                            'review_example_com/org/project.ram')
        # Test that we zeroed the gauges
        self.scheds.first.sched._runStats()
        self.assertUnReportedStat(tenant_ram_stat, value='1024', kind='g')
        self.assertUnReportedStat(project_ram_stat, value='1024', kind='g')
        self.assertReportedStat(tenant_ram_stat, value='0', kind='g')
        self.assertReportedStat(project_ram_stat, value='0', kind='g')

        # First check that successful jobs do not autohold
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(A.reported, 1)
        # project-test2
        self.assertEqual(self.history[0].result, 'SUCCESS')

        # Check nodepool for a held node
        held_node = None
        for node in self.fake_nodepool.getNodes():
            if node['state'] == zuul.model.STATE_HOLD:
                held_node = node
                break
        self.assertIsNone(held_node)

        # Hold in build to check the stats
        self.executor_server.hold_jobs_in_build = True

        # Now test that failed jobs are autoheld

        # Set resources only for this node so we can examine the code
        # path for updating the stats on autohold.
        self.fake_nodepool.resources = {
            'cores': 2,
            'ram': 1024,
            'instances': 1,
        }

        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        self.executor_server.failJob('project-test2', B)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        # Get the build request object
        build = list(self.getCurrentBuilds())[0]

        # We should report using the held node's resources
        self.waitUntilNodeCacheSync(
            self.scheds.first.sched.nodepool.zk_nodepool)
        self.statsd.clear()
        self.scheds.first.sched._runStats()
        self.assertReportedStat(tenant_ram_stat, value='1024', kind='g')
        self.assertReportedStat(project_ram_stat, value='1024', kind='g')
        self.assertUnReportedStat(tenant_ram_stat, value='0', kind='g')
        self.assertUnReportedStat(project_ram_stat, value='0', kind='g')

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(B.reported, 1)
        # project-test2
        self.assertEqual(self.history[1].result, 'FAILURE')
        self.assertTrue(build.held)

        # Check nodepool for a held node
        held_node = None
        for node in self.fake_nodepool.getNodes():
            if node['state'] == zuul.model.STATE_HOLD:
                held_node = node
                break
        self.assertIsNotNone(held_node)
        # Validate node has recorded the failed job
        self.assertEqual(
            held_node['hold_job'],
            " ".join(['tenant-one',
                      'review.example.com/org/project',
                      'project-test2', '.*'])
        )
        self.assertEqual(held_node['comment'], "reason text")

        # The hold request current_count should have incremented
        # and we should have recorded the held node ID.
        request2 = self.sched_zk_nodepool.getHoldRequest(
            request.id)
        self.assertEqual(request.current_count + 1, request2.current_count)
        self.assertEqual(1, len(request2.nodes))
        self.assertEqual(1, len(request2.nodes[0]["nodes"]))

        # We should still report we use the resources
        self.waitUntilNodeCacheSync(
            self.scheds.first.sched.nodepool.zk_nodepool)
        self.statsd.clear()
        self.scheds.first.sched._runStats()
        self.assertReportedStat(tenant_ram_stat, value='1024', kind='g')
        self.assertReportedStat(project_ram_stat, value='1024', kind='g')
        self.assertUnReportedStat(tenant_ram_stat, value='0', kind='g')
        self.assertUnReportedStat(project_ram_stat, value='0', kind='g')

        # Another failed change should not hold any more nodes
        self.fake_nodepool.resources = {}
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        self.executor_server.failJob('project-test2', C)
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertEqual(C.data['status'], 'NEW')
        self.assertEqual(C.reported, 1)
        # project-test2
        self.assertEqual(self.history[2].result, 'FAILURE')

        held_nodes = 0
        for node in self.fake_nodepool.getNodes():
            if node['state'] == zuul.model.STATE_HOLD:
                held_nodes += 1
        self.assertEqual(held_nodes, 1)

        # request current_count should not have changed
        request3 = self.sched_zk_nodepool.getHoldRequest(
            request2.id)
        self.assertEqual(request2.current_count, request3.current_count)

        # Deleting hold request should set held nodes to used
        self.sched_zk_nodepool.deleteHoldRequest(request3)
        node_states = [n['state'] for n in self.fake_nodepool.getNodes()]
        self.assertEqual(3, len(node_states))
        self.assertEqual([zuul.model.STATE_USED] * 3, node_states)

        # Nodepool deletes the nodes
        for n in self.fake_nodepool.getNodes():
            self.fake_nodepool.removeNode(n)

        # We should now report that we no longer use the nodes resources
        self.waitUntilNodeCacheSync(
            self.scheds.first.sched.nodepool.zk_nodepool)
        self.statsd.clear()
        self.scheds.first.sched._runStats()
        self.assertUnReportedStat(tenant_ram_stat, value='1024', kind='g')
        self.assertUnReportedStat(project_ram_stat, value='1024', kind='g')
        self.assertReportedStat(tenant_ram_stat, value='0', kind='g')
        self.assertReportedStat(project_ram_stat, value='0', kind='g')

    @simple_layout('layouts/autohold.yaml')
    def test_autohold_info(self):
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        # Empty dict should be returned for "not found"
        request = client.autohold_info("XxXxX")
        self.assertEqual({}, request)

        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1)
        self.assertTrue(r)

        # There should be a record in ZooKeeper
        request_list = self.sched_zk_nodepool.getHoldRequests()
        self.assertEqual(1, len(request_list))
        request = self.sched_zk_nodepool.getHoldRequest(
            request_list[0])
        self.assertIsNotNone(request)

        request = client.autohold_info(request.id)
        self.assertNotEqual({}, request)
        self.assertEqual('tenant-one', request['tenant'])
        self.assertEqual('review.example.com/org/project', request['project'])
        self.assertEqual('project-test2', request['job'])
        self.assertEqual('reason text', request['reason'])
        self.assertEqual(1, request['max_count'])
        self.assertEqual(0, request['current_count'])

    @simple_layout('layouts/autohold.yaml')
    def test_autohold_delete(self):
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1)
        self.assertTrue(r)

        # There should be a record in ZooKeeper
        request_list = self.sched_zk_nodepool.getHoldRequests()
        self.assertEqual(1, len(request_list))
        request = self.sched_zk_nodepool.getHoldRequest(
            request_list[0])
        self.assertIsNotNone(request)

        # Delete and verify no more requests
        self.assertTrue(client.autohold_delete(request.id))
        request_list = self.sched_zk_nodepool.getHoldRequests()
        self.assertEqual([], request_list)

    def test_autohold_padding(self):
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1)
        self.assertTrue(r)

        # There should be a record in ZooKeeper
        request_list = self.sched_zk_nodepool.getHoldRequests()
        self.assertEqual(1, len(request_list))
        request = self.sched_zk_nodepool.getHoldRequest(
            request_list[0])
        self.assertIsNotNone(request)

        # Assert the ID leads with a bunch of zeros, them strip them
        # off to test autohold_delete can handle a user passing in an
        # ID without leading zeros.
        self.assertEqual(request.id[0:5], '00000')
        trimmed_request = request.id[5:]
        # Delete and verify no more requests
        self.assertTrue(client.autohold_delete(trimmed_request))
        request_list = self.sched_zk_nodepool.getHoldRequests()
        self.assertEqual([], request_list)

    def _test_autohold_scoped(self, change_obj, change, ref):
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        # create two changes on the same project, and autohold request
        # for one of them.
        other = self.fake_gerrit.addFakeChange(
            'org/project', 'master', 'other'
        )

        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            str(change), ref, "reason text", 1)
        self.assertTrue(r)

        # First, check that an unrelated job does not trigger autohold, even
        # when it failed
        self.executor_server.failJob('project-test2', other)
        self.fake_gerrit.addEvent(other.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertEqual(other.data['status'], 'NEW')
        self.assertEqual(other.reported, 1)
        # project-test2
        self.assertEqual(self.history[0].result, 'FAILURE')

        # Check nodepool for a held node
        held_node = None
        for node in self.fake_nodepool.getNodes():
            if node['state'] == zuul.model.STATE_HOLD:
                held_node = node
                break
        self.assertIsNone(held_node)

        # And then verify that failed job for the defined change
        # triggers the autohold

        self.executor_server.failJob('project-test2', change_obj)
        self.fake_gerrit.addEvent(change_obj.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertEqual(change_obj.data['status'], 'NEW')
        self.assertEqual(change_obj.reported, 1)
        # project-test2
        self.assertEqual(self.history[1].result, 'FAILURE')

        # Check nodepool for a held node
        held_node = None
        for node in self.fake_nodepool.getNodes():
            if node['state'] == zuul.model.STATE_HOLD:
                held_node = node
                break
        self.assertIsNotNone(held_node)

        # Validate node has recorded the failed job
        if change != "":
            ref = "refs/changes/%s/%s/.*" % (
                str(change_obj.number).zfill(2)[-2:], str(change_obj.number)
            )

        self.assertEqual(
            held_node['hold_job'],
            " ".join(['tenant-one',
                      'review.example.com/org/project',
                      'project-test2', ref])
        )
        self.assertEqual(held_node['comment'], "reason text")

    @simple_layout('layouts/autohold.yaml')
    def test_autohold_change(self):
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')

        self._test_autohold_scoped(A, change=A.number, ref="")

    @simple_layout('layouts/autohold.yaml')
    def test_autohold_ref(self):
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        ref = A.data['currentPatchSet']['ref']
        self._test_autohold_scoped(A, change="", ref=ref)

    @simple_layout('layouts/autohold.yaml')
    def test_autohold_scoping(self):
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')

        # create three autohold requests, scoped to job, change and
        # a specific ref
        change = str(A.number)
        ref = A.data['currentPatchSet']['ref']
        r1 = client.autohold('tenant-one', 'org/project', 'project-test2',
                             "", "", "reason text", 1)
        self.assertTrue(r1)
        r2 = client.autohold('tenant-one', 'org/project', 'project-test2',
                             change, "", "reason text", 1)
        self.assertTrue(r2)
        r3 = client.autohold('tenant-one', 'org/project', 'project-test2',
                             "", ref, "reason text", 1)
        self.assertTrue(r3)

        # Fail 3 jobs for the same change, and verify that the autohold
        # requests are fullfilled in the expected order: from the most
        # specific towards the most generic one.

        def _fail_job_and_verify_autohold_request(change_obj, ref_filter):
            self.executor_server.failJob('project-test2', change_obj)
            self.fake_gerrit.addEvent(change_obj.getPatchsetCreatedEvent(1))

            self.waitUntilSettled()

            # Check nodepool for a held node
            held_node = None
            for node in self.fake_nodepool.getNodes():
                if node['state'] == zuul.model.STATE_HOLD:
                    held_node = node
                    break
            self.assertIsNotNone(held_node)

            self.assertEqual(
                held_node['hold_job'],
                " ".join(['tenant-one',
                          'review.example.com/org/project',
                          'project-test2', ref_filter])
            )
            self.assertFalse(held_node['_lock'], "Node %s is locked" %
                             (node['_oid'],))
            self.fake_nodepool.removeNode(held_node)

        _fail_job_and_verify_autohold_request(A, ref)

        ref = "refs/changes/%s/%s/.*" % (str(change).zfill(2)[-2:],
                                         str(change))
        _fail_job_and_verify_autohold_request(A, ref)
        _fail_job_and_verify_autohold_request(A, ".*")

    @simple_layout('layouts/autohold.yaml')
    def test_autohold_ignores_aborted_jobs(self):
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1)
        self.assertTrue(r)

        self.executor_server.hold_jobs_in_build = True

        # Create a change that will have its job aborted
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # Creating new patchset on change A will abort A,1's job because
        # a new patchset arrived replacing A,1 with A,2.
        A.addPatchset()
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(2))

        self.waitUntilSettled()
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        # Note only the successful job for A,2 will report as we don't
        # report aborted builds for old patchsets.
        self.assertEqual(A.reported, 1)
        # A,1 project-test2
        self.assertEqual(self.history[0].result, 'ABORTED')
        # A,2 project-test2
        self.assertEqual(self.history[1].result, 'SUCCESS')

        # Check nodepool for a held node
        held_node = None
        for node in self.fake_nodepool.getNodes():
            if node['state'] == zuul.model.STATE_HOLD:
                held_node = node
                break
        self.assertIsNone(held_node)

    @simple_layout('layouts/autohold.yaml')
    def test_autohold_hold_expiration(self):
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1, node_hold_expiration=30)
        self.assertTrue(r)

        # Hold a failed job
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        self.executor_server.failJob('project-test2', B)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(B.reported, 1)
        # project-test2
        self.assertEqual(self.history[0].result, 'FAILURE')

        # Check nodepool for a held node
        held_node = None
        for node in self.fake_nodepool.getNodes():
            if node['state'] == zuul.model.STATE_HOLD:
                held_node = node
                break
        self.assertIsNotNone(held_node)

        # Validate node has hold_expiration property
        self.assertEqual(int(held_node['hold_expiration']), 30)

    @simple_layout('layouts/autohold.yaml')
    def test_autohold_list(self):
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1)
        self.assertTrue(r)

        autohold_requests = client.autohold_list()
        self.assertNotEqual([], autohold_requests)
        self.assertEqual(1, len(autohold_requests))

        request = autohold_requests[0]
        self.assertEqual('tenant-one', request['tenant'])
        self.assertIn('org/project', request['project'])
        self.assertEqual('project-test2', request['job'])
        self.assertEqual(".*", request['ref_filter'])
        self.assertEqual("reason text", request['reason'])

    @simple_layout('layouts/autohold.yaml')
    def test_autohold_request_expiration(self):
        orig_exp = RecordingExecutorServer.EXPIRED_HOLD_REQUEST_TTL

        def reset_exp():
            self.executor_server.EXPIRED_HOLD_REQUEST_TTL = orig_exp

        self.addCleanup(reset_exp)

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        # Temporarily shorten the hold request expiration time
        r = client.autohold('tenant-one', 'org/project', 'project-test2',
                            "", "", "reason text", 1, 1)
        self.assertTrue(r)

        autohold_requests = client.autohold_list()
        self.assertEqual(1, len(autohold_requests))
        req = autohold_requests[0]
        self.assertIsNone(req['expired'])

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.executor_server.failJob('project-test2', A)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        autohold_requests = client.autohold_list()
        self.assertEqual(1, len(autohold_requests))
        req = autohold_requests[0]
        self.assertIsNotNone(req['expired'])

        # Temporarily shorten hold time so that the hold request can be
        # auto-deleted (which is done on another test failure). And wait
        # long enough for nodes to expire and request to delete.
        self.executor_server.EXPIRED_HOLD_REQUEST_TTL = 1
        time.sleep(3)

        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        self.executor_server.failJob('project-test2', B)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        for _ in iterate_timeout(10, 'hold request expiration'):
            if len(client.autohold_list()) == 0:
                break

    @simple_layout('layouts/three-projects.yaml')
    def test_dependent_behind_dequeue(self):
        # This particular test does a large amount of merges and needs a little
        # more time to complete
        self.wait_timeout = 120
        "test that dependent changes behind dequeued changes work"
        # This complicated test is a reproduction of a real life bug
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project2', 'master', 'C')
        D = self.fake_gerrit.addFakeChange('org/project2', 'master', 'D')
        E = self.fake_gerrit.addFakeChange('org/project2', 'master', 'E')
        F = self.fake_gerrit.addFakeChange('org/project3', 'master', 'F')
        D.setDependsOn(C, 1)
        E.setDependsOn(D, 1)
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        D.addApproval('Code-Review', 2)
        E.addApproval('Code-Review', 2)
        F.addApproval('Code-Review', 2)

        A.fail_merge = True

        # Change object re-use in the gerrit trigger is hidden if
        # changes are added in quick succession; waiting makes it more
        # like real life.
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(D.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(E.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(F.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        # all jobs running

        # Grab pointers to the jobs we want to release before
        # releasing any, because list indexes may change as
        # the jobs complete.
        a, b, c = self.builds[:3]
        a.release()
        b.release()
        c.release()
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(D.data['status'], 'MERGED')
        self.assertEqual(E.data['status'], 'MERGED')
        self.assertEqual(F.data['status'], 'MERGED')

        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)
        self.assertEqual(D.reported, 2)
        self.assertEqual(E.reported, 2)
        self.assertEqual(F.reported, 2)

        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 15)
        self.assertEqual(len(self.history), 44)

    def test_merger_repack(self):
        "Test that the merger works after a repack"

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEmptyQueues()
        self.build_history = []

        path = os.path.join(self.merger_src_root, "review.example.com",
                            "org/project")
        if os.path.exists(path):
            repack_repo(path)
        path = os.path.join(self.executor_src_root, "review.example.com",
                            "org/project")
        if os.path.exists(path):
            repack_repo(path)

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)

    def test_merger_repack_large_change(self):
        "Test that the merger works with large changes after a repack"
        # https://bugs.executepad.net/zuul/+bug/1078946
        # This test assumes the repo is already cloned; make sure it is
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        trusted, project = tenant.getProject('org/project')
        url = self.fake_gerrit.getGitUrl(project)
        self.executor_server.merger._addProject(
            'review.example.com', 'gerrit', 'org/project', url, None, None,
            None)
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addPatchset(large=True)
        # TODOv3(jeblair): add hostname to upstream root
        path = os.path.join(self.upstream_root, 'org/project')
        repack_repo(path)
        path = os.path.join(self.merger_src_root, 'review.example.com',
                            'org/project')
        if os.path.exists(path):
            repack_repo(path)
        path = os.path.join(self.executor_src_root, 'review.example.com',
                            'org/project')
        if os.path.exists(path):
            repack_repo(path)

        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)

    def test_new_patchset_dequeues_old(self):
        "Test that a new patchset causes the old to be dequeued"
        # D -> C (depends on B) -> B (depends on A) -> A -> M
        self.executor_server.hold_jobs_in_build = True
        M = self.fake_gerrit.addFakeChange('org/project', 'master', 'M')
        M.setMerged()

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        D = self.fake_gerrit.addFakeChange('org/project', 'master', 'D')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        D.addApproval('Code-Review', 2)

        C.setDependsOn(B, 1)
        B.setDependsOn(A, 1)
        A.setDependsOn(M, 1)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(D.addApproval('Approved', 1))
        self.waitUntilSettled()

        B.addPatchset()
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(2))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.data['status'], 'NEW')
        self.assertEqual(C.reported, 2)
        self.assertEqual(D.data['status'], 'MERGED')
        self.assertEqual(D.reported, 2)
        self.assertEqual(len(self.history), 9)  # 3 each for A, B, D.

    @simple_layout('layouts/no-dequeue-on-new-patchset.yaml')
    def test_no_dequeue_on_new_patchset(self):
        "Test the dequeue-on-new-patchset false value"
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        self.executor_server.hold_jobs_in_build = True
        A.addApproval('Code-Review', 2)

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 1)

        A.addPatchset()
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(2))
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 2)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='project1-test', result='SUCCESS', changes='1,1'),
            dict(name='project1-test', result='SUCCESS', changes='1,2'),
        ], ordered=False)

    @simple_layout('layouts/no-dequeue-on-new-patchset.yaml')
    def test_no_dequeue_on_new_patchset_deps(self):
        "Test dependencies are updated if dequeue-on-new-patchset is false"
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        B.data['commitMessage'] = '%s\n\nDepends-On: %s\n' % (
            B.subject, A.data['url'])
        B.addApproval('Code-Review', 2)

        self.executor_server.hold_jobs_in_build = True

        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 1)

        A.addPatchset()
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(2))
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        # The item should be dequeued because of the dependency change
        self.assertHistory([
            dict(name='project1-test', result='ABORTED', changes='1,1 2,1'),
        ], ordered=False)

    def test_new_patchset_check(self):
        "Test a new patchset in check"

        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        check_pipeline = tenant.layout.pipelines['check']

        # Add two git-dependent changes
        B.setDependsOn(A, 1)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # A live item, and a non-live/live pair
        items = check_pipeline.getAllItems()
        self.assertEqual(len(items), 3)

        self.assertEqual(items[0].change.number, '1')
        self.assertEqual(items[0].change.patchset, '1')
        self.assertFalse(items[0].live)

        self.assertEqual(items[1].change.number, '2')
        self.assertEqual(items[1].change.patchset, '1')
        self.assertTrue(items[1].live)

        self.assertEqual(items[2].change.number, '1')
        self.assertEqual(items[2].change.patchset, '1')
        self.assertTrue(items[2].live)

        # Add a new patchset to A
        A.addPatchset()
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(2))
        self.waitUntilSettled()

        # The live copy of A,1 should be gone, but the non-live and B
        # should continue, and we should have a new A,2
        items = check_pipeline.getAllItems()
        self.assertEqual(len(items), 3)

        self.assertEqual(items[0].change.number, '1')
        self.assertEqual(items[0].change.patchset, '1')
        self.assertFalse(items[0].live)

        self.assertEqual(items[1].change.number, '2')
        self.assertEqual(items[1].change.patchset, '1')
        self.assertTrue(items[1].live)

        self.assertEqual(items[2].change.number, '1')
        self.assertEqual(items[2].change.patchset, '2')
        self.assertTrue(items[2].live)

        # Add a new patchset to B
        B.addPatchset()
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(2))
        self.waitUntilSettled()

        # The live copy of B,1 should be gone, and it's non-live copy of A,1
        # but we should have a new B,2 (still based on A,1)
        items = check_pipeline.getAllItems()
        self.assertEqual(len(items), 3)

        self.assertEqual(items[0].change.number, '1')
        self.assertEqual(items[0].change.patchset, '2')
        self.assertTrue(items[0].live)

        self.assertEqual(items[1].change.number, '1')
        self.assertEqual(items[1].change.patchset, '1')
        self.assertFalse(items[1].live)

        self.assertEqual(items[2].change.number, '2')
        self.assertEqual(items[2].change.patchset, '2')
        self.assertTrue(items[2].live)

        self.builds[0].release()
        self.waitUntilSettled()
        self.builds[0].release()
        self.waitUntilSettled()
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.reported, 1)
        self.assertEqual(B.reported, 1)
        self.assertEqual(self.history[0].result, 'ABORTED')
        self.assertEqual(self.history[0].changes, '1,1')
        self.assertEqual(self.history[1].result, 'ABORTED')
        self.assertEqual(self.history[1].changes, '1,1 2,1')
        self.assertEqual(self.history[2].result, 'SUCCESS')
        self.assertEqual(self.history[2].changes, '1,2')
        self.assertEqual(self.history[3].result, 'SUCCESS')
        self.assertEqual(self.history[3].changes, '1,1 2,2')

    def test_abandoned_gate(self):
        "Test that an abandoned change is dequeued from gate"

        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 1, "One job being built (on hold)")
        self.assertEqual(self.builds[0].name, 'project-merge')

        self.fake_gerrit.addEvent(A.getChangeAbandonedEvent())
        self.waitUntilSettled()

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        self.assertBuilds([])
        self.assertHistory([
            dict(name='project-merge', result='ABORTED', changes='1,1')],
            ordered=False)
        self.assertEqual(A.reported, 1,
                         "Abandoned gate change should report only start")

    def test_abandoned_check(self):
        "Test that an abandoned change is dequeued from check"

        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        check_pipeline = tenant.layout.pipelines['check']

        # Add two git-dependent changes
        B.setDependsOn(A, 1)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        # A live item, and a non-live/live pair
        items = check_pipeline.getAllItems()
        self.assertEqual(len(items), 3)

        self.assertEqual(items[0].change.number, '1')
        self.assertFalse(items[0].live)

        self.assertEqual(items[1].change.number, '2')
        self.assertTrue(items[1].live)

        self.assertEqual(items[2].change.number, '1')
        self.assertTrue(items[2].live)

        # Abandon A
        self.fake_gerrit.addEvent(A.getChangeAbandonedEvent())
        self.waitUntilSettled()

        # The live copy of A should be gone, but the non-live and B
        # should continue
        items = check_pipeline.getAllItems()
        self.assertEqual(len(items), 2)

        self.assertEqual(items[0].change.number, '1')
        self.assertFalse(items[0].live)

        self.assertEqual(items[1].change.number, '2')
        self.assertTrue(items[1].live)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.history), 4)
        self.assertEqual(self.history[0].result, 'ABORTED',
                         'Build should have been aborted')
        self.assertEqual(A.reported, 0, "Abandoned change should not report")
        self.assertEqual(B.reported, 1, "Change should report")

    def test_cancel_starting_build(self):
        "Test that a canceled build that is not processed yet is removed"

        self.executor_server.hold_jobs_in_start = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        for _ in iterate_timeout(30, 'Wait for build to be in starting phase'):
            if self.executor_server.job_workers:
                break

        tevent = threading.Event()

        def data_watch(event):
            # Set the threading event as soon as the cancel node is present
            tevent.set()

        builds = list(self.executor_api.all())
        # When using DataWatch it is possible for the cancel znode to be
        # created, then deleted almost immediately before the watch handling
        # happens. When this happens kazoo sees no stat info and treats the
        # event as a noop because no new version is available. Use exists to
        # avoid this problem.
        self.zk_client.client.exists(f"{builds[0].path}/cancel", data_watch)

        # Abandon change to cancel build
        self.fake_gerrit.addEvent(A.getChangeAbandonedEvent())

        self.assertTrue(tevent.wait(timeout=30))

        self.executor_server.hold_jobs_in_start = False
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='project-merge', result='ABORTED')
        ])

    def test_abandoned_not_timer(self):
        "Test that an abandoned change does not cancel timer jobs"
        # This test can not use simple_layout because it must start
        # with a configuration which does not include a
        # timer-triggered job so that we have an opportunity to set
        # the hold flag before the first job.
        self.executor_server.hold_jobs_in_build = True
        # Start timer trigger - also org/project
        self.commitConfigUpdate('common-config', 'layouts/idle.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        # The pipeline triggers every second, so we should have seen
        # several by now.
        time.sleep(5)
        self.waitUntilSettled()
        # Stop queuing timer triggered jobs so that the assertions
        # below don't race against more jobs being queued.
        # Must be in same repo, so overwrite config with another one
        self.commitConfigUpdate('common-config', 'layouts/no-timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        # If APScheduler is in mid-event when we remove the job, we
        # can end up with one more event firing, so give it an extra
        # second to settle.
        time.sleep(1)
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 1, "One timer job")

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 2, "One change plus one timer job")

        self.fake_gerrit.addEvent(A.getChangeAbandonedEvent())
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 1, "One timer job remains")

        self.executor_server.release()
        self.waitUntilSettled()

    def test_new_patchset_dequeues_old_on_head(self):
        "Test that a new patchset causes the old to be dequeued (at head)"
        # D -> C (depends on B) -> B (depends on A) -> A -> M
        self.executor_server.hold_jobs_in_build = True
        M = self.fake_gerrit.addFakeChange('org/project', 'master', 'M')
        M.setMerged()
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        D = self.fake_gerrit.addFakeChange('org/project', 'master', 'D')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        D.addApproval('Code-Review', 2)

        C.setDependsOn(B, 1)
        B.setDependsOn(A, 1)
        A.setDependsOn(M, 1)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(D.addApproval('Approved', 1))
        self.waitUntilSettled()

        A.addPatchset()
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(2))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.data['status'], 'NEW')
        self.assertEqual(C.reported, 2)
        self.assertEqual(D.data['status'], 'MERGED')
        self.assertEqual(D.reported, 2)
        self.assertEqual(len(self.history), 7)

    def test_new_patchset_dequeues_old_without_dependents(self):
        "Test that a new patchset causes only the old to be dequeued"
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        B.addPatchset()
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(2))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(C.reported, 2)
        self.assertEqual(len(self.history), 9)

    def test_new_patchset_dequeues_old_independent_queue(self):
        "Test that a new patchset causes the old to be dequeued (independent)"
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        B.addPatchset()
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(2))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(A.reported, 1)
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(B.reported, 1)
        self.assertEqual(C.data['status'], 'NEW')
        self.assertEqual(C.reported, 1)
        self.assertEqual(len(self.history), 10)
        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 1)

    @simple_layout('layouts/noop-job.yaml')
    def test_noop_job(self):
        "Test that the internal noop job works"
        A = self.fake_gerrit.addFakeChange('org/noop-project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        queue = list(self.executor_api.queued())
        self.assertEqual(len(queue), 0)
        self.assertTrue(self.scheds.first.sched._areAllBuildsComplete())
        self.assertEqual(len(self.history), 0)
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)

    @simple_layout('layouts/no-jobs-project.yaml')
    def test_no_job_project(self):
        "Test that reports with no jobs don't get sent"
        A = self.fake_gerrit.addFakeChange('org/no-jobs-project',
                                           'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # Change wasn't reported to
        self.assertEqual(A.reported, False)

        # Check queue is empty afterwards
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        check_pipeline = tenant.layout.pipelines['check']
        items = check_pipeline.getAllItems()
        self.assertEqual(len(items), 0)

        self.assertEqual(len(self.history), 0)

    def test_zuul_refs(self):
        "Test that zuul refs exist and have the right changes"
        self.executor_server.hold_jobs_in_build = True
        M1 = self.fake_gerrit.addFakeChange('org/project1', 'master', 'M1')
        M1.setMerged()
        M2 = self.fake_gerrit.addFakeChange('org/project2', 'master', 'M2')
        M2.setMerged()

        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project2', 'master', 'C')
        D = self.fake_gerrit.addFakeChange('org/project2', 'master', 'D')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        D.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(D.addApproval('Approved', 1))

        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        a_build = b_build = c_build = d_build = None
        for x in self.builds:
            if x.parameters['zuul']['change'] == '3':
                a_build = x
            elif x.parameters['zuul']['change'] == '4':
                b_build = x
            elif x.parameters['zuul']['change'] == '5':
                c_build = x
            elif x.parameters['zuul']['change'] == '6':
                d_build = x
            if a_build and b_build and c_build and d_build:
                break

        # should have a, not b, and should not be in project2
        self.assertTrue(a_build.hasChanges(A))
        self.assertFalse(a_build.hasChanges(B, M2))

        # should have a and b, and should not be in project2
        self.assertTrue(b_build.hasChanges(A, B))
        self.assertFalse(b_build.hasChanges(M2))

        # should have a and b in 1, c in 2
        self.assertTrue(c_build.hasChanges(A, B, C))
        self.assertFalse(c_build.hasChanges(D))

        # should have a and b in 1, c and d in 2
        self.assertTrue(d_build.hasChanges(A, B, C, D))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(C.reported, 2)
        self.assertEqual(D.data['status'], 'MERGED')
        self.assertEqual(D.reported, 2)

    def test_rerun_on_error(self):
        "Test that if a worker fails to run a job, it is run again"
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.builds[0].requeue = True
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        self.assertEqual(self.countJobResults(self.history, None), 1)
        self.assertEqual(self.countJobResults(self.history, 'SUCCESS'), 3)

    def test_statsd(self):
        "Test each of the statsd methods used in the scheduler"
        statsd = self.scheds.first.sched.statsd
        statsd.incr('test-incr')
        statsd.timing('test-timing', 3)
        statsd.gauge('test-gauge', 12)
        self.assertReportedStat('test-incr', '1', 'c')
        self.assertReportedStat('test-timing', '3', 'ms')
        self.assertReportedStat('test-gauge', '12', 'g')

        # test key normalization
        statsd.extra_keys = {'hostname': '1_2_3_4'}

        statsd.incr('hostname-incr.{hostname}.{fake}', fake='1:2')
        statsd.timing('hostname-timing.{hostname}.{fake}', 3, fake='1:2')
        statsd.gauge('hostname-gauge.{hostname}.{fake}', 12, fake='1:2')
        self.assertReportedStat('hostname-incr.1_2_3_4.1_2', '1', 'c')
        self.assertReportedStat('hostname-timing.1_2_3_4.1_2', '3', 'ms')
        self.assertReportedStat('hostname-gauge.1_2_3_4.1_2', '12', 'g')

    def test_statsd_conflict(self):
        statsd = self.scheds.first.sched.statsd
        statsd.gauge('test-gauge', 12)
        # since test-gauge is already a value, we can't make
        # subvalues.  Test the assert works.
        statsd.gauge('test-gauge.1_2_3_4', 12)
        self.assertReportedStat('test-gauge', '12', 'g')
        self.assertRaises(Exception, self.assertReportedStat,
                          'test-gauge.1_2_3_4', '12', 'g')

    def test_file_head(self):
        # This is a regression test for an observed bug.  A change
        # with a file named "HEAD" in the root directory of the repo
        # was processed by a merger.  It then was unable to reset the
        # repo because of:
        #   GitCommandError: 'git reset --hard HEAD' returned
        #       with exit code 128
        #   stderr: 'fatal: ambiguous argument 'HEAD': both revision
        #       and filename
        #   Use '--' to separate filenames from revisions'

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addPatchset({'HEAD': ''})
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(2))
        self.waitUntilSettled()

        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertIn('Build succeeded', A.messages[0])
        self.assertIn('Build succeeded', B.messages[0])

    def test_file_jobs(self):
        "Test that file jobs run only when appropriate"
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addPatchset({'pip-requires': 'foo'})
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        testfile_jobs = [x for x in self.history
                         if x.name == 'project-testfile']

        self.assertEqual(len(testfile_jobs), 1)
        self.assertEqual(testfile_jobs[0].changes, '1,2')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(B.reported, 2)

    def _test_irrelevant_files_jobs(self, should_skip):
        "Test that jobs with irrelevant-files filter run only when appropriate"
        if should_skip:
            files = {'ignoreme': 'ignored\n'}
        else:
            files = {'respectme': 'please!\n'}

        change = self.fake_gerrit.addFakeChange('org/project',
                                                'master',
                                                'test irrelevant-files',
                                                files=files)
        self.fake_gerrit.addEvent(change.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        tested_change_ids = [x.changes[0] for x in self.history
                             if x.name == 'project-test-irrelevant-files']

        if should_skip:
            self.assertEqual([], tested_change_ids)
        else:
            self.assertIn(change.data['number'], tested_change_ids)

    @simple_layout('layouts/irrelevant-files.yaml')
    def test_irrelevant_files_match_skips_job(self):
        self._test_irrelevant_files_jobs(should_skip=True)

    @simple_layout('layouts/irrelevant-files.yaml')
    def test_irrelevant_files_no_match_runs_job(self):
        self._test_irrelevant_files_jobs(should_skip=False)

    @simple_layout('layouts/inheritance.yaml')
    def test_inherited_jobs_keep_matchers(self):
        files = {'ignoreme': 'ignored\n'}

        change = self.fake_gerrit.addFakeChange('org/project',
                                                'master',
                                                'test irrelevant-files',
                                                files=files)
        self.fake_gerrit.addEvent(change.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        run_jobs = set([build.name for build in self.history])

        self.assertEqual(set(['project-test-nomatch-starts-empty',
                              'project-test-nomatch-starts-full']), run_jobs)

    @simple_layout('layouts/job-vars.yaml')
    def test_inherited_job_variables(self):
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='parentjob', result='SUCCESS'),
            dict(name='child1', result='SUCCESS'),
            dict(name='child2', result='SUCCESS'),
            dict(name='child3', result='SUCCESS'),
            dict(name='override_project_var', result='SUCCESS'),
            dict(name='job_from_template1', result='SUCCESS'),
            dict(name='job_from_template2', result='SUCCESS'),
        ], ordered=False)
        j = self.getJobFromHistory('parentjob')
        rp = set([p['name'] for p in j.parameters['projects']])
        job_vars = j.job.combined_variables
        self.assertEqual(job_vars['project_var'], 'set_in_project')
        self.assertEqual(job_vars['template_var1'], 'set_in_template1')
        self.assertEqual(job_vars['template_var2'], 'set_in_template2')
        self.assertEqual(job_vars['override'], 0)
        self.assertEqual(job_vars['child1override'], 0)
        self.assertEqual(job_vars['parent'], 0)
        self.assertEqual(job_vars['deep']['override'], 0)
        self.assertFalse('child1' in job_vars)
        self.assertFalse('child2' in job_vars)
        self.assertFalse('child3' in job_vars)
        self.assertEqual(rp, set(['org/project', 'org/project0',
                                  'org/project0']))
        j = self.getJobFromHistory('child1')
        rp = set([p['name'] for p in j.parameters['projects']])
        job_vars = j.job.combined_variables
        self.assertEqual(job_vars['project_var'], 'set_in_project')
        self.assertEqual(job_vars['override'], 1)
        self.assertEqual(job_vars['child1override'], 1)
        self.assertEqual(job_vars['parent'], 0)
        self.assertEqual(job_vars['child1'], 1)
        self.assertEqual(job_vars['deep']['override'], 1)
        self.assertFalse('child2' in job_vars)
        self.assertFalse('child3' in job_vars)
        self.assertEqual(rp, set(['org/project', 'org/project0',
                                  'org/project1']))
        j = self.getJobFromHistory('child2')
        job_vars = j.job.combined_variables
        self.assertEqual(job_vars['project_var'], 'set_in_project')
        rp = set([p['name'] for p in j.parameters['projects']])
        self.assertEqual(job_vars['override'], 2)
        self.assertEqual(job_vars['child1override'], 0)
        self.assertEqual(job_vars['parent'], 0)
        self.assertEqual(job_vars['deep']['override'], 2)
        self.assertFalse('child1' in job_vars)
        self.assertEqual(job_vars['child2'], 2)
        self.assertFalse('child3' in job_vars)
        self.assertEqual(rp, set(['org/project', 'org/project0',
                                  'org/project2']))
        j = self.getJobFromHistory('child3')
        job_vars = j.job.combined_variables
        self.assertEqual(job_vars['project_var'], 'set_in_project')
        rp = set([p['name'] for p in j.parameters['projects']])
        self.assertEqual(job_vars['override'], 3)
        self.assertEqual(job_vars['child1override'], 0)
        self.assertEqual(job_vars['parent'], 0)
        self.assertEqual(job_vars['deep']['override'], 3)
        self.assertFalse('child1' in job_vars)
        self.assertFalse('child2' in job_vars)
        self.assertEqual(job_vars['child3'], 3)
        self.assertEqual(rp, set(['org/project', 'org/project0',
                                  'org/project3']))
        j = self.getJobFromHistory('override_project_var')
        job_vars = j.job.combined_variables
        self.assertEqual(job_vars['project_var'], 'override_in_job')

    @simple_layout('layouts/job-variants.yaml')
    def test_job_branch_variants(self):
        self.create_branch('org/project', 'stable/diablo')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project', 'stable/diablo'))
        self.create_branch('org/project', 'stable/essex')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project', 'stable/essex'))
        self.waitUntilSettled()

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        B = self.fake_gerrit.addFakeChange('org/project', 'stable/diablo', 'B')
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        C = self.fake_gerrit.addFakeChange('org/project', 'stable/essex', 'C')
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='python27', result='SUCCESS'),
            dict(name='python27', result='SUCCESS'),
            dict(name='python27', result='SUCCESS'),
        ])

        j = self.history[0].job
        self.assertEqual(j.timeout, 40)
        self.assertEqual(len(j.nodeset.nodes), 1)
        self.assertEqual(next(iter(j.nodeset.nodes.values())).label, 'new')
        self.assertEqual([x['path'] for x in j.pre_run],
                         ['base-pre', 'py27-pre'])
        self.assertEqual([x['path'] for x in j.post_run],
                         ['py27-post-a', 'py27-post-b', 'base-post'])
        self.assertEqual([x['path'] for x in j.run],
                         ['playbooks/python27.yaml'])

        j = self.history[1].job
        self.assertEqual(j.timeout, 50)
        self.assertEqual(len(j.nodeset.nodes), 1)
        self.assertEqual(next(iter(j.nodeset.nodes.values())).label, 'old')
        self.assertEqual([x['path'] for x in j.pre_run],
                         ['base-pre', 'py27-pre', 'py27-diablo-pre'])
        self.assertEqual([x['path'] for x in j.post_run],
                         ['py27-diablo-post', 'py27-post-a', 'py27-post-b',
                          'base-post'])
        self.assertEqual([x['path'] for x in j.run],
                         ['py27-diablo'])

        j = self.history[2].job
        self.assertEqual(j.timeout, 40)
        self.assertEqual(len(j.nodeset.nodes), 1)
        self.assertEqual(next(iter(j.nodeset.nodes.values())).label, 'new')
        self.assertEqual([x['path'] for x in j.pre_run],
                         ['base-pre', 'py27-pre', 'py27-essex-pre'])
        self.assertEqual([x['path'] for x in j.post_run],
                         ['py27-essex-post', 'py27-post-a', 'py27-post-b',
                          'base-post'])
        self.assertEqual([x['path'] for x in j.run],
                         ['playbooks/python27.yaml'])

    @simple_layout("layouts/no-run.yaml")
    def test_job_without_run(self):
        "Test that a job without a run playbook errors"
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertIn('Job base does not specify a run playbook',
                      A.messages[-1])

    def test_queue_names(self):
        "Test shared change queue names"
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        (trusted, project1) = tenant.getProject('org/project1')
        (trusted, project2) = tenant.getProject('org/project2')
        # Change queues are created lazy by the dependent pipeline manager
        # so retrieve the queue first without having to really enqueue a
        # change first.
        gate = tenant.layout.pipelines['gate']
        FakeChange = namedtuple('FakeChange', ['project', 'branch'])
        fake_a = FakeChange(project1, 'master')
        fake_b = FakeChange(project2, 'master')
        with gate.manager.currentContext(self.createZKContext()):
            gate.manager.getChangeQueue(fake_a, None)
            gate.manager.getChangeQueue(fake_b, None)
        q1 = gate.getQueue(project1.canonical_name, None)
        q2 = gate.getQueue(project2.canonical_name, None)
        self.assertEqual(q1.name, 'integrated')
        self.assertEqual(q2.name, 'integrated')

    @simple_layout("layouts/template-queue.yaml")
    def test_template_queue(self):
        "Test a shared queue can be constructed from a project-template"
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        (trusted, project1) = tenant.getProject('org/project1')
        (trusted, project2) = tenant.getProject('org/project2')

        # Change queues are created lazy by the dependent pipeline manager
        # so retrieve the queue first without having to really enqueue a
        # change first.
        gate = tenant.layout.pipelines['gate']
        FakeChange = namedtuple('FakeChange', ['project', 'branch'])
        fake_a = FakeChange(project1, 'master')
        fake_b = FakeChange(project2, 'master')
        with gate.manager.currentContext(self.createZKContext()):
            gate.manager.getChangeQueue(fake_a, None)
            gate.manager.getChangeQueue(fake_b, None)
        q1 = gate.getQueue(project1.canonical_name, None)
        q2 = gate.getQueue(project2.canonical_name, None)
        self.assertEqual(q1.name, 'integrated')
        self.assertEqual(q2.name, 'integrated')

    @simple_layout("layouts/template-project-queue.yaml")
    def test_template_project_queue(self):
        "Test a shared queue can be constructed from a project-template"
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        (trusted, project1) = tenant.getProject('org/project1')
        (trusted, project2) = tenant.getProject('org/project2')

        # Change queues are created lazy by the dependent pipeline manager
        # so retrieve the queue first without having to really enqueue a
        # change first.
        gate = tenant.layout.pipelines['gate']
        FakeChange = namedtuple('FakeChange', ['project', 'branch'])
        fake_a = FakeChange(project1, 'master')
        fake_b = FakeChange(project2, 'master')
        with gate.manager.currentContext(self.createZKContext()):
            gate.manager.getChangeQueue(fake_a, None)
            gate.manager.getChangeQueue(fake_b, None)
        q1 = gate.getQueue(project1.canonical_name, None)
        q2 = gate.getQueue(project2.canonical_name, None)
        self.assertEqual(q1.name, 'integrated')
        self.assertEqual(q2.name, 'integrated')

    @simple_layout("layouts/regex-template-queue.yaml")
    def test_regex_template_queue(self):
        "Test a shared queue can be constructed from a regex project-template"
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        (trusted, project1) = tenant.getProject('org/project1')
        (trusted, project2) = tenant.getProject('org/project2')
        # Change queues are created lazy by the dependent pipeline manager
        # so retrieve the queue first without having to really enqueue a
        # change first.
        gate = tenant.layout.pipelines['gate']
        FakeChange = namedtuple('FakeChange', ['project', 'branch'])
        fake_a = FakeChange(project1, 'master')
        fake_b = FakeChange(project2, 'master')
        with gate.manager.currentContext(self.createZKContext()):
            gate.manager.getChangeQueue(fake_a, None)
            gate.manager.getChangeQueue(fake_b, None)
        q1 = gate.getQueue(project1.canonical_name, None)
        q2 = gate.getQueue(project2.canonical_name, None)
        self.assertEqual(q1.name, 'integrated')
        self.assertEqual(q2.name, 'integrated')

    @simple_layout("layouts/regex-queue.yaml")
    @skipIfMultiScheduler()
    def test_regex_queue(self):
        "Test a shared queue can be constructed from a regex project"
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        (trusted, project1) = tenant.getProject('org/project1')
        (trusted, project2) = tenant.getProject('org/project2')
        # Change queues are created lazy by the dependent pipeline manager
        # so retrieve the queue first without having to really enqueue a
        # change first.
        gate = tenant.layout.pipelines['gate']
        FakeChange = namedtuple('FakeChange', ['project', 'branch'])
        fake_a = FakeChange(project1, 'master')
        fake_b = FakeChange(project2, 'master')
        with gate.manager.currentContext(self.createZKContext()):
            gate.manager.getChangeQueue(fake_a, None)
            gate.manager.getChangeQueue(fake_b, None)
        q1 = gate.getQueue(project1.canonical_name, None)
        q2 = gate.getQueue(project2.canonical_name, None)
        self.assertEqual(q1.name, 'integrated')
        self.assertEqual(q2.name, 'integrated')

    def test_queue_precedence(self):
        "Test that queue precedence works"

        self.hold_jobs_in_queue = True
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))

        self.waitUntilSettled()
        self.hold_jobs_in_queue = False
        self.executor_api.release()
        self.waitUntilSettled()

        # Run one build at a time to ensure non-race order:
        self.orderedRelease()
        self.executor_server.hold_jobs_in_build = False
        self.waitUntilSettled()

        self.log.debug(self.history)
        self.assertEqual(self.history[0].pipeline, 'gate')
        self.assertEqual(self.history[1].pipeline, 'check')
        self.assertEqual(self.history[2].pipeline, 'gate')
        self.assertEqual(self.history[3].pipeline, 'gate')
        self.assertEqual(self.history[4].pipeline, 'check')
        self.assertEqual(self.history[5].pipeline, 'check')

    def test_reconfigure_merge(self):
        """Test that two reconfigure events are merged"""
        # Wrap the recofiguration handler so we can count how many
        # times it runs.
        with mock.patch.object(
                zuul.scheduler.Scheduler, '_doTenantReconfigureEvent',
                wraps=self.scheds.first.sched._doTenantReconfigureEvent
        ) as mymock:
            with self.scheds.first.sched.run_handler_lock:
                self.create_branch('org/project', 'stable/diablo')
                self.fake_gerrit.addEvent(
                    self.fake_gerrit.getFakeBranchCreatedEvent(
                        'org/project', 'stable/diablo'))
                self.create_branch('org/project', 'stable/essex')
                self.fake_gerrit.addEvent(
                    self.fake_gerrit.getFakeBranchCreatedEvent(
                        'org/project', 'stable/essex'))
                for _ in iterate_timeout(60, 'jobs started'):
                    if len(self.scheds.first.sched.trigger_events[
                            'tenant-one']) == 2:
                        break

            self.waitUntilSettled()
            mymock.assert_called_once()

    def test_live_reconfiguration(self):
        "Test that live reconfiguration works"
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)

    def test_live_reconfiguration_layout_cache_fallback(self):
        # Test that re-calculating a dynamic fallback layout works after it
        # was removed during a reconfiguration.
        self.executor_server.hold_jobs_in_build = True

        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: project-test3
                parent: project-test1

            # add a job by the canonical project name
            - project:
                gate:
                  jobs:
                    - project-test3:
                        dependencies:
                          - project-merge
            """)

        file_dict = {'zuul.d/a.yaml': in_repo_conf}

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        pipeline = tenant.layout.pipelines['gate']
        items = pipeline.getAllItems()
        self.assertEqual(len(items), 1)
        self.assertIsNone(items[0].layout_uuid)

        # Assert that the layout cache is empty after a reconfiguration.
        self.assertEqual(pipeline.manager._layout_cache, {})

        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B',
                                           parent='refs/changes/01/1/1')
        B.addApproval('Code-Review', 2)

        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        items = pipeline.getAllItems()
        self.assertEqual(len(items), 2)
        for item in items:
            # Layout UUID should be set again for all live items. It had to
            # be re-calculated for the first item in the queue as it was reset
            # during re-enqueue.
            self.assertIsNotNone(item.layout_uuid)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(B.reported, 2)

        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-merge', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-test3', result='SUCCESS', changes='1,1'),
            dict(name='project-test3', result='SUCCESS', changes='1,1 2,1'),
        ], ordered=False)

    def test_live_reconfiguration_layout_cache_non_live(self):
        # Test that the layout UUID is only reset for live items.
        self.executor_server.hold_jobs_in_build = True

        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: project-test3
                parent: project-test1

            # add a job by the canonical project name
            - project:
                check:
                  jobs:
                    - project-test3:
                        dependencies:
                          - project-merge
            """)

        file_dict = {'zuul.d/a.yaml': in_repo_conf}

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B',
                                           parent='refs/changes/01/1/1')
        B.setDependsOn(A, 1)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        pipeline = tenant.layout.pipelines['check']
        items = pipeline.getAllItems()
        self.assertEqual(len(items), 2)

        # Assert that the layout UUID of the live item is reset during a
        # reconfiguration, but non-live items keep their UUID.
        self.assertIsNotNone(items[0].layout_uuid)
        self.assertIsNone(items[1].layout_uuid)

        # Cache should be empty after a reconfiguration
        self.assertEqual(pipeline.manager._layout_cache, {})

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(A.reported, 0)
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(B.reported, 1)

        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-test3', result='SUCCESS', changes='1,1 2,1'),
        ], ordered=False)

    def test_live_reconfiguration_command_socket(self):
        "Test that live reconfiguration via command socket works"

        # record previous tenant reconfiguration state, which may not be set
        old = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)
        self.waitUntilSettled()

        command_socket = self.scheds.first.config.get(
            'scheduler', 'command_socket')
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(command_socket)
            s.sendall('full-reconfigure\n'.encode('utf8'))

        # Wait for full reconfiguration. Note that waitUntilSettled is not
        # reliable here because the reconfigure event may arrive in the
        # event queue after waitUntilSettled.
        start = time.time()
        while True:
            if time.time() - start > 15:
                raise Exception("Timeout waiting for full reconfiguration")
            new = self.scheds.first.sched.tenant_layout_state.get(
                'tenant-one', EMPTY_LAYOUT_STATE)
            if old < new:
                break
            else:
                time.sleep(0)

    def test_double_live_reconfiguration_shared_queue(self):
        # This was a real-world regression.  A change is added to
        # gate; a reconfigure happens, a second change which depends
        # on the first is added, and a second reconfiguration happens.
        # Ensure that both changes merge.

        # A failure may indicate incorrect caching or cleaning up of
        # references during a reconfiguration.
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        B.setDependsOn(A, 1)
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)

        # Add the parent change.
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        # Reconfigure (with only one change in the pipeline).
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        # Add the child change.
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        # Reconfigure (with both in the pipeline).
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.history), 8)

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(B.reported, 2)

    def test_live_reconfiguration_del_project(self):
        # Test project deletion from tenant while changes are enqueued

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project1', 'master', 'C')

        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 8)

        self.newTenantConfig('config/single-tenant/main-one-project.yaml')
        # This layout defines only org/project, not org/project1
        self.commitConfigUpdate(
            'common-config',
            'layouts/live-reconfiguration-del-project.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(C.data['status'], 'NEW')
        self.assertEqual(A.reported, 1)
        self.assertEqual(B.reported, 0)
        self.assertEqual(C.reported, 0)

        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='2,1'),
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-merge', result='SUCCESS', changes='3,1'),
            dict(name='project-test1', result='ABORTED', changes='2,1'),
            dict(name='project-test2', result='ABORTED', changes='2,1'),
            dict(name='project1-project2-integration',
                 result='ABORTED', changes='2,1'),
            dict(name='project-test1', result='ABORTED', changes='3,1'),
            dict(name='project-test2', result='ABORTED', changes='3,1'),
            dict(name='project1-project2-integration',
                 result='ABORTED', changes='3,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
        ], ordered=False)

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertEqual(len(tenant.layout.pipelines['check'].queues), 0)
        self.assertIn('Build succeeded', A.messages[0])

    def test_live_reconfiguration_del_pipeline(self):
        # Test pipeline deletion while changes are enqueued

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 2)

        # This layout defines only org/project, not org/project1
        self.commitConfigUpdate(
            'common-config',
            'layouts/live-reconfiguration-del-pipeline.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(A.reported, 0)

        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='ABORTED', changes='1,1'),
            dict(name='project-test2', result='ABORTED', changes='1,1'),
        ], ordered=False)

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertEqual(len(tenant.layout.pipelines), 0)

    def test_live_reconfiguration_del_tenant(self):
        # Test tenant deletion while changes are enqueued

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project1', 'master', 'C')

        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 8)

        self.newTenantConfig('config/single-tenant/main-no-tenants.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(C.data['status'], 'NEW')
        self.assertEqual(A.reported, 0)
        self.assertEqual(B.reported, 0)
        self.assertEqual(C.reported, 0)

        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='2,1'),
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-merge', result='SUCCESS', changes='3,1'),
            dict(name='project-test1', result='ABORTED', changes='2,1'),
            dict(name='project-test2', result='ABORTED', changes='2,1'),
            dict(name='project1-project2-integration',
                 result='ABORTED', changes='2,1'),
            dict(name='project-test1', result='ABORTED', changes='3,1'),
            dict(name='project-test2', result='ABORTED', changes='3,1'),
            dict(name='project1-project2-integration',
                 result='ABORTED', changes='3,1'),
            dict(name='project-test1', result='ABORTED', changes='1,1'),
            dict(name='project-test2', result='ABORTED', changes='1,1'),
        ], ordered=False)

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertIsNone(tenant)

    @simple_layout("layouts/reconfigure-failed-head.yaml")
    def test_live_reconfiguration_failed_change_at_head(self):
        # Test that if we reconfigure with a failed change at head,
        # that the change behind it isn't reparented onto it.

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        B.addApproval('Code-Review', 2)

        self.executor_server.failJob('job1', A)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))

        self.waitUntilSettled()

        self.assertBuilds([
            dict(name='job1', changes='1,1'),
            dict(name='job2', changes='1,1'),
            dict(name='job1', changes='1,1 2,1'),
            dict(name='job2', changes='1,1 2,1'),
        ])

        self.release(self.builds[0])
        self.waitUntilSettled()

        self.assertBuilds([
            dict(name='job2', changes='1,1'),
            dict(name='job1', changes='2,1'),
            dict(name='job2', changes='2,1'),
        ])

        # Unordered history comparison because the aborts can finish
        # in any order.
        self.assertHistory([
            dict(name='job1', result='FAILURE', changes='1,1'),
            dict(name='job1', result='ABORTED', changes='1,1 2,1'),
            dict(name='job2', result='ABORTED', changes='1,1 2,1'),
        ], ordered=False)

        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertBuilds([])

        self.assertHistory([
            dict(name='job1', result='FAILURE', changes='1,1'),
            dict(name='job1', result='ABORTED', changes='1,1 2,1'),
            dict(name='job2', result='ABORTED', changes='1,1 2,1'),
            dict(name='job2', result='SUCCESS', changes='1,1'),
            dict(name='job1', result='SUCCESS', changes='2,1'),
            dict(name='job2', result='SUCCESS', changes='2,1'),
        ], ordered=False)
        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)

    def test_delayed_repo_init(self):
        self.init_repo("org/new-project")
        files = {'README': ''}
        self.addCommitToRepo("org/new-project", 'Initial commit',
                             files=files, tag='init')
        self.newTenantConfig('tenants/delayed-repo-init.yaml')
        self.commitConfigUpdate(
            'common-config',
            'layouts/delayed-repo-init.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        A = self.fake_gerrit.addFakeChange('org/new-project', 'master', 'A')

        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)

    @simple_layout('layouts/single-job-with-nodeset.yaml')
    def test_live_reconfiguration_queued_node_requests(self):
        # Test that a job with a queued node request still has the
        # correct state after reconfiguration.
        self.fake_nodepool.pause()
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        def get_job():
            tenant = self.scheds.first.sched.abide.tenants['tenant-one']
            for pipeline in tenant.layout.pipelines.values():
                pipeline_status = pipeline.formatStatusJSON(
                    self.scheds.first.sched.globals.websocket_url)
                for queue in pipeline_status['change_queues']:
                    for head in queue['heads']:
                        for item in head:
                            for job in item['jobs']:
                                if job['name'] == 'check-job':
                                    return job

        job = get_job()
        self.assertTrue(job['queued'])

        self.scheds.execute(lambda app: app.sched.reconfigure(self.config))
        self.waitUntilSettled()

        job = get_job()
        self.assertTrue(job['queued'])

        self.fake_nodepool.unpause()
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='check-job', result='SUCCESS', changes='1,1'),
        ])

    @simple_layout('layouts/repo-deleted.yaml')
    def test_repo_deleted(self):
        self.init_repo("org/delete-project")
        A = self.fake_gerrit.addFakeChange('org/delete-project', 'master', 'A')

        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)

        # Delete org/new-project zuul repo. Should be recloned.
        p = 'org/delete-project'
        if os.path.exists(os.path.join(self.merger_src_root, p)):
            shutil.rmtree(os.path.join(self.merger_src_root, p))
        if os.path.exists(os.path.join(self.executor_src_root, p)):
            shutil.rmtree(os.path.join(self.executor_src_root, p))

        B = self.fake_gerrit.addFakeChange('org/delete-project', 'master', 'B')

        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(B.reported, 2)

    @simple_layout('layouts/untrusted-secrets.yaml')
    def test_untrusted_secrets(self):
        "Test untrusted secrets"
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertHistory([])
        self.assertEqual(A.patchsets[0]['approvals'][0]['value'], "-1")
        self.assertIn('does not allow post-review job',
                      A.messages[0])

    @simple_layout('layouts/tags.yaml')
    def test_tags(self):
        "Test job tags"
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project2', 'master', 'B')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(self.history), 2)

        results = {self.getJobFromHistory('merge',
                   project='org/project1').uuid: ['extratag', 'merge'],
                   self.getJobFromHistory('merge',
                   project='org/project2').uuid: ['merge']}

        for build in self.history:
            self.assertEqual(results.get(build.uuid, ''),
                             build.parameters['zuul'].get('jobtags'))

    def test_timer_template(self):
        "Test that a periodic job is triggered"
        # This test can not use simple_layout because it must start
        # with a configuration which does not include a
        # timer-triggered job so that we have an opportunity to set
        # the hold flag before the first job.
        self.create_branch('org/project', 'stable')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project', 'stable'))
        self.executor_server.hold_jobs_in_build = True
        self.commitConfigUpdate('common-config', 'layouts/timer-template.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))

        # The pipeline triggers every second, so we should have seen
        # several by now.
        time.sleep(5)
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 2)

        merge_count_project1 = 0
        for job in self.merge_job_history.get(
            zuul.model.MergeRequest.REF_STATE
        ):
            if job.payload["items"][0]["project"] == "org/project1":
                merge_count_project1 += 1
        self.assertEquals(merge_count_project1, 0,
                          "project1 shouldn't have any refstate call")

        self.executor_server.hold_jobs_in_build = False
        # Stop queuing timer triggered jobs so that the assertions
        # below don't race against more jobs being queued.
        self.commitConfigUpdate('common-config', 'layouts/no-timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        # If APScheduler is in mid-event when we remove the job, we
        # can end up with one more event firing, so give it an extra
        # second to settle.
        time.sleep(1)
        self.waitUntilSettled()
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='project-bitrot', result='SUCCESS',
                 ref='refs/heads/master'),
            dict(name='project-bitrot', result='SUCCESS',
                 ref='refs/heads/stable'),
        ], ordered=False)

    def _test_timer(self, config_file):
        # This test can not use simple_layout because it must start
        # with a configuration which does not include a
        # timer-triggered job so that we have an opportunity to set
        # the hold flag before the first job.
        self.create_branch('org/project', 'stable')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project', 'stable'))
        self.executor_server.hold_jobs_in_build = True
        self.commitConfigUpdate('common-config', config_file)
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))

        # The pipeline triggers every second, so we should have seen
        # several by now.
        for _ in iterate_timeout(60, 'jobs started'):
            if len(self.builds) > 1:
                break

        merge_count_project1 = 0
        for job in self.gearman_server.jobs_history:
            if job.name == b'merger:refstate':
                args = job.arguments
                if isinstance(args, bytes):
                    args = args.decode('utf-8')
                args = json.loads(args)
                if args["items"][0]["project"] == "org/project1":
                    merge_count_project1 += 1
        self.assertEquals(merge_count_project1, 0,
                          "project1 shouldn't have any refstate call")

        # Ensure that the status json has the ref so we can render it in the
        # web ui.
        pipeline = self.scheds.first.sched.abide.tenants[
            'tenant-one'].layout.pipelines['periodic']
        pipeline_status = pipeline.formatStatusJSON(
            self.scheds.first.sched.globals.websocket_url)

        first = pipeline_status['change_queues'][0]['heads'][0][0]
        second = pipeline_status['change_queues'][1]['heads'][0][0]
        self.assertIn(first['ref'], ['refs/heads/master', 'refs/heads/stable'])
        self.assertIn(second['ref'],
                      ['refs/heads/master', 'refs/heads/stable'])

        self.executor_server.hold_jobs_in_build = False

        # Stop queuing timer triggered jobs so that the assertions
        # below don't race against more jobs being queued.
        self.commitConfigUpdate('common-config', 'layouts/no-timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        # If APScheduler is in mid-event when we remove the job, we
        # can end up with one more event firing, so give it an extra
        # second to settle.
        time.sleep(3)
        self.waitUntilSettled()

        self.executor_server.release()
        self.waitUntilSettled()

        self.assertTrue(len(self.history) > 1)
        for job in self.history[:1]:
            self.assertEqual(job.result, 'SUCCESS')
            self.assertEqual(job.name, 'project-bitrot')
            self.assertIn(job.ref, ('refs/heads/stable', 'refs/heads/master'))

    def test_timer(self):
        "Test that a periodic job is triggered"
        self._test_timer('layouts/timer.yaml')

    def test_timer_with_jitter(self):
        "Test that a periodic job with a jitter is triggered"
        self._test_timer('layouts/timer-jitter.yaml')

    def test_idle(self):
        "Test that frequent periodic jobs work"
        # This test can not use simple_layout because it must start
        # with a configuration which does not include a
        # timer-triggered job so that we have an opportunity to set
        # the hold flag before the first job.
        self.executor_server.hold_jobs_in_build = True

        for x in range(1, 3):
            # Test that timer triggers periodic jobs even across
            # layout config reloads.
            # Start timer trigger
            self.commitConfigUpdate('common-config',
                                    'layouts/idle.yaml')
            self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
            self.waitUntilSettled()

            # The pipeline triggers every second, so we should have seen
            # several by now.
            time.sleep(5)

            # Stop queuing timer triggered jobs so that the assertions
            # below don't race against more jobs being queued.
            self.commitConfigUpdate('common-config',
                                    'layouts/no-timer.yaml')
            self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
            self.waitUntilSettled()
            # If APScheduler is in mid-event when we remove the job,
            # we can end up with one more event firing, so give it an
            # extra second to settle.
            time.sleep(1)
            self.waitUntilSettled()
            self.assertEqual(len(self.builds), 1,
                             'Timer builds iteration #%d' % x)
            self.executor_server.release('.*')
            self.waitUntilSettled()
            self.assertEqual(len(self.builds), 0)
            self.assertEqual(len(self.history), x)

    @simple_layout('layouts/smtp.yaml')
    def test_check_smtp_pool(self):
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.waitUntilSettled()

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(self.smtp_messages), 2)

        # A.messages only holds what FakeGerrit places in it. Thus we
        # work on the knowledge of what the first message should be as
        # it is only configured to go to SMTP.

        self.assertEqual('zuul@example.com',
                         self.smtp_messages[0]['from_email'])
        self.assertEqual(['you@example.com'],
                         self.smtp_messages[0]['to_email'])
        self.assertEqual('Starting check jobs.',
                         self.smtp_messages[0]['body'])

        self.assertEqual('zuul_from@example.com',
                         self.smtp_messages[1]['from_email'])
        self.assertEqual(['alternative_me@example.com'],
                         self.smtp_messages[1]['to_email'])
        self.assertEqual(A.messages[0],
                         self.smtp_messages[1]['body'])

    @simple_layout('layouts/smtp.yaml')
    @mock.patch('zuul.driver.gerrit.gerritreporter.GerritReporter.report')
    def test_failed_reporter(self, report_mock):
        '''Test that one failed reporter doesn't break other reporters'''
        # Warning hacks. We sort the reports here so that the test is
        # deterministic. Gerrit reporting will fail, but smtp reporting
        # should succeed.
        report_mock.side_effect = Exception('Gerrit failed to report')

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        check = tenant.layout.pipelines['check']

        check.success_actions = sorted(check.success_actions,
                                       key=lambda x: x.name)
        self.assertEqual(check.success_actions[0].name, 'gerrit')
        self.assertEqual(check.success_actions[1].name, 'smtp')

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # We know that if gerrit ran first and failed and smtp ran second
        # and sends mail then we handle failures in reporters gracefully.
        self.assertEqual(len(self.smtp_messages), 2)

        # A.messages only holds what FakeGerrit places in it. Thus we
        # work on the knowledge of what the first message should be as
        # it is only configured to go to SMTP.

        self.assertEqual('zuul@example.com',
                         self.smtp_messages[0]['from_email'])
        self.assertEqual(['you@example.com'],
                         self.smtp_messages[0]['to_email'])
        self.assertEqual('Starting check jobs.',
                         self.smtp_messages[0]['body'])

        self.assertEqual('zuul_from@example.com',
                         self.smtp_messages[1]['from_email'])
        self.assertEqual(['alternative_me@example.com'],
                         self.smtp_messages[1]['to_email'])
        # This double checks that Gerrit side failed
        self.assertEqual(A.messages, [])

    def test_timer_smtp(self):
        "Test that a periodic job is triggered"
        # This test can not use simple_layout because it must start
        # with a configuration which does not include a
        # timer-triggered job so that we have an opportunity to set
        # the hold flag before the first job.
        self.executor_server.hold_jobs_in_build = True
        self.commitConfigUpdate('common-config', 'layouts/timer-smtp.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))

        # The pipeline triggers every second, so we should have seen
        # several by now.
        time.sleep(5)
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 2)
        self.executor_server.release('.*')
        self.waitUntilSettled()
        self.assertEqual(len(self.history), 2)

        self.assertEqual(self.getJobFromHistory(
            'project-bitrot-stable-old').result, 'SUCCESS')
        self.assertEqual(self.getJobFromHistory(
            'project-bitrot-stable-older').result, 'SUCCESS')

        self.assertEqual(len(self.smtp_messages), 1)

        # A.messages only holds what FakeGerrit places in it. Thus we
        # work on the knowledge of what the first message should be as
        # it is only configured to go to SMTP.

        self.assertEqual('zuul_from@example.com',
                         self.smtp_messages[0]['from_email'])
        self.assertEqual(['alternative_me@example.com'],
                         self.smtp_messages[0]['to_email'])
        self.assertIn('Subject: Periodic check for org/project succeeded',
                      self.smtp_messages[0]['headers'])

        # Stop queuing timer triggered jobs and let any that may have
        # queued through so that end of test assertions pass.
        self.commitConfigUpdate('common-config', 'layouts/no-timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        # If APScheduler is in mid-event when we remove the job, we
        # can end up with one more event firing, so give it an extra
        # second to settle.
        time.sleep(1)
        self.waitUntilSettled()
        self.executor_server.release('.*')
        self.waitUntilSettled()

    @skip("Disabled for early v3 development")
    def test_timer_sshkey(self):
        "Test that a periodic job can setup SSH key authentication"
        self.worker.hold_jobs_in_build = True
        self.config.set('zuul', 'layout_config',
                        'tests/fixtures/layout-timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.registerJobs()

        # The pipeline triggers every second, so we should have seen
        # several by now.
        time.sleep(5)
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 2)

        ssh_wrapper = os.path.join(self.git_root, ".ssh_wrapper_gerrit")
        self.assertTrue(os.path.isfile(ssh_wrapper))
        with open(ssh_wrapper) as f:
            ssh_wrapper_content = f.read()
        self.assertIn("fake_id_rsa", ssh_wrapper_content)
        # In the unit tests Merger runs in the same process,
        # so we see its' environment variables
        self.assertEqual(os.environ['GIT_SSH'], ssh_wrapper)

        self.worker.release('.*')
        self.waitUntilSettled()
        self.assertEqual(len(self.history), 2)

        self.assertEqual(self.getJobFromHistory(
            'project-bitrot-stable-old').result, 'SUCCESS')
        self.assertEqual(self.getJobFromHistory(
            'project-bitrot-stable-older').result, 'SUCCESS')

        # Stop queuing timer triggered jobs and let any that may have
        # queued through so that end of test assertions pass.
        self.config.set('zuul', 'layout_config',
                        'tests/fixtures/layout-no-timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.registerJobs()
        self.waitUntilSettled()
        # If APScheduler is in mid-event when we remove the job, we
        # can end up with one more event firing, so give it an extra
        # second to settle.
        time.sleep(1)
        self.waitUntilSettled()
        self.worker.release('.*')
        self.waitUntilSettled()

    def test_client_enqueue_change_with_trigger(self):
        """Test that the RPC client can enqueue a change with the deprecated
           trigger argument"""
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        A.addApproval('Approved', 1)

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.enqueue(tenant='tenant-one',
                           pipeline='gate',
                           project='org/project',
                           trigger='gerrit',
                           change='1,1')
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(r, True)

    def test_client_enqueue_change_no_trigger(self):
        """Test that the RPC client can enqueue a change without an explicit
           trigger"""
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        A.addApproval('Approved', 1)

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.enqueue(tenant='tenant-one',
                           pipeline='gate',
                           project='org/project',
                           trigger=None,
                           change='1,1')
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(r, True)

    @simple_layout('layouts/three-projects.yaml')
    def test_client_enqueue_change_wrong_project(self):
        "Test that an enqueue fails if a change doesn't belong to the project"
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        A.addApproval('Code-Review', 2)
        A.addApproval('Approved', 1)

        B = self.fake_gerrit.addFakeChange('org/project2', 'master', 'B')
        B.addApproval('Code-Review', 2)
        B.addApproval('Approved', 1)

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        matcher = AfterPreprocessing(
            str, MatchesRegex(
                r'.*Change <Change \w+ org/project2 2,1> does not belong to '
                r'project "org/project1"',
                re.DOTALL
            )
        )
        with testtools.ExpectedException(zuul.rpcclient.RPCFailure, matcher):
            r = client.enqueue(tenant='tenant-one',
                               pipeline='gate',
                               project='org/project1',
                               trigger=None,
                               change='2,1')
            self.assertEqual(r, False)
        self.waitUntilSettled()

    def test_client_enqueue_ref(self):
        "Test that the RPC client can enqueue a ref"
        p = "review.example.com/org/project"
        upstream = self.getUpstreamRepos([p])
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.setMerged()
        A_commit = str(upstream[p].commit('master'))
        self.log.debug("A commit: %s" % A_commit)

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.enqueue_ref(
            tenant='tenant-one',
            pipeline='post',
            project='org/project',
            trigger=None,
            ref='master',
            oldrev='90f173846e3af9154517b88543ffbd1691f31366',
            newrev=A_commit)
        self.waitUntilSettled()
        job_names = [x.name for x in self.history]
        self.assertEqual(len(self.history), 1)
        self.assertIn('project-post', job_names)
        self.assertEqual(r, True)

    def test_client_dequeue_ref(self):
        "Test that the RPC client can dequeue a ref"

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        self.executor_server.hold_jobs_in_build = True

        p = "review.example.com/org/project"
        upstream = self.getUpstreamRepos([p])
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.setMerged()
        A_commit = str(upstream[p].commit('master'))
        self.log.debug("A commit: %s" % A_commit)

        r = client.enqueue_ref(
            tenant='tenant-one',
            pipeline='post',
            project='org/project',
            trigger=None,
            ref='master',
            oldrev='90f173846e3af9154517b88543ffbd1691f31366',
            newrev=A_commit)

        p = "review.example.com/org/project1"
        upstream = self.getUpstreamRepos([p])
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        B.setMerged()
        B_commit = str(upstream[p].commit('master'))
        self.log.debug("B commit: %s" % B_commit)

        r = client.enqueue_ref(
            tenant='tenant-one',
            pipeline='post',
            project='org/project1',
            trigger=None,
            ref='master',
            oldrev='90f173846e3af9154517b88543ffbd1691f31366',
            newrev=B_commit)

        self.waitUntilSettled()
        r = client.dequeue(
            tenant='tenant-one',
            pipeline='post',
            project='org/project1',
            change=None,
            ref='master')
        self.waitUntilSettled()
        self.executor_server.release('.*')
        self.waitUntilSettled()
        job_names = [x.name for x in self.history]
        self.assertEqual(len(self.history), 2)
        aborted_build = [
            build for build in self.history if
            build.result == 'ABORTED'][0]
        self.assertEqual(aborted_build.newrev, B_commit)
        self.assertIn('project-post', job_names)
        self.assertEqual(r, True)

    def test_client_dequeue_dependent_change(self):
        "Test that the RPC client can dequeue a change"
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')

        C.setDependsOn(B, 1)
        B.setDependsOn(A, 1)

        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        # Promote to 'gate' pipeline
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        client.dequeue(
            tenant='tenant-one',
            pipeline='gate',
            project='org/project',
            change='1,1',
            ref=None)

        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        gate_pipeline = tenant.layout.pipelines['gate']
        self.assertEqual(gate_pipeline.getAllItems(), [])
        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 1)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    def test_client_dequeue_independent_change(self):
        "Test that the RPC client can dequeue a change"

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')

        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        client.dequeue(
            tenant='tenant-one',
            pipeline='check',
            project='org/project',
            change='1,1',
            ref=None)
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        check_pipeline = tenant.layout.pipelines['check']
        self.assertEqual(len(check_pipeline.getAllItems()), 2)
        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 1)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    @simple_layout('layouts/three-projects.yaml')
    def test_client_dequeue_wrong_project(self):
        "Test that dequeue fails if change and project do not match"

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project1', 'master', 'C')
        D = self.fake_gerrit.addFakeChange('org/project2', 'master', 'D')

        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        D.addApproval('Code-Review', 2)

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(D.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        matcher = AfterPreprocessing(
            str,
            MatchesRegex(
                '.*Change 4,1 does not belong to project "org/project1"',
                re.DOTALL,
            ),
            annotate=False
        )
        with testtools.ExpectedException(
            zuul.rpcclient.RPCFailure, matcher):
            client.dequeue(
                tenant='tenant-one',
                pipeline='check',
                project='org/project1',
                change='4,1',
                ref=None
            )

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    def test_client_dequeue_change_by_ref(self):
        "Test that the RPC client can dequeue a change by ref"
        # Test this on the periodic pipeline, where it makes most sense to
        # use ref
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        self.create_branch('org/project', 'stable')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project', 'stable'))
        self.waitUntilSettled()
        self.executor_server.hold_jobs_in_build = True
        self.commitConfigUpdate('common-config', 'layouts/timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))

        # We expect that one build for each branch (master and stable) appears.
        for _ in iterate_timeout(30, 'Wait for two builds that are hold'):
            if len(self.builds) == 2:
                break
        self.waitUntilSettled()

        client.dequeue(
            tenant='tenant-one',
            pipeline='periodic',
            project='org/project',
            change=None,
            ref='refs/heads/stable')
        self.waitUntilSettled()

        self.commitConfigUpdate('common-config',
                                'layouts/no-timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 1)

    def test_client_enqueue_negative(self):
        "Test that the RPC client returns errors"
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        matcher = AfterPreprocessing(
            str, MatchesRegex(r'.*Unknown tenant', re.DOTALL)
        )
        with testtools.ExpectedException(zuul.rpcclient.RPCFailure, matcher):
            r = client.enqueue(tenant='tenant-foo',
                               pipeline='gate',
                               project='org/project',
                               trigger=None,
                               change='1,1')
            self.assertEqual(r, False)

        matcher = AfterPreprocessing(
            str, MatchesRegex(r'.*Unknown project', re.DOTALL)
        )
        with testtools.ExpectedException(zuul.rpcclient.RPCFailure, matcher):
            r = client.enqueue(tenant='tenant-one',
                               pipeline='gate',
                               project='project-does-not-exist',
                               trigger=None,
                               change='1,1')
            self.assertEqual(r, False)

        matcher = AfterPreprocessing(
            str, MatchesRegex(r'.*Unknown pipeline', re.DOTALL)
        )
        with testtools.ExpectedException(zuul.rpcclient.RPCFailure, matcher):
            r = client.enqueue(tenant='tenant-one',
                               pipeline='pipeline-does-not-exist',
                               project='org/project',
                               trigger=None,
                               change='1,1')
            self.assertEqual(r, False)

        matcher = AfterPreprocessing(
            str, MatchesRegex(r'.*Unknown change', re.DOTALL)
        )
        with testtools.ExpectedException(zuul.rpcclient.RPCFailure, matcher):
            r = client.enqueue(tenant='tenant-one',
                               pipeline='gate',
                               project='org/project',
                               trigger=None,
                               change='1,1')
            self.assertEqual(r, False)

        self.waitUntilSettled()
        self.assertEqual(len(self.history), 0)
        self.assertEqual(len(self.builds), 0)

    def test_client_enqueue_ref_negative(self):
        "Test that the RPC client returns errors"
        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        with testtools.ExpectedException(zuul.rpcclient.RPCFailure,
                                         "New rev must be 40 character sha1"):
            r = client.enqueue_ref(
                tenant='tenant-one',
                pipeline='post',
                project='org/project',
                trigger=None,
                ref='master',
                oldrev='90f173846e3af9154517b88543ffbd1691f31366',
                newrev='10054041')
            self.assertEqual(r, False)
        with testtools.ExpectedException(zuul.rpcclient.RPCFailure,
                                         "Old rev must be 40 character sha1"):
            r = client.enqueue_ref(
                tenant='tenant-one',
                pipeline='post',
                project='org/project',
                trigger=None,
                ref='master',
                oldrev='10054041',
                newrev='90f173846e3af9154517b88543ffbd1691f31366')
            self.assertEqual(r, False)
        with testtools.ExpectedException(zuul.rpcclient.RPCFailure,
                                         "New rev must be base16 hash"):
            r = client.enqueue_ref(
                tenant='tenant-one',
                pipeline='post',
                project='org/project',
                trigger=None,
                ref='master',
                oldrev='90f173846e3af9154517b88543ffbd1691f31366',
                newrev='notbase16')
            self.assertEqual(r, False)
        with testtools.ExpectedException(zuul.rpcclient.RPCFailure,
                                         "Old rev must be base16 hash"):
            r = client.enqueue_ref(
                tenant='tenant-one',
                pipeline='post',
                project='org/project',
                trigger=None,
                ref='master',
                oldrev='notbase16',
                newrev='90f173846e3af9154517b88543ffbd1691f31366')
            self.assertEqual(r, False)

    def test_client_promote(self):
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

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.promote(tenant='tenant-one',
                           pipeline='gate',
                           change_ids=['2,1', '3,1'])

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

        self.assertEqual(r, True)

    def test_client_promote_dependent(self):
        "Test that the RPC client can promote a dependent change"
        # C (depends on B) -> B -> A ; then promote C to get:
        # A -> C (depends on B) -> B
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')

        C.setDependsOn(B, 1)

        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))

        self.waitUntilSettled()

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.promote(tenant='tenant-one',
                           pipeline='gate',
                           change_ids=['3,1'])

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

        self.assertEqual(r, True)

    def test_client_promote_negative(self):
        "Test that the RPC client returns errors for promotion"
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        with testtools.ExpectedException(zuul.rpcclient.RPCFailure):
            r = client.promote(tenant='tenant-one',
                               pipeline='nonexistent',
                               change_ids=['2,1', '3,1'])
            self.assertEqual(r, False)

        with testtools.ExpectedException(zuul.rpcclient.RPCFailure):
            r = client.promote(tenant='tenant-one',
                               pipeline='gate',
                               change_ids=['4,1'])
            self.assertEqual(r, False)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    @simple_layout('layouts/rate-limit.yaml')
    def test_queue_rate_limiting(self):
        "Test that DependentPipelines are rate limited with dep across window"
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')

        C.setDependsOn(B, 1)
        self.executor_server.failJob('project-test1', A)

        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        # Only A and B will have their merge jobs queued because
        # window is 2.
        self.assertEqual(len(self.builds), 2)
        self.assertEqual(self.builds[0].name, 'project-merge')
        self.assertEqual(self.builds[1].name, 'project-merge')

        # Release the merge jobs one at a time.
        self.builds[0].release()
        self.waitUntilSettled()
        self.builds[0].release()
        self.waitUntilSettled()

        # Only A and B will have their test jobs queued because
        # window is 2.
        self.assertEqual(len(self.builds), 4)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test2')
        self.assertEqual(self.builds[2].name, 'project-test1')
        self.assertEqual(self.builds[3].name, 'project-test2')

        self.executor_server.release('project-.*')
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        queue = tenant.layout.pipelines['gate'].queues[0]
        # A failed so window is reduced by 1 to 1.
        self.assertEqual(queue.window, 1)
        self.assertEqual(queue.window_floor, 1)
        self.assertEqual(A.data['status'], 'NEW')

        # Gate is reset and only B's merge job is queued because
        # window shrunk to 1.
        self.assertEqual(len(self.builds), 1)
        self.assertEqual(self.builds[0].name, 'project-merge')

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        # Only B's test jobs are queued because window is still 1.
        self.assertEqual(len(self.builds), 2)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test2')

        self.executor_server.release('project-.*')
        self.waitUntilSettled()

        # B was successfully merged so window is increased to 2.
        self.assertEqual(queue.window, 2)
        self.assertEqual(queue.window_floor, 1)
        self.assertEqual(B.data['status'], 'MERGED')

        # Only C is left and its merge job is queued.
        self.assertEqual(len(self.builds), 1)
        self.assertEqual(self.builds[0].name, 'project-merge')

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        # After successful merge job the test jobs for C are queued.
        self.assertEqual(len(self.builds), 2)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test2')

        self.executor_server.release('project-.*')
        self.waitUntilSettled()

        # C successfully merged so window is bumped to 3.
        self.assertEqual(queue.window, 3)
        self.assertEqual(queue.window_floor, 1)
        self.assertEqual(C.data['status'], 'MERGED')

    @simple_layout('layouts/rate-limit.yaml')
    def test_queue_rate_limiting_dependent(self):
        "Test that DependentPipelines are rate limited with dep in window"
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')

        B.setDependsOn(A, 1)

        self.executor_server.failJob('project-test1', A)

        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        # Only A and B will have their merge jobs queued because
        # window is 2.
        self.assertEqual(len(self.builds), 2)
        self.assertEqual(self.builds[0].name, 'project-merge')
        self.assertEqual(self.builds[1].name, 'project-merge')

        self.orderedRelease(2)

        # Only A and B will have their test jobs queued because
        # window is 2.
        self.assertEqual(len(self.builds), 4)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test2')
        self.assertEqual(self.builds[2].name, 'project-test1')
        self.assertEqual(self.builds[3].name, 'project-test2')

        self.executor_server.release('project-.*')
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        queue = tenant.layout.pipelines['gate'].queues[0]
        # A failed so window is reduced by 1 to 1.
        self.assertEqual(queue.window, 1)
        self.assertEqual(queue.window_floor, 1)
        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(B.data['status'], 'NEW')

        # Gate is reset and only C's merge job is queued because
        # window shrunk to 1 and A and B were dequeued.
        self.assertEqual(len(self.builds), 1)
        self.assertEqual(self.builds[0].name, 'project-merge')

        self.orderedRelease(1)

        # Only C's test jobs are queued because window is still 1.
        self.assertEqual(len(self.builds), 2)
        builds = self.getSortedBuilds()
        self.assertEqual(builds[0].name, 'project-test1')
        self.assertEqual(builds[1].name, 'project-test2')

        self.executor_server.release('project-.*')
        self.waitUntilSettled()

        # C was successfully merged so window is increased to 2.
        self.assertEqual(queue.window, 2)
        self.assertEqual(queue.window_floor, 1)
        self.assertEqual(C.data['status'], 'MERGED')

    @simple_layout('layouts/rate-limit-reconfigure.yaml')
    def test_queue_rate_limiting_reconfigure(self):
        """Test that changes survive a reconfigure when no longer in window.

        This is a regression tests for a case that lead to an exception during
        re-enqueue. The exception happened when former active items had already
        build results but then dropped out of the active window. During
        re-enqueue the job graph was not re-initialized because the items were
        no longer active.
        """
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        D = self.fake_gerrit.addFakeChange('org/project', 'master', 'D')

        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        D.addApproval('Code-Review', 2)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(D.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 4)
        self.assertEqual(self.builds[0].name, 'project-merge')
        self.assertEqual(self.builds[1].name, 'project-merge')
        self.assertEqual(self.builds[2].name, 'project-merge')
        self.assertEqual(self.builds[3].name, 'project-merge')

        self.orderedRelease(4)

        self.assertEqual(len(self.builds), 8)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test2')
        self.assertEqual(self.builds[2].name, 'project-test1')
        self.assertEqual(self.builds[3].name, 'project-test2')
        self.assertEqual(self.builds[4].name, 'project-test1')
        self.assertEqual(self.builds[5].name, 'project-test2')
        self.assertEqual(self.builds[6].name, 'project-test1')
        self.assertEqual(self.builds[7].name, 'project-test2')

        self.executor_server.failJob('project-test1', B)
        self.builds[2].release()
        self.builds[3].release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 4)
        # A's jobs
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test2')
        # C's and D's merge jobs
        self.assertEqual(self.builds[2].name, 'project-merge')
        self.assertEqual(self.builds[3].name, 'project-merge')

        # Release merge jobs of C, D after speculative gate reset
        self.executor_server.release('project-merge')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 6)

        # A's jobs
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test2')
        # C's + D's jobs
        self.assertEqual(self.builds[2].name, 'project-test1')
        self.assertEqual(self.builds[3].name, 'project-test2')
        self.assertEqual(self.builds[4].name, 'project-test1')
        self.assertEqual(self.builds[5].name, 'project-test2')

        # Fail D's job so we have a build results for an item that
        # is not in the active window after B is reported
        # (condition that previously lead to an exception)
        self.executor_server.failJob('project-test1', D)
        self.builds[4].release()
        self.waitUntilSettled()

        # Release A's jobs
        self.builds[0].release()
        self.builds[1].release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 3)

        # C's jobs
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test2')
        # D's remaining job
        self.assertEqual(self.builds[2].name, 'project-test2')

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        queue = tenant.layout.pipelines['gate'].queues[0]
        self.assertEqual(queue.window, 1)

        # D dropped out of the window
        self.assertFalse(queue.queue[-1].active)

        self.commitConfigUpdate('org/common-config',
                                'layouts/rate-limit-reconfigure2.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        # D's remaining job should still be queued
        self.assertEqual(len(self.builds), 3)
        self.executor_server.release('project-.*')
        self.waitUntilSettled()

    @simple_layout('layouts/reconfigure-window.yaml')
    def test_reconfigure_window_shrink(self):
        # Test the active window shrinking during reconfiguration
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        queue = tenant.layout.pipelines['gate'].queues[0]
        self.assertEqual(queue.window, 20)
        self.assertTrue(len(self.builds), 4)

        self.executor_server.release('job1')
        self.waitUntilSettled()
        self.commitConfigUpdate('org/common-config',
                                'layouts/reconfigure-window2.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        queue = tenant.layout.pipelines['gate'].queues[0]
        # Even though we have configured a smaller window, the value
        # on the existing shared queue should be used.
        self.assertEqual(queue.window, 20)
        self.assertTrue(len(self.builds), 4)

        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        queue = tenant.layout.pipelines['gate'].queues[0]
        self.assertEqual(queue.window, 20)
        self.assertTrue(len(self.builds), 4)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()

        self.waitUntilSettled()
        self.assertHistory([
            dict(name='job1', result='SUCCESS', changes='1,1'),
            dict(name='job1', result='SUCCESS', changes='1,1 2,1'),
            dict(name='job2', result='SUCCESS', changes='1,1'),
            dict(name='job2', result='SUCCESS', changes='1,1 2,1'),
        ], ordered=False)

    @simple_layout('layouts/reconfigure-window-fixed.yaml')
    def test_reconfigure_window_fixed(self):
        # Test the active window shrinking during reconfiguration
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        queue = tenant.layout.pipelines['gate'].queues[0]
        self.assertEqual(queue.window, 2)
        self.assertEqual(len(self.builds), 4)

        self.waitUntilSettled()
        self.commitConfigUpdate('org/common-config',
                                'layouts/reconfigure-window-fixed2.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        queue = tenant.layout.pipelines['gate'].queues[0]
        # Because we have configured a static window, it should
        # be allowed to shrink on reconfiguration.
        self.assertEqual(queue.window, 1)
        # B is outside the window, but still marked active until the
        # next pass through the queue processor.
        self.assertEqual(len(self.builds), 4)

        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        queue = tenant.layout.pipelines['gate'].queues[0]
        self.assertEqual(queue.window, 1)
        self.waitUntilSettled()
        # B's builds should not be canceled
        self.assertEqual(len(self.builds), 4)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()

        self.waitUntilSettled()
        self.assertHistory([
            dict(name='job1', result='SUCCESS', changes='1,1'),
            dict(name='job2', result='SUCCESS', changes='1,1'),
            dict(name='job1', result='SUCCESS', changes='1,1 2,1'),
            dict(name='job2', result='SUCCESS', changes='1,1 2,1'),
        ], ordered=False)

    @simple_layout('layouts/reconfigure-window-fixed.yaml')
    def test_reconfigure_window_fixed_requests(self):
        # Test the active window shrinking during reconfiguration with
        # outstanding node requests
        self.executor_server.hold_jobs_in_build = True

        # Start the jobs for A
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.log.debug("A complete")

        # Hold node requests for B
        self.fake_nodepool.pause()
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.log.debug("B complete")

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        queue = tenant.layout.pipelines['gate'].queues[0]
        self.assertEqual(queue.window, 2)
        self.assertEqual(len(self.builds), 2)

        self.waitUntilSettled()
        self.commitConfigUpdate('org/common-config',
                                'layouts/reconfigure-window-fixed2.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        self.log.debug("Reconfiguration complete")

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        queue = tenant.layout.pipelines['gate'].queues[0]
        # Because we have configured a static window, it should
        # be allowed to shrink on reconfiguration.
        self.assertEqual(queue.window, 1)
        self.assertEqual(len(self.builds), 2)

        # After the previous reconfig, the queue processor will have
        # run and marked B inactive; run another reconfiguration so
        # that we're testing what happens when we reconfigure after
        # the active window having shrunk.
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))

        # Unpause the node requests now
        self.fake_nodepool.unpause()
        self.waitUntilSettled()
        self.log.debug("Nodepool unpause complete")

        # Allow A to merge and B to enter the active window and complete
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        self.log.debug("Executor unpause complete")

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        queue = tenant.layout.pipelines['gate'].queues[0]
        self.assertEqual(queue.window, 1)

        self.waitUntilSettled()
        self.assertHistory([
            dict(name='job1', result='SUCCESS', changes='1,1'),
            dict(name='job2', result='SUCCESS', changes='1,1'),
            dict(name='job1', result='SUCCESS', changes='1,1 2,1'),
            dict(name='job2', result='SUCCESS', changes='1,1 2,1'),
        ], ordered=False)

    @simple_layout('layouts/footer-message.yaml')
    def test_footer_message(self):
        "Test a pipeline's footer message is correctly added to the report."
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.executor_server.failJob('project-test1', A)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(2, len(self.smtp_messages))

        failure_msg = """\
Build failed.  For information on how to proceed, see \
http://wiki.example.org/Test_Failures"""

        footer_msg = """\
For CI problems and help debugging, contact ci@example.org"""

        self.assertTrue(self.smtp_messages[0]['body'].startswith(failure_msg))
        self.assertTrue(self.smtp_messages[0]['body'].endswith(footer_msg))
        self.assertFalse(self.smtp_messages[1]['body'].startswith(failure_msg))
        self.assertTrue(self.smtp_messages[1]['body'].endswith(footer_msg))

    @simple_layout('layouts/start-message.yaml')
    def test_start_message(self):
        "Test a pipeline's start message is correctly added to the report."
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(1, len(self.smtp_messages))
        start_msg = "Jobs started in gate for 1,1."
        self.assertTrue(self.smtp_messages[0]['body'].startswith(start_msg))

    @simple_layout('layouts/unmanaged-project.yaml')
    def test_unmanaged_project_start_message(self):
        "Test start reporting is not done for unmanaged projects."
        self.init_repo("org/project", tag='init')
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(0, len(A.messages))

    @simple_layout('layouts/merge-failure.yaml')
    def test_merge_failure_reporters(self):
        """Check that the config is set up correctly"""

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertEqual(
            "Merge Failed.\n\nThis change or one of its cross-repo "
            "dependencies was unable to be automatically merged with the "
            "current state of its repository. Please rebase the change and "
            "upload a new patchset.",
            tenant.layout.pipelines['check'].merge_failure_message)
        self.assertEqual(
            "The merge failed! For more information...",
            tenant.layout.pipelines['gate'].merge_failure_message)

        self.assertEqual(
            len(tenant.layout.pipelines['check'].merge_failure_actions), 1)
        self.assertEqual(
            len(tenant.layout.pipelines['gate'].merge_failure_actions), 2)

        self.assertTrue(isinstance(
            tenant.layout.pipelines['check'].merge_failure_actions[0],
            gerritreporter.GerritReporter))

        self.assertTrue(
            (
                isinstance(tenant.layout.pipelines['gate'].
                           merge_failure_actions[0],
                           zuul.driver.smtp.smtpreporter.SMTPReporter) and
                isinstance(tenant.layout.pipelines['gate'].
                           merge_failure_actions[1],
                           gerritreporter.GerritReporter)
            ) or (
                isinstance(tenant.layout.pipelines['gate'].
                           merge_failure_actions[0],
                           gerritreporter.GerritReporter) and
                isinstance(tenant.layout.pipelines['gate'].
                           merge_failure_actions[1],
                           zuul.driver.smtp.smtpreporter.SMTPReporter)
            )
        )

    @skip("Disabled for early v3 development")
    def test_merge_failure_reports(self):
        """Check that when a change fails to merge the correct message is sent
        to the correct reporter"""
        self.updateConfigLayout(
            'tests/fixtures/layout-merge-failure.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.registerJobs()

        # Check a test failure isn't reported to SMTP
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.executor_server.failJob('project-test1', A)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(3, len(self.history))  # 3 jobs
        self.assertEqual(0, len(self.smtp_messages))

        # Check a merge failure is reported to SMTP
        # B should be merged, but C will conflict with B
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        B.addPatchset(['conflict'])
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        C.addPatchset(['conflict'])
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(6, len(self.history))  # A and B jobs
        self.assertEqual(1, len(self.smtp_messages))
        self.assertEqual('The merge failed! For more information...',
                         self.smtp_messages[0]['body'])

    @skip("Disabled for early v3 development")
    def test_default_merge_failure_reports(self):
        """Check that the default merge failure reports are correct."""

        # A should report success, B should report merge failure.
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addPatchset(['conflict'])
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        B.addPatchset(['conflict'])
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(3, len(self.history))  # A jobs
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(B.data['status'], 'NEW')
        self.assertIn('Build succeeded', A.messages[1])
        self.assertIn('Merge Failed', B.messages[1])
        self.assertIn('automatically merged', B.messages[1])
        self.assertNotIn('logs.example.com', B.messages[1])
        self.assertNotIn('SKIPPED', B.messages[1])

    def test_client_get_running_jobs(self):
        "Test that the RPC client can get a list of running jobs"
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        # Wait for executor server to send the initial workData back to zuul
        start = time.time()
        while True:
            if time.time() - start > 10:
                raise Exception("Timeout waiting for gearman server to report "
                                + "back to the client")
            build = list(self.getCurrentBuilds())[0]
            # TODO (felix): If we don't want to look up the builds from the
            # pipelines/queues, we could use a DataWatch to listen for
            # BuildStatus events (which set the worker info). However, this
            # solution might not be as straight forward and more error prone
            # due to the nature of watches.
            if build.start_time:
                break
            else:
                time.sleep(0)

        running_items = client.get_running_jobs()

        self.assertEqual(1, len(running_items))
        running_item = running_items[0]
        self.assertEqual([], running_item['failing_reasons'])
        self.assertEqual([], running_item['items_behind'])
        self.assertEqual('https://review.example.com/1', running_item['url'])
        self.assertIsNone(running_item['item_ahead'])
        self.assertEqual('org/project', running_item['project'])
        self.assertIsNone(running_item['remaining_time'])
        self.assertEqual(True, running_item['active'])
        self.assertEqual('1,1', running_item['id'])

        self.assertEqual(3, len(running_item['jobs']))
        for job in running_item['jobs']:
            if job['name'] == 'project-merge':
                self.assertEqual('project-merge', job['name'])
                self.assertEqual('gate', job['pipeline'])
                self.assertEqual(False, job['retry'])
                self.assertEqual(
                    'stream/{uuid}?logfile=console.log'
                    .format(uuid=job['uuid']), job['url'])
                self.assertEqual(
                    'finger://{hostname}/{uuid}'.format(
                        hostname=self.executor_server.hostname,
                        uuid=job['uuid']),
                    job['finger_url'])
                self.assertEqual(False, job['canceled'])
                self.assertEqual(True, job['voting'])
                self.assertIsNone(job['result'])
                self.assertEqual('gate', job['pipeline'])
                break

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        running_items = client.get_running_jobs()
        self.assertEqual(0, len(running_items))

    @simple_layout('layouts/nonvoting-pipeline.yaml')
    def test_nonvoting_pipeline(self):
        "Test that a nonvoting pipeline (experimental) can still report"

        A = self.fake_gerrit.addFakeChange('org/experimental-project',
                                           'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(
            self.getJobFromHistory('experimental-project-test').result,
            'SUCCESS')
        self.assertEqual(A.reported, 1)

    @simple_layout('layouts/disable_at.yaml')
    def test_disable_at(self):
        "Test a pipeline will only report to the disabled trigger when failing"

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertEqual(3, tenant.layout.pipelines['check'].disable_at)
        self.assertEqual(
            0, tenant.layout.pipelines['check'].state.consecutive_failures)
        self.assertFalse(tenant.layout.pipelines['check'].state.disabled)

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        D = self.fake_gerrit.addFakeChange('org/project', 'master', 'D')
        E = self.fake_gerrit.addFakeChange('org/project', 'master', 'E')
        F = self.fake_gerrit.addFakeChange('org/project', 'master', 'F')
        G = self.fake_gerrit.addFakeChange('org/project', 'master', 'G')
        H = self.fake_gerrit.addFakeChange('org/project', 'master', 'H')
        I = self.fake_gerrit.addFakeChange('org/project', 'master', 'I')
        J = self.fake_gerrit.addFakeChange('org/project', 'master', 'J')
        K = self.fake_gerrit.addFakeChange('org/project', 'master', 'K')

        self.executor_server.failJob('project-test1', A)
        self.executor_server.failJob('project-test1', B)
        # Let C pass, resetting the counter
        self.executor_server.failJob('project-test1', D)
        self.executor_server.failJob('project-test1', E)
        self.executor_server.failJob('project-test1', F)
        self.executor_server.failJob('project-test1', G)
        self.executor_server.failJob('project-test1', H)
        # I also passes but should only report to the disabled reporters
        self.executor_server.failJob('project-test1', J)
        self.executor_server.failJob('project-test1', K)

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(
            2, tenant.layout.pipelines['check'].state.consecutive_failures)
        self.assertFalse(tenant.layout.pipelines['check'].state.disabled)

        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(
            0, tenant.layout.pipelines['check'].state.consecutive_failures)
        self.assertFalse(tenant.layout.pipelines['check'].state.disabled)

        self.fake_gerrit.addEvent(D.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(E.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(F.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # We should be disabled now
        self.assertEqual(
            3, tenant.layout.pipelines['check'].state.consecutive_failures)
        self.assertTrue(tenant.layout.pipelines['check'].state.disabled)

        # We need to wait between each of these patches to make sure the
        # smtp messages come back in an expected order
        self.fake_gerrit.addEvent(G.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(H.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(I.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # The first 6 (ABCDEF) jobs should have reported back to gerrt thus
        # leaving a message on each change
        self.assertEqual(1, len(A.messages))
        self.assertIn('Build failed.', A.messages[0])
        self.assertEqual(1, len(B.messages))
        self.assertIn('Build failed.', B.messages[0])
        self.assertEqual(1, len(C.messages))
        self.assertIn('Build succeeded.', C.messages[0])
        self.assertEqual(1, len(D.messages))
        self.assertIn('Build failed.', D.messages[0])
        self.assertEqual(1, len(E.messages))
        self.assertIn('Build failed.', E.messages[0])
        self.assertEqual(1, len(F.messages))
        self.assertIn('Build failed.', F.messages[0])

        # The last 3 (GHI) would have only reported via smtp.
        self.assertEqual(3, len(self.smtp_messages))
        self.assertEqual(0, len(G.messages))
        self.assertIn('Build failed.', self.smtp_messages[0]['body'])
        self.assertIn(
            'project-test1 https://', self.smtp_messages[0]['body'])
        self.assertEqual(0, len(H.messages))
        self.assertIn('Build failed.', self.smtp_messages[1]['body'])
        self.assertIn(
            'project-test1 https://', self.smtp_messages[1]['body'])
        self.assertEqual(0, len(I.messages))
        self.assertIn('Build succeeded.', self.smtp_messages[2]['body'])
        self.assertIn(
            'project-test1 https://', self.smtp_messages[2]['body'])

        # Now reload the configuration (simulate a HUP) to check the pipeline
        # comes out of disabled
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')

        self.assertEqual(3, tenant.layout.pipelines['check'].disable_at)
        self.assertEqual(
            0, tenant.layout.pipelines['check'].state.consecutive_failures)
        self.assertFalse(tenant.layout.pipelines['check'].state.disabled)

        self.fake_gerrit.addEvent(J.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(K.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(
            2, tenant.layout.pipelines['check'].state.consecutive_failures)
        self.assertFalse(tenant.layout.pipelines['check'].state.disabled)

        # J and K went back to gerrit
        self.assertEqual(1, len(J.messages))
        self.assertIn('Build failed.', J.messages[0])
        self.assertEqual(1, len(K.messages))
        self.assertIn('Build failed.', K.messages[0])
        # No more messages reported via smtp
        self.assertEqual(3, len(self.smtp_messages))

    @simple_layout('layouts/one-job-project.yaml')
    def test_one_job_project(self):
        "Test that queueing works with one job"
        A = self.fake_gerrit.addFakeChange('org/one-job-project',
                                           'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/one-job-project',
                                           'master', 'B')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(B.reported, 2)

    def test_job_aborted(self):
        "Test that if a execute server aborts a job, it is run again"
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 2)

        # first abort
        self.builds[0].aborted = True
        self.executor_server.release('.*-test*')
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 1)

        # second abort
        self.builds[0].aborted = True
        self.executor_server.release('.*-test*')
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 1)

        # third abort
        self.builds[0].aborted = True
        self.executor_server.release('.*-test*')
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 1)

        # fourth abort
        self.builds[0].aborted = True
        self.executor_server.release('.*-test*')
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 1)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.history), 7)
        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 4)
        self.assertEqual(self.countJobResults(self.history, 'SUCCESS'), 3)

    def test_rerun_on_abort(self):
        "Test that if a execute server fails to run a job, it is run again"

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 2)
        self.builds[0].requeue = True
        self.executor_server.release('.*-test*')
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        items = tenant.layout.pipelines['check'].getAllItems()
        build_set = items[0].current_build_set

        for x in range(3):
            # We should have x+1 retried builds for project-test1
            retry_builds = build_set.getRetryBuildsForJob('project-test1')
            self.assertEqual(len(retry_builds), x + 1)
            for build in retry_builds:
                self.assertEqual(build.retry, True)
                self.assertEqual(build.result, 'RETRY')

            self.assertEqual(len(self.builds), 1,
                             'len of builds at x=%d is wrong' % x)
            self.builds[0].requeue = True
            self.executor_server.release('.*-test1')
            self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        self.assertEqual(len(self.history), 6)
        self.assertEqual(self.countJobResults(self.history, 'SUCCESS'), 2)
        self.assertEqual(A.reported, 1)
        self.assertIn('RETRY_LIMIT', A.messages[0])

    def test_executor_disconnect(self):
        "Test that jobs are completed after an executor disconnect"

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        # Forcibly disconnect the executor from ZK
        self.executor_server.zk_client.client.stop()
        self.executor_server.zk_client.client.start()

        # Find the build in the scheduler so we can check its status
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        items = tenant.layout.pipelines['gate'].getAllItems()
        builds = items[0].current_build_set.getBuilds()
        build = builds[0]

        # Clean up the build
        self.scheds.first.sched.executor.cleanupLostBuildRequests()
        # Wait for the build to be reported as lost
        for x in iterate_timeout(30, 'retry build'):
            if build.result == 'RETRY':
                break

        # If we didn't timeout, then it worked; we're done
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        # There is a test-only race in the recording executor class
        # where we may record a successful first build, even though
        # the executor didn't actually send a build complete event.
        # This could probabyl be improved, but for now, it's
        # sufficient to verify that the job was retried.  So we omit a
        # result classifier on the first build.
        self.assertHistory([
            dict(name='project-merge', changes='1,1'),
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
        ], ordered=False)

    # TODO: There seems to be a race condition in the kazoo election
    # recipe that can cause the stats election thread to hang after
    # reconnecting.
    @skip("This is unstable in the gate")
    def test_scheduler_disconnect(self):
        "Test that jobs are completed after a scheduler disconnect"

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        # Forcibly disconnect the scheduler from ZK
        self.scheds.execute(lambda app: app.sched.zk_client.client.stop())
        self.scheds.execute(lambda app: app.sched.zk_client.client.start())

        # Clean up lost builds
        self.scheds.first.sched.executor.cleanupLostBuildRequests()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
        ], ordered=False)

    # TODO: See comment for test_scheduler_disconnect.
    @skip("This is unstable in the gate")
    def test_zookeeper_disconnect(self):
        "Test that jobs are executed after a zookeeper disconnect"

        self.fake_nodepool.pause()
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.scheds.execute(lambda app: app.sched.zk_client.client.stop())
        self.scheds.execute(lambda app: app.sched.zk_client.client.start())
        self.fake_nodepool.unpause()
        # Wait until we win the nodepool election in order to avoid a
        # race in waitUntilSettled with the request being fulfilled
        # without submitting an event.
        for x in iterate_timeout(60, 'nodepool election won'):
            found = [app for app in self.scheds
                     if (app.sched.nodepool.election_won and
                         app.sched.nodepool.election.is_still_valid())]
            if found:
                break
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)

    def test_nodepool_cleanup(self):
        "Test that we cleanup leaked node requests"
        self.fake_nodepool.pause()
        system_id = self.scheds.first.sched.system.system_id
        zk_nodepool = self.scheds.first.sched.nodepool.zk_nodepool
        req1 = zuul.model.NodeRequest(system_id, "uuid1", "tenant",
                                      "pipeline", "job", ['label'], None,
                                      0, None)
        zk_nodepool.submitNodeRequest(req1, 100)
        req2 = zuul.model.NodeRequest("someone else", "uuid1", "tenant",
                                      "pipeline", "job", ['label'], None,
                                      0, None)
        zk_nodepool.submitNodeRequest(req2, 100)
        self.assertEqual(zk_nodepool.getNodeRequests(),
                         ['100-0000000000', '100-0000000001'])
        self.scheds.first.sched._runNodeRequestCleanup()
        self.assertEqual(zk_nodepool.getNodeRequests(),
                         ['100-0000000001'])
        zk_nodepool.deleteNodeRequest(req2.id)

    def test_nodepool_failure(self):
        "Test that jobs are reported after a nodepool failure"

        self.fake_nodepool.pause()
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        req = self.fake_nodepool.getNodeRequests()[0]
        self.fake_nodepool.addFailRequest(req)

        self.fake_nodepool.unpause()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(A.reported, 2)
        self.assertTrue(re.search('project-merge .* NODE_FAILURE',
                                  A.messages[1]))
        self.assertTrue(re.search('project-test1 .* SKIPPED', A.messages[1]))
        self.assertTrue(re.search('project-test2 .* SKIPPED', A.messages[1]))

    def test_nodepool_resources(self):
        "Test that resources are reported"

        self.executor_server.hold_jobs_in_build = True
        self.fake_nodepool.resources = {
            'cores': 2,
            'ram': 1024,
            'instances': 1,
        }
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.executor_server.release('project-merge')
        self.waitUntilSettled()
        self.waitUntilNodeCacheSync(
            self.scheds.first.sched.nodepool.zk_nodepool)
        self.scheds.first.sched._runStats()

        # Check that resource usage gauges are reported
        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
        ])
        # All 3 nodes are in use
        self.assertReportedStat(
            'zuul.nodepool.resources.tenant.tenant-one.cores',
            value='6', kind='g')
        self.assertReportedStat(
            'zuul.nodepool.resources.tenant.tenant-one.ram',
            value='3072', kind='g')
        self.assertReportedStat(
            'zuul.nodepool.resources.tenant.tenant-one.instances',
            value='3', kind='g')
        self.assertReportedStat(
            'zuul.nodepool.resources.project.review_example_com/org/project.'
            'cores', value='6', kind='g')
        self.assertReportedStat(
            'zuul.nodepool.resources.project.review_example_com/org/project.'
            'ram', value='3072', kind='g')
        self.assertReportedStat(
            'zuul.nodepool.resources.project.review_example_com/org/project.'
            'instances', value='3', kind='g')

        # Check that resource usage counters are reported
        self.assertReportedStat(
            'zuul.nodepool.resources.tenant.tenant-one.cores',
            kind='c')
        self.assertReportedStat(
            'zuul.nodepool.resources.tenant.tenant-one.ram',
            kind='c')
        self.assertReportedStat(
            'zuul.nodepool.resources.tenant.tenant-one.instances',
            kind='c')
        self.assertReportedStat(
            'zuul.nodepool.resources.project.review_example_com/org/project.'
            'cores', kind='c')
        self.assertReportedStat(
            'zuul.nodepool.resources.project.review_example_com/org/project.'
            'ram', kind='c')
        self.assertReportedStat(
            'zuul.nodepool.resources.project.review_example_com/org/project.'
            'instances', kind='c')

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)

    def test_nodepool_pipeline_priority(self):
        "Test that nodes are requested at the correct pipeline priority"

        self.fake_nodepool.pause()

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getRefUpdatedEvent())
        self.waitUntilSettled()

        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        C.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        reqs = self.fake_nodepool.getNodeRequests()

        # The requests come back sorted by priority. Since we have
        # three requests for the three changes each with a different
        # priority.  Also they get a serial number based on order they
        # were received so the number on the endof the oid should map
        # to order submitted.

        # * gate first - high priority - change C
        self.assertEqual(reqs[0]['_oid'], '100-0000000002')
        self.assertEqual(reqs[0]['node_types'], ['label1'])
        # * check second - normal priority - change B
        self.assertEqual(reqs[1]['_oid'], '200-0000000001')
        self.assertEqual(reqs[1]['node_types'], ['label1'])
        # * post third - low priority - change A
        # additionally, the post job defined uses an ubuntu-xenial node,
        # so we include that check just as an extra verification
        self.assertEqual(reqs[2]['_oid'], '300-0000000000')
        self.assertEqual(reqs[2]['node_types'], ['ubuntu-xenial'])

        self.fake_nodepool.unpause()
        self.waitUntilSettled()

    @simple_layout('layouts/two-projects-integrated.yaml')
    def test_nodepool_relative_priority_check(self):
        "Test that nodes are requested at the relative priority"

        self.fake_nodepool.pause()

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        C = self.fake_gerrit.addFakeChange('org/project1', 'master', 'C')
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        D = self.fake_gerrit.addFakeChange('org/project2', 'master', 'D')
        self.fake_gerrit.addEvent(D.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        reqs = self.fake_nodepool.getNodeRequests()

        # The requests come back sorted by priority.

        # Change A, first change for project, high relative priority.
        self.assertEqual(reqs[0]['_oid'], '200-0000000000')
        self.assertEqual(reqs[0]['relative_priority'], 0)

        # Change C, first change for project1, high relative priority.
        self.assertEqual(reqs[1]['_oid'], '200-0000000002')
        self.assertEqual(reqs[1]['relative_priority'], 0)

        # Change B, second change for project, lower relative priority.
        self.assertEqual(reqs[2]['_oid'], '200-0000000001')
        self.assertEqual(reqs[2]['relative_priority'], 1)

        # Change D, first change for project2 shared with project1,
        # lower relative priority than project1.
        self.assertEqual(reqs[3]['_oid'], '200-0000000003')
        self.assertEqual(reqs[3]['relative_priority'], 1)

        # Fulfill only the first request
        self.fake_nodepool.fulfillRequest(reqs[0])
        for x in iterate_timeout(30, 'fulfill request'):
            reqs = list(self.scheds.first.sched.nodepool.getNodeRequests())
            if len(reqs) < 4:
                break
        self.waitUntilSettled()

        reqs = self.fake_nodepool.getNodeRequests()

        # Change B, now first change for project, equal priority.
        self.assertEqual(reqs[0]['_oid'], '200-0000000001')
        self.assertEqual(reqs[0]['relative_priority'], 0)

        # Change C, now first change for project1, equal priority.
        self.assertEqual(reqs[1]['_oid'], '200-0000000002')
        self.assertEqual(reqs[1]['relative_priority'], 0)

        # Change D, first change for project2 shared with project1,
        # still lower relative priority than project1.
        self.assertEqual(reqs[2]['_oid'], '200-0000000003')
        self.assertEqual(reqs[2]['relative_priority'], 1)

        self.fake_nodepool.unpause()
        self.waitUntilSettled()

    @simple_layout('layouts/two-projects-integrated.yaml')
    def test_nodepool_relative_priority_long(self):
        "Test that nodes are requested at the relative priority"

        self.fake_nodepool.pause()

        count = 13
        changes = []
        for x in range(count):
            change = self.fake_gerrit.addFakeChange(
                'org/project', 'master', 'A')
            self.fake_gerrit.addEvent(change.getPatchsetCreatedEvent(1))
            self.waitUntilSettled()
            changes.append(change)

        reqs = self.fake_nodepool.getNodeRequests()
        self.assertEqual(len(reqs), 13)
        # The requests come back sorted by priority.
        for x in range(10):
            self.assertEqual(reqs[x]['relative_priority'], x)
        self.assertEqual(reqs[10]['relative_priority'], 10)
        self.assertEqual(reqs[11]['relative_priority'], 10)
        self.assertEqual(reqs[12]['relative_priority'], 10)

        # Fulfill only the first request
        self.fake_nodepool.fulfillRequest(reqs[0])
        for x in iterate_timeout(30, 'fulfill request'):
            reqs = list(self.scheds.first.sched.nodepool.getNodeRequests())
            if len(reqs) < count:
                break
        self.waitUntilSettled()

        reqs = self.fake_nodepool.getNodeRequests()
        self.assertEqual(len(reqs), 12)
        for x in range(10):
            self.assertEqual(reqs[x]['relative_priority'], x)
        self.assertEqual(reqs[10]['relative_priority'], 10)
        self.assertEqual(reqs[11]['relative_priority'], 10)

        self.fake_nodepool.unpause()
        self.waitUntilSettled()

    @simple_layout('layouts/two-projects-integrated.yaml')
    def test_nodepool_relative_priority_gate(self):
        "Test that nodes are requested at the relative priority"

        self.fake_nodepool.pause()

        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        B = self.fake_gerrit.addFakeChange('org/project2', 'master', 'B')
        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        # project does not share a queue with project1 and project2.
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        C.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        reqs = self.fake_nodepool.getNodeRequests()

        # The requests come back sorted by priority.

        # Change A, first change for shared queue, high relative
        # priority.
        self.assertEqual(reqs[0]['_oid'], '100-0000000000')
        self.assertEqual(reqs[0]['relative_priority'], 0)

        # Change C, first change for independent project, high
        # relative priority.
        self.assertEqual(reqs[1]['_oid'], '100-0000000002')
        self.assertEqual(reqs[1]['relative_priority'], 0)

        # Change B, second change for shared queue, lower relative
        # priority.
        self.assertEqual(reqs[2]['_oid'], '100-0000000001')
        self.assertEqual(reqs[2]['relative_priority'], 1)

        self.fake_nodepool.unpause()
        self.waitUntilSettled()

    def test_nodepool_project_removal(self):
        "Test that nodes are returned unused after project removal"

        self.fake_nodepool.pause()
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.newTenantConfig('config/single-tenant/main-one-project.yaml')
        # This layout defines only org/project, not org/project1
        self.commitConfigUpdate(
            'common-config',
            'layouts/live-reconfiguration-del-project.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        self.fake_nodepool.unpause()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(A.reported, 0)
        for node in self.fake_nodepool.getNodes():
            self.assertFalse(node['_lock'])
            self.assertEqual(node['state'], 'ready')

    @simple_layout('layouts/multiple-templates.yaml')
    def test_multiple_project_templates(self):
        # Test that applying multiple project templates to a project
        # doesn't alter them when used for a second project.
        A = self.fake_gerrit.addFakeChange('org/project2', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        build = self.getJobFromHistory('py27')
        self.assertEqual(build.parameters['zuul']['jobtags'], [])

    def test_pending_merge_in_reconfig(self):
        # Test that if we are waiting for an outstanding merge on
        # reconfiguration that we continue to do so.
        self.hold_merge_jobs_in_queue = True
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        A.setMerged()
        self.fake_gerrit.addEvent(A.getRefUpdatedEvent())
        self.waitUntilSettled()

        jobs = list(self.merger_api.all())
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].state, zuul.model.MergeRequest.HOLD)

        # Reconfigure while we still have an outstanding merge job
        self.hold_merge_jobs_in_queue = False
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        (trusted, project1) = tenant.getProject('org/project1')
        self.scheds.first.sched.reconfigureTenant(
            self.scheds.first.sched.abide.tenants['tenant-one'],
            project1, None)
        self.waitUntilSettled()

        # Verify the merge job is still running and that the item is
        # in the pipeline
        jobs = list(self.merger_api.all())
        self.assertEqual(jobs[0].state, zuul.model.MergeRequest.HOLD)
        self.assertEqual(len(jobs), 1)

        pipeline = tenant.layout.pipelines['post']
        self.assertEqual(len(pipeline.getAllItems()), 1)
        self.merger_api.release()
        self.waitUntilSettled()

        jobs = list(self.merger_api.all())
        self.assertEqual(len(jobs), 0)

    @simple_layout('layouts/parent-matchers.yaml')
    def test_parent_matchers(self):
        "Test that if a job's parent does not match, the job does not run"
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertHistory([])

        files = {'foo.txt': ''}
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B',
                                           files=files)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        files = {'bar.txt': ''}
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C',
                                           files=files)
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        files = {'foo.txt': '', 'bar.txt': ''}
        D = self.fake_gerrit.addFakeChange('org/project', 'master', 'D',
                                           files=files)
        self.fake_gerrit.addEvent(D.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='child-job', result='SUCCESS', changes='3,1'),
            dict(name='child-job', result='SUCCESS', changes='4,1'),
        ], ordered=False)

    @simple_layout('layouts/file-matchers.yaml')
    def test_file_matchers(self):
        "Test several file matchers"
        files = {'parent1.txt': ''}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=files)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        files = {'parent2.txt': ''}
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B',
                                           files=files)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        files = {'child.txt': ''}
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C',
                                           files=files)
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        files = {'project.txt': ''}
        D = self.fake_gerrit.addFakeChange('org/project', 'master', 'D',
                                           files=files)
        self.fake_gerrit.addEvent(D.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        files = {'tests/foo': ''}
        E = self.fake_gerrit.addFakeChange('org/project', 'master', 'E',
                                           files=files)
        self.fake_gerrit.addEvent(E.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        files = {'tests/docs/foo': ''}
        F = self.fake_gerrit.addFakeChange('org/project', 'master', 'F',
                                           files=files)
        self.fake_gerrit.addEvent(F.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='child-job', result='SUCCESS', changes='2,1'),

            dict(name='child-override-job', result='SUCCESS', changes='3,1'),

            dict(name='project-override-job', result='SUCCESS', changes='4,1'),

            dict(name='irr-job', result='SUCCESS', changes='5,1'),
            dict(name='irr-override-job', result='SUCCESS', changes='5,1'),

            dict(name='irr-job', result='SUCCESS', changes='6,1'),
        ], ordered=False)

    def test_trusted_project_dep_on_non_live_untrusted_project(self):
        # Test we get a layout for trusted projects when they depend on
        # non live untrusted projects. This checks against a bug where
        # trusted project config changes can end up in a infinite loop
        # trying to find the right layout.
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        files = {'zuul.yaml': ''}
        B = self.fake_gerrit.addFakeChange('common-config', 'master', 'B',
                                           files=files)
        B.setDependsOn(A, 1)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project1-project2-integration',
                 result='SUCCESS', changes='1,1 2,1'),
        ], ordered=False)

    @simple_layout('layouts/success-message.yaml')
    def test_success_message(self):
        # Test the success_message (and failure_message) job attrs
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        self.executor_server.failJob('badjob', A)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertEqual(len(A.messages), 1)
        self.assertTrue('YAY' in A.messages[0])
        self.assertTrue('BOO' in A.messages[0])

    def test_merge_error(self):
        # Test we don't get stuck on a merger error
        self.waitUntilSettled()
        self.patch(zuul.merger.merger.Repo, 'retry_attempts', 1)

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.patch(git.Git, 'GIT_PYTHON_GIT_EXECUTABLE',
                   os.path.join(FIXTURE_DIR, 'git_fail.sh'))
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

    @simple_layout('layouts/vars.yaml')
    def test_jobdata(self):
        # Test the use of JobData objects for job variables
        self.executor_server.hold_jobs_in_build = True

        self.useFixture(fixtures.MonkeyPatch(
            'zuul.model.FrozenJob.MAX_DATA_LEN',
            1))

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # Make sure we're really using JobData objects
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        item = tenant.layout.pipelines['check'].queues[0].queue[0]
        job = item.getJobs()[0]
        self.assertTrue(isinstance(job._variables, zuul.model.JobData))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='check-job', result='SUCCESS', changes='1,1'),
        ], ordered=False)


class TestChangeQueues(ZuulTestCase):
    tenant_config_file = 'config/change-queues/main.yaml'

    def _test_dependent_queues_per_branch(self, project,
                                          queue_name='integrated',
                                          queue_repo='common-config'):
        self.create_branch(project, 'stable')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(project, 'stable'))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange(project, 'master', 'A')
        B = self.fake_gerrit.addFakeChange(project, 'stable', 'B')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)

        self.executor_server.failJob('project-test', A)

        # Let first go A into gate then B
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        # There should be one project-test job at the head of each queue
        self.assertBuilds([
            dict(name='project-test', changes='1,1'),
            dict(name='project-test', changes='2,1'),
        ])
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        _, p = tenant.getProject(project)
        q1 = tenant.layout.pipelines['gate'].getQueue(
            p.canonical_name, 'master')
        q2 = tenant.layout.pipelines['gate'].getQueue(
            p.canonical_name, 'stable')
        self.assertEqual(q1.name, queue_name)
        self.assertEqual(q2.name, queue_name)

        # Both queues must contain one item
        self.assertEqual(len(q1.queue), 1)
        self.assertEqual(len(q2.queue), 1)

        # Fail job on the change on master
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertNotEqual(A.data['status'], 'MERGED')
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)

        # Now reconfigure the queue to be non-branched and run the same test
        # again.
        conf = textwrap.dedent(
            """
            - queue:
                name: {}
                per-branch: false
            """).format(queue_name)

        file_dict = {'zuul.d/queue.yaml': conf}
        C = self.fake_gerrit.addFakeChange(queue_repo, 'master', 'A',
                                           files=file_dict)
        C.setMerged()
        self.fake_gerrit.addEvent(C.getChangeMergedEvent())
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = True
        D = self.fake_gerrit.addFakeChange(project, 'master', 'D')
        E = self.fake_gerrit.addFakeChange(project, 'stable', 'E')
        D.addApproval('Code-Review', 2)
        E.addApproval('Code-Review', 2)

        self.executor_server.failJob('project-test', D)

        # Let first go A into gate then B
        self.fake_gerrit.addEvent(D.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.fake_gerrit.addEvent(E.addApproval('Approved', 1))
        self.waitUntilSettled()

        # There should be two project-test jobs in a shared queue
        self.assertBuilds([
            dict(name='project-test', changes='4,1'),
            dict(name='project-test', changes='4,1 5,1'),
        ])
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        _, p = tenant.getProject(project)
        q1 = tenant.layout.pipelines['gate'].getQueue(
            p.canonical_name, 'master')
        q2 = tenant.layout.pipelines['gate'].getQueue(
            p.canonical_name, 'stable')
        q3 = tenant.layout.pipelines['gate'].getQueue(
            p.canonical_name, None)

        # There should be no branch specific queues anymore
        self.assertEqual(q1, None)
        self.assertEqual(q2, None)
        self.assertEqual(q3.name, queue_name)

        # Both queues must contain one item
        self.assertEqual(len(q3.queue), 2)

        # Release project-test of D to make history after test deterministic
        self.executor_server.release('project-test', change='4 1')
        self.waitUntilSettled()

        # Fail job on the change on master
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertNotEqual(D.data['status'], 'MERGED')
        self.assertEqual(E.data['status'], 'MERGED')
        self.assertEqual(D.reported, 2)
        self.assertEqual(E.reported, 2)

        self.assertHistory([
            # Independent runs because of per branch queues
            dict(name='project-test', result='FAILURE', changes='1,1'),
            dict(name='project-test', result='SUCCESS', changes='2,1'),

            # Same queue with gate reset because of 4,1
            dict(name='project-test', result='FAILURE', changes='4,1'),

            # Result can be anything depending on timing of the gate reset.
            dict(name='project-test', changes='4,1 5,1'),
            dict(name='project-test', result='SUCCESS', changes='5,1'),
        ], ordered=False)

    def test_dependent_queues_per_branch(self):
        """
        Test that change queues can be different for different branches.

        In this case the project contains zuul config so the branches are
        known upfront and the queues are pre-seeded.
        """
        self._test_dependent_queues_per_branch('org/project')

    def test_dependent_queues_per_branch_no_config(self):
        """
        Test that change queues can be different for different branches.

        In this case we create changes for two branches in a repo that
        doesn't contain zuul config so the queues are not pre-seeded
        in the gate pipeline.
        """
        self._test_dependent_queues_per_branch('org/project2')

    def test_dependent_queues_per_branch_untrusted(self):
        """
        Test that change queues can be different for different branches.

        In this case we create changes for two branches in an untrusted repo
        that defines its own queue.
        """
        self._test_dependent_queues_per_branch(
            'org/project3', queue_name='integrated-untrusted',
            queue_repo='org/project3')

    def test_dependent_queues_per_branch_project_queue(self):
        """
        Test that change queues can be different for different branches.

        In this case we create changes for two branches in a repo that
        references the queue on project level instead of pipeline level.
        """
        self._test_dependent_queues_per_branch('org/project4')


class TestJobUpdateBrokenConfig(ZuulTestCase):
    tenant_config_file = 'config/job-update-broken/main.yaml'

    def test_fix_check_without_running(self):
        "Test that we can fix a broken check pipeline (don't run the job)"
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: existing-files
                files:
                  - README.txt

            - project-template:
                name: files-template
                check:
                  jobs:
                    - existing-files
                    - noop
            """)

        # When the config is broken, we don't override any files
        # matchers since we don't have a valid basis.  Since this
        # doesn't update README.txt, nothing should run.
        file_dict = {'zuul.d/existing.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([])
        self.assertEqual(A.reported, 1)

    def test_fix_check_with_running(self):
        "Test that we can fix a broken check pipeline (do run the job)"
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: existing-files
                files:
                  - README.txt

            - project-template:
                name: files-template
                check:
                  jobs:
                    - existing-files
            """)

        # When the config is broken, we don't override any files
        # matchers since we don't have a valid basis.  Since this
        # does update README.txt, the job should run.
        file_dict = {'zuul.d/existing.yaml': in_repo_conf,
                     'README.txt': ''}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='existing-files', result='SUCCESS', changes='1,1'),
        ])
        self.assertEqual(A.reported, 1)


class TestJobUpdateFileMatcher(ZuulTestCase):
    tenant_config_file = 'config/job-update/main.yaml'

    def test_matchers(self):
        "Test matchers work as expected with no change"
        file_dict = {'README.txt': ''}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        file_dict = {'something_else': ''}
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B',
                                           files=file_dict)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='existing-files', result='SUCCESS', changes='1,1'),
            dict(name='existing-irr', result='SUCCESS', changes='2,1'),
        ])

    def test_job_update(self):
        "Test matchers are overridden with a config update"
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: existing-files
                tags: foo
            - job:
                name: existing-irr
                tags: foo
            """)

        file_dict = {'zuul.d/new.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='existing-files', result='SUCCESS', changes='1,1'),
            dict(name='existing-irr', result='SUCCESS', changes='1,1'),
        ], ordered=False)

    def test_job_update_files(self):
        "Test that changes to file matchers themselves don't run jobs"
        # Normally we want to ignore file matchers and run jobs if the
        # job config changes, but if the only thing about the job
        # config that changes *is* the file matchers, then we don't
        # want to run it.
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: existing-files
                files: 'doesnotexist'
            - job:
                name: existing-irr
                irrelevant-files:
                  - README
                  - ^zuul.d/.*$
                  - newthing
            """)

        file_dict = {'zuul.d/new.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertHistory([])

    def test_new_job(self):
        "Test matchers are overridden when creating a new job"
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: new-files
                parent: existing-files

            - project:
                check:
                  jobs:
                    - new-files
            """)

        file_dict = {'zuul.d/new.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='new-files', result='SUCCESS', changes='1,1'),
        ])

    def test_patch_series(self):
        "Test that we diff to the nearest layout in a patch series"
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: new-files1
                parent: existing-files

            - project:
                check:
                  jobs:
                    - new-files1
            """)

        file_dict = {'zuul.d/new1.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)

        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: new-files2
                parent: existing-files

            - project:
                check:
                  jobs:
                    - new-files2
            """)

        file_dict = {'zuul.d/new2.yaml': in_repo_conf}
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B',
                                           files=file_dict)
        B.setDependsOn(A, 1)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='new-files2', result='SUCCESS', changes='1,1 2,1'),
        ])

    def test_disable_match(self):
        "Test matchers are not overridden if we say so"
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: new-files
                parent: existing-files
                match-on-config-updates: false

            - project:
                check:
                  jobs:
                    - new-files
            """)

        file_dict = {'zuul.d/new.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([])


class TestAmbiguousProjectNames(ZuulTestCase):
    config_file = 'zuul-connections-multiple-gerrits.conf'
    tenant_config_file = 'config/ambiguous-names/main.yaml'

    def test_client_enqueue_canonical(self):
        "Test that the RPC client can enqueue a change using canonical name"
        A = self.fake_review_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        A.addApproval('Approved', 1)

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.enqueue(tenant='tenant-one',
                           pipeline='check',
                           project='review.example.com/org/project',
                           trigger=None,
                           change='1,1')
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('project-merge').result,
                         'SUCCESS')
        self.assertEqual(r, True)

    def test_client_enqueue_ref_canonical(self):
        "Test that the RPC client can enqueue a ref using canonical name"
        p = "review.example.com/org/project"
        upstream = self.getUpstreamRepos([p])
        A = self.fake_review_gerrit.addFakeChange('org/project', 'master', 'A')
        A.setMerged()
        A_commit = str(upstream[p].commit('master'))
        self.log.debug("A commit: %s" % A_commit)

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.enqueue_ref(
            tenant='tenant-one',
            pipeline='post',
            project='review.example.com/org/project',
            trigger=None,
            ref='master',
            oldrev='90f173846e3af9154517b88543ffbd1691f31366',
            newrev=A_commit)
        self.waitUntilSettled()
        job_names = [x.name for x in self.history]
        self.assertEqual(len(self.history), 1)
        self.assertIn('project-post', job_names)
        self.assertEqual(r, True)


class TestExecutor(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def assertFinalState(self):
        # In this test, we expect to shut down in a non-final state,
        # so skip these checks.
        pass

    def assertCleanShutdown(self):
        self.log.debug("Assert clean shutdown")

        # After shutdown, make sure no jobs are running
        self.assertEqual({}, self.executor_server.job_workers)

        # Make sure that git.Repo objects have been garbage collected.
        gc.disable()
        try:
            gc.collect()
            for obj in gc.get_objects():
                if isinstance(obj, git.Repo):
                    self.log.debug("Leaked git repo object: %s" % repr(obj))
            gc.enable()
        finally:
            gc.enable()

    def test_executor_shutdown(self):
        "Test that the executor can shut down with jobs running"

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()


class TestDependencyGraph(ZuulTestCase):
    tenant_config_file = 'config/dependency-graph/main.yaml'

    def test_dependeny_graph_dispatch_jobs_once(self):
        "Test a job in a dependency graph is queued only once"
        # Job dependencies, starting with A
        #     A
        #    / \
        #   B   C
        #  / \ / \
        # D   F   E
        #     |
        #     G

        self.executor_server.hold_jobs_in_build = True
        change = self.fake_gerrit.addFakeChange(
            'org/project', 'master', 'change')
        change.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(change.addApproval('Approved', 1))

        self.waitUntilSettled()
        self.assertEqual([b.name for b in self.builds], ['A'])

        self.executor_server.release('A')
        self.waitUntilSettled()
        self.assertEqual(sorted(b.name for b in self.builds), ['B', 'C'])

        self.executor_server.release('B')
        self.waitUntilSettled()
        self.assertEqual(sorted(b.name for b in self.builds), ['C', 'D'])

        self.executor_server.release('D')
        self.waitUntilSettled()
        self.assertEqual([b.name for b in self.builds], ['C'])

        self.executor_server.release('C')
        self.waitUntilSettled()
        self.assertEqual(sorted(b.name for b in self.builds), ['E', 'F'])

        self.executor_server.release('F')
        self.waitUntilSettled()
        self.assertEqual(sorted(b.name for b in self.builds), ['E', 'G'])

        self.executor_server.release('G')
        self.waitUntilSettled()
        self.assertEqual([b.name for b in self.builds], ['E'])

        self.executor_server.release('E')
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 0)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)
        self.assertEqual(len(self.history), 7)

        self.assertEqual(change.data['status'], 'MERGED')
        self.assertEqual(change.reported, 2)

    def test_jobs_launched_only_if_all_dependencies_are_successful(self):
        "Test that a job waits till all dependencies are successful"
        # Job dependencies, starting with A
        #     A
        #    / \
        #   B   C*
        #  / \ / \
        # D   F   E
        #     |
        #     G

        self.executor_server.hold_jobs_in_build = True
        change = self.fake_gerrit.addFakeChange(
            'org/project', 'master', 'change')
        change.addApproval('Code-Review', 2)

        self.executor_server.failJob('C', change)

        self.fake_gerrit.addEvent(change.addApproval('Approved', 1))

        self.waitUntilSettled()
        self.assertEqual([b.name for b in self.builds], ['A'])

        self.executor_server.release('A')
        self.waitUntilSettled()
        self.assertEqual(sorted(b.name for b in self.builds), ['B', 'C'])

        self.executor_server.release('B')
        self.waitUntilSettled()
        self.assertEqual(sorted(b.name for b in self.builds), ['C', 'D'])

        self.executor_server.release('D')
        self.waitUntilSettled()
        self.assertEqual([b.name for b in self.builds], ['C'])

        self.executor_server.release('C')
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 0)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)
        self.assertEqual(len(self.history), 4)

        self.assertEqual(change.data['status'], 'NEW')
        self.assertEqual(change.reported, 2)

    @simple_layout('layouts/soft-dependencies-error.yaml')
    def test_soft_dependencies_error(self):
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([])
        self.assertEqual(len(A.messages), 1)
        self.assertTrue('Job project-merge not defined' in A.messages[0])
        self.log.info(A.messages)

    @simple_layout('layouts/soft-dependencies.yaml')
    def test_soft_dependencies(self):
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='deploy', result='SUCCESS', changes='1,1'),
        ], ordered=False)

    @simple_layout('layouts/soft-dependencies.yaml')
    def test_soft_dependencies_failure(self):
        file_dict = {'main.c': 'test'}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        self.executor_server.failJob('build', A)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='build', result='FAILURE', changes='1,1'),
        ], ordered=False)
        self.assertIn('SKIPPED', A.messages[0])


class TestDuplicatePipeline(ZuulTestCase):
    tenant_config_file = 'config/duplicate-pipeline/main.yaml'

    def test_duplicate_pipelines(self):
        "Test that a change matching multiple pipelines works"

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getChangeRestoredEvent())
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='project-test1', result='SUCCESS', changes='1,1',
                 pipeline='dup1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1',
                 pipeline='dup2'),
        ], ordered=False)

        self.assertEqual(len(A.messages), 2)

        if 'dup1' in A.messages[0]:
            self.assertIn('dup1', A.messages[0])
            self.assertNotIn('dup2', A.messages[0])
            self.assertIn('project-test1', A.messages[0])
            self.assertIn('dup2', A.messages[1])
            self.assertNotIn('dup1', A.messages[1])
            self.assertIn('project-test1', A.messages[1])
        else:
            self.assertIn('dup1', A.messages[1])
            self.assertNotIn('dup2', A.messages[1])
            self.assertIn('project-test1', A.messages[1])
            self.assertIn('dup2', A.messages[0])
            self.assertNotIn('dup1', A.messages[0])
            self.assertIn('project-test1', A.messages[0])


class TestSchedulerRegexProject(ZuulTestCase):
    tenant_config_file = 'config/regex-project/main.yaml'

    def test_regex_project(self):
        "Test that changes are tested in parallel and merged in series"

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project2', 'master', 'C')

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        # We expect the following builds:
        #  - 1 for org/project
        #  - 3 for org/project1
        #  - 3 for org/project2
        self.assertEqual(len(self.history), 7)
        self.assertEqual(A.reported, 1)
        self.assertEqual(B.reported, 1)
        self.assertEqual(C.reported, 1)

        self.assertHistory([
            dict(name='project-test', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='SUCCESS', changes='2,1'),
            dict(name='project-common-test', result='SUCCESS', changes='2,1'),
            dict(name='project-common-test-canonical', result='SUCCESS',
                 changes='2,1'),
            dict(name='project-test2', result='SUCCESS', changes='3,1'),
            dict(name='project-common-test', result='SUCCESS', changes='3,1'),
            dict(name='project-common-test-canonical', result='SUCCESS',
                 changes='3,1'),
        ], ordered=False)


class TestSchedulerTemplatedProject(ZuulTestCase):
    tenant_config_file = 'config/templated-project/main.yaml'

    def test_job_from_templates_executed(self):
        "Test whether a job generated via a template can be executed"

        A = self.fake_gerrit.addFakeChange(
            'org/templated-project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')

    def test_layered_templates(self):
        "Test whether a job generated via a template can be executed"

        A = self.fake_gerrit.addFakeChange(
            'org/layered-project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('layered-project-test3'
                                                ).result, 'SUCCESS')
        self.assertEqual(self.getJobFromHistory('layered-project-test4'
                                                ).result, 'SUCCESS')
        self.assertEqual(self.getJobFromHistory('layered-project-foo-test5'
                                                ).result, 'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test6').result,
                         'SUCCESS')

    def test_unimplied_branch_matchers(self):
        # This tests that there are no implied branch matchers added
        # to project templates in unbranched projects.
        self.create_branch('org/layered-project', 'stable')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/layered-project', 'stable'))
        self.waitUntilSettled()

        A = self.fake_gerrit.addFakeChange(
            'org/layered-project', 'stable', 'A')

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.log.info(
            self.getJobFromHistory('project-test1').
            parameters['zuul']['_inheritance_path'])

    def test_implied_branch_matchers(self):
        # This tests that there is an implied branch matcher when a
        # template is used on an in-repo project pipeline definition.
        self.create_branch('untrusted-config', 'stable')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'untrusted-config', 'stable'))
        self.waitUntilSettled()

        A = self.fake_gerrit.addFakeChange(
            'untrusted-config', 'stable', 'A')

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.log.info(
            self.getJobFromHistory('project-test1').
            parameters['zuul']['_inheritance_path'])

        # Now create a new branch named stable-foo and change the project
        # pipeline
        self.create_branch('untrusted-config', 'stable-foo')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'untrusted-config', 'stable-foo'))
        self.waitUntilSettled()

        in_repo_conf = textwrap.dedent(
            """
            - project:
                name: untrusted-config
                templates:
                  - test-three-and-four
                check:
                  jobs:
                    - project-test7
            """)
        file_dict = {'zuul.d/project.yaml': in_repo_conf}
        B = self.fake_gerrit.addFakeChange('untrusted-config', 'stable-foo',
                                           'B', files=file_dict)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
            dict(name='project-test7', result='SUCCESS', changes='2,1'),
            dict(name='layered-project-test3', result='SUCCESS',
                 changes='2,1'),
            dict(name='layered-project-test4', result='SUCCESS',
                 changes='2,1'),
        ], ordered=False)

        # Inheritance path should not contain items from branch stable
        # This tests that not only is it the case that the stable
        # branch project-template did not apply, but also that the
        # stable branch definitions of the project-test7 did not apply
        # (since the job definitions also have implied branch
        # matchers).
        job = self.getJobFromHistory('project-test7', branch='stable-foo')
        inheritance_path = job.parameters['zuul']['_inheritance_path']
        self.assertEqual(len(inheritance_path), 4)
        stable_items = [x for x in inheritance_path
                        if 'untrusted-config/zuul.d/jobs.yaml@stable#' in x]
        self.assertEqual(len(stable_items), 0)


class TestSchedulerMerges(ZuulTestCase):
    tenant_config_file = 'config/merges/main.yaml'

    def _test_project_merge_mode(self, mode):
        self.executor_server.keep_jobdir = False
        project = 'org/project-%s' % mode
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange(project, 'master', 'A')
        B = self.fake_gerrit.addFakeChange(project, 'master', 'B')
        C = self.fake_gerrit.addFakeChange(project, 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        build = self.builds[-1]
        path = os.path.join(build.jobdir.src_root, 'review.example.com',
                            project)
        repo = git.Repo(path)
        repo_messages = [c.message.strip() for c in repo.iter_commits()]
        repo_messages.reverse()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        return repo_messages

    def _test_merge(self, mode):
        us_path = 'file://' + os.path.join(
            self.upstream_root, 'org/project-%s' % mode)
        expected_messages = [
            'initial commit',
            'add content from fixture',
            # the intermediate commits order is nondeterministic
            "Merge commit 'refs/changes/02/2/1' of %s into HEAD" % us_path,
            "Merge commit 'refs/changes/03/3/1' of %s into HEAD" % us_path,
        ]
        result = self._test_project_merge_mode(mode)
        self.assertEqual(result[:2], expected_messages[:2])
        self.assertEqual(result[-2:], expected_messages[-2:])

    def test_project_merge_mode_merge(self):
        self._test_merge('merge')

    def test_project_merge_mode_merge_resolve(self):
        self._test_merge('merge-resolve')

    def test_project_merge_mode_cherrypick(self):
        expected_messages = [
            'initial commit',
            'add content from fixture',
            'A-1',
            'B-1',
            'C-1']
        result = self._test_project_merge_mode('cherry-pick')
        self.assertEqual(result, expected_messages)

    def test_merge_branch(self):
        "Test that the right commits are on alternate branches"
        self.create_branch('org/project-merge-branches', 'mp')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project-merge-branches', 'mp'))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange(
            'org/project-merge-branches', 'mp', 'A')
        B = self.fake_gerrit.addFakeChange(
            'org/project-merge-branches', 'mp', 'B')
        C = self.fake_gerrit.addFakeChange(
            'org/project-merge-branches', 'mp', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        build = self.builds[-1]
        self.assertEqual(build.parameters['zuul']['branch'], 'mp')
        path = os.path.join(build.jobdir.src_root, 'review.example.com',
                            'org/project-merge-branches')
        repo = git.Repo(path)

        repo_messages = [c.message.strip() for c in repo.iter_commits()]
        repo_messages.reverse()
        correct_messages = [
            'initial commit',
            'add content from fixture',
            'mp commit',
            'A-1', 'B-1', 'C-1']
        self.assertEqual(repo_messages, correct_messages)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    def test_merge_multi_branch(self):
        "Test that dependent changes on multiple branches are merged"
        self.create_branch('org/project-merge-branches', 'mp')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project-merge-branches', 'mp'))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange(
            'org/project-merge-branches', 'master', 'A')
        B = self.fake_gerrit.addFakeChange(
            'org/project-merge-branches', 'mp', 'B')
        C = self.fake_gerrit.addFakeChange(
            'org/project-merge-branches', 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        job_A = None
        for job in self.builds:
            if 'project-merge' in job.name:
                job_A = job

        path = os.path.join(job_A.jobdir.src_root, 'review.example.com',
                            'org/project-merge-branches')
        repo = git.Repo(path)
        repo_messages = [c.message.strip()
                         for c in repo.iter_commits()]
        repo_messages.reverse()
        correct_messages = [
            'initial commit', 'add content from fixture', 'A-1']
        self.assertEqual(repo_messages, correct_messages)

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        job_B = None
        for job in self.builds:
            if 'project-merge' in job.name:
                job_B = job

        path = os.path.join(job_B.jobdir.src_root, 'review.example.com',
                            'org/project-merge-branches')
        repo = git.Repo(path)
        repo_messages = [c.message.strip() for c in repo.iter_commits()]
        repo_messages.reverse()
        correct_messages = [
            'initial commit', 'add content from fixture', 'mp commit', 'B-1']
        self.assertEqual(repo_messages, correct_messages)

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        job_C = None
        for job in self.builds:
            if 'project-merge' in job.name:
                job_C = job

        path = os.path.join(job_C.jobdir.src_root, 'review.example.com',
                            'org/project-merge-branches')
        repo = git.Repo(path)
        repo_messages = [c.message.strip() for c in repo.iter_commits()]

        repo_messages.reverse()
        correct_messages = [
            'initial commit', 'add content from fixture',
            'A-1', 'C-1']
        # Ensure the right commits are in the history for this ref
        self.assertEqual(repo_messages, correct_messages)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()


class TestSemaphore(ZuulTestCase):
    tenant_config_file = 'config/semaphore/main.yaml'

    def test_semaphore_one(self):
        "Test semaphores with max=1 (mutex)"
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')

        self.executor_server.hold_jobs_in_build = True

        # Pause nodepool so we can check the ordering of getting the nodes
        # and aquiring the semaphore.
        self.fake_nodepool.paused = True

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        status = tenant.layout.pipelines["check"].formatStatusJSON()
        jobs = status["change_queues"][0]["heads"][0][0]["jobs"]
        self.assertIsNone(jobs[0]["waiting_status"])
        self.assertIsNone(jobs[1]["waiting_status"])
        self.assertEqual(jobs[2]["waiting_status"],
                         'semaphores: test-semaphore')

        # By default we first lock the semaphore and then get the nodes
        # so at this point the semaphore needs to be aquired.
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)
        self.fake_nodepool.paused = False
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 3)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'semaphore-one-test1')
        self.assertEqual(self.builds[2].name, 'project-test1')

        self.executor_server.release('semaphore-one-test1')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 3)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test1')
        self.assertEqual(self.builds[2].name, 'semaphore-one-test2')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        self.executor_server.release('semaphore-one-test2')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 3)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test1')
        self.assertEqual(self.builds[2].name, 'semaphore-one-test1')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        self.executor_server.release('semaphore-one-test1')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 3)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test1')
        self.assertEqual(self.builds[2].name, 'semaphore-one-test2')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        self.executor_server.release('semaphore-one-test2')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 2)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test1')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()

        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 0)

        self.assertEqual(A.reported, 1)
        self.assertEqual(B.reported, 1)
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.assertReportedStat(
            'zuul.tenant.tenant-one.semaphore.test-semaphore.holders',
            value='1', kind='g')
        self.assertReportedStat(
            'zuul.tenant.tenant-one.semaphore.test-semaphore.holders',
            value='0', kind='g')

    def test_semaphore_two(self):
        "Test semaphores with max>1"
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders(
                "test-semaphore-two")), 0)

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 4)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'semaphore-two-test1')
        self.assertEqual(self.builds[2].name, 'semaphore-two-test2')
        self.assertEqual(self.builds[3].name, 'project-test1')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders(
                "test-semaphore-two")), 2)

        self.executor_server.release('semaphore-two-test1')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 4)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'semaphore-two-test2')
        self.assertEqual(self.builds[2].name, 'project-test1')
        self.assertEqual(self.builds[3].name, 'semaphore-two-test1')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders(
                "test-semaphore-two")), 2)

        self.executor_server.release('semaphore-two-test2')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 4)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test1')
        self.assertEqual(self.builds[2].name, 'semaphore-two-test1')
        self.assertEqual(self.builds[3].name, 'semaphore-two-test2')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders(
                "test-semaphore-two")), 2)

        self.executor_server.release('semaphore-two-test1')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 3)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test1')
        self.assertEqual(self.builds[2].name, 'semaphore-two-test2')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders(
                "test-semaphore-two")), 1)

        self.executor_server.release('semaphore-two-test2')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 2)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test1')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders(
                "test-semaphore-two")), 0)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()

        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 0)

        self.assertEqual(A.reported, 1)
        self.assertEqual(B.reported, 1)

    def test_semaphore_node_failure(self):
        "Test semaphore and node failure"
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')

        # Pause nodepool so we can fail the node request later
        self.fake_nodepool.pause()

        A = self.fake_gerrit.addFakeChange('org/project2', 'master', 'A')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # By default we first lock the semaphore and then get the nodes
        # so at this point the semaphore needs to be aquired.
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        # Fail the node request and unpause
        req = self.fake_nodepool.getNodeRequests()[0]
        self.fake_nodepool.addFailRequest(req)
        self.fake_nodepool.unpause()
        self.waitUntilSettled()

        # At this point the job that holds the semaphore failed with
        # node_failure and the semaphore must be released.
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.assertEquals(1, A.reported)
        self.assertTrue(re.search('semaphore-one-test3 .* NODE_FAILURE',
                                  A.messages[0]))

    def test_semaphore_resources_first(self):
        "Test semaphores with max=1 (mutex) and get resources first"
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')

        self.executor_server.hold_jobs_in_build = True

        # Pause nodepool so we can check the ordering of getting the nodes
        # and aquiring the semaphore.
        self.fake_nodepool.paused = True

        A = self.fake_gerrit.addFakeChange('org/project3', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project3', 'master', 'B')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # Here we first get the resources and then lock the semaphore
        # so at this point the semaphore should not be aquired.
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)
        self.fake_nodepool.paused = False
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 3)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name,
                         'semaphore-one-test1-resources-first')
        self.assertEqual(self.builds[2].name, 'project-test1')

        self.executor_server.release('semaphore-one-test1')
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 3)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test1')
        self.assertEqual(self.builds[2].name,
                         'semaphore-one-test2-resources-first')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    def test_semaphore_resources_first_node_failure(self):
        "Test semaphore and node failure"
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')

        # Pause nodepool so we can fail the node request later
        self.fake_nodepool.pause()

        A = self.fake_gerrit.addFakeChange('org/project4', 'master', 'A')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # With resources first we first get the nodes so at this point the
        # semaphore must not be aquired.
        self.assertEqual(len(tenant.semaphore_handler.semaphoreHolders(
            "test-semaphore")), 0)

        # Fail the node request and unpause
        req = self.fake_nodepool.getNodeRequests()[0]
        self.fake_nodepool.addFailRequest(req)
        self.fake_nodepool.unpause()
        self.waitUntilSettled()

        # At this point the job should never have acuired a semaphore so check
        # that it still has not locked a semaphore.
        self.assertEqual(len(tenant.semaphore_handler.semaphoreHolders(
            "test-semaphore")), 0)
        self.assertEquals(1, A.reported)
        self.assertTrue(
            re.search('semaphore-one-test1-resources-first .* NODE_FAILURE',
                      A.messages[0]))

    def test_semaphore_zk_error(self):
        "Test semaphore release with zk error"
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')

        A = self.fake_gerrit.addFakeChange('org/project2', 'master', 'A')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        # Simulate a single zk error in useNodeSet
        orig_useNodeSet = self.scheds.first.sched.nodepool.useNodeSet

        def broken_use_nodeset(nodeset, tenant_name, project_name):
            # restore original useNodeSet
            self.scheds.first.sched.nodepool.useNodeSet = orig_useNodeSet
            raise NoNodeError()

        self.scheds.first.sched.nodepool.useNodeSet = broken_use_nodeset

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # The semaphore should be released
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        # cleanup the queue
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

    def test_semaphore_abandon(self):
        "Test abandon with job semaphores"
        self.executor_server.hold_jobs_in_build = True
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        check_pipeline = tenant.layout.pipelines['check']

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        self.fake_gerrit.addEvent(A.getChangeAbandonedEvent())
        self.waitUntilSettled()

        # The check pipeline should be empty
        items = check_pipeline.getAllItems()
        self.assertEqual(len(items), 0)

        # The semaphore should be released
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    def test_semaphore_abandon_pending_node_request(self):
        "Test abandon with job semaphores and pending node request"
        self.executor_server.hold_jobs_in_build = True

        # Pause nodepool so we can check the ordering of getting the nodes
        # and aquiring the semaphore.
        self.fake_nodepool.paused = True

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        check_pipeline = tenant.layout.pipelines['check']

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        self.fake_gerrit.addEvent(A.getChangeAbandonedEvent())
        self.waitUntilSettled()

        # The check pipeline should be empty
        items = check_pipeline.getAllItems()
        self.assertEqual(len(items), 0)

        # The semaphore should be released
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.executor_server.hold_jobs_in_build = False
        self.fake_nodepool.paused = False
        self.executor_server.release()
        self.waitUntilSettled()

    def test_semaphore_abandon_pending_execution(self):
        "Test abandon with job semaphores and pending job execution"

        # Pause the executor so it doesn't take any jobs.
        self.executor_server.pause()

        # Start merger as the paused executor won't take merge jobs.
        self._startMerger()

        # Pause nodepool so we can wait on the node requests and fulfill them
        # in a controlled manner.
        self.fake_nodepool.paused = True

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        check_pipeline = tenant.layout.pipelines['check']

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        reqs = list(self.scheds.first.sched.nodepool.getNodeRequests())
        self.assertEqual(len(reqs), 2)

        # Now unpause nodepool to fulfill the node requests. We cannot use
        # waitUntilSettled here because the executor is paused.
        self.fake_nodepool.paused = False
        for _ in iterate_timeout(30, 'fulfill node requests'):
            reqs = [
                r for r in self.scheds.first.sched.nodepool.getNodeRequests()
                if r.state != zuul.model.STATE_FULFILLED
            ]
            if len(reqs) == 0:
                break

        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        self.fake_gerrit.addEvent(A.getChangeAbandonedEvent())
        self.waitUntilSettled()

        # The check pipeline should be empty
        items = check_pipeline.getAllItems()
        self.assertEqual(len(items), 0)

        # The semaphore should be released
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.executor_server.release()
        self.waitUntilSettled()

    def test_semaphore_new_patchset(self):
        "Test new patchset with job semaphores"
        self.executor_server.hold_jobs_in_build = True
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        check_pipeline = tenant.layout.pipelines['check']

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        A.addPatchset()
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(2))
        self.waitUntilSettled()

        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        items = check_pipeline.getAllItems()
        self.assertEqual(items[0].change.number, '1')
        self.assertEqual(items[0].change.patchset, '2')
        self.assertTrue(items[0].live)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        # The semaphore should be released
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

    def test_semaphore_reconfigure(self):
        "Test reconfigure with job semaphores"
        self.executor_server.hold_jobs_in_build = True
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        # reconfigure without layout change
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')

        # semaphore still must be held
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        # remove the pipeline
        self.commitConfigUpdate(
            'common-config',
            'config/semaphore/zuul-reconfiguration.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')

        self.executor_server.release('project-test1')
        self.waitUntilSettled()

        # There should be no builds anymore
        self.assertEqual(len(self.builds), 0)

        # The semaphore should be released
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

    def test_semaphore_handler_cleanup(self):
        "Test the semaphore handler leak cleanup"
        self.executor_server.hold_jobs_in_build = True
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        # Save some variables for later use while the job is running
        check_pipeline = tenant.layout.pipelines['check']
        item = check_pipeline.getAllItems()[0]
        job = item.getJob('semaphore-one-test1')

        tenant.semaphore_handler.cleanupLeaks()

        # Nothing has leaked; our handle should be present.
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        # Make sure the semaphore is released normally
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

        # Use our previously saved data to simulate a leaked semaphore
        tenant.semaphore_handler.acquire(item, job, False)
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        tenant.semaphore_handler.cleanupLeaks()
        # Make sure the leaked semaphore is cleaned up
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0)

    @simple_layout('layouts/multiple-semaphores.yaml')
    def test_multiple_semaphores(self):
        # Test a job with multiple semaphores
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # One job should be running, and hold sem1
        self.assertBuilds([dict(name='job1')])

        B = self.fake_gerrit.addFakeChange('org/project2', 'master', 'B')
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # Job2 requires sem1 and sem2; it hasn't started because job
        # is still holding sem1.
        self.assertBuilds([dict(name='job1')])

        self.executor_server.release('job1')
        self.waitUntilSettled()

        # Job1 is finished, so job2 can acquire both semaphores.
        self.assertBuilds([dict(name='job2')])

        self.executor_server.release()
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='job1', result='SUCCESS', changes='1,1'),
            dict(name='job2', result='SUCCESS', changes='2,1'),
        ])
        # TODO(corvus): Consider a version of this test which launches
        # 2 jobs with the same multiple-semaphore requirements
        # simultaneously to test the behavior with contention (at
        # least one should be able to start on each pass through the
        # loop).


class TestSemaphoreMultiTenant(ZuulTestCase):
    tenant_config_file = 'config/multi-tenant-semaphore/main.yaml'

    def test_semaphore_tenant_isolation(self):
        "Test semaphores in multiple tenants"

        self.waitUntilSettled()
        tenant_one = self.scheds.first.sched.abide.tenants.get('tenant-one')
        tenant_two = self.scheds.first.sched.abide.tenants.get('tenant-two')

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project2', 'master', 'C')
        D = self.fake_gerrit.addFakeChange('org/project2', 'master', 'D')
        E = self.fake_gerrit.addFakeChange('org/project2', 'master', 'E')
        self.assertEqual(
            len(tenant_one.semaphore_handler.semaphoreHolders(
                "test-semaphore")), 0)
        self.assertEqual(
            len(tenant_two.semaphore_handler.semaphoreHolders(
                "test-semaphore")), 0)

        # add patches to project1 of tenant-one
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # one build of project1-test1 must run
        # semaphore of tenant-one must be acquired once
        # semaphore of tenant-two must not be acquired
        self.assertEqual(len(self.builds), 1)
        self.assertEqual(self.builds[0].name, 'project1-test1')
        self.assertEqual(
            len(tenant_one.semaphore_handler.semaphoreHolders(
                "test-semaphore")), 1)
        self.assertEqual(
            len(tenant_two.semaphore_handler.semaphoreHolders(
                "test-semaphore")), 0)

        # add patches to project2 of tenant-two
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(D.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(E.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # one build of project1-test1 must run
        # two builds of project2-test1 must run
        # semaphore of tenant-one must be acquired once
        # semaphore of tenant-two must be acquired twice
        self.assertEqual(len(self.builds), 3)
        self.assertEqual(self.builds[0].name, 'project1-test1')
        self.assertEqual(self.builds[1].name, 'project2-test1')
        self.assertEqual(self.builds[2].name, 'project2-test1')
        self.assertEqual(
            len(tenant_one.semaphore_handler.semaphoreHolders(
                "test-semaphore")), 1)
        self.assertEqual(
            len(tenant_two.semaphore_handler.semaphoreHolders(
                "test-semaphore")), 2)

        self.executor_server.release('project1-test1')
        self.waitUntilSettled()

        # one build of project1-test1 must run
        # two builds of project2-test1 must run
        # semaphore of tenant-one must be acquired once
        # semaphore of tenant-two must be acquired twice
        self.assertEqual(len(self.builds), 3)
        self.assertEqual(self.builds[0].name, 'project2-test1')
        self.assertEqual(self.builds[1].name, 'project2-test1')
        self.assertEqual(self.builds[2].name, 'project1-test1')
        self.assertEqual(
            len(tenant_one.semaphore_handler.semaphoreHolders(
                "test-semaphore")), 1)
        self.assertEqual(
            len(tenant_two.semaphore_handler.semaphoreHolders(
                "test-semaphore")), 2)

        self.executor_server.release('project2-test1')
        self.waitUntilSettled()

        # one build of project1-test1 must run
        # one build of project2-test1 must run
        # semaphore of tenant-one must be acquired once
        # semaphore of tenant-two must be acquired once
        self.assertEqual(len(self.builds), 2)
        self.assertEqual(
            len(tenant_one.semaphore_handler.semaphoreHolders(
                "test-semaphore")), 1)
        self.assertEqual(
            len(tenant_two.semaphore_handler.semaphoreHolders(
                "test-semaphore")), 1)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()

        self.waitUntilSettled()

        # no build must run
        # semaphore of tenant-one must not be acquired
        # semaphore of tenant-two must not be acquired
        self.assertEqual(len(self.builds), 0)
        self.assertEqual(
            len(tenant_one.semaphore_handler.semaphoreHolders(
                "test-semaphore")), 0)
        self.assertEqual(
            len(tenant_two.semaphore_handler.semaphoreHolders(
                "test-semaphore")), 0)

        self.assertEqual(A.reported, 1)
        self.assertEqual(B.reported, 1)


class TestImplicitProject(ZuulTestCase):
    tenant_config_file = 'config/implicit-project/main.yaml'

    def test_implicit_project(self):
        # config project should work with implicit project name
        A = self.fake_gerrit.addFakeChange('common-config', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))

        # untrusted project should work with implicit project name
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertEqual(A.reported, 1)
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(B.reported, 1)
        self.assertHistory([
            dict(name='test-common', result='SUCCESS', changes='1,1'),
            dict(name='test-common', result='SUCCESS', changes='2,1'),
            dict(name='test-project', result='SUCCESS', changes='2,1'),
        ], ordered=False)

        # now test adding a further project in repo
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: test-project
                run: playbooks/test-project.yaml
            - job:
                name: test2-project
                run: playbooks/test-project.yaml

            - project:
                check:
                  jobs:
                    - test-project
                gate:
                  jobs:
                    - test-project

            - project:
                check:
                  jobs:
                    - test2-project
                gate:
                  jobs:
                    - test2-project

            """)
        file_dict = {'.zuul.yaml': in_repo_conf}
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        C.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        # change C must be merged
        self.assertEqual(C.data['status'], 'MERGED')
        self.assertEqual(C.reported, 2)
        self.assertHistory([
            dict(name='test-common', result='SUCCESS', changes='1,1'),
            dict(name='test-common', result='SUCCESS', changes='2,1'),
            dict(name='test-project', result='SUCCESS', changes='2,1'),
            dict(name='test-common', result='SUCCESS', changes='3,1'),
            dict(name='test-project', result='SUCCESS', changes='3,1'),
            dict(name='test2-project', result='SUCCESS', changes='3,1'),
        ], ordered=False)


class TestSemaphoreInRepo(ZuulTestCase):
    config_file = 'zuul-connections-gerrit-and-github.conf'
    tenant_config_file = 'config/in-repo/main.yaml'

    def test_semaphore_in_repo(self):
        "Test semaphores in repo config"

        # This tests dynamic semaphore handling in project repos. The semaphore
        # max value should not be evaluated dynamically but must be updated
        # after the change lands.

        self.waitUntilSettled()
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')

        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: project-test1

            - job:
                name: project-test2
                run: playbooks/project-test2.yaml
                semaphore: test-semaphore

            - project:
                name: org/project
                tenant-one-gate:
                  jobs:
                    - project-test2

            # the max value in dynamic layout must be ignored
            - semaphore:
                name: test-semaphore
                max: 2
            """)

        in_repo_playbook = textwrap.dedent(
            """
            - hosts: all
              tasks: []
            """)

        file_dict = {'.zuul.yaml': in_repo_conf,
                     'playbooks/project-test2.yaml': in_repo_playbook}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        B.setDependsOn(A, 1)
        C.setDependsOn(A, 1)

        self.executor_server.hold_jobs_in_build = True

        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        # check that the layout in a queue item still has max value of 1
        # for test-semaphore
        pipeline = tenant.layout.pipelines.get('tenant-one-gate')
        queue = None
        for queue_candidate in pipeline.queues:
            if queue_candidate.name == 'org/project':
                queue = queue_candidate
                break
        queue_item = queue.queue[0]
        item_dynamic_layout = pipeline.manager._layout_cache.get(
            queue_item.layout_uuid)
        self.assertIsNotNone(item_dynamic_layout)
        dynamic_test_semaphore = \
            item_dynamic_layout.semaphores.get('test-semaphore')
        self.assertEqual(dynamic_test_semaphore.max, 1)

        # one build must be in queue, one semaphores acquired
        self.assertEqual(len(self.builds), 1)
        self.assertEqual(self.builds[0].name, 'project-test2')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            1)

        self.executor_server.release('project-test2')
        self.waitUntilSettled()

        # change A must be merged
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2)

        # send change-merged event as the gerrit mock doesn't send it
        self.fake_gerrit.addEvent(A.getChangeMergedEvent())
        self.waitUntilSettled()

        # now that change A was merged, the new semaphore max must be effective
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertEqual(tenant.layout.semaphores.get('test-semaphore').max, 2)

        # two builds must be in queue, two semaphores acquired
        self.assertEqual(len(self.builds), 2)
        self.assertEqual(self.builds[0].name, 'project-test2')
        self.assertEqual(self.builds[1].name, 'project-test2')
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            2)

        self.executor_server.release('project-test2')
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)
        self.assertEqual(
            len(tenant.semaphore_handler.semaphoreHolders("test-semaphore")),
            0
        )

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()

        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 0)

        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)


class TestSchedulerBranchMatcher(ZuulTestCase):

    @simple_layout('layouts/matcher-test.yaml')
    def test_job_branch_ignored(self):
        '''
        Test that branch matching logic works.

        The 'ignore-branch' job has a branch matcher that is supposed to
        match every branch except for the 'featureA' branch, so it should
        not be run on a change to that branch.
        '''
        self.create_branch('org/project', 'featureA')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project', 'featureA'))
        self.waitUntilSettled()
        A = self.fake_gerrit.addFakeChange('org/project', 'featureA', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.printHistory()
        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertJobNotInHistory('ignore-branch')
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2,
                         "A should report start and success")
        self.assertIn('gate', A.messages[1],
                      "A should transit gate")


class TestSchedulerFailFast(ZuulTestCase):
    tenant_config_file = 'config/fail-fast/main.yaml'

    def test_fail_fast(self):
        """
        Tests that a pipeline that is flagged with fail-fast
        aborts jobs early.
        """
        self.executor_server.hold_jobs_in_build = True
        self.fake_nodepool.pause()

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.executor_server.failJob('project-test1', A)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 1)
        self.assertEqual(self.builds[0].name, 'project-merge')
        self.executor_server.release('project-merge')
        self.waitUntilSettled()

        # Now project-test1, project-test2 and project-test6
        # should be running
        self.assertEqual(len(self.builds), 3)

        # Release project-test1 which will fail
        self.executor_server.release('project-test1')
        self.waitUntilSettled()

        self.fake_nodepool.unpause()
        self.waitUntilSettled()

        # Now project-test2 must be aborted
        self.assertEqual(len(self.builds), 0)
        self.assertEqual(A.reported, 1)
        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='FAILURE', changes='1,1'),
            dict(name='project-test2', result='ABORTED', changes='1,1'),
            dict(name='project-test6', result='ABORTED', changes='1,1'),
        ], ordered=False)

    def test_fail_fast_gate(self):
        """
        Tests that a pipeline that is flagged with fail-fast
        aborts jobs early.
        """
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        self.executor_server.failJob('project-test1', B)
        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 4)
        # Release project-test1 which will fail
        self.builds[2].release()
        self.waitUntilSettled()

        # We should only have the builds from change A now
        self.assertEqual(len(self.builds), 2)
        self.assertEqual(self.builds[0].name, 'project-test1')
        self.assertEqual(self.builds[1].name, 'project-test2')

        # But both changes should still be in the pipeline
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        items = tenant.layout.pipelines['gate'].getAllItems()
        self.assertEqual(len(items), 2)
        self.assertEqual(A.reported, 1)
        self.assertEqual(B.reported, 1)

        # Release change A
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertHistory([
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='FAILURE', changes='1,1 2,1'),
            dict(name='project-test2', result='ABORTED', changes='1,1 2,1'),
        ], ordered=False)

    def test_fail_fast_nonvoting(self):
        """
        Tests that a pipeline that is flagged with fail-fast
        doesn't abort jobs due to a non-voting job.
        """
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.executor_server.failJob('project-test6', A)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 2)
        self.assertEqual(self.builds[0].name, 'project-merge')
        self.executor_server.release('project-merge')
        self.waitUntilSettled()

        # Now project-test1, project-test2, project-test5 and project-test6
        # should be running
        self.assertEqual(len(self.builds), 4)

        # Release project-test6 which will fail
        self.executor_server.release('project-test6')
        self.waitUntilSettled()

        # Now project-test1, project-test2 and project-test5 should be running
        self.assertEqual(len(self.builds), 3)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)
        self.assertEqual(A.reported, 1)
        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
            dict(name='project-test3', result='SUCCESS', changes='1,1'),
            dict(name='project-test4', result='SUCCESS', changes='1,1'),
            dict(name='project-test5', result='SUCCESS', changes='1,1'),
            dict(name='project-test6', result='FAILURE', changes='1,1'),
        ], ordered=False)

    def test_fail_fast_retry(self):
        """
        Tests that a retried build doesn't trigger fail-fast.
        """
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # project-merge and project-test5
        self.assertEqual(len(self.builds), 2)

        # Force a retry of first build
        self.builds[0].requeue = True
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)
        self.assertEqual(A.reported, 1)
        self.assertHistory([
            dict(name='project-merge', result=None, changes='1,1'),
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
            dict(name='project-test3', result='SUCCESS', changes='1,1'),
            dict(name='project-test4', result='SUCCESS', changes='1,1'),
            dict(name='project-test5', result='SUCCESS', changes='1,1'),
            dict(name='project-test6', result='SUCCESS', changes='1,1'),
        ], ordered=False)


class TestPipelineSupersedes(ZuulTestCase):

    @simple_layout('layouts/pipeline-supercedes.yaml')
    def test_supercedes(self):
        """
        Tests that a pipeline that is flagged with fail-fast
        aborts jobs early.
        """
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 1)
        self.assertEqual(self.builds[0].name, 'test-job')

        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 1)
        self.assertEqual(self.builds[0].name, 'test-job')
        self.assertEqual(self.builds[0].pipeline, 'gate')

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)
        self.assertEqual(A.reported, 2)
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertHistory([
            dict(name='test-job', result='ABORTED', changes='1,1'),
            dict(name='test-job', result='SUCCESS', changes='1,1'),
        ], ordered=False)


class TestReportBuildPage(ZuulTestCase):
    tenant_config_file = 'config/build-page/main.yaml'

    def test_tenant_url(self):
        """
        Test that the tenant url is used in reporting the build page.
        """
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='python27', result='SUCCESS', changes='1,1'),
        ])
        self.assertIn('python27 https://one.example.com/build/',
                      A.messages[0])

    def test_base_url(self):
        """
        Test that the web base url is used in reporting the build page.
        """
        A = self.fake_gerrit.addFakeChange('org/project2', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='python27', result='SUCCESS', changes='1,1'),
        ])
        self.assertIn('python27 https://zuul.example.com/t/tenant-two/build/',
                      A.messages[0])

    def test_no_build_page(self):
        """
        Test that we fall back to the old behavior if the tenant is
        not configured to report the build page
        """
        A = self.fake_gerrit.addFakeChange('org/project3', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='python27', result='SUCCESS', changes='1,1'),
        ])
        self.assertIn('python27 https://', A.messages[0])


class TestSchedulerSmartReconfiguration(ZuulTestCase):
    tenant_config_file = 'config/multi-tenant/main.yaml'

    def _test_smart_reconfiguration(self, command_socket=False):
        """
        Tests that smart reconfiguration works

        In this scenario we have the tenants tenant-one, tenant-two and
        tenant-three. We make the following changes and then trigger a smart
        reconfiguration:
        - tenant-one remains unchanged
        - tenant-two gets another repo
        - tenant-three gets removed completely
        - tenant-four is a new tenant
        """
        self.executor_server.hold_jobs_in_build = True

        # Create changes for all tenants
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        B = self.fake_gerrit.addFakeChange('org/project2', 'master', 'B')
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        C = self.fake_gerrit.addFakeChange('org/project3', 'master', 'C')
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))

        # record previous tenant reconfiguration time, which may not be set
        old_one = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)
        old_two = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-two', EMPTY_LAYOUT_STATE)
        self.waitUntilSettled()

        self.newTenantConfig('config/multi-tenant/main-reconfig.yaml')

        del self.merge_job_history
        self.scheds.execute(
            lambda app: app.smartReconfigure(command_socket=command_socket))

        # Wait for smart reconfiguration. Only tenant-two should be
        # reconfigured. Note that waitUntilSettled is not
        # reliable here because the reconfigure event may arrive in the
        # event queue after waitUntilSettled.
        start = time.time()
        while True:
            if time.time() - start > 30:
                raise Exception("Timeout waiting for smart reconfiguration")
            new_two = self.scheds.first.sched.tenant_layout_state.get(
                'tenant-two', EMPTY_LAYOUT_STATE)
            if old_two < new_two:
                break
            else:
                time.sleep(0.1)

        self.waitUntilSettled()

        # We're only adding two new repos, so we should only need to
        # issue 2 cat jobs.
        cat_jobs = self.merge_job_history.get(zuul.model.MergeRequest.CAT)
        self.assertEqual(len(cat_jobs), 2)

        # Ensure that tenant-one has not been reconfigured
        new_one = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)
        self.assertEqual(old_one, new_one)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        # Changes in tenant-one and tenant-two have to be reported
        self.assertEqual(1, A.reported)
        self.assertEqual(1, B.reported)

        # The tenant-three has been removed so nothing should be reported
        self.assertEqual(0, C.reported)
        self.assertNotIn('tenant-three', self.scheds.first.sched.abide.tenants)

        # Verify known tenants
        expected_tenants = {'tenant-one', 'tenant-two', 'tenant-four'}
        self.assertEqual(expected_tenants,
                         self.scheds.first.sched.abide.tenants.keys())

        self.assertIsNotNone(
            self.scheds.first.sched.tenant_layout_state.get('tenant-four'),
            'Tenant tenant-four should exist now.'
        )

        # Test that the new tenant-four actually works
        D = self.fake_gerrit.addFakeChange('org/project4', 'master', 'D')
        self.fake_gerrit.addEvent(D.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertEqual(1, D.reported)

        # Test that the new project in tenant-two works
        B2 = self.fake_gerrit.addFakeChange('org/project2b', 'master', 'B2')
        self.fake_gerrit.addEvent(B2.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertEqual(1, B2.reported)

    def test_smart_reconfiguration(self):
        "Test that live reconfiguration works"
        self._test_smart_reconfiguration()

    def test_smart_reconfiguration_command_socket(self):
        "Test that live reconfiguration works using command socket"
        self._test_smart_reconfiguration(command_socket=True)


class TestReconfigureBranch(ZuulTestCase):

    def _setupTenantReconfigureTime(self):
        self.old = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)

    def _createBranch(self):
        self.create_branch('org/project1', 'stable')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project1', 'stable'))
        self.waitUntilSettled()

    def _deleteBranch(self):
        self.delete_branch('org/project1', 'stable')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchDeletedEvent(
                'org/project1', 'stable'))
        self.waitUntilSettled()

    def _expectReconfigure(self, doReconfigure):
        new = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)
        if doReconfigure:
            self.assertLess(self.old, new)
        else:
            self.assertEqual(self.old, new)
        self.old = new


class TestReconfigureBranchCreateDeleteSshHttp(TestReconfigureBranch):
    tenant_config_file = 'config/single-tenant/main.yaml'
    config_file = 'zuul-gerrit-web.conf'

    def test_reconfigure_cache_branch_create_delete(self):
        "Test that cache is updated clear on branch creation/deletion"
        self._setupTenantReconfigureTime()
        self._createBranch()
        self._expectReconfigure(True)
        self._deleteBranch()
        self._expectReconfigure(True)


class TestReconfigureBranchCreateDeleteSsh(TestReconfigureBranch):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def test_reconfigure_cache_branch_create_delete(self):
        "Test that cache is updated clear on branch creation/deletion"
        self._setupTenantReconfigureTime()
        self._createBranch()
        self._expectReconfigure(True)
        self._deleteBranch()
        self._expectReconfigure(True)


class TestReconfigureBranchCreateDeleteHttp(TestReconfigureBranch):
    tenant_config_file = 'config/single-tenant/main.yaml'
    config_file = 'zuul-gerrit-no-stream.conf'

    def test_reconfigure_cache_branch_create_delete(self):
        "Test that cache is updated clear on branch creation/deletion"
        self._setupTenantReconfigureTime()
        self._createBranch()
        self._expectReconfigure(True)
        self._deleteBranch()
        self._expectReconfigure(True)


class TestEventProcessing(ZuulTestCase):
    tenant_config_file = 'config/event-processing/main.yaml'

    # Some regression tests for ZK-distributed event processing

    def test_independent_tenants(self):
        # Test that an exception in one tenant doesn't break others

        orig = zuul.scheduler.Scheduler._forward_trigger_event

        def patched_forward(obj, *args, **kw):
            if args[1].name == 'tenant-one':
                raise Exception("test")
            return orig(obj, *args, **kw)

        self.useFixture(fixtures.MonkeyPatch(
            'zuul.scheduler.Scheduler._forward_trigger_event',
            patched_forward))

        A = self.fake_gerrit.addFakeChange('org/project2', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='checkjob', result='SUCCESS', changes='1,1'),
        ], ordered=False)

    @skip("Failure can only be detected in logs; see test_ref_equality")
    def test_change_types(self):
        # Test that when we decide whether to forward events, we can
        # compare items with different change types (branch vs
        # change).

        # We can't detect a failure here except by observing the logs;
        # this test is left in case that's useful in the future, but
        # automated detection of this failure case is handled by
        # test_ref_equality.

        # Enqueue a tag
        self.executor_server.hold_jobs_in_build = True
        event = self.fake_gerrit.addFakeTag('org/project1', 'master', 'foo')
        self.fake_gerrit.addEvent(event)

        # Enqueue a change and make sure the scheduler is able to
        # compare the two when forwarding the event
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='tagjob', result='SUCCESS'),
            dict(name='checkjob', result='SUCCESS', changes='1,1'),
        ], ordered=False)

# Copyright 2012 Hewlett-Packard Development Company, L.P.
# Copyright 2014 Wikimedia Foundation Inc.
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

import json
import logging
import configparser
import multiprocessing
import os
import re
import time
from unittest import mock

from tests.base import (
    BaseTestCase,
    ZuulTestCase,
    AnsibleZuulTestCase,
    FIXTURE_DIR,
    simple_layout,
    iterate_timeout
)

from zuul.executor.sensors.startingbuilds import StartingBuildsSensor
from zuul.executor.sensors.ram import RAMSensor
from zuul.executor.server import squash_variables
from zuul.model import NodeSet, Group


class TestExecutorRepos(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    log = logging.getLogger("zuul.test.executor")

    def assertRepoState(self, repo, state, project, build, number):
        if 'branch' in state:
            self.assertFalse(repo.head.is_detached,
                             'Project %s commit for build %s #%s should '
                             'not have a detached HEAD' % (
                                 project, build, number))
            self.assertEqual(repo.active_branch.name,
                             state['branch'],
                             'Project %s commit for build %s #%s should '
                             'be on the correct branch' % (
                                 project, build, number))
            # Remote 'origin' needs to be kept intact with a bogus URL
            self.assertEqual(repo.remotes.origin.url, 'file:///dev/null')
            self.assertIn(state['branch'], repo.remotes.origin.refs)
        if 'commit' in state:
            self.assertEqual(state['commit'],
                             str(repo.commit('HEAD')),
                             'Project %s commit for build %s #%s should '
                             'be correct' % (
                                 project, build, number))
        ref = repo.commit('HEAD')
        repo_messages = set(
            [c.message.strip() for c in repo.iter_commits(ref)])
        if 'present' in state:
            for change in state['present']:
                msg = '%s-1' % change.subject
                self.assertTrue(msg in repo_messages,
                                'Project %s for build %s #%s should '
                                'have change %s' % (
                                    project, build, number, change.subject))
        if 'absent' in state:
            for change in state['absent']:
                msg = '%s-1' % change.subject
                self.assertTrue(msg not in repo_messages,
                                'Project %s for build %s #%s should '
                                'not have change %s' % (
                                    project, build, number, change.subject))

    def assertBuildStates(self, states, projects):
        for number, build in enumerate(self.builds):
            work = build.getWorkspaceRepos(projects)
            state = states[number]

            for project in projects:
                self.assertRepoState(work[project], state[project],
                                     project, build, number)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    @simple_layout('layouts/repo-checkout-two-project.yaml')
    def test_one_branch(self):
        self.executor_server.hold_jobs_in_build = True

        p1 = 'review.example.com/org/project1'
        p2 = 'review.example.com/org/project2'
        projects = [p1, p2]
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project2', 'master', 'B')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(2, len(self.builds), "Two builds are running")

        upstream = self.getUpstreamRepos(projects)
        states = [
            {p1: dict(present=[A], absent=[B], branch='master'),
             p2: dict(commit=str(upstream[p2].commit('master')),
                      branch='master'),
             },
            {p1: dict(present=[A], absent=[B], branch='master'),
             p2: dict(present=[B], absent=[A], branch='master'),
             },
        ]

        self.assertBuildStates(states, projects)

    @simple_layout('layouts/repo-checkout-four-project.yaml')
    def test_multi_branch(self):
        self.executor_server.hold_jobs_in_build = True

        p1 = 'review.example.com/org/project1'
        p2 = 'review.example.com/org/project2'
        p3 = 'review.example.com/org/project3'
        p4 = 'review.example.com/org/project4'
        projects = [p1, p2, p3, p4]

        self.create_branch('org/project2', 'stable/havana')
        self.create_branch('org/project4', 'stable/havana')
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project2', 'stable/havana',
                                           'B')
        C = self.fake_gerrit.addFakeChange('org/project3', 'master', 'C')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(3, len(self.builds), "Three builds are running")

        upstream = self.getUpstreamRepos(projects)
        states = [
            {p1: dict(present=[A], absent=[B, C], branch='master'),
             p2: dict(commit=str(upstream[p2].commit('master')),
                      branch='master'),
             p3: dict(commit=str(upstream[p3].commit('master')),
                      branch='master'),
             p4: dict(commit=str(upstream[p4].commit('master')),
                      branch='master'),
             },
            {p1: dict(present=[A], absent=[B, C], branch='master'),
             p2: dict(present=[B], absent=[A, C], branch='stable/havana'),
             p3: dict(commit=str(upstream[p3].commit('master')),
                      branch='master'),
             p4: dict(commit=str(upstream[p4].commit('stable/havana')),
                      branch='stable/havana'),
             },
            {p1: dict(present=[A], absent=[B, C], branch='master'),
             p2: dict(commit=str(upstream[p2].commit('master')),
                      branch='master'),
             p3: dict(present=[C], absent=[A, B], branch='master'),
             p4: dict(commit=str(upstream[p4].commit('master')),
                      branch='master'),
             },
        ]

        self.assertBuildStates(states, projects)

    @simple_layout('layouts/repo-checkout-six-project.yaml')
    def test_project_override(self):
        self.executor_server.hold_jobs_in_build = True

        p1 = 'review.example.com/org/project1'
        p2 = 'review.example.com/org/project2'
        p3 = 'review.example.com/org/project3'
        p4 = 'review.example.com/org/project4'
        p5 = 'review.example.com/org/project5'
        p6 = 'review.example.com/org/project6'
        projects = [p1, p2, p3, p4, p5, p6]

        self.create_branch('org/project3', 'stable/havana')
        self.create_branch('org/project4', 'stable/havana')
        self.create_branch('org/project6', 'stable/havana')
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        C = self.fake_gerrit.addFakeChange('org/project2', 'master', 'C')
        D = self.fake_gerrit.addFakeChange('org/project3', 'stable/havana',
                                           'D')
        A.addApproval('Code-Review', 2)
        B.addApproval('Code-Review', 2)
        C.addApproval('Code-Review', 2)
        D.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(C.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(D.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(4, len(self.builds), "Four builds are running")

        upstream = self.getUpstreamRepos(projects)
        states = [
            {p1: dict(present=[A], absent=[B, C, D], branch='master'),
             p2: dict(commit=str(upstream[p2].commit('master')),
                      branch='master'),
             p3: dict(commit=str(upstream[p3].commit('master')),
                      branch='master'),
             p4: dict(commit=str(upstream[p4].commit('master')),
                      branch='master'),
             p5: dict(commit=str(upstream[p5].commit('master')),
                      branch='master'),
             p6: dict(commit=str(upstream[p6].commit('master')),
                      branch='master'),
             },
            {p1: dict(present=[A, B], absent=[C, D], branch='master'),
             p2: dict(commit=str(upstream[p2].commit('master')),
                      branch='master'),
             p3: dict(commit=str(upstream[p3].commit('master')),
                      branch='master'),
             p4: dict(commit=str(upstream[p4].commit('master')),
                      branch='master'),
             p5: dict(commit=str(upstream[p5].commit('master')),
                      branch='master'),
             p6: dict(commit=str(upstream[p6].commit('master')),
                      branch='master'),
             },
            {p1: dict(present=[A, B], absent=[C, D], branch='master'),
             p2: dict(present=[C], absent=[A, B, D], branch='master'),
             p3: dict(commit=str(upstream[p3].commit('master')),
                      branch='master'),
             p4: dict(commit=str(upstream[p4].commit('master')),
                      branch='master'),
             p5: dict(commit=str(upstream[p5].commit('master')),
                      branch='master'),
             p6: dict(commit=str(upstream[p6].commit('master')),
                      branch='master'),
             },
            {p1: dict(present=[A, B], absent=[C, D], branch='master'),
             p2: dict(present=[C], absent=[A, B, D], branch='master'),
             p3: dict(present=[D], absent=[A, B, C],
                      branch='stable/havana'),
             p4: dict(commit=str(upstream[p4].commit('master')),
                      branch='master'),
             p5: dict(commit=str(upstream[p5].commit('master')),
                      branch='master'),
             p6: dict(commit=str(upstream[p6].commit('stable/havana')),
                      branch='stable/havana'),
             },
        ]

        self.assertBuildStates(states, projects)

    def test_periodic_override(self):
        # This test can not use simple_layout because it must start
        # with a configuration which does not include a
        # timer-triggered job so that we have an opportunity to set
        # the hold flag before the first job.

        # This tests that we can override the branch in a timer
        # trigger (mostly to ensure backwards compatability for jobs).
        self.executor_server.hold_jobs_in_build = True

        p1 = 'review.example.com/org/project1'
        projects = [p1]
        self.create_branch('org/project1', 'stable/havana')

        # Start timer trigger - also org/project
        self.commitConfigUpdate('common-config',
                                'layouts/repo-checkout-timer-override.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))

        # The pipeline triggers every second, so we should have seen
        # several by now.
        time.sleep(5)
        self.waitUntilSettled()

        # Stop queuing timer triggered jobs so that the assertions
        # below don't race against more jobs being queued.
        self.commitConfigUpdate('common-config',
                                'layouts/repo-checkout-no-timer-override.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        # If APScheduler is in mid-event when we remove the job, we
        # can end up with one more event firing, so give it an extra
        # second to settle.
        time.sleep(1)
        self.waitUntilSettled()

        self.assertEqual(1, len(self.builds), "One build is running")

        upstream = self.getUpstreamRepos(projects)
        states = [
            {p1: dict(commit=str(upstream[p1].commit('stable/havana')),
                      branch='stable/havana'),
             },
        ]

        self.assertBuildStates(states, projects)

    def test_periodic(self):
        # This test can not use simple_layout because it must start
        # with a configuration which does not include a
        # timer-triggered job so that we have an opportunity to set
        # the hold flag before the first job.
        self.executor_server.hold_jobs_in_build = True
        # Start timer trigger - also org/project
        self.commitConfigUpdate('common-config',
                                'layouts/repo-checkout-timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))

        p1 = 'review.example.com/org/project1'
        projects = [p1]
        self.create_branch('org/project1', 'stable/havana')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'org/project1', 'stable/havana'))
        self.waitUntilSettled()

        # The pipeline triggers every second, so we should have seen
        # several by now.
        time.sleep(5)
        self.waitUntilSettled()

        # Stop queuing timer triggered jobs so that the assertions
        # below don't race against more jobs being queued.
        self.commitConfigUpdate('common-config',
                                'layouts/repo-checkout-no-timer.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()
        # If APScheduler is in mid-event when we remove the job, we
        # can end up with one more event firing, so give it an extra
        # second to settle.
        time.sleep(1)
        self.waitUntilSettled()

        self.assertEqual(2, len(self.builds), "Two builds are running")

        upstream = self.getUpstreamRepos(projects)
        states = [
            {p1: dict(commit=str(upstream[p1].commit('stable/havana')),
                      branch='stable/havana'),
             },
            {p1: dict(commit=str(upstream[p1].commit('master')),
                      branch='master'),
             },
        ]
        if self.builds[0].parameters['zuul']['ref'] == 'refs/heads/master':
            states = list(reversed(states))

        self.assertBuildStates(states, projects)

    @simple_layout('layouts/repo-checkout-post.yaml')
    def test_post_and_master_checkout(self):
        self.executor_server.hold_jobs_in_build = True
        p1 = "review.example.com/org/project1"
        p2 = "review.example.com/org/project2"
        projects = [p1, p2]
        upstream = self.getUpstreamRepos(projects)

        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        event = A.getRefUpdatedEvent()
        A.setMerged()
        A_commit = str(upstream[p1].commit('master'))
        self.log.debug("A commit: %s" % A_commit)

        # Add another commit to the repo that merged right after this
        # one to make sure that our post job runs with the one that we
        # intended rather than simply the current repo state.
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B',
                                           parent='refs/changes/01/1/1')
        B.setMerged()
        B_commit = str(upstream[p1].commit('master'))
        self.log.debug("B commit: %s" % B_commit)

        self.fake_gerrit.addEvent(event)
        self.waitUntilSettled()

        states = [
            {p1: dict(commit=A_commit,
                      present=[A], absent=[B], branch='master'),
             p2: dict(commit=str(upstream[p2].commit('master')),
                      absent=[A, B], branch='master'),
             },
        ]

        self.assertBuildStates(states, projects)

    @simple_layout('layouts/repo-checkout-tag.yaml')
    def test_tag_checkout(self):
        self.executor_server.hold_jobs_in_build = True
        p1 = "review.example.com/org/project1"
        p2 = "review.example.com/org/project2"
        projects = [p1, p2]
        upstream = self.getUpstreamRepos(projects)

        self.create_branch('org/project2', 'stable/havana')
        files = {'README': 'tagged readme'}
        self.addCommitToRepo('org/project2', 'tagged commit',
                             files, branch='stable/havana', tag='test-tag')

        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        states = [
            {p1: dict(present=[A], branch='master'),
             p2: dict(commit=str(upstream[p2].commit('test-tag')),
                      absent=[A]),
             },
        ]

        self.assertBuildStates(states, projects)


class TestAnsibleJob(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def run_job(self):
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        return list(self.executor_server.job_workers.values())[0]

    def test_host_keys(self):
        self.fake_nodepool.host_keys = ['fake-host-key']
        job = self.run_job()
        keys = job.host_list[0]['host_keys']
        self.assertEqual(keys[0], '127.0.0.1 fake-host-key')

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    def test_host_keys_connection_port(self):
        # Test with custom connection_port set
        self.fake_nodepool.host_keys = ['fake-host-key']
        self.fake_nodepool.connection_port = 22022
        job = self.run_job()
        keys = job.host_list[0]['host_keys']
        self.assertEqual(keys[0], '[127.0.0.1]:22022 fake-host-key')

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    def test_no_host_keys_connection_port(self):
        # Test with no host keys
        self.fake_nodepool.host_keys = []
        self.fake_nodepool.connection_port = 22022
        job = self.run_job()
        keys = job.host_list[0]['host_keys']
        self.assertEqual(keys, [])
        self.assertEqual(
            job.host_list[0]['host_vars']['ansible_ssh_common_args'],
            '-o StrictHostKeyChecking=false')

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    def test_no_shell_type(self):
        # Test without shell type set
        job = self.run_job()
        host = job.host_list[0]

        self.assertNotIn('ansible_shell_type', host['host_vars'])

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    def test_custom_shell_type(self):
        # Test with custom shell type set.
        self.fake_nodepool.shell_type = 'cmd'
        job = self.run_job()
        host = job.host_list[0]

        self.assertIn('ansible_shell_type', host['host_vars'])
        self.assertEqual(
            host['host_vars']['ansible_shell_type'],
            'cmd')

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()


class TestExecutorHostname(ZuulTestCase):
    config_file = 'zuul-executor-hostname.conf'
    tenant_config_file = 'config/single-tenant/main.yaml'

    def test_executor_hostname(self):
        self.assertEqual('test-executor-hostname.example.com',
                         self.executor_server.hostname)


class TestStartingBuildsSensor(ZuulTestCase):
    config_file = 'zuul.conf'
    tenant_config_file = 'config/governor/main.yaml'

    def test_default_case(self):
        # Given
        cores = multiprocessing.cpu_count()

        # When
        sensor = StartingBuildsSensor(None, cores * 2.5, None)

        # Then
        coefficient = 2 if multiprocessing.cpu_count() <= 4 else 1
        max_default = int(cores * 2.5 * coefficient)
        self.assertEqual(sensor.max_starting_builds, max_default)
        self.assertEqual(sensor.min_starting_builds, max(int(cores / 2), 1))

    def test_configuration_not_exists(self):
        # Given
        cores = multiprocessing.cpu_count()

        # When
        sensor = StartingBuildsSensor(None, cores * 2.5, self.config)

        # Then
        coefficient = 2 if multiprocessing.cpu_count() <= 4 else 1
        max_default = int(cores * 2.5 * coefficient)
        self.assertEqual(sensor.max_starting_builds, max_default)
        self.assertEqual(sensor.min_starting_builds, max(int(cores / 2), 1))

    def test_configuration_override(self):
        # Given
        cores = multiprocessing.cpu_count()
        self.config.set('executor', 'max_starting_builds', '5')

        # When
        sensor = StartingBuildsSensor(None, cores * 2.5, self.config)

        # Then
        self.assertEqual(sensor.max_starting_builds, 5)
        self.assertEqual(sensor.min_starting_builds, min(
            max(int(cores / 2), 1), sensor.max_starting_builds))

    def test_configuration_override_affecting_min(self):
        # Given
        cores = multiprocessing.cpu_count()
        self.config.set('executor', 'max_starting_builds', '1')

        # When
        sensor = StartingBuildsSensor(None, cores * 2.5, self.config)

        # Then
        self.assertEqual(sensor.max_starting_builds, 1)
        self.assertEqual(sensor.min_starting_builds, 1)


class TestGovernor(ZuulTestCase):
    config_file = 'zuul-executor-governor.conf'
    tenant_config_file = 'config/governor/main.yaml'

    @mock.patch('os.getloadavg')
    @mock.patch('psutil.virtual_memory')
    def test_load_governor(self, vm_mock, loadavg_mock):
        class Dummy(object):
            pass
        ram = Dummy()
        ram.percent = 20.0  # 20% used
        ram.total = 8 * 1024 * 1024 * 1024  # 8GiB
        vm_mock.return_value = ram
        loadavg_mock.return_value = (0.0, 0.0, 0.0)
        self.executor_server.manageLoad()
        self.assertTrue(self.executor_server.accepting_work)

        # fake the load to be higher than permitted
        fake_load = multiprocessing.cpu_count() * 2.6
        loadavg_mock.return_value = (fake_load, fake_load, fake_load)
        self.executor_server.manageLoad()
        self.assertFalse(self.executor_server.accepting_work)

    @mock.patch('os.getloadavg')
    @mock.patch('psutil.virtual_memory')
    def test_ram_governor(self, vm_mock, loadavg_mock):
        class Dummy(object):
            pass
        ram = Dummy()
        ram.percent = 20.0  # 20% used
        ram.total = 8 * 1024 * 1024 * 1024  # 8GiB
        vm_mock.return_value = ram
        loadavg_mock.return_value = (0.0, 0.0, 0.0)
        self.executor_server.manageLoad()
        self.assertTrue(self.executor_server.accepting_work)
        ram.percent = 99.0  # 99% used
        self.executor_server.manageLoad()
        self.assertFalse(self.executor_server.accepting_work)

    @mock.patch('os.getloadavg')
    @mock.patch('psutil.virtual_memory')
    def test_ram_cgroup_governor(self, vm_mock, loadavg_mock):
        class Dummy(object):
            pass
        ram = Dummy()
        ram.percent = 20.0  # 20% used
        ram.total = 8 * 1024 * 1024 * 1024  # 8GiB
        vm_mock.return_value = ram
        loadavg_mock.return_value = (0.0, 0.0, 0.0)

        # Set no cgroup limit
        ram_sensor = [x for x in self.executor_server.sensors
                      if isinstance(x, RAMSensor)][0]
        ram_sensor.cgroup_stats_file = os.path.join(
            FIXTURE_DIR, 'cgroup', 'memory.stat.nolimit')
        self.executor_server.manageLoad()
        self.assertTrue(self.executor_server.accepting_work)

        # Set cgroup limit 5GiB and ram usage 20%
        ram_sensor.cgroup_stats_file = os.path.join(
            FIXTURE_DIR, 'cgroup', 'memory.stat.ok')
        self.executor_server.manageLoad()
        self.assertTrue(self.executor_server.accepting_work)

        # Set cgroup limit 5GiB and ram usage 96%
        ram_sensor.cgroup_stats_file = os.path.join(
            FIXTURE_DIR, 'cgroup', 'memory.stat.bad')
        self.executor_server.manageLoad()
        self.assertFalse(self.executor_server.accepting_work)

    @mock.patch('os.getloadavg')
    @mock.patch('os.statvfs')
    def test_hdd_governor(self, statvfs_mock, loadavg_mock):
        class Dummy(object):
            pass
        hdd = Dummy()
        hdd.f_frsize = 4096
        hdd.f_blocks = 120920708
        hdd.f_bfree = 95716701
        statvfs_mock.return_value = hdd  # 20.84% used
        loadavg_mock.return_value = (0.0, 0.0, 0.0)

        self.executor_server.manageLoad()
        self.assertTrue(self.executor_server.accepting_work)

        self.assertReportedStat(
            'zuul.executor.test-executor-hostname_example_com.pct_used_hdd',
            value='2084', kind='g')

        hdd.f_bfree = 5716701
        statvfs_mock.return_value = hdd  # 95.27% used

        self.executor_server.manageLoad()
        self.assertFalse(self.executor_server.accepting_work)

        self.assertReportedStat(
            'zuul.executor.test-executor-hostname_example_com.pct_used_hdd',
            value='9527', kind='g')

    @mock.patch('os.getloadavg')
    def test_pause_governor(self, loadavg_mock):
        loadavg_mock.return_value = (0.0, 0.0, 0.0)

        self.executor_server.manageLoad()
        self.assertTrue(self.executor_server.accepting_work)

        self.executor_server.pause_sensor.pause = True
        self.executor_server.manageLoad()
        self.assertFalse(self.executor_server.accepting_work)

    def waitForExecutorBuild(self, jobname):
        self.log.debug("Waiting for %s to start", jobname)
        timeout = time.time() + 30
        build = None
        while time.time() < timeout and not build:
            for b in self.builds:
                if b.name == jobname:
                    build = b
                    break
            time.sleep(0.1)
        self.log.debug("Found build %s", jobname)
        build_id = build.uuid
        while (time.time() < timeout and
               build_id not in self.executor_server.job_workers):
            time.sleep(0.1)
        worker = self.executor_server.job_workers[build_id]
        self.log.debug("Found worker %s", jobname)
        while (time.time() < timeout and
               not worker.started):
            time.sleep(0.1)
        self.log.debug("Worker for %s started: %s", jobname, worker.started)
        return build

    @mock.patch('os.getloadavg')
    def test_slow_start(self, loadavg_mock):
        loadavg_mock.return_value = (0.0, 0.0, 0.0)

        def _set_starting_builds(min, max):
            for sensor in self.executor_server.sensors:
                if isinstance(sensor, StartingBuildsSensor):
                    sensor.min_starting_builds = min
                    sensor.max_starting_builds = max

        # Note: This test relies on the fact that manageLoad is only
        # run at specific points.  Several times in the test we check
        # that manageLoad has disabled or enabled job acceptance based
        # on the number of "starting" jobs.  Some of those jobs may
        # have actually moved past the "starting" phase and are
        # actually "running".  But because manageLoad hasn't run
        # again, it still uses the old values.  Keep this in mind when
        # double checking its calculations.
        #
        # Disable the periodic governor runs to make sure they don't
        # interefere (only possible if the test runs longer than 10
        # seconds).
        self.executor_server.governor_stop_event.set()
        self.executor_server.hold_jobs_in_build = True
        _set_starting_builds(1, 1)
        self.executor_server.manageLoad()
        self.assertTrue(self.executor_server.accepting_work)
        A = self.fake_gerrit.addFakeChange('common-config', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))

        build1 = self.waitForExecutorBuild('test1')
        # With one job (test1) being started, we should no longer
        # be accepting new work
        self.assertFalse(self.executor_server.accepting_work)
        self.assertEqual(len(self.executor_server.job_workers), 1)
        # Allow enough starting builds for the test to complete.
        _set_starting_builds(1, 3)
        # We must wait for build1 to enter a waiting state otherwise
        # the subsequent release() is a noop and the build is never
        # released.  We don't use waitUntilSettled as that requires
        # the other two builds to start which can't happen while we
        # don't accept jobs.
        for x in iterate_timeout(30, "build1 is waiting"):
            if build1.waiting:
                break
        build1.release()
        for x in iterate_timeout(30, "Wait for build1 to complete"):
            if build1.uuid not in self.executor_server.job_workers:
                break
        self.executor_server.manageLoad()
        # This manageLoad call has determined that there are 0 workers
        # running, so our full complement of 3 starting builds is
        # available.  It will re-register for work and pick up the
        # next two jobs.

        self.waitForExecutorBuild('test2')
        self.waitForExecutorBuild('test3')
        # When each of these jobs started, they caused manageLoad to
        # be called, the second invocation calculated that there were
        # 2 workers running, so our starting build limit was reduced
        # to 1.  Usually it will calculate that there are 2 starting
        # builds, but theoretically it could count only 1 if the first
        # build manages to leave the starting phase before the second
        # build starts.  It should always count the second build as
        # starting.  As long as at least one build is still in the
        # starting phase, this will exceed the limit and unregister.
        self.assertFalse(self.executor_server.accepting_work)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        self.executor_server.manageLoad()
        self.assertTrue(self.executor_server.accepting_work)


class TestLineMapping(AnsibleZuulTestCase):
    config_file = 'zuul-gerrit-web.conf'
    tenant_config_file = 'config/line-mapping/main.yaml'

    def test_line_mapping(self):
        header = 'add something to the top\n'
        footer = 'this is the change\n'

        with open(os.path.join(FIXTURE_DIR,
                               'config/line-mapping/git/',
                               'org_project/README')) as f:
            content = f.read()

        # The change under test adds a line to the end.
        file_dict = {'README': content + footer}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)

        # An intervening change adds a line to the top.
        file_dict = {'README': header + content}
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B',
                                           files=file_dict)
        B.setMerged()

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('file-comments').result,
                         'SUCCESS')
        self.assertEqual(len(A.comments), 2)
        comments = sorted(A.comments, key=lambda x: x['line'])
        self.assertEqual(comments[0],
                         {'file': 'README',
                          'line': 14,
                          'message': 'interesting comment',
                          'reviewer': {'email': 'zuul@example.com',
                                       'name': 'Zuul',
                                       'username': 'jenkins'}}
        )
        self.assertEqual(
            comments[1],
            {
                "file": "README",
                "line": 14,
                "message": "That's a cool section",
                "range": {
                    "end_character": 26,
                    "end_line": 14,
                    "start_character": 0,
                    "start_line": 12
                },
                "reviewer": {
                    "email": "zuul@example.com",
                    "name": "Zuul",
                    "username": "jenkins"
                }
            }
        )


class TestExecutorFacts(AnsibleZuulTestCase):
    tenant_config_file = 'config/executor-facts/main.yaml'

    def _get_file(self, build, path):
        p = os.path.join(build.jobdir.root, path)
        with open(p) as f:
            return f.read()

    def test_datetime_fact(self):
        self.executor_server.keep_jobdir = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getChangeMergedEvent())
        self.waitUntilSettled()

        self.assertEqual(self.getJobFromHistory('datetime-fact').result,
                         'SUCCESS')

        j = json.loads(self._get_file(self.history[0],
                                      'work/logs/job-output.json'))

        date_time = \
            j[0]['plays'][0]['tasks'][0]['hosts']['localhost']['date_time']
        self.assertEqual(18, len(date_time))


class TestAnsibleCallbackConfigs(AnsibleZuulTestCase):

    config_file = 'zuul-executor-ansible-callback.conf'
    tenant_config_file = 'config/ansible-callbacks/main.yaml'

    def test_ansible_callback_config(self):
        self.executor_server.keep_jobdir = True
        A = self.fake_gerrit.addFakeChange('common-config', 'master', 'A')
        self.fake_gerrit.addEvent(A.getChangeMergedEvent())
        self.waitUntilSettled()

        callbacks = [
            'callback_test_callback',
            'callback_nocows = True',
            'callback_nocows = False',
            'callback_\\nnocows = True',
            'callback_\\nnocows = False',
            'callback_ansible_interpolation'
        ]

        p = os.path.join(self.getJobFromHistory('callback-test').jobdir.root,
                         'ansible/playbook_0/ansible.cfg')
        self.assertEqual(self.getJobFromHistory('callback-test').result,
                         'SUCCESS')

        c = configparser.ConfigParser(interpolation=None)
        c.read(p)
        for callback in callbacks:
            self.assertIn(callback, c.sections())
        self.assertIn('test_field', c['callback_ansible_interpolation'])
        self.assertIn('test-%-value',
                      c['callback_ansible_interpolation']['test_field'])

        self.assertIn('file_name', c['callback_test_callback'])
        self.assertEqual('callback-success',
                         c['callback_test_callback']['file_name'])
        callback_result_file = os.path.join(
            self.getJobFromHistory('callback-test').jobdir.root,
            'trusted/project_0/review.example.com/',
            'common-config/playbooks/callback_plugins/',
            c['callback_test_callback']['file_name'])
        self.assertTrue(os.path.isfile(callback_result_file))


class TestExecutorEnvironment(AnsibleZuulTestCase):
    tenant_config_file = 'config/zuul-environment-filter/main.yaml'

    @mock.patch.dict('os.environ', {'ZUUL_TEST_VAR': 'some-value',
                                    'TEST_VAR': 'not-empty'})
    def test_zuul_environment_filter(self):
        A = self.fake_gerrit.addFakeChange('common-config', 'master', 'A')
        self.fake_gerrit.addEvent(A.getChangeMergedEvent())
        self.waitUntilSettled()

        self.assertEqual(
            self.getJobFromHistory('zuul-environment-filter').result,
            'SUCCESS')


class TestExecutorStart(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def setup_config(self, config_file: str):
        config = super(TestExecutorStart, self).setup_config(config_file)
        self.junk_dir = os.path.join(self.jobdir_root, 'junk')
        os.makedirs(self.junk_dir)
        return config

    def test_executor_start(self):
        self.assertFalse(os.path.exists(self.junk_dir))


class TestExecutorExtraPackages(AnsibleZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    test_package = 'pywinrm'

    def setUp(self):
        super(TestExecutorExtraPackages, self).setUp()
        import subprocess
        ansible_manager = self.executor_server.ansible_manager
        for version in ansible_manager._supported_versions:
            command = [ansible_manager.getAnsibleCommand(version, 'pip'),
                       'uninstall', '-y', self.test_package]
            # We want to error if the uninstall fails as the test below
            # relies on the package not being installed to be properly
            # exercised.
            s = subprocess.run(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
            self.log.info(s.stdout)
            self.assertEqual(s.returncode, 0)

    @mock.patch('zuul.lib.ansible.ManagedAnsible.extra_packages',
                new_callable=mock.PropertyMock)
    def test_extra_packages(self, mock_extra_packages):
        mock_extra_packages.return_value = [self.test_package]
        ansible_manager = self.executor_server.ansible_manager
        self.assertFalse(ansible_manager.validate())
        ansible_manager.install()
        self.assertTrue(ansible_manager.validate())


class TestVarSquash(BaseTestCase):
    def test_squash_variables(self):
        # Test that we correctly squash job variables
        nodeset = NodeSet()
        nodes = [
            {'name': 'node1', 'host_vars': {
                'host': 'node1_host',
                'extra': 'node1_extra',
            }},
            {'name': 'node2', 'host_vars': {
                'host': 'node2_host',
                'extra': 'node2_extra',
            }},
        ]
        nodeset.addGroup(Group('group1', ['node1']))
        nodeset.addGroup(Group('group2', ['node2']))
        groupvars = {
            'group1': {
                'host': 'group1_host',
                'group': 'group1_group',
                'extra': 'group1_extra',
            },
            'group2': {
                'host': 'group2_host',
                'group': 'group2_group',
                'extra': 'group2_extra',
            },
            'all': {
                'all2': 'groupvar_all2',
            }
        }
        jobvars = {
            'host': 'jobvar_host',
            'group': 'jobvar_group',
            'all': 'jobvar_all',
            'extra': 'jobvar_extra',
        }
        extravars = {
            'extra': 'extravar_extra',
        }
        out = squash_variables(
            nodes, nodeset, jobvars, groupvars, extravars)

        expected = {
            'node1': {
                'all': 'jobvar_all',
                'all2': 'groupvar_all2',
                'group': 'group1_group',
                'host': 'node1_host',
                'extra': 'extravar_extra'},
            'node2': {
                'all': 'jobvar_all',
                'all2': 'groupvar_all2',
                'group': 'group2_group',
                'host': 'node2_host',
                'extra': 'extravar_extra'},
        }
        self.assertEqual(out, expected)


class TestExecutorFailure(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    @mock.patch('zuul.executor.server.ExecutorServer.executeJob')
    def test_executor_job_start_failure(self, execute_job_mock):
        execute_job_mock.side_effect = Exception('Failed to start')
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertTrue(re.search(
            '- project-merge .* ERROR',
            A.messages[-1]))

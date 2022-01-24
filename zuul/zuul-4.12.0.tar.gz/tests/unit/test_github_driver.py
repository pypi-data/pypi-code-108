# Copyright 2015 GoodData
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
import os
import re
from testtools.matchers import MatchesRegex, Not, StartsWith
import urllib
import socket
import time
import textwrap
from unittest import mock, skip

import git
import github3.exceptions

from tests.fakegithub import FakeGithubEnterpriseClient
from zuul.driver.github.githubconnection import GithubShaCache
from zuul.zk.layout import LayoutState
import zuul.rpcclient
from zuul.lib import strings
from zuul.model import MergeRequest

from tests.base import (AnsibleZuulTestCase, BaseTestCase,
                        ZuulGithubAppTestCase, ZuulTestCase,
                        simple_layout, random_sha1)
from tests.base import ZuulWebFixture

EMPTY_LAYOUT_STATE = LayoutState("", "", 0, None, {})


class TestGithubDriver(ZuulTestCase):
    config_file = 'zuul-github-driver.conf'
    scheduler_count = 1

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_pull_event(self):
        self.executor_server.hold_jobs_in_build = True

        body = "This is the\nPR body."
        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A',
                                                 body=body)
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test1').result)
        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test2').result)

        job = self.getJobFromHistory('project-test2')
        zuulvars = job.parameters['zuul']
        self.assertEqual(str(A.number), zuulvars['change'])
        self.assertEqual(str(A.head_sha), zuulvars['patchset'])
        self.assertEqual('master', zuulvars['branch'])
        self.assertEquals('https://github.com/org/project/pull/1',
                          zuulvars['items'][0]['change_url'])
        expected = "A\n\n{}".format(body)
        self.assertEqual(zuulvars["message"],
                         strings.b64encode(expected))
        self.assertEqual(1, len(A.comments))
        self.assertThat(
            A.comments[0],
            MatchesRegex(r'.*\[project-test1 \]\(.*\).*', re.DOTALL))
        self.assertThat(
            A.comments[0],
            MatchesRegex(r'.*\[project-test2 \]\(.*\).*', re.DOTALL))
        self.assertEqual(2, len(self.history))

        # test_pull_unmatched_branch_event(self):
        self.create_branch('org/project', 'unmatched_branch')
        B = self.fake_github.openFakePullRequest(
            'org/project', 'unmatched_branch', 'B')
        self.fake_github.emitEvent(B.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        self.assertEqual(2, len(self.history))

        # now emit closed event without merging
        self.fake_github.emitEvent(A.getPullRequestClosedEvent())
        self.waitUntilSettled()

        # nothing should have happened due to the merged requirement
        self.assertEqual(2, len(self.history))

        # now merge the PR and emit the event again
        A.setMerged('merged')

        self.fake_github.emitEvent(A.getPullRequestClosedEvent())
        self.waitUntilSettled()

        # post job must be run
        self.assertEqual(3, len(self.history))

    @simple_layout('layouts/files-github.yaml', driver='github')
    def test_pull_matched_file_event(self):
        A = self.fake_github.openFakePullRequest(
            'org/project', 'master', 'A',
            files={'random.txt': 'test', 'build-requires': 'test'})
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        self.assertEqual(1, len(self.history))

        # test_pull_unmatched_file_event
        B = self.fake_github.openFakePullRequest('org/project', 'master', 'B',
                                                 files={'random.txt': 'test2'})
        self.fake_github.emitEvent(B.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        self.assertEqual(1, len(self.history))

    @simple_layout('layouts/files-github.yaml', driver='github')
    def test_pull_changed_files_length_mismatch(self):
        files = {'{:03d}.txt'.format(n): 'test' for n in range(300)}
        # File 301 which is not included in the list of files of the PR,
        # since Github only returns max. 300 files in alphabetical order
        files["foobar-requires"] = "test"
        A = self.fake_github.openFakePullRequest(
            'org/project', 'master', 'A', files=files)

        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        self.assertEqual(1, len(self.history))

    @simple_layout('layouts/files-github.yaml', driver='github')
    def test_pull_changed_files_length_mismatch_reenqueue(self):
        # Hold jobs so we can trigger a reconfiguration while the item is in
        # the pipeline
        self.executor_server.hold_jobs_in_build = True

        files = {'{:03d}.txt'.format(n): 'test' for n in range(300)}
        # File 301 which is not included in the list of files of the PR,
        # since Github only returns max. 300 files in alphabetical order
        files["foobar-requires"] = "test"
        A = self.fake_github.openFakePullRequest(
            'org/project', 'master', 'A', files=files)

        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # Comment on the pull request to trigger updateChange
        self.fake_github.emitEvent(A.getCommentAddedEvent('casual comment'))
        self.waitUntilSettled()

        # Trigger reconfig to enforce a reenqueue of the item
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        # Now we can release all jobs
        self.executor_server.hold_jobs_in_build = True
        self.executor_server.release()
        self.waitUntilSettled()

        # There must be exactly one successful job in the history. If there is
        # an aborted job in the history the reenqueue failed.
        self.assertHistory([
            dict(name='project-test1', result='SUCCESS',
                 changes="%s,%s" % (A.number, A.head_sha)),
        ])

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_pull_github_files_error(self):
        A = self.fake_github.openFakePullRequest(
            'org/project', 'master', 'A')

        with mock.patch("tests.fakegithub.FakePull.files") as files_mock:
            files_mock.side_effect = github3.exceptions.ServerError(
                mock.MagicMock())
            self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
            self.waitUntilSettled()
        self.assertEqual(1, files_mock.call_count)
        self.assertEqual(2, len(self.history))

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_comment_event(self):
        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')
        self.fake_github.emitEvent(A.getCommentAddedEvent('test me'))
        self.waitUntilSettled()
        self.assertEqual(2, len(self.history))

        # Test an unmatched comment, history should remain the same
        B = self.fake_github.openFakePullRequest('org/project', 'master', 'B')
        self.fake_github.emitEvent(B.getCommentAddedEvent('casual comment'))
        self.waitUntilSettled()
        self.assertEqual(2, len(self.history))

        # Test an unmatched comment, history should remain the same
        C = self.fake_github.openFakePullRequest('org/project', 'master', 'C')
        self.fake_github.emitEvent(
            C.getIssueCommentAddedEvent('a non-PR issue comment'))
        self.waitUntilSettled()
        self.assertEqual(2, len(self.history))

    @simple_layout('layouts/push-tag-github.yaml', driver='github')
    def test_tag_event(self):
        self.executor_server.hold_jobs_in_build = True

        self.create_branch('org/project', 'tagbranch')
        files = {'README.txt': 'test'}
        self.addCommitToRepo('org/project', 'test tag',
                             files, branch='tagbranch', tag='newtag')
        path = os.path.join(self.upstream_root, 'org/project')
        repo = git.Repo(path)
        tag = repo.tags['newtag']
        sha = tag.commit.hexsha
        del repo

        # Notify zuul about the new branch to load the config
        self.fake_github.emitEvent(
            self.fake_github.getPushEvent(
                'org/project',
                ref='refs/heads/%s' % 'tagbranch'))
        self.waitUntilSettled()

        # Record previous tenant reconfiguration time
        before = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)

        self.fake_github.emitEvent(
            self.fake_github.getPushEvent('org/project', 'refs/tags/newtag',
                                          new_rev=sha))
        self.waitUntilSettled()

        # Make sure the tenant hasn't been reconfigured due to the new tag
        after = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)
        self.assertEqual(before, after)

        build_params = self.builds[0].parameters
        self.assertEqual('refs/tags/newtag', build_params['zuul']['ref'])
        self.assertFalse('oldrev' in build_params['zuul'])
        self.assertEqual(sha, build_params['zuul']['newrev'])
        self.assertEqual(
            'https://github.com/org/project/releases/tag/newtag',
            build_params['zuul']['change_url'])
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-tag').result)

    @simple_layout('layouts/push-tag-github.yaml', driver='github')
    def test_push_event(self):
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')
        old_sha = '0' * 40
        new_sha = A.head_sha
        A.setMerged("merging A")
        pevent = self.fake_github.getPushEvent(project='org/project',
                                               ref='refs/heads/master',
                                               old_rev=old_sha,
                                               new_rev=new_sha)
        self.fake_github.emitEvent(pevent)
        self.waitUntilSettled()

        build_params = self.builds[0].parameters
        self.assertEqual('refs/heads/master', build_params['zuul']['ref'])
        self.assertFalse('oldrev' in build_params['zuul'])
        self.assertEqual(new_sha, build_params['zuul']['newrev'])
        self.assertEqual(
            'https://github.com/org/project/commit/%s' % new_sha,
            build_params['zuul']['change_url'])

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-post').result)
        self.assertEqual(1, len(self.history))

        # test unmatched push event
        old_sha = random_sha1()
        new_sha = random_sha1()
        self.fake_github.emitEvent(
            self.fake_github.getPushEvent('org/project',
                                          'refs/heads/unmatched_branch',
                                          old_sha, new_sha))
        self.waitUntilSettled()

        self.assertEqual(1, len(self.history))

    @simple_layout('layouts/labeling-github.yaml', driver='github')
    def test_labels(self):
        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')
        self.fake_github.emitEvent(A.addLabel('test'))
        self.waitUntilSettled()
        self.assertEqual(1, len(self.history))
        self.assertEqual('project-labels', self.history[0].name)
        self.assertEqual(['tests passed'], A.labels)

        # test label removed
        B = self.fake_github.openFakePullRequest('org/project', 'master', 'B')
        B.addLabel('do not test')
        self.fake_github.emitEvent(B.removeLabel('do not test'))
        self.waitUntilSettled()
        self.assertEqual(2, len(self.history))
        self.assertEqual('project-labels', self.history[1].name)
        self.assertEqual(['tests passed'], B.labels)

        # test unmatched label
        C = self.fake_github.openFakePullRequest('org/project', 'master', 'C')
        self.fake_github.emitEvent(C.addLabel('other label'))
        self.waitUntilSettled()
        self.assertEqual(2, len(self.history))
        self.assertEqual(['other label'], C.labels)

    @simple_layout('layouts/reviews-github.yaml', driver='github')
    def test_reviews(self):
        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')
        self.fake_github.emitEvent(A.getReviewAddedEvent('approve'))
        self.waitUntilSettled()
        self.assertEqual(1, len(self.history))
        self.assertEqual('project-reviews', self.history[0].name)
        self.assertEqual(['tests passed'], A.labels)

        # test_review_unmatched_event
        B = self.fake_github.openFakePullRequest('org/project', 'master', 'B')
        self.fake_github.emitEvent(B.getReviewAddedEvent('comment'))
        self.waitUntilSettled()
        self.assertEqual(1, len(self.history))

        # test sending reviews
        C = self.fake_github.openFakePullRequest('org/project', 'master', 'C')
        self.fake_github.emitEvent(C.getCommentAddedEvent(
            "I solemnly swear that I am up to no good"))
        self.waitUntilSettled()
        self.assertEqual('project-reviews', self.history[0].name)
        self.assertEqual(1, len(C.reviews))
        self.assertEqual('APPROVE', C.reviews[0].as_dict()['state'])

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_timer_event(self):
        self.executor_server.hold_jobs_in_build = True
        self.commitConfigUpdate('org/common-config',
                                'layouts/timer-github.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        time.sleep(2)
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 1)
        self.executor_server.hold_jobs_in_build = False
        # Stop queuing timer triggered jobs so that the assertions
        # below don't race against more jobs being queued.
        self.commitConfigUpdate('org/common-config',
                                'layouts/no-timer-github.yaml')
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
        ], ordered=False)

    @simple_layout('layouts/dequeue-github.yaml', driver='github')
    def test_dequeue_pull_synchronized(self):
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_github.openFakePullRequest(
            'org/one-job-project', 'master', 'A')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # event update stamp has resolution one second, wait so the latter
        # one has newer timestamp
        time.sleep(1)

        # On a push to a PR Github may emit a pull_request_review event with
        # the old head so send that right before the synchronized event.
        review_event = A.getReviewAddedEvent('dismissed')
        A.addCommit()
        self.fake_github.emitEvent(review_event)

        self.fake_github.emitEvent(A.getPullRequestSynchronizeEvent())
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(2, len(self.history))
        self.assertEqual(1, self.countJobResults(self.history, 'ABORTED'))

    @simple_layout('layouts/dequeue-github.yaml', driver='github')
    def test_dequeue_pull_abandoned(self):
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_github.openFakePullRequest(
            'org/one-job-project', 'master', 'A')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        self.fake_github.emitEvent(A.getPullRequestClosedEvent())
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(1, len(self.history))
        self.assertEqual(1, self.countJobResults(self.history, 'ABORTED'))

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_git_https_url(self):
        """Test that git_ssh option gives git url with ssh"""
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        _, project = tenant.getProject('org/project')

        url = self.fake_github.real_getGitUrl(project)
        self.assertEqual('https://github.com/org/project', url)

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_git_ssh_url(self):
        """Test that git_ssh option gives git url with ssh"""
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        _, project = tenant.getProject('org/project')

        url = self.fake_github_ssh.real_getGitUrl(project)
        self.assertEqual('ssh://git@github.com/org/project.git', url)

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_git_enterprise_url(self):
        """Test that git_url option gives git url with proper host"""
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        _, project = tenant.getProject('org/project')

        url = self.fake_github_ent.real_getGitUrl(project)
        self.assertEqual('ssh://git@github.enterprise.io/org/project.git', url)

    @simple_layout('layouts/reporting-github.yaml', driver='github')
    def test_reporting(self):
        project = 'org/project'
        github = self.fake_github.getGithubClient(None)

        # pipeline reports pull status both on start and success
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_github.openFakePullRequest(project, 'master', 'A')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # We should have a status container for the head sha
        self.assertIn(
            A.head_sha, github.repo_from_project(project)._commits.keys())
        statuses = self.fake_github.getCommitStatuses(project, A.head_sha)

        # We should only have one status for the head sha
        self.assertEqual(1, len(statuses))
        check_status = statuses[0]
        check_url = (
            'http://zuul.example.com/t/tenant-one/status/change/%s,%s' %
            (A.number, A.head_sha))
        self.assertEqual('tenant-one/check', check_status['context'])
        self.assertEqual('check status: pending',
                         check_status['description'])
        self.assertEqual('pending', check_status['state'])
        self.assertEqual(check_url, check_status['url'])
        self.assertEqual(0, len(A.comments))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        # We should only have two statuses for the head sha
        statuses = self.fake_github.getCommitStatuses(project, A.head_sha)
        self.assertEqual(2, len(statuses))
        check_status = statuses[0]
        check_url = 'http://zuul.example.com/t/tenant-one/buildset/'
        self.assertEqual('tenant-one/check', check_status['context'])
        self.assertEqual('check status: success',
                         check_status['description'])
        self.assertEqual('success', check_status['state'])
        self.assertThat(check_status['url'], StartsWith(check_url))
        self.assertEqual(1, len(A.comments))
        self.assertThat(A.comments[0],
                        MatchesRegex(r'.*Build succeeded.*', re.DOTALL))

        # pipeline does not report any status but does comment
        self.executor_server.hold_jobs_in_build = True
        self.fake_github.emitEvent(
            A.getCommentAddedEvent('reporting check'))
        self.waitUntilSettled()
        statuses = self.fake_github.getCommitStatuses(project, A.head_sha)
        self.assertEqual(2, len(statuses))
        # comments increased by one for the start message
        self.assertEqual(2, len(A.comments))
        self.assertThat(A.comments[1],
                        MatchesRegex(r'.*Starting reporting jobs.*',
                                     re.DOTALL))
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        # pipeline reports success status
        statuses = self.fake_github.getCommitStatuses(project, A.head_sha)
        self.assertEqual(3, len(statuses))
        report_status = statuses[0]
        self.assertEqual('tenant-one/reporting', report_status['context'])
        self.assertEqual('reporting status: success',
                         report_status['description'])
        self.assertEqual('success', report_status['state'])
        self.assertEqual(2, len(A.comments))

        base = 'http://zuul.example.com/t/tenant-one/buildset/'

        # Deconstructing the URL because we don't save the BuildSet UUID
        # anywhere to do a direct comparison and doing regexp matches on a full
        # URL is painful.

        # The first part of the URL matches the easy base string
        self.assertThat(report_status['url'], StartsWith(base))

        # The rest of the URL is a UUID
        self.assertThat(report_status['url'][len(base):],
                        MatchesRegex(r'^[a-fA-F0-9]{32}$'))

    @simple_layout('layouts/reporting-github.yaml', driver='github')
    def test_truncated_status_description(self):
        project = 'org/project'
        # pipeline reports pull status both on start and success
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_github.openFakePullRequest(project, 'master', 'A')
        self.fake_github.emitEvent(
            A.getCommentAddedEvent('long pipeline'))
        self.waitUntilSettled()
        statuses = self.fake_github.getCommitStatuses(project, A.head_sha)
        self.assertEqual(1, len(statuses))
        check_status = statuses[0]
        # Status is truncated due to long pipeline name
        self.assertEqual('status: pending',
                         check_status['description'])

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        # We should only have two statuses for the head sha
        statuses = self.fake_github.getCommitStatuses(project, A.head_sha)
        self.assertEqual(2, len(statuses))
        check_status = statuses[0]
        # Status is truncated due to long pipeline name
        self.assertEqual('status: success',
                         check_status['description'])

    @simple_layout('layouts/reporting-github.yaml', driver='github')
    def test_push_reporting(self):
        project = 'org/project2'
        # pipeline reports pull status both on start and success
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_github.openFakePullRequest(project, 'master', 'A')
        old_sha = '0' * 40
        new_sha = A.head_sha
        A.setMerged("merging A")
        pevent = self.fake_github.getPushEvent(project=project,
                                               ref='refs/heads/master',
                                               old_rev=old_sha,
                                               new_rev=new_sha)
        self.fake_github.emitEvent(pevent)
        self.waitUntilSettled()

        # there should only be one report, a status
        self.assertEqual(1, len(self.fake_github.github_data.reports))
        # Verify the user/context/state of the status
        status = ('zuul', 'tenant-one/push-reporting', 'pending')
        self.assertEqual(status, self.fake_github.github_data.reports[0][-1])

        # free the executor, allow the build to finish
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        # Now there should be a second report, the success of the build
        self.assertEqual(2, len(self.fake_github.github_data.reports))
        # Verify the user/context/state of the status
        status = ('zuul', 'tenant-one/push-reporting', 'success')
        self.assertEqual(status, self.fake_github.github_data.reports[-1][-1])

        # now make a PR which should also comment
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_github.openFakePullRequest(project, 'master', 'A')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # Now there should be a four reports, a new comment
        # and status
        self.assertEqual(4, len(self.fake_github.github_data.reports))
        self.executor_server.release()
        self.waitUntilSettled()

    @simple_layout("layouts/reporting-github.yaml", driver="github")
    def test_reporting_checks_api_unauthorized(self):
        # Using the checks API only works with app authentication. As all tests
        # within the TestGithubDriver class are executed without app
        # authentication, the checks API won't work here.

        project = "org/project3"
        github = self.fake_github.getGithubClient(None)

        # The pipeline reports pull request status both on start and success.
        # As we are not authenticated as app, this won't create or update any
        # check runs, but should post two comments (start, success) informing
        # the user about the missing authentication.
        A = self.fake_github.openFakePullRequest(project, "master", "A")
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        self.assertIn(
            A.head_sha, github.repo_from_project(project)._commits.keys()
        )
        check_runs = self.fake_github.getCommitChecks(project, A.head_sha)
        self.assertEqual(0, len(check_runs))

        expected_warning = (
            "Unable to create or update check tenant-one/checks-api-reporting."
            " Must be authenticated as app integration."
        )
        self.assertEqual(2, len(A.comments))
        self.assertIn(expected_warning, A.comments[0])
        self.assertIn(expected_warning, A.comments[1])

    @simple_layout('layouts/merging-github.yaml', driver='github')
    def test_report_pull_merge(self):
        # pipeline merges the pull request on success
        A = self.fake_github.openFakePullRequest('org/project', 'master',
                                                 'PR title',
                                                 body='I shouldnt be seen',
                                                 body_text='PR body')
        self.fake_github.emitEvent(A.getCommentAddedEvent('merge me'))
        self.waitUntilSettled()
        self.assertTrue(A.is_merged)
        self.assertThat(A.merge_message,
                        MatchesRegex(r'.*PR title\n\nPR body.*', re.DOTALL))
        self.assertThat(A.merge_message,
                        Not(MatchesRegex(
                            r'.*I shouldnt be seen.*',
                            re.DOTALL)))
        self.assertEqual(len(A.comments), 0)

        # pipeline merges the pull request on success after failure
        self.fake_github.merge_failure = True
        B = self.fake_github.openFakePullRequest('org/project', 'master', 'B')
        self.fake_github.emitEvent(B.getCommentAddedEvent('merge me'))
        self.waitUntilSettled()
        self.assertFalse(B.is_merged)
        self.assertEqual(len(B.comments), 1)
        self.assertEqual(B.comments[0],
                         'Pull request merge failed: Unknown merge failure')
        self.fake_github.merge_failure = False

        # pipeline merges the pull request on second run of merge
        # first merge failed on 405 Method Not Allowed error
        self.fake_github.merge_not_allowed_count = 1
        C = self.fake_github.openFakePullRequest('org/project', 'master', 'C')
        self.fake_github.emitEvent(C.getCommentAddedEvent('merge me'))
        self.waitUntilSettled()
        self.assertTrue(C.is_merged)

        # pipeline does not merge the pull request
        # merge failed on 405 Method Not Allowed error - twice
        self.fake_github.merge_not_allowed_count = 2
        D = self.fake_github.openFakePullRequest('org/project', 'master', 'D')
        self.fake_github.emitEvent(D.getCommentAddedEvent('merge me'))
        self.waitUntilSettled()
        self.assertFalse(D.is_merged)
        self.assertEqual(len(D.comments), 1)
        # Validate that the merge failure comment contains the message github
        # returned
        self.assertEqual(D.comments[0],
                         'Pull request merge failed: Merge not allowed '
                         'because of fake reason')

    @simple_layout('layouts/merging-github.yaml', driver='github')
    def test_report_pull_merge_message_reviewed_by(self):
        # pipeline merges the pull request on success
        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')

        self.fake_github.emitEvent(A.getCommentAddedEvent('merge me'))
        self.waitUntilSettled()
        self.assertTrue(A.is_merged)
        # assert that no 'Reviewed-By' is in merge commit message
        self.assertThat(A.merge_message,
                        Not(MatchesRegex(r'.*Reviewed-By.*', re.DOTALL)))

        B = self.fake_github.openFakePullRequest('org/project', 'master', 'B')
        B.addReview('derp', 'APPROVED')

        self.fake_github.emitEvent(B.getCommentAddedEvent('merge me'))
        self.waitUntilSettled()
        self.assertTrue(B.is_merged)
        # assert that single 'Reviewed-By' is in merge commit message
        self.assertThat(B.merge_message,
                        MatchesRegex(
                            r'.*Reviewed-by: derp <derp@example.com>.*',
                            re.DOTALL))

        C = self.fake_github.openFakePullRequest('org/project', 'master', 'C')
        C.addReview('derp', 'APPROVED')
        C.addReview('herp', 'COMMENTED')

        self.fake_github.emitEvent(C.getCommentAddedEvent('merge me'))
        self.waitUntilSettled()
        self.assertTrue(C.is_merged)
        # assert that multiple 'Reviewed-By's are in merge commit message
        self.assertThat(C.merge_message,
                        MatchesRegex(
                            r'.*Reviewed-by: derp <derp@example.com>.*',
                            re.DOTALL))
        self.assertThat(C.merge_message,
                        MatchesRegex(
                            r'.*Reviewed-by: herp <herp@example.com>.*',
                            re.DOTALL))

    @simple_layout('layouts/dependent-github.yaml', driver='github')
    def test_draft_pr(self):
        # pipeline merges the pull request on success
        A = self.fake_github.openFakePullRequest('org/project', 'master',
                                                 'PR title', draft=True)
        self.fake_github.emitEvent(A.addLabel('merge'))
        self.waitUntilSettled()

        # A draft pull request must not enter the gate
        self.assertFalse(A.is_merged)
        self.assertHistory([])

    @simple_layout('layouts/reporting-multiple-github.yaml', driver='github')
    def test_reporting_multiple_github(self):
        project = 'org/project1'
        github = self.fake_github.getGithubClient(None)

        # pipeline reports pull status both on start and success
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_github.openFakePullRequest(project, 'master', 'A')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        # open one on B as well, which should not effect A reporting
        B = self.fake_github.openFakePullRequest('org/project2', 'master',
                                                 'B')
        self.fake_github.emitEvent(B.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        # We should have a status container for the head sha
        statuses = self.fake_github.getCommitStatuses(project, A.head_sha)
        self.assertIn(
            A.head_sha, github.repo_from_project(project)._commits.keys())
        # We should only have one status for the head sha
        self.assertEqual(1, len(statuses))
        check_status = statuses[0]
        check_url = (
            'http://zuul.example.com/t/tenant-one/status/change/%s,%s' %
            (A.number, A.head_sha))
        self.assertEqual('tenant-one/check', check_status['context'])
        self.assertEqual('check status: pending', check_status['description'])
        self.assertEqual('pending', check_status['state'])
        self.assertEqual(check_url, check_status['url'])
        self.assertEqual(0, len(A.comments))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        # We should only have two statuses for the head sha
        statuses = self.fake_github.getCommitStatuses(project, A.head_sha)
        self.assertEqual(2, len(statuses))
        check_status = statuses[0]
        check_url = 'http://zuul.example.com/t/tenant-one/buildset/'
        self.assertEqual('tenant-one/check', check_status['context'])
        self.assertEqual('success', check_status['state'])
        self.assertEqual('check status: success', check_status['description'])
        self.assertThat(check_status['url'], StartsWith(check_url))
        self.assertEqual(1, len(A.comments))
        self.assertThat(A.comments[0],
                        MatchesRegex(r'.*Build succeeded.*', re.DOTALL))

    @simple_layout('layouts/dependent-github.yaml', driver='github')
    def test_parallel_changes(self):
        "Test that changes are tested in parallel and merged in series"

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')
        B = self.fake_github.openFakePullRequest('org/project', 'master', 'B')
        C = self.fake_github.openFakePullRequest('org/project', 'master', 'C')

        self.fake_github.emitEvent(A.addLabel('merge'))
        self.fake_github.emitEvent(B.addLabel('merge'))
        self.fake_github.emitEvent(C.addLabel('merge'))

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
        self.assertTrue(self.builds[2].hasChanges(A))
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

        all_builds = self.builds[:]
        self.release(all_builds[2])
        self.release(all_builds[3])
        self.waitUntilSettled()
        self.assertFalse(A.is_merged)
        self.assertFalse(B.is_merged)
        self.assertFalse(C.is_merged)

        self.release(all_builds[0])
        self.release(all_builds[1])
        self.waitUntilSettled()
        self.assertTrue(A.is_merged)
        self.assertTrue(B.is_merged)
        self.assertFalse(C.is_merged)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 0)
        self.assertEqual(len(self.history), 9)
        self.assertTrue(C.is_merged)

        self.assertNotIn('merge', A.labels)
        self.assertNotIn('merge', B.labels)
        self.assertNotIn('merge', C.labels)

    @simple_layout('layouts/dependent-github.yaml', driver='github')
    def test_failed_changes(self):
        "Test that a change behind a failed change is retested"
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')
        B = self.fake_github.openFakePullRequest('org/project', 'master', 'B')

        self.executor_server.failJob('project-test1', A)

        self.fake_github.emitEvent(A.addLabel('merge'))
        self.fake_github.emitEvent(B.addLabel('merge'))
        self.waitUntilSettled()

        self.executor_server.release('.*-merge')
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()

        self.waitUntilSettled()
        # It's certain that the merge job for change 2 will run, but
        # the test1 and test2 jobs may or may not run.
        self.assertTrue(len(self.history) > 6)
        self.assertFalse(A.is_merged)
        self.assertTrue(B.is_merged)
        self.assertNotIn('merge', A.labels)
        self.assertNotIn('merge', B.labels)

    @simple_layout('layouts/dependent-github.yaml', driver='github')
    def test_failed_change_at_head(self):
        "Test that if a change at the head fails, jobs behind it are canceled"

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')
        B = self.fake_github.openFakePullRequest('org/project', 'master', 'B')
        C = self.fake_github.openFakePullRequest('org/project', 'master', 'C')

        self.executor_server.failJob('project-test1', A)

        self.fake_github.emitEvent(A.addLabel('merge'))
        self.fake_github.emitEvent(B.addLabel('merge'))
        self.fake_github.emitEvent(C.addLabel('merge'))

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

        # project-test2, project-merge for B
        self.assertEqual(len(self.builds), 2)
        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 4)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 0)
        self.assertEqual(len(self.history), 15)
        self.assertFalse(A.is_merged)
        self.assertTrue(B.is_merged)
        self.assertTrue(C.is_merged)
        self.assertNotIn('merge', A.labels)
        self.assertNotIn('merge', B.labels)
        self.assertNotIn('merge', C.labels)

    def _test_push_event_reconfigure(self, project, branch,
                                     expect_reconfigure=False,
                                     old_sha=None, new_sha=None,
                                     modified_files=None,
                                     removed_files=None,
                                     expected_cat_jobs=None):
        pevent = self.fake_github.getPushEvent(
            project=project,
            ref='refs/heads/%s' % branch,
            old_rev=old_sha,
            new_rev=new_sha,
            modified_files=modified_files,
            removed_files=removed_files)

        # record previous tenant reconfiguration time, which may not be set
        old = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)
        self.waitUntilSettled()

        if expected_cat_jobs is not None:
            # clear the merge jobs history so we can count the cat jobs
            # issued during reconfiguration
            del self.merge_job_history

        self.fake_github.emitEvent(pevent)
        self.waitUntilSettled()
        new = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)

        if expect_reconfigure:
            # New timestamp should be greater than the old timestamp
            self.assertLess(old, new)
        else:
            # Timestamps should be equal as no reconfiguration shall happen
            self.assertEqual(old, new)

        if expected_cat_jobs is not None:
            # Check the expected number of cat jobs here as the (empty) config
            # of org/project should be cached.
            cat_jobs = self.merge_job_history.get(MergeRequest.CAT)
            self.assertEqual(expected_cat_jobs, len(cat_jobs), cat_jobs)

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_push_event_reconfigure(self):
        self._test_push_event_reconfigure('org/common-config', 'master',
                                          modified_files=['zuul.yaml'],
                                          old_sha='0' * 40,
                                          expect_reconfigure=True,
                                          expected_cat_jobs=1)

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_push_event_reconfigure_complex_branch(self):

        branch = 'feature/somefeature'
        project = 'org/common-config'

        # prepare an existing branch
        self.create_branch(project, branch)

        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project(project)
        repo._create_branch(branch)
        repo._set_branch_protection(branch, False)

        self.fake_github.emitEvent(
            self.fake_github.getPushEvent(
                project,
                ref='refs/heads/%s' % branch))
        self.waitUntilSettled()

        A = self.fake_github.openFakePullRequest(project, branch, 'A')
        old_sha = A.head_sha
        A.setMerged("merging A")
        new_sha = random_sha1()

        self._test_push_event_reconfigure(project, branch,
                                          expect_reconfigure=True,
                                          old_sha=old_sha,
                                          new_sha=new_sha,
                                          modified_files=['zuul.yaml'],
                                          expected_cat_jobs=1)

        # there are no exclude-unprotected-branches in the test class, so a
        # reconfigure shall occur
        repo._delete_branch(branch)

        self._test_push_event_reconfigure(project, branch,
                                          expect_reconfigure=True,
                                          old_sha=new_sha,
                                          new_sha='0' * 40,
                                          removed_files=['zuul.yaml'])

    # TODO(jlk): Make this a more generic test for unknown project
    @skip("Skipped for rewrite of webhook handler")
    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_ping_event(self):
        # Test valid ping
        pevent = {'repository': {'full_name': 'org/project'}}
        resp = self.fake_github.emitEvent(('ping', pevent))
        self.assertEqual(resp.status_code, 200, "Ping event didn't succeed")

        # Test invalid ping
        pevent = {'repository': {'full_name': 'unknown-project'}}
        self.assertRaises(
            urllib.error.HTTPError,
            self.fake_github.emitEvent,
            ('ping', pevent),
        )

    @simple_layout('layouts/gate-github.yaml', driver='github')
    def test_status_checks(self):
        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project('org/project')
        repo._set_branch_protection(
            'master', contexts=['tenant-one/check', 'tenant-one/gate'])

        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # since the required status 'tenant-one/check' is not fulfilled no
        # job is expected
        self.assertEqual(0, len(self.history))

        # now set a failing status 'tenant-one/check'
        repo = github.repo_from_project('org/project')
        repo.create_status(A.head_sha, 'failed', 'example.com', 'description',
                           'tenant-one/check')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        self.assertEqual(0, len(self.history))

        # now set a successful status followed by a failing status to check
        # that the later failed status wins
        repo.create_status(A.head_sha, 'success', 'example.com', 'description',
                           'tenant-one/check')
        repo.create_status(A.head_sha, 'failed', 'example.com', 'description',
                           'tenant-one/check')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        self.assertEqual(0, len(self.history))

        # now set the required status 'tenant-one/check'
        repo.create_status(A.head_sha, 'success', 'example.com', 'description',
                           'tenant-one/check')

        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # the change should have entered the gate
        self.assertEqual(2, len(self.history))

    # This test case verifies that no reconfiguration happens if a branch was
    # deleted that didn't contain configuration.
    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_no_reconfigure_on_non_config_branch_delete(self):
        branch = 'feature/somefeature'
        project = 'org/common-config'

        # prepare an existing branch
        self.create_branch(project, branch)

        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project(project)
        repo._create_branch(branch)
        repo._set_branch_protection(branch, False)

        A = self.fake_github.openFakePullRequest(project, branch, 'A')
        old_sha = A.head_sha
        A.setMerged("merging A")
        new_sha = random_sha1()

        self._test_push_event_reconfigure(project, branch,
                                          expect_reconfigure=False,
                                          old_sha=old_sha,
                                          new_sha=new_sha,
                                          modified_files=['README.md'])

        # Check if deleting that branch is ignored as well
        repo._delete_branch(branch)

        self._test_push_event_reconfigure(project, branch,
                                          expect_reconfigure=False,
                                          old_sha=new_sha,
                                          new_sha='0' * 40,
                                          modified_files=['README.md'])

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_client_dequeue_change_github(self):
        "Test that the RPC client can dequeue a github pull request"

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')

        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        client.dequeue(
            tenant='tenant-one',
            pipeline='check',
            project='org/project',
            change='{},{}'.format(A.number, A.head_sha),
            ref=None)

        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        check_pipeline = tenant.layout.pipelines['check']
        self.assertEqual(check_pipeline.getAllItems(), [])
        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 2)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_client_enqueue_change_github(self):
        "Test that the RPC client can enqueue a pull request"
        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.enqueue(tenant='tenant-one',
                           pipeline='check',
                           project='org/project',
                           trigger='github',
                           change='{},{}'.format(A.number, A.head_sha))
        self.waitUntilSettled()

        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(r, True)

        # check that change_url is correct
        job1_params = self.getJobFromHistory('project-test1').parameters
        job2_params = self.getJobFromHistory('project-test2').parameters
        self.assertEquals('https://github.com/org/project/pull/1',
                          job1_params['zuul']['items'][0]['change_url'])
        self.assertEquals('https://github.com/org/project/pull/1',
                          job2_params['zuul']['items'][0]['change_url'])

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_pull_commit_race(self):
        """Test graceful handling of delayed availability of commits"""

        github = self.fake_github.getGithubClient('org/project')
        repo = github.repo_from_project('org/project')
        repo.fail_not_found = 1

        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test1').result)
        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test2').result)

        job = self.getJobFromHistory('project-test2')
        zuulvars = job.parameters['zuul']
        self.assertEqual(str(A.number), zuulvars['change'])
        self.assertEqual(str(A.head_sha), zuulvars['patchset'])
        self.assertEqual('master', zuulvars['branch'])
        self.assertEqual(1, len(A.comments))
        self.assertThat(
            A.comments[0],
            MatchesRegex(r'.*\[project-test1 \]\(.*\).*', re.DOTALL))
        self.assertThat(
            A.comments[0],
            MatchesRegex(r'.*\[project-test2 \]\(.*\).*', re.DOTALL))
        self.assertEqual(2, len(self.history))

    @simple_layout('layouts/gate-github-cherry-pick.yaml', driver='github')
    def test_merge_method_cherry_pick(self):
        """
        Tests that the merge mode gets forwarded to the reporter and the
        merge fails because cherry-pick is not supported by github.
        """
        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project('org/project')
        repo._set_branch_protection(
            'master', contexts=['tenant-one/check', 'tenant-one/gate'])

        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        repo = github.repo_from_project('org/project')
        repo.create_status(A.head_sha, 'success', 'example.com', 'description',
                           'tenant-one/check')

        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # the change should have entered the gate
        self.assertEqual(2, len(self.history))

        # Merge should have failed because cherry-pick is not supported
        self.assertEqual(2, len(A.comments))
        self.assertFalse(A.is_merged)
        self.assertEquals(A.comments[1],
                          'Merge mode cherry-pick not supported by Github')

    @simple_layout('layouts/gate-github-squash-merge.yaml', driver='github')
    def test_merge_method_squash_merge(self):
        """
        Tests that the merge mode gets forwarded to the reporter and the
        merge fails because cherry-pick is not supported by github.
        """
        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project('org/project')
        repo._set_branch_protection(
            'master', contexts=['tenant-one/check', 'tenant-one/gate'])

        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        repo = github.repo_from_project('org/project')
        repo.create_status(A.head_sha, 'success', 'example.com', 'description',
                           'tenant-one/check')

        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # the change should have entered the gate
        self.assertEqual(2, len(self.history))

        # now check if the merge was done via rebase
        merges = [report for report in self.fake_github.github_data.reports
                  if report[2] == 'merge']
        assert(len(merges) == 1 and merges[0][3] == 'squash')

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_invalid_event(self):
        # Regression test to make sure the event forwarder thread continues
        # running in case the event from the GithubEventProcessor is None.
        self.fake_github.emitEvent(("pull_request", "invalid"))
        self.waitUntilSettled()

        A = self.fake_github.openFakePullRequest('org/project', 'master',
                                                 'A')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test1').result)
        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test2').result)


class TestMultiGithubDriver(ZuulTestCase):
    config_file = 'zuul-multi-github.conf'
    tenant_config_file = 'config/multi-github/main.yaml'
    scheduler_count = 1

    def test_multi_app(self):
        """Test that we can handle multiple app."""
        A = self.fake_github_ro.openFakePullRequest(
            'org/project', 'master', 'A')
        self.fake_github_ro.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        self.executor_server.release()
        self.waitUntilSettled()
        self.assertEqual(
            'SUCCESS',
            self.getJobFromHistory('project-test').result)


class TestGithubUnprotectedBranches(ZuulTestCase):
    config_file = 'zuul-github-driver.conf'
    tenant_config_file = 'config/unprotected-branches/main.yaml'
    scheduler_count = 1

    def test_unprotected_branches(self):
        tenant = self.scheds.first.sched.abide.tenants\
            .get('tenant-one')

        project1 = tenant.untrusted_projects[0]
        project2 = tenant.untrusted_projects[1]

        tpc1 = tenant.project_configs[project1.canonical_name]
        tpc2 = tenant.project_configs[project2.canonical_name]

        # project1 should have parsed master
        self.assertIn('master', tpc1.parsed_branch_config.keys())

        # project2 should have no parsed branch
        self.assertEqual(0, len(tpc2.parsed_branch_config.keys()))

        # now enable branch protection and trigger reload
        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project('org/project2')
        repo._set_branch_protection('master', True)

        pevent = self.fake_github.getPushEvent(project='org/project2',
                                               ref='refs/heads/master')
        self.fake_github.emitEvent(pevent)
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        tpc1 = tenant.project_configs[project1.canonical_name]
        tpc2 = tenant.project_configs[project2.canonical_name]

        # project1 and project2 should have parsed master now
        self.assertIn('master', tpc1.parsed_branch_config.keys())
        self.assertIn('master', tpc2.parsed_branch_config.keys())

    def test_filtered_branches_in_build(self):
        """
        Tests unprotected branches are filtered in builds if excluded
        """
        self.executor_server.keep_jobdir = True

        # Enable branch protection on org/project2@master
        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project('org/project2')
        self.create_branch('org/project2', 'feat-x')
        repo._set_branch_protection('master', True)

        # Enable branch protection on org/project3@stable. We'll use a PR on
        # this branch as a depends-on to validate that the stable branch
        # which is not protected in org/project2 is not filtered out.
        repo = github.repo_from_project('org/project3')
        self.create_branch('org/project3', 'stable')
        repo._set_branch_protection('stable', True)

        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        A = self.fake_github.openFakePullRequest('org/project3', 'stable', 'A')
        msg = "Depends-On: https://github.com/org/project1/pull/%s" % A.number
        B = self.fake_github.openFakePullRequest('org/project2', 'master', 'B',
                                                 body=msg)

        self.fake_github.emitEvent(B.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        build = self.history[0]
        path = os.path.join(
            build.jobdir.src_root, 'github.com', 'org/project2')
        build_repo = git.Repo(path)
        branches = [x.name for x in build_repo.branches]
        self.assertNotIn('feat-x', branches)

        self.assertHistory([
            dict(name='used-job', result='SUCCESS',
                 changes="%s,%s %s,%s" % (A.number, A.head_sha,
                                          B.number, B.head_sha)),
        ])

    def test_unfiltered_branches_in_build(self):
        """
        Tests unprotected branches are not filtered in builds if not excluded
        """
        self.executor_server.keep_jobdir = True

        # Enable branch protection on org/project1@master
        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project('org/project1')
        self.create_branch('org/project1', 'feat-x')
        repo._set_branch_protection('master', True)
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        A = self.fake_github.openFakePullRequest('org/project1', 'master', 'A')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        build = self.history[0]
        path = os.path.join(
            build.jobdir.src_root, 'github.com', 'org/project1')
        build_repo = git.Repo(path)
        branches = [x.name for x in build_repo.branches]
        self.assertIn('feat-x', branches)

        self.assertHistory([
            dict(name='project-test', result='SUCCESS',
                 changes="%s,%s" % (A.number, A.head_sha)),
        ])

    def test_unprotected_push(self):
        """Test that unprotected pushes don't cause tenant reconfigurations"""

        # Prepare repo with an initial commit
        A = self.fake_github.openFakePullRequest('org/project2', 'master', 'A')
        A.setMerged("merging A")

        # Do a push on top of A
        pevent = self.fake_github.getPushEvent(project='org/project2',
                                               old_rev=A.head_sha,
                                               ref='refs/heads/master',
                                               modified_files=['zuul.yaml'])

        # record previous tenant reconfiguration time, which may not be set
        old = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)
        self.waitUntilSettled()

        self.fake_github.emitEvent(pevent)
        self.waitUntilSettled()
        new = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)

        # We don't expect a reconfiguration because the push was to an
        # unprotected branch
        self.assertEqual(old, new)

        # now enable branch protection and trigger the push event again
        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project('org/project2')
        repo._set_branch_protection('master', True)

        self.fake_github.emitEvent(pevent)
        self.waitUntilSettled()
        new = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)

        # We now expect that zuul reconfigured itself
        self.assertLess(old, new)

    def test_protected_branch_delete(self):
        """Test that protected branch deletes trigger a tenant reconfig"""

        # Prepare repo with an initial commit and enable branch protection
        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project('org/project2')
        repo._set_branch_protection('master', True)
        self.fake_github.emitEvent(
            self.fake_github.getPushEvent(
                project='org/project2', ref='refs/heads/master'))

        A = self.fake_github.openFakePullRequest('org/project2', 'master', 'A')
        A.setMerged("merging A")

        # add a spare branch so that the project is not empty after master gets
        # deleted.
        repo._create_branch('feat-x')
        self.fake_github.emitEvent(
            self.fake_github.getPushEvent(
                project='org/project2', ref='refs/heads/feat-x'))

        self.waitUntilSettled()

        # record previous tenant reconfiguration time, which may not be set
        old = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)
        self.waitUntilSettled()

        # Delete the branch
        repo._delete_branch('master')
        pevent = self.fake_github.getPushEvent(project='org/project2',
                                               old_rev=A.head_sha,
                                               new_rev='0' * 40,
                                               ref='refs/heads/master',
                                               modified_files=['zuul.yaml'])

        self.fake_github.emitEvent(pevent)
        self.waitUntilSettled()
        new = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)

        # We now expect that zuul reconfigured itself as we deleted a protected
        # branch
        self.assertLess(old, new)

    # This test verifies that a PR is considered in case it was created for
    # a branch just has been set to protected before a tenant reconfiguration
    # took place.
    def test_reconfigure_on_pr_to_new_protected_branch(self):
        self.create_branch('org/project2', 'release')

        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project('org/project2')
        repo._set_branch_protection('master', True)
        repo._create_branch('release')
        repo._create_branch('feature')

        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        repo._set_branch_protection('release', True)

        self.executor_server.hold_jobs_in_build = True

        A = self.fake_github.openFakePullRequest(
            'org/project2', 'release', 'A')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('used-job').result)

        job = self.getJobFromHistory('used-job')
        zuulvars = job.parameters['zuul']
        self.assertEqual(str(A.number), zuulvars['change'])
        self.assertEqual(str(A.head_sha), zuulvars['patchset'])
        self.assertEqual('release', zuulvars['branch'])

        self.assertEqual(1, len(self.history))

    def _test_push_event_reconfigure(self, project, branch,
                                     expect_reconfigure=False,
                                     old_sha=None, new_sha=None,
                                     modified_files=None,
                                     removed_files=None,
                                     expected_cat_jobs=None):
        pevent = self.fake_github.getPushEvent(
            project=project,
            ref='refs/heads/%s' % branch,
            old_rev=old_sha,
            new_rev=new_sha,
            modified_files=modified_files,
            removed_files=removed_files)

        # record previous tenant reconfiguration time, which may not be set
        old = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)
        self.waitUntilSettled()

        if expected_cat_jobs is not None:
            # clear the merge jobs history so we can count the cat jobs
            # issued during reconfiguration
            del self.merge_job_history

        self.fake_github.emitEvent(pevent)
        self.waitUntilSettled()
        new = self.scheds.first.sched.tenant_layout_state.get(
            'tenant-one', EMPTY_LAYOUT_STATE)

        if expect_reconfigure:
            # New timestamp should be greater than the old timestamp
            self.assertLess(old, new)
        else:
            # Timestamps should be equal as no reconfiguration shall happen
            self.assertEqual(old, new)

        if expected_cat_jobs is not None:
            # Check the expected number of cat jobs here as the (empty) config
            # of org/project should be cached.
            cat_jobs = self.merge_job_history.get(MergeRequest.CAT, [])
            self.assertEqual(expected_cat_jobs, len(cat_jobs), cat_jobs)

    def test_push_event_reconfigure_complex_branch(self):

        branch = 'feature/somefeature'
        project = 'org/project2'

        # prepare an existing branch
        self.create_branch(project, branch)

        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project(project)
        repo._create_branch(branch)
        repo._set_branch_protection(branch, False)

        self.fake_github.emitEvent(
            self.fake_github.getPushEvent(
                project,
                ref='refs/heads/%s' % branch))
        self.waitUntilSettled()

        A = self.fake_github.openFakePullRequest(project, branch, 'A')
        old_sha = A.head_sha
        A.setMerged("merging A")
        new_sha = random_sha1()

        # branch is not protected, no reconfiguration even if config file
        self._test_push_event_reconfigure(project, branch,
                                          expect_reconfigure=False,
                                          old_sha=old_sha,
                                          new_sha=new_sha,
                                          modified_files=['zuul.yaml'],
                                          expected_cat_jobs=0)

        # branch is not protected: no reconfiguration
        repo._delete_branch(branch)

        self._test_push_event_reconfigure(project, branch,
                                          expect_reconfigure=False,
                                          old_sha=new_sha,
                                          new_sha='0' * 40,
                                          removed_files=['zuul.yaml'])


class TestGithubWebhook(ZuulTestCase):
    config_file = 'zuul-github-driver.conf'
    scheduler_count = 1

    def setUp(self):
        super(TestGithubWebhook, self).setUp()

        # Start the web server
        self.web = self.useFixture(
            ZuulWebFixture(self.changes, self.config,
                           self.additional_event_queues, self.upstream_root,
                           self.rpcclient, self.poller_events,
                           self.git_url_with_auth, self.addCleanup,
                           self.test_root))

        host = '127.0.0.1'
        # Wait until web server is started
        while True:
            port = self.web.port
            try:
                with socket.create_connection((host, port)):
                    break
            except ConnectionRefusedError:
                pass

        self.fake_github.setZuulWebPort(port)

    def tearDown(self):
        super(TestGithubWebhook, self).tearDown()

    @simple_layout('layouts/basic-github.yaml', driver='github')
    def test_webhook(self):
        """Test that we can get github events via zuul-web."""

        self.executor_server.hold_jobs_in_build = True

        A = self.fake_github.openFakePullRequest('org/project', 'master', 'A')
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent(),
                                   use_zuulweb=True)
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test1').result)
        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test2').result)

        job = self.getJobFromHistory('project-test2')
        zuulvars = job.parameters['zuul']
        self.assertEqual(str(A.number), zuulvars['change'])
        self.assertEqual(str(A.head_sha), zuulvars['patchset'])
        self.assertEqual('master', zuulvars['branch'])
        self.assertEqual(1, len(A.comments))
        self.assertThat(
            A.comments[0],
            MatchesRegex(r'.*\[project-test1 \]\(.*\).*', re.DOTALL))
        self.assertThat(
            A.comments[0],
            MatchesRegex(r'.*\[project-test2 \]\(.*\).*', re.DOTALL))
        self.assertEqual(2, len(self.history))

        # test_pull_unmatched_branch_event(self):
        self.create_branch('org/project', 'unmatched_branch')
        B = self.fake_github.openFakePullRequest(
            'org/project', 'unmatched_branch', 'B')
        self.fake_github.emitEvent(B.getPullRequestOpenedEvent(),
                                   use_zuulweb=True)
        self.waitUntilSettled()

        self.assertEqual(2, len(self.history))


class TestGithubShaCache(BaseTestCase):
    scheduler_count = 1

    def testInsert(self):
        cache = GithubShaCache()
        pr_dict = {
            'head': {
                'sha': '123456',
            },
            'number': 1,
            'state': 'open',
        }
        cache.update('foo/bar', pr_dict)
        self.assertEqual(cache.get('foo/bar', '123456'), set({1}))

    def testRemoval(self):
        cache = GithubShaCache()
        pr_dict = {
            'head': {
                'sha': '123456',
            },
            'number': 1,
            'state': 'open',
        }
        cache.update('foo/bar', pr_dict)
        self.assertEqual(cache.get('foo/bar', '123456'), set({1}))

        # Create 4096 entries so original falls off.
        for x in range(0, 4096):
            pr_dict['head']['sha'] = str(x)
            cache.update('foo/bar', pr_dict)
            cache.get('foo/bar', str(x))

        self.assertEqual(cache.get('foo/bar', '123456'), set())

    def testMultiInsert(self):
        cache = GithubShaCache()
        pr_dict = {
            'head': {
                'sha': '123456',
            },
            'number': 1,
            'state': 'open',
        }
        cache.update('foo/bar', pr_dict)
        self.assertEqual(cache.get('foo/bar', '123456'), set({1}))
        pr_dict['number'] = 2
        cache.update('foo/bar', pr_dict)
        self.assertEqual(cache.get('foo/bar', '123456'), set({1, 2}))

    def testMultiProjectInsert(self):
        cache = GithubShaCache()
        pr_dict = {
            'head': {
                'sha': '123456',
            },
            'number': 1,
            'state': 'open',
        }
        cache.update('foo/bar', pr_dict)
        self.assertEqual(cache.get('foo/bar', '123456'), set({1}))
        cache.update('foo/baz', pr_dict)
        self.assertEqual(cache.get('foo/baz', '123456'), set({1}))

    def testNoMatch(self):
        cache = GithubShaCache()
        pr_dict = {
            'head': {
                'sha': '123456',
            },
            'number': 1,
            'state': 'open',
        }
        cache.update('foo/bar', pr_dict)
        self.assertEqual(cache.get('bar/foo', '789'), set())
        self.assertEqual(cache.get('foo/bar', '789'), set())

    def testClosedPRRemains(self):
        cache = GithubShaCache()
        pr_dict = {
            'head': {
                'sha': '123456',
            },
            'number': 1,
            'state': 'closed',
        }
        cache.update('foo/bar', pr_dict)
        self.assertEqual(cache.get('foo/bar', '123456'), set({1}))


class TestGithubAppDriver(ZuulGithubAppTestCase):
    """Inheriting from ZuulGithubAppTestCase will enable app authentication"""
    config_file = 'zuul-github-driver.conf'
    scheduler_count = 1

    @simple_layout("layouts/reporting-github.yaml", driver="github")
    def test_reporting_checks_api(self):
        """Using the checks API only works with app authentication"""
        project = "org/project3"
        github = self.fake_github.getGithubClient(None)
        repo = github.repo_from_project('org/project3')
        repo._set_branch_protection(
            'master', contexts=['tenant-one/checks-api-reporting',
                                'tenant-one/gate'])

        # pipeline reports pull request status both on start and success
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_github.openFakePullRequest(project, "master", "A")
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # We should have a pending check for the head sha
        self.assertIn(
            A.head_sha, github.repo_from_project(project)._commits.keys())
        check_runs = self.fake_github.getCommitChecks(project, A.head_sha)

        self.assertEqual(1, len(check_runs))
        check_run = check_runs[0]

        self.assertEqual("tenant-one/checks-api-reporting", check_run["name"])
        self.assertEqual("in_progress", check_run["status"])
        self.assertThat(
            check_run["output"]["summary"],
            MatchesRegex(r'.*Starting checks-api-reporting jobs.*', re.DOTALL)
        )
        # The external id should be a json-string containing all relevant
        # information to uniquely identify this change.
        self.assertEqual(
            json.dumps(
                {
                    "tenant": "tenant-one",
                    "pipeline": "checks-api-reporting",
                    "change": 1
                }
            ),
            check_run["external_id"],
        )
        # A running check run should provide a custom abort action
        self.assertEqual(1, len(check_run["actions"]))
        self.assertEqual(
            {
                "identifier": "abort",
                "description": "Abort this check run",
                "label": "Abort",
            },
            check_run["actions"][0],
        )

        # TODO (felix): How can we test if the details_url was set correctly?
        # How can the details_url be configured on the test case?

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        # We should now have an updated status for the head sha
        check_runs = self.fake_github.getCommitChecks(project, A.head_sha)
        self.assertEqual(1, len(check_runs))
        check_run = check_runs[0]

        self.assertEqual("tenant-one/checks-api-reporting", check_run["name"])
        self.assertEqual("completed", check_run["status"])
        self.assertEqual("success", check_run["conclusion"])
        self.assertThat(
            check_run["output"]["summary"],
            MatchesRegex(r'.*Build succeeded.*', re.DOTALL)
        )
        self.assertIsNotNone(check_run["completed_at"])
        # A completed check run should not provide any custom actions
        self.assertEqual(0, len(check_run["actions"]))

        # Tell gate to merge to test checks requirements
        self.fake_github.emitEvent(A.getCommentAddedEvent('merge me'))
        self.waitUntilSettled()
        self.assertTrue(A.is_merged)

    @simple_layout("layouts/reporting-github.yaml", driver="github")
    def test_reporting_checks_api_dequeue(self):
        "Test that a dequeued change will be reported back to the check run"
        project = "org/project4"
        github = self.fake_github.getGithubClient(None)

        client = zuul.rpcclient.RPCClient(
            "127.0.0.1", self.gearman_server.port
        )
        self.addCleanup(client.shutdown)

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_github.openFakePullRequest(project, "master", "A")
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # We should have a pending check for the head sha
        self.assertIn(
            A.head_sha, github.repo_from_project(project)._commits.keys())
        check_runs = self.fake_github.getCommitChecks(project, A.head_sha)

        self.assertEqual(1, len(check_runs))
        check_run = check_runs[0]

        self.assertEqual(
            "tenant-one/checks-api-reporting-skipped", check_run["name"])
        self.assertEqual("in_progress", check_run["status"])
        self.assertThat(
            check_run["output"]["summary"],
            MatchesRegex(
                r'.*Starting checks-api-reporting-skipped jobs.*', re.DOTALL)
        )

        # Use the client to dequeue the pending change
        client.dequeue(
            tenant="tenant-one",
            pipeline="checks-api-reporting-skipped",
            project="org/project4",
            change="{},{}".format(A.number, A.head_sha),
            ref=None,
        )
        self.waitUntilSettled()

        # We should now have a skipped check run for the head sha
        check_runs = self.fake_github.getCommitChecks(project, A.head_sha)
        self.assertEqual(1, len(check_runs))
        check_run = check_runs[0]

        self.assertEqual(
            "tenant-one/checks-api-reporting-skipped", check_run["name"])
        self.assertEqual("completed", check_run["status"])
        self.assertEqual("skipped", check_run["conclusion"])
        self.assertThat(
            check_run["output"]["summary"],
            MatchesRegex(r'.*Build canceled.*', re.DOTALL)
        )
        self.assertIsNotNone(check_run["completed_at"])

    @simple_layout("layouts/reporting-github.yaml", driver="github")
    def test_update_non_existing_check_run(self):
        project = "org/project3"
        github = self.fake_github.getGithubClient(None)

        # Make check run creation fail
        github._data.fail_check_run_creation = True

        # pipeline reports pull request status both on start and success
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_github.openFakePullRequest(project, "master", "A")
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # We should have no pending check for the head sha
        commit = github.repo_from_project(project)._commits.get(A.head_sha)
        check_runs = commit.check_runs()
        self.assertEqual(0, len(check_runs))

        # Make check run creation work again
        github._data.fail_check_run_creation = False

        # Now run the build and check if the update of the check_run could
        # still be accomplished.
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        check_runs = self.fake_github.getCommitChecks(project, A.head_sha)
        self.assertEqual(1, len(check_runs))
        check_run = check_runs[0]

        self.assertEqual("tenant-one/checks-api-reporting", check_run["name"])
        self.assertEqual("completed", check_run["status"])
        self.assertEqual("success", check_run["conclusion"])
        self.assertThat(
            check_run["output"]["summary"],
            MatchesRegex(r'.*Build succeeded.*', re.DOTALL)
        )
        self.assertIsNotNone(check_run["completed_at"])
        # A completed check run should not provide any custom actions
        self.assertEqual(0, len(check_run["actions"]))

    @simple_layout("layouts/reporting-github.yaml", driver="github")
    def test_update_check_run_missing_permissions(self):
        project = "org/project3"
        github = self.fake_github.getGithubClient(None)

        repo = github.repo_from_project(project)
        repo._set_permission("checks", False)

        A = self.fake_github.openFakePullRequest(project, "master", "A")
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # Alghough we are authenticated as github app, we are lacking the
        # necessary "checks" permissions for the test repository. Thus, the
        # check run creation/update should fail and we end up in two comments
        # being posted to the PR with appropriate warnings.
        commit = github.repo_from_project(project)._commits.get(A.head_sha)
        check_runs = commit.check_runs()
        self.assertEqual(0, len(check_runs))

        self.assertIn(
            A.head_sha, github.repo_from_project(project)._commits.keys()
        )
        check_runs = self.fake_github.getCommitChecks(project, A.head_sha)
        self.assertEqual(0, len(check_runs))

        expected_warning = (
            "Failed to create check run tenant-one/checks-api-reporting: "
            "403 Resource not accessible by integration"
        )
        self.assertEqual(2, len(A.comments))
        self.assertIn(expected_warning, A.comments[0])
        self.assertIn(expected_warning, A.comments[1])

    @simple_layout("layouts/reporting-github.yaml", driver="github")
    def test_abort_check_run(self):
        "Test that we can dequeue a change by aborting the related check run"
        project = "org/project3"

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_github.openFakePullRequest(project, "master", "A")
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # We should have a pending check for the head sha that provides an
        # abort action.
        check_runs = self.fake_github.getCommitChecks(project, A.head_sha)

        self.assertEqual(1, len(check_runs))
        check_run = check_runs[0]
        self.assertEqual("tenant-one/checks-api-reporting", check_run["name"])
        self.assertEqual("in_progress", check_run["status"])
        self.assertEqual(1, len(check_run["actions"]))
        self.assertEqual("abort", check_run["actions"][0]["identifier"])
        self.assertEqual(
            {
                "tenant": "tenant-one",
                "pipeline": "checks-api-reporting",
                "change": 1
            },
            json.loads(check_run["external_id"])
        )

        # Simulate a click on the "Abort" button in Github by faking a webhook
        # event with our custom abort action.
        # Handling this event should dequeue the related change
        self.fake_github.emitEvent(A.getCheckRunAbortEvent(check_run))
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get("tenant-one")
        check_pipeline = tenant.layout.pipelines["check"]
        self.assertEqual(0, len(check_pipeline.getAllItems()))
        self.assertEqual(1, self.countJobResults(self.history, "ABORTED"))

        # The buildset was already dequeued, so there shouldn't be anything to
        # release.
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        # Since the change/buildset was dequeued, the check run should be
        # reported as cancelled and don't provide any further action.
        check_runs = self.fake_github.getCommitChecks(project, A.head_sha)
        self.assertEqual(1, len(check_runs))
        aborted_check_run = check_runs[0]

        self.assertEqual(
            "tenant-one/checks-api-reporting", aborted_check_run["name"]
        )
        self.assertEqual("completed", aborted_check_run["status"])
        self.assertEqual("cancelled", aborted_check_run["conclusion"])
        self.assertEqual(0, len(aborted_check_run["actions"]))


class TestCheckRunAnnotations(ZuulGithubAppTestCase, AnsibleZuulTestCase):
    """We need Github app authentication and be able to run Ansible jobs"""
    config_file = 'zuul-github-driver.conf'
    tenant_config_file = "config/github-file-comments/main.yaml"
    scheduler_count = 1

    def test_file_comments(self):
        project = "org/project"
        github = self.fake_github.getGithubClient(None)

        # The README file must be part of this PR to make the comment function
        # work. Thus we change it's content to provide some more text.
        files_dict = {
            "README": textwrap.dedent(
                """
                section one
                ===========

                here is some text
                and some more text
                and a last line of text

                section two
                ===========

                here is another section
                with even more text
                and the end of the section
                """
            ),
        }

        A = self.fake_github.openFakePullRequest(
            project, "master", "A", files=files_dict
        )
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # We should have a pending check for the head sha
        self.assertIn(
            A.head_sha, github.repo_from_project(project)._commits.keys())
        check_runs = self.fake_github.getCommitChecks(project, A.head_sha)

        self.assertEqual(1, len(check_runs))
        check_run = check_runs[0]

        self.assertEqual("tenant-one/check", check_run["name"])
        self.assertEqual("completed", check_run["status"])
        self.assertThat(
            check_run["output"]["summary"],
            MatchesRegex(r'.*Build succeeded.*', re.DOTALL)
        )

        annotations = check_run["output"]["annotations"]
        self.assertEqual(6, len(annotations))

        self.assertEqual(annotations[0], {
            "path": "README",
            "annotation_level": "warning",
            "message": "Simple line annotation",
            "start_line": 1,
            "end_line": 1,
        })

        self.assertEqual(annotations[1], {
            "path": "README",
            "annotation_level": "warning",
            "message": "Line annotation with level",
            "start_line": 2,
            "end_line": 2,
        })

        # As the columns are not part of the same line, they are ignored in the
        # annotation. Otherwise Github will complain about the request.
        self.assertEqual(annotations[2], {
            "path": "README",
            "annotation_level": "notice",
            "message": "simple range annotation",
            "start_line": 4,
            "end_line": 6,
        })

        self.assertEqual(annotations[3], {
            "path": "README",
            "annotation_level": "failure",
            "message": "Columns must be part of the same line",
            "start_line": 7,
            "end_line": 7,
            "start_column": 13,
            "end_column": 26,
        })

        # From the invalid/error file comments, only the "line out of file"
        # should remain. All others are excluded as they would result in
        # invalid Github requests, making the whole check run update fail.
        self.assertEqual(annotations[4], {
            "path": "README",
            "annotation_level": "warning",
            "message": "Line is not part of the file",
            "end_line": 9999,
            "start_line": 9999
        })

        self.assertEqual(annotations[5], {
            "path": "README",
            "annotation_level": "warning",
            "message": "Invalid level will fall back to warning",
            "start_line": 3,
            "end_line": 3,
        })

    def test_many_file_comments(self):
        # Test that we only send 50 comments to github
        project = "org/project"
        github = self.fake_github.getGithubClient(None)

        # The file must be part of this PR to make the comment function
        # work. Thus we change it's content to provide some more text.
        files_dict = {
            "bigfile": textwrap.dedent(
                """
                section one
                ===========

                here is some text
                """
            ),
        }

        A = self.fake_github.openFakePullRequest(
            project, "master", "A", files=files_dict
        )
        self.fake_github.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        # We should have a pending check for the head sha
        self.assertIn(
            A.head_sha, github.repo_from_project(project)._commits.keys())
        check_runs = self.fake_github.getCommitChecks(project, A.head_sha)

        self.assertEqual(1, len(check_runs))
        check_run = check_runs[0]

        self.assertEqual("tenant-one/check", check_run["name"])
        self.assertEqual("completed", check_run["status"])
        self.assertThat(
            check_run["output"]["summary"],
            MatchesRegex(r'.*Build succeeded.*', re.DOTALL)
        )

        annotations = check_run["output"]["annotations"]
        self.assertEqual(50, len(annotations))

        # Comments are sorted by uniqueness, so our most unique
        # comment is first.
        self.assertEqual(annotations[0], {
            "path": "bigfile",
            "annotation_level": "warning",
            "message": "Insightful comment",
            "start_line": 2,
            "end_line": 2,
        })
        # This comment appears 3 times.
        self.assertEqual(annotations[1], {
            "path": "bigfile",
            "annotation_level": "warning",
            "message": "Useful comment",
            "start_line": 1,
            "end_line": 1,
        })
        # The rest.
        self.assertEqual(annotations[4], {
            "path": "bigfile",
            "annotation_level": "warning",
            "message": "Annoying comment",
            "start_line": 1,
            "end_line": 1,
        })


class TestGithubDriverEnterise(ZuulGithubAppTestCase):
    config_file = 'zuul-github-driver-enterprise.conf'
    scheduler_count = 1

    @simple_layout('layouts/merging-github.yaml', driver='github')
    def test_report_pull_merge(self):
        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project('org/project')
        repo._set_branch_protection(
            'master', require_review=True)

        # pipeline merges the pull request on success
        A = self.fake_github.openFakePullRequest('org/project', 'master',
                                                 'PR title',
                                                 body='I shouldnt be seen',
                                                 body_text='PR body')

        self.fake_github.emitEvent(A.getCommentAddedEvent('merge me'))
        self.waitUntilSettled()

        # Since the PR was not approved it should not be merged
        self.assertFalse(A.is_merged)

        A.addReview('derp', 'APPROVED')
        self.fake_github.emitEvent(A.getCommentAddedEvent('merge me'))
        self.waitUntilSettled()

        # After approval it should be merged
        self.assertTrue(A.is_merged)
        self.assertThat(A.merge_message,
                        MatchesRegex(r'.*PR title\n\nPR body.*', re.DOTALL))
        self.assertThat(A.merge_message,
                        Not(MatchesRegex(
                            r'.*I shouldnt be seen.*',
                            re.DOTALL)))
        self.assertEqual(len(A.comments), 0)


class TestGithubDriverEnteriseLegacy(ZuulGithubAppTestCase):
    config_file = 'zuul-github-driver-enterprise.conf'
    scheduler_count = 1

    def setUp(self):
        self.old_version = FakeGithubEnterpriseClient.version
        FakeGithubEnterpriseClient.version = '2.19.0'

        super().setUp()

    def tearDown(self):
        super().tearDown()
        FakeGithubEnterpriseClient.version = self.old_version

    @simple_layout('layouts/merging-github.yaml', driver='github')
    def test_report_pull_merge(self):
        github = self.fake_github.getGithubClient()
        repo = github.repo_from_project('org/project')
        repo._set_branch_protection(
            'master', require_review=True)

        # pipeline merges the pull request on success
        A = self.fake_github.openFakePullRequest('org/project', 'master',
                                                 'PR title',
                                                 body='I shouldnt be seen',
                                                 body_text='PR body')

        self.fake_github.emitEvent(A.getCommentAddedEvent('merge me'))
        self.waitUntilSettled()

        # Note: PR was not approved but old github does not support
        # reviewDecision so this gets ignored and zuul merges nevertheless
        self.assertTrue(A.is_merged)
        self.assertThat(A.merge_message,
                        MatchesRegex(r'.*PR title\n\nPR body.*', re.DOTALL))
        self.assertThat(A.merge_message,
                        Not(MatchesRegex(
                            r'.*I shouldnt be seen.*',
                            re.DOTALL)))
        self.assertEqual(len(A.comments), 0)

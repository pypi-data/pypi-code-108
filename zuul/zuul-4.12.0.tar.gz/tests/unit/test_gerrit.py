# Copyright 2015 BMW Car IT GmbH
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
import textwrap
from unittest import mock

import tests.base
from tests.base import (
    AnsibleZuulTestCase,
    BaseTestCase,
    simple_layout,
    skipIfMultiScheduler,
    ZuulTestCase,
)
from zuul.driver.gerrit import GerritDriver
from zuul.driver.gerrit.gerritconnection import GerritConnection

FIXTURE_DIR = os.path.join(tests.base.FIXTURE_DIR, 'gerrit')


def read_fixture(file):
    with open('%s/%s' % (FIXTURE_DIR, file), 'r') as fixturefile:
        lines = fixturefile.readlines()
        command = lines[0].replace('\n', '')
        value = ''.join(lines[1:])
        return command, value


def read_fixtures(files):
    calls = []
    values = []
    for fixture_file in files:
        command, value = read_fixture(fixture_file)
        calls.append(mock.call(command))
        values.append([value, ''])
    return calls, values


class TestGerrit(BaseTestCase):

    @mock.patch('zuul.driver.gerrit.gerritconnection.GerritConnection._ssh')
    def run_query(self, files, expected_patches, _ssh_mock):
        gerrit_config = {
            'user': 'gerrit',
            'server': 'localhost',
        }
        driver = GerritDriver()
        gerrit = GerritConnection(driver, 'review_gerrit', gerrit_config)

        calls, values = read_fixtures(files)
        _ssh_mock.side_effect = values

        result = gerrit.simpleQuery('project:zuul/zuul')

        _ssh_mock.assert_has_calls(calls)
        self.assertEqual(len(calls), _ssh_mock.call_count,
                         '_ssh should be called %d times' % len(calls))
        self.assertIsNotNone(result, 'Result is not none')
        self.assertEqual(len(result), expected_patches,
                         'There must be %d patches.' % expected_patches)

    def test_simple_query_pagination_new(self):
        files = ['simple_query_pagination_new_1',
                 'simple_query_pagination_new_2']
        expected_patches = 5
        self.run_query(files, expected_patches)

    def test_simple_query_pagination_old(self):
        files = ['simple_query_pagination_old_1',
                 'simple_query_pagination_old_2',
                 'simple_query_pagination_old_3']
        expected_patches = 5
        self.run_query(files, expected_patches)

    def test_ref_name_check_rules(self):
        # See man git-check-ref-format for the rules referenced here
        test_strings = [
            ('refs/heads/normal', True),
            ('refs/heads/.bad', False),  # rule 1
            ('refs/heads/bad.lock', False),  # rule 1
            ('refs/heads/good.locked', True),
            ('refs/heads/go.od', True),
            ('refs/heads//bad', False),  # rule 6
            ('refs/heads/b?d', False),  # rule 5
            ('refs/heads/b[d', False),  # rule 5
            ('refs/heads/b..ad', False),  # rule 3
            ('bad', False),  # rule 2
            ('refs/heads/\nbad', False),  # rule 4
            ('/refs/heads/bad', False),  # rule 6
            ('refs/heads/bad/', False),  # rule 6
            ('refs/heads/bad.', False),  # rule 7
            ('.refs/heads/bad', False),  # rule 1
            ('refs/he@{ads/bad', False),  # rule 8
            ('@', False),  # rule 9
            ('refs\\heads/bad', False)  # rule 10
        ]

        for ref, accepted in test_strings:
            self.assertEqual(
                accepted,
                GerritConnection._checkRefFormat(ref),
                ref + ' shall be ' + ('accepted' if accepted else 'rejected'))

    def test_getGitURL(self):
        gerrit_config = {
            'user': 'gerrit',
            'server': 'localhost',
            'password': '1/badpassword',
        }
        # The 1/ in the password ensures we test the url encoding
        # path; this is the format of password we get from
        # googlesource.com.
        driver = GerritDriver()
        gerrit = GerritConnection(driver, 'review_gerrit', gerrit_config)
        project = gerrit.source.getProject('org/project')
        url = gerrit.source.getGitUrl(project)
        self.assertEqual(
            'https://gerrit:1%2Fbadpassword@localhost/org/project',
            url)

    def test_git_over_ssh_getGitURL(self):
        gerrit_config = {
            'user': 'gerrit',
            'server': 'localhost',
            'password': '1/badpassword',
            'git_over_ssh': 'true',
        }
        # The 1/ in the password ensures we test the url encoding
        # path; this is the format of password we get from
        # googlesource.com.
        driver = GerritDriver()
        gerrit = GerritConnection(driver, 'review_gerrit', gerrit_config)
        project = gerrit.source.getProject('org/project')
        url = gerrit.source.getGitUrl(project)
        self.assertEqual(
            'ssh://gerrit@localhost:29418/org/project',
            url)


class TestGerritWeb(ZuulTestCase):
    config_file = 'zuul-gerrit-web.conf'
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

    def test_dynamic_line_comment(self):
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: garbage-job
                garbage: True
            """)

        file_dict = {'.zuul.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(A.patchsets[0]['approvals'][0]['value'], "-1")
        self.assertEqual(A.patchsets[0]['approvals'][0]['__tag'],
                         "autogenerated:zuul:check")
        self.assertIn('Zuul encountered a syntax error',
                      A.messages[0])
        comments = sorted(A.comments, key=lambda x: x['line'])
        self.assertEqual(comments[0],
                         {'file': '.zuul.yaml',
                          'line': 4,
                          'message': "extra keys not allowed @ "
                                     "data['garbage']",
                          'range': {'end_character': 0,
                                    'end_line': 4,
                                    'start_character': 2,
                                    'start_line': 2},
                          'reviewer': {'email': 'zuul@example.com',
                                       'name': 'Zuul',
                                       'username': 'jenkins'}}
        )

    def test_message_too_long(self):
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: garbage-job
                %s
                garbage: True
            """
        ) % ('\n' * 16384)

        file_dict = {'.zuul.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(A.patchsets[0]['approvals'][0]['value'], "-1")
        self.assertEqual(A.patchsets[0]['approvals'][0]['__tag'],
                         "autogenerated:zuul:check")
        self.assertIn('... (truncated)',
                      A.messages[0])

    def test_dependent_dynamic_line_comment(self):
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: garbage-job
                garbage: True
            """)

        file_dict = {'.zuul.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        B.data['commitMessage'] = '%s\n\nDepends-On: %s\n' % (
            B.subject, A.data['id'])

        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(B.patchsets[0]['approvals'][0]['value'], "-1")
        self.assertIn('This change depends on a change '
                      'with an invalid configuration',
                      B.messages[0])
        self.assertEqual(B.comments, [])

    @simple_layout('layouts/single-file-matcher.yaml')
    def test_single_file(self):
        # HTTP requests don't return a commit_msg entry in the files
        # list, but the rest of zuul always expects one.  This test
        # returns a single file to exercise the single-file code path
        # in the files matcher.
        files = {'README': 'please!\n'}

        change = self.fake_gerrit.addFakeChange('org/project',
                                                'master',
                                                'test irrelevant-files',
                                                files=files)
        self.fake_gerrit.addEvent(change.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        tested_change_ids = [x.changes[0] for x in self.history
                             if x.name == 'project-test-irrelevant-files']

        self.assertEqual([], tested_change_ids)

    def test_recheck(self):
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertEqual(3, len(self.history))

        self.fake_gerrit.addEvent(A.getChangeCommentEvent(1))
        self.waitUntilSettled()
        self.assertEqual(3, len(self.history))

        self.fake_gerrit.addEvent(A.getChangeCommentEvent(1,
                                  'recheck'))
        self.waitUntilSettled()
        self.assertEqual(6, len(self.history))

        self.fake_gerrit.addEvent(A.getChangeCommentEvent(1,
                                  patchsetcomment='recheck'))
        self.waitUntilSettled()
        self.assertEqual(9, len(self.history))

        self.fake_gerrit.addEvent(A.getChangeCommentEvent(1,
                                  patchsetcomment='do not recheck'))
        self.waitUntilSettled()
        self.assertEqual(9, len(self.history))


class TestFileComments(AnsibleZuulTestCase):
    config_file = 'zuul-gerrit-web.conf'
    tenant_config_file = 'config/gerrit-file-comments/main.yaml'

    def test_file_comments(self):
        A = self.fake_gerrit.addFakeChange(
            'org/project', 'master', 'A',
            files={'path/to/file.py': 'test1',
                   'otherfile.txt': 'test2',
                   })
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertEqual(self.getJobFromHistory('file-comments').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('file-comments-error').result,
                         'SUCCESS')
        self.assertEqual(len(A.comments), 6)
        comments = sorted(A.comments, key=lambda x: (x['file'], x['line']))
        self.assertEqual(
            comments[0],
            {
                'file': 'otherfile.txt',
                'line': 21,
                'message': 'This is a much longer message.\n\n'
                'With multiple paragraphs.\n',
                'reviewer': {
                    'email': 'zuul@example.com',
                    'name': 'Zuul',
                    'username': 'jenkins'
                },
            },
        )

        self.assertEqual(
            comments[1],
            {
                "file": "path/to/file.py",
                "line": 2,
                "message": "levels are ignored by gerrit",
                "reviewer": {
                    "email": "zuul@example.com",
                    "name": "Zuul",
                    "username": "jenkins",
                },
            },
        )

        self.assertEqual(
            comments[2],
            {
                "file": "path/to/file.py",
                "line": 21,
                "message": (
                    "A second zuul return value using the same file should not"
                    "\noverride the first result, but both should be merged.\n"
                ),
                "reviewer": {
                    "email": "zuul@example.com",
                    "name": "Zuul",
                    "username": "jenkins",
                },
            },
        )

        self.assertEqual(
            comments[3],
            {
                'file': 'path/to/file.py',
                'line': 42,
                'message': 'line too long',
                'reviewer': {
                    'email': 'zuul@example.com',
                    'name': 'Zuul',
                    'username': 'jenkins'
                },
            },
        )

        self.assertEqual(
            comments[4],
            {
                "file": "path/to/file.py",
                "line": 42,
                "message": (
                    "A second comment applied to the same line in the same "
                    "file\nshould also be added to the result.\n"
                ),
                "reviewer": {
                    "email": "zuul@example.com",
                    "name": "Zuul",
                    "username": "jenkins",
                }
            }
        )

        self.assertEqual(comments[5],
                         {'file': 'path/to/file.py',
                          'line': 82,
                          'message': 'line too short',
                          'reviewer': {'email': 'zuul@example.com',
                                       'name': 'Zuul',
                                       'username': 'jenkins'}}
        )
        self.assertIn('expected a dictionary', A.messages[0],
                      "A should have a validation error reported")
        self.assertIn('invalid file missingfile.txt', A.messages[0],
                      "A should have file error reported")


class TestChecksApi(ZuulTestCase):
    config_file = 'zuul-gerrit-web.conf'

    @simple_layout('layouts/gerrit-checks.yaml')
    def test_check_pipeline(self):
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.setDependsOn(B, 1)
        A.setCheck('zuul:check', reset=True)
        self.waitForPoll('gerrit')
        self.waitUntilSettled()

        self.assertEqual(A.checks_history[0]['zuul:check']['state'],
                         'NOT_STARTED')

        self.assertEqual(A.checks_history[1]['zuul:check']['state'],
                         'SCHEDULED')
        self.assertEqual(
            A.checks_history[1]['zuul:check']['url'],
            'http://zuul.example.com/t/tenant-one/status/change/2,1')

        self.assertEqual(A.checks_history[2]['zuul:check']['state'],
                         'RUNNING')
        self.assertEqual(
            A.checks_history[2]['zuul:check']['url'],
            'http://zuul.example.com/t/tenant-one/status/change/2,1')

        self.assertEqual(A.checks_history[3]['zuul:check']['state'],
                         'SUCCESSFUL')
        self.assertTrue(
            A.checks_history[3]['zuul:check']['url'].startswith(
                'http://zuul.example.com/t/tenant-one/buildset/'))

        self.assertEqual(len(A.checks_history), 4)

        self.assertTrue(isinstance(
            A.checks_history[3]['zuul:check']['started'], str))
        self.assertTrue(isinstance(
            A.checks_history[3]['zuul:check']['finished'], str))
        self.assertTrue(
            A.checks_history[3]['zuul:check']['finished'] >
            A.checks_history[3]['zuul:check']['started'])
        self.assertEqual(A.checks_history[3]['zuul:check']['message'],
                         'Change passed all voting jobs')
        self.assertHistory([
            dict(name='test-job', result='SUCCESS', changes='1,1 2,1')])
        self.assertEqual(A.reported, 0, "no messages should be reported")
        self.assertEqual(A.messages, [], "no messages should be reported")
        # Make sure B was never updated
        self.assertEqual(len(B.checks_history), 0)

    @simple_layout('layouts/gerrit-checks.yaml')
    def test_gate_pipeline(self):
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        A.addApproval('Approved', 1)
        A.setCheck('zuul:gate', reset=True)
        self.waitForPoll('gerrit')
        self.waitUntilSettled()

        self.assertEqual(A.checks_history[0]['zuul:gate']['state'],
                         'NOT_STARTED')
        self.assertEqual(A.checks_history[1]['zuul:gate']['state'],
                         'SCHEDULED')
        self.assertEqual(A.checks_history[2]['zuul:gate']['state'],
                         'RUNNING')
        self.assertEqual(A.checks_history[3]['zuul:gate']['state'],
                         'SUCCESSFUL')
        self.assertEqual(len(A.checks_history), 4)
        self.assertHistory([
            dict(name='test-job', result='SUCCESS', changes='1,1')])
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertEqual(A.reported, 2,
                         "start and success messages should be reported")

    @simple_layout('layouts/gerrit-checks-scheme.yaml')
    @skipIfMultiScheduler()
    # This is the only gerrit checks API test which is failing because
    # it uses a check scheme rather than an UUID. The scheme must first
    # be evaluated and mapped to an UUID.
    # This shouldn't be a problem in production as the evaluation takes
    # place on the gerrit webserver. However, in the tests we get a
    # dedicated (fake) gerrit webserver for each fake gerrrit
    # connection. Since each scheduler gets a new connection, only one
    # of those webservers will be aware of the check. If any other
    # webserver tries to evaluate the check it will fail with
    # "Unable to find matching checker".
    def test_check_pipeline_scheme(self):
        self.fake_gerrit.addFakeChecker(uuid='zuul_check:abcd',
                                        repository='org/project',
                                        status='ENABLED')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))
        self.waitUntilSettled()

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.setCheck('zuul_check:abcd', reset=True)
        self.waitForPoll('gerrit')
        self.waitUntilSettled()

        self.assertEqual(A.checks_history[0]['zuul_check:abcd']['state'],
                         'NOT_STARTED')
        self.assertEqual(A.checks_history[1]['zuul_check:abcd']['state'],
                         'SCHEDULED')
        self.assertEqual(A.checks_history[2]['zuul_check:abcd']['state'],
                         'RUNNING')
        self.assertEqual(A.checks_history[3]['zuul_check:abcd']['state'],
                         'SUCCESSFUL')
        self.assertEqual(len(A.checks_history), 4)
        self.assertHistory([
            dict(name='test-job', result='SUCCESS', changes='1,1')])

    @simple_layout('layouts/gerrit-checks-nojobs.yaml')
    def test_no_jobs(self):
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.setCheck('zuul:check', reset=True)
        self.waitForPoll('gerrit')
        self.waitUntilSettled()

        self.assertEqual(A.checks_history[0]['zuul:check']['state'],
                         'NOT_STARTED')
        self.assertEqual(A.checks_history[1]['zuul:check']['state'],
                         'SCHEDULED')
        self.assertEqual(A.checks_history[2]['zuul:check']['state'],
                         'NOT_RELEVANT')
        self.assertEqual(len(A.checks_history), 3)
        self.assertEqual(A.data['status'], 'NEW')

    @simple_layout('layouts/gerrit-checks.yaml')
    def test_config_error(self):
        # Test that line comments are reported on config errors
        in_repo_conf = textwrap.dedent(
            """
            - project:
                check:
                  jobs:
                    - bad-job
            """)
        file_dict = {'.zuul.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        A.setCheck('zuul:check', reset=True)
        self.waitForPoll('gerrit')
        self.waitUntilSettled()

        self.assertEqual(A.checks_history[0]['zuul:check']['state'],
                         'NOT_STARTED')
        self.assertEqual(A.checks_history[1]['zuul:check']['state'],
                         'SCHEDULED')
        self.assertEqual(A.checks_history[2]['zuul:check']['state'],
                         'FAILED')
        self.assertEqual(len(A.checks_history), 3)
        comments = sorted(A.comments, key=lambda x: x['line'])
        self.assertEqual(comments[0],
                         {'file': '.zuul.yaml',
                          'line': 5,
                          'message': 'Job bad-job not defined',
                          'range': {'end_character': 0,
                                    'end_line': 5,
                                    'start_character': 2,
                                    'start_line': 2},
                          'reviewer': {'email': 'zuul@example.com',
                                       'name': 'Zuul',
                                       'username': 'jenkins'}}
        )
        self.assertEqual(A.reported, 0, "no messages should be reported")
        self.assertEqual(A.messages, [], "no messages should be reported")

    @simple_layout('layouts/gerrit-checks.yaml')
    def test_new_patchset(self):
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.setCheck('zuul:check', reset=True)
        self.waitForPoll('gerrit')
        self.waitUntilSettled()

        self.assertEqual(A.checks_history[0]['zuul:check']['state'],
                         'NOT_STARTED')
        self.assertEqual(A.checks_history[1]['zuul:check']['state'],
                         'SCHEDULED')
        self.assertEqual(A.checks_history[2]['zuul:check']['state'],
                         'RUNNING')
        self.assertEqual(len(A.checks_history), 3)

        A.addPatchset()
        A.setCheck('zuul:check', reset=True)
        self.waitForPoll('gerrit')
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()
        self.log.info(A.checks_history)
        self.assertEqual(A.checks_history[3]['zuul:check']['state'],
                         'NOT_STARTED')
        self.assertEqual(A.checks_history[4]['zuul:check']['state'],
                         'SCHEDULED')
        self.assertEqual(A.checks_history[5]['zuul:check']['state'],
                         'RUNNING')
        self.assertEqual(A.checks_history[6]['zuul:check']['state'],
                         'SUCCESSFUL')
        self.assertEqual(len(A.checks_history), 7)
        self.assertHistory([
            dict(name='test-job', result='ABORTED', changes='1,1'),
            dict(name='test-job', result='SUCCESS', changes='1,2'),
        ], ordered=False)


class TestPolling(ZuulTestCase):
    config_file = 'zuul-gerrit-no-stream.conf'

    @simple_layout('layouts/gerrit-checks.yaml')
    def test_config_update(self):
        # Test that the config is updated via polling when a change
        # merges without stream-events enabled.
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: test-job2
                parent: test-job
            - project:
                check:
                  jobs:
                    - test-job2
            """)

        file_dict = {'.zuul.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        A.setMerged()
        self.waitForPoll('gerrit')

        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        B.setCheck('zuul:check', reset=True)
        self.waitForPoll('gerrit')
        self.waitUntilSettled()

        self.assertEqual(B.checks_history[0]['zuul:check']['state'],
                         'NOT_STARTED')
        self.assertEqual(B.checks_history[1]['zuul:check']['state'],
                         'SCHEDULED')
        self.assertEqual(B.checks_history[2]['zuul:check']['state'],
                         'RUNNING')
        self.assertEqual(B.checks_history[3]['zuul:check']['state'],
                         'SUCCESSFUL')
        self.assertEqual(len(B.checks_history), 4)
        self.assertHistory([
            dict(name='test-job', result='SUCCESS', changes='2,1'),
            dict(name='test-job2', result='SUCCESS', changes='2,1'),
        ], ordered=False)

    @simple_layout('layouts/gerrit-poll-post.yaml')
    def test_post(self):
        # Test that ref-updated events trigger post jobs.
        self.waitUntilSettled()
        # Wait for an initial poll to get the original sha.
        self.waitForPoll('gerrit-ref')

        # Merge a change.
        self.create_commit('org/project')

        # Wait for the job to run.
        self.waitForPoll('gerrit-ref')
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='post-job', result='SUCCESS'),
        ])

    @simple_layout('layouts/gerrit-poll-post.yaml')
    def test_tag(self):
        # Test that ref-updated events trigger post jobs.
        self.waitUntilSettled()
        # Wait for an initial poll to get the original sha.
        self.waitForPoll('gerrit-ref')

        # Merge a change.
        self.fake_gerrit.addFakeTag('org/project', 'master', 'foo')

        # Wait for the job to run.
        self.waitForPoll('gerrit-ref')
        self.waitUntilSettled()

        self.assertHistory([
            dict(name='tag-job', result='SUCCESS'),
        ])


class TestWrongConnection(ZuulTestCase):
    config_file = 'zuul-connections-multiple-gerrits.conf'
    tenant_config_file = 'config/wrong-connection-in-pipeline/main.yaml'

    def test_wrong_connection(self):
        # Test if the wrong connection is configured in a gate pipeline

        # Our system has two gerrits, and we have configured a gate
        # pipeline to trigger on the "review_gerrit" connection, but
        # report (and merge) via "another_gerrit".
        A = self.fake_review_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_review_gerrit.addEvent(A.addApproval('Approved', 1))

        self.waitUntilSettled()

        B = self.fake_review_gerrit.addFakeChange('org/project', 'master', 'B')
        # Let's try this as if the change was merged (say, via another tenant).
        B.setMerged()
        B.addApproval('Code-Review', 2)
        self.fake_review_gerrit.addEvent(B.addApproval('Approved', 1))

        self.waitUntilSettled()

        self.assertEqual(A.reported, 0)
        self.assertEqual(B.reported, 0)
        self.assertHistory([
            dict(name='test-job', result='SUCCESS', changes='1,1'),
            dict(name='test-job', result='SUCCESS', changes='2,1'),
        ], ordered=False)

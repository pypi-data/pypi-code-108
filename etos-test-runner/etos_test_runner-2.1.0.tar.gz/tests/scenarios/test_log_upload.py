# Copyright 2020-2021 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests full executions."""
import os
import logging
from copy import deepcopy
from shutil import rmtree
from contextlib import contextmanager
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
from etos_lib.lib.debug import Debug
from etos_test_runner.etr import ETR

# pylint:disable=too-many-locals

SUITE = {
    "name": "Test ETOS API scenario",
    "priority": 1,
    "recipes": [
        {
            "constraints": [
                {"key": "ENVIRONMENT", "value": {}},
                {"key": "PARAMETERS", "value": {}},
                {"key": "COMMAND", "value": "exit 0"},
                {
                    "key": "TEST_RUNNER",
                    "value": "registry.nordix.org/eiffel/etos-python-test-runner:3.9.0",
                },
                {"key": "EXECUTE", "value": ["echo 'this is the pre-execution step'"]},
                {
                    "key": "CHECKOUT",
                    "value": ["echo 'this is the checkout step'"],
                },
            ],
            "id": "6e8d29eb-4b05-4f5e-9207-0c94438479c7",
            "testCase": {
                "id": "ETOS_API_functests",
                "tracker": "Github",
                "url": "https://github.com/eiffel-community/etos-api",
            },
        }
    ],
    "test_runner": "registry.nordix.org/eiffel/etos-python-test-runner:3.9.0",
    "iut": {
        "provider_id": "default",
        "identity": "pkg:docker/production/etos/etos-api@1.2.0",
        "type": "docker",
        "namespace": "production/etos",
        "name": "etos-api",
        "version": "1.2.0",
        "qualifiers": {},
        "subpath": None,
    },
    "artifact": "e9b0c120-8638-4c73-9b5c-e72226415ae6",
    "context": "fde87097-46bd-4916-b69f-48dbbec47936",
    "executor": {},
    "log_area": {
        "provider_id": "default",
        "livelogs": "http://localhost/livelogs",
        "type": "ARTIFACTORY",
        "upload": {
            "url": "http://localhost/logs/{context}/{folder}/{name}",
            "method": "POST",
        },
        "logs": {},
    },
}


class TestLogUpload(TestCase):
    """Test a log upload of ETR."""

    logger = logging.getLogger(__name__)

    @classmethod
    def setUpClass(cls):
        """Create a debug instance."""
        cls.main_suite_id = "577381ad-8356-4939-ab77-02e7abe06699"
        cls.debug = Debug()

    def setUp(self):
        """Create patch objects and a test folder to execute from."""
        self.patchers = []
        self.original = Path.cwd()
        self.root = Path().joinpath("testfolder").absolute()
        if self.root.exists():
            rmtree(self.root)
        self.root.mkdir()
        os.chdir(self.root)
        self._patch_wait_for_request()
        self._patch_http_request()
        self._patch_test_suite_started_request()

    def _patch_wait_for_request(self):
        """Patch the ETOS library wait for request method."""
        patcher = patch("etos_lib.etos.Http.wait_for_request")
        self.patchers.append(patcher)
        self.wait_for_request = patcher.start()
        self.suite = deepcopy(SUITE)
        self.wait_for_request.return_value = [self.suite]

    def _patch_http_request(self):
        """Patch the ETOS library http request method."""
        patcher = patch("etos_lib.etos.Http.request")
        self.patchers.append(patcher)
        self.http_request = patcher.start()
        self.http_request.return_value = True

    def _patch_test_suite_started_request(self):
        """Patch the GraphQL request for test suite started."""
        patcher = patch("etos_test_runner.lib.testrunner.request_test_suite_started")
        self.patchers.append(patcher)
        self.request_test_suite_started = patcher.start()
        self.request_test_suite_started.return_value = [
            {
                "data": {"testSuiteCategories": []},
                "meta": {"id": self.main_suite_id},
            }
        ]

    def tearDown(self):
        """Clear the test folder and patchers."""
        os.chdir(self.original)
        rmtree(self.root, ignore_errors=True)
        for patcher in self.patchers:
            patcher.stop()

    @staticmethod
    @contextmanager
    def environ(add_environment):
        """Set environment variables in context and remove after.

        :param add_environment: Environment variables to add.
        :type add_environment: dict
        """
        current = {}
        for key, value in add_environment.items():
            current[key] = os.getenv(key)
            os.environ[key] = str(value)
        yield
        for key, value in current.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value

    @staticmethod
    def get_event(event_name, events):
        """Get an event by name.

        :param event_name: Event name to find.
        :type event_name: str
        :return: Event with the name.
        :rtype: :obj:`eiffellib.lib.events.EiffelBaseEvent`
        """
        try:
            return [event for event in events if event.meta.type == event_name][0]
        except IndexError:
            return None

    @staticmethod
    def get_events(event_name, events):
        """Get multiple events by name.

        :param event_name: Event name to find.
        :type event_name: str
        :return: Events with the name.
        :rtype: list
        """
        try:
            return [event for event in events if event.meta.type == event_name]
        except IndexError:
            return []

    def test_log_upload(self):
        """Test that log upload works as expected.

        Approval criteria:
            - Log upload shall be executed after each test and after each suite.
            - Logs shall be attached to TestSuiteFinished event.

        Test steps::
            1. Initialize and run ETR.
            2. Verify that upload works as expected.
            3. Verify that log url was attached to event.
        """
        environment = {
            "ETOS_DISABLE_SENDING_EVENTS": "1",
            "ETOS_DISABLE_RECEIVING_EVENTS": "1",
            "ETOS_GRAPHQL_SERVER": "http://localhost/graphql",
            "SUB_SUITE_URL": "http://localhost/download_suite",
            "HOME": self.root,  # There is something weird with tox and HOME. This fixes it.
        }
        with self.environ(environment):
            self.logger.info("STEP: Initialize and run ETR.")
            etr = ETR()
            etr.run_etr()
            sub_suite_started = self.get_event(
                "EiffelTestSuiteStartedEvent", self.debug.events_published
            )

            self.logger.info("STEP: Verify that upload works as expected.")
            filenames = [
                f"{self.suite['recipes'][0]['testCase']['id']}_test_output.log",
                "full_execution.log",
                "workspace.tar.gz",
            ]

            for method_call in self.http_request.call_args_list:
                verb, url, as_json = method_call.args
                data = method_call.kwargs.get("data")
                filename = Path(data.name)

                self.assertEqual(verb, self.suite["log_area"]["upload"]["method"])
                self.assertEqual(
                    url,
                    self.suite["log_area"]["upload"]["url"].format(
                        context=self.suite["context"],
                        name=filename.name,
                        folder=f"{self.main_suite_id}/{sub_suite_started.meta.event_id}",
                    ),
                )
                self.assertTrue(as_json)

                for path in filenames:
                    if filename.name == path:
                        filenames.remove(path)
                        break
                else:
                    raise AssertionError(f"{filename} should not have been uploaded.")
            self.assertEqual(len(filenames), 0)

            self.logger.info("STEP: Verify that log url was attached to event.")
            test_suite_finished = self.get_event(
                "EiffelTestSuiteFinishedEvent", self.debug.events_published
            )

            files = [
                f"{self.suite['recipes'][0]['testCase']['id']}_test_output.log",
                "full_execution.log",
            ]
            for filename in files:
                url = self.suite["log_area"]["upload"]["url"].format(
                    context=self.suite["context"],
                    name=filename,
                    folder=f"{self.main_suite_id}/{sub_suite_started.meta.event_id}",
                )
                for log in test_suite_finished.data.data.get("persistentLogs"):
                    if log["name"] == filename and log["uri"] == url:
                        test_suite_finished.data.data["persistentLogs"].remove(log)
                        break
                else:
                    raise AssertionError(f"{filename} was not attached to TestSuiteFinished event.")

    def test_log_upload_rename_file_too_long(self):
        """Test that log upload works and that it renames too long filenames.

        Approval criteria:
            - Log names shall be renamed if they are considered too long.

        Test steps::
            1. Initialize ETR.
            2. Run ETR with a suite that creates a file with a too long name.
            3. Verify that the file was renamed before upload.
        """
        environment = {
            "ETOS_DISABLE_SENDING_EVENTS": "1",
            "ETOS_DISABLE_RECEIVING_EVENTS": "1",
            "ETOS_GRAPHQL_SERVER": "http://localhost/graphql",
            "SUB_SUITE_URL": "http://localhost/download_suite",
            "HOME": self.root,  # There is something weird with tox and HOME. This fixes it.
        }
        suite = deepcopy(SUITE)
        command_index = suite["recipes"][0]["constraints"].index(
            {"key": "COMMAND", "value": "exit 0"}
        )
        suite["recipes"][0]["constraints"][command_index] = {
            "key": "COMMAND",
            "value": f"touch $LOG_PATH/{'a'*251}.txt",
        }
        # The file that is created will total to '255' characters, the maximum limit, but since
        # ETR attaches the test case name for each log file generated by that test case we will
        # get a filename that is too long (ETOS_API_Functests_(a*251).txt) and thus should
        # be renamed.
        with self.environ(environment):
            self.logger.info("STEP: Initialize ETR.")
            etr = ETR()

            self.logger.info("STEP: Run ETR with a suite that creates a file with a too long name.")
            self.wait_for_request.return_value = [suite]
            etr.run_etr()
            test_suite_finished = self.get_event(
                "EiffelTestSuiteFinishedEvent", self.debug.events_published
            )

            self.logger.info("STEP: Verify that the file was renamed before upload")
            for log in test_suite_finished.data.data.get("persistentLogs"):
                if log["name"].endswith("aa.txt"):
                    self.assertLessEqual(len(log["name"]), 255)
                    break
            else:
                raise AssertionError("Log file was not uploaded")

    def test_log_upload_rename_file_exists(self):
        """Test that log upload works and that it renames files with the same name.

        Approval criteria:
            - Log names shall be renamed if are named the same.

        Test steps::
            1. Initialize ETR.
            2. Run ETR with a test suite that creates two files with the same name.
            3. Verify that one file was renamed before upload.
        """
        environment = {
            "ETOS_DISABLE_SENDING_EVENTS": "1",
            "ETOS_DISABLE_RECEIVING_EVENTS": "1",
            "ETOS_GRAPHQL_SERVER": "http://localhost/graphql",
            "SUB_SUITE_URL": "http://localhost/download_suite",
            "HOME": self.root,  # There is something weird with tox and HOME. This fixes it.
        }
        command_index = self.suite["recipes"][0]["constraints"].index(
            {"key": "COMMAND", "value": "exit 0"}
        )
        self.suite["recipes"][0]["constraints"][command_index] = {
            "key": "COMMAND",
            "value": "touch $LOG_PATH/my_file.txt",
        }
        recipe = deepcopy(self.suite["recipes"][0])
        self.suite["recipes"].append(recipe)
        # Same test has been added twice. Both tests creates file "my_file.txt"
        # and the tests have the same name.
        # Filenames will be "ETOS_API_Functest_my_file.txt"
        with self.environ(environment):
            self.logger.info("STEP: Initialize ETR.")
            etr = ETR()

            self.logger.info(
                "STEP: Run ETR with a test suite that creates two files with the same name."
            )
            etr.run_etr()

            self.logger.info("STEP: Verify that the file was renamed before upload")
            sub_suite_started = self.get_event(
                "EiffelTestSuiteStartedEvent", self.debug.events_published
            )
            test_suite_finished = self.get_event(
                "EiffelTestSuiteFinishedEvent", self.debug.events_published
            )
            expected = [
                {
                    "name": "ETOS_API_functests_my_file.txt",
                    "uri": self.suite["log_area"]["upload"]["url"].format(
                        context=self.suite["context"],
                        folder=f"{self.main_suite_id}/{sub_suite_started.meta.event_id}",
                        name="ETOS_API_functests_my_file.txt",
                    ),
                },
                {
                    "name": "1_ETOS_API_functests_my_file.txt",
                    "uri": self.suite["log_area"]["upload"]["url"].format(
                        context=self.suite["context"],
                        folder=f"{self.main_suite_id}/{sub_suite_started.meta.event_id}",
                        name="1_ETOS_API_functests_my_file.txt",
                    ),
                },
            ]
            for log in test_suite_finished.data.data.get("persistentLogs"):
                if "ETOS_API_functests_my_file.txt" in log["name"]:
                    self.assertIn(log, expected)
                    expected.remove(log)
            self.assertEqual(len(expected), 0)

    def test_artifact_upload(self):
        """Test that artifact upload works as expected.

        Approval criteria:
            - Artifact upload shall be executed after each test and after each suite.
            - Artifacts shall be attached to ArtifactCreated event.

        Test steps::
            1. Initialize and run ETR suite which creates an artifact.
            2. Verify that upload works as expected.
            3. Verify that artifact was attached to event.
        """
        environment = {
            "ETOS_DISABLE_SENDING_EVENTS": "1",
            "ETOS_DISABLE_RECEIVING_EVENTS": "1",
            "ETOS_GRAPHQL_SERVER": "http://localhost/graphql",
            "SUB_SUITE_URL": "http://localhost/download_suite",
            "HOME": self.root,  # There is something weird with tox and HOME. This fixes it.
        }
        command_index = self.suite["recipes"][0]["constraints"].index(
            {"key": "COMMAND", "value": "exit 0"}
        )
        self.suite["recipes"][0]["constraints"][command_index] = {
            "key": "COMMAND",
            "value": "touch $ARTIFACT_PATH/my_artifact.txt",
        }
        with self.environ(environment):
            self.logger.info("STEP: Initialize and run ETR suite which creates an artifact.")
            etr = ETR()
            etr.run_etr()
            self.logger.info("STEP: Verify that upload works as expected.")
            sub_suite_started = self.get_event(
                "EiffelTestSuiteStartedEvent", self.debug.events_published
            )
            test_name = self.suite["recipes"][0]["testCase"]["id"]
            suite_name = self.suite.get("name").replace(" ", "-")
            artifact = f"{test_name}_my_artifact.txt"

            # We only verify that test artifact upload works. Global artifact is tested by
            # test_log_upload.
            for method_call in self.http_request.call_args_list:
                verb, url, as_json = method_call.args
                data = method_call.kwargs.get("data")
                filename = Path(data.name)
                if filename.name == artifact:
                    self.assertEqual(verb, self.suite["log_area"]["upload"]["method"])
                    self.assertEqual(
                        url,
                        self.suite["log_area"]["upload"]["url"].format(
                            context=self.suite["context"],
                            name=filename.name,
                            folder=f"{self.main_suite_id}/{sub_suite_started.meta.event_id}",
                        ),
                    )
                    self.assertTrue(as_json)
                    break
            else:
                raise AssertionError(f"Artifact {artifact} was not uploaded.")

            self.logger.info("STEP: Verify that artifact was attached to event.")
            artifact_created = self.get_events(
                "EiffelArtifactCreatedEvent", self.debug.events_published
            )
            self.assertEqual(len(artifact_created), 2)
            test_created = artifact_created.pop(0)
            suite_created = artifact_created.pop(0)
            self.assertEqual(
                test_created.data.data.get("identity"),
                f"pkg:etos-test-output/{suite_name}/{test_name}",
            )
            self.assertListEqual(
                test_created.data.data.get("fileInformation"), [{"name": artifact}]
            )
            self.assertEqual(
                suite_created.data.data.get("identity"),
                f"pkg:etos-test-output/{suite_name}",
            )
            self.assertListEqual(
                suite_created.data.data.get("fileInformation"),
                [{"name": "workspace.tar.gz"}],
            )
            self.assertEqual(len(artifact_created), 0)
            artifact_published = self.get_events(
                "EiffelArtifactPublishedEvent", self.debug.events_published
            )
            self.assertEqual(len(artifact_published), 2)
            my_artifact = artifact_published.pop(0)
            url = self.suite["log_area"]["upload"]["url"].format(
                context=self.suite["context"],
                name="",
                folder=f"{self.main_suite_id}/{sub_suite_started.meta.event_id}",
            )
            self.assertListEqual(
                my_artifact.data.data.get("locations"),
                [{"type": "ARTIFACTORY", "uri": url}],
            )

            url = self.suite["log_area"]["upload"]["url"].format(
                context=self.suite["context"],
                name="",
                folder=f"{self.main_suite_id}/{sub_suite_started.meta.event_id}",
            )
            workspace = artifact_published.pop(0)
            self.assertListEqual(
                workspace.data.data.get("locations"),
                [{"type": "ARTIFACTORY", "uri": url}],
            )
            self.assertEqual(len(artifact_published), 0)

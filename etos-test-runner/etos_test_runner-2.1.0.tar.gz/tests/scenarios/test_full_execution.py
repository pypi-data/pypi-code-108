# Copyright 2020 Axis Communications AB.
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
                    "value": [
                        "git clone https://github.com/eiffel-community/etos-test-runner.git ."
                    ],
                },
            ],
            "id": "6e8d29eb-4b05-4f5e-9207-0c94438479c7",
            "testCase": {
                "id": "ETOS API functests",
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
        "upload": {"url": "http://localhost/logs", "method": "POST"},
        "logs": {},
    },
}


class TestFullExecution(TestCase):
    """Test a full execution of ETR."""

    logger = logging.getLogger(__name__)

    @classmethod
    def setUpClass(cls):
        """Create a debug instance."""
        cls.debug = Debug()

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
                "meta": {"id": "577381ad-8356-4939-ab77-02e7abe06699"},
            }
        ]

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

    def validate_event_name_order(self, events):
        """Validate ETR sent events.

        :raises AssertionError: If events are not correct.

        :param events: All events sent, in order.
        :type events: deque
        """
        self.logger.info(events)
        event_names_in_order = [
            "EiffelActivityTriggeredEvent",
            "EiffelActivityStartedEvent",
            "EiffelTestSuiteStartedEvent",
            "EiffelArtifactCreatedEvent",
            "EiffelArtifactPublishedEvent",
            "EiffelTestSuiteFinishedEvent",
            "EiffelActivityFinishedEvent",
        ]
        for event_name in event_names_in_order:
            self.assertEqual(events.popleft().meta.type, event_name)
        self.assertEqual(list(events), [])

    def test_full(self):
        """Test that a full execution scenario works as expected.

        Approval criteria:
            - It shall be possible to execute a full suite in ETR.
            - ETR shall send events in the correct order.

        Test steps::
            1. Initialize and run ETR.
            2. Verify that events were sent in the correct order.
            3. Verify that ETR returned with status code 0.
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
            result = etr.run_etr()

            self.logger.info("STEP: Verify that events were sent in the correct order.")
            self.validate_event_name_order(self.debug.events_published.copy())

            self.logger.info("STEP: Verify that ETR returned with status code 0.")
            # Result is either dictionary with outcome or an exit status code.
            # Exit status code on success is 0
            self.assertEqual(result, 0)

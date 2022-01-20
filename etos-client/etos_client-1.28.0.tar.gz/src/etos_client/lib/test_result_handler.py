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
"""ETOS Client test result handler."""
import time
import logging
from .graphql import (
    request_activity,
    request_activity_canceled,
    request_test_suite_finished,
    request_test_suite_started,
    request_suite,
    request_announcements,
    request_environment,
)

_LOGGER = logging.getLogger(__name__)


class ETOSTestResultHandler:
    """Handle ETOS test results."""

    activity_id = None

    def __init__(self, etos):
        """Initialize ETOS Client test result handler.

        :param etos: ETOS Library instance.
        :type etos: :obj:`etos_lib.etos.ETOS`
        """
        self.etos = etos
        self.events = {}
        self.announcements = []

    @property
    def has_started(self):
        """Whether or not test suites have started.

        :return: Whether or not test suites have started.
        :rtype bool
        """
        return len(self.events.get("testSuiteStarted", [])) >= 1

    @property
    def has_finished(self):
        """Whether or not test suites have finished.

        :return: Whether or not test suites have finished.
        :rtype bool
        """
        return bool(self.events.get("mainSuiteFinished", False))

    @property
    def spinner_text(self):
        """Generate the spinner text based on test results.

        :return: String formatted for the Halo spinner.
        :rtype: str
        """
        message_template = (
            "{announcement}\t"
            "Started : {started_length}\t"
            "Finished: {finished_length}\t"
        )
        try:
            announcement = self.announcements[-1]["data"]["body"]
        except (KeyError, IndexError, TypeError):
            announcement = ""

        params = {
            "started_length": len(self.events.get("testSuiteStarted", [])),
            "finished_length": len(self.events.get("testSuiteFinished", [])),
            "announcement": announcement,
        }
        return message_template.format(**params)

    def get_environment_events(self):
        """Get the environment events set for this execution."""
        events = self.events.get("testSuiteStarted", [])
        ids = [
            started["meta"]["id"]
            for started in events + [self.events.get("mainSuiteStarted")]
        ]
        ids.append(self.activity_id)
        self.events["environmentDefined"] = list(request_environment(self.etos, ids))

    def test_result(self):
        """Build test results based on events retrieved.

        :return: Result and message.
        :rtype: tuple
        """
        nbr_of_fail = 0
        if not self.events.get("testSuiteStarted"):
            return False, "Test suite did not start."
        self.get_environment_events()

        main_suite_finished = self.events.get("mainSuiteFinished", [{}])[0]
        data = main_suite_finished.get("data", {})
        outcome = data.get("testSuiteOutcome", {})
        verdict = outcome.get("verdict")
        if verdict == "PASSED":
            result = True
        else:
            for test_suite_finished in self.events.get("testSuiteFinished"):
                data = test_suite_finished.get("data", {})
                outcome = data.get("testSuiteOutcome", {})
                verdict = outcome.get("verdict")
                if verdict != "PASSED":
                    nbr_of_fail += 1
        if nbr_of_fail > 0:
            nbr_of_suites = len(self.events.get("testSuiteStarted"))
            message = f"{nbr_of_fail}/{nbr_of_suites} test suites failed."
            result = False
        else:
            message = "Test suite finished successfully."
            result = True
        return result, message

    def latest_announcement(self, spinner):
        """Find latest announcement and print it.

        :param spinner: Spinner text item.
        :type spinner: :obj:`Spinner`
        """
        for announcement in request_announcements(
            self.etos, [self.etos.config.get("suite_id"), self.activity_id]
        ):
            if announcement not in self.announcements:
                self.announcements.append(announcement)
                data = self.announcements[-1].get("data")
                spinner.info(f"{data.get('heading')}: {data.get('body')}")
                spinner.start("Waiting for ETOS.")

    @staticmethod
    def split_main_and_sub_suites_started(started):
        """Split test suite started into main suite and sub suites.

        :param started: Test suites that have started in a specified activity.
        :type started: list
        :return: Main suite and sub suites started.
        :rtype: tuple
        """
        sub_suite_started = []
        main_suite = None
        for test_suite_started in started:
            for category in test_suite_started["data"]["testSuiteCategories"]:
                if "Sub suite" in category.get("type"):
                    sub_suite_started.append(test_suite_started)
                    break
            else:
                main_suite = test_suite_started
        return main_suite, sub_suite_started

    def get_events(self, suite_id):
        """Get events from an activity started from suite id.

        :param suite_id: ID of test execution recipe that triggered this activity.
        :type suite_id: str
        :return: Dictionary of all events generated for this suite.
        :rtype: dict
        """
        if self.activity_id is None:
            activity = request_activity(self.etos, suite_id)
            if activity is None:
                return {}
            self.activity_id = activity["meta"]["id"]

        results = {"activityId": self.activity_id}

        started = list(request_test_suite_started(self.etos, self.activity_id))
        if not started:
            return {}
        main_suite, sub_suite_started = self.split_main_and_sub_suites_started(started)
        results["testSuiteStarted"] = sub_suite_started
        results["mainSuiteStarted"] = main_suite

        started_ids = [
            test_suite_started["meta"]["id"] for test_suite_started in started
        ]
        main_suite_link = {
            "testSuiteStarted": {"meta": {"id": main_suite["meta"]["id"]}}
        }

        finished = list(request_test_suite_finished(self.etos, started_ids))
        if not finished:
            return results
        results["testSuiteFinished"] = [
            sub_finished
            for sub_finished in finished
            if main_suite_link not in sub_finished["links"]
        ]
        results["mainSuiteFinished"] = [
            main_suite
            for main_suite in finished
            if main_suite_link in main_suite["links"]
        ]
        return results

    def print_suite(self, spinner):
        """Print test suite batchesUri.

        :param spinner: Spinner text item.
        :type spinner: :obj:`Spinner`
        """
        spinner.text = "Waiting for test suite url."
        timeout = time.time() + 60
        while time.time() < timeout:
            tercc = request_suite(self.etos, self.etos.config.get("suite_id"))
            if tercc:
                spinner.info(f"Test suite: {tercc['data']['batchesUri']}")
                spinner.start()
                return
            time.sleep(1)
        raise TimeoutError("Test suite not available in 10s.")

    def wait_for_test_suite_finished(self, spinner):
        """Query graphql server until the number of started is equal to number of finished.

        :param spinner: Spinner text item.
        :type spinner: :obj:`Spinner`
        :return: Whether it was a successful execution or not, the test results
                 and if the execution was canceled.
        :rtype: tuple
        """
        self.print_suite(spinner)
        timeout = time.time() + 3600 * 24
        while time.time() < timeout:
            self.latest_announcement(spinner)
            time.sleep(10)
            self.events = self.get_events(self.etos.config.get("suite_id"))
            canceled = request_activity_canceled(self.etos, self.activity_id)
            if canceled:
                return (
                    False,
                    (
                        "Test Suite was canceled, with the following reason: "
                        f"{canceled['data']['reason']}"
                    ),
                    canceled,
                )
            if not self.has_started:
                continue
            spinner.text = self.spinner_text
            if self.has_finished:
                return *self.test_result(), canceled
        return False, "Test suites did not finish", canceled

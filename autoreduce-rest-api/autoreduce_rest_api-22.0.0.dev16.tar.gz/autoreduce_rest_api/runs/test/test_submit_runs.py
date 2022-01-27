# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Test cases for submitting runs."""
# pylint:disable=no-member
import json
import os
import time
from typing import Callable
from unittest.mock import Mock, patch
from parameterized import parameterized

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
import requests
from rest_framework.authtoken.models import Token

from autoreduce_db.reduction_viewer.models import ReductionRun
from autoreduce_qp.queue_processor.queue_listener import setup_connection
from autoreduce_utils.clients.connection_exception import ConnectionException
from autoreduce_utils.settings import SCRIPTS_DIRECTORY

from autoreduce_rest_api.runs.views import NO_RUNS_KEY_MESSAGE

INSTRUMENT_NAME = "TESTINSTRUMENT"


def wait_until(predicate, timeout=30, period=0.25):
    """Wait until the condition is True, or it times out."""
    must_end = time.time() + timeout
    while time.time() < must_end:
        if predicate():
            return True

        time.sleep(period)

    return False


class SubmitRunsTest(LiveServerTestCase):
    fixtures = [
        "autoreduce_rest_api/autoreduce_django/fixtures/super_user_fixture.json",
        "autoreduce_rest_api/autoreduce_django/fixtures/status_fixture.json"
    ]

    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.queue_client, cls.listener = setup_connection()
        except ConnectionException as err:
            raise RuntimeError("Could not connect to ActiveMQ - check your credentials. If running locally check that "
                               "ActiveMQ Docker container is running and started") from err

        os.makedirs(SCRIPTS_DIRECTORY % INSTRUMENT_NAME, exist_ok=True)
        with open(os.path.join(SCRIPTS_DIRECTORY % INSTRUMENT_NAME, "reduce_vars.py"), mode='w',
                  encoding="utf-8") as file:
            file.write("")

        return super().setUpClass()

    def setUp(self) -> None:
        user = get_user_model()
        self.token = Token.objects.create(user=user.objects.first())
        return super().setUp()

    @parameterized.expand([[requests.post, "/api/runs/"], [requests.post, "/api/runs/batch/"],
                           [requests.delete, "/api/runs/"], [requests.delete, "/api/runs/batch/"]])
    def test_no_runs_key_in_json_returns_json_msg_error(self, requests_callable: Callable, url: str):
        """
        Test that not specifying any "runs" will return a response with 400 and an error message.
        """
        response = requests_callable(f"{self.live_server_url}{url}{INSTRUMENT_NAME}",
                                     json={},
                                     headers={"Authorization": f"Token {self.token}"})
        assert response.status_code == 400
        assert json.loads(response.content)["error"] == NO_RUNS_KEY_MESSAGE

    @parameterized.expand([
        ['autoreduce_rest_api.runs.views.submit_main', requests.post, "/api/runs/"],
        ['autoreduce_rest_api.runs.views.submit_batch_main', requests.post, "/api/runs/batch/"],
        ['autoreduce_rest_api.runs.views.remove_main', requests.delete, "/api/runs/"],
        ['autoreduce_rest_api.runs.views.remove_main', requests.delete, "/api/runs/batch/"],
    ])
    def test_raising_returns_json_error(self, mock_path: str, requests_callable: Callable, url: str):
        """
        Parameterized test that checks that the correct error message
        is returned from each of the views available.
        """
        with patch(mock_path, side_effect=RuntimeError("Test error")) as mock_main:
            response = requests_callable(f"{self.live_server_url}{url}{INSTRUMENT_NAME}",
                                         json={
                                             "runs": list(range(63125, 63131)),
                                         },
                                         headers={"Authorization": f"Token {self.token}"})
            assert response.status_code == 400
            assert json.loads(response.content)["error"] == "Test error"
            mock_main.assert_called_once()

    @patch("autoreduce_scripts.manual_operations.manual_submission.read_from_datafile", return_value="test title")
    @patch('autoreduce_scripts.manual_operations.manual_submission.get_run_data_from_icat',
           return_value=["/tmp/location", "RB1234567"])
    def test_submit_and_delete_run_range(self, get_run_data_from_icat: Mock, read_from_datafile: Mock):
        """Submit and delete a run range via the API.

        Args:
            get_run_data_from_icat: Mocks the function to call ICAT, to avoid unnecessary calls to their service
        """
        response = requests.post(f"{self.live_server_url}/api/runs/{INSTRUMENT_NAME}",
                                 json={
                                     "runs": list(range(63125, 63131)),
                                     "software": {
                                         "name": "Mantid",
                                         "version": "6.2.0"
                                     },
                                 },
                                 headers={"Authorization": f"Token {self.token}"})
        assert response.status_code == 200
        assert wait_until(lambda: ReductionRun.objects.count() == 6)
        assert get_run_data_from_icat.call_count == 6
        assert read_from_datafile.call_count == 6
        get_run_data_from_icat.reset_mock()

        response = requests.delete(f"{self.live_server_url}/api/runs/{INSTRUMENT_NAME}",
                                   json={
                                       "runs": list(range(63125, 63131)),
                                   },
                                   headers={"Authorization": f"Token {self.token}"})
        assert response.status_code == 200
        assert wait_until(lambda: ReductionRun.objects.count() == 0)
        get_run_data_from_icat.assert_not_called()

    @patch("autoreduce_scripts.manual_operations.manual_submission.read_from_datafile", return_value="test title")
    @patch("autoreduce_scripts.manual_operations.manual_submission.get_run_data_from_icat",
           return_value=["/tmp/location", "RB1234567"])
    def test_batch_submit_and_delete_run(self, get_run_data_from_icat: Mock, read_from_datafile: Mock):
        """Submit and delete a run range via the API."""
        response = requests.post(f"{self.live_server_url}/api/runs/batch/{INSTRUMENT_NAME}",
                                 headers={"Authorization": f"Token {self.token}"},
                                 json={
                                     "runs": [63125, 63130],
                                     "software": {
                                         "name": "Mantid",
                                         "version": "6.2.0"
                                     },
                                     "reduction_arguments": {
                                         "standard_vars": {
                                             "apple": "banana"
                                         }
                                     },
                                     "user_id": 99199,
                                     "description": "Test description"
                                 })
        assert response.status_code == 200
        assert wait_until(lambda: ReductionRun.objects.count() == 1)
        assert get_run_data_from_icat.call_count == 2
        assert read_from_datafile.call_count == 2
        get_run_data_from_icat.reset_mock()

        reduced_run = ReductionRun.objects.first()
        assert reduced_run.started_by == 99199
        assert reduced_run.run_description == "Test description"

        response = requests.delete(f"{self.live_server_url}/api/runs/batch/{INSTRUMENT_NAME}",
                                   json={"runs": [reduced_run.pk]},
                                   headers={"Authorization": f"Token {self.token}"})
        assert response.status_code == 200
        assert wait_until(lambda: ReductionRun.objects.count() == 0)
        get_run_data_from_icat.assert_not_called()

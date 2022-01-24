#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import json

import pytest


@pytest.fixture
def async_url():
    return "http://host_name.com/status/status_id/"


@pytest.fixture
def resolved_url():
    return "https://host_name.com/finished/id/"


@pytest.fixture
def async_success_callback(resolved_url):
    def callback(request):
        return 303, {"Location": resolved_url}, ""

    return callback


@pytest.fixture
def async_pending_callback():
    def callback(request):
        return (
            200,
            {},
            json.dumps(
                dict(
                    status="INITIALIZED", message="", code=0, created="2016-07-22T12:00:00.123456Z"
                )
            ),
        )

    return callback


@pytest.fixture
def async_job_failure_callback():
    def callback(request):
        return (
            200,
            {},
            json.dumps(
                dict(status="ERROR", message="", code=0, created="2016-07-22T12:00:00.123456Z")
            ),
        )

    return callback


@pytest.fixture
def async_job_completed_callback():
    def callback(request):
        return (
            200,
            {},
            json.dumps(
                dict(status="COMPLETED", message="", code=0, created="2016-07-22T12:00:00.123456Z")
            ),
        )

    return callback


@pytest.fixture
def async_server_nonsense_callback():
    """
    A callback that returns a nonsensical status code.
    400-level and 500-level are caught and raised automatically by the client, so
    we'll have this callback return a 299 (that is not a real status code)
    to stand in for the "I don't know what the server is trying to say"
    """

    def callback(request):
        return 299, {}, json.dumps({"message": "An unexpected error has occurred"})

    return callback


@pytest.fixture
def async_not_finished_callback():
    def callback(request):
        return (
            200,
            {},
            json.dumps(
                dict(status="RUNNING", message="", code=0, created="2016-07-22T12:00:00.123456Z")
            ),
        )

    return callback


@pytest.fixture
def custom_resolver():
    def resolver(response):
        data = response.json()
        if data["status"] in ["COMPLETED", "ERROR"]:
            return data

    return resolver

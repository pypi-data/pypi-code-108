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
import responses

from datarobot import errors, Project


@responses.activate
def test_timeout(mock_async_time, async_url):

    mock_async_time.time.side_effect = (0, 0, 1000)

    responses.add(
        responses.GET,
        async_url,
        content_type="application/json",
        status=200,
        body=json.dumps({"status": "RUNNING"}),
    )

    with pytest.raises(errors.AsyncTimeoutError):
        Project.from_async(async_url, max_wait=1)


@responses.activate
def test_check_failed(async_url):
    """
    Getting status_code different from 200 and 303 should raise AsyncFailureError
    """
    responses.add(
        responses.GET, async_url, content_type="application/json", status=504, body=json.dumps({}),
    )

    with pytest.raises(errors.AsyncFailureError):
        Project.from_async(async_url, max_wait=1)


@responses.activate
def test_check_exception_for_failure_contains_status_code_and_async_location(async_url):
    """
    Getting status_code different from 200 and 303 should raise AsyncFailureError
    """
    responses.add(
        responses.GET, async_url, content_type="application/json", status=504, body=json.dumps({}),
    )

    with pytest.raises(errors.ProjectAsyncFailureError) as e:
        Project.from_async(async_url, max_wait=1)
        assert e.status_code == 504
        assert e.async_location == async_url


@responses.activate
def test_project_creation_failed(async_url, async_failure_json):
    responses.add(
        responses.GET,
        async_url,
        content_type="application/json",
        status=200,
        body=async_failure_json,
    )

    with pytest.raises(errors.AsyncProcessUnsuccessfulError):
        Project.from_async(async_url, max_wait=1)


@responses.activate
def test_project_creation_aborted(async_url, async_aborted_json):
    responses.add(
        responses.GET,
        async_url,
        content_type="application/json",
        status=200,
        body=async_aborted_json,
    )

    with pytest.raises(errors.AsyncProcessUnsuccessfulError):
        Project.from_async(async_url, max_wait=1)

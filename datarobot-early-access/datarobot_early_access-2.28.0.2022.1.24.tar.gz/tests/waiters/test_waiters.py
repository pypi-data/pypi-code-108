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

from datarobot import errors
from datarobot.utils.waiters import wait_for_async_resolution, wait_for_custom_resolution


class TestWaitForAsyncResolution(object):
    @responses.activate
    def test_success(self, client, async_url, async_success_callback, resolved_url):
        responses.add_callback(
            responses.GET,
            async_url,
            callback=async_success_callback,
            content_type="application/json",
        )
        result = wait_for_async_resolution(client, async_url)
        assert result == resolved_url

    @responses.activate
    def test_job_failure(
        self, client, async_url, async_job_failure_callback,
    ):
        responses.add_callback(
            responses.GET,
            async_url,
            callback=async_job_failure_callback,
            content_type="application/json",
        )
        with pytest.raises(errors.AsyncProcessUnsuccessfulError):
            wait_for_async_resolution(client, async_url)

    @responses.activate
    def test_server_wtf(
        self, client, async_url, async_server_nonsense_callback,
    ):
        responses.add_callback(
            responses.GET,
            async_url,
            callback=async_server_nonsense_callback,
            content_type="application/json",
        )
        with pytest.raises(errors.AsyncFailureError):
            wait_for_async_resolution(client, async_url)

    @responses.activate
    def test_server_timeout(self, client, async_url, async_not_finished_callback, mock_async_time):
        responses.add_callback(
            responses.GET,
            async_url,
            callback=async_not_finished_callback,
            content_type="application/json",
        )
        mock_async_time.time.side_effect = (0, 0, 10 ** 6)

        with pytest.raises(errors.AsyncTimeoutError):
            wait_for_async_resolution(client, async_url)


class TestWaitForCustomResolution(object):
    @responses.activate
    @pytest.mark.parametrize(
        "callback", ["async_job_failure_callback", "async_job_completed_callback"],
    )
    def test_success(self, request, client, async_url, callback, custom_resolver):
        callback = request.getfixturevalue(callback)
        responses.add_callback(
            responses.GET, async_url, callback=callback, content_type="application/json"
        )
        result = wait_for_custom_resolution(client, async_url, custom_resolver)
        _, _, expected_body = callback(None)
        assert result == json.loads(expected_body)

    @responses.activate
    def test_server_timeout(
        self, client, async_url, async_not_finished_callback, mock_async_time, custom_resolver
    ):
        responses.add_callback(
            responses.GET,
            async_url,
            callback=async_not_finished_callback,
            content_type="application/json",
        )
        mock_async_time.time.side_effect = (0, 0, 10 ** 6)

        with pytest.raises(errors.AsyncTimeoutError):
            wait_for_custom_resolution(client, async_url, custom_resolver)

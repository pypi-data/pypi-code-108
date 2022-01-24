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
import mock
import pytest

from datarobot.client import get_client
from tests.utils import SDKTestcase


class TestBuildRequestWithFile(SDKTestcase):
    def test_file_doesnt_exist(self):
        client = get_client()
        with self.assertRaises(ValueError):
            client.build_request_with_file(
                "PUT", "http://host-name/", "meh.csv", file_path="meh.csv"
            )

    def test_non_string_content(self):
        client = get_client()
        with self.assertRaises(AssertionError):
            client.build_request_with_file("PUT", "http://host-name/", "meh.csv", content=1234)


def test_join_endpoint(client):
    """Ensure no // in generated endpoints."""
    with mock.patch.object(client, "endpoint", "http://host_name.local/api/v2"):
        assert (
            client._join_endpoint("asdf/endpoint/")
            == "http://host_name.local/api/v2/asdf/endpoint/"
        )
        with pytest.raises(ValueError):
            # /absolute/paths are rejected
            client._join_endpoint("/asdf/endpoint/")
    with mock.patch.object(client, "endpoint", "http://host_name.local/api/v2/"):
        assert (
            client._join_endpoint("asdf/endpoint/")
            == "http://host_name.local/api/v2/asdf/endpoint/"
        )
    with mock.patch.object(client, "endpoint", "http://host_name.local"):
        assert client._join_endpoint("asdf/endpoint/") == "http://host_name.local/asdf/endpoint/"
    with mock.patch.object(client, "endpoint", "http://host_name.local/"):
        assert client._join_endpoint("asdf/endpoint/") == "http://host_name.local/asdf/endpoint/"


def test_strip_endpoint(client):
    url = "https://host_name.com/the/url/I/want/"
    stripped = client.strip_endpoint(url)
    assert stripped == "the/url/I/want/"


def test_strip_endpoint_with_training_slash(client):
    client.endpoint = "https://host_name.com/"
    url = "https://host_name.com/the/url/I/want/"
    stripped = client.strip_endpoint(url)
    assert stripped == "the/url/I/want/"


def test_strip_endpoint_invalid_url(client):
    url = "http://localhost/api/v2/wrong/prefix/on/this/url"
    with pytest.raises(ValueError):
        client.strip_endpoint(url)

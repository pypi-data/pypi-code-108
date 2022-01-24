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

import mock
import pytest
import responses

import datarobot.client
from datarobot.client import get_client


@pytest.yield_fixture
def client_version_mock():
    with mock.patch("datarobot.client._get_client_version") as mv:
        yield mv


@pytest.fixture
def version_endpoint(default_config_endpoint):
    return default_config_endpoint + "/version/"


class TestVersionCheck(object):
    @pytest.fixture
    def server_version_string(self):
        yield "2.3.0"

    @pytest.fixture(autouse=True)
    def server_version_response(self, version_endpoint, server_version_string):
        responses.add(
            responses.GET,
            version_endpoint,
            status=200,
            body=json.dumps({"major": "2", "minor": "3", "versionString": server_version_string}),
        )

    @pytest.yield_fixture(autouse=True)
    def no_global_client(self, default_config):
        with mock.patch("datarobot.client._global_client", None) as gc:
            yield gc

    @responses.activate
    @pytest.mark.usefixtures("known_warning")
    def test_major_incompat(self, client_version_mock):
        client_version_mock.return_value = "3.0.0"
        client = get_client()
        assert client is None
        assert datarobot.client._global_client is None

    @responses.activate
    @pytest.mark.usefixtures("known_warning")
    def test_minor_incompat(self, client_version_mock):
        client_version_mock.return_value = "2.4.0"
        client = get_client()
        assert client is not None
        assert datarobot.client._global_client is client

    @responses.activate
    @pytest.mark.parametrize("server_version_string", ["2.4.0"])
    def test_server_can_be_ahead_of_client(self, client_version_mock):
        client_version_mock.return_value = "2.3.0"
        client = get_client()
        assert client is not None
        assert datarobot.client._global_client is client

    @responses.activate
    @pytest.mark.usefixtures("known_warning")
    def test_client_version_import_is_present(self):
        try:
            client = get_client()
            assert client is not None
            assert datarobot.client._global_client is client
        except NameError:
            pytest.fail("Version import statement is not present in client.py")


class TestServerVersion(object):
    @responses.activate
    @pytest.mark.usefixtures("default_config", "known_warning")
    def test_version_does_not_exist(self, version_endpoint):
        """This situation happens if a user is using a client that is new
        enough to check for version on a server that doesn't have an endpoint
        to supply that version
        """
        responses.add(responses.GET, version_endpoint, status=404, body="")

        get_client()

    @responses.activate
    @pytest.mark.usefixtures("default_config")
    def test_version_does_exist(self, version_endpoint, client_version_mock):
        client_version_mock.return_value = "2.4.0"

        responses.add(
            responses.GET,
            version_endpoint,
            status=200,
            body=json.dumps({"major": "2", "minor": "4", "versionString": "2.4.0"}),
        )

        get_client()


class TestClientServerEndpointProtocol(object):
    @pytest.fixture(autouse=True)
    def version_patch(self):
        with mock.patch("datarobot.client._get_client_version") as gv:
            gv.return_value = "2.4.0"
            yield gv

    @responses.activate
    @pytest.mark.parametrize(
        "default_config_endpoint, expected_endpoint",
        [
            pytest.param("https://user_config.com", "https://user_config.com", id="https"),
            pytest.param("http://user_config.com", "http://user_config.com", id="http"),
        ],
    )
    @pytest.mark.usefixtures("default_config")
    def test_correct_configuration_no_changes(self, version_endpoint, expected_endpoint):
        responses.add(
            responses.GET,
            version_endpoint,
            status=200,
            body=json.dumps({"major": "2", "minor": "4", "versionString": "2.4.0"}),
        )

        client = get_client()
        assert client.endpoint == expected_endpoint

    @responses.activate
    @pytest.mark.usefixtures("default_config")
    def test_http_https_protocol_missmatch(self, version_endpoint):
        """If a user specifies http but the server tells them to upgrade to https,
        we want the user to be made aware of it so they can update their config
        """
        https_version_endpoint = version_endpoint.replace("http://", "https://")
        responses.add(
            responses.GET,
            version_endpoint,
            status=301,
            headers={"Location": https_version_endpoint},
        )
        responses.add(
            responses.GET,
            https_version_endpoint,
            status=200,
            body=json.dumps({"major": "2", "minor": "4", "versionString": "2.4.0"}),
        )
        with pytest.warns(UserWarning):  # Expected: warns user about the http/https mismatch
            client = get_client()
        assert client.endpoint.startswith("https://")

    @responses.activate
    @pytest.mark.usefixtures("default_config")
    def test_protocol_check_no_version_returned(self, version_endpoint):
        """There is code that checks for this scenario explicitly. I have no idea why, as it seems like
        `versionString` has always been present on the server response, and has never been empty.
        Also, there is no one else to ask - I am the one who put in the check.
        """
        https_version_endpoint = version_endpoint.replace("http://", "https://")
        responses.add(
            responses.GET,
            version_endpoint,
            status=301,
            headers={"Location": https_version_endpoint},
        )
        responses.add(
            responses.GET,
            https_version_endpoint,
            status=200,
            body=json.dumps({"major": "2", "minor": "4", "versionString": None}),
        )
        with pytest.warns(UserWarning):  # Expected: warns user about the http/https mismatch
            client = get_client()
        assert client.endpoint.startswith("https://")

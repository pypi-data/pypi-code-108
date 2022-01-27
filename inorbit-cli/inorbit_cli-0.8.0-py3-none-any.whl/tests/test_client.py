# Copyright (c) 2021, InOrbit, Inc.
# All rights reserved.
import inorbit.exceptions
import pytest
from inorbit import client
from inorbit.client import InOrbit
from inorbit.constants import DEFAULT_URL


def test_client_defaults(monkeypatch):
    # InOrbit client API KEY default value can
    # be found in the `tox.ini` file.
    assert client.api_key == "foo"

    # Test client uses `DEFAULT_URL` by default
    # Create a new instance with no `url` parameter to avoid test failures
    # on environments with `INORBIT_CLI_URL` environment variable set.
    test_client = InOrbit(api_key="foo")
    assert test_client._url == DEFAULT_URL

    # Test if API auth headers are configured correctly
    assert "X-Auth-InOrbit-App-Key" in client.headers
    assert client.headers["X-Auth-InOrbit-App-Key"] == "foo"


def test_client_init():
    # Test exception raised when no `api_key` is provided
    with pytest.raises(ValueError):
        _ = InOrbit()

    # Test `DEFAULT_URL` is used when no client `url` is specified
    test_client = InOrbit(api_key="foo")
    assert test_client.api_key == "foo"
    assert test_client._url == DEFAULT_URL

    # Test happy path
    test_client = InOrbit(api_key="foo", url="https://foobar.com")
    assert test_client._url == "https://foobar.com"

    # Check trailing `/` are removed
    test_client = InOrbit(api_key="foo", url="https://foobar.com/")
    assert test_client._url == "https://foobar.com"


def test_client_build_url_method():
    # Create client for testing
    test_client = InOrbit(api_key="foo", url="https://foobar.com")

    # Test build url prepend base url
    assert test_client._build_url("/baz") == "https://foobar.com/baz"
    # Test build url ignores base url whn path starts with `http` or `https`
    assert test_client._build_url("http://foo.bar/baz") == "http://foo.bar/baz"
    assert test_client._build_url("https://foo.bar/baz") == "https://foo.bar/baz"


def test_client_get_session_opts():
    # Create client for testing
    test_client = InOrbit(api_key="foo", url="https://foobar.com")

    client_session_opts = test_client._get_session_opts()
    assert client_session_opts == {"headers": {"X-Auth-InOrbit-App-Key": "foo"}}


def test_client_http_request(requests_mock):
    test_client = InOrbit(api_key="foo", url="https://test.com")
    requests_mock.get("http://test.com/foo", json={"foo": "bar"})
    response = test_client.http_request("get", "http://test.com/foo").json()
    assert response == {"foo": "bar"}

    requests_mock.post("http://test.com/bar", text="OK")
    response = test_client.http_request("post", "http://test.com/bar")
    assert response.text == "OK"

    with pytest.raises(inorbit.exceptions.InOrbitAuthenticationError) as excinfo:
        requests_mock.get(
            "http://test.com/foo",
            status_code=403,
            json={"error": "AUTHENTICATION_ERROR: wrong credentials"},
        )
        _ = test_client.http_request("get", "http://test.com/foo")

    assert excinfo.value.args[0] == "AUTHENTICATION_ERROR: wrong credentials"

    with pytest.raises(inorbit.exceptions.InOrbitError) as excinfo:
        requests_mock.get("http://test.com/foo", status_code=500, text="Unexpected error")
        _ = test_client.http_request("get", "http://test.com/foo")

    assert excinfo.value.args[0] == "(500) Unexpected error"


def test_inorbit_client_http_get_requests(requests_mock):
    test_client = InOrbit(api_key="foo", url="https://test.com")

    # Test client parameters
    requests_mock.get(
        url="https://test.com/configuration/list",
        status_code=200,
        json=[
            {
                "id": "cpuLoadPercentage",
                "kind": "IncidentDefinition",
                "label": "My CPU incident",
                "scope": "company",
                "suppressed": False,
            }
        ],
    )
    response = test_client.http_get(
        "/configuration/list", query_data={"kind": "IncidentDefinition"}
    )
    assert response.status_code == 200
    assert response.request.query == "kind=incidentdefinition"
    assert "id" in response.json()[0]
    assert "kind" in response.json()[0]
    assert "label" in response.json()[0]
    assert "scope" in response.json()[0]
    assert "suppressed" in response.json()[0]


def test_inorbit_client_http_post_requests(requests_mock):
    test_client = InOrbit(api_key="foo", url="https://test.com")

    # Test `configuration/apply` endpoint

    # happy path
    requests_mock.post(
        "https://test.com/configuration/apply", status_code=200, text="Configuration Applied"
    )
    response = test_client.http_post("/configuration/apply")
    assert response.status_code == 200
    assert response.text == "Configuration Applied"

    # validation, schema and quota error
    requests_mock.post("https://test.com/configuration/apply", status_code=400, text="TODO")
    with pytest.raises(inorbit.exceptions.InOrbitError) as excinfo:
        response = test_client.http_post("/configuration/apply")
        assert response.status_code == 400  # bad_request
        assert response.text == "TODO"

    # authorization error
    requests_mock.post("https://test.com/configuration/apply", status_code=401, text="TODO")
    with pytest.raises(inorbit.exceptions.InOrbitError) as excinfo:
        response = test_client.http_post("/configuration/apply")
        assert response.status_code == 401  # unauthorized
        assert response.text == "TODO"

    # internal server error
    requests_mock.post("https://test.com/configuration/apply", status_code=500, text="TODO")
    with pytest.raises(inorbit.exceptions.InOrbitError) as excinfo:
        response = test_client.http_post("/configuration/apply")
        assert response.status_code == 500  # internal_server_error
        assert response.text == "TODO"

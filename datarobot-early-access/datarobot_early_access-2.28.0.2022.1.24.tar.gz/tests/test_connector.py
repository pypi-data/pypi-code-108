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
import responses
import six

from datarobot import Connector


@responses.activate
def test_list(connectors_endpoint, connectors_list_server_resp):
    responses.add(responses.GET, connectors_endpoint, json=connectors_list_server_resp)
    connectors = Connector.list()
    for connector, server_payload in zip(connectors, connectors_list_server_resp["data"]):
        assert connector.id == server_payload["id"]
        assert connector.creator == server_payload["creatorId"]
        assert connector.configuration_id == server_payload["configurationId"]
        assert connector.base_name == server_payload["baseName"]
        assert connector.canonical_name == server_payload["canonicalName"]


@responses.activate
def test_get(connectors_endpoint, s3_connector_server_resp):
    connector_id = s3_connector_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(connectors_endpoint, connector_id),
        json=s3_connector_server_resp,
    )

    connector = Connector.get(connector_id)
    assert connector.id == s3_connector_server_resp["id"]
    assert connector.creator == s3_connector_server_resp["creatorId"]
    assert connector.configuration_id == s3_connector_server_resp["configurationId"]
    assert connector.base_name == s3_connector_server_resp["baseName"]
    assert connector.canonical_name == s3_connector_server_resp["canonicalName"]


@responses.activate
def test_future_proof(connectors_endpoint, s3_connector_server_resp):
    connector_id = s3_connector_server_resp["id"]
    resp = dict(s3_connector_server_resp, new_key="new")
    responses.add(responses.GET, "{}{}/".format(connectors_endpoint, connector_id), json=resp)

    connector = Connector.get(connector_id)
    assert connector.id == connector_id


@responses.activate
def test_create(
    connectors_endpoint,
    driver_libraries_endpoint,
    driver_library_upload_server_resp,
    s3_connector_server_resp,
):
    connector_id = s3_connector_server_resp["id"]
    responses.add(responses.POST, driver_libraries_endpoint, json=driver_library_upload_server_resp)
    responses.add(
        responses.POST,
        connectors_endpoint,
        json=s3_connector_server_resp,
        adding_headers={"Location": "https://host_name.com/status/status-id/"},
    )
    location = "https://host_name.com/externalConnectors/{}/".format(connector_id)
    responses.add(
        responses.GET,
        "https://host_name.com/status/status-id/",
        status=303,
        body="",
        content_type="application/json",
        adding_headers={"Location": location},
    )
    responses.add(
        responses.GET,
        "{}{}/".format(connectors_endpoint, connector_id),
        json=s3_connector_server_resp,
    )

    with mock.patch("os.path.exists"):
        with mock.patch("datarobot.rest.open", create=True) as open_mock:
            open_mock.return_value = six.StringIO("thra\ntata\nrata")
            connector = Connector.create("/tmp/{}".format(s3_connector_server_resp["baseName"]))

    assert connector.id == s3_connector_server_resp["id"]
    assert connector.creator == s3_connector_server_resp["creatorId"]
    assert connector.configuration_id == s3_connector_server_resp["configurationId"]
    assert connector.base_name == s3_connector_server_resp["baseName"]
    assert connector.canonical_name == s3_connector_server_resp["canonicalName"]


@responses.activate
def test_update(
    connectors_endpoint,
    driver_libraries_endpoint,
    driver_library_upload_server_resp,
    s3_connector_server_resp,
):
    connector_id = s3_connector_server_resp["id"]

    responses.add(
        responses.GET,
        "{}{}/".format(connectors_endpoint, connector_id),
        json=s3_connector_server_resp,
    )
    responses.add(responses.POST, driver_libraries_endpoint, json=driver_library_upload_server_resp)
    responses.add(
        responses.PATCH,
        "{}{}/".format(connectors_endpoint, connector_id),
        json=s3_connector_server_resp,
        adding_headers={"Location": "https://host_name.com/status/status-id/"},
    )
    location = "https://host_name.com/externalConnectors/{}/".format(connector_id)
    responses.add(
        responses.GET,
        "https://host_name.com/status/status-id/",
        status=303,
        body="",
        content_type="application/json",
        adding_headers={"Location": location},
    )
    responses.add(
        responses.GET,
        "{}{}/".format(connectors_endpoint, connector_id),
        json=s3_connector_server_resp,
    )

    with mock.patch("os.path.exists"):
        with mock.patch("datarobot.rest.open", create=True) as open_mock:
            open_mock.return_value = six.StringIO("thra\ntata\nrata")
            connector = Connector.get(connector_id)
            connector = connector.update("/tmp/{}".format(s3_connector_server_resp["baseName"]))

    assert connector.id == s3_connector_server_resp["id"]
    assert connector.creator == s3_connector_server_resp["creatorId"]
    assert connector.configuration_id == s3_connector_server_resp["configurationId"]
    assert connector.base_name == s3_connector_server_resp["baseName"]
    assert connector.canonical_name == s3_connector_server_resp["canonicalName"]


@responses.activate
def test_delete(connectors_endpoint, s3_connector_server_resp):
    connector_id = s3_connector_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(connectors_endpoint, connector_id),
        json=s3_connector_server_resp,
    )
    delete_url = "{}{}/".format(connectors_endpoint, connector_id)
    responses.add(responses.DELETE, delete_url)

    driver = Connector.get(connector_id)
    driver.delete()
    assert responses.calls[1].request.method == responses.DELETE
    assert responses.calls[1].request.url == delete_url

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
from datetime import datetime

import pytest
import responses

from datarobot import DataStore, SharingAccess
from datarobot.utils import parse_time
from tests.utils import request_body_to_json


@responses.activate
def test_list(data_stores_endpoint, data_stores_list_server_resp):
    responses.add(responses.GET, data_stores_endpoint, json=data_stores_list_server_resp)

    data_stores = DataStore.list()

    for data_store, server_payload in zip(data_stores, data_stores_list_server_resp["data"]):
        assert data_store.id == server_payload["id"]
        assert data_store.type == server_payload["type"]
        assert data_store.canonical_name == server_payload["canonicalName"]
        assert data_store.creator == server_payload["creator"]
        assert data_store.updated == parse_time(server_payload["updated"])
        assert data_store.params.driver_id == server_payload["params"]["driverId"]
        assert data_store.params.jdbc_url == server_payload["params"]["jdbcUrl"]


@responses.activate
def test_list_no_jdbc_url(data_stores_endpoint, data_stores_list_server_resp_no_jdbc_url):
    responses.add(
        responses.GET, data_stores_endpoint, json=data_stores_list_server_resp_no_jdbc_url
    )

    data_stores = DataStore.list()

    for data_store, server_payload in zip(
        data_stores, data_stores_list_server_resp_no_jdbc_url["data"]
    ):
        assert data_store.id == server_payload["id"]
        assert data_store.type == server_payload["type"]
        assert data_store.canonical_name == server_payload["canonicalName"]
        assert data_store.creator == server_payload["creator"]
        assert data_store.updated == parse_time(server_payload["updated"])
        assert data_store.params.driver_id == server_payload["params"]["driverId"]
        assert data_store.params.jdbc_url is None
        assert "jdbcUrl" not in server_payload["params"]


@responses.activate
def test_get(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp,
    )

    data_store = DataStore.get(data_store_id)

    assert data_store.id == postgresql_data_store_server_resp["id"]
    assert data_store.type == postgresql_data_store_server_resp["type"]
    assert data_store.canonical_name == postgresql_data_store_server_resp["canonicalName"]
    assert data_store.creator == postgresql_data_store_server_resp["creator"]
    assert data_store.updated == parse_time(postgresql_data_store_server_resp["updated"])
    assert data_store.params.driver_id == postgresql_data_store_server_resp["params"]["driverId"]
    assert data_store.params.jdbc_url == postgresql_data_store_server_resp["params"]["jdbcUrl"]


@responses.activate
def test_get_no_jdbc_url(data_stores_endpoint, postgresql_data_store_server_resp_no_jdbc_url):
    data_store_id = postgresql_data_store_server_resp_no_jdbc_url["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp_no_jdbc_url,
    )

    data_store = DataStore.get(data_store_id)

    server_resp = postgresql_data_store_server_resp_no_jdbc_url

    assert data_store.id == server_resp["id"]
    assert data_store.type == server_resp["type"]
    assert data_store.canonical_name == server_resp["canonicalName"]
    assert data_store.creator == server_resp["creator"]
    assert data_store.updated == parse_time(server_resp["updated"])
    assert data_store.params.driver_id == server_resp["params"]["driverId"]
    assert data_store.params.jdbc_url is None
    assert "jdbcUrl" not in server_resp["params"]


@responses.activate
def test_future_proof(data_stores_endpoint, postgresql_data_store_server_resp):
    aug_res = dict(postgresql_data_store_server_resp, newest="NEW_KEY")
    aug_res["params"]["newKey"] = "hihihi"
    data_store_id = aug_res["id"]
    responses.add(responses.GET, "{}{}/".format(data_stores_endpoint, data_store_id), json=aug_res)

    data_store = DataStore.get(data_store_id)

    assert data_store.id == data_store_id


@responses.activate
def test_create(data_stores_endpoint, postgresql_data_store_server_resp):
    responses.add(responses.POST, data_stores_endpoint, json=postgresql_data_store_server_resp)

    data_store = DataStore.create(
        data_store_type=postgresql_data_store_server_resp["type"],
        canonical_name=postgresql_data_store_server_resp["canonicalName"],
        driver_id=postgresql_data_store_server_resp["params"]["driverId"],
        jdbc_url=postgresql_data_store_server_resp["params"]["jdbcUrl"],
    )

    assert data_store.id == postgresql_data_store_server_resp["id"]
    assert data_store.type == postgresql_data_store_server_resp["type"]
    assert data_store.canonical_name == postgresql_data_store_server_resp["canonicalName"]
    assert data_store.creator == postgresql_data_store_server_resp["creator"]
    assert data_store.updated == parse_time(postgresql_data_store_server_resp["updated"])
    assert data_store.params.driver_id == postgresql_data_store_server_resp["params"]["driverId"]
    assert data_store.params.jdbc_url == postgresql_data_store_server_resp["params"]["jdbcUrl"]


@responses.activate
def test_update(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp,
    )
    updated_data_store_server_resp = dict(
        postgresql_data_store_server_resp,
        canonicalName="updated_canonical_name",
        params={"driverId": "updated_driver_id", "jdbcUrl": "updated_jdbc_url"},
    )
    responses.add(
        responses.PATCH,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=updated_data_store_server_resp,
    )

    data_store = DataStore.get(data_store_id)

    data_store.update(
        canonical_name=updated_data_store_server_resp["canonicalName"],
        driver_id=updated_data_store_server_resp["params"]["driverId"],
        jdbc_url=updated_data_store_server_resp["params"]["jdbcUrl"],
    )

    assert data_store.id == updated_data_store_server_resp["id"]
    assert data_store.type == updated_data_store_server_resp["type"]
    assert data_store.canonical_name == updated_data_store_server_resp["canonicalName"]
    assert data_store.creator == updated_data_store_server_resp["creator"]
    assert data_store.updated == parse_time(postgresql_data_store_server_resp["updated"])
    assert data_store.params.driver_id == updated_data_store_server_resp["params"]["driverId"]
    assert data_store.params.jdbc_url == updated_data_store_server_resp["params"]["jdbcUrl"]


@responses.activate
def test_unable_to_change_type(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp,
    )
    responses.add(
        responses.PATCH,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp,
    )

    data_store = DataStore.get(data_store_id)
    data_store._type = "new_type"
    data_store.update()
    new_data_store = DataStore.get(data_store_id)

    assert new_data_store.type == postgresql_data_store_server_resp["type"]


@responses.activate
def test_unable_to_change_creator(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp,
    )
    responses.add(
        responses.PATCH,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp,
    )

    data_store = DataStore.get(data_store_id)
    data_store._creator = "new_creator"
    data_store.update()
    new_data_store = DataStore.get(data_store_id)

    assert new_data_store.creator == postgresql_data_store_server_resp["creator"]


@responses.activate
def test_unable_to_change_updated_time(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp,
    )
    responses.add(
        responses.PATCH,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp,
    )

    data_store = DataStore.get(data_store_id)
    data_store._updated = datetime.now()
    data_store.update()
    new_data_store = DataStore.get(data_store_id)

    assert new_data_store.updated == parse_time(postgresql_data_store_server_resp["updated"])


@responses.activate
def test_delete(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp,
    )
    delete_url = "{}{}/".format(data_stores_endpoint, data_store_id)
    responses.add(responses.DELETE, delete_url)

    data_store = DataStore.get(data_store_id)
    data_store.delete()

    assert responses.calls[1].request.method == responses.DELETE
    assert responses.calls[1].request.url == delete_url


@responses.activate
def test_connection_test(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp,
    )
    responses.add(
        responses.POST,
        "{}{}/test/".format(data_stores_endpoint, data_store_id),
        json={"message": "Connection successful"},
    )

    data_store = DataStore.get(data_store_id)
    resp = data_store.test(username="my_username", password="my_password")

    assert resp["message"] == "Connection successful"


@responses.activate
def test_schemas_list(
    data_stores_endpoint, postgresql_data_store_server_resp, postgresql_schemas_list_server_resp
):
    data_store_id = postgresql_data_store_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp,
    )
    responses.add(
        responses.POST,
        "{}{}/schemas/".format(data_stores_endpoint, data_store_id),
        json=postgresql_schemas_list_server_resp,
    )

    data_store = DataStore.get(data_store_id)
    resp = data_store.schemas(username="my_username", password="my_password")

    assert resp == postgresql_schemas_list_server_resp


@responses.activate
def test_tables_list(
    data_stores_endpoint, postgresql_data_store_server_resp, postgresql_tables_list_server_resp
):
    data_store_id = postgresql_data_store_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp,
    )
    responses.add(
        responses.POST,
        "{}{}/tables/".format(data_stores_endpoint, data_store_id),
        json=postgresql_tables_list_server_resp,
    )

    data_store = DataStore.get(data_store_id)
    resp = data_store.tables(username="my_username", password="my_password", schema="demo")

    assert resp == postgresql_tables_list_server_resp


@responses.activate
@pytest.mark.parametrize("extra_keys", [{}, {"newKey": "blah"}])
def test_get_access_list(data_stores_endpoint, postgresql_data_store_server_resp, extra_keys):
    data_store = DataStore.from_server_data(postgresql_data_store_server_resp)
    access_list = {
        "data": [
            {
                "username": "me@datarobot.com",
                "userId": "1234deadbeeffeeddead4321",
                "role": "OWNER",
                "canShare": True,
            }
        ],
        "count": 1,
        "previous": None,
        "next": None,
    }
    access_record = access_list["data"][0]
    access_record.update(extra_keys)
    responses.add(
        responses.GET,
        "{}{}/accessControl/".format(data_stores_endpoint, data_store.id),
        json=access_list,
    )

    response = data_store.get_access_list()
    assert len(response) == 1

    share_info = response[0]
    assert share_info.username == access_record["username"]
    assert share_info.user_id == access_record["userId"]
    assert share_info.role == access_record["role"]
    assert share_info.can_share == access_record["canShare"]


@responses.activate
def test_share(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store = DataStore.from_server_data(postgresql_data_store_server_resp)
    request = SharingAccess("me@datarobot.com", "EDITOR")
    responses.add(
        responses.PATCH,
        "{}{}/accessControl/".format(data_stores_endpoint, data_store.id),
        status=204,
    )

    data_store.share([request])

    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == {"data": [{"username": "me@datarobot.com", "role": "EDITOR"}]}


@responses.activate
def test_remove(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store = DataStore.from_server_data(postgresql_data_store_server_resp)
    request = SharingAccess("me@datarobot.com", None)
    responses.add(
        responses.PATCH,
        "{}{}/accessControl/".format(data_stores_endpoint, data_store.id),
        status=204,
    )

    data_store.share([request])

    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == {"data": [{"username": "me@datarobot.com", "role": None}]}


@responses.activate
def test_share_with_grant(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store = DataStore.from_server_data(postgresql_data_store_server_resp)
    responses.add(
        responses.PATCH,
        "{}{}/accessControl/".format(data_stores_endpoint, data_store.id),
        status=204,
    )

    data_store.share(
        [
            SharingAccess("me@datarobot.com", "EDITOR", can_share=True),
            SharingAccess("other@datarobot.com", "CONSUMER", can_share=False),
        ]
    )

    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == {
        "data": [
            {"username": "me@datarobot.com", "role": "EDITOR", "canShare": True},
            {"username": "other@datarobot.com", "role": "CONSUMER", "canShare": False},
        ]
    }

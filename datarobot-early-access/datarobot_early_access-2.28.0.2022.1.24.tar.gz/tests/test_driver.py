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

from datarobot import DataDriver


@responses.activate
def test_list(drivers_endpoint, drivers_list_server_resp):
    responses.add(responses.GET, drivers_endpoint, json=drivers_list_server_resp)
    drivers = DataDriver.list()
    for driver, server_payload in zip(drivers, drivers_list_server_resp["data"]):
        assert driver.id == server_payload["id"]
        assert driver.class_name == server_payload["className"]
        assert driver.base_names == server_payload["baseNames"]
        assert driver.canonical_name == server_payload["canonicalName"]
        assert driver.creator == server_payload["creator"]


@responses.activate
def test_get(drivers_endpoint, postgresql_driver_server_resp):
    driver_id = postgresql_driver_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(drivers_endpoint, driver_id),
        json=postgresql_driver_server_resp,
    )

    driver = DataDriver.get(driver_id)
    assert driver.id == postgresql_driver_server_resp["id"]
    assert driver.class_name == postgresql_driver_server_resp["className"]
    assert driver.base_names == postgresql_driver_server_resp["baseNames"]
    assert driver.canonical_name == postgresql_driver_server_resp["canonicalName"]
    assert driver.creator == postgresql_driver_server_resp["creator"]


@responses.activate
def test_future_proof(drivers_endpoint, postgresql_driver_server_resp):
    driver_id = postgresql_driver_server_resp["id"]
    resp = dict(postgresql_driver_server_resp, new_key="new")
    responses.add(responses.GET, "{}{}/".format(drivers_endpoint, driver_id), json=resp)

    driver = DataDriver.get(driver_id)
    assert driver.id == driver_id


@responses.activate
def test_create(
    drivers_endpoint,
    driver_libraries_endpoint,
    driver_library_upload_server_resp,
    postgresql_driver_server_resp,
):
    responses.add(responses.POST, driver_libraries_endpoint, json=driver_library_upload_server_resp)
    responses.add(responses.POST, drivers_endpoint, json=postgresql_driver_server_resp)

    with mock.patch("os.path.exists"):
        with mock.patch("datarobot.rest.open", create=True) as open_mock:
            open_mock.return_value = six.StringIO("thra\ntata\nrata")
            driver = DataDriver.create(
                class_name=postgresql_driver_server_resp["className"],
                canonical_name=postgresql_driver_server_resp["canonicalName"],
                files=[
                    "/tmp/{}".format(name) for name in postgresql_driver_server_resp["baseNames"]
                ],
            )
    assert driver.id == postgresql_driver_server_resp["id"]
    assert driver.class_name == postgresql_driver_server_resp["className"]
    assert driver.base_names == postgresql_driver_server_resp["baseNames"]
    assert driver.canonical_name == postgresql_driver_server_resp["canonicalName"]
    assert driver.creator == postgresql_driver_server_resp["creator"]


@responses.activate
def test_create_local_multiple_libraries(
    drivers_endpoint,
    driver_libraries_endpoint,
    driver_library_upload_server_resp,
    postgresql_driver_server_resp,
):
    postgresql_driver_server_resp["baseNames"] += postgresql_driver_server_resp["baseNames"]
    responses.add(responses.POST, driver_libraries_endpoint, json=driver_library_upload_server_resp)
    responses.add(responses.POST, drivers_endpoint, json=postgresql_driver_server_resp)

    with mock.patch("os.path.exists"):
        with mock.patch("datarobot.rest.open", create=True) as open_mock:
            open_mock.return_value = six.StringIO("thra\ntata\nrata")
            # send with multiple libraries
            driver = DataDriver.create(
                class_name=postgresql_driver_server_resp["className"],
                canonical_name=postgresql_driver_server_resp["canonicalName"],
                files=[
                    "/tmp/{}".format(name) for name in postgresql_driver_server_resp["baseNames"]
                ],
            )
    assert driver.id == postgresql_driver_server_resp["id"]
    assert driver.class_name == postgresql_driver_server_resp["className"]
    assert driver.base_names == postgresql_driver_server_resp["baseNames"]
    assert driver.canonical_name == postgresql_driver_server_resp["canonicalName"]
    assert driver.creator == postgresql_driver_server_resp["creator"]


@responses.activate
def test_update(drivers_endpoint, postgresql_driver_server_resp):
    driver_id = postgresql_driver_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(drivers_endpoint, driver_id),
        json=postgresql_driver_server_resp,
    )

    updated_postgresql_driver_server_resp = dict(
        postgresql_driver_server_resp, className="NewClassName", canonicalName="NewCanonicalName"
    )

    responses.add(
        responses.PATCH,
        "{}{}/".format(drivers_endpoint, driver_id),
        json=updated_postgresql_driver_server_resp,
    )

    driver = DataDriver.get(driver_id)
    driver.update(class_name="NewClassName", canonical_name="NewCanonicalName")
    assert driver.class_name == updated_postgresql_driver_server_resp["className"]
    assert driver.canonical_name == updated_postgresql_driver_server_resp["canonicalName"]


@responses.activate
def test_update_unable_to_change_base_names(
    drivers_endpoint, postgresql_driver_server_resp, mysql_driver_server_resp
):
    driver_id = postgresql_driver_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(drivers_endpoint, driver_id),
        json=postgresql_driver_server_resp,
    )

    responses.add(
        responses.PATCH,
        "{}{}/".format(drivers_endpoint, driver_id),
        json=postgresql_driver_server_resp,
    )

    driver = DataDriver.get(driver_id)

    driver._base_names = mysql_driver_server_resp["baseNames"]
    driver.update()

    # get driver from backend
    new_driver = DataDriver.get(driver_id)

    # assert server side has not been changed
    assert new_driver.base_names != mysql_driver_server_resp["baseNames"]
    assert new_driver.base_names == postgresql_driver_server_resp["baseNames"]


@responses.activate
def test_update_unable_to_change_creator(
    drivers_endpoint, postgresql_driver_server_resp, mysql_driver_server_resp
):
    driver_id = postgresql_driver_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(drivers_endpoint, driver_id),
        json=postgresql_driver_server_resp,
    )

    responses.add(
        responses.PATCH,
        "{}{}/".format(drivers_endpoint, driver_id),
        json=postgresql_driver_server_resp,
    )

    driver = DataDriver.get(driver_id)

    driver._creator = mysql_driver_server_resp["creator"]
    driver.update()

    # get driver from backend
    new_driver = DataDriver.get(driver_id)

    # assert server side has not been changed
    assert new_driver.creator != mysql_driver_server_resp["creator"]
    assert new_driver.creator == postgresql_driver_server_resp["creator"]


@responses.activate
def test_delete(drivers_endpoint, postgresql_driver_server_resp):
    driver_id = postgresql_driver_server_resp["id"]
    responses.add(
        responses.GET,
        "{}{}/".format(drivers_endpoint, driver_id),
        json=postgresql_driver_server_resp,
    )
    delete_url = "{}{}/".format(drivers_endpoint, driver_id)
    responses.add(responses.DELETE, delete_url)

    driver = DataDriver.get(driver_id)
    driver.delete()
    assert responses.calls[1].request.method == responses.DELETE
    assert responses.calls[1].request.url == delete_url

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
from uuid import uuid4

import pytest
import responses

from datarobot import PredictionServer


@pytest.fixture()
def prediction_server_data_cloud():
    return {
        "id": "5c2aad800000000000000000",
        "url": "https://predictions.example.com",
        "datarobot-key": str(uuid4()),
    }


@pytest.fixture()
def prediction_server_data_on_prem():
    return {
        "id": None,
        "url": "https://predictions.example.com",
        "datarobot-key": None,
    }


def make_prediction_server_list_response(prediction_server_data):
    return {"count": 1, "next": None, "previous": None, "data": [prediction_server_data]}


@responses.activate
@pytest.mark.parametrize(
    "prediction_server_data_fixture",
    ["prediction_server_data_cloud", "prediction_server_data_on_prem"],
)
def test_prediction_server_list(request, prediction_server_data_fixture):
    prediction_server_data = request.getfixturevalue(prediction_server_data_fixture)

    server_list_response = make_prediction_server_list_response(prediction_server_data)
    responses.add(
        responses.GET,
        "https://host_name.com/predictionServers/",
        status=200,
        content_type="application/json",
        body=json.dumps(server_list_response),
    )

    prediction_servers = PredictionServer.list()
    assert len(prediction_servers) == 1

    prediction_server = prediction_servers[0]
    assert prediction_server.id == prediction_server_data["id"]
    assert prediction_server.url == prediction_server_data["url"]
    assert prediction_server.datarobot_key == prediction_server_data["datarobot-key"]

    repr = "PredictionServer({url})".format(url=prediction_server_data["url"])
    assert str(prediction_server) == repr

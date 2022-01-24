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

from datarobot import Model
from datarobot.errors import ClientError
from datarobot.models.confusion_chart import ConfusionChart


@pytest.fixture
def confusion_chart_validation_data(model_id, confusion_chart_data):
    return {"source": "validation", "sourceModelId": model_id, "data": confusion_chart_data}


@pytest.fixture
def confusion_chart_parent_model_validation_data(parent_model_id, confusion_chart_data):
    return {"source": "validation", "sourceModelId": parent_model_id, "data": confusion_chart_data}


@pytest.fixture
def confusion_chart_parent_model_holdout_data(parent_model_id, confusion_chart_data):
    return {"source": "holdout", "sourceModelId": parent_model_id, "data": confusion_chart_data}


@pytest.fixture
def confusion_chart_validation_metadata_server_data():
    return {
        "source": "validation",
        "classNames": ["1", "2", "3"],
        "totalMatrixSum": 24,
        "relevantClassesPositions": [[1]],
    }


@pytest.fixture
def confusion_chart_holdout_metadata_server_data():
    return {
        "source": "holdout",
        "classNames": ["1", "2", "3"],
        "totalMatrixSum": 24,
        "relevantClassesPositions": [[1]],
    }


def test_instantiation(confusion_chart_validation_data):
    confusion_chart_validation_data["data"]["classes"] = ["1", "2", "3"]
    confusion_chart = ConfusionChart.from_server_data(confusion_chart_validation_data)

    assert confusion_chart.classes == ["1", "2", "3"]
    assert confusion_chart.confusion_matrix == [[9, 0, 0], [0, 4, 1], [0, 1, 9]]
    assert confusion_chart.source == "validation"
    assert confusion_chart.source_model_id == confusion_chart_validation_data["sourceModelId"]


def test_future_proof(confusion_chart_validation_data):
    data_with_future_keys = dict(confusion_chart_validation_data, new_key="some future data")
    data_with_future_keys["data"]["classMetrics"][0]["new_key"] = "some future bin data"
    data_with_future_keys["data"]["classes"] = ["1", "2", "3"]
    confusion_chart = ConfusionChart.from_server_data(data_with_future_keys)

    assert confusion_chart.classes == ["1", "2", "3"]
    assert confusion_chart.confusion_matrix == [[9, 0, 0], [0, 4, 1], [0, 1, 9]]
    assert confusion_chart.source == "validation"


@pytest.fixture
def confusion_chart_validation_data_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/confusionCharts/{}/".format(
        project_id, model_id, "validation"
    )


@pytest.fixture
def confusion_chart_parent_model_validation_data_url(project_id, parent_model_id):
    return "https://host_name.com/projects/{}/models/{}/confusionCharts/{}/".format(
        project_id, parent_model_id, "validation"
    )


@pytest.fixture
def confusion_chart_list_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/confusionCharts/".format(
        project_id, model_id
    )


@pytest.fixture
def confusion_chart_parent_list_url(project_id, parent_model_id):
    return "https://host_name.com/projects/{}/models/{}/confusionCharts/".format(
        project_id, parent_model_id
    )


@pytest.fixture
def frozen_model_url(project_id, model_id):
    return "https://host_name.com/projects/{}/frozenModels/{}/".format(project_id, model_id)


@pytest.fixture
def confusion_chart_validation_metadata_response(
    project_url, model_id, confusion_chart_validation_metadata_server_data
):
    responses.add(
        responses.GET,
        "{}models/{}/confusionCharts/validation/metadata/".format(project_url, model_id),
        json=confusion_chart_validation_metadata_server_data,
        content_type="application/json",
    )


@pytest.fixture
def confusion_chart_parent_model_validation_metadata_response(
    project_url, parent_model_id, confusion_chart_validation_metadata_server_data
):
    responses.add(
        responses.GET,
        "{}models/{}/confusionCharts/validation/metadata/".format(project_url, parent_model_id),
        json=confusion_chart_validation_metadata_server_data,
        content_type="application/json",
    )


@pytest.fixture
def confusion_chart_parent_model_holdout_metadata_response(
    project_url, parent_model_id, confusion_chart_validation_metadata_server_data
):
    responses.add(
        responses.GET,
        "{}models/{}/confusionCharts/holdout/metadata/".format(project_url, parent_model_id),
        json=confusion_chart_validation_metadata_server_data,
        content_type="application/json",
    )


@responses.activate
@pytest.mark.usefixtures("confusion_chart_validation_metadata_response")
def test_get_validation_confusion_chart(
    confusion_chart_validation_data, confusion_chart_validation_data_url, project_id, model_id
):
    responses.add(
        responses.GET,
        confusion_chart_validation_data_url,
        status=200,
        content_type="application/json",
        body=json.dumps(confusion_chart_validation_data),
    )
    model = Model(id=model_id, project_id=project_id)
    cm = model.get_confusion_chart("validation")

    assert cm.source == confusion_chart_validation_data["source"]
    assert cm.classes == ["1", "2", "3"]
    assert cm.confusion_matrix == [[9, 0, 0], [0, 4, 1], [0, 1, 9]]
    assert cm.source_model_id == model_id


@responses.activate
def test_get_frozen_validation_confusion_chart_no_fallback(
    confusion_chart_validation_data_url, project_id, model_id
):
    responses.add(responses.GET, confusion_chart_validation_data_url, status=404)
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    with pytest.raises(ClientError):
        model.get_confusion_chart("validation")


@responses.activate
@pytest.mark.usefixtures(
    "confusion_chart_parent_model_validation_metadata_response", "known_warning"
)
def test_get_frozen_validation_confusion_chart_with_fallback(
    confusion_chart_parent_model_validation_data,
    confusion_chart_validation_data_url,
    confusion_chart_parent_model_validation_data_url,
    frozen_model_url,
    project_id,
    model_id,
    parent_model_id,
    frozen_json,
):

    responses.add(responses.GET, confusion_chart_validation_data_url, status=404)
    responses.add(
        responses.GET,
        frozen_model_url,
        body=frozen_json,
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        confusion_chart_parent_model_validation_data_url,
        status=200,
        content_type="application/json",
        body=json.dumps(confusion_chart_parent_model_validation_data),
    )
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    cm = model.get_confusion_chart("validation", fallback_to_parent_insights=True)

    assert cm.source == confusion_chart_parent_model_validation_data["source"]
    assert cm.classes == ["1", "2", "3"]
    assert cm.confusion_matrix == [[9, 0, 0], [0, 4, 1], [0, 1, 9]]
    assert cm.source_model_id == parent_model_id


@responses.activate
@pytest.mark.usefixtures("confusion_chart_validation_metadata_response")
def test_get_all_confusion_chart(
    confusion_chart_validation_data, confusion_chart_list_url, project_id, model_id
):
    responses.add(
        responses.GET,
        confusion_chart_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps({"charts": [confusion_chart_validation_data]}),
    )
    model = Model(id=model_id, project_id=project_id)
    cm_list = model.get_all_confusion_charts()

    assert len(cm_list) == 1
    assert cm_list[0].source == confusion_chart_validation_data["source"]
    assert cm_list[0].classes == ["1", "2", "3"]
    assert cm_list[0].confusion_matrix == [[9, 0, 0], [0, 4, 1], [0, 1, 9]]
    assert cm_list[0].source_model_id == model_id


@responses.activate
@pytest.mark.usefixtures("confusion_chart_validation_metadata_response")
def test_get_frozen_all_confusion_chart_no_fallback(
    confusion_chart_validation_data, confusion_chart_list_url, project_id, model_id
):
    responses.add(
        responses.GET,
        confusion_chart_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps({"charts": [confusion_chart_validation_data]}),
    )
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    cm_list = model.get_all_confusion_charts()

    assert len(cm_list) == 1
    assert cm_list[0].source == confusion_chart_validation_data["source"]
    assert cm_list[0].classes == ["1", "2", "3"]
    assert cm_list[0].confusion_matrix == [[9, 0, 0], [0, 4, 1], [0, 1, 9]]
    assert cm_list[0].source_model_id == model_id


@responses.activate
@pytest.mark.usefixtures(
    "confusion_chart_validation_metadata_response",
    "confusion_chart_parent_model_validation_metadata_response",
    "confusion_chart_parent_model_holdout_metadata_response",
    "known_warning",
)
def test_get_frozen_all_confusion_chart_with_fallback(
    confusion_chart_validation_data,
    confusion_chart_parent_model_validation_data,
    confusion_chart_parent_model_holdout_data,
    confusion_chart_list_url,
    confusion_chart_parent_list_url,
    frozen_model_url,
    project_id,
    model_id,
    parent_model_id,
    frozen_json,
):
    responses.add(
        responses.GET,
        confusion_chart_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps({"charts": [confusion_chart_validation_data]}),
    )
    responses.add(
        responses.GET,
        frozen_model_url,
        body=frozen_json,
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        confusion_chart_parent_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps(
            {
                "charts": [
                    confusion_chart_parent_model_validation_data,
                    confusion_chart_parent_model_holdout_data,
                ]
            }
        ),
    )
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    cm_list = model.get_all_confusion_charts(fallback_to_parent_insights=True)

    assert len(cm_list) == 2
    assert cm_list[0].source == confusion_chart_validation_data["source"]
    assert cm_list[0].classes == ["1", "2", "3"]
    assert cm_list[0].confusion_matrix == [[9, 0, 0], [0, 4, 1], [0, 1, 9]]
    assert cm_list[0].source_model_id == model_id

    assert cm_list[1].source == confusion_chart_parent_model_holdout_data["source"]
    assert cm_list[1].classes == ["1", "2", "3"]
    assert cm_list[1].confusion_matrix == [[9, 0, 0], [0, 4, 1], [0, 1, 9]]
    assert cm_list[1].source_model_id == parent_model_id

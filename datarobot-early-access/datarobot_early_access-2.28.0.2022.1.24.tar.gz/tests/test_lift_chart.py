# -*- coding: utf-8 -*-
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
from datarobot.models.lift_chart import LiftChart


@pytest.fixture
def lift_chart_validation_data(model_id, lift_chart_bins_data):
    return {"source": "validation", "bins": lift_chart_bins_data, "sourceModelId": model_id}


@pytest.fixture
def multiclass_lift_chart_validation_data(model_id, lift_chart_bins_data):
    return {
        "source": "validation",
        "classBins": [
            {"targetClass": "classA", "bins": lift_chart_bins_data},
            {"targetClass": "classB", "bins": lift_chart_bins_data},
            {"targetClass": "classC", "bins": lift_chart_bins_data},
        ],
    }


@pytest.fixture
def multilabel_lift_chart_validation_data(model_id, project_id, lift_chart_bins_data):
    return get_multilabel_lift_chart_validation_data(model_id, project_id, lift_chart_bins_data)


def get_multilabel_lift_chart_validation_data(model_id, project_id, lift_chart_bins_data):
    return {
        "projectId": project_id,
        "labels": ["cat", u"🐕"],
        "modelId": model_id,
        "source": "validation",
        "labelBins": [
            {"label": "cat", "bins": lift_chart_bins_data},
            {"label": u"🐕", "bins": lift_chart_bins_data},
        ],
    }


@pytest.fixture
def multilabel_lift_chart_validation_parent_data(parent_model_id, project_id, lift_chart_bins_data):
    return get_multilabel_lift_chart_validation_data(
        parent_model_id, project_id, lift_chart_bins_data
    )


@pytest.fixture
def lift_chart_parent_model_validation_data(parent_model_id, lift_chart_bins_data):
    return {"source": "validation", "bins": lift_chart_bins_data, "sourceModelId": parent_model_id}


@pytest.fixture
def lift_chart_parent_model_holdout_data(parent_model_id, lift_chart_bins_data):
    return {"source": "holdout", "bins": lift_chart_bins_data, "sourceModelId": parent_model_id}


@pytest.fixture
def expected_bin_data(lift_chart_validation_data):
    expected_bins = [dict(bin_data) for bin_data in lift_chart_validation_data["bins"]]
    for expected in expected_bins:
        weight = expected.pop("binWeight")
        expected["bin_weight"] = weight
    return expected_bins


def test_instantiation(lift_chart_validation_data, expected_bin_data):
    lc = LiftChart.from_server_data(lift_chart_validation_data)

    assert lc.source == lift_chart_validation_data["source"]
    assert lc.bins == expected_bin_data


def test_future_proof(lift_chart_validation_data):
    data_with_future_keys = dict(lift_chart_validation_data, new_key="some future lift data")
    data_with_future_keys["bins"][0]["new_key"] = "some future bin data"
    LiftChart.from_server_data(data_with_future_keys)


@pytest.fixture
def lift_chart_validation_data_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/liftChart/validation/".format(
        project_id, model_id
    )


@pytest.fixture
def multiclass_lift_chart_validation_data_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/multiclassLiftChart/validation/".format(
        project_id, model_id
    )


@pytest.fixture
def multiclass_lift_chart_list_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/multiclassLiftChart/".format(
        project_id, model_id
    )


@pytest.fixture
def multilabel_lift_chart_validation_data_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/multilabelLiftCharts/validation/".format(
        project_id, model_id
    )


@pytest.fixture
def multilabel_lift_chart_validation_data_parent_url(project_id, parent_model_id):
    return "https://host_name.com/projects/{}/models/{}/multilabelLiftCharts/validation/".format(
        project_id, parent_model_id
    )


@pytest.fixture
def multilabel_lift_chart_list_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/multilabelLiftCharts/".format(
        project_id, model_id
    )


@pytest.fixture
def multilabel_lift_chart_parent_list_url(project_id, parent_model_id):
    return "https://host_name.com/projects/{}/models/{}/multilabelLiftCharts/".format(
        project_id, parent_model_id
    )


@pytest.fixture
def lift_chart_parent_model_validation_data_url(project_id, parent_model_id):
    return "https://host_name.com/projects/{}/models/{}/liftChart/validation/".format(
        project_id, parent_model_id
    )


@pytest.fixture
def lift_chart_list_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/liftChart/".format(project_id, model_id)


@pytest.fixture
def lift_chart_parent_list_url(project_id, parent_model_id):
    return "https://host_name.com/projects/{}/models/{}/liftChart/".format(
        project_id, parent_model_id
    )


@pytest.fixture
def frozen_model_url(project_id, model_id):
    return "https://host_name.com/projects/{}/frozenModels/{}/".format(project_id, model_id)


@responses.activate
def test_get_validation_lift_chart(
    lift_chart_validation_data,
    expected_bin_data,
    lift_chart_validation_data_url,
    project_id,
    model_id,
):
    responses.add(
        responses.GET,
        lift_chart_validation_data_url,
        status=200,
        content_type="application/json",
        body=json.dumps(lift_chart_validation_data),
    )
    model = Model(id=model_id, project_id=project_id)
    lc = model.get_lift_chart("validation")

    assert lc.source == lift_chart_validation_data["source"]
    assert lc.bins == expected_bin_data
    assert lc.source_model_id == model_id


@responses.activate
def test_get_validation_multiclass_lift_chart(
    multiclass_lift_chart_validation_data,
    expected_bin_data,
    multiclass_lift_chart_validation_data_url,
    project_id,
    model_id,
):
    responses.add(
        responses.GET,
        multiclass_lift_chart_validation_data_url,
        status=200,
        content_type="application/json",
        body=json.dumps(multiclass_lift_chart_validation_data),
    )
    model = Model(id=model_id, project_id=project_id)
    lcs = model.get_multiclass_lift_chart("validation")
    # 3-class multiclass contains 3 records for each class
    assert len(lcs) == 3
    for lc in lcs:
        assert lc.source == multiclass_lift_chart_validation_data["source"]
        assert lc.bins == expected_bin_data
        assert lc.source_model_id == model_id


@responses.activate
def test_get_all_multiclass_lift_charts(
    multiclass_lift_chart_validation_data,
    expected_bin_data,
    multiclass_lift_chart_list_url,
    project_id,
    model_id,
):
    responses.add(
        responses.GET,
        multiclass_lift_chart_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps({"charts": [multiclass_lift_chart_validation_data]}),
    )
    model = Model(id=model_id, project_id=project_id)
    lift_charts = model.get_all_multiclass_lift_charts()

    assert len(lift_charts) == 3
    for lift_chart in lift_charts:
        assert lift_chart.source == multiclass_lift_chart_validation_data["source"]
        assert lift_chart.bins == expected_bin_data
        assert lift_chart.source_model_id == model_id


@responses.activate
def test_get_validation_multilabel_lift_charts(
    multilabel_lift_chart_validation_data,
    expected_bin_data,
    multilabel_lift_chart_validation_data_url,
    project_id,
    model_id,
):
    responses.add(
        responses.GET,
        multilabel_lift_chart_validation_data_url,
        status=200,
        content_type="application/json",
        body=json.dumps(multilabel_lift_chart_validation_data),
    )
    model = Model(id=model_id, project_id=project_id)
    lift_charts = model.get_multilabel_lift_charts("validation")

    expected_labels = ["cat", u"🐕"]

    assert len(lift_charts) == len(expected_labels)
    for lift_chart, expected_label in zip(lift_charts, expected_labels):
        assert lift_chart.source == "validation"
        assert lift_chart.bins == expected_bin_data
        assert lift_chart.source_model_id == model_id
        assert lift_chart.target_class == expected_label


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_get_validation_multilabel_lift_charts_fallback_to_parent_insight(
    multilabel_lift_chart_validation_parent_data,
    expected_bin_data,
    multilabel_lift_chart_validation_data_url,
    multilabel_lift_chart_validation_data_parent_url,
    project_id,
    model_id,
    parent_model_id,
    frozen_json,
    frozen_model_url,
):
    responses.add(responses.GET, multilabel_lift_chart_validation_data_url, status=404)
    responses.add(
        responses.GET,
        frozen_model_url,
        body=frozen_json,
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        multilabel_lift_chart_validation_data_parent_url,
        status=200,
        content_type="application/json",
        body=json.dumps(multilabel_lift_chart_validation_parent_data),
    )
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    lift_charts = model.get_multilabel_lift_charts("validation", fallback_to_parent_insights=True)

    expected_labels = ["cat", u"🐕"]

    assert len(lift_charts) == len(expected_labels)
    for lift_chart, expected_label in zip(lift_charts, expected_labels):
        assert lift_chart.source == "validation"
        assert lift_chart.bins == expected_bin_data
        assert lift_chart.source_model_id == parent_model_id
        assert lift_chart.target_class == expected_label


@responses.activate
def test_get_validation_multilabel_lift_charts_no_charts_and_fallback_flag_not_set(
    multilabel_lift_chart_validation_data_url, project_id, model_id, parent_model_id,
):
    responses.add(responses.GET, multilabel_lift_chart_validation_data_url, status=404)
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    with pytest.raises(ClientError):
        model.get_multilabel_lift_charts("validation")


@responses.activate
def test_get_frozen_validation_lift_chart_no_fallback(
    lift_chart_validation_data_url, project_id, model_id
):
    responses.add(responses.GET, lift_chart_validation_data_url, status=404)
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    with pytest.raises(ClientError):
        model.get_lift_chart("validation")


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_get_frozen_validation_lift_chart_with_fallback(
    lift_chart_parent_model_validation_data,
    expected_bin_data,
    lift_chart_validation_data_url,
    lift_chart_parent_model_validation_data_url,
    frozen_model_url,
    project_id,
    model_id,
    parent_model_id,
    frozen_json,
):

    responses.add(responses.GET, lift_chart_validation_data_url, status=404)
    responses.add(
        responses.GET,
        frozen_model_url,
        body=frozen_json,
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        lift_chart_parent_model_validation_data_url,
        status=200,
        content_type="application/json",
        body=json.dumps(lift_chart_parent_model_validation_data),
    )
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    lc = model.get_lift_chart("validation", fallback_to_parent_insights=True)

    assert lc.source == lift_chart_parent_model_validation_data["source"]
    assert lc.bins == expected_bin_data
    assert lc.source_model_id == parent_model_id


@responses.activate
def test_get_all_lift_charts(
    lift_chart_validation_data, expected_bin_data, lift_chart_list_url, project_id, model_id
):
    responses.add(
        responses.GET,
        lift_chart_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps({"charts": [lift_chart_validation_data]}),
    )
    model = Model(id=model_id, project_id=project_id)
    lc_list = model.get_all_lift_charts()

    assert len(lc_list) == 1
    assert lc_list[0].source == lift_chart_validation_data["source"]
    assert lc_list[0].bins == expected_bin_data
    assert lc_list[0].source_model_id == model_id


@responses.activate
def test_get_frozen_all_lift_charts_no_fallback(
    lift_chart_validation_data, expected_bin_data, lift_chart_list_url, project_id, model_id
):
    responses.add(
        responses.GET,
        lift_chart_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps({"charts": [lift_chart_validation_data]}),
    )
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    lc_list = model.get_all_lift_charts()

    assert len(lc_list) == 1
    assert lc_list[0].source == lift_chart_validation_data["source"]
    assert lc_list[0].bins == expected_bin_data
    assert lc_list[0].source_model_id == model_id


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_get_frozen_all_lift_charts_with_fallback(
    lift_chart_validation_data,
    lift_chart_parent_model_validation_data,
    lift_chart_parent_model_holdout_data,
    expected_bin_data,
    lift_chart_list_url,
    lift_chart_parent_list_url,
    frozen_model_url,
    project_id,
    model_id,
    parent_model_id,
    frozen_json,
):
    responses.add(
        responses.GET,
        lift_chart_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps({"charts": [lift_chart_validation_data]}),
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
        lift_chart_parent_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps(
            {
                "charts": [
                    lift_chart_parent_model_validation_data,
                    lift_chart_parent_model_holdout_data,
                ]
            }
        ),
    )
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    lc_list = model.get_all_lift_charts(fallback_to_parent_insights=True)

    assert len(lc_list) == 2
    assert lc_list[0].source == lift_chart_validation_data["source"]
    assert lc_list[0].bins == expected_bin_data
    assert lc_list[0].source_model_id == model_id

    assert lc_list[1].source == lift_chart_parent_model_holdout_data["source"]
    assert lc_list[1].bins == expected_bin_data
    assert lc_list[1].source_model_id == parent_model_id

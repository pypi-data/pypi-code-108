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

from datarobot import DatetimeModel, Model, ModelRecommendation
from datarobot.enums import RECOMMENDED_MODEL_TYPE


@pytest.fixture
def list_recommended_model_json():
    model_list = [
        {
            "recommendationType": RECOMMENDED_MODEL_TYPE.MOST_ACCURATE,
            "modelId": "model1",
            "projectId": "project1",
        },
        {
            "recommendationType": RECOMMENDED_MODEL_TYPE.FAST_ACCURATE,
            "modelId": "model2",
            "projectId": "project1",
        },
    ]
    return json.dumps(model_list)


@pytest.fixture
def recommended_model_json():
    model = {
        "recommendationType": "Fast & Accurate",
        "modelId": "5ad8e121fcf4c87d96ae02dd",
        "projectId": "project1",
    }
    return json.dumps(model)


@pytest.fixture
def recommended_model_extra_field_json():
    model = {
        "recommendationType": "Fast & Accurate",
        "modelId": "5ad8e121fcf4c87d96ae02dd",
        "projectId": "project1",
        "extraField": "value",
    }
    return json.dumps(model)


@pytest.fixture
def non_datetime_project_json(project_id):
    project = {
        "partition": {"cvMethod": "random"},
        "projectId": project_id,
    }
    return json.dumps(project)


@pytest.fixture
def datetime_project_json(project_id):
    project = {
        "partition": {"cvMethod": "datetime"},
        "projectId": project_id,
    }
    return json.dumps(project)


@pytest.fixture
def most_accurate_recommended_model_json(project_id, model_id):
    model = {
        "recommendationType": RECOMMENDED_MODEL_TYPE.MOST_ACCURATE,
        "modelId": model_id,
        "projectId": project_id,
    }
    return json.dumps(model)


@pytest.fixture
def recommended_datetime_model_json(project_id, model_id):
    model = {
        "backtests": [
            {
                "index": 0,
                "score": 0.7,
                "status": "COMPLETED",
                "training_start_date": "2015-10-26T19:00:00.000000Z",
                "training_duration": "P0Y1M0D",
                "training_row_count": 880,
                "training_end_date": "2015-11-26T19:00:00.000000Z",
            },
        ],
        "projectId": project_id,
        "dataSelectionMethod": "rowCount",
        "trainingInfo": {
            "predictionTrainingDuration": "P0Y1M0D",
            "holdoutTrainingStartDate": "2015-10-26T19:00:00.000000Z",
            "predictionTrainingStartDate": "2015-10-26T19:00:00.000000Z",
            "holdoutTrainingDuration": "P0Y1M0D",
            "predictionTrainingRowCount": 880,
            "holdoutTrainingEndDate": "2015-12-10T19:00:00.000000Z",
            "predictionTrainingEndDate": "2015-12-10T19:00:00.000000Z",
            "holdoutTrainingRowCount": 880,
        },
        "id": model_id,
        "effective_feature_derivation_window_start": -120,
        "effective_feature_derivation_window_end": 0,
    }
    return json.dumps(model)


@responses.activate
def test_recommended_model_default(recommended_model_json):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/recommendedModels/recommendedModel/",
        body=recommended_model_json,
    )
    recommended_model = ModelRecommendation.get("p-id")
    assert recommended_model.recommendation_type == "Fast & Accurate"
    assert recommended_model.model_id == "5ad8e121fcf4c87d96ae02dd"
    assert recommended_model.project_id == "project1"


@responses.activate
def test_recommended_model_specific(list_recommended_model_json):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/recommendedModels/",
        body=list_recommended_model_json,
    )
    recommended_model = ModelRecommendation.get("p-id", RECOMMENDED_MODEL_TYPE.MOST_ACCURATE)
    assert recommended_model.recommendation_type == "Most Accurate"
    assert recommended_model.model_id == "model1"
    assert recommended_model.project_id == "project1"


@responses.activate
def test_recommended_model_ignore_extra_fields(recommended_model_extra_field_json):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/recommendedModels/recommendedModel/",
        body=recommended_model_extra_field_json,
    )
    recommended_model = ModelRecommendation.get("p-id")
    assert recommended_model.recommendation_type == "Fast & Accurate"
    assert recommended_model.model_id == "5ad8e121fcf4c87d96ae02dd"
    assert recommended_model.project_id == "project1"
    assert not hasattr(recommended_model, "extraField")


@responses.activate
def test_recommended_model_list(list_recommended_model_json):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/recommendedModels/",
        body=list_recommended_model_json,
    )
    recommended_models = ModelRecommendation.get_all("p-id")
    assert len(recommended_models) == 2
    expected_models = json.loads(list_recommended_model_json)

    expected_model1 = next(model for model in expected_models if model["modelId"] == "model1")
    expected_model2 = next(model for model in expected_models if model["modelId"] == "model2")
    actual_model1 = [model for model in recommended_models if model.model_id == "model1"]
    actual_model2 = [model for model in recommended_models if model.model_id == "model2"]

    assert len(actual_model1) == 1
    assert len(actual_model2) == 1
    actual_model1 = actual_model1[0]
    actual_model2 = actual_model2[0]

    assert actual_model1.recommendation_type == expected_model1["recommendationType"]
    assert actual_model2.recommendation_type == expected_model2["recommendationType"]
    assert actual_model1.project_id == expected_model1["projectId"]
    assert actual_model2.project_id == expected_model2["projectId"]

    assert (
        ModelRecommendation.get_recommendation(
            recommended_models, RECOMMENDED_MODEL_TYPE.MOST_ACCURATE
        )
        is not None
    )

    assert (
        ModelRecommendation.get_recommendation(
            recommended_models, RECOMMENDED_MODEL_TYPE.RECOMMENDED_FOR_DEPLOYMENT
        )
        is None
    )


@responses.activate
def test_recommended_non_datetime_model(
    project_id, model_id, non_datetime_project_json, most_accurate_recommended_model_json
):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{pid}/".format(pid=project_id),
        status=200,
        body=non_datetime_project_json,
    )
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{pid}/models/{lid}/".format(pid=project_id, lid=model_id),
        status=200,
        body=most_accurate_recommended_model_json,
    )
    recommendation = ModelRecommendation(project_id, model_id, RECOMMENDED_MODEL_TYPE.MOST_ACCURATE)
    model = recommendation.get_model()
    assert isinstance(model, Model)
    assert hasattr(model, "model_type")
    assert not hasattr(model, "effective_feature_derivation_window_start")


@responses.activate
def test_recommended_datetime_model(
    project_id, model_id, datetime_project_json, recommended_datetime_model_json
):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{pid}/".format(pid=project_id),
        status=200,
        body=datetime_project_json,
    )
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{pid}/datetimeModels/{lid}/".format(
            pid=project_id, lid=model_id
        ),
        status=200,
        body=recommended_datetime_model_json,
    )
    recommendation = ModelRecommendation(project_id, model_id, RECOMMENDED_MODEL_TYPE.MOST_ACCURATE)
    model = recommendation.get_model()
    assert isinstance(model, DatetimeModel)
    assert hasattr(model, "model_type")
    assert hasattr(model, "effective_feature_derivation_window_start")
    assert model.effective_feature_derivation_window_start == -120
    assert model.effective_feature_derivation_window_end == 0

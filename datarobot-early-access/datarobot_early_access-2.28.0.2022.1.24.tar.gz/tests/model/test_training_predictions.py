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
import csv
import io
import json
import tempfile

import pandas as pd
import pytest
import responses
import six
import trafaret

from datarobot import TrainingPredictions
from datarobot.models.training_predictions import TrainingPredictionsRow


def _write_csv(lines):

    if six.PY2:

        buf = io.BytesIO()
        wr = csv.writer(buf)
        wr.writerows(lines)
        return buf.getvalue()

    buf = io.StringIO()
    wr = csv.writer(buf)
    wr.writerows(lines)
    return buf.getvalue().encode("utf-8")


@pytest.fixture
def prediction_id():
    return "59d92fe8962d7464ca8c6bd6"


@pytest.fixture
def predictions_with_shap_exp_csv():
    return """row_id,partition_id,prediction,class_1.0,class_0.0,explained_class,Explanation_1_feature_name,Explanation_1_feature_value,Explanation_1_strength,shap_remaining_total,shap_base_value
        0,TrainTestOverlap,0.0,0.311178247734139,0.6888217522658611,1.0,number_diagnoses,9,-0.07643818895488698,0.006562548084582246,0.39640626311300003
        1,TrainTestOverlap,0.0,0.2829861111111111,0.7170138888888888,1.0,number_diagnoses,6,0.06648347981438553,-0.013534302788801085,0.39640626311300003
        2,TrainTestOverlap,0.0,0.42699724517906334,0.5730027548209367,1.0,number_diagnoses,9,0.08556893050818416,-0.032619753482599656,0.39640626311300003
        3,TrainTestOverlap,0.0,0.32653061224489793,0.6734693877551021,1.0,number_diagnoses,3,0.05807900167179779,-0.0051298246462132885,0.39640626311300003
        4,TrainTestOverlap,0.0,0.06,0.94,1.0,number_inpatient,0,-0.056383896138088974,-0.0570362457984236,0.39640626311300003
        5,TrainTestOverlap,0.0,0.3774597495527728,0.6225402504472273,1.0,number_diagnoses,8,0.04847090471521205,-0.03250602234256627,0.39640626311300003
        6,TrainTestOverlap,0.0,0.13768115942028986,0.8623188405797102,1.0,admission_type_id,Elective,0.08996873371035077,0.040252262429918834,0.39640626311300003
        7,TrainTestOverlap,1.0,0.5300353356890459,0.4699646643109541,1.0,admission_type_id,Emergency,0.16263335056706338,-0.03241235442679378,0.39640626311300003
        8,TrainTestOverlap,1.0,0.6408668730650154,0.35913312693498456,1.0,number_inpatient,1,0.34801989552094514,-0.055934082238188985,0.39640626311300003
        9,TrainTestOverlap,0.0,0.2027972027972028,0.7972027972027972,1.0,number_inpatient,0,0.1146691220002886,-0.08407812406711129,0.39640626311300003
    """


@responses.activate
def test_get__no_requests_made(project_id, prediction_id):
    TrainingPredictions.get(project_id, prediction_id)
    assert len(responses.calls) == 0


@responses.activate
def test_list__ok(project_id, model_id, prediction_id):
    training_prediction_stub = [
        {
            "url": "https://host_name.com/projects/{}/trainingPredictions/{}//".format(
                project_id, prediction_id
            ),
            "id": prediction_id,
            "modelId": model_id,
            "dataSubset": "all",
        },
        {
            "url": "https://host_name.com/projects/{}/trainingPredictions/{}//".format(
                project_id, prediction_id
            ),
            "id": prediction_id,
            "modelId": model_id,
            "dataSubset": "all",
            "explanationAlgorithm": "shap",
            "maxExplanations": 7,
            "shapWarnings": {
                "partitionName": "holdout",
                "value": {"mismatchRowCount": 1, "maxNormalizedMismatch": 0.01},
            },
        },
    ]
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/trainingPredictions/".format(project_id),
        status=200,
        body=json.dumps({"data": training_prediction_stub}),
    )

    training_predictions_list = TrainingPredictions.list(project_id)

    assert len(training_predictions_list) == 2
    training_prediction = training_predictions_list[0]
    assert training_prediction.project_id == project_id
    assert training_prediction.model_id == model_id
    assert training_prediction.prediction_id == prediction_id
    training_prediction_with_shap_exp = training_predictions_list[1]
    assert training_prediction_with_shap_exp.project_id == project_id
    assert training_prediction_with_shap_exp.model_id == model_id
    assert training_prediction_with_shap_exp.explanation_algorithm == "shap"
    assert training_prediction_with_shap_exp.max_explanations == 7
    assert training_prediction_with_shap_exp.shap_warnings == {
        "partition_name": "holdout",
        "value": {"mismatch_row_count": 1, "max_normalized_mismatch": 0.01},
    }


@responses.activate
def test_list__no_url_in_api_response__error(project_id, model_id, prediction_id):
    training_prediction_stub = {
        "url": "",
        "id": prediction_id,
        "modelId": model_id,
        "trainingPredictionSet": "all",
    }
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/trainingPredictions/".format(project_id),
        status=200,
        body=json.dumps({"data": [training_prediction_stub]}),
    )

    with pytest.raises(trafaret.DataError):
        TrainingPredictions.list(project_id)


@responses.activate
def test_iterate_rows__empty_predictions__ok(project_id, prediction_id):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id,
    )
    response = {"data": [], "next": "{}?offset=100&limit=100".format(url)}
    responses.add(
        responses.GET, url, body=json.dumps(response), status=200, content_type="application/json",
    )

    obj = TrainingPredictions.get(project_id, prediction_id)

    assert list(obj.iterate_rows()) == []


@responses.activate
def test_iterate_rows__malfromed_predictions__data_error(project_id, prediction_id):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id,
    )
    items = [
        {
            "row_id": "wrong-id",
            "partition_id": "holdout",
            "prediction": 0.42,
            "prediction_values": [],
        }
    ]
    response = {"data": items, "next": "{}?offset=100&limit=100".format(url)}
    responses.add(
        responses.GET, url, body=json.dumps(response), status=200, content_type="application/json",
    )

    with pytest.raises(trafaret.DataError):
        obj = TrainingPredictions.get(project_id, prediction_id)
        it = obj.iterate_rows()
        next(it)


@responses.activate
def test_iterate_rows__extra_fields__ignored(project_id, prediction_id):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id,
    )
    items = [
        {
            "row_id": 1,
            "partition_id": 2,
            "prediction": 0.42,
            "prediction_values": [
                {
                    "label": "test-label",
                    "value": 0.42,
                    "extra-prediction": "you are going to win a lottery for sure",
                }
            ],
        },
    ]
    response = {"data": items, "next": "{}?offset=100&limit=100".format(url), "prev": None}
    responses.add(
        responses.GET, url, body=json.dumps(response), status=200, content_type="application/json",
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    assert list(obj.iterate_rows()) == [
        TrainingPredictionsRow(
            row_id=1,
            partition_id=2,
            prediction=0.42,
            prediction_values=[{"label": "test-label", "value": 0.42}],
            timestamp=None,
            forecast_point=None,
            forecast_distance=None,
            series_id=None,
            prediction_explanations=None,
            shap_metadata=None,
        )
    ]


@responses.activate
def test_iterate_rows__all_rows_at_once__ok(project_id, prediction_id):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id,
    )
    items = [
        {"row_id": 1, "partition_id": 2, "prediction": 0.42, "prediction_values": []},
        {"row_id": 2, "partition_id": 2, "prediction": 0.22, "prediction_values": []},
        {"row_id": 3, "partition_id": 2, "prediction": 0.82, "prediction_values": []},
    ]
    response = {"data": items, "next": None, "prev": None}
    responses.add(
        responses.GET, url, body=json.dumps(response), status=200, content_type="application/json",
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    assert len(list(obj.iterate_rows(batch_size=3))) == 3


@responses.activate
def test_iterate_rows__one_prediction__ok(project_id, prediction_id):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id,
    )
    items = [
        {"row_id": 1, "partition_id": 2, "prediction": 0.42, "prediction_values": []},
    ]
    response = {"data": items, "next": "{}?offset=100&limit=100".format(url)}
    responses.add(
        responses.GET, url, body=json.dumps(response), status=200, content_type="application/json",
    )

    obj = TrainingPredictions.get(project_id, prediction_id)

    assert list(obj.iterate_rows()) == [
        TrainingPredictionsRow(
            row_id=1,
            partition_id=2,
            prediction=0.42,
            prediction_values=[],
            timestamp=None,
            forecast_point=None,
            forecast_distance=None,
            series_id=None,
            prediction_explanations=None,
            shap_metadata=None,
        ),
    ]
    assert len(responses.calls) == 1


@responses.activate
def test_iterate_rows__one_prediction_with_shap_exp(project_id, prediction_id):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id,
    )
    items = [
        {
            "row_id": 1,
            "partition_id": 2,
            "prediction": 0.42,
            "prediction_values": [],
            "prediction_explanations": [
                {
                    "feature": "first_name",
                    "feature_value": "some_value",
                    "strength": -0.07,
                    "label": 1.0,
                },
                {"feature": "second_name", "feature_value": "0", "strength": -0.05, "label": 1.0},
            ],
            "shap_metadata": {
                "shap_base_value": 0.39,
                "shap_remaining_total": 0.03,
                "warnings": {"mismatch_row_count": 1, "max_normalized_mismatch": 0.01},
            },
        },
    ]
    response = {"data": items, "next": "{}?offset=100&limit=100".format(url)}
    responses.add(
        responses.GET, url, body=json.dumps(response), status=200, content_type="application/json"
    )

    training_predictions = TrainingPredictions.get(project_id, prediction_id)

    data = list(training_predictions.iterate_rows())
    assert len(data) == 1
    training_prediction = data[0]
    assert training_prediction.row_id == 1
    assert training_prediction.partition_id == 2
    assert training_prediction.prediction == 0.42
    assert training_prediction.prediction_values == []
    assert training_prediction.timestamp is None
    assert training_prediction.forecast_point is None
    assert training_prediction.forecast_distance is None
    assert training_prediction.series_id is None
    assert training_prediction.series_id is None
    assert training_prediction.prediction_explanations == [
        {"feature": "first_name", "feature_value": "some_value", "strength": -0.07, "label": 1.0},
        {"feature": "second_name", "feature_value": "0", "strength": -0.05, "label": 1.0},
    ]
    assert training_prediction.shap_metadata == {
        "shap_base_value": 0.39,
        "shap_remaining_total": 0.03,
        "warnings": {"mismatch_row_count": 1, "max_normalized_mismatch": 0.01},
    }
    assert len(responses.calls) == 1


@responses.activate
def test_iterate_rows__two_predictions_with_limit_equals_one__three_requests_were_made(
    project_id, prediction_id,
):
    items = [
        {"row_id": 1, "partition_id": 2, "prediction": 0.42, "prediction_values": []},
        {"row_id": 2, "partition_id": 2, "prediction": 0.22, "prediction_values": []},
    ]
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id,
    )
    body = {"data": items[:1], "next": "{}?offset=1&limit=1".format(url)}
    responses.add(
        responses.GET, url, body=json.dumps(body), status=200, content_type="application/json",
    )

    obj = TrainingPredictions.get(project_id, prediction_id)

    it = obj.iterate_rows(batch_size=1)

    assert next(it, None) == TrainingPredictionsRow(
        row_id=1,
        partition_id=2,
        prediction=0.42,
        prediction_values=[],
        timestamp=None,
        forecast_point=None,
        forecast_distance=None,
        series_id=None,
        prediction_explanations=None,
        shap_metadata=None,
    )
    assert len(responses.calls) == 1

    body2 = {"data": items[1:], "next": "{}?offset=2&limit=1".format(url)}
    responses.reset()
    responses.add(
        responses.GET,
        url,
        body=json.dumps(body2),
        status=200,
        content_type="application/json",
        match_querystring=False,
    )

    assert next(it, None) == TrainingPredictionsRow(
        row_id=2,
        partition_id=2,
        prediction=0.22,
        prediction_values=[],
        timestamp=None,
        forecast_point=None,
        forecast_distance=None,
        series_id=None,
        prediction_explanations=None,
        shap_metadata=None,
    )
    assert len(responses.calls) == 1

    body = {"data": [], "next": "{}?offset=3&limit=1".format(url)}
    responses.reset()
    responses.add(
        responses.GET, url, body=json.dumps(body), status=200, content_type="application/json",
    )

    assert next(it, None) is None
    assert len(responses.calls) == 1


@responses.activate
@pytest.mark.parametrize(
    ["serializer", "response"],
    [
        pytest.param(
            "json",
            {
                "body": lambda url: json.dumps(
                    {
                        "data": [
                            {
                                "row_id": 1,
                                "partition_id": 2,
                                "prediction": 0.42,
                                "prediction_values": [],
                            },
                            {
                                "row_id": 2,
                                "partition_id": 2,
                                "prediction": 0.22,
                                "prediction_values": [],
                            },
                        ],
                        "next": "{}?limit=20".format(url),
                    }
                ),
                "content_type": "application/json",
            },
            id="json",
        ),
        pytest.param(
            "csv",
            {
                "body": lambda url: _write_csv(
                    [["row_id", "partition_id", "prediction"], [1, 2, 0.42], [2, 2, 0.22]]
                ),
                "content_type": "text/csv",
                "stream": True,
            },
            id="csv",
        ),
    ],
)
def test_get_all_as_dataframe__regression_two_predictions__ok(
    project_id, prediction_id, project_url, project_with_target_json, serializer, response,
):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id,
    )
    response["body"] = response["body"](url)
    responses.add(responses.GET, url, status=200, **response)
    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    data_frame = obj.get_all_as_dataframe(serializer=serializer)

    assert isinstance(data_frame, pd.DataFrame)
    assert data_frame.shape == (2, 3)
    assert list(data_frame.columns) == [
        "row_id",
        "partition_id",
        "prediction",
    ]


@responses.activate
@pytest.mark.parametrize(
    ["serializer", "response"],
    [
        pytest.param(
            "json",
            {
                "body": lambda url: json.dumps(
                    {
                        "data": [
                            {
                                "row_id": 1,
                                "partition_id": "1960-01-01T00:00:00.000000Z",
                                "prediction": 0.42,
                                "prediction_values": [],
                                "timestamp": "1960-01-01T00:00:00.000000Z",
                                "forecast_point": "1959-12-01T00:00:00.000000Z",
                                "forecast_distance": 1,
                                "series_id": "1",
                            },
                            {
                                "row_id": 2,
                                "partition_id": "1960-01-01T00:00:00.000000Z",
                                "prediction": 0.22,
                                "prediction_values": [],
                                "timestamp": "1959-11-01T00:00:00.000000Z",
                                "forecast_point": "1959-12-01T00:00:00.000000Z",
                                "forecast_distance": 2,
                                "series_id": "1",
                            },
                        ],
                        "next": "{}?limit=20".format(url),
                    }
                ),
                "content_type": "application/json",
            },
            id="json",
        ),
        pytest.param(
            "csv",
            {
                "body": lambda url: _write_csv(
                    [
                        [
                            "row_id",
                            "partition_id",
                            "prediction",
                            "timestamp",
                            "forecast_point",
                            "forecast_distance",
                            "series_id",
                        ],
                        [
                            1,
                            "1960-01-01T00:00:00.000000Z",
                            0.42,
                            "1960-01-01T00:00:00.000000Z",
                            "1959-12-01T00:00:00.000000Z",
                            1,
                            "1",
                        ],
                        [
                            2,
                            "1960-01-01T00:00:00.000000Z",
                            0.22,
                            "1959-11-01T00:00:00.000000Z",
                            "1959-12-01T00:00:00.000000Z",
                            2,
                            "1",
                        ],
                    ]
                ),
                "content_type": "text/csv",
                "stream": True,
            },
            id="csv",
        ),
        pytest.param(
            "json",
            {
                "body": lambda url: json.dumps(
                    {
                        "data": [
                            {
                                "row_id": 1,
                                "partition_id": "1960-01-01T00:00:00.000000Z",
                                "prediction": 0.42,
                                "prediction_values": [],
                                "timestamp": "1960-01-01T00:00:00.000000Z",
                                "forecast_point": "1959-12-01T00:00:00.000000Z",
                                "forecast_distance": 1,
                                "series_id": 1,
                            },
                            {
                                "row_id": 2,
                                "partition_id": "1960-01-01T00:00:00.000000Z",
                                "prediction": 0.22,
                                "prediction_values": [],
                                "timestamp": "1959-11-01T00:00:00.000000Z",
                                "forecast_point": "1959-12-01T00:00:00.000000Z",
                                "forecast_distance": 2,
                                "series_id": 1,
                            },
                        ],
                        "next": "{}?limit=20".format(url),
                    }
                ),
                "content_type": "application/json",
            },
            id="json",
        ),
        pytest.param(
            "csv",
            {
                "body": lambda url: _write_csv(
                    [
                        [
                            "row_id",
                            "partition_id",
                            "prediction",
                            "timestamp",
                            "forecast_point",
                            "forecast_distance",
                            "series_id",
                        ],
                        [
                            1,
                            "1960-01-01T00:00:00.000000Z",
                            0.42,
                            "1960-01-01T00:00:00.000000Z",
                            "1959-12-01T00:00:00.000000Z",
                            1,
                            1,
                        ],
                        [
                            2,
                            "1960-01-01T00:00:00.000000Z",
                            0.22,
                            "1959-11-01T00:00:00.000000Z",
                            "1959-12-01T00:00:00.000000Z",
                            2,
                            1,
                        ],
                    ]
                ),
                "content_type": "text/csv",
                "stream": True,
            },
            id="csv",
        ),
    ],
)
def test_get_all_as_dataframe__timeseries_predictions__ok(
    project_id, prediction_id, project_url, project_with_target_json, serializer, response,
):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id,
    )
    response["body"] = response["body"](url)
    responses.add(responses.GET, url, status=200, **response)
    project_data = json.loads(project_with_target_json)
    project_data["partition"]["use_time_series"] = True
    responses.add(
        responses.GET,
        project_url,
        body=json.dumps(project_data),
        status=200,
        content_type="application/json",
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    data_frame = obj.get_all_as_dataframe(serializer=serializer)

    assert isinstance(data_frame, pd.DataFrame)
    assert data_frame.shape == (2, 7)
    assert set(data_frame.columns) == {
        "row_id",
        "partition_id",
        "prediction",
        "timestamp",
        "forecast_point",
        "forecast_distance",
        "series_id",
    }

    assert len(data_frame) == 2
    assert None not in data_frame.timestamp.unique()
    assert None not in data_frame.forecast_point.unique()
    assert all(isinstance(value, int) for value in data_frame.forecast_distance)


@responses.activate
@pytest.mark.parametrize(
    ["serializer", "response"],
    [
        pytest.param(
            "json",
            {
                "body": lambda url: json.dumps(
                    {
                        "data": [
                            {
                                "row_id": 1,
                                "partition_id": 2,
                                "prediction": 0.42,
                                "prediction_values": [],
                            },
                            {
                                "row_id": 2,
                                "partition_id": 2,
                                "prediction": 0.22,
                                "prediction_values": [],
                            },
                        ],
                        "next": "{}?limit=20".format(url),
                    }
                ),
                "content_type": "application/json",
            },
            id="json",
        ),
        pytest.param(
            "csv",
            {
                "body": lambda url: _write_csv(
                    [["row_id", "partition_id", "prediction"], [1, 2, 0.42], [2, 2, 0.22]]
                ),
                "content_type": "text/csv",
                "stream": True,
            },
            id="csv",
        ),
    ],
)
def test_download_to_csv__two_regression_predictions__ok(
    project_id, prediction_id, project_url, project_with_target_json, serializer, response,
):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id,
    )
    response["body"] = response["body"](url)
    responses.add(responses.GET, url, status=200, **response)
    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    with tempfile.NamedTemporaryFile(mode="r") as a_file:
        obj.download_to_csv(a_file.name, serializer=serializer)
        data_frame = pd.read_csv(a_file.name)

    assert data_frame.shape == (2, 3)
    assert set(data_frame.columns) == {"row_id", "partition_id", "prediction"}


@responses.activate
def test_iterate_rows__one_classification_prediction__ok(project_id, prediction_id):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id,
    )
    items = [
        {
            "row_id": 1,
            "partition_id": 2,
            "prediction": 0.42,
            "prediction_values": [{"label": "good", "value": 0.8}, {"label": "bad", "value": 0.2}],
        },
    ]
    response = {"data": items, "next": "{}?offset=100&limit=100".format(url)}
    responses.add(
        responses.GET, url, body=json.dumps(response), status=200, content_type="application/json",
    )

    obj = TrainingPredictions.get(project_id, prediction_id)

    assert list(obj.iterate_rows()) == [
        TrainingPredictionsRow(
            row_id=1,
            partition_id=2,
            prediction=0.42,
            prediction_values=[{"label": "good", "value": 0.8}, {"label": "bad", "value": 0.2}],
            timestamp=None,
            forecast_point=None,
            forecast_distance=None,
            series_id=None,
            prediction_explanations=None,
            shap_metadata=None,
        ),
    ]
    assert len(responses.calls) == 1


@responses.activate
@pytest.mark.parametrize(
    ["serializer", "response"],
    [
        pytest.param(
            "json",
            {
                "body": lambda url: json.dumps(
                    {
                        "data": [
                            {
                                "row_id": 1,
                                "partition_id": 2,
                                "prediction": 0.42,
                                "prediction_values": [
                                    {"label": "good", "value": 0.8},
                                    {"label": "bad", "value": 0.2},
                                ],
                            }
                        ],
                        "next": "{}?limit=20".format(url),
                    }
                ),
                "content_type": "application/json",
            },
            id="json",
        ),
        pytest.param(
            "csv",
            {
                "body": lambda url: _write_csv(
                    [
                        ["row_id", "partition_id", "prediction", "foo_good", "foo_bad"],
                        [1, 2, 0.42, 0.8, 0.2],
                    ]
                ),
                "content_type": "text/csv",
                "stream": True,
            },
            id="csv",
        ),
    ],
)
def test_get_all_as_dataframe__one_classification_prediction__ok(
    project_id, prediction_id, project_url, project_with_target_json, serializer, response,
):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id,
    )
    response["body"] = response["body"](url)
    responses.add(responses.GET, url, status=200, **response)

    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    data_frame = obj.get_all_as_dataframe(class_prefix="foo_", serializer=serializer)

    assert isinstance(data_frame, pd.DataFrame)
    assert data_frame.shape == (1, 5)
    assert set(data_frame.columns) == {
        "row_id",
        "partition_id",
        "prediction",
        "foo_good",
        "foo_bad",
    }


@responses.activate
@pytest.mark.parametrize(
    ["serializer", "response"],
    [
        pytest.param(
            "json",
            {
                "body": lambda url: json.dumps(
                    {
                        "data": [
                            {
                                "row_id": 1,
                                "partition_id": 2,
                                "prediction": 0.42,
                                "prediction_values": [
                                    {"label": "good", "value": 0.3},
                                    {"label": "bad", "value": 0.2},
                                    {"label": "ugly", "value": 0.2},
                                    {"label": "none", "value": 0.0},
                                ],
                            }
                        ],
                        "next": "{}?limit=20".format(url),
                    }
                ),
                "content_type": "application/json",
            },
            id="json",
        ),
        pytest.param(
            "csv",
            {
                "body": lambda url: _write_csv(
                    [
                        [
                            "row_id",
                            "partition_id",
                            "prediction",
                            "class_good",
                            "class_bad",
                            "class_ugly",
                            "class_none",
                        ],
                        [1, 2, 0.42, 0.3, 0.2, 0.2, 0.0],
                    ]
                ),
                "content_type": "text/csv",
                "stream": True,
            },
            id="csv",
        ),
    ],
)
def test_download_to_csv__multiclass_project__prediction__ok(
    project_id, prediction_id, project_url, project_with_target_json, serializer, response,
):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id,
    )
    response["body"] = response["body"](url)
    responses.add(responses.GET, url, status=200, **response)

    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    with tempfile.NamedTemporaryFile(mode="r") as a_file:
        obj.download_to_csv(a_file.name, serializer=serializer)
        data_frame = pd.read_csv(a_file.name)

    assert data_frame.shape == (1, 7)
    assert set(data_frame.columns) == {
        "row_id",
        "partition_id",
        "prediction",
        "class_good",
        "class_bad",
        "class_ugly",
        "class_none",
    }


@responses.activate
@pytest.mark.parametrize(
    ["serializer", "response"],
    [
        pytest.param(
            "json",
            {
                "body": lambda url: json.dumps(
                    {
                        "data": [
                            {
                                "row_id": 0,
                                "partition_id": "0.0",
                                "prediction": 0.0,
                                "prediction_threshold": 0.5,
                                "prediction_values": [
                                    {"label": 1.0, "value": 0.311178247734139},
                                    {"label": 0.0, "value": 0.6888217522658611},
                                ],
                                "prediction_explanations": [
                                    {
                                        "featureValue": "5",
                                        "strength": -0.07643818895488697,
                                        "feature": "number_diagnoses",
                                        "label": 1.0,
                                    },
                                ],
                                "shap_metadata": {
                                    "shap_base_value": 0.39640626311302185,
                                    "shap_remaining_total": 0.06644934718939229,
                                    "warnings": None,
                                },
                            }
                        ],
                        "next": "{}?limit=20".format(url),
                    }
                ),
                "content_type": "application/json",
            },
            id="json",
        ),
        pytest.param(
            "csv",
            {
                "body": lambda url: _write_csv(
                    [
                        [
                            "row_id",
                            "partition_id",
                            "prediction",
                            "class_1.0",
                            "class_0.0",
                            "explained_class",
                            "Explanation_1_feature_name",
                            "Explanation_1_feature_value",
                            "Explanation_1_strength",
                            "shap_remaining_total",
                            "shap_base_value",
                        ],
                        [
                            0,
                            0.0,
                            0.0,
                            0.311178247734139,
                            0.6888217522658611,
                            1.0,
                            "number_diagnoses",
                            5,
                            -0.07643818895488697,
                            "number_inpatient",
                            0,
                            -0.05988679910481005,
                            0.06644934718939229,
                            0.396406263113,
                        ],
                    ]
                ),
                "content_type": "text/csv",
                "stream": True,
            },
            id="csv",
        ),
    ],
)
def test_get_all_as_dataframe_one_classification_prediction_with_explanations(
    project_id, prediction_id, project_url, project_with_target_json, serializer, response
):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id
    )
    response["body"] = response["body"](url)
    responses.add(responses.GET, url, status=200, **response)

    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    data_frame = obj.get_all_as_dataframe(serializer=serializer)

    assert isinstance(data_frame, pd.DataFrame)
    assert data_frame.shape == (1, 11)
    assert set(data_frame.columns) == {
        "row_id",
        "partition_id",
        "prediction",
        "class_1.0",
        "class_0.0",
        "explained_class",
        "shap_remaining_total",
        "shap_base_value",
        "Explanation_1_feature_name",
        "Explanation_1_feature_value",
        "Explanation_1_strength",
    }


@responses.activate
@pytest.mark.parametrize(
    ["serializer", "response"],
    [
        pytest.param(
            "json",
            {
                "body": lambda url: json.dumps(
                    {
                        "data": [
                            {
                                "row_id": 0,
                                "partition_id": "0.0",
                                "prediction": 71700.0,
                                "prediction_values": [{"value": 71700.0, "label": "SalePrice"}],
                                "shap_metadata": {
                                    "shap_base_value": 31108.28125,
                                    "shap_remaining_total": -4045.506156357904,
                                    "warnings": None,
                                },
                                "prediction_explanations": [
                                    {
                                        "feature_value": "172632",
                                        "strength": 9021.030323424387,
                                        "feature": "MachineID",
                                        "label": "SalePrice",
                                    },
                                    {
                                        "feature_value": "3855",
                                        "strength": -4883.805345350174,
                                        "feature": "ModelID",
                                        "label": "SalePrice",
                                    },
                                ],
                            },
                            {
                                "row_id": 1,
                                "partition_id": "0.0",
                                "prediction": 12275.0,
                                "prediction_values": [{"value": 12275.0, "label": "SalePrice"}],
                                "shap_metadata": {
                                    "shap_base_value": 31108.28125,
                                    "shap_remaining_total": -3350.9689739794676,
                                    "warnings": None,
                                },
                                "prediction_explanations": [
                                    {
                                        "feature_value": "1986",
                                        "strength": -6307.912477762799,
                                        "feature": "YearMade",
                                        "label": "SalePrice",
                                    },
                                    {
                                        "feature_value": "1190700",
                                        "strength": -3257.09113279142,
                                        "feature": "MachineID",
                                        "label": "SalePrice",
                                    },
                                ],
                            },
                        ],
                        "next": "{}?limit=20".format(url),
                    }
                ),
                "content_type": "application/json",
            },
            id="json",
        ),
        pytest.param(
            "csv",
            {
                "body": lambda url: _write_csv(
                    [
                        [
                            "row_id",
                            "partition_id",
                            "prediction",
                            "Explanation_1_feature_name",
                            "Explanation_1_feature_value",
                            "Explanation_1_strength",
                            "Explanation_2_feature_name",
                            "Explanation_2_feature_value",
                            "Explanation_2_strength",
                            "shap_remaining_total",
                            "shap_base_value",
                        ],
                        [
                            0,
                            0.0,
                            71700.0,
                            "MachineID",
                            "172632",
                            9021.030323424387,
                            "ModelID",
                            "3855",
                            -4883.805345350174,
                            -4045.506156357904,
                            31108.28125,
                        ],
                        [
                            1,
                            0.0,
                            12275.0,
                            "YearMade",
                            "1986",
                            -6307.912477762799,
                            "MachineID",
                            "1190700",
                            -3257.09113279142,
                            -3350.9689739794676,
                            31108.28125,
                        ],
                    ]
                ),
                "content_type": "text/csv",
                "stream": True,
            },
            id="csv",
        ),
    ],
)
def test_get_all_as_dataframe_regression_predictions_with_explanations(
    project_id, prediction_id, project_url, project_with_target_json, serializer, response
):
    url = "https://host_name.com/projects/{}/trainingPredictions/{}/".format(
        project_id, prediction_id
    )
    response["body"] = response["body"](url)
    responses.add(responses.GET, url, status=200, **response)
    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )

    predictions = TrainingPredictions.get(project_id, prediction_id)
    data_frame = predictions.get_all_as_dataframe(serializer=serializer)

    assert isinstance(data_frame, pd.DataFrame)
    assert data_frame.shape == (2, 11)
    assert list(data_frame.columns) == [
        "row_id",
        "partition_id",
        "prediction",
        "Explanation_1_feature_name",
        "Explanation_1_feature_value",
        "Explanation_1_strength",
        "Explanation_2_feature_name",
        "Explanation_2_feature_value",
        "Explanation_2_strength",
        "shap_remaining_total",
        "shap_base_value",
    ]

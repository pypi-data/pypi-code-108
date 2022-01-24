# -*- encoding: utf-8 -*-
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
import json

from dateutil.tz import tzutc
import pandas as pd
import pytest
import responses

from datarobot import errors, Predictions
from datarobot.utils import parse_time
from tests.utils import add_response


@pytest.fixture
def sample_prediction():
    return {
        u"positiveClass": None,
        u"task": u"Regression",
        u"predictions": [
            {u"positiveProbability": None, u"prediction": 32.0, u"rowId": 0},
            {u"positiveProbability": None, u"prediction": 100.0, u"rowId": 1},
            {u"positiveProbability": None, u"prediction": 212.0, u"rowId": 2},
        ],
    }


@pytest.fixture
def predictions_regression_with_shap_explanations():
    return {
        "shapBaseValue": [31108.28125],
        "task": "Regression",
        "positiveClass": None,
        "predictions": [
            {
                "positiveProbability": None,
                "predictionExplanationMetadata": {"shapRemainingTotal": -6969.941378326501},
                "prediction": 27229.166666666668,
                "rowId": 0,
                "predictionExplanations": [
                    {
                        "featureValue": "2004",
                        "strength": 3090.8262156678165,
                        "feature": "YearMade",
                        "label": "SalePrice",
                    },
                    {
                        "featureValue": "999089",
                        "strength": -2788.4580943655205,
                        "feature": "MachineID",
                        "label": "SalePrice",
                    },
                    {
                        "featureValue": "2006",
                        "strength": -2286.181442643504,
                        "feature": "saledate (Year)",
                        "label": "SalePrice",
                    },
                ],
            },
            {
                "positiveProbability": None,
                "predictionExplanationMetadata": {"shapRemainingTotal": 13439.981135022792},
                "prediction": 60583.333333333336,
                "rowId": 1,
                "predictionExplanations": [
                    {
                        "featureValue": "117657",
                        "strength": 16035.069717943523,
                        "feature": "MachineID",
                        "label": "SalePrice",
                    },
                    {
                        "featureValue": "77",
                        "strength": 10105.427194858292,
                        "feature": "ModelID",
                        "label": "SalePrice",
                    },
                    {
                        "featureValue": "Medium",
                        "strength": 3432.899846833262,
                        "feature": "ProductSize",
                        "label": "SalePrice",
                    },
                ],
            },
        ],
    }


@pytest.fixture
def predictions_binary_with_shap_explanations():
    return {
        "shapBaseValue": [0.39640626311302185],
        "task": "Binary",
        "positiveClass": 1.0,
        "predictions": [
            {
                "positiveProbability": 0.311178247734139,
                "prediction": 0.0,
                "predictionExplanations": [
                    {
                        "featureValue": "9",
                        "strength": 0.05346482340175079,
                        "feature": "number_diagnoses",
                        "label": 1.0,
                    },
                    {
                        "featureValue": "0",
                        "strength": -0.049024358641319835,
                        "feature": "number_inpatient",
                        "label": 1.0,
                    },
                    {
                        "featureValue": "Surgery-Neuro",
                        "strength": -0.03165299590594699,
                        "feature": "medical_specialty",
                        "label": 1.0,
                    },
                ],
                "rowId": 0,
                "predictionValues": [
                    {"value": 0.3111782477000000, "label": 1.0},
                    {"value": 0.6888217522658611, "label": 0.0},
                ],
                # To test the case with empty metadata from API.
                "predictionExplanationMetadata": {"shapRemainingTotal": None},
                "predictionThreshold": 0.5,
            },
            {
                "positiveProbability": 0.2829861111111111,
                "prediction": 0.0,
                "predictionExplanations": [
                    {
                        "featureValue": "0",
                        "strength": -0.05744066866980976,
                        "feature": "number_inpatient",
                        "label": 1.0,
                    },
                    {
                        "featureValue": "6",
                        "strength": -0.04089034311313498,
                        "feature": "number_diagnoses",
                        "label": 1.0,
                    },
                    {
                        "featureValue": "[50-75)",
                        "strength": 0.03388593271674542,
                        "feature": "weight",
                        "label": 1.0,
                    },
                ],
                "rowId": 1,
                "predictionValues": [
                    {"value": 0.2829861111111111, "label": 1.0},
                    {"value": 0.7170138888888888, "label": 0.0},
                ],
                "predictionExplanationMetadata": {"shapRemainingTotal": -0.00887273281105585},
                "predictionThreshold": 0.5,
            },
        ],
    }


@pytest.fixture
def predictions_multilabel_json():
    predictions = {
        "positiveClass": None,
        "task": "Multilabel",
        "predictions": [
            {
                "predictionValues": [
                    {"threshold": 0.5, "value": 0.6, "label": "cat"},
                    {"threshold": 0.5, "value": 0.5, "label": u"🐕"},
                    {"threshold": 0.5, "value": 0.4, "label": "Maine Coon"},
                    {"threshold": 0.5, "value": 0.7, "label": "British_Shorthair"},
                ],
                "prediction": ["cat", "British_Shorthair"],
                "rowId": 0,
            },
            {
                "predictionValues": [
                    {"threshold": 0.5, "value": 0.1, "label": "cat"},
                    {"threshold": 0.5, "value": 0.4, "label": u"🐕"},
                    {"threshold": 0.5, "value": 0.4, "label": "Maine Coon"},
                    {"threshold": 0.5, "value": 0.1, "label": "British_Shorthair"},
                ],
                "prediction": [],
                "rowId": 1,
            },
        ],
    }
    return predictions


@pytest.fixture
def predictions_with_shap_exp_csv():
    return """row_id,prediction,Explanation_1_feature_name,Explanation_1_feature_value,Explanation_1_strength,shap_remaining_total,shap_base_value
    0,27229.166666666668,YearMade,2004,3090.8262156678165,-6969.941378326501,31108.28125
    1,60583.333333333336,MachineID,117657,16035.069717943523,13439.981135022792,31108.28125
    2,11800.0,fiSecondaryDesc,nan,-14385.515413569377,-4922.765764714323,31108.28125
    3,17453.125,fiSecondaryDesc,nan,-7614.76113549681,-6040.3950427868795,31108.28125
    4,11539.473684210527,Hydraulics_Flow,Standard,-14743.391828540229,-4825.41571693096,31108.28125
    5,22555.555555555555,MachineID,1001274,-6044.702269899164,-2508.024220884521,31108.28125
    6,60583.333333333336,MachineID,772701,20612.841554550116,8862.20929841619,31108.28125
    7,31200.0,MachineID,902002,13999.795343335558,-13908.076521619252,31108.28125
    8,67863.63636363637,YearMade,2008,30190.432159295826,6564.919474920468,31108.28125
    9,21176.470588235294,ProductSize,Large,7127.206390025408,-17059.016865184112,31108.28125
    """


@pytest.fixture
def predictions_metadata_with_shap_exp(prediction_id, project_id, model_id, dataset_id):
    url = "http://localhost/api/v2/projects/{}/predictions/{}/".format(project_id, prediction_id)
    return {
        "url": url,
        "id": prediction_id,
        "projectId": project_id,
        "modelId": model_id,
        "predictionDatasetId": dataset_id,
        "actualValueColumn": None,
        "forecastPoint": None,
        "includesPredictionIntervals": False,
        "predictionIntervalsSize": None,
        "predictionsStartDate": None,
        "predictionsEndDate": None,
        "explanationAlgorithm": "shap",
        "maxExplanations": 1,
        "shapWarnings": {"mismatchRowCount": 1, "maxNormalizedMismatch": 0.01},
    }


@pytest.fixture
def sample_prediction_metadata(prediction_id):
    project_id = "59d92fe8962d7464ca8c6bd6"
    url = "http://localhost/api/v2/projects/{}/predictions/{}/".format(project_id, prediction_id)

    return {
        "projectId": project_id,
        "id": prediction_id,
        "predictionDatasetId": "a_dataset_id",
        "modelId": "a_model_id",
        "includesPredictionIntervals": False,
        "predictionIntervalsSize": None,
        "url": url,
        "forecastPoint": "2017-01-01T15:00:00Z",
        "predictionsStartDate": None,
        "predictionsEndDate": None,
    }


@pytest.fixture
def prediction_id():
    return "59d92fe8962d7464ca8c6bd6"


@pytest.fixture
def model_id():
    return "modelid"


@pytest.fixture
def dataset_id():
    return "datasetid"


@pytest.fixture
def predictions_url(project_id, prediction_id):
    return "https://host_name.com/projects/{}/predictions/{}/".format(project_id, prediction_id)


@pytest.fixture
def predictions_metadata_url(project_id):
    return "https://host_name.com/projects/{}/predictionsMetadata/".format(project_id)


@pytest.fixture
def predictions_metadata_by_id_url(predictions_metadata_url, prediction_id):
    return predictions_metadata_url + "{}/".format(prediction_id)


@responses.activate
def test_get__fetches_metadata(project_id, prediction_id, sample_prediction_metadata):
    metadata_url = "https://host_name.com/projects/{}/predictionsMetadata/{}/".format(
        project_id, prediction_id,
    )
    responses.add(
        responses.GET,
        metadata_url,
        body=json.dumps(sample_prediction_metadata),
        status=200,
        content_type="application/json",
    )

    preds = Predictions.get(project_id, prediction_id)

    assert preds.project_id == project_id
    assert preds.prediction_id == prediction_id
    assert preds.model_id == sample_prediction_metadata["modelId"]
    assert preds.dataset_id == sample_prediction_metadata["predictionDatasetId"]
    assert preds.includes_prediction_intervals == (
        sample_prediction_metadata["includesPredictionIntervals"]
    )
    assert preds.forecast_point == parse_time(sample_prediction_metadata["forecastPoint"])
    assert preds.predictions_start_date == parse_time(
        sample_prediction_metadata["predictionsStartDate"]
    )
    assert preds.predictions_end_date == parse_time(
        sample_prediction_metadata["predictionsEndDate"]
    )
    assert preds.explanation_algorithm is None
    assert preds.max_explanations is None
    assert preds.shap_warnings is None


@responses.activate
def test_get_predictions_with_shap_explanations(
    project_id, prediction_id, predictions_metadata_with_shap_exp, predictions_metadata_by_id_url,
):
    mocked_response = predictions_metadata_with_shap_exp
    add_response(url=predictions_metadata_by_id_url, body=mocked_response)

    predictions = Predictions.get(project_id, prediction_id)

    assert predictions.project_id == project_id
    assert predictions.prediction_id == prediction_id
    assert predictions.model_id == mocked_response["modelId"]
    assert predictions.dataset_id == mocked_response["predictionDatasetId"]
    assert predictions.actual_value_column is None
    assert predictions.forecast_point is None
    assert not predictions.includes_prediction_intervals
    assert predictions.predictions_start_date is None
    assert predictions.predictions_end_date is None
    assert predictions.explanation_algorithm == mocked_response["explanationAlgorithm"]
    assert predictions.max_explanations == mocked_response["maxExplanations"]
    assert predictions.shap_warnings is not None
    assert (
        predictions.shap_warnings["mismatch_row_count"]
        == mocked_response["shapWarnings"]["mismatchRowCount"]
    )
    assert (
        predictions.shap_warnings["max_normalized_mismatch"]
        == mocked_response["shapWarnings"]["maxNormalizedMismatch"]
    )


@responses.activate
def test_list__ok(project_id, model_id, prediction_id, dataset_id, predictions_metadata_url):
    stub = [
        {
            "url": "http://localhost/api/v2/projects/{}/predictions/{}/".format(
                project_id, prediction_id
            ),
            "id": prediction_id,
            "modelId": model_id,
            "predictionDatasetId": dataset_id,
            "includesPredictionIntervals": False,
            "forecastPoint": "2017-01-01T15:00:00Z",
        },
        {
            "url": "http://localhost/api/v2/projects/{}/predictions/{}/".format(
                project_id, prediction_id
            ),
            "id": prediction_id,
            "modelId": model_id,
            "predictionDatasetId": dataset_id,
            "includesPredictionIntervals": False,
            "predictionsStartDate": "2019-05-19T00:00:00.000000Z",
            "predictionsEndDate": "2019-05-20T00:00:00.000000Z",
            "actualValueColumn": "actuals",
        },
        {
            "url": "http://localhost/api/v2/projects/{}/predictions/{}/".format(
                project_id, prediction_id
            ),
            "id": prediction_id,
            "projectId": project_id,
            "modelId": model_id,
            "predictionDatasetId": dataset_id,
            "includesPredictionIntervals": False,
            "predictionsStartDate": None,
            "predictionsEndDate": None,
            "predictionIntervalsSize": None,
            "actualValueColumn": None,
            "forecastPoint": None,
            "explanationAlgorithm": "shap",
            "maxExplanations": 1,
            "shapWarnings": None,
        },
    ]
    add_response(url=predictions_metadata_url, body={"data": stub})

    predictions_list = Predictions.list(project_id)

    assert len(predictions_list) == 3
    prediction = predictions_list[0]
    assert prediction.project_id == project_id
    assert prediction.model_id == model_id
    assert prediction.dataset_id == dataset_id
    assert prediction.prediction_id == prediction_id
    assert not prediction.includes_prediction_intervals
    assert prediction.prediction_intervals_size is None
    assert prediction.forecast_point == datetime(2017, 1, 1, 15, tzinfo=tzutc())
    assert prediction.predictions_start_date is None
    assert prediction.predictions_end_date is None
    assert prediction.explanation_algorithm is None
    assert prediction.max_explanations is None
    assert prediction.shap_warnings is None
    bulk_pred_metadata = predictions_list[1]
    assert bulk_pred_metadata.forecast_point is None
    assert bulk_pred_metadata.predictions_start_date == datetime(2019, 5, 19, tzinfo=tzutc())
    assert bulk_pred_metadata.predictions_end_date == datetime(2019, 5, 20, tzinfo=tzutc())
    assert bulk_pred_metadata.actual_value_column == "actuals"
    assert bulk_pred_metadata.explanation_algorithm is None
    assert bulk_pred_metadata.max_explanations is None
    assert bulk_pred_metadata.shap_warnings is None
    predictions_with_shap_exp = predictions_list[2]
    assert predictions_with_shap_exp.project_id == project_id
    assert predictions_with_shap_exp.model_id == model_id
    assert predictions_with_shap_exp.dataset_id == dataset_id
    assert predictions_with_shap_exp.prediction_id == prediction_id
    assert not predictions_with_shap_exp.includes_prediction_intervals
    assert predictions_with_shap_exp.prediction_intervals_size is None
    assert predictions_with_shap_exp.forecast_point is None
    assert predictions_with_shap_exp.predictions_start_date is None
    assert predictions_with_shap_exp.predictions_end_date is None
    assert predictions_with_shap_exp.explanation_algorithm == "shap"
    assert predictions_with_shap_exp.max_explanations == 1
    assert predictions_with_shap_exp.shap_warnings is None


@responses.activate
def test_get_all_as_dataframe__ok(
    project_id,
    prediction_id,
    project_with_target_json,
    sample_prediction,
    sample_prediction_metadata,
    predictions_url,
    predictions_metadata_by_id_url,
):
    add_response(predictions_url, sample_prediction)
    add_response(predictions_metadata_by_id_url, sample_prediction_metadata)

    obj = Predictions.get(project_id, prediction_id)
    data_frame = obj.get_all_as_dataframe()

    assert isinstance(data_frame, pd.DataFrame)
    assert data_frame.shape == (len(sample_prediction["predictions"]), 2)
    assert list(data_frame.columns) == [
        "prediction",
        "row_id",
    ]


@responses.activate
def test_get_all_as_dataframe_regression_json_serializer(
    project_id,
    prediction_id,
    predictions_metadata_by_id_url,
    predictions_metadata_with_shap_exp,
    predictions_url,
    predictions_regression_with_shap_explanations,
):
    add_response(predictions_metadata_by_id_url, predictions_metadata_with_shap_exp)
    add_response(predictions_url, predictions_regression_with_shap_explanations)

    predictions = Predictions.get(project_id, prediction_id)
    data_frame = predictions.get_all_as_dataframe(serializer="json")
    assert isinstance(data_frame, pd.DataFrame)
    assert data_frame.shape == (2, 13)
    assert "row_id" in data_frame.columns
    assert "prediction" in data_frame.columns
    assert "shap_remaining_total" in data_frame.columns
    assert "shap_base_value" in data_frame.columns
    explanation_columns = [column for column in data_frame.columns if "Explanation_" in column]
    assert len(explanation_columns) == 9
    feature_name_columns = [column for column in explanation_columns if "feature_name" in column]
    assert len(feature_name_columns) == 3
    feature_value_columns = [column for column in explanation_columns if "feature_value" in column]
    assert len(feature_value_columns) == 3
    strength_columns = [column for column in explanation_columns if "strength" in column]
    assert len(strength_columns) == 3


@responses.activate
def test_get_all_as_dataframe_binary_json_serializer(
    project_id,
    prediction_id,
    predictions_metadata_by_id_url,
    predictions_metadata_with_shap_exp,
    predictions_url,
    predictions_binary_with_shap_explanations,
):
    add_response(predictions_metadata_by_id_url, predictions_metadata_with_shap_exp)
    add_response(predictions_url, predictions_binary_with_shap_explanations)

    predictions = Predictions.get(project_id, prediction_id)
    data_frame = predictions.get_all_as_dataframe(serializer="json")
    assert isinstance(data_frame, pd.DataFrame)
    assert data_frame.shape == (2, 18)
    assert "row_id" in data_frame.columns
    assert "prediction" in data_frame.columns
    assert "shap_remaining_total" in data_frame.columns
    assert "shap_base_value" in data_frame.columns
    assert "explained_class" in data_frame.columns
    explanation_columns = [column for column in data_frame.columns if "Explanation_" in column]
    assert len(explanation_columns) == 9
    feature_name_columns = [column for column in explanation_columns if "feature_name" in column]
    assert len(feature_name_columns) == 3
    feature_value_columns = [column for column in explanation_columns if "feature_value" in column]
    assert len(feature_value_columns) == 3
    strength_columns = [column for column in explanation_columns if "strength" in column]
    assert len(strength_columns) == 3


@responses.activate
def test_get_all_as_dataframe_multilabel_json_serializer(
    project_id,
    prediction_id,
    predictions_metadata_by_id_url,
    predictions_url,
    predictions_multilabel_json,
    sample_prediction_metadata,
):
    add_response(predictions_metadata_by_id_url, sample_prediction_metadata)
    add_response(predictions_url, predictions_multilabel_json)

    predictions = Predictions.get(project_id, prediction_id)
    actual = predictions.get_all_as_dataframe(serializer="json")

    expected = pd.DataFrame(
        [
            {
                u"row_id": 0,
                u"threshold_cat": 0.5,
                u"prediction_cat": 1,
                u"class_cat": 0.6,
                u"threshold_🐕": 0.5,
                u"prediction_🐕": 0,
                u"class_🐕": 0.5,
                u"threshold_Maine Coon": 0.5,
                u"prediction_Maine Coon": 0,
                u"class_Maine Coon": 0.4,
                u"threshold_British_Shorthair": 0.5,
                u"prediction_British_Shorthair": 1,
                u"class_British_Shorthair": 0.7,
            },
            {
                u"row_id": 1,
                u"threshold_cat": 0.5,
                u"prediction_cat": 0,
                u"class_cat": 0.1,
                u"threshold_🐕": 0.5,
                u"prediction_🐕": 0,
                u"class_🐕": 0.4,
                u"threshold_Maine Coon": 0.5,
                u"prediction_Maine Coon": 0,
                u"class_Maine Coon": 0.4,
                u"threshold_British_Shorthair": 0.5,
                u"prediction_British_Shorthair": 0,
                u"class_British_Shorthair": 0.1,
            },
        ]
    )
    types_mapping = {}
    for column in expected.columns:
        if column.startswith("prediction_"):
            types_mapping[column] = "int8"
        elif column.startswith("threshold_"):
            types_mapping[column] = "float32"
        elif column.startswith("class_"):
            types_mapping[column] = "float32"
    expected = expected.astype(types_mapping)

    pd.testing.assert_frame_equal(actual, expected[actual.columns])


@responses.activate
def test_get_all_as_dataframe_csv_serializer(
    project_id,
    prediction_id,
    predictions_url,
    predictions_metadata_by_id_url,
    predictions_metadata_with_shap_exp,
    predictions_with_shap_exp_csv,
):
    add_response(url=predictions_metadata_by_id_url, body=predictions_metadata_with_shap_exp)
    add_response(url=predictions_url, body=predictions_with_shap_exp_csv, content_type="text/csv")

    predictions = Predictions.get(project_id, prediction_id)
    data_frame = predictions.get_all_as_dataframe(serializer="csv")
    assert isinstance(data_frame, pd.DataFrame)
    assert data_frame.shape == (10, 7)
    assert "row_id" in data_frame.columns
    assert "prediction" in data_frame.columns
    assert "shap_remaining_total" in data_frame.columns
    assert "shap_base_value" in data_frame.columns
    explanation_columns = [column for column in data_frame.columns if "Explanation_1" in column]
    assert len(explanation_columns) == 3
    assert any(["feature_name" in column for column in explanation_columns])
    assert any(["feature_value" in column for column in explanation_columns])
    assert any(["strength" in column for column in explanation_columns])


@responses.activate
def test_get_not_found(project_id, prediction_id, predictions_metadata_by_id_url):
    add_response(predictions_metadata_by_id_url, "", status=404)
    with pytest.raises(errors.ClientError):
        Predictions.get(project_id, prediction_id)


@responses.activate
def test_get_as_data_frame_server_error(project_id, prediction_id, predictions_metadata_by_id_url):
    add_response(predictions_metadata_by_id_url, "", status=500)
    with pytest.raises(errors.ServerError):
        Predictions.get(project_id, prediction_id)


def test_repr():
    preds = Predictions("project_id", "prediction_id", "model_id", "dataset_id", False)

    assert (
        repr(preds) == "Predictions(prediction_id='prediction_id', project_id='project_id', "
        "model_id='model_id', dataset_id='dataset_id', "
        "includes_prediction_intervals=False, prediction_intervals_size=None, "
        "forecast_point=None, predictions_start_date=None, "
        "predictions_end_date=None, actual_value_column=None, "
        "explanation_algorithm=None, max_explanations=None, shap_warnings=None)"
    )

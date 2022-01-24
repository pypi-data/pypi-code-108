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

from mock import mock
import pytest
import responses

from datarobot import DatetimeModel
from datarobot.enums import AnomalyAssessmentStatus
from datarobot.models.anomaly_assessment import (
    AnomalyAssessmentExplanations,
    AnomalyAssessmentPredictionsPreview,
    AnomalyAssessmentRecord,
)


@pytest.fixture
def project_id():
    return "5ece5927962d741e19c2febb"


@pytest.fixture
def model_id():
    return "607d6544823fa548132dc257"


@pytest.fixture
def completed_record_id():
    return "607d657551a4bef68dd29d2f"


@pytest.fixture
def anomaly_assessment_single_record_response(unittest_endpoint):
    latest_loc = (
        "{}/projects/5ece5927962d741e19c2febb/anomalyAssessmentRecords/"
        "607d657551a4bef68dd29d2f/explanations/"
        "?endDate=2015-11-02T00%3A00%3A00.000000Z&pointsCount=2".format(unittest_endpoint)
    )
    return {
        "count": 1,
        "next": None,
        "data": [
            {
                "status": "completed",
                "seriesId": "S1F03YZM",
                "endDate": "2015-11-02T00:00:00.000000Z",
                "startDate": "2015-10-07T00:00:00.000000Z",
                "recordId": "607d657551a4bef68dd29d2f",
                "projectId": "5ece5927962d741e19c2febb",
                "backtest": "holdout",
                "source": "training",
                "latestExplanationsLocation": latest_loc,
                "deleteLocation": "{}/projects/5ece5927962d741e19c2febb/"
                "anomalyAssessmentRecords/607d657551a4bef68dd29d2f/".format(unittest_endpoint),
                "predictionThreshold": 0.001152261490359791,
                "statusDetails": "insight data is available.",
                "previewLocation": "{}/projects/5ece5927962d741e19c2febb/"
                "anomalyAssessmentRecords/607d657551a4bef68dd29d2f/predictionsPreview/".format(
                    unittest_endpoint
                ),
                "modelId": "607d6544823fa548132dc257",
            },
        ],
        "previous": None,
    }


@pytest.fixture
def anomaly_assessment_records_response(unittest_endpoint):
    return {
        "count": 2,
        "next": "{}/projects/5ece5927962d741e19c2febb/anomalyAssessmentRecords/"
        "?limit=2&offset=2".format(unittest_endpoint),
        "data": [
            {
                "status": "noData",
                "seriesId": "S1F03YZM",
                "endDate": None,
                "startDate": None,
                "recordId": "607edabbe8c1f4b282d29c20",
                "projectId": "5ece5927962d741e19c2febb",
                "backtest": 0,
                "source": "validation",
                "latestExplanationsLocation": None,
                "deleteLocation": "{}/projects/5ece5927962d741e19c2febb/anomalyAssessmentRecords/"
                "607edabbe8c1f4b282d29c20/".format(unittest_endpoint),
                "predictionThreshold": None,
                "statusDetails": "There is no data for specified parameters.",
                "previewLocation": None,
                "modelId": "607d6544823fa548132dc257",
            },
            {
                "status": "completed",
                "seriesId": "S1F0EGMT",
                "endDate": "2015-11-02T00:00:00.000000Z",
                "startDate": "2015-10-07T00:00:00.000000Z",
                "recordId": "607d657551a4bef68dd29d2f",
                "projectId": "5ece5927962d741e19c2febb",
                "backtest": 0,
                "source": "validation",
                "latestExplanationsLocation": "{}/projects/5ece5927962d741e19c2febb/"
                "anomalyAssessmentRecords/607d657551a4bef68dd29d2f/"
                "explanations/?endDate=2015-11-02T00%3A00%3A00.000000Z&pointsCount=2".format(
                    unittest_endpoint
                ),
                "deleteLocation": "{}/projects/5ece5927962d741e19c2febb/anomalyAssessmentRecords/"
                "607d657551a4bef68dd29d2f/".format(unittest_endpoint),
                "predictionThreshold": 0.001152261490359791,
                "statusDetails": "insight data is available.",
                "previewLocation": "{}/projects/5ece5927962d741e19c2febb/anomalyAssessmentRecords/"
                "607d657551a4bef68dd29d2f/predictionsPreview/".format(unittest_endpoint),
                "modelId": "607d6544823fa548132dc257",
            },
        ],
        "previous": None,
    }


@pytest.fixture
def anomaly_explanations_response():
    return {
        "count": 2,
        "shapBaseValue": 0.01,
        "endDate": "2015-11-02T00:00:00.000000Z",
        "seriesId": "S1F0EGMT",
        "startDate": "2015-11-02T00:00:00.000000Z",
        "recordId": "607d657551a4bef68dd29d2f",
        "projectId": "5ece5927962d741e19c2febb",
        "source": "validation",
        "data": [
            {
                "shapExplanation": [
                    {
                        "featureValue": "75929023.55426522",
                        "strength": 2.730025962114207e-07,
                        "feature": "attribute1 (35 day std)",
                    },
                    {
                        "featureValue": "343016.23529411765",
                        "strength": 2.5279249798097965e-07,
                        "feature": "attribute6 (35 day mean)",
                    },
                ],
                "timestamp": "2015-10-31T00:00:00.000000Z",
                "prediction": 0.001152261490359791,
            },
            {"shapExplanation": [], "timestamp": "2015-11-02T00:00:00.000000Z", "prediction": 0.4},
        ],
        "backtest": 0,
        "modelId": "607d6544823fa548132dc257",
    }


@pytest.fixture()
def anomaly_predictions_preview_response():
    return {
        "seriesId": "S1F0EGMT",
        "startDate": "2015-10-07T00:00:00.000000Z",
        "endDate": "2015-11-02T00:00:00.000000Z",
        "recordId": "607d657551a4bef68dd29d2f",
        "projectId": "5ece5927962d741e19c2febb",
        "source": "validation",
        "previewBins": [
            {
                "avgPredicted": 0.4,
                "startDate": "2015-10-07T00:00:00.000000Z",
                "frequency": 2,
                "endDate": "2015-11-03T00:00:00.000000Z",
                "maxPredicted": 0.5,
            }
        ],
        "backtest": 0,
        "modelId": "607d6544823fa548132dc257",
    }


def check_metadata(record, project_id, model_id):
    assert record.project_id == project_id
    assert record.model_id == model_id
    assert record.series_id
    assert record.record_id
    assert record.source == "validation"
    assert record.backtest == 0


@responses.activate
def test_get_anomaly_assessment_records(
    anomaly_assessment_records_response,
    anomaly_predictions_preview_response,
    anomaly_explanations_response,
    unittest_endpoint,
    project_id,
    model_id,
    completed_record_id,
):

    responses.add(
        responses.GET,
        "{}/projects/{}/anomalyAssessmentRecords/?limit=100&offset=0&modelId={}".format(
            unittest_endpoint, project_id, model_id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(anomaly_assessment_records_response),
    )
    responses.add(
        responses.GET,
        "{}/projects/{}/anomalyAssessmentRecords/{}/explanations/?"
        "endDate=2015-11-02T00%3A00%3A00.000000Z&pointsCount=2".format(
            unittest_endpoint, project_id, completed_record_id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(anomaly_explanations_response),
    )
    responses.add(
        responses.GET,
        "{}/projects/{}/anomalyAssessmentRecords/{}/explanations/?"
        "startDate=2015-10-07T00%3A00%3A00.000000Z&"
        "endDate=2015-11-03T00%3A00%3A00.000000Z".format(
            unittest_endpoint, project_id, completed_record_id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(anomaly_explanations_response),
    )
    responses.add(
        responses.GET,
        "{}/projects/{}/anomalyAssessmentRecords/{}/predictionsPreview/".format(
            unittest_endpoint, project_id, completed_record_id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(anomaly_predictions_preview_response),
    )
    responses.add(
        responses.DELETE,
        "{}/projects/{}/anomalyAssessmentRecords/{}/".format(
            unittest_endpoint, project_id, completed_record_id
        ),
        status=204,
        content_type="application/json",
    )
    model = DatetimeModel(id=model_id, project_id=project_id)
    records = model.get_anomaly_assessment_records()
    no_data_record = records[0]
    completed_record = records[1]
    assert no_data_record.series_id == "S1F03YZM"
    assert no_data_record.status == AnomalyAssessmentStatus.NO_DATA
    assert no_data_record.latest_explanations_location is None
    assert no_data_record.preview_location is None
    assert no_data_record.start_date is None
    assert no_data_record.end_date is None
    assert no_data_record.prediction_threshold is None
    assert completed_record.series_id == "S1F0EGMT"
    assert completed_record.status == AnomalyAssessmentStatus.COMPLETED
    for record in records:
        check_metadata(record, project_id, model_id)
        assert record.delete_location
    explanations = completed_record.get_latest_explanations()
    assert isinstance(explanations, AnomalyAssessmentExplanations)
    preview = completed_record.get_predictions_preview()
    assert isinstance(preview, AnomalyAssessmentPredictionsPreview)
    assert preview.series_id == "S1F0EGMT"
    check_metadata(preview, project_id, model_id)
    assert preview.preview_bins == [
        {
            "avg_predicted": 0.4,
            "max_predicted": 0.5,
            "start_date": "2015-10-07T00:00:00.000000Z",
            "end_date": "2015-11-03T00:00:00.000000Z",
            "frequency": 2,
        }
    ]
    check_metadata(explanations, project_id, model_id)
    assert explanations.shap_base_value == 0.01
    assert explanations.count == 2
    assert explanations.series_id == "S1F0EGMT"
    assert explanations.data == [
        {
            "shap_explanation": [
                {
                    "feature_value": "75929023.55426522",
                    "strength": mock.ANY,
                    "feature": "attribute1 (35 day std)",
                },
                {
                    "feature_value": "343016.23529411765",
                    "strength": mock.ANY,
                    "feature": "attribute6 (35 day mean)",
                },
            ],
            "timestamp": "2015-10-31T00:00:00.000000Z",
            "prediction": mock.ANY,
        },
        {
            "shap_explanation": [],
            "timestamp": "2015-11-02T00:00:00.000000Z",
            "prediction": mock.ANY,
        },
    ]
    regions = preview.find_anomalous_regions(max_prediction_threshold=0.5)
    assert len(regions) == 1
    explanations = completed_record.get_explanations_data_in_regions(
        regions, prediction_threshold=0.4
    )
    assert len(explanations["explanations"]) == 1
    assert explanations["shap_base_value"] == 0.01
    assert completed_record.delete() is None


@responses.activate
def test_initialize_anomaly_assessment(
    unittest_endpoint, project_id, model_id, anomaly_assessment_single_record_response
):

    backtest = "holdout"
    source = "training"
    series_id = "S1F03YZM"
    responses.add(
        responses.POST,
        "{}/projects/{}/models/{}/anomalyAssessmentInitialization/".format(
            unittest_endpoint, project_id, model_id
        ),
        status=202,
        content_type="application/json",
        body=json.dumps({"seriesId": series_id, "backtest": backtest, "source": source}),
        adding_headers={"Location": "{}/status/status-id/".format(unittest_endpoint)},
    )
    responses.add(
        responses.GET,
        "{}/status/status-id/".format(unittest_endpoint),
        status=303,
        body="",
        content_type="application/json",
        adding_headers={
            "Location": "{}/projects/{}/anomalyAssessmentRecords/?seriesId={}"
            "&backtest={}&source={}".format(
                unittest_endpoint, project_id, model_id, series_id, backtest, source
            )
        },
    )
    record_resp_url = (
        "{}/projects/{}/anomalyAssessmentRecords/"
        "?seriesId={}&backtest={}&source={}".format(
            unittest_endpoint, project_id, model_id, series_id, backtest, source
        )
    )
    responses.add(
        responses.GET,
        "{}/status/status-id/".format(unittest_endpoint),
        status=303,
        body="",
        content_type="application/json",
        adding_headers={"Location": record_resp_url},
    )
    responses.add(
        responses.GET,
        record_resp_url,
        status=200,
        content_type="application/json",
        body=json.dumps(anomaly_assessment_single_record_response),
    )
    model = DatetimeModel(id=model_id, project_id=project_id)
    new_record = model.initialize_anomaly_assessment(backtest, source, series_id=series_id)
    assert isinstance(new_record, AnomalyAssessmentRecord)
    assert new_record.backtest == backtest
    assert new_record.series_id == series_id
    assert new_record.source == source
    assert new_record.model_id == model_id
    assert new_record.project_id == project_id

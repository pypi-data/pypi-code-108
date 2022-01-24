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

from datarobot.enums import FairnessMetricsSet


@pytest.fixture
def fairness_insights_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/fairnessInsights/".format(
        project_id, model_id
    )


@pytest.fixture
def data_disparity_insights_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/dataDisparityInsights/".format(
        project_id, model_id
    )


@pytest.fixture
def cross_class_accuracy_scores_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/crossClassAccuracyScores/".format(
        project_id, model_id
    )


@pytest.fixture
def fairness_insights_job_creation_response(fairness_insights_url, job_url):
    responses.add(
        responses.POST,
        fairness_insights_url,
        body="",
        status=202,
        adding_headers={"Location": job_url},
    )


@pytest.fixture
def data_disparity_insights_job_creation_response(data_disparity_insights_url, job_url):
    responses.add(
        responses.POST,
        data_disparity_insights_url,
        body="",
        status=202,
        adding_headers={"Location": job_url},
    )


@pytest.fixture
def cross_class_accuracy_scores_job_creation_response(cross_class_accuracy_scores_url, job_url):
    responses.add(
        responses.POST,
        cross_class_accuracy_scores_url,
        body="",
        status=202,
        adding_headers={"Location": job_url},
    )


def fairness_insights_server_data(model_id, fairness_metric):
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "data": [
            {
                "modelId": "".format(model_id),
                "fairnessMetric": fairness_metric,
                "fairnessThreshold": 0.8,
                "predictionThreshold": 0.5,
                "protectedFeature": "race",
                "perClassFairness": [
                    {
                        "className": "Amer-Indian-Eskimo",
                        "value": 0.35355038390571986,
                        "absoluteValue": 0.07547169811320754,
                        "entriesCount": 53,
                        "isStatisticallySignificant": False,
                    },
                    {
                        "className": "Asian-Pac-Islander",
                        "value": 1,
                        "absoluteValue": 0.23417721518987342,
                        "entriesCount": 158,
                        "isStatisticallySignificant": False,
                    },
                    {
                        "className": "White",
                        "value": 1.0,
                        "absoluteValue": 0.21346801346801347,
                        "entriesCount": 4455,
                        "isStatisticallySignificant": True,
                    },
                ],
            },
        ],
        "totalCount": 1,
    }


@pytest.fixture
def feature():
    return "race"


@pytest.fixture
def class_name1():
    return "Amer-Indian-Eskimo"


@pytest.fixture
def class_name2():
    return "Black"


@pytest.fixture
def data_disparity_insights_server_data(feature, class_name1, class_name2):
    return {
        "count": 2,
        "next": None,
        "previous": None,
        "totalCount": 2,
        "data": {
            "protectedFeature": feature,
            "metric": "psi",
            "values": [{"label": class_name1, "count": 53}, {"label": class_name2, "count": 511}],
            "features": [
                {
                    "name": "salary",
                    "disparityScore": 0.019521590824952226,
                    "featureImpact": 1,
                    "status": "Healthy",
                    "detailsHistogram": [
                        {
                            "bin": ">50K",
                            "bars": [
                                {"label": class_name1, "value": 0.09433962264150944},
                                {"label": class_name2, "value": 0.13894324853228962},
                            ],
                        },
                    ],
                },
                {
                    "name": "capital_gain",
                    "disparityScore": 0.03430540040461845,
                    "featureImpact": 1.0,
                    "status": "Healthy",
                    "detailsHistogram": [
                        {
                            "bin": "[0.0, 9999.9)",
                            "bars": [
                                {"label": class_name1, "value": 0.9811320754716981},
                                {"label": class_name2, "value": 0.9804305283757339},
                            ],
                        },
                        {
                            "bin": "[9999.9, 19999.8)",
                            "bars": [
                                {"label": class_name1, "value": 0.018867924528301886},
                                {"label": class_name2, "value": 0.009784735812133072},
                            ],
                        },
                    ],
                },
            ],
        },
    }


@pytest.fixture
def cross_class_accuracy_scores_server_data(model_id, feature, class_name1, class_name2):
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "data": [
            {
                "feature": feature,
                "modelId": model_id,
                "predictionThreshold": 0.5,
                "perClassAccuracyScores": [
                    {
                        "className": class_name1,
                        "metrics": [
                            {"metric": "LogLoss", "value": 0.15817195767047793},
                            {"metric": "f1", "value": 0.7175572519083969},
                            {"metric": "AUC", "value": 0.9645006402048656},
                            {"metric": "accuracy", "value": 0.9275929549902152},
                        ],
                    },
                    {
                        "className": class_name2,
                        "metrics": [
                            {"metric": "LogLoss", "value": 0.10583976310412195},
                            {"metric": "f1", "value": 0.8888888888888888},
                            {"metric": "AUC", "value": 1.0},
                            {"metric": "accuracy", "value": 0.9811320754716981},
                        ],
                    },
                ],
            },
        ],
        "totalCount": 1,
    }


@pytest.fixture
def fairness_insights_response_equal_parity(fairness_insights_url, model_id):
    body = json.dumps(fairness_insights_server_data(model_id, FairnessMetricsSet.EQUAL_PARITY))
    responses.add(
        responses.GET,
        "{}?offset=0&limit=100&fairnessMetricsSet={}".format(
            fairness_insights_url, FairnessMetricsSet.EQUAL_PARITY
        ),
        status=200,
        content_type="application/json",
        body=body,
    )


@pytest.fixture
def data_disparity_insights_response(
    data_disparity_insights_url,
    data_disparity_insights_server_data,
    feature,
    class_name1,
    class_name2,
):
    body = json.dumps(data_disparity_insights_server_data)
    responses.add(
        responses.GET,
        "{}?feature={}&className1={}&className2={}".format(
            data_disparity_insights_url, feature, class_name1, class_name2
        ),
        status=200,
        content_type="application/json",
        body=body,
    )


@pytest.fixture
def cross_class_accuracy_scores_response(
    cross_class_accuracy_scores_url, cross_class_accuracy_scores_server_data,
):
    body = json.dumps(cross_class_accuracy_scores_server_data)
    responses.add(
        responses.GET,
        cross_class_accuracy_scores_url,
        status=200,
        content_type="application/json",
        body=body,
    )


@responses.activate
@pytest.mark.usefixtures(
    "fairness_insights_job_creation_response", "fairness_insights_response_equal_parity",
)
def test_request_fairness_insights(one_model, job_id):
    assert one_model.request_fairness_insights() == job_id

    fairness_metrics_set = FairnessMetricsSet.EQUAL_PARITY
    assert one_model.request_fairness_insights(fairness_metrics_set) == job_id

    fairness_insights = one_model.get_fairness_insights(fairness_metrics_set=fairness_metrics_set)
    assert fairness_insights["data"][0]["fairnessMetric"] == fairness_metrics_set


@responses.activate
@pytest.mark.usefixtures(
    "data_disparity_insights_job_creation_response",
    "data_disparity_insights_response",
    "data_disparity_insights_server_data",
)
def test_request_data_disparity_insights(one_model, job_id, feature, class_name1, class_name2):
    assert (
        one_model.request_data_disparity_insights(
            feature=feature, compared_class_names=[class_name1, class_name2]
        )
        == job_id
    )

    data_disparity_insights = one_model.get_data_disparity_insights(
        feature, class_name1, class_name2
    )
    assert data_disparity_insights["data"]["protectedFeature"] == feature


@responses.activate
@pytest.mark.usefixtures(
    "cross_class_accuracy_scores_job_creation_response",
    "cross_class_accuracy_scores_response",
    "cross_class_accuracy_scores_server_data",
)
def test_cross_class_accuracy_scores(one_model, job_id, feature):
    assert one_model.request_cross_class_accuracy_scores() == job_id

    data_disparity_insights = one_model.get_cross_class_accuracy_scores()
    assert data_disparity_insights["data"][0]["feature"] == feature

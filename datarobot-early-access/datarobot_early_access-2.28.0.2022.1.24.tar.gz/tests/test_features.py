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

import mock
import pandas as pd
import pytest
import responses
from six.moves.urllib_parse import parse_qs, urlparse
from trafaret import DataError

from datarobot import Feature, FeatureHistogram, ModelingFeature, Project
from datarobot.errors import InvalidUsageError
from datarobot.models.feature import (
    DatasetFeature,
    DatasetFeatureHistogram,
    FeatureLineage,
    InteractionFeature,
    MulticategoricalHistogram,
)
from datarobot.utils import camelize


@pytest.fixture
def list_features_json():
    return """
    [{
        "id": 34,
        "name": "Claim_Amount",
        "featureType": "Numeric",
        "importance": 1,
        "lowInformation": false,
        "uniqueCount": 200,
        "naCount": 0,
        "dateFormat": null,
        "projectId": "556cdfbb100d2b0e88585195",
        "min": 1,
        "max": 1,
        "mean": 1,
        "median": 1,
        "stdDev": 0,
        "timeSeriesEligible": false,
        "timeSeriesEligibilityReason": "notADate",
        "timeStep": null,
        "timeUnit": null,
        "targetLeakage": "SKIPPED_DETECTION"
    }]
    """


@pytest.fixture
def feature_json():
    return """
    {
        "id": 34,
        "name": "Claim_Amount",
        "featureType": "Numeric",
        "importance": 1,
        "lowInformation": false,
        "uniqueCount": 200,
        "naCount": 0,
        "dateFormat": null,
        "projectId": "556cdfbb100d2b0e88585195",
        "min": 1,
        "max": 1,
        "mean": 1,
        "median": 1,
        "stdDev": 0,
        "timeSeriesEligible": false,
        "timeSeriesEligibilityReason": "notADate",
        "timeStep": null,
        "timeUnit": null,
        "feature_lineage_id": null,
        "targetLeakage": "SKIPPED_DETECTION"
    }
    """


@pytest.fixture
def feature_json_no_leakage():
    return """
    {
        "id": 34,
        "name": "Claim_Amount",
        "featureType": "Numeric",
        "importance": 1,
        "lowInformation": false,
        "uniqueCount": 200,
        "naCount": 0,
        "dateFormat": null,
        "projectId": "56cdd3baccf94e69733ff20f",
        "min": 1,
        "max": 1,
        "mean": 1,
        "median": 1,
        "stdDev": 0,
        "timeSeriesEligible": false,
        "timeSeriesEligibilityReason": "notADate",
        "timeStep": null,
        "timeUnit": null,
        "targetLeakage": "FALSE"
    }
    """


@pytest.fixture
def feature_json_leakage():
    return """
    {
        "id": 34,
        "name": "Claim_Amount",
        "featureType": "Numeric",
        "importance": 1,
        "lowInformation": true,
        "uniqueCount": 200,
        "naCount": 0,
        "dateFormat": null,
        "projectId": "56cdd3baccf94e69733ff20f",
        "min": 1,
        "max": 1,
        "mean": 1,
        "median": 1,
        "stdDev": 0,
        "timeSeriesEligible": false,
        "timeSeriesEligibilityReason": "notADate",
        "timeStep": null,
        "timeUnit": null,
        "targetLeakage": "HIGH_RISK"
    }
    """


@pytest.fixture
def feature_json_invalid_leakage():
    return """
    {
        "id": 34,
        "name": "Claim_Amount",
        "featureType": "Numeric",
        "importance": 1,
        "lowInformation": true,
        "uniqueCount": 200,
        "naCount": 0,
        "dateFormat": null,
        "projectId": "56cdd3baccf94e69733ff20f",
        "min": 1,
        "max": 1,
        "mean": 1,
        "median": 1,
        "stdDev": 0,
        "timeSeriesEligible": false,
        "timeSeriesEligibilityReason": "notADate",
        "timeStep": null,
        "timeUnit": null,
        "targetLeakage": 4
    }
    """


@pytest.fixture
def modeling_feature_server_data(project_id):
    return {
        "featureType": "Numeric",
        "lowInformation": False,
        "uniqueCount": 252,
        "name": "a_feat",
        "min": 0.052,
        "importance": 0.0039430549403626225,
        "max": 0.15,
        "dateFormat": None,
        "median": 0.091,
        "stdDev": 0.014,
        "projectId": project_id,
        "naCount": 0,
        "parentFeatureNames": ["original"],
        "mean": 0.092,
    }


@pytest.fixture
def summarized_categorical_feature_json():
    return """
        {
            "id": 12,
            "name": "bids_device[count]",
            "featureType": "Summarized Categorical",
            "importance": 1,
            "lowInformation": false,
            "uniqueCount": 200,
            "naCount": 0,
            "dateFormat": null,
            "projectId": "556cdfbb100d2b0e88585195",
            "min": null,
            "max": null,
            "mean": null,
            "median": null,
            "stdDev": null,
            "timeSeriesEligible": false,
            "timeSeriesEligibilityReason": "notADate",
            "timeStep": null,
            "timeUnit": null,
            "targetLeakage": "SKIPPED_DETECTION",
            "keySummary": [
            {
                "key": "phone1",
                "summary": {
                    "min": 100,
                    "max": 200,
                    "median": 0,
                    "mean": 23.4,
                    "stdDev": 0,
                    "pctRows": 44.96
                }
            },
            {
                "key": "phone2",
                "summary": {
                    "min": 0,
                    "max": 4798,
                    "median": 0,
                    "mean": 24.91,
                    "stdDev": 194.917,
                    "pctRows": 38.75
                }
            }]
        }
        """


@pytest.fixture
def summarized_categorical_feature_json_empty_keys():
    return """
        {
            "id": 12,
            "name": "bids_device[count]",
            "featureType": "Summarized Categorical",
            "importance": 1,
            "lowInformation": false,
            "uniqueCount": 200,
            "naCount": 0,
            "dateFormat": null,
            "projectId": "556cdfbb100d2b0e88585195",
            "min": null,
            "max": null,
            "mean": null,
            "median": null,
            "stdDev": null,
            "timeSeriesEligible": false,
            "timeSeriesEligibilityReason": "notADate",
            "timeStep": null,
            "timeUnit": null,
            "targetLeakage": "SKIPPED_DETECTION",
            "keySummary": [
            {
                "key": " ",
                "summary": {
                    "min": 100,
                    "max": 200,
                    "median": 0,
                    "mean": 23.4,
                    "stdDev": 0,
                    "pctRows": 44.96
                }
            },
            {
                "key": "%",
                "summary": {
                    "min": 0,
                    "max": 4798,
                    "median": 0,
                    "mean": 24.91,
                    "stdDev": 194.917,
                    "pctRows": 38.75
                }
            }]
        }
        """


def get_feature_response_multicategorical(multilabel_insights_key, project_id, feature_name):
    return {
        u"dataQualities": u"NO_ISSUES_FOUND",
        u"dateFormat": None,
        u"featureLineageId": None,
        u"featureType": u"Multicategorical",
        u"id": 10,
        u"importance": 1,
        u"keySummary": [
            {
                u"key": u"interest_low",
                u"summary": {
                    u"max": 1,
                    u"mean": 0.7375,
                    u"median": 1.0,
                    u"min": 0,
                    u"pctRows": 73.75,
                    u"stdDev": 0.44137435443704354,
                },
            },
            {
                u"key": u"price_very_high",
                u"summary": {
                    u"max": 1,
                    u"mean": 0.225,
                    u"median": 0.0,
                    u"min": 0,
                    u"pctRows": 22.5,
                    u"stdDev": 0.41889342094762905,
                },
            },
        ],
        u"lowInformation": False,
        u"max": None,
        u"mean": None,
        u"median": None,
        u"min": None,
        u"multilabelInsights": {u"multilabelInsightsKey": multilabel_insights_key},
        u"naCount": 0,
        u"name": feature_name,
        u"parentFeatureNames": [],
        u"projectId": project_id,
        u"stdDev": None,
        u"targetLeakage": u"SKIPPED_DETECTION",
        u"targetLeakageReason": u"no target leakage was detected",
        u"timeSeriesEligibilityReason": u"notADate",
        u"timeSeriesEligible": False,
        u"timeStep": None,
        u"timeUnit": None,
        u"uniqueCount": 13,
    }


@pytest.fixture
def feature_lineage_json():
    return """
        {
            "steps": [
                {
                    "dataType": "Numeric",
                    "parents": [],
                    "id": 0,
                    "stepType": "generatedColumn",
                    "name": "transactions_lower[Description] (30 days entropy)"
                },
                {
                    "isTimeAware": false,
                    "name": "Entropy",
                    "stepType": "action",
                    "groupBy": [],
                    "timeInfo": null,
                    "parents": [
                        0
                    ],
                    "arguments": {},
                    "actionType": "safer",
                    "id": 1,
                    "description": "Calculates the entropy over distribution of the categorie."
                },
                {
                    "joinInfo": {
                        "leftTable": {
                            "datasteps": [
                                4
                            ],
                            "columns": [
                                "CustomerID"
                            ]
                        },
                        "rightTable": {
                            "datasteps": [
                                5
                            ],
                            "columns": [
                                "customer_id"
                            ]
                        },
                        "joinType": "left"
                    },
                    "isTimeAware": false,
                    "id": 2,
                    "stepType": "join",
                    "parents": [
                        1
                    ]
                },
                {
                    "isTimeAware": true,
                    "name": "Value counts",
                    "stepType": "action",
                    "groupBy": [
                        "customer_id"
                    ],
                    "timeInfo": {
                        "duration": {
                            "duration": 30,
                            "timeUnit": "DAY"
                        },
                        "latest": {
                            "duration": 0,
                            "timeUnit": "DAY"
                        }
                    },
                    "parents": [
                        2
                    ],
                    "arguments": {
                        "fdwMeta": {
                            "duration": 30,
                            "timeUnit": "DAY"
                        },
                        "enableHashing": false
                    },
                    "actionType": "safer",
                    "id": 3,
                    "description": \
"Counts values of a given type within the feature derivation window.\\n\
    The whole dataset is in use when time aware modeling is disabled."
                },
                {
                    "name": "Primary dataset",
                    "catalogVersionId": null,
                    "stepType": "data",
                    "catalogId": null,
                    "parents": [
                        2
                    ],
                    "id": 4,
                    "columns": [
                        {
                            "dataType": "Numeric",
                            "isInput": false,
                            "name": "date",
                            "isCutoff": true
                        },
                        {
                            "dataType": "Categorical",
                            "isInput": false,
                            "name": "CustomerID",
                            "isCutoff": false
                        }
                    ]
                },
                {
                    "name": "transactions_lower",
                    "catalogVersionId": "5dcab3fe3a35220406f281e4",
                    "stepType": "data",
                    "catalogId": "5dcab3fe3a35220406f281e3",
                    "parents": [
                        3
                    ],
                    "id": 5,
                    "columns": [
                        {
                            "dataType": "Categorical",
                            "isInput": true,
                            "name": "Description",
                            "isCutoff": false
                        },
                        {
                            "dataType": "Numeric",
                            "isInput": false,
                            "name": "Date",
                            "isCutoff": true
                        },
                        {
                            "dataType": "Categorical",
                            "isInput": false,
                            "name": "customer_id",
                            "isCutoff": false
                        }
                    ]
                }
            ]
        }
        """


@pytest.fixture
def modeling_features_list_server_data(modeling_feature_server_data):
    return {"count": 1, "next": None, "previous": None, "data": [modeling_feature_server_data]}


@pytest.fixture
def modeling_features_with_next_page_server_data(modeling_feature_server_data, project_url):
    next_page_url = "{}modelingFeatures/?offset=1&limit=1".format(project_url)
    feat = dict(modeling_feature_server_data)
    feat["name"] = "first_page"
    return {"count": 1, "next": next_page_url, "previous": None, "data": [feat]}


@pytest.fixture
def modeling_features_with_previous_page_server_data(modeling_feature_server_data, project_url):
    previous_page_url = "{}modelingFeatures/?offset=0&limit=1".format(project_url)
    feat = dict(modeling_feature_server_data)
    feat["name"] = "second_page"
    return {"count": 1, "next": None, "previous": previous_page_url, "data": [feat]}


@pytest.fixture
def feature_sans_importance_json():
    return """
    {
        "id": 34,
        "name": "Claim_Amount",
        "featureType": "Numeric",
        "importance": null,
        "lowInformation": false,
        "uniqueCount": 200,
        "naCount": 0,
        "dateFormat": null,
        "projectId": "556cdfbb100d2b0e88585195",
        "min": 1,
        "max": 1,
        "mean": 1,
        "median": 1,
        "stdDev": 0,
        "timeSeriesEligible": false,
        "timeSeriesEligibilityReason": "notADate",
        "timeStep": null,
        "timeUnit": null,
        "targetLeakage": "SKIPPED_DETECTION"
    }
    """


@pytest.fixture
def claim_amount_json():
    return """
    {
        "id": 34,
        "name": "Claim Amount",
        "featureType": "Numeric",
        "importance": null,
        "lowInformation": false,
        "uniqueCount": 200,
        "naCount": 0,
        "dateFormat": null,
        "projectId": "556cdfbb100d2b0e88585195",
        "min": 1,
        "max": 1,
        "mean": 1,
        "median": 1,
        "stdDev": 0,
        "timeSeriesEligible": false,
        "timeSeriesEligibilityReason": "notADate",
        "timeStep": null,
        "timeUnit": null,
        "targetLeakage": "SKIPPED_DETECTION"
    }
    """


@pytest.fixture
def low_info_feature_json():
    """The information for a feature that has been marked as low info

    DataRobot does not finish gathering the naCount or generate a featureType
    in these situations
    """
    return """
    {
    "featureType": null,
    "lowInformation": true,
    "name": "mths_since_last_major_derog",
    "uniqueCount": 0,
    "importance": null,
    "id": 25,
    "naCount": null,
    "dateFormat": null,
    "projectId": "556cdfbb100d2b0e88585195",
    "min": null,
    "max": null,
    "mean": null,
    "median": null,
    "stdDev": null,
    "timeSeriesEligible": false,
    "timeSeriesEligibilityReason": "notADate",
    "timeStep": null,
    "timeUnit": null,
    "targetLeakage": "SKIPPED_DETECTION"
    }
    """


@pytest.fixture
def float_feature_json():
    return """
    {
        "uniqueCount": 1,
        "lowInformation": false,
        "name": "float",
        "dateFormat": null,
        "importance": 0.2648777523946366,
        "projectId": "556cdfbb100d2b0e88585195",
        "featureType": "Date",
        "id": 10,
        "naCount": 0,
        "min": 123.45,
        "max": 123.45,
        "mean": 123.45,
        "median": 123.45,
        "stdDev": 0,
        "timeSeriesEligible": false,
        "timeSeriesEligibilityReason": "notADate",
        "timeStep": null,
        "timeUnit": null,
        "targetLeakage": "SKIPPED_DETECTION"
    }
    """


@pytest.fixture
def date_feature_json():
    return """
    {
        "uniqueCount": 157,
        "lowInformation": false,
        "name": "dates",
        "dateFormat": "%Y-%m-%d %H:%M:%S",
        "importance": 0.2648777523946366,
        "projectId": "556cdfbb100d2b0e88585195",
        "featureType": "Date",
        "id": 1,
        "naCount": 0,
        "min": "2017-03-04T00:00:00",
        "max": "2017-06-15T04:40:39",
        "mean": "2017-04-24T14:20:19",
        "median": "2017-04-24T14:20:19",
        "stdDev": "30.089 days",
        "timeSeriesEligible": true,
        "timeSeriesEligibilityReason": "suitable",
        "timeStep": 3,
        "timeUnit": "MONTH",
        "targetLeakage": "SKIPPED_DETECTION"
    }
    """


@pytest.fixture
def histogram_plot_json():
    return """
    {
        "plot":
        [
            {"label": "5.0", "count": 50.5, "target": 3.01},
            {"label": "15.1", "count": 150.6, "target": 2.9529411764},
            {"label": "25.2", "count": 250.7, "target": 2.8980769230},
            {"label": "==Missing==", "count": 350.8, "target": 2.8452830188},
            {"label": "=All Other=", "count": 450.9, "target": 2.79444444446}
        ]
    }
    """


@pytest.fixture
def histogram_plot_without_target_json():
    return """
    {
        "plot":
        [
            {"label": "5.0", "count": 50, "target": null},
            {"label": "15.1", "count": 150, "target": null},
            {"label": "==Missing==", "count": 350, "target": null},
            {"label": "=All Other=", "count": 450, "target": null}
        ]
    }
    """


@pytest.fixture
def histogram_plot_for_dataset_missing_target_field():
    return """
    {
        "plot":
        [
            {"label": "5.0", "count": 50},
            {"label": "15.1", "count": 150},
            {"label": "==Missing==", "count": 350},
            {"label": "=All Other=", "count": 450}
        ]
    }
    """


@pytest.fixture
def feature_server_data(feature_json):
    return json.loads(feature_json)


def test_future_proof(feature_server_data):
    Feature.from_server_data(dict(feature_server_data, future="key"))


@responses.activate
def test_features(list_features_json):
    responses.add(
        responses.GET, "https://host_name.com/projects/p-id/features/", body=list_features_json
    )
    feature = Project("p-id").get_features()[0]
    assert isinstance(feature, Feature)
    assert feature.id == 34
    assert feature.name == "Claim_Amount"
    assert feature.feature_type == "Numeric"
    assert feature.importance == 1
    assert feature.low_information is False
    assert feature.unique_count == 200
    assert feature.na_count == 0
    assert feature.project_id == "556cdfbb100d2b0e88585195"
    assert feature.min == 1
    assert feature.max == 1
    assert feature.median == 1
    assert feature.median == 1
    assert feature.std_dev == 0
    assert feature.time_series_eligible is False
    assert feature.time_series_eligibility_reason == "notADate"
    assert feature.time_step is None
    assert feature.time_unit is None


@responses.activate
def test_feature(feature_sans_importance_json):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/features/f-id/",
        body=feature_sans_importance_json,
    )
    feature = Feature.get("p-id", "f-id")
    assert isinstance(feature, Feature)
    assert feature.id == 34
    assert feature.name == "Claim_Amount"
    assert feature.feature_type == "Numeric"
    assert feature.importance is None
    assert feature.feature_lineage_id is None
    assert feature.low_information is False
    assert feature.unique_count == 200
    assert feature.na_count == 0
    assert feature.date_format is None
    assert feature.project_id == "556cdfbb100d2b0e88585195"
    assert feature.min == 1
    assert feature.max == 1
    assert feature.median == 1
    assert feature.median == 1
    assert feature.std_dev == 0
    assert feature.target_leakage == "SKIPPED_DETECTION"


@responses.activate
def test_feature_no_leakage(feature_json_no_leakage):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/features/f-id/",
        body=feature_json_no_leakage,
    )
    feature = Feature.get("p-id", "f-id")
    assert isinstance(feature, Feature)
    assert feature.low_information is False
    assert feature.target_leakage == "FALSE"


@responses.activate
def test_feature_leakage(feature_json_leakage):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/features/f-id/",
        body=feature_json_leakage,
    )
    feature = Feature.get("p-id", "f-id")
    assert isinstance(feature, Feature)
    assert feature.low_information is True
    assert feature.target_leakage == "HIGH_RISK"


@responses.activate
def test_feature_invalid_leakage(feature_json_invalid_leakage):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/features/f-id/",
        body=feature_json_invalid_leakage,
    )
    with pytest.raises(DataError):
        Feature.get("p-id", "f-id")


@responses.activate
def test_feature_with_low_info(low_info_feature_json):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/features/f-id/",
        body=low_info_feature_json,
    )
    feature = Feature.get("p-id", "f-id")
    assert feature.na_count is None
    assert feature.feature_type is None
    assert feature.min is None
    assert feature.max is None
    assert feature.median is None
    assert feature.median is None
    assert feature.std_dev is None


@responses.activate
def test_feature_with_space(claim_amount_json):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/features/Claim%20Amount/",
        body=claim_amount_json,
    )
    feature = Feature.get("p-id", "Claim Amount")
    assert isinstance(feature, Feature)


@responses.activate
def test_float_feature(float_feature_json):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/features/float/",
        body=float_feature_json,
    )
    feature = Feature.get("p-id", "float")
    assert isinstance(feature, Feature)
    assert feature.min == 123.45
    assert feature.max == 123.45
    assert feature.mean == 123.45
    assert feature.median == 123.45
    assert feature.std_dev == 0


@responses.activate
def test_date_feature(date_feature_json):
    responses.add(
        responses.GET, "https://host_name.com/projects/p-id/features/dates/", body=date_feature_json
    )
    feature = Feature.get("p-id", "dates")
    assert isinstance(feature, Feature)
    assert feature.date_format == json.loads(date_feature_json)["dateFormat"]
    assert feature.min == "2017-03-04T00:00:00"
    assert feature.max == "2017-06-15T04:40:39"
    assert feature.mean == "2017-04-24T14:20:19"
    assert feature.median == "2017-04-24T14:20:19"
    assert feature.std_dev == "30.089 days"
    assert feature.time_series_eligible is True
    assert feature.time_series_eligibility_reason == "suitable"
    assert feature.time_step == 3
    assert feature.time_unit == "MONTH"


@responses.activate
def test_summarized_categorical_feature(summarized_categorical_feature_json):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/features/bids_device/",
        body=summarized_categorical_feature_json,
    )
    feature = Feature.get("p-id", "bids_device")
    assert isinstance(feature, Feature)
    assert feature.name == "bids_device[count]"
    assert feature.min is None
    assert feature.max is None
    assert feature.mean is None
    assert feature.median is None
    assert feature.std_dev is None
    assert feature.key_summary
    assert len(feature.key_summary) == 2
    assert feature.key_summary[0]["key"] == "phone1"
    assert len(feature.key_summary[0]["summary"]) == 6
    assert feature.key_summary[1]["key"] == "phone2"
    assert len(feature.key_summary[0]["summary"]) == 6


@responses.activate
def test_summarized_categorical_feature_empty_key(summarized_categorical_feature_json_empty_keys):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/features/bids_device/",
        body=summarized_categorical_feature_json_empty_keys,
    )
    feature = Feature.get("p-id", "bids_device")
    assert isinstance(feature, Feature)
    assert feature.name == "bids_device[count]"
    assert feature.min is None
    assert feature.max is None
    assert feature.mean is None
    assert feature.median is None
    assert feature.std_dev is None
    assert feature.key_summary
    assert len(feature.key_summary) == 2
    assert feature.key_summary[0]["key"] == " "
    assert len(feature.key_summary[0]["summary"]) == 6
    assert feature.key_summary[1]["key"] == "%"
    assert len(feature.key_summary[0]["summary"]) == 6


@responses.activate
def test_multicategorical_feature():
    multilabel_insights_key = "foo_insights_key"
    project_id = "p-id"
    feature_name = "feature_name"
    response = get_feature_response_multicategorical(
        multilabel_insights_key, project_id, feature_name
    )
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/features/bids_device/",
        body=json.dumps(response),
    )
    feature = Feature.get("p-id", "bids_device")
    assert feature.multilabel_insights_key == multilabel_insights_key


@responses.activate
def test_multicategorical_feature_no_multilabel_insights_in_response():
    multilabel_insights_key = "foo_insights_key"
    project_id = "p-id"
    feature_name = "feature_name"
    response = get_feature_response_multicategorical(
        multilabel_insights_key, project_id, feature_name
    )
    del response["multilabelInsights"]
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/features/bids_device/",
        body=json.dumps(response),
    )
    feature = Feature.get("p-id", "bids_device")
    assert feature.multilabel_insights_key is None


@responses.activate
def test_get_multiseries_properties_pre_computed(
    date_feature_json, multiseries_precomputed_properties
):
    feature = Feature.from_server_data(json.loads(date_feature_json))

    properties = feature.get_multiseries_properties(["series_id"])
    assert properties == {
        "time_series_eligible": True,
        "time_step": multiseries_precomputed_properties["timeStep"],
        "time_unit": multiseries_precomputed_properties["timeUnit"],
    }
    assert len(responses.calls) == 1


@responses.activate
def test_get_multiseries_properties_with_computation(
    date_feature_json, multiseries_postcomputed_properties
):
    feature = Feature.from_server_data(json.loads(date_feature_json))

    properties = feature.get_multiseries_properties(["series_id"])
    assert properties == {
        "time_series_eligible": True,
        "time_step": multiseries_postcomputed_properties["timeStep"],
        "time_unit": multiseries_postcomputed_properties["timeUnit"],
    }
    assert len(responses.calls) == 4


@responses.activate
@pytest.mark.usefixtures("multiseries_ineligible_properties")
def test_get_multiseries_properties_not_eligible(float_feature_json):
    feature = Feature.from_server_data(json.loads(float_feature_json))

    properties = feature.get_multiseries_properties(["series_id"])
    assert properties == {"time_series_eligible": False, "time_step": None, "time_unit": None}
    assert len(responses.calls) == 4


def test_feature_with_non_ascii_name(feature_server_data, unicode_string):
    data_copy = dict(feature_server_data)
    data_copy["name"] = unicode_string
    feature = Feature.from_server_data(data_copy)
    print(feature)  # actually part of the test - this used to fail (testing __repr__)


@pytest.mark.usefixtures("known_warning")
def test_bc_instantiate_feature_from_dict(feature_server_data):
    feature = Feature(feature_server_data)
    assert feature.id == feature_server_data["id"]
    assert feature.name == feature_server_data["name"]
    assert feature.feature_type == feature_server_data["featureType"]
    assert feature.importance == feature_server_data["importance"]
    assert feature.low_information == feature_server_data["lowInformation"]
    assert feature.unique_count == feature_server_data["uniqueCount"]
    assert feature.na_count == feature_server_data["naCount"]
    assert feature.project_id == "556cdfbb100d2b0e88585195"


def test_modeling_feature_future_proof(modeling_feature_server_data):
    future_data = dict(modeling_feature_server_data, new="new")
    ModelingFeature.from_server_data(future_data)


@responses.activate
def test_get_modeling_feature(modeling_feature_server_data, project_url, project_id):
    name = modeling_feature_server_data["name"]
    responses.add(
        responses.GET,
        "{}modelingFeatures/a_feat/".format(project_url),
        json=modeling_feature_server_data,
    )

    feature = ModelingFeature.get(project_id, name)
    assert feature.project_id == project_id
    assert feature.name == modeling_feature_server_data["name"]
    assert feature.feature_type == modeling_feature_server_data["featureType"]
    assert feature.importance == modeling_feature_server_data["importance"]
    assert feature.low_information == modeling_feature_server_data["lowInformation"]
    assert feature.unique_count == modeling_feature_server_data["uniqueCount"]
    assert feature.na_count == modeling_feature_server_data["naCount"]
    assert feature.date_format == modeling_feature_server_data["dateFormat"]
    assert feature.min == modeling_feature_server_data["min"]
    assert feature.max == modeling_feature_server_data["max"]
    assert feature.mean == modeling_feature_server_data["mean"]
    assert feature.median == modeling_feature_server_data["median"]
    assert feature.std_dev == modeling_feature_server_data["stdDev"]
    assert feature.parent_feature_names == modeling_feature_server_data["parentFeatureNames"]


@responses.activate
def test_list_modeling_features(modeling_features_list_server_data, project_url, project):
    responses.add(
        responses.GET,
        "{}modelingFeatures/".format(project_url),
        json=modeling_features_list_server_data,
    )
    feats = project.get_modeling_features()

    assert len(feats) == len(modeling_features_list_server_data["data"])
    assert isinstance(feats[0], ModelingFeature)
    assert feats[0].name == modeling_features_list_server_data["data"][0]["name"]


@responses.activate
def test_list_modeling_features_paginated(
    modeling_features_with_next_page_server_data,
    modeling_features_with_previous_page_server_data,
    project,
    project_url,
):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}modelingFeatures/".format(project_url),
            json=modeling_features_with_next_page_server_data,
        )
        rsps.add(
            responses.GET,
            "{}modelingFeatures/".format(project_url),
            json=modeling_features_with_previous_page_server_data,
        )
        feats = project.get_modeling_features(batch_size=1)

        first_page_req = rsps.calls[0].request
        second_page_req = rsps.calls[1].request
        assert {"limit": ["1"]} == parse_qs(urlparse(first_page_req.url).query)
        assert {"limit": ["1"], "offset": ["1"]} == parse_qs(urlparse(second_page_req.url).query)

    assert len(feats) == 2
    names = {"first_page", "second_page"}
    assert {feat.name for feat in feats} == names


@responses.activate
@pytest.mark.parametrize("histogram_class", [FeatureHistogram, DatasetFeatureHistogram])
def test_feature_histogram(
    histogram_class, project_url, project_id, modeling_feature_server_data, histogram_plot_json
):
    feature_name = modeling_feature_server_data["name"]
    project_url = _convert_project_url_for_dataset_histogram(histogram_class, project_url)

    responses.add(
        responses.GET,
        "{}featureHistograms/{}/".format(project_url, feature_name),
        body=histogram_plot_json,
    )

    histogram = histogram_class.get(project_id, feature_name)

    assert len(histogram.plot) == 5
    assert histogram.plot[0]["label"] == "5.0"
    assert histogram.plot[0]["count"] == 50.5
    assert histogram.plot[0]["target"] == 3.01


@responses.activate
def test_dataset_feature_histogram_with_missing_target_field(
    project_url, project_id, histogram_plot_for_dataset_missing_target_field
):
    feature_name = "joe"
    dataset_url = project_url.replace("projects", "datasets")
    responses.add(
        responses.GET,
        "{}featureHistograms/{}/".format(dataset_url, feature_name),
        body=histogram_plot_for_dataset_missing_target_field,
    )

    histogram = DatasetFeatureHistogram.get(project_id, feature_name)

    assert len(histogram.plot) == 4
    assert histogram.plot[0]["label"] == "5.0"
    assert histogram.plot[0]["count"] == 50
    assert histogram.plot[0]["target"] is None


@responses.activate
@pytest.mark.parametrize("histogram_class", [FeatureHistogram, DatasetFeatureHistogram])
def test_feature_histogram_without_target(
    histogram_class,
    project_url,
    project_id,
    modeling_feature_server_data,
    histogram_plot_without_target_json,
):
    feature_name = modeling_feature_server_data["name"]
    project_url = _convert_project_url_for_dataset_histogram(histogram_class, project_url)
    responses.add(
        responses.GET,
        "{}featureHistograms/{}/".format(project_url, feature_name),
        body=histogram_plot_without_target_json,
    )

    histogram = histogram_class.get(project_id, feature_name)

    assert len(histogram.plot) == 4
    assert histogram.plot[0]["label"] == "5.0"
    assert histogram.plot[0]["count"] == 50
    assert histogram.plot[0]["target"] is None


@responses.activate
@pytest.mark.parametrize("histogram_class", [FeatureHistogram, DatasetFeatureHistogram])
def test_feature_histogram_with_bin_limit(
    histogram_class, project_url, project_id, modeling_feature_server_data, histogram_plot_json
):
    bin_limit = 5
    feature_name = modeling_feature_server_data["name"]
    project_url = _convert_project_url_for_dataset_histogram(histogram_class, project_url)
    responses.add(
        responses.GET,
        "{}featureHistograms/{}/?binLimit={}".format(project_url, feature_name, bin_limit),
        body=histogram_plot_json,
    )

    histogram = histogram_class.get(project_id, feature_name, bin_limit)

    assert len(histogram.plot) == 5
    assert histogram.plot[0]["label"] == "5.0"
    assert histogram.plot[0]["count"] == 50.5
    assert histogram.plot[0]["target"] == 3.01


@responses.activate
@pytest.mark.parametrize("histogram_class", [FeatureHistogram, DatasetFeatureHistogram])
def test_feature_histogram_using_summarized_categorical_key(
    histogram_class, project_url, project_id, histogram_plot_json
):
    key_name = "sc_key1"
    feature_name = "bids_device"
    project_url = _convert_project_url_for_dataset_histogram(histogram_class, project_url)
    responses.add(
        responses.GET,
        "{}featureHistograms/{}/?key={}".format(project_url, feature_name, key_name),
        body=histogram_plot_json,
    )

    histogram = histogram_class.get(project_id, feature_name=feature_name, key_name=key_name)

    assert len(histogram.plot) == 5
    assert histogram.plot[0]["label"] == "5.0"
    assert histogram.plot[0]["count"] == 50.5
    assert histogram.plot[0]["target"] == 3.01


def _convert_project_url_for_dataset_histogram(feature_class, project_url):
    if issubclass(feature_class, DatasetFeatureHistogram):
        project_url = project_url.replace("projects", "datasets")
    return project_url


@responses.activate
def test_feature_histogram_from_feature(
    project_url, project_id, list_features_json, histogram_plot_json
):
    responses.add(
        responses.GET, "https://host_name.com/projects/p-id/features/", body=list_features_json
    )
    feature = Project("p-id").get_features()[0]

    bin_limit = 3
    responses.add(
        responses.GET,
        "{}featureHistograms/{}/?binLimit={}".format(project_url, feature.name, bin_limit),
        body=histogram_plot_json,
    )

    actualPlot = feature.get_histogram(bin_limit).plot
    expectedPlot = FeatureHistogram.get(project_id, feature.name, bin_limit).plot
    assert actualPlot == expectedPlot


@responses.activate
def test_feature_histogram_from_modeling_feature(
    project_url, project_id, modeling_feature_server_data, histogram_plot_json
):
    name = modeling_feature_server_data["name"]
    responses.add(
        responses.GET,
        "{}modelingFeatures/{}/".format(project_url, name),
        json=modeling_feature_server_data,
    )
    feature = ModelingFeature.get(project_id, name)

    bin_limit = 3
    responses.add(
        responses.GET,
        "{}featureHistograms/{}/?binLimit={}".format(project_url, feature.name, bin_limit),
        body=histogram_plot_json,
    )

    actualPlot = feature.get_histogram(bin_limit).plot
    expectedPlot = FeatureHistogram.get(project_id, feature.name, bin_limit).plot
    assert actualPlot == expectedPlot


def assert_dataset_feature(feature_obj, feature_json):
    # type: (DatasetFeature, dict) -> None
    keys = [
        "id",
        "dataset_id",
        "dataset_version_id",
        "name",
        "feature_type",
        "low_information",
        "unique_count",
        "na_count",
        "date_format",
        "min",
        "max",
        "mean",
        "median",
        "std_dev",
        "time_series_eligible",
        "time_series_eligibility_reason",
        "time_step",
        "time_unit",
        "target_leakage",
        "target_leakage_reason",
    ]
    assert isinstance(feature_obj, DatasetFeature)
    for key in keys:
        assert getattr(feature_obj, key) == feature_json.get(camelize(key))


@responses.activate
def test_get_interaction_feature(interaction_feature_server_data, project_url, project_id):

    responses.add(
        responses.GET,
        "{}interactionFeatures/int0/".format(project_url),
        json=interaction_feature_server_data,
    )

    feature = InteractionFeature.get(project_id, "int0")
    assert feature.rows == interaction_feature_server_data["rows"]
    assert feature.bars == interaction_feature_server_data["bars"]
    assert feature.bubbles == interaction_feature_server_data["bubbles"]
    assert set(feature.source_columns) == set(interaction_feature_server_data["source_columns"])


@responses.activate
def test_get_feature_lineage(project_id, project_url, feature_lineage_json):
    feature_lineage_id = "5f05b824949de873c7300a4c"

    responses.add(
        responses.GET,
        "{}featureLineages/{}/".format(project_url, feature_lineage_id),
        body=feature_lineage_json,
    )

    feature_lineage = FeatureLineage.get(project_id, feature_lineage_id)
    assert len(feature_lineage.steps) == 6

    assert [x["step_type"] for x in feature_lineage.steps] == [
        "generatedColumn",
        "action",
        "join",
        "action",
        "data",
        "data",
    ]
    assert [x["parents"] for x in feature_lineage.steps] == [[], [0], [1], [2], [2], [3]]
    assert feature_lineage.steps[3]["is_time_aware"]
    assert feature_lineage.steps[3]["time_info"] == {
        "duration": {"duration": 30, "time_unit": "DAY"},
        "latest": {"duration": 0, "time_unit": "DAY"},
    }
    assert "arguments" not in feature_lineage.steps[3]
    assert "classname" not in feature_lineage.steps[3]
    assert "action_type" not in feature_lineage.steps[3]
    assert "actionType" not in feature_lineage.steps[3]


class TestDatasetFeature(object):
    @staticmethod
    def convert_to_dataset_feature(feature_json):
        dataset_id = str(uuid4())
        version_id = str(uuid4())
        feature_json["datasetId"] = dataset_id
        feature_json["datasetVersionId"] = version_id
        feature_json["targetLeakageReason"] = "ummmm. Do not question target leakage!"
        return feature_json

    def test_instantiation(
        self,
        feature_json,
        feature_json_leakage,
        feature_json_no_leakage,
        feature_sans_importance_json,
        date_feature_json,
        low_info_feature_json,
        claim_amount_json,
        float_feature_json,
        summarized_categorical_feature_json,
        summarized_categorical_feature_json_empty_keys,
    ):

        for feature_string in [
            feature_json,
            feature_json_leakage,
            feature_json_no_leakage,
            feature_sans_importance_json,
            date_feature_json,
            low_info_feature_json,
            claim_amount_json,
            float_feature_json,
            summarized_categorical_feature_json,
            summarized_categorical_feature_json_empty_keys,
        ]:
            feature_json = json.loads(feature_string)
            new_json = self.convert_to_dataset_feature(feature_json)
            new_obj = DatasetFeature.from_server_data(new_json)
            assert_dataset_feature(new_obj, new_json)

    @responses.activate
    def test_get_histogram(self, feature_json, unittest_endpoint, histogram_plot_json):
        dataset_feature_json = self.convert_to_dataset_feature(json.loads(feature_json))
        feature = DatasetFeature.from_server_data(dataset_feature_json)

        url = "{}/datasets/{}/featureHistograms/{}/".format(
            unittest_endpoint, feature.dataset_id, feature.name
        )
        responses.add(responses.GET, url, body=histogram_plot_json)

        result = feature.get_histogram()
        assert result.plot == json.loads(histogram_plot_json)["plot"]

        request = responses.calls[0].request
        url_tail = "{}/featureHistograms/{}/".format(feature.dataset_id, feature.name)
        assert request.url.endswith(url_tail)

    @responses.activate
    def test_get_histogram_with_bin(self, feature_json, unittest_endpoint, histogram_plot_json):
        dataset_feature_json = self.convert_to_dataset_feature(json.loads(feature_json))
        feature = DatasetFeature.from_server_data(dataset_feature_json)

        url = "{}/datasets/{}/featureHistograms/{}/?binLimit=5".format(
            unittest_endpoint, feature.dataset_id, feature.name
        )
        responses.add(responses.GET, url, body=histogram_plot_json)

        result = feature.get_histogram(bin_limit=5)
        assert result.plot == json.loads(histogram_plot_json)["plot"]

        request = responses.calls[0].request
        url_tail = "{}/featureHistograms/{}/?binLimit=5".format(feature.dataset_id, feature.name)
        assert request.url.endswith(url_tail)


class TestMulticategoricalSpecificMethods(object):
    @pytest.fixture
    def multilabel_insights_key(self):
        return "edca06201e9ba259981661145de283fd"

    @pytest.fixture
    def project_id(self):
        return "601bddf788dfc14dddd926d0"

    @pytest.fixture
    def feature_name(self):
        return "target"

    @pytest.fixture
    def feature_response_multicategorical(self, multilabel_insights_key, project_id, feature_name):
        return get_feature_response_multicategorical(
            multilabel_insights_key, project_id, feature_name
        )

    @pytest.fixture
    def multilabel_insights_histogram_response(self, project_id, feature_name):
        response = {
            u"featureName": feature_name,
            u"histogram": [
                {
                    u"label": u"interest_low",
                    u"plot": [
                        {u"labelRelevance": 0, u"rowCount": 42, u"rowPct": 26.25},
                        {u"labelRelevance": 1, u"rowCount": 118, u"rowPct": 73.75},
                    ],
                },
                {
                    u"label": u"price_very_high",
                    u"plot": [
                        {u"labelRelevance": 0, u"rowCount": 124, u"rowPct": 77.5},
                        {u"labelRelevance": 1, u"rowCount": 36, u"rowPct": 22.5},
                    ],
                },
            ],
            u"projectId": project_id,
        }
        return response

    @pytest.fixture
    def expected_histogram_values(self):
        return [
            {
                u"label": u"interest_low",
                u"plot": [
                    {u"label_relevance": 0, u"row_count": 42, u"row_pct": 26.25},
                    {u"label_relevance": 1, u"row_count": 118, u"row_pct": 73.75},
                ],
            },
            {
                u"label": u"price_very_high",
                u"plot": [
                    {u"label_relevance": 0, u"row_count": 124, u"row_pct": 77.5},
                    {u"label_relevance": 1, u"row_count": 36, u"row_pct": 22.5},
                ],
            },
        ]

    @responses.activate
    def test_multicategorical_histogram_get(
        self,
        multilabel_insights_key,
        multilabel_insights_histogram_response,
        project_id,
        feature_name,
        expected_histogram_values,
    ):
        responses.add(
            responses.GET,
            "https://host_name.com/multilabelInsights/{multilabel_insights_key}/histogram/".format(
                multilabel_insights_key=multilabel_insights_key
            ),
            body=json.dumps(multilabel_insights_histogram_response),
        )
        histogram = MulticategoricalHistogram.get(multilabel_insights_key)

        self._assert_histogram(histogram, feature_name, expected_histogram_values)

    def _assert_histogram(self, histogram, feature_name, expected_histogram_values):
        assert histogram.values == expected_histogram_values
        assert histogram.feature_name == feature_name

    def test_multicategorical_histogram_to_dataframe(self, expected_histogram_values, feature_name):
        multicategorical_histogram = MulticategoricalHistogram(
            feature_name=feature_name, histogram=expected_histogram_values
        )
        actual = multicategorical_histogram.to_dataframe()

        expected = pd.DataFrame(
            [
                {
                    "feature_name": feature_name,
                    "label": "interest_low",
                    "label_relevance": 0,
                    "row_count": 42,
                    "row_pct": 26.25,
                },
                {
                    "feature_name": feature_name,
                    "label": "interest_low",
                    "label_relevance": 1,
                    "row_count": 118,
                    "row_pct": 73.75,
                },
                {
                    "feature_name": feature_name,
                    "label": "price_very_high",
                    "label_relevance": 0,
                    "row_count": 124,
                    "row_pct": 77.5,
                },
                {
                    "feature_name": feature_name,
                    "label": "price_very_high",
                    "label_relevance": 1,
                    "row_count": 36,
                    "row_pct": 22.5,
                },
            ]
        )

        pd.testing.assert_frame_equal(actual, expected)

    def test_feature_get_multicategorical_histogram_not_a_multicategorical_feature(self):
        feature = Feature(id=1324, feature_type="Regression")
        error_message = (
            "Multicategorical Histograms are only available for features"
            "with feature_type Multicategorical. "
            "This feature is of type: Regression"
        )
        with pytest.raises(InvalidUsageError, match=error_message):
            feature.get_multicategorical_histogram()

    def test_feature_get_multicategorical_histogram_multicategorical_feature_but_no_insights_key(
        self,
    ):
        feature = Feature(id=1324, feature_type="Multicategorical", multilabel_insights=None)
        error_message = "A valid multilabel_insights_key is required, but not present"
        with pytest.raises(ValueError, match=error_message):
            feature.get_multicategorical_histogram()

    @responses.activate
    def test_feature_get_multicategorical_histogram_via_feature(
        self,
        feature_response_multicategorical,
        multilabel_insights_key,
        multilabel_insights_histogram_response,
        expected_histogram_values,
        project_id,
        feature_name,
    ):
        responses.add(
            responses.GET,
            "https://host_name.com/projects/{}/features/{}/".format(project_id, feature_name),
            json=feature_response_multicategorical,
        )
        responses.add(
            responses.GET,
            "https://host_name.com/multilabelInsights/{multilabel_insights_key}/histogram/".format(
                multilabel_insights_key=multilabel_insights_key
            ),
            json=multilabel_insights_histogram_response,
        )
        feature = Feature.get(project_id, feature_name)
        histogram = feature.get_multicategorical_histogram()

        self._assert_histogram(histogram, feature_name, expected_histogram_values)

    @responses.activate
    @pytest.mark.parametrize(
        ["getter_method", "patch_target"],
        [
            pytest.param(
                "get_pairwise_correlations", "datarobot.models.feature.PairwiseCorrelations"
            ),
            pytest.param(
                "get_pairwise_joint_probabilities",
                "datarobot.models.feature.PairwiseJointProbabilities",
            ),
            pytest.param(
                "get_pairwise_conditional_probabilities",
                "datarobot.models.feature.PairwiseConditionalProbabilities",
            ),
        ],
    )
    def test_get_pairwise_statistics_getter(
        self,
        getter_method,
        patch_target,
        feature_response_multicategorical,
        project_id,
        feature_name,
    ):
        responses.add(
            responses.GET,
            "https://host_name.com/projects/{}/features/{}/".format(project_id, feature_name),
            json=feature_response_multicategorical,
        )
        feature = Feature.get(project_id, feature_name)
        with mock.patch(patch_target, autospec=True) as p:
            returned = feature.__getattribute__(getter_method)()
        assert returned == p.get.return_value
        p.get.assert_called_once_with(feature.multilabel_insights_key)

    @pytest.mark.parametrize(
        "getter_method",
        [
            "get_pairwise_correlations",
            "get_pairwise_joint_probabilities",
            "get_pairwise_conditional_probabilities",
        ],
    )
    def test_pairwise_statistics_getter_multicategorical_feature_but_no_insights_key(
        self, getter_method
    ):
        feature = Feature(id=1324, feature_type="Multicategorical", multilabel_insights=None)
        error_message = "A valid multilabel_insights_key is required, but not present"
        with pytest.raises(ValueError, match=error_message):
            feature.__getattribute__(getter_method)()

    @pytest.mark.parametrize(
        ["getter_method", "expected_error_message"],
        [
            pytest.param(
                "get_pairwise_correlations",
                (
                    "Pairwise Correlation is only available for features"
                    "with feature_type Multicategorical. "
                    "This feature is of type: Regression"
                ),
                id="correlation",
            ),
            pytest.param(
                "get_pairwise_joint_probabilities",
                (
                    "Pairwise Joint Probability is only available for features"
                    "with feature_type Multicategorical. "
                    "This feature is of type: Regression"
                ),
                id="joint_probabilities",
            ),
            pytest.param(
                "get_pairwise_conditional_probabilities",
                (
                    "Pairwise Conditional Probability is only available for features"
                    "with feature_type Multicategorical. "
                    "This feature is of type: Regression"
                ),
                id="conditional_probabilities",
            ),
        ],
    )
    def test_pairwise_statistics_getter_not_a_multicategorical_feature(
        self, getter_method, expected_error_message
    ):
        feature = Feature(id=1324, feature_type="Regression")
        with pytest.raises(InvalidUsageError, match=expected_error_message):
            feature.__getattribute__(getter_method)()

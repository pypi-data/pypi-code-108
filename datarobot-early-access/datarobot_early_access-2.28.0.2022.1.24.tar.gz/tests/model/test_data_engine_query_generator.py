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

import datarobot as dr
from datarobot.models.data_engine_query_generator import (
    QueryGeneratorDataset,
    QueryGeneratorSettings,
)

_base_url = "https://host_name.com"
_create_url = "{}/dataEngineQueryGenerators/"
_get_url = "{}/dataEngineQueryGenerators/{}/"

_query_generator_id = "queryGeneratorId"
_query_generator_url = _get_url.format(_base_url, _query_generator_id)


@pytest.fixture
def query_generator_record():
    return {
        "id": "queryGeneratorId",
        "query": "queryText",
        "datasets": [
            {
                "datasetId": "datasetId",
                "datasetVersionId": "datasetVersionId",
                "alias": "datasetAlias",
            }
        ],
        "generatorType": "TimeSeries",
        "generatorSettings": {
            "target": "y",
            "datetimePartitionColumn": "date",
            "multiSeriesIdColumns": ["id"],
            "timeUnit": "DAY",
            "timeStep": 1,
            "defaultNumericAggregationMethod": "sum",
            "defaultCategoricalAggregationMethod": "mostFrequent",
            "defaultTextAggregationMethod": "concatenate",
            "startFromSeriesMinDatetime": True,
            "endToSeriesMaxDatetime": True,
        },
        "generatedQuery": "queryText",
        "inputFeatureTypes": {},
    }


@pytest.fixture
def query_generator_get_json(query_generator_record):
    return json.dumps(query_generator_record)


def test_query_generator_dataset():
    dataset = QueryGeneratorDataset(
        alias="my_dataset", dataset_id="my_dataset_id", dataset_version_id="my_dataset_version_id"
    )
    assert dataset.to_dict() == {
        "alias": "my_dataset",
        "dataset_id": "my_dataset_id",
        "dataset_version_id": "my_dataset_version_id",
    }
    assert dataset.to_payload() == {
        "alias": "my_dataset",
        "datasetId": "my_dataset_id",
        "datasetVersionId": "my_dataset_version_id",
    }


def test_query_generator_settings():
    settings = QueryGeneratorSettings(
        datetime_partition_column="date",
        time_unit="DAY",
        time_step=1,
        default_numeric_aggregation_method="sum",
        default_categorical_aggregation_method="mostFrequent",
        target="y",
        multiseries_id_columns=["id"],
        default_text_aggregation_method="concatenate",
        start_from_series_min_datetime=True,
        end_to_series_max_datetime=True,
    )
    assert settings.to_dict() == {
        "datetime_partition_column": "date",
        "time_unit": "DAY",
        "time_step": 1,
        "default_numeric_aggregation_method": "sum",
        "default_categorical_aggregation_method": "mostFrequent",
        "target": "y",
        "multiseries_id_columns": ["id"],
        "default_text_aggregation_method": "concatenate",
        "start_from_series_min_datetime": True,
        "end_to_series_max_datetime": True,
    }
    assert settings.to_payload() == {
        "datetimePartitionColumn": "date",
        "timeUnit": "DAY",
        "timeStep": 1,
        "defaultNumericAggregationMethod": "sum",
        "defaultCategoricalAggregationMethod": "mostFrequent",
        "target": "y",
        "multiseriesIdColumns": ["id"],
        "defaultTextAggregationMethod": "concatenate",
        "startFromSeriesMinDatetime": True,
        "endToSeriesMaxDatetime": True,
    }


@responses.activate
def test_query_generator_get_valid(query_generator_get_json):
    responses.add(
        responses.GET,
        _query_generator_url,
        body=query_generator_get_json,
        status=200,
        content_type="application/json",
    )
    query_generator = dr.DataEngineQueryGenerator.get(_query_generator_id)

    assert isinstance(query_generator, dr.DataEngineQueryGenerator)
    assert query_generator.id == _query_generator_id
    assert query_generator.datasets == [
        {
            "dataset_id": "datasetId",
            "dataset_version_id": "datasetVersionId",
            "alias": "datasetAlias",
        }
    ]
    assert query_generator.generator_type == "TimeSeries"
    assert query_generator.generator_settings == {
        "target": "y",
        "datetime_partition_column": "date",
        "multi_series_id_columns": ["id"],
        "time_unit": "DAY",
        "time_step": 1,
        "default_numeric_aggregation_method": "sum",
        "default_categorical_aggregation_method": "mostFrequent",
        "default_text_aggregation_method": "concatenate",
        "start_from_series_min_datetime": True,
        "end_to_series_max_datetime": True,
    }
    assert query_generator.query == "queryText"


@pytest.fixture
@responses.activate
def query_generator(query_generator_get_json):
    responses.add(
        responses.POST,
        _create_url.format(_base_url),
        body="",
        status=202,
        adding_headers={"Location": "{}/status/some-status-id/".format(_base_url)},
        content_type="application_json",
    )
    responses.add(
        responses.GET,
        "{}/status/some-status-id/".format(_base_url),
        body="",
        status=303,
        adding_headers={"Location": _query_generator_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        _query_generator_url,
        body=query_generator_get_json,
        status=200,
        content_type="application/json",
    )
    query_generator = dr.DataEngineQueryGenerator.create(
        generator_type="TimeSeries",
        datasets=[
            QueryGeneratorDataset(
                alias="datasetAlias", dataset_id="datasetId", dataset_version_id="datasetVersionId"
            )
        ],
        generator_settings=QueryGeneratorSettings(
            datetime_partition_column="date",
            time_unit="DAY",
            time_step=1,
            default_numeric_aggregation_method="sum",
            default_categorical_aggregation_method="mostFrequent",
            target="y",
            multiseries_id_columns=["id"],
            default_text_aggregation_method="concatenate",
            start_from_series_min_datetime=True,
            end_to_series_max_datetime=True,
        ),
    )
    return query_generator


def test_query_generator_create(query_generator):
    assert isinstance(query_generator, dr.DataEngineQueryGenerator)
    assert query_generator.id == _query_generator_id
    assert query_generator.datasets == [
        {
            "dataset_id": "datasetId",
            "dataset_version_id": "datasetVersionId",
            "alias": "datasetAlias",
        }
    ]
    assert query_generator.generator_type == "TimeSeries"
    assert query_generator.generator_settings == {
        "target": "y",
        "datetime_partition_column": "date",
        "multi_series_id_columns": ["id"],
        "time_unit": "DAY",
        "time_step": 1,
        "default_numeric_aggregation_method": "sum",
        "default_categorical_aggregation_method": "mostFrequent",
        "default_text_aggregation_method": "concatenate",
        "start_from_series_min_datetime": True,
        "end_to_series_max_datetime": True,
    }
    assert query_generator.query == "queryText"


@responses.activate
def test_query_generator_create_dataset(query_generator, mock_dataset):
    responses.add(
        responses.POST,
        "{}/dataEngineWorkspaceStates/fromDataEngineQueryGenerator/".format(_base_url),
        body=json.dumps({"workspaceStateId": "someWorkspaceStateId"}),
        status=201,
        content_type="application_json",
    )
    responses.add(
        responses.POST,
        "{}/datasets/fromDataEngineWorkspaceState/".format(_base_url),
        body="",
        status=202,
        adding_headers={"Location": "{}/status/some-status-id/".format(_base_url)},
        content_type="application_json",
    )
    dataset_url = "{}/datasets/{}".format(_base_url, mock_dataset["datasetId"])
    responses.add(
        responses.GET,
        "{}/status/some-status-id/".format(_base_url),
        body="",
        status=303,
        adding_headers={"Location": dataset_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        dataset_url,
        body=json.dumps(mock_dataset),
        status=200,
        content_type="application/json",
    )
    dataset = query_generator.create_dataset()
    assert isinstance(dataset, dr.Dataset)

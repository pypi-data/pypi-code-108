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

from datarobot import errors
from datarobot.models.secondary_dataset import SecondaryDataset, SecondaryDatasetConfigurations
from tests.utils import request_body_to_json


@pytest.fixture
def ids():
    return {
        "pid": "5a530498d5c1f302d6d17699",
        "graph_id": "5a530498d5c1f302d6d17111",
        "identifier_1": "test_dataset_1",
        "catalog_version_id_1": "5a530498d5c1f302d6d17121",
        "catalog_id_1": "5a530498d5c1f302d6d17115",
        "identifier_2": "test_dataset_2",
        "catalog_version_id_2": "6a530498d5c1f302d6d17121",
        "catalog_id_2": "6a530498d5c1f302d6d17115",
    }


@pytest.fixture
def secondary_datasets(ids):
    secondary_dataset_1 = SecondaryDataset(
        identifier=ids["identifier_1"],
        catalog_version_id=ids["catalog_version_id_1"],
        catalog_id=ids["catalog_id_1"],
        snapshot_policy="specified",
    )
    secondary_dataset_2 = SecondaryDataset(
        identifier=ids["identifier_2"],
        catalog_version_id=ids["catalog_version_id_2"],
        catalog_id=ids["catalog_id_2"],
        snapshot_policy="specified",
    )
    return [secondary_dataset_1, secondary_dataset_2]


@pytest.fixture
def secondary_dataset_configurations_response(ids):
    return {
        "projectId": ids["pid"],
        "secondaryDatasets": [
            {
                "snapshotPolicy": "specified",
                "identifier": ids["identifier_1"],
                "catalogVersionId": ids["catalog_version_id_1"],
                "catalogId": ids["catalog_id_1"],
            },
            {
                "snapshotPolicy": "specified",
                "identifier": ids["identifier_2"],
                "catalogVersionId": ids["catalog_version_id_2"],
                "catalogId": ids["catalog_id_2"],
            },
        ],
        "id": "5df109112ca582033ff44084",
        "name": "Testing",
    }


@responses.activate
def test_create_secondary_dataset_configurations(
    ids, secondary_datasets, secondary_dataset_configurations_response
):
    url = "https://host_name.com/projects/{}/secondaryDatasetsConfigurations/".format(ids["pid"])
    responses.add(
        responses.POST, url, status=201, body=json.dumps(secondary_dataset_configurations_response),
    )

    datasets = [dataset.to_dict() for dataset in secondary_datasets]
    result = SecondaryDatasetConfigurations.create(
        ids["pid"], secondary_datasets=datasets, name="Testing"
    )

    assert responses.calls[0].request.method == "POST"

    # verify request payload
    payload = request_body_to_json(responses.calls[0].request)
    all_secondary_datasets = payload["secondaryDatasets"]
    assert len(all_secondary_datasets) == 2

    # verify response
    assert isinstance(result, SecondaryDatasetConfigurations)
    assert result.project_id == ids["pid"]
    assert result.name == "Testing"
    assert len(result.secondary_datasets) == 2
    dataset = result.secondary_datasets[0]
    assert dataset.catalog_id == ids["catalog_id_1"]
    assert dataset.catalog_version_id == ids["catalog_version_id_1"]
    assert dataset.snapshot_policy == "specified"


@responses.activate
def test_failure_in_create_secondary_dataset_configurations__status_error_code(
    ids, secondary_datasets
):
    url = "https://host_name.com/projects/{}/secondaryDatasetsConfigurations/".format(ids["pid"])
    responses.add(responses.POST, url, status=404, body="")

    datasets = [dataset.to_dict() for dataset in secondary_datasets]
    with pytest.raises(errors.ClientError):
        SecondaryDatasetConfigurations.create(
            ids["pid"], secondary_datasets=datasets, name="Testing"
        )


@responses.activate
def test_secondary_dataset_configurations_retrieve(secondary_dataset_configurations_response):
    config_id = secondary_dataset_configurations_response["id"]
    pid = secondary_dataset_configurations_response["projectId"]
    url = "https://host_name.com/projects/{}/secondaryDatasetsConfigurations/{}/".format(
        pid, config_id
    )
    responses.add(responses.GET, url, json=secondary_dataset_configurations_response)

    secondary_dataset_config = SecondaryDatasetConfigurations(id=config_id, project_id=pid).get()

    assert responses.calls[0].request.method == "GET"
    assert secondary_dataset_config.id == config_id
    assert secondary_dataset_config.project_id == pid

    dataset = secondary_dataset_config.secondary_datasets[0]
    assert isinstance(dataset, SecondaryDataset)
    identifier = dataset.identifier
    expected_config = secondary_dataset_configurations_response["secondaryDatasets"]
    expected_dataset = [d for d in expected_config if d["identifier"] == identifier][0]
    assert dataset.catalog_id == expected_dataset["catalogId"]
    assert dataset.catalog_version_id == expected_dataset["catalogVersionId"]
    assert dataset.snapshot_policy == expected_dataset["snapshotPolicy"]


@responses.activate
def test_secondary_dataset_configurations_deletion(secondary_dataset_configurations_response):
    config_id = secondary_dataset_configurations_response["id"]
    pid = secondary_dataset_configurations_response["projectId"]
    url = "https://host_name.com/projects/{}/secondaryDatasetsConfigurations/{}/".format(
        pid, config_id
    )
    responses.add(responses.GET, url, json=secondary_dataset_configurations_response)
    responses.add(responses.DELETE, url)
    secondary_dataset_config = SecondaryDatasetConfigurations(id=config_id, project_id=pid).get()
    secondary_dataset_config.delete()
    assert responses.calls[1].request.method == responses.DELETE
    assert responses.calls[1].request.url == url


@responses.activate
def test_secondary_dataset_configurations_list(secondary_dataset_configurations_response):
    config_id = secondary_dataset_configurations_response["id"]
    pid = secondary_dataset_configurations_response["projectId"]
    config_list = {
        "data": [
            secondary_dataset_configurations_response,
            secondary_dataset_configurations_response,
        ]
    }
    url = "https://host_name.com/projects/{}/secondaryDatasetsConfigurations/".format(pid)
    responses.add(responses.GET, url, json=config_list)

    secondary_dataset_config = SecondaryDatasetConfigurations().list(project_id=pid)

    assert responses.calls[0].request.method == "GET"
    assert len(secondary_dataset_config) == 2
    config = secondary_dataset_config[0]
    assert config.id == config_id
    assert config.project_id == pid

    dataset = config.secondary_datasets[0]
    assert isinstance(dataset, SecondaryDataset)
    identifier = dataset.identifier
    expected_config = secondary_dataset_configurations_response["secondaryDatasets"]
    expected_dataset = [d for d in expected_config if d["identifier"] == identifier][0]
    assert dataset.catalog_id == expected_dataset["catalogId"]
    assert dataset.catalog_version_id == expected_dataset["catalogVersionId"]
    assert dataset.snapshot_policy == expected_dataset["snapshotPolicy"]


@responses.activate
def test_secondary_dataset_configurations(secondary_datasets):
    result = SecondaryDatasetConfigurations(
        id="c_id", project_id="p_id", config=[], secondary_datasets=secondary_datasets
    )
    assert isinstance(result, SecondaryDatasetConfigurations)
    result_config = result.to_dict()
    assert isinstance(result_config["secondary_datasets"], list)
    assert isinstance(result_config["secondary_datasets"][0], dict)
    assert isinstance(result_config["secondary_datasets"][1], dict)

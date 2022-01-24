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
from copy import deepcopy
import json
import os
import random

import dateutil
import mock
from pandas import DataFrame
import pytest
import responses
import six

from datarobot import errors
from datarobot.enums import DEFAULT_TIMEOUT
from datarobot.models.dataset import Dataset, DatasetDetails, FeatureTypeCount, ProjectLocation
from datarobot.utils import camelize, dataframe_to_buffer
from datarobot.utils.sourcedata import list_of_records_to_buffer
from tests.project.conftest import *  # noqa: E403
from tests.test_features import assert_dataset_feature
from tests.test_helpers import fixture_file_path
from tests.utils import request_body_to_json

BASIC_CREDS = {"credentialType": "basic", "user": "user123", "password": "pass123"}
S3_CREDS = {"credentialType": "s3", "awsAccessKeyId": "key123", "awsSecretAccessKey": "secret123"}
OAUTH_CREDS = {
    "credentialType": "oauth",
    "oauthRefreshToken": "token123",
    "oauthClientId": "client123",
    "oauthClientSecret": "secret123",
}
# GCP credentials are for allow extra params.
GCP_CREDS = {"credentialType": "gcp", "type": "aaa", "privateKeyId": "123", "privateKey": "456"}


@pytest.fixture
def file_path():
    file_path = "delme.csv"
    if os.path.exists(file_path):
        os.remove(file_path)

    yield file_path

    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture()
def create_dataset_response():
    return {
        "catalogVersionId": "5e31d20d5d5f030f3ea51b25",
        "statusId": "8dab34bc-9b71-406b-ae37-85626eec2584",
        "catalogId": "5e31d20c5d5f030f3ea51b24",
    }


@pytest.fixture()
def mock_dataset_details(dataset_id):
    return {
        "datasetId": dataset_id,
        "dataEngineQueryId": None,
        "dataSourceId": None,
        "dataSourceType": "local",
        "description": None,
        "eda1ModificationDate": "2020-01-09T19:11:11.372000Z",
        "eda1ModifierFullName": "Eric Shaw",
        "error": "",
        "featureCount": 31,
        "featureCountByType": [
            {"count": 2, "featureType": "Text"},
            {"count": 1, "featureType": "Boolean"},
            {"count": 18, "featureType": "Numeric"},
            {"count": 6, "featureType": "Categorical"},
        ],
        "lastModificationDate": "2020-01-09T19:11:11.856000Z",
        "lastModifierFullName": "Eric Shaw",
        "tags": [],
        "uri": "Anomaly_credit_card.csv",
    }


@pytest.fixture()
def empty_dataset_details(dataset_id):
    return {
        "datasetId": dataset_id,
        "dataEngineQueryId": None,
        "dataSourceId": None,
        "dataSourceType": "",
        "description": "",
        "eda1ModificationDate": None,
        "eda1ModifierFullName": None,
        "error": "",
        "featureCount": None,
        "featureCountByType": [],
        "lastModificationDate": "2020-02-18T22:17:05.586000Z",
        "lastModifierFullName": "Eric Shaw",
        "tags": [],
        "uri": "N/A",
    }


@pytest.fixture()
def empty_dataset():
    return {
        "isLatestVersion": True,
        "categories": [],
        "name": "Untitled Dataset",
        "datasetId": "5e39941679dd6b1d33332b42",
        "versionId": "5e39941679dd6b1d33332b43",
        "dataPersisted": None,
        "createdBy": "Eric Shaw",
        "creationDate": "2020-02-04T15:56:06.893000Z",
        "isSnapshot": False,
        "isDataEngineEligible": True,
        "datasetSize": 0,
        "rowCount": 0,
        "processingState": "RUNNING",
        "elysianFields": "so cool",
    }


@pytest.fixture()
def mock_dataset_full_response(mock_dataset, mock_dataset_details):
    response = mock_dataset_details
    response.update(mock_dataset)
    return response


@pytest.fixture()
def empty_dataset_full_response(empty_dataset, empty_dataset_details):
    response = empty_dataset_details
    response.update(empty_dataset)
    return response


@pytest.fixture()
def mock_dataset_list():
    return {
        "count": 2,
        "totalCount": 2,
        "next": None,
        "data": [
            {
                "isLatestVersion": True,
                "name": "Anomaly_credit_card.csv",
                "datasetId": "5e177c5bf6fe7c042641f118",
                "versionId": "5e177c5cf6fe7c042641f119",
                "categories": ["TRAINING", "PREDICTION"],
                "createdBy": "Eric Shaw",
                "dataPersisted": True,
                "creationDate": "2020-01-09T19:17:48.282000Z",
                "isSnapshot": True,
                "isDataEngineEligible": True,
                "datasetSize": 10993415,
                "rowCount": 26127,
                "processingState": "COMPLETED",
                "extraneousFields": ["electrical", "gravitational"],
            },
            {
                "isLatestVersion": True,
                "name": "Anomaly_credit_card.csv",
                "datasetId": "5e177ab185047702f27ef88a",
                "versionId": "5e177ab285047702f27ef88b",
                "categories": ["TRAINING", "PREDICTION"],
                "createdBy": "Eric Shaw",
                "dataPersisted": True,
                "creationDate": "2020-01-09T19:10:42.261000Z",
                "isSnapshot": True,
                "isDataEngineEligible": True,
                "datasetSize": 3456098,
                "rowCount": 32498,
                "processingState": "SOMETHING",
            },
        ],
    }


def assert_base_dataset_fields(api_obj, dataset_json):
    assert api_obj.version_id == dataset_json["versionId"]
    assert api_obj.name == dataset_json["name"]
    assert api_obj.categories == dataset_json["categories"]
    assert api_obj.created_at == dateutil.parser.parse(dataset_json["creationDate"])
    assert api_obj.created_by == dataset_json["createdBy"]
    assert api_obj.data_persisted == dataset_json["dataPersisted"]
    assert api_obj.is_data_engine_eligible == dataset_json["isDataEngineEligible"]
    assert api_obj.is_latest_version == dataset_json["isLatestVersion"]
    assert api_obj.is_snapshot == dataset_json["isSnapshot"]
    assert api_obj.size == dataset_json["datasetSize"]
    assert api_obj.row_count == dataset_json["rowCount"]
    assert api_obj.processing_state == dataset_json["processingState"]


def assert_dataset(dataset_obj, dataset_json):
    # type: (Dataset, dict) -> None
    assert dataset_obj.id == dataset_json["datasetId"]
    assert_base_dataset_fields(dataset_obj, dataset_json)


@pytest.fixture()
def dataset_get_response(dataset_url, mock_dataset_full_response):
    add_mock_get_response(dataset_url, mock_dataset_full_response)


@pytest.fixture()
def dataset_delete_response(dataset_url, mock_dataset):
    responses.add(
        responses.DELETE, dataset_url, status=204, content_type="application/json",
    )


def add_mock_get_response(url, json_dict):
    responses.add(
        responses.GET, url, status=200, content_type="application/json", body=json.dumps(json_dict)
    )


def test_from_server_data(mock_dataset_full_response):
    dataset = Dataset.from_server_data(mock_dataset_full_response)
    assert_dataset(dataset, mock_dataset_full_response)


def test_from_server_data_with_unknown_category_still_builds(mock_dataset):
    mock_dataset["categories"].append("foo")
    dataset = Dataset.from_server_data(mock_dataset)
    assert_dataset(dataset, mock_dataset)


def test_from_server_empty_dataset(empty_dataset_full_response):
    dataset = Dataset.from_server_data(empty_dataset_full_response)
    assert_dataset(dataset, empty_dataset_full_response)


@responses.activate
@pytest.mark.usefixtures("dataset_get_response")
def test_get_dataset(mock_dataset):
    dataset = Dataset.get(mock_dataset["datasetId"])
    assert_dataset(dataset, mock_dataset)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url.endswith("/datasets/{}/".format(dataset.id))


@responses.activate
@pytest.mark.usefixtures("dataset_get_response", "dataset_delete_response")
def test_delete_dataset(mock_dataset):
    dataset = Dataset.get(mock_dataset["datasetId"])
    Dataset.delete(dataset.id)

    assert responses.calls[1].request.method == "DELETE"
    assert responses.calls[1].request.url.endswith("/datasets/{}/".format(dataset.id))


@responses.activate
def test_un_delete_dataset(dataset_url, dataset_id):
    url = "{}deleted/".format(dataset_url)
    responses.add(
        responses.PATCH, url, status=204, content_type="application/json",
    )

    Dataset.un_delete(dataset_id)
    assert responses.calls[0].request.method == "PATCH"
    assert responses.calls[0].request.url.endswith("/datasets/{}/deleted/".format(dataset_id))


@responses.activate
def test_list_dataset(unittest_endpoint, mock_dataset_list):
    url = "{}/{}/".format(unittest_endpoint, "datasets")
    add_mock_get_response(url, mock_dataset_list)

    dataset_list = Dataset.list()
    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url.endswith("/datasets/")
    for dataset_obj, json_obj in zip(dataset_list, mock_dataset_list["data"]):
        assert_dataset(dataset_obj, json_obj)


@responses.activate
def test_list_dataset_multiple_pages(unittest_endpoint, mock_dataset_list):
    second_data_list = deepcopy(mock_dataset_list)
    next_link = "http://app.datarobot.com/api/datasets/2"
    mock_dataset_list["next"] = next_link
    url = "{}/{}/".format(unittest_endpoint, "datasets")

    add_mock_get_response(url, mock_dataset_list)
    add_mock_get_response(next_link, second_data_list)

    dataset_list = Dataset.list()
    assert len(dataset_list) == 2 * len(mock_dataset_list["data"])

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url.endswith("/datasets/")
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url.endswith(next_link)
    for dataset_obj, json_obj in zip(dataset_list, mock_dataset_list["data"] * 2):
        assert_dataset(dataset_obj, json_obj)


@responses.activate
def test_list_dataset_with_params(unittest_endpoint, mock_dataset_list):
    url = "{}/{}/".format(unittest_endpoint, "datasets")
    add_mock_get_response(url, mock_dataset_list)

    Dataset.list(category="thingy")
    assert get_url(0).endswith("?category=thingy")

    Dataset.list(order_by="thingies")
    assert get_url(1).endswith("?orderBy=thingies")

    Dataset.list(filter_failed=True)
    assert get_url(2).endswith("?filterFailed=true")


@responses.activate
def test_iterate_dataset_multiple_pages(unittest_endpoint, mock_dataset_list):
    second_data_list = deepcopy(mock_dataset_list)
    next_link = "http://app.datarobot.com/api/datasets/2"
    mock_dataset_list["next"] = next_link
    url = "{}/{}/".format(unittest_endpoint, "datasets")

    add_mock_get_response(url, mock_dataset_list)
    add_mock_get_response(next_link, second_data_list)

    dataset_iterator = Dataset.iterate()

    for el in mock_dataset_list["data"]:
        from_iterator = next(dataset_iterator)
        assert_dataset(from_iterator, el)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url.endswith("/datasets/")
    assert len(responses.calls) == 1

    for el in mock_dataset_list["data"]:
        from_iterator = next(dataset_iterator)
        assert_dataset(from_iterator, el)

    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url.endswith(next_link)

    assert list(dataset_iterator) == []


@responses.activate
def test_iterate_dataset_with_params(unittest_endpoint, mock_dataset_list):
    url = "{}/{}/".format(unittest_endpoint, "datasets")
    add_mock_get_response(url, mock_dataset_list)

    next(Dataset.iterate(category="thingy"))
    assert get_url(0).endswith("datasets/?category=thingy")

    next(Dataset.iterate(order_by="thingies"))
    assert get_url(1).endswith("datasets/?orderBy=thingies")

    next(Dataset.iterate(filter_failed=True))
    assert get_url(2).endswith("datasets/?filterFailed=true")

    next(Dataset.iterate(offset=5))
    assert get_url(3).endswith("datasets/?offset=5")

    next(Dataset.iterate(limit=3))
    assert get_url(4).endswith("datasets/?limit=3")


@responses.activate
def test_update(dataset_url, mock_dataset_obj, mock_dataset_list):
    updated_json = mock_dataset_list["data"][1]

    updated_json["datasetId"] = mock_dataset_obj.id

    with pytest.raises(AssertionError):
        assert_dataset(mock_dataset_obj, updated_json)

    add_mock_get_response(dataset_url, updated_json)
    mock_dataset_obj.update()
    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url.endswith("/datasets/{}/".format(mock_dataset_obj.id))
    assert_dataset(mock_dataset_obj, updated_json)


@responses.activate
def test_modify_name(dataset_url, mock_dataset):
    dataset = Dataset.from_server_data(mock_dataset)
    new_name = "new_name"
    mock_dataset["name"] = new_name
    assert dataset.name != new_name

    responses.add(
        responses.PATCH,
        dataset_url,
        status=200,
        content_type="application/json",
        body=json.dumps(mock_dataset),
    )
    dataset.modify(name=new_name)
    request = responses.calls[0].request
    request_body = request_body_to_json(request)
    assert request_body == {"name": new_name}
    assert request.method == "PATCH"
    assert request.url.endswith("/datasets/{}/".format(dataset.id))
    assert_dataset(dataset, mock_dataset)


@responses.activate
def test_modify_categories(dataset_url, mock_dataset):
    dataset = Dataset.from_server_data(mock_dataset)
    new_categories = []
    mock_dataset["categories"] = new_categories
    assert dataset.categories != new_categories

    responses.add(
        responses.PATCH,
        dataset_url,
        status=200,
        content_type="application/json",
        body=json.dumps(mock_dataset),
    )
    dataset.modify(categories=new_categories)
    request = responses.calls[0].request
    request_body = request_body_to_json(request)
    assert request_body == {"categories": new_categories}
    assert request.method == "PATCH"
    assert request.url.endswith("/datasets/{}/".format(dataset.id))
    assert_dataset(dataset, mock_dataset)


@responses.activate
def test_modify_with_no_params_makes_no_api_call_and_does_not_change_dataset(mock_dataset_obj):
    original_name = mock_dataset_obj.name
    original_categories = mock_dataset_obj.categories

    mock_dataset_obj.modify()

    assert len(responses.calls) == 0
    assert mock_dataset_obj.name == original_name
    assert mock_dataset_obj.categories == original_categories


@responses.activate
def test_get_projects(dataset_url, mock_dataset_obj):
    url = "{}projects/".format(dataset_url)
    next_link = "https://nextpage.com"
    location_one = {"url": "https://location.com/id-1/", "id": "id-1"}
    location_two = {"url": "https://location.com/id-2/", "id": "id-2"}
    projects_response_one = {
        "count": 1,
        "totalCount": 2,
        "next": next_link,
        "data": [location_one],
        "previous": None,
    }
    projects_response_two = {
        "count": 1,
        "totalCount": 2,
        "next": None,
        "data": [location_two],
        "previous": None,
    }
    add_mock_get_response(url, projects_response_one)
    add_mock_get_response(next_link, projects_response_two)

    result = mock_dataset_obj.get_projects()
    # noinspection PyArgumentList
    expected = {ProjectLocation(**location_one), ProjectLocation(**location_two)}
    assert set(result) == expected


class TestProjectCreate(object):
    @responses.activate
    @pytest.mark.usefixtures("project_creation_responses")
    def test_create_from_dataset_use_defaults(
        self, project_collection_url, project_without_target_json, mock_dataset_obj
    ):
        project = mock_dataset_obj.create_project()

        create_body = request_body_to_json(responses.calls[0].request)
        assert create_body == {
            "datasetId": mock_dataset_obj.id,
            "datasetVersionId": mock_dataset_obj.version_id,
        }
        assert responses.calls[0].request.url == project_collection_url

        response_json = json.loads(project_without_target_json)
        assert project.id == response_json["id"]
        assert project.project_name == response_json["projectName"]
        assert project.file_name == response_json["fileName"]
        assert project.stage == response_json["stage"]

    @responses.activate
    @pytest.mark.usefixtures("project_creation_responses")
    @pytest.mark.parametrize(
        "param_name,param_value",
        [
            ("project_name", "my cool name"),
            ("user", "that guy over there"),
            ("password", "my voice is my passport"),
            ("credential_id", "12345"),
            ("credential_data", BASIC_CREDS),
            ("credential_data", S3_CREDS),
            ("credential_data", OAUTH_CREDS),
            ("credential_data", GCP_CREDS),
            ("use_kerberos", True),
        ],
    )
    def test_create_from_dataset_using_params(self, param_name, param_value, mock_dataset_obj):
        mock_dataset_obj.create_project(**{param_name: param_value})
        create_body = request_body_to_json(responses.calls[0].request)
        assert create_body == {
            "datasetId": mock_dataset_obj.id,
            "datasetVersionId": mock_dataset_obj.version_id,
            camelize(param_name): param_value,
        }


class TestDatasetDownloadFile(object):
    @pytest.fixture()
    def downloaded_file(self):
        return b"a,b,c\n1,2,3\n4,5,6\n"

    @pytest.fixture
    def file_download_response(self, dataset_url, downloaded_file):
        url = "{}file/".format(dataset_url)
        responses.add(responses.GET, url, status=200, content_type="test/csv", body=downloaded_file)

    @responses.activate
    @pytest.mark.usefixtures("file_download_response")
    def test_get_file_with_file_path(self, mock_dataset_obj, downloaded_file, file_path):
        mock_dataset_obj.get_file(file_path=file_path)

        with open(file_path, "rb") as f:
            result = f.read()

        assert result == downloaded_file

    @responses.activate
    @pytest.mark.usefixtures("file_download_response")
    def test_get_file_with_filelike(self, mock_dataset_obj, downloaded_file, file_path):
        with open(file_path, "wb") as filelike:
            mock_dataset_obj.get_file(filelike=filelike)

        with open(file_path, "rb") as f:
            result = f.read()

        assert result == downloaded_file

    def test_get_file_with_neither_filelike_nor_file_path_raises_type_error(self, mock_dataset_obj):
        with pytest.raises(TypeError):
            mock_dataset_obj.get_file()

    def test_get_file_with_both_filelike_and_file_path_raises_type_error(
        self, mock_dataset_obj, file_path
    ):
        with pytest.raises(TypeError):
            with open(file_path, "wb") as filelike:
                mock_dataset_obj.get_file(file_path=file_path, filelike=filelike)


class TestDatasetGetFeatures(object):
    @pytest.fixture
    def feature_list_response(self):
        return {
            "count": 2,
            "totalCount": 52,
            "next": None,
            "data": [
                {
                    "timeSeriesEligibilityReason": "notADate",
                    "uniqueCount": 3,
                    "lowInformation": False,
                    "datasetVersionId": "5e1779e085047702f27ef884",
                    "name": "A1Cresult",
                    "dateFormat": None,
                    "max": 1,
                    "min": 2,
                    "median": 3,
                    "targetLeakage": "SKIPPED_DETECTION",
                    "featureType": "Numerical",
                    "naCount": 8379,
                    "stdDev": 4,
                    "timeStep": None,
                    "targetLeakageReason": "no target leakage was detected",
                    "timeSeriesEligible": False,
                    "timeUnit": None,
                    "id": 21,
                    "datasetId": "5e1779df85047702f27ef883",
                    "mean": 7,
                },
                {
                    "timeSeriesEligibilityReason": "notADate",
                    "uniqueCount": 30,
                    "lowInformation": False,
                    "datasetVersionId": "5e1779e085047702f27ef884",
                    "name": "acarbose",
                    "dateFormat": None,
                    "max": None,
                    "min": None,
                    "median": None,
                    "targetLeakage": "SKIPPED_DETECTION",
                    "featureType": "Categorical",
                    "naCount": 0,
                    "stdDev": None,
                    "timeStep": None,
                    "targetLeakageReason": "no target leakage was detected",
                    "timeSeriesEligible": False,
                    "timeUnit": None,
                    "id": 33,
                    "datasetId": "5e1779df85047702f27ef883",
                    "mean": None,
                },
            ],
            "previous": None,
        }

    @responses.activate
    def test_get_all_features(self, dataset_url, feature_list_response, mock_dataset_obj):
        url = "{}allFeaturesDetails/".format(dataset_url)

        add_mock_get_response(url, feature_list_response)
        result = mock_dataset_obj.get_all_features()

        json_list = feature_list_response["data"]
        assert len(result) == len(json_list)
        for feature_obj, feature_json in zip(result, json_list):
            assert_dataset_feature(feature_obj, feature_json)

        assert responses.calls[0].request.url == url

    @responses.activate
    def test_get_all_features_handles_pagination(
        self, dataset_url, feature_list_response, mock_dataset_obj
    ):
        url = "{}allFeaturesDetails/".format(dataset_url)
        second_page = "https://the-second-page.com/"

        first_page = deepcopy(feature_list_response)
        first_page["next"] = second_page

        add_mock_get_response(url, first_page)
        add_mock_get_response(second_page, feature_list_response)
        result = mock_dataset_obj.get_all_features()

        json_list = feature_list_response["data"] * 2
        assert len(result) == len(json_list)
        for feature_obj, feature_json in zip(result, json_list):
            assert_dataset_feature(feature_obj, feature_json)

        assert responses.calls[0].request.url == url
        assert responses.calls[1].request.url == second_page

    @responses.activate
    def test_get_all_features_order_by(self, dataset_url, mock_dataset_obj, feature_list_response):
        url = "{}allFeaturesDetails/".format(dataset_url)
        add_mock_get_response(url, feature_list_response)

        mock_dataset_obj.get_all_features(order_by="joe")
        assert responses.calls[0].request.url == "{}?orderBy={}".format(url, "joe")

    @responses.activate
    def test_iterate_all_features_handles_pagination(
        self, dataset_url, feature_list_response, mock_dataset_obj
    ):
        url = "{}allFeaturesDetails/".format(dataset_url)
        second_page = "https://the-second-page.com/"

        first_page = deepcopy(feature_list_response)
        first_page["next"] = second_page

        add_mock_get_response(url, first_page)
        add_mock_get_response(second_page, feature_list_response)

        features_iterator = mock_dataset_obj.iterate_all_features()

        for el in feature_list_response["data"]:
            from_iterator = next(features_iterator)
            assert_dataset_feature(from_iterator, el)

        assert responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url.endswith("/allFeaturesDetails/")
        assert len(responses.calls) == 1

        for el in feature_list_response["data"]:
            from_iterator = next(features_iterator)
            assert_dataset_feature(from_iterator, el)

        assert responses.calls[1].request.method == "GET"
        assert responses.calls[1].request.url.endswith(second_page)

        assert list(features_iterator) == []

    @responses.activate
    def test_iterate_all_features_with_params(
        self, dataset_url, feature_list_response, mock_dataset_obj
    ):
        url = "{}allFeaturesDetails/".format(dataset_url)
        add_mock_get_response(url, feature_list_response)

        next(mock_dataset_obj.iterate_all_features(order_by="thingies"))
        assert get_url(0).endswith("allFeaturesDetails/?orderBy=thingies")

        next(mock_dataset_obj.iterate_all_features(offset=5))
        assert get_url(1).endswith("allFeaturesDetails/?offset=5")

        next(mock_dataset_obj.iterate_all_features(limit=3))
        assert get_url(2).endswith("allFeaturesDetails/?limit=3")


class TestDatasetCreation(object):
    @pytest.fixture()
    def status_location(self):
        return "https://some_location.com/"

    @pytest.fixture()
    def set_status_response(self, dataset_url, mock_dataset, status_location):
        responses.add(responses.GET, status_location, status=303, headers={"Location": dataset_url})
        add_mock_get_response(url=dataset_url, json_dict=mock_dataset)
        return dataset_url

    @staticmethod
    def add_mock_upload_response(url, status_location):
        responses.add(responses.POST, url, status=200, adding_headers={"Location": status_location})

    @pytest.fixture()
    def set_up_file_upload(
        self, unittest_endpoint, status_location, set_status_response, file_path
    ):
        with open(file_path, "wb") as f:
            f.write(b"")
        self.add_mock_upload_response(
            "{}/datasets/fromFile/".format(unittest_endpoint), status_location
        )
        yield file_path

    @responses.activate
    def test_create_from_file_path(self, mock_dataset, set_up_file_upload, status_location):
        file_path = set_up_file_upload
        result = Dataset.create_from_file(file_path)

        post_call = responses.calls[0].request
        assert post_call.method == "POST"
        assert post_call.url.endswith("datasets/fromFile/")
        file_field = post_call.body.fields["file"]

        assert file_field[0] == os.path.basename(file_path)
        filelike = file_field[1]
        assert filelike.name == file_path

        status_call = responses.calls[1].request
        assert status_call.method == "GET"
        assert status_call.url == status_location

        get_dataset_call = responses.calls[2].request
        assert get_dataset_call.method == "GET"
        assert get_dataset_call.url.endswith("/datasets/{}/".format(mock_dataset["datasetId"]))

        assert_dataset(result, mock_dataset)

    @responses.activate
    def test_create_from_file_path_with_categories(
        self, mock_dataset, set_up_file_upload, dataset_url
    ):
        updated_dataset = deepcopy(mock_dataset)
        updated_dataset["categories"] = ["some", "new", "categories"]
        responses.add(
            responses.PATCH,
            dataset_url,
            status=200,
            content_type="application/json",
            body=json.dumps(updated_dataset),
        )
        categories = ["a", "b", "c"]
        result = Dataset.create_from_file(file_path=set_up_file_upload, categories=categories)
        patch_call = responses.calls[3].request
        assert patch_call.method == "PATCH"
        assert request_body_to_json(patch_call) == {"categories": categories}

        assert_dataset(result, updated_dataset)

    @responses.activate
    def test_create_from_filelike_with_name_field(self, mock_dataset, set_up_file_upload):
        file_path = set_up_file_upload
        with open(file_path, "wb") as file_pointer:
            # noinspection PyTypeChecker
            result = Dataset.create_from_file(filelike=file_pointer)

            post_call = responses.calls[0].request
            file_field = post_call.body.fields["file"]

            assert file_field[0] == os.path.basename(file_path)
            filelike = file_field[1]
            assert filelike.name == file_path

        assert_dataset(result, mock_dataset)

    @responses.activate
    def test_create_from_filelike_without_name_field(self, set_up_file_upload):
        file_contents = "hello"
        file_pointer = six.StringIO(file_contents)
        # noinspection PyTypeChecker
        Dataset.create_from_file(filelike=file_pointer)

        post_call = responses.calls[0].request
        file_field = post_call.body.fields["file"]

        assert file_field[0] == "data.csv"
        filelike = file_field[1]
        filelike.seek(0)
        assert filelike.read() == file_contents

    @responses.activate
    def test_create_from_file_uses_read_timeout(self):
        """
        Check that the read_timeout parameter gets passed correctly down into
        the `requests` library
        """
        path = fixture_file_path("synthetic-100.csv")
        read_timeout = 2

        # return 400 since all we care is that read_timeout is passed down to the HTTP request
        responses.add(
            responses.POST, "https://host_name.com/datasets/fromFile/", body="", status=400,
        )

        with mock.patch.object(
            Dataset._client, "request", wraps=Dataset._client.request
        ) as mock_request:
            try:
                Dataset.create_from_file(path, read_timeout=read_timeout)
            except errors.ClientError:
                pass

            timeout = mock_request.call_args[1]["timeout"]
            assert timeout[0] == DEFAULT_TIMEOUT.CONNECT  # Connect timeout;
            assert timeout[1] == read_timeout  # Read timeout;

    @responses.activate
    def test_create_from_file_uses_max_wait(self, mock_async_time, dataset_url):
        """
        Check that the max_wait parameter is in effect when uploading file
        """
        path = fixture_file_path("synthetic-100.csv")
        mock_async_time.time.side_effect = (0, 5)
        responses.add(
            responses.POST,
            "https://host_name.com/datasets/fromFile/",
            body="",
            status=200,
            headers={"Location": dataset_url},
        )
        responses.add(responses.GET, dataset_url, content_type="application/json", status=200)

        with pytest.raises(errors.AsyncTimeoutError):
            Dataset.create_from_file(path, max_wait=2)

    def test_create_from_file_no_file_params_raises_type_error(self):
        with pytest.raises(TypeError):
            Dataset.create_from_file(categories=["a", "b"])

    def test_create_from_file_two_file_params_raises_type_error(self):
        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            Dataset.create_from_file(file_path="a-path.csv", filelike=six.StringIO())

    @responses.activate
    def test_create_from_in_memory_data_with_dataframe(self, mock_dataset, set_up_file_upload):
        data = [{"a": "x", "b": "y"}, {"a": "d", "b": "e"}]
        df = DataFrame(data)
        test_buffer = dataframe_to_buffer(df)

        result = Dataset.create_from_in_memory_data(data_frame=df)

        post_call = responses.calls[0].request
        assert post_call.url.endswith("/datasets/fromFile/")
        assert post_call.method == "POST"
        file_field = post_call.body.fields["file"]
        assert file_field[0] == "data.csv"
        filelike = file_field[1]
        filelike.seek(0)
        assert filelike.read() == test_buffer.read()

        assert_dataset(result, mock_dataset)

    @responses.activate
    def test_create_from_in_memory_data_with_source_list(self, mock_dataset, set_up_file_upload):
        data = [{"a": "x", "b": "y"}, {"a": "d", "b": "e"}]
        test_buffer = list_of_records_to_buffer(data)

        result = Dataset.create_from_in_memory_data(records=data)

        post_call = responses.calls[0].request
        file_field = post_call.body.fields["file"]
        assert file_field[0] == "data.csv"
        filelike = file_field[1]
        filelike.seek(0)
        assert filelike.read() == test_buffer.read()

        assert_dataset(result, mock_dataset)

    @responses.activate
    def test_create_from_in_memory_data_with_categories(
        self, mock_dataset, set_up_file_upload, dataset_url
    ):
        updated_response = deepcopy(mock_dataset)
        updated_response["categories"] = ["some", "new", "categories"]
        responses.add(
            responses.PATCH,
            dataset_url,
            status=200,
            content_type="application/json",
            body=json.dumps(updated_response),
        )
        data = [{"a": "x", "b": "y"}, {"a": "d", "b": "e"}]
        categories = ["a", "b", "c"]
        result = Dataset.create_from_in_memory_data(records=data, categories=categories)

        patch_call = responses.calls[3].request
        assert patch_call.method == "PATCH"
        assert request_body_to_json(patch_call) == {"categories": categories}

        assert_dataset(result, updated_response)

    def test_create_from_in_memory_data_using_no_fields_raises_type_error(self):
        with pytest.raises(TypeError):
            Dataset.create_from_in_memory_data()

    def test_create_from_in_memory_data_using_both_fields_raises_type_error(self):
        data = [{"a": "x", "b": "y"}, {"a": "d", "b": "e"}]
        with pytest.raises(TypeError):
            Dataset.create_from_in_memory_data(data_frame=DataFrame(data), records=data)

    @pytest.fixture()
    def set_up_url_upload(self, unittest_endpoint, status_location, set_status_response):
        self.add_mock_upload_response(
            "{}/datasets/fromURL/".format(unittest_endpoint), status_location
        )

    @responses.activate
    @pytest.mark.usefixtures("set_up_url_upload")
    def test_create_from_url(self, mock_dataset):
        url = "https://somewhere.com"
        result = Dataset.create_from_url(url=url)

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {"url": url}

    @responses.activate
    @pytest.mark.usefixtures("set_up_url_upload")
    def test_create_from_url_with_do_snapshot(self, mock_dataset):
        do_snapshot = bool(random.randint(0, 1))
        url = "https://somewhere.com"
        result = Dataset.create_from_url(url=url, do_snapshot=do_snapshot)

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {"url": url, "doSnapshot": do_snapshot}

    @responses.activate
    @pytest.mark.usefixtures("set_up_url_upload")
    def test_create_from_url_with_persist_data_after_ingesiont(self, mock_dataset):
        persist_data_after_ingestion = bool(random.randint(0, 1))
        url = "https://somewhere.com"
        result = Dataset.create_from_url(
            url=url, persist_data_after_ingestion=persist_data_after_ingestion
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "url": url,
            "persistDataAfterIngestion": persist_data_after_ingestion,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_url_upload")
    def test_create_from_url_with_categories(self, mock_dataset):
        categories = ["a", "b", "c"]
        url = "https://somewhere.com"
        result = Dataset.create_from_url(url=url, categories=categories)

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {"url": url, "categories": categories}

    @pytest.fixture()
    def set_up_data_source_upload(self, unittest_endpoint, status_location, set_status_response):
        self.add_mock_upload_response(
            "{}/datasets/fromDataSource/".format(unittest_endpoint), status_location
        )

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    def test_create_from_data_source(self, mock_dataset):
        username = "test_user"
        password = "megasuperubersecretpassword"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_from_data_source(
            data_source_id=data_source_id, username=username, password=password
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "user": username,
            "password": password,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("do_snapshot", [True, False])
    def test_create_from_data_source_with_do_snapshot(self, mock_dataset, do_snapshot):
        username = "test_user"
        password = "megasuperubersecretpassword"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_from_data_source(
            data_source_id=data_source_id,
            username=username,
            password=password,
            do_snapshot=do_snapshot,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "user": username,
            "password": password,
            "doSnapshot": do_snapshot,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("persist_data_after_ingestion", [True, False])
    def test_create_from_data_source_with_persist_data_after_ingestion(
        self, mock_dataset, persist_data_after_ingestion
    ):
        username = "test_user"
        password = "megasuperubersecretpassword"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_from_data_source(
            data_source_id=data_source_id,
            username=username,
            password=password,
            persist_data_after_ingestion=persist_data_after_ingestion,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "user": username,
            "password": password,
            "persistDataAfterIngestion": persist_data_after_ingestion,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    def test_create_from_data_source_with_categories(self, mock_dataset):
        categories = ["a", "b", "c"]
        username = "test_user"
        password = "megasuperubersecretpassword"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_from_data_source(
            data_source_id=data_source_id,
            username=username,
            password=password,
            categories=categories,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "user": username,
            "password": password,
            "categories": categories,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("use_kerberos", [True, False])
    def test_create_from_data_source_with_use_kerberos(self, mock_dataset, use_kerberos):
        username = "test_user"
        password = "megasuperubersecretpassword"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_from_data_source(
            data_source_id=data_source_id,
            username=username,
            password=password,
            use_kerberos=use_kerberos,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "user": username,
            "password": password,
            "useKerberos": use_kerberos,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    def test_create_from_data_source_credentials(self, mock_dataset):
        data_source_id = "5acc8437ec8d670001ba16bf"
        credential_id = "6acc8437ec8d670001ba16bf"
        result = Dataset.create_from_data_source(
            data_source_id=data_source_id, credential_id=credential_id
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {"dataSourceId": data_source_id, "credentialId": credential_id}

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("do_snapshot", [True, False])
    def test_create_from_data_source_with_do_snapshot_credentials(self, mock_dataset, do_snapshot):
        credential_id = "6acc8437ec8d670001ba16bf"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_from_data_source(
            data_source_id=data_source_id, credential_id=credential_id, do_snapshot=do_snapshot
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "credentialId": credential_id,
            "doSnapshot": do_snapshot,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("persist_data_after_ingestion", [True, False])
    def test_create_from_data_source_with_persist_data_after_ingestion_credentials(
        self, mock_dataset, persist_data_after_ingestion
    ):
        credential_id = "6acc8437ec8d670001ba16bf"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_from_data_source(
            data_source_id=data_source_id,
            credential_id=credential_id,
            persist_data_after_ingestion=persist_data_after_ingestion,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "credentialId": credential_id,
            "persistDataAfterIngestion": persist_data_after_ingestion,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    def test_create_from_data_source_with_categories_credentials(self, mock_dataset):
        categories = ["a", "b", "c"]
        credential_id = "6acc8437ec8d670001ba16bf"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_from_data_source(
            data_source_id=data_source_id, credential_id=credential_id, categories=categories
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "credentialId": credential_id,
            "categories": categories,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("use_kerberos", [True, False])
    def test_create_from_data_source_with_use_kerberos_credentials(
        self, mock_dataset, use_kerberos
    ):
        credential_id = "6acc8437ec8d670001ba16bf"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_from_data_source(
            data_source_id=data_source_id, credential_id=credential_id, use_kerberos=use_kerberos
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "credentialId": credential_id,
            "useKerberos": use_kerberos,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("credential_data", [BASIC_CREDS, S3_CREDS, OAUTH_CREDS, GCP_CREDS])
    def test_create_from_data_source_credential_data(self, mock_dataset, credential_data):
        data_source_id = "5acc8437ec8d670001ba16bf"

        result = Dataset.create_from_data_source(
            data_source_id=data_source_id, credential_data=credential_data
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {"dataSourceId": data_source_id, "credentialData": credential_data}

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("do_snapshot", [True, False])
    @pytest.mark.parametrize("credential_data", [BASIC_CREDS, S3_CREDS, OAUTH_CREDS, GCP_CREDS])
    def test_create_from_data_source_with_do_snapshot_credential_data(
        self, mock_dataset, do_snapshot, credential_data
    ):
        data_source_id = "5acc8437ec8d670001ba16bf"

        result = Dataset.create_from_data_source(
            data_source_id=data_source_id, credential_data=credential_data, do_snapshot=do_snapshot
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "credentialData": credential_data,
            "doSnapshot": do_snapshot,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("persist_data_after_ingestion", [True, False])
    @pytest.mark.parametrize("credential_data", [BASIC_CREDS, S3_CREDS, OAUTH_CREDS, GCP_CREDS])
    def test_create_from_data_source_with_persist_data_after_ingestion_credential_data(
        self, mock_dataset, persist_data_after_ingestion, credential_data
    ):
        data_source_id = "5acc8437ec8d670001ba16bf"

        result = Dataset.create_from_data_source(
            data_source_id=data_source_id,
            credential_data=credential_data,
            persist_data_after_ingestion=persist_data_after_ingestion,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "credentialData": credential_data,
            "persistDataAfterIngestion": persist_data_after_ingestion,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("credential_data", [BASIC_CREDS, S3_CREDS, OAUTH_CREDS, GCP_CREDS])
    def test_create_from_data_source_with_categories_credential_data(
        self, mock_dataset, credential_data
    ):
        categories = ["a", "b", "c"]
        data_source_id = "5acc8437ec8d670001ba16bf"

        result = Dataset.create_from_data_source(
            data_source_id=data_source_id, credential_data=credential_data, categories=categories
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "credentialData": credential_data,
            "categories": categories,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("use_kerberos", [True, False])
    @pytest.mark.parametrize("credential_data", [BASIC_CREDS, S3_CREDS, OAUTH_CREDS, GCP_CREDS])
    def test_create_from_data_source_with_use_kerberos_credential_data(
        self, mock_dataset, use_kerberos, credential_data
    ):
        data_source_id = "5acc8437ec8d670001ba16bf"

        result = Dataset.create_from_data_source(
            data_source_id=data_source_id,
            credential_data=credential_data,
            use_kerberos=use_kerberos,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "credentialData": credential_data,
            "useKerberos": use_kerberos,
        }

    @pytest.fixture
    def set_up_query_generator(self, unittest_endpoint, status_location, set_status_response):
        responses.add(
            responses.POST,
            "{}/dataEngineWorkspaceStates/fromDataEngineQueryGenerator/".format(unittest_endpoint),
            body=json.dumps({"workspaceStateId": "someWorkspaceStateId"}),
            status=201,
            content_type="application_json",
        )
        self.add_mock_upload_response(
            "{}/datasets/fromDataEngineWorkspaceState/".format(unittest_endpoint), status_location
        )

    @responses.activate
    @pytest.mark.usefixtures("set_up_query_generator")
    def test_create_from_query_generator(self, mock_dataset):

        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_from_query_generator(generator_id=data_source_id)

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {"queryGeneratorId": data_source_id}


class TestDatasetDetails(object):
    @staticmethod
    def assert_details_equal(details_obj, details_json):
        # type: (DatasetDetails, dict) -> None

        def date_or_none(date_entry):
            return dateutil.parser.parse(date_entry) if date_entry else None

        assert details_obj.dataset_id == details_json["datasetId"]
        assert details_obj.data_source_type == details_json["dataSourceType"]
        assert details_obj.error == details_json["error"]
        assert details_obj.last_modification_date == dateutil.parser.parse(
            details_json["lastModificationDate"]
        )
        assert details_obj.last_modifier_full_name == details_json["lastModifierFullName"]
        assert details_obj.uri == details_json["uri"]
        assert details_obj.data_engine_query_id == details_json["dataEngineQueryId"]
        assert details_obj.data_source_id == details_json["dataSourceId"]
        assert details_obj.description == details_json["description"]
        assert details_obj.eda1_modification_date == date_or_none(
            details_json["eda1ModificationDate"]
        )
        assert details_obj.eda1_modifier_full_name == details_json["eda1ModifierFullName"]
        assert details_obj.feature_count == details_json["featureCount"]
        json_list = details_json["featureCountByType"]
        assert details_obj.feature_count_by_type == [
            FeatureTypeCount(feature_type=el["featureType"], count=el["count"]) for el in json_list
        ]
        assert details_obj.tags == details_json["tags"]

        assert_base_dataset_fields(details_obj, details_json)

    def test_create_from_server_data(self, mock_dataset_full_response):
        details = DatasetDetails.from_server_data(mock_dataset_full_response)
        self.assert_details_equal(details, mock_dataset_full_response)

    def test_create_from_server_data_using_empty_response(self, empty_dataset_full_response):
        details = DatasetDetails.from_server_data(empty_dataset_full_response)
        self.assert_details_equal(details, empty_dataset_full_response)

    @responses.activate
    def test_get_method(self, dataset_get_response, mock_dataset_full_response):
        details = DatasetDetails.get(mock_dataset_full_response["datasetId"])
        self.assert_details_equal(details, mock_dataset_full_response)

        assert responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url.endswith("/datasets/{}/".format(details.dataset_id))

    @responses.activate
    def test_to_dataset(self, dataset_get_response, mock_dataset_full_response):
        details = DatasetDetails.from_server_data(mock_dataset_full_response)
        dataset = details.to_dataset()
        assert details.dataset_id == dataset.id
        assert_dataset(dataset, mock_dataset_full_response)

        assert len(responses.calls) == 0

    @responses.activate
    def test_dataset_method_get_details(self, dataset_get_response, mock_dataset_full_response):
        dataset = Dataset.from_server_data(mock_dataset_full_response)
        details = dataset.get_details()

        assert details.dataset_id == dataset.id
        self.assert_details_equal(details, mock_dataset_full_response)

        assert responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url.endswith("/datasets/{}/".format(details.dataset_id))
        assert len(responses.calls) == 1


class TestDatasetVersionCreation(object):
    @pytest.fixture()
    def status_location(self):
        return "https://some_location.com/"

    @pytest.fixture()
    def set_status_response(self, dataset_url, mock_dataset, status_location):
        responses.add(responses.GET, status_location, status=303, headers={"Location": dataset_url})
        add_mock_get_response(url=dataset_url, json_dict=mock_dataset)
        return dataset_url

    @staticmethod
    def add_mock_upload_response(url, status_location):
        responses.add(responses.POST, url, status=200, adding_headers={"Location": status_location})

    @pytest.fixture()
    def set_up_file_upload(
        self, unittest_endpoint, status_location, set_status_response, file_path, mock_dataset
    ):
        with open(file_path, "wb") as f:
            f.write(b"")
        dataset_id = mock_dataset["datasetId"]
        self.add_mock_upload_response(
            "{}/datasets/{}/versions/fromFile/".format(unittest_endpoint, dataset_id),
            status_location,
        )
        yield file_path

    @responses.activate
    def test_create_from_file_path(self, mock_dataset, set_up_file_upload, status_location):
        file_path = set_up_file_upload
        result = Dataset.create_version_from_file(mock_dataset["datasetId"], file_path)

        post_call = responses.calls[0].request
        assert post_call.method == "POST"
        url = "datasets/{}/versions/fromFile/".format(mock_dataset["datasetId"])
        assert post_call.url.endswith(url)
        file_field = post_call.body.fields["file"]

        assert file_field[0] == os.path.basename(file_path)
        filelike = file_field[1]
        assert filelike.name == file_path

        status_call = responses.calls[1].request
        assert status_call.method == "GET"
        assert status_call.url == status_location

        get_dataset_call = responses.calls[2].request
        assert get_dataset_call.method == "GET"
        assert get_dataset_call.url.endswith("/datasets/{}/".format(mock_dataset["datasetId"]))

        assert_dataset(result, mock_dataset)

    @responses.activate
    def test_create_from_file_path_with_categories(
        self, mock_dataset, set_up_file_upload, dataset_url
    ):
        updated_dataset = deepcopy(mock_dataset)
        updated_dataset["categories"] = ["some", "new", "categories"]
        responses.add(
            responses.PATCH,
            dataset_url,
            status=200,
            content_type="application/json",
            body=json.dumps(updated_dataset),
        )
        categories = ["a", "b", "c"]
        result = Dataset.create_version_from_file(
            dataset_id=mock_dataset["datasetId"],
            file_path=set_up_file_upload,
            categories=categories,
        )
        patch_call = responses.calls[3].request
        assert patch_call.method == "PATCH"
        assert request_body_to_json(patch_call) == {"categories": categories}

        assert_dataset(result, updated_dataset)

    @responses.activate
    def test_create_from_filelike_with_name_field(self, mock_dataset, set_up_file_upload):
        file_path = set_up_file_upload
        with open(file_path, "wb") as file_pointer:
            # noinspection PyTypeChecker
            result = Dataset.create_version_from_file(
                dataset_id=mock_dataset["datasetId"], filelike=file_pointer
            )

            post_call = responses.calls[0].request
            file_field = post_call.body.fields["file"]

            assert file_field[0] == os.path.basename(file_path)
            filelike = file_field[1]
            assert filelike.name == file_path

        assert_dataset(result, mock_dataset)

    def test_create_from_file_no_file_params_raises_type_error(self, mock_dataset):
        with pytest.raises(TypeError):
            Dataset.create_version_from_file(
                dataset_id=mock_dataset["datasetId"], categories=["a", "b"]
            )

    def test_create_from_file_two_file_params_raises_type_error(self, mock_dataset):
        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            Dataset.create_version_from_file(
                dataset_id=mock_dataset["datasetId"],
                file_path="a-path.csv",
                filelike=six.StringIO(),
            )

    @responses.activate
    def test_create_from_in_memory_data_with_dataframe(self, mock_dataset, set_up_file_upload):
        data = [{"a": "x", "b": "y"}, {"a": "d", "b": "e"}]
        df = DataFrame(data)
        test_buffer = dataframe_to_buffer(df)

        result = Dataset.create_version_from_in_memory_data(
            dataset_id=mock_dataset["datasetId"], data_frame=df
        )

        post_call = responses.calls[0].request
        url = "datasets/{}/versions/fromFile/".format(mock_dataset["datasetId"])
        assert post_call.url.endswith(url)
        assert post_call.method == "POST"
        file_field = post_call.body.fields["file"]
        assert file_field[0] == "data.csv"
        filelike = file_field[1]
        filelike.seek(0)
        assert filelike.read() == test_buffer.read()

        assert_dataset(result, mock_dataset)

    @responses.activate
    def test_create_from_in_memory_data_with_source_list(self, mock_dataset, set_up_file_upload):
        data = [{"a": "x", "b": "y"}, {"a": "d", "b": "e"}]
        test_buffer = list_of_records_to_buffer(data)

        result = Dataset.create_version_from_in_memory_data(
            dataset_id=mock_dataset["datasetId"], records=data
        )

        post_call = responses.calls[0].request
        file_field = post_call.body.fields["file"]
        assert file_field[0] == "data.csv"
        filelike = file_field[1]
        filelike.seek(0)
        assert filelike.read() == test_buffer.read()

        assert_dataset(result, mock_dataset)

    def test_create_from_in_memory_data_using_no_fields_raises_type_error(self, mock_dataset):
        with pytest.raises(TypeError):
            Dataset.create_version_from_in_memory_data(dataset_id=mock_dataset["datasetId"])

    def test_create_from_in_memory_data_using_both_fields_raises_type_error(self, mock_dataset):
        data = [{"a": "x", "b": "y"}, {"a": "d", "b": "e"}]
        with pytest.raises(TypeError):
            Dataset.create_version_from_in_memory_data(
                dataset_id=mock_dataset["datasetId"], data_frame=DataFrame(data), records=data
            )

    @pytest.fixture()
    def set_up_url_upload(
        self, unittest_endpoint, status_location, set_status_response, mock_dataset
    ):
        self.add_mock_upload_response(
            "{}/datasets/{}/versions/fromURL/".format(unittest_endpoint, mock_dataset["datasetId"]),
            status_location,
        )

    @responses.activate
    @pytest.mark.usefixtures("set_up_url_upload")
    def test_create_from_url(self, mock_dataset):
        url = "https://somewhere.com"
        result = Dataset.create_version_from_url(dataset_id=mock_dataset["datasetId"], url=url)

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {"url": url}

    @responses.activate
    @pytest.mark.usefixtures("set_up_url_upload")
    def test_create_from_url_with_categories(self, mock_dataset):
        categories = ["a", "b", "c"]
        url = "https://somewhere.com"
        result = Dataset.create_version_from_url(
            dataset_id=mock_dataset["datasetId"], url=url, categories=categories
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {"url": url, "categories": categories}

    @pytest.fixture()
    def set_up_data_source_upload(
        self, unittest_endpoint, status_location, set_status_response, mock_dataset
    ):
        self.add_mock_upload_response(
            "{}/datasets/{}/versions/fromDataSource/".format(
                unittest_endpoint, mock_dataset["datasetId"]
            ),
            status_location,
        )

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    def test_create_from_data_source(self, mock_dataset):
        username = "test_user"
        password = "megasuperubersecretpassword"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_version_from_data_source(
            dataset_id=mock_dataset["datasetId"],
            data_source_id=data_source_id,
            username=username,
            password=password,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "user": username,
            "password": password,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    def test_create_from_data_source_with_categories(self, mock_dataset):
        categories = ["a", "b", "c"]
        username = "test_user"
        password = "megasuperubersecretpassword"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_version_from_data_source(
            dataset_id=mock_dataset["datasetId"],
            data_source_id=data_source_id,
            username=username,
            password=password,
            categories=categories,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "user": username,
            "password": password,
            "categories": categories,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("use_kerberos", [True, False])
    def test_create_from_data_source_with_use_kerberos(self, mock_dataset, use_kerberos):
        username = "test_user"
        password = "megasuperubersecretpassword"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_version_from_data_source(
            dataset_id=mock_dataset["datasetId"],
            data_source_id=data_source_id,
            username=username,
            password=password,
            use_kerberos=use_kerberos,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "user": username,
            "password": password,
            "useKerberos": use_kerberos,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    def test_create_from_data_source_credentials(self, mock_dataset):
        data_source_id = "5acc8437ec8d670001ba16bf"
        credential_id = "6acc8437ec8d670001ba16bf"
        result = Dataset.create_version_from_data_source(
            dataset_id=mock_dataset["datasetId"],
            data_source_id=data_source_id,
            credential_id=credential_id,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {"dataSourceId": data_source_id, "credentialId": credential_id}

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    def test_create_from_data_source_with_categories_credentials(self, mock_dataset):
        categories = ["a", "b", "c"]
        credential_id = "6acc8437ec8d670001ba16bf"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_version_from_data_source(
            dataset_id=mock_dataset["datasetId"],
            data_source_id=data_source_id,
            credential_id=credential_id,
            categories=categories,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "credentialId": credential_id,
            "categories": categories,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("use_kerberos", [True, False])
    def test_create_from_data_source_with_use_kerberos_credentials(
        self, mock_dataset, use_kerberos
    ):
        credential_id = "6acc8437ec8d670001ba16bf"
        data_source_id = "5acc8437ec8d670001ba16bf"
        result = Dataset.create_version_from_data_source(
            dataset_id=mock_dataset["datasetId"],
            data_source_id=data_source_id,
            credential_id=credential_id,
            use_kerberos=use_kerberos,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "credentialId": credential_id,
            "useKerberos": use_kerberos,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("credential_data", [BASIC_CREDS, S3_CREDS, OAUTH_CREDS, GCP_CREDS])
    def test_create_from_data_source_credential_data(self, mock_dataset, credential_data):
        data_source_id = "5acc8437ec8d670001ba16bf"

        result = Dataset.create_version_from_data_source(
            dataset_id=mock_dataset["datasetId"],
            data_source_id=data_source_id,
            credential_data=credential_data,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {"dataSourceId": data_source_id, "credentialData": credential_data}

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("credential_data", [BASIC_CREDS, S3_CREDS, OAUTH_CREDS, GCP_CREDS])
    def test_create_from_data_source_with_categories_credential_data(
        self, mock_dataset, credential_data
    ):
        categories = ["a", "b", "c"]
        data_source_id = "5acc8437ec8d670001ba16bf"

        result = Dataset.create_version_from_data_source(
            dataset_id=mock_dataset["datasetId"],
            data_source_id=data_source_id,
            credential_data=credential_data,
            categories=categories,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "credentialData": credential_data,
            "categories": categories,
        }

    @responses.activate
    @pytest.mark.usefixtures("set_up_data_source_upload")
    @pytest.mark.parametrize("use_kerberos", [True, False])
    @pytest.mark.parametrize("credential_data", [BASIC_CREDS, S3_CREDS, OAUTH_CREDS, GCP_CREDS])
    def test_create_from_data_source_with_use_kerberos_credential_data(
        self, mock_dataset, use_kerberos, credential_data
    ):
        data_source_id = "5acc8437ec8d670001ba16bf"

        result = Dataset.create_version_from_data_source(
            dataset_id=mock_dataset["datasetId"],
            data_source_id=data_source_id,
            credential_data=credential_data,
            use_kerberos=use_kerberos,
        )

        assert_dataset(result, mock_dataset)
        post_params = request_body_to_json(responses.calls[0].request)
        assert post_params == {
            "dataSourceId": data_source_id,
            "credentialData": credential_data,
            "useKerberos": use_kerberos,
        }


def get_url(index):
    return responses.calls[index].request.url

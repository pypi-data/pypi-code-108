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

import pytest
import responses
from six.moves.urllib_parse import parse_qs, urlparse

from datarobot import DatasetFeaturelist, Featurelist, ModelingFeaturelist, Project
from datarobot.utils import from_api, parse_time
from tests.utils import SDKTestcase


class TestFeaturelist(SDKTestcase):
    def test_instantiate_featurelist(self):
        data = {
            "id": "5223deadbeefdeadbeef9999",
            "name": "Raw Features",
            "features": ["One Fish", "Two Fish", "Red Fish", "Blue Fish"],
            "project_id": "5223deadbeefdeadbeef0101",
            "created": parse_time("2018-07-02T18:49:38.019000Z"),
            "is_user_created": True,
            "num_models": 5,
        }

        flist = Featurelist.from_data(data)

        assert flist.id == data["id"]
        assert flist.name == data["name"]
        assert flist.features == data["features"]
        assert repr(flist) == "Featurelist(Raw Features)"
        assert flist.created == data["created"]
        assert flist.is_user_created == data["is_user_created"]
        assert flist.num_models == data["num_models"]

    @pytest.mark.usefixtures("known_warning")
    def test_instantiate_featurelist_from_dict_deprecated(self):
        data = {
            "id": "5223deadbeefdeadbeef9999",
            "name": "Raw Features",
            "features": ["One Fish", "Two Fish", "Red Fish", "Blue Fish"],
            "project_id": "5223deadbeefdeadbeef0101",
            "created": parse_time("2018-07-02T18:49:38.019000Z"),
            "is_user_created": True,
            "num_models": 5,
        }

        flist = Featurelist(data)

        assert flist.id == data["id"]
        assert flist.name == data["name"]
        assert flist.features, data["features"]
        assert flist.project.id == data["project_id"]
        assert repr(flist) == "Featurelist(Raw Features)"


def test_future_proof(featurelist_server_data):
    Featurelist.from_server_data(dict(featurelist_server_data, future="new"))


@pytest.mark.usefixtures("known_warning")
def test_project_is_known_deprecation(featurelist_server_data):
    fl = Featurelist.from_server_data(dict(featurelist_server_data, future="new"))
    assert fl.project


@responses.activate
def test_get_featurelist(featurelist_server_data, project_id):
    url_template = "https://host_name.com/projects/{}/featurelists/{}/"
    responses.add(
        responses.GET,
        url_template.format(project_id, featurelist_server_data["id"]),
        json=featurelist_server_data,
        status=200,
        content_type="application/json",
    )
    result = Featurelist.get(project_id, featurelist_server_data["id"])
    assert result.project_id == project_id
    assert result.name == featurelist_server_data["name"]
    assert isinstance(result.created, datetime)


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_get_featurelist_with_project_instance(featurelist_server_data, project_id):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/featurelists/f-id/".format(project_id),
        json=featurelist_server_data,
        status=200,
        content_type="application/json",
    )

    pdata = {"id": project_id, "project_name": "Projects"}
    project = Project.from_data(pdata)

    result = Featurelist.get(project, "f-id")
    assert result.project.id == project_id
    assert result.name == featurelist_server_data["name"]


def test_rejects_bad_project_input():
    not_a_project = 5
    with pytest.raises(ValueError):
        Featurelist.get(not_a_project, "f-id")


def test_print_non_ascii_featurelist(featurelist_server_data):
    hello = u"\u3053\u3093\u306b\u3061\u306f"
    data = dict(featurelist_server_data)
    data["name"] = hello
    featurelist = Featurelist.from_server_data(data)
    print(featurelist)  # actually part of the test - this used to fail (testing __repr__)


@pytest.fixture
def modeling_featurelist_server_data(project_id):
    return {
        "projectId": project_id,
        "id": "5a077ec5a297f9d9229aacaa",
        "name": "Timeseries Extracted Features",
        "created": "2018-07-02T18:49:38.019000Z",
        "numModels": 5,
        "isUserCreated": False,
        "description": "A Modeling List",
        "features": [
            "Digital Spend (14 day max)",
            "Digital Spend (14 day mean)",
            "Digital Spend (14 day median)",
            "Digital Spend (14 day min)",
            "Digital Spend (14 day std)",
            "Digital Spend (1st lag)",
            "Digital Spend (21 day max)",
            "Digital Spend (21 day mean)",
            "Digital Spend (21 day median)",
            "Digital Spend (21 day min)",
            "Digital Spend (21 day std)",
            "Digital Spend (28 day max)",
            "Digital Spend (28 day mean)",
            "Digital Spend (28 day median)",
            "Digital Spend (28 day min)",
            "Digital Spend (28 day std)",
            "Digital Spend (2nd lag)",
            "Digital Spend (3rd lag)",
            "Digital Spend (4th lag)",
            "Digital Spend (5th lag)",
            "Digital Spend (7 day max)",
            "Digital Spend (7 day mean)",
            "Digital Spend (7 day median)",
            "Digital Spend (7 day min)",
            "Digital Spend (7 day std)",
            "Forecast Distance",
            "Inventory Rate (14 day max)",
            "Inventory Rate (14 day mean)",
            "Inventory Rate (14 day median)",
            "Inventory Rate (14 day min)",
            "Inventory Rate (14 day std)",
            "Inventory Rate (1st lag)",
            "Inventory Rate (21 day max)",
            "Inventory Rate (21 day mean)",
            "Inventory Rate (21 day median)",
            "Inventory Rate (21 day min)",
            "Inventory Rate (21 day std)",
            "Inventory Rate (28 day max)",
            "Inventory Rate (28 day mean)",
            "Inventory Rate (28 day median)",
            "Inventory Rate (28 day min)",
            "Inventory Rate (28 day std)",
            "Inventory Rate (2nd lag)",
            "Inventory Rate (3rd lag)",
            "Inventory Rate (4th lag)",
            "Inventory Rate (5th lag)",
            "Inventory Rate (7 day max)",
            "Inventory Rate (7 day mean)",
            "Inventory Rate (7 day median)",
            "Inventory Rate (7 day min)",
            "Inventory Rate (7 day std)",
            "Num Employees (14 day max)",
            "Num Employees (14 day mean)",
            "Num Employees (14 day median)",
            "Num Employees (14 day min)",
            "Num Employees (14 day std)",
            "Num Employees (1st lag)",
            "Num Employees (21 day max)",
            "Num Employees (21 day mean)",
            "Num Employees (21 day median)",
            "Num Employees (21 day min)",
            "Num Employees (21 day std)",
            "Num Employees (28 day max)",
            "Num Employees (28 day mean)",
            "Num Employees (28 day median)",
            "Num Employees (28 day min)",
            "Num Employees (28 day std)",
            "Num Employees (2nd lag)",
            "Num Employees (3rd lag)",
            "Num Employees (4th lag)",
            "Num Employees (5th lag)",
            "Num Employees (7 day max)",
            "Num Employees (7 day mean)",
            "Num Employees (7 day median)",
            "Num Employees (7 day min)",
            "Num Employees (7 day std)",
            "Precipitation (14 day max)",
            "Precipitation (14 day mean)",
            "Precipitation (14 day median)",
            "Precipitation (14 day min)",
            "Precipitation (14 day std)",
            "Precipitation (1st lag)",
            "Precipitation (21 day max)",
            "Precipitation (21 day mean)",
            "Precipitation (21 day median)",
            "Precipitation (21 day min)",
            "Precipitation (21 day std)",
            "Precipitation (28 day max)",
            "Precipitation (28 day mean)",
            "Precipitation (28 day median)",
            "Precipitation (28 day min)",
            "Precipitation (28 day std)",
            "Precipitation (2nd lag)",
            "Precipitation (3rd lag)",
            "Precipitation (4th lag)",
            "Precipitation (5th lag)",
            "Precipitation (7 day max)",
            "Precipitation (7 day mean)",
            "Precipitation (7 day median)",
            "Precipitation (7 day min)",
            "Precipitation (7 day std)",
            "Sales (actual)",
            "Sales (log) (7 day diff) (14 day max)",
            "Sales (log) (7 day diff) (14 day mean)",
            "Sales (log) (7 day diff) (14 day median)",
            "Sales (log) (7 day diff) (14 day min)",
            "Sales (log) (7 day diff) (14 day std)",
            "Sales (log) (7 day diff) (1st lag)",
            "Sales (log) (7 day diff) (21 day max)",
            "Sales (log) (7 day diff) (21 day mean)",
            "Sales (log) (7 day diff) (21 day median)",
            "Sales (log) (7 day diff) (21 day std)",
            "Sales (log) (7 day diff) (28 day max)",
            "Sales (log) (7 day diff) (28 day mean)",
            "Sales (log) (7 day diff) (28 day median)",
            "Sales (log) (7 day diff) (28 day min)",
            "Sales (log) (7 day diff) (28 day std)",
            "Sales (log) (7 day diff) (2nd lag)",
            "Sales (log) (7 day diff) (3rd lag)",
            "Sales (log) (7 day diff) (4th lag)",
            "Sales (log) (7 day diff) (5th lag)",
            "Sales (log) (7 day diff) (7 day max)",
            "Sales (log) (7 day diff) (7 day mean)",
            "Sales (log) (7 day diff) (7 day median)",
            "Sales (log) (7 day diff) (7 day min)",
            "Sales (log) (7 day diff) (7 day std)",
            "Sales (log) (naive 7 day seasonal value)",
            "Time (Day of Month) (actual)",
            "Time (Day of Week) (actual)",
            "Time (Month) (actual)",
            "Time (Year) (actual)",
            "Time (actual)",
            "dr_row_type",
        ],
    }


@pytest.fixture
def modeling_featurelists_list_server_data(modeling_featurelist_server_data):
    return {"count": 1, "next": None, "previous": None, "data": [modeling_featurelist_server_data]}


@pytest.fixture
def modeling_featurelists_with_next_page_server_data(modeling_featurelist_server_data, project_url):
    next_page_url = "{}modelingFeaturelists/?offset=1&limit=1".format(project_url)
    flist = dict(modeling_featurelist_server_data)
    flist["name"] = "first_page"
    return {"count": 1, "next": next_page_url, "previous": None, "data": [flist]}


@pytest.fixture
def modeling_featurelists_with_previous_page_server_data(
    modeling_featurelist_server_data, project_url
):
    previous_page_url = "{}modelingFeaturelists/?offset=0&limit=1".format(project_url)
    flist = dict(modeling_featurelist_server_data)
    flist["name"] = "second_page"
    return {"count": 1, "next": None, "previous": previous_page_url, "data": [flist]}


@pytest.fixture
def dataset_featurelist_server_data(dataset_id):
    return {
        "datasetVersionId": None,
        "datasetId": dataset_id,
        "id": "5a077ec5a297f9d9229aacab",
        "name": "Informative Features",
        "creationDate": "2018-07-02T18:49:38.019000Z",
        "createdBy": "A User",
        "userCreated": False,
        "description": "System created featurelist",
        "features": [
            "rowID",
            "race",
            "gender",
            "age",
            "weight",
            "admission_type_id",
            "discharge_disposition_id",
            "admission_source_id",
            "time_in_hospital",
            "payer_code",
            "medical_specialty",
            "num_lab_procedures",
            "num_procedures",
            "num_medications",
            "number_outpatient",
            "number_emergency",
            "number_inpatient",
            "diag_1",
            "diag_2",
            "diag_3",
            "number_diagnoses",
            "max_glu_serum",
            "A1Cresult",
            "metformin",
            "repaglinide",
            "nateglinide",
            "chlorpropamide",
            "glimepiride",
            "acetohexamide",
            "glipizide",
            "glyburide",
            "tolbutamide",
            "pioglitazone",
            "rosiglitazone",
            "acarbose",
            "miglitol",
            "troglitazone",
            "tolazamide",
            "examide",
            "citoglipton",
            "insulin",
            "glyburide_metformin",
            "glipizide_metformin",
            "glimepiride_pioglitazone",
            "metformin_rosiglitazone",
            "metformin_pioglitazone",
            "change",
            "diabetesMed",
            "readmitted",
            "diag_1_desc",
            "diag_2_desc",
            "diag_3_desc",
            "is_expired",
        ],
    }


@pytest.fixture
def dataset_featurelists_list_server_data(dataset_featurelist_server_data):
    return {"count": 1, "next": None, "previous": None, "data": [dataset_featurelist_server_data]}


def test_modeling_featurelist_future_proof(modeling_featurelist_server_data):
    future_data = dict(modeling_featurelist_server_data, new="new")
    ModelingFeaturelist.from_server_data(future_data)


@responses.activate
def test_get_modeling_featurelist(modeling_featurelist_server_data, project_url, project_id):
    flist_id = modeling_featurelist_server_data["id"]
    url = "{}modelingFeaturelists/{}/".format(project_url, flist_id)
    responses.add(responses.GET, url, json=modeling_featurelist_server_data)

    flist = ModelingFeaturelist.get(project_id, flist_id)
    assert flist.project_id == project_id
    assert flist.name == modeling_featurelist_server_data["name"]
    assert flist.features == modeling_featurelist_server_data["features"]
    assert flist.id == flist_id
    assert isinstance(flist.created, datetime)
    assert flist.num_models == modeling_featurelist_server_data["numModels"]
    assert flist.is_user_created == modeling_featurelist_server_data["isUserCreated"]
    assert flist.description == modeling_featurelist_server_data["description"]


@responses.activate
def test_get_dataset_featurelist(dataset_featurelist_server_data, dataset_url, dataset_id):
    flist_id = dataset_featurelist_server_data["id"]
    url = "{}{}/{}/".format(dataset_url, "featurelists", flist_id)
    responses.add(responses.GET, url, json=dataset_featurelist_server_data)

    flist = DatasetFeaturelist.get(dataset_id, flist_id)
    assert flist.dataset_id == dataset_id
    assert flist.dataset_version_id == dataset_featurelist_server_data["datasetVersionId"]
    assert flist.name == dataset_featurelist_server_data["name"]
    assert flist.features == dataset_featurelist_server_data["features"]
    assert flist.id == flist_id
    assert isinstance(flist.creation_date, datetime)
    assert flist.created_by == dataset_featurelist_server_data["createdBy"]
    assert flist.user_created == dataset_featurelist_server_data["userCreated"]
    assert flist.description == dataset_featurelist_server_data["description"]


@responses.activate
def test_list_modeling_featurelists(modeling_featurelists_list_server_data, project_url, project):
    responses.add(
        responses.GET,
        "{}modelingFeaturelists/".format(project_url),
        json=modeling_featurelists_list_server_data,
    )
    flists = project.get_modeling_featurelists()

    assert len(flists) == len(modeling_featurelists_list_server_data["data"])
    assert isinstance(flists[0], ModelingFeaturelist)
    assert flists[0].name == modeling_featurelists_list_server_data["data"][0]["name"]


@responses.activate
def test_list_modeling_featurelists_paginated(
    modeling_featurelists_with_next_page_server_data,
    modeling_featurelists_with_previous_page_server_data,
    project,
    project_url,
):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}modelingFeaturelists/".format(project_url),
            json=modeling_featurelists_with_next_page_server_data,
        )
        rsps.add(
            responses.GET,
            "{}modelingFeaturelists/".format(project_url),
            json=modeling_featurelists_with_previous_page_server_data,
        )
        feats = project.get_modeling_featurelists(batch_size=1)

        first_page_req = rsps.calls[0].request
        second_page_req = rsps.calls[1].request
        assert {"limit": ["1"]} == parse_qs(urlparse(first_page_req.url).query)
        assert {"limit": ["1"], "offset": ["1"]} == parse_qs(urlparse(second_page_req.url).query)

    assert len(feats) == 2
    names = {"first_page", "second_page"}
    assert {feat.name for feat in feats} == names


@responses.activate
def test_list_dataset_featurelists(
    dataset_featurelists_list_server_data, dataset_url, mock_dataset_obj
):
    url = "{}{}/".format(dataset_url, "featurelists")
    responses.add(responses.GET, url, json=dataset_featurelists_list_server_data)
    flists = mock_dataset_obj.get_featurelists()

    assert len(flists) == len(dataset_featurelists_list_server_data["data"])
    assert isinstance(flists[0], DatasetFeaturelist)
    assert flists[0].name == dataset_featurelists_list_server_data["data"][0]["name"]


@responses.activate
def test_create_modeling_featurelist(modeling_featurelist_server_data, project_url, project):
    responses.add(
        responses.POST,
        "{}modelingFeaturelists/".format(project_url),
        json=modeling_featurelist_server_data,
    )

    name = modeling_featurelist_server_data["name"]
    features = modeling_featurelist_server_data["features"]
    flist = project.create_modeling_featurelist(name, features)

    assert isinstance(flist, ModelingFeaturelist)
    assert flist.id == modeling_featurelist_server_data["id"]
    assert flist.name == name
    assert flist.project_id == modeling_featurelist_server_data["projectId"]
    assert flist.features == features
    assert flist.is_user_created == modeling_featurelist_server_data["isUserCreated"]
    assert flist.num_models == modeling_featurelist_server_data["numModels"]
    assert flist.description == modeling_featurelist_server_data["description"]
    assert isinstance(flist.created, datetime)


@responses.activate
def test_create_dataset_featurelist(
    dataset_featurelist_server_data, dataset_url, mock_dataset_obj, dataset_id
):
    url = "{}{}/".format(dataset_url, "featurelists")
    responses.add(responses.POST, url, json=dataset_featurelist_server_data)

    name = dataset_featurelist_server_data["name"]
    features = dataset_featurelist_server_data["features"]
    flist = mock_dataset_obj.create_featurelist(name, features)

    assert isinstance(flist, DatasetFeaturelist)
    assert flist.id == dataset_featurelist_server_data["id"]
    assert flist.name == name
    assert flist.dataset_id == dataset_id
    assert flist.dataset_version_id == dataset_featurelist_server_data["datasetVersionId"]
    assert flist.features == features
    assert flist.user_created == dataset_featurelist_server_data["userCreated"]
    assert flist.created_by == dataset_featurelist_server_data["createdBy"]
    assert isinstance(flist.creation_date, datetime)
    assert flist.description == dataset_featurelist_server_data["description"]


@responses.activate
def test_update_featurelist_name_only(featurelist_server_data, project_url):
    featurelist = Featurelist.from_server_data(featurelist_server_data)
    responses.add(
        responses.PATCH, "{}featurelists/{}/".format(project_url, featurelist.id), status=204
    )

    new_name = "a new name"
    featurelist.update(name=new_name)
    assert featurelist.name == new_name
    assert featurelist.description == featurelist_server_data["description"]


@responses.activate
def test_update_featurelist_description_only(featurelist_server_data, project_url):
    featurelist = Featurelist.from_server_data(featurelist_server_data)
    responses.add(
        responses.PATCH, "{}featurelists/{}/".format(project_url, featurelist.id), status=204
    )

    new_description = "a new description"
    featurelist.update(description=new_description)
    assert featurelist.name == featurelist_server_data["name"]
    assert featurelist.description == new_description


@responses.activate
def test_update_featurelist(featurelist_server_data, project_url):
    featurelist = Featurelist.from_server_data(featurelist_server_data)
    responses.add(
        responses.PATCH, "{}featurelists/{}/".format(project_url, featurelist.id), status=204
    )

    new_name = "a new name"
    new_description = "a new description"
    featurelist.update(name=new_name, description=new_description)
    assert featurelist.name == new_name
    assert featurelist.description == new_description


@responses.activate
def test_update_modeling_featurelist_name_only(modeling_featurelist_server_data, project_url):
    featurelist = ModelingFeaturelist.from_server_data(modeling_featurelist_server_data)
    old_description = modeling_featurelist_server_data["description"]
    responses.add(
        responses.PATCH,
        "{}modelingFeaturelists/{}/".format(project_url, featurelist.id),
        status=204,
    )

    new_name = "a new name"
    featurelist.update(name=new_name)
    assert featurelist.name == new_name
    assert featurelist.description == old_description


@responses.activate
def test_update_modeling_featurelist_description_only(
    modeling_featurelist_server_data, project_url
):
    featurelist = ModelingFeaturelist.from_server_data(modeling_featurelist_server_data)
    responses.add(
        responses.PATCH,
        "{}modelingFeaturelists/{}/".format(project_url, featurelist.id),
        status=204,
    )

    new_description = "a new description"
    featurelist.update(description=new_description)
    assert featurelist.name == modeling_featurelist_server_data["name"]
    assert featurelist.description == new_description


@responses.activate
def test_update_modeling_featurelist(modeling_featurelist_server_data, project_url):
    featurelist = ModelingFeaturelist.from_server_data(modeling_featurelist_server_data)
    responses.add(
        responses.PATCH,
        "{}modelingFeaturelists/{}/".format(project_url, featurelist.id),
        status=204,
    )

    new_name = "a new name"
    new_description = "a new description"
    featurelist.update(name=new_name, description=new_description)
    assert featurelist.name == new_name
    assert featurelist.description == new_description


@responses.activate
def test_update_dataset_featurelist(dataset_featurelist_server_data, dataset_url):
    featurelist = DatasetFeaturelist.from_server_data(dataset_featurelist_server_data)
    url = "{}{}/{}/".format(dataset_url, "featurelists", featurelist.id)
    responses.add(responses.PATCH, url, status=204)

    new_name = "a new name"
    featurelist.update(name=new_name)
    assert featurelist.name == new_name
    assert featurelist.description == dataset_featurelist_server_data["description"]


@responses.activate
@pytest.mark.parametrize(
    "dry_run,delete_dependencies", [(False, False), (False, True), (True, False), (True, True)]
)
def test_delete_featurelist(featurelist_server_data, project_url, dry_run, delete_dependencies):
    featurelist = Featurelist.from_server_data(featurelist_server_data)
    response = {
        "dryRun": dry_run,
        "canDelete": True,
        "numAffectedModels": 3,
        "numAffectedJobs": 1,
        "deletionBlockedReason": "",
    }
    responses.add(
        responses.DELETE,
        "{}featurelists/{}/".format(project_url, featurelist.id),
        status=200,
        json=response,
    )

    result = featurelist.delete(dry_run=dry_run, delete_dependencies=delete_dependencies)

    delete_request = responses.calls[0].request
    expected_query_params = {
        "dryRun": [str(dry_run)],
        "deleteDependencies": [str(delete_dependencies)],
    }
    assert parse_qs(urlparse(delete_request.url).query) == expected_query_params
    assert result == from_api(response)


@responses.activate
def test_delete_featurelist_with_unicode_reason(featurelist_server_data, project_url):
    featurelist = Featurelist.from_server_data(featurelist_server_data)
    response = {
        "dryRun": False,
        "canDelete": True,
        "numAffectedModels": 3,
        "numAffectedJobs": 1,
        "deletion_blocked_reason": u"\u3053\u3093\u306b\u3061\u306f",
    }
    responses.add(
        responses.DELETE,
        "{}featurelists/{}/".format(project_url, featurelist.id),
        status=200,
        json=response,
    )

    result = featurelist.delete()
    assert result == from_api(response)


@responses.activate
@pytest.mark.parametrize(
    "dry_run,delete_dependencies", [(False, False), (False, True), (True, False), (True, True)]
)
def test_delete_modeling_featurelist(
    modeling_featurelist_server_data, project_url, dry_run, delete_dependencies
):
    featurelist = ModelingFeaturelist.from_server_data(modeling_featurelist_server_data)
    response = {
        "dryRun": dry_run,
        "canDelete": True,
        "numAffectedModels": 3,
        "numAffectedJobs": 1,
        "deletionBlockedReason": "",
    }
    responses.add(
        responses.DELETE,
        "{}modelingFeaturelists/{}/".format(project_url, featurelist.id),
        status=200,
        json=response,
    )

    result = featurelist.delete(dry_run=dry_run, delete_dependencies=delete_dependencies)

    delete_request = responses.calls[0].request
    expected_query_params = {
        "dryRun": [str(dry_run)],
        "deleteDependencies": [str(delete_dependencies)],
    }
    assert parse_qs(urlparse(delete_request.url).query) == expected_query_params
    assert result == from_api(response)


@responses.activate
def test_delete_modeling_featurelist_with_unicode_reason(
    modeling_featurelist_server_data, project_url
):
    featurelist = ModelingFeaturelist.from_server_data(modeling_featurelist_server_data)
    response = {
        "dryRun": False,
        "canDelete": True,
        "numAffectedModels": 3,
        "numAffectedJobs": 1,
        "deletion_blocked_reason": u"\u3053\u3093\u306b\u3061\u306f",
    }
    responses.add(
        responses.DELETE,
        "{}modelingFeaturelists/{}/".format(project_url, featurelist.id),
        status=200,
        json=response,
    )

    result = featurelist.delete()
    assert result == from_api(response)


@responses.activate
def test_delete_dataset_featurelist(dataset_featurelist_server_data, dataset_url):
    featurelist = DatasetFeaturelist.from_server_data(dataset_featurelist_server_data)
    url = "{}{}/{}/".format(dataset_url, "featurelists", featurelist.id)
    responses.add(responses.DELETE, url, status=200)
    featurelist.delete()

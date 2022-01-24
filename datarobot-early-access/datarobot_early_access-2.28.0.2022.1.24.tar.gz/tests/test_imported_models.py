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

from datarobot import ImportedModel
from tests.test_helpers import fixture_file_path

imported_model_dict = {
    u"originUrl": u"http://app.datarobot.com/",
    u"datasetName": u"train_data.csv",
    u"modelName": u"Linear Regression (5)",
    u"displayName": u"Linear Regression (5)",
    u"target": u"target",
    u"projectId": u"57b37876c808912b1c87094a",
    u"importedByUsername": u"david.chudzicki@datarobot.com",
    u"note": None,
    u"importedAt": u"2016-08-28 22:39:56.117000",
    u"version": 1.8,
    u"projectName": u"Unnamed Project",
    u"featurelistName": u"week_day",
    u"createdByUsername": u"david.chudzicki@datarobot.com",
    u"modelId": u"57b70cf5c80891295500c6e8",
    u"importedById": u"56a5a34b16f4b622fb8426f6",
    u"id": u"301d0dd18e034c058dbed3bdf8207a4a",
    u"createdById": u"56a5a34b16f4b622fb8426f6",
}


def add_imported_model_get_response(model_id):
    url = "https://host_name.com/importedModels/{}/".format(model_id)
    responses.add(responses.GET, url, body=json.dumps(imported_model_dict))


@pytest.fixture
@responses.activate
def imported_model():
    add_imported_model_get_response(imported_model_dict["id"])
    return ImportedModel.get(imported_model_dict["id"])


@responses.activate
def test_get(imported_model):
    assert imported_model.id == imported_model_dict["id"]


@responses.activate
def test_list():
    response_dict = {u"count": 1, u"next": None, u"previous": None, u"data": [imported_model_dict]}
    url = "https://host_name.com/importedModels/"
    responses.add(responses.GET, url, body=json.dumps(response_dict))
    imported_models = ImportedModel.list(imported_model_dict["id"])
    assert isinstance(imported_models, list)
    assert len(imported_models) == 1
    assert isinstance(imported_models[0], ImportedModel)


@responses.activate
def test_update(imported_model):
    url = "https://host_name.com/importedModels/{}/".format(imported_model_dict["id"])
    responses.add(responses.PATCH, url, body="this is not actually used")
    new_note = "new note"
    new_display_name = "new_display_name"
    imported_model.update(display_name=new_display_name, note=new_note)
    assert imported_model.note == new_note
    assert imported_model.display_name == new_display_name


@responses.activate
def test_delete(imported_model):
    url = "https://host_name.com/importedModels/{}/".format(imported_model_dict["id"])
    responses.add(responses.DELETE, url, body="not used")
    imported_model.delete()


@responses.activate
def test_create():
    responses.add(
        responses.POST,
        "https://host_name.com/importedModels/",
        body="",
        status=202,
        content_type="application/json",
        adding_headers={"Location": "https://host_name.com/status/status-id/"},
    )

    responses.add(
        responses.GET,
        "https://host_name.com/status/status-id/",
        status=303,
        body="",
        content_type="application/json",
        adding_headers={
            "Location": "https://host_name.com/importedModels/{}/".format(imported_model_dict["id"])
        },
    )
    add_imported_model_get_response(imported_model_dict["id"])

    imported_model = ImportedModel.create(fixture_file_path("some_model.drmodel"))
    assert isinstance(imported_model, ImportedModel)

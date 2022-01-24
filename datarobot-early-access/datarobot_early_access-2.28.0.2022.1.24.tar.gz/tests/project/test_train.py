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
import pytest
import responses

import datarobot
from datarobot import Blueprint, enums, Project
from tests.utils import request_body_to_json


@responses.activate
def test_async_flow(project, project_id, model_job_json, model_collection_url):
    responses.add(
        responses.POST,
        model_collection_url,
        content_type="application/json",
        status=202,
        body="",
        adding_headers={"Location": "https://host_name.com/projects/p-id/modelJobs/12/"},
    )
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/modelJobs/12/".format(project_id),
        content_type="application/json",
        status=200,
        body=model_job_json,
    )

    blueprint_id = "e1c7fc29ba2e612a72272324b8a842af"
    retval = project.train(blueprint_id)
    assert retval == "12"


def test_print_project_from_id():
    project = Project("some-project-id")
    print(project)  # checks that method relevant to print works on this (failed in one release)


@responses.activate
def test_all_defaults(project, model_collection_url):
    responses.add(
        responses.POST,
        model_collection_url,
        content_type="application/json",
        status=201,
        body="",
        adding_headers={"Location": "http://host_name.com/projects/p-id/modelJobs/id/"},
    )
    blueprint_id = "e1c7fc29ba2e612a72272324b8a842af"
    model_id = project.train(blueprint_id)
    assert responses.calls[0].request.url == model_collection_url
    payload = request_body_to_json(responses.calls[0].request)
    assert "samplePct" not in payload
    assert "trainingRowCount" not in payload
    assert "id" == model_id


@responses.activate
def test_no_defaults(project, model_collection_url):
    responses.add(
        responses.POST,
        model_collection_url,
        content_type="application/json",
        status=201,
        body="",
        adding_headers={"Location": "http://host_name.com/projects/p-id/modelJobs/id/"},
    )
    blueprint_id = "e1c7fc29ba2e612a72272324b8a842af"
    dataset_id = "5223deadbeefdeadbeef0101"
    source_project_id = "5223deadbeefdeadbeef1234"
    scoring_type = datarobot.SCORING_TYPE.cross_validation
    sample_pct = 44

    project.train(
        blueprint_id,
        featurelist_id=dataset_id,
        source_project_id=source_project_id,
        sample_pct=sample_pct,
        scoring_type=scoring_type,
    )
    assert responses.calls[0].request.url == model_collection_url
    request = request_body_to_json(responses.calls[0].request)
    assert request["blueprintId"] == blueprint_id
    assert request["sourceProjectId"] == source_project_id
    assert request["featurelistId"] == dataset_id
    assert request["samplePct"] == sample_pct
    assert request["scoringType"] == scoring_type
    assert "trainingRowCount" not in request


def test_train_cant_use_both(project):
    blueprint_id = "a-blueprint"
    with pytest.raises(ValueError):
        project.train(blueprint_id, sample_pct=40, training_row_count=100)


@responses.activate
def test_train_by_rowcount_with_bp_id(project, model_collection_url, project_url):
    responses.add(
        responses.POST,
        model_collection_url,
        content_type="application/json",
        status=201,
        body="",
        adding_headers={"Location": "{}/modelJobs/5/".format(project_url)},
    )
    blueprint_id = "a-blueprint-id-hash"
    training_row_count = 50
    project.train(blueprint_id, training_row_count=training_row_count)
    assert responses.calls[0].request.url == model_collection_url
    payload = request_body_to_json(responses.calls[0].request)
    assert payload["blueprintId"] == blueprint_id
    assert payload["trainingRowCount"] == training_row_count
    assert "samplePct" not in payload


@responses.activate
def test_train_by_rowcount_with_trainable(project, model_collection_url, project_url):
    responses.add(
        responses.POST,
        model_collection_url,
        content_type="application/json",
        status=201,
        body="",
        adding_headers={"Location": "{}/modelJobs/5/".format(project_url)},
    )
    blueprint_id = "a-blueprint-hash"
    trainable = Blueprint.from_data(
        {
            "id": blueprint_id,
            "project_id": project.id,
            "model_type": "A fake model",
            "processes": ["Things", "Stuff"],
        }
    )
    training_row_count = 50

    project.train(trainable, training_row_count=training_row_count)
    payload = request_body_to_json(responses.calls[0].request)
    assert payload["blueprintId"] == blueprint_id
    assert payload["trainingRowCount"] == training_row_count
    assert "samplePct" not in payload


@responses.activate
def test_with_trainable_object_ignores_any_source_project_id(project, model_collection_url):

    responses.add(
        responses.POST,
        model_collection_url,
        content_type="application/json",
        status=201,
        body="",
        adding_headers={"Location": "http://pam/api/v2/projects/p-id/models/id/"},
    )
    blueprint_id = "e1c7fc29ba2e612a72272324b8a842af"
    source_project_id = "5223deadbeefdeadbeef1234"

    data = dict(
        id=blueprint_id,
        project_id=source_project_id,
        model_type="Pretend Model",
        processes=["Cowboys", "Aliens"],
    )

    blueprint = Blueprint.from_data(data)

    project.train(blueprint, source_project_id="should-be-ignored")
    assert responses.calls[0].request.url == model_collection_url
    request = request_body_to_json(responses.calls[0].request)
    assert request["blueprintId"] == blueprint_id
    assert request["sourceProjectId"] == source_project_id


MONO_INC_FL_ID = "5ae1afb6962d74625f940991"
MONO_DEC_FL_ID = "5ae1afb6962d74625f940992"
BLUEPRINT_ID = "5a997601962d742269a38dd9"


@pytest.mark.parametrize(
    "blueprint,featurelists",
    [
        (Blueprint(id=BLUEPRINT_ID), (MONO_INC_FL_ID, MONO_DEC_FL_ID)),
        (BLUEPRINT_ID, (MONO_INC_FL_ID, MONO_DEC_FL_ID)),
        (BLUEPRINT_ID, (None, None)),
        (BLUEPRINT_ID, (MONO_INC_FL_ID, None)),
        (BLUEPRINT_ID, (None, MONO_DEC_FL_ID)),
        (BLUEPRINT_ID, (enums.MONOTONICITY_FEATURELIST_DEFAULT, MONO_DEC_FL_ID)),
    ],
)
@responses.activate
def test_monotonicity_blueprint(blueprint, project, featurelists):
    monotonic_increasing_featurelist_id, monotonic_decreasing_featurelist_id = featurelists

    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/models/".format(project.id),
        content_type="application/json",
        status=201,
        body="",
        adding_headers={
            "Location": "https://host_name.com/projects/p-id/5a9975c9962d746034393e42/modelJobs/1/"
        },
    )

    project.train(
        blueprint,
        monotonic_increasing_featurelist_id=monotonic_increasing_featurelist_id,
        monotonic_decreasing_featurelist_id=monotonic_decreasing_featurelist_id,
    )
    payload = request_body_to_json(responses.calls[0].request)
    if monotonic_increasing_featurelist_id is enums.MONOTONICITY_FEATURELIST_DEFAULT:
        assert "monotonicIncreasingFeaturelistId" not in payload
    else:
        assert payload["monotonicIncreasingFeaturelistId"] == monotonic_increasing_featurelist_id

    if monotonic_decreasing_featurelist_id is enums.MONOTONICITY_FEATURELIST_DEFAULT:
        assert "monotonicDecreasingFeaturelistId" not in payload
    else:
        assert payload["monotonicDecreasingFeaturelistId"] == monotonic_decreasing_featurelist_id

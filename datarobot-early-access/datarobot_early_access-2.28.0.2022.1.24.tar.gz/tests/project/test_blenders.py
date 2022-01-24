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

import responses

from datarobot import BlenderModel, ModelJob, Project
from datarobot.enums import BLENDER_METHOD


@responses.activate
def test_blend_return_job_id():
    job_id = 1
    location = "https://host_name.com/projects/p-id/modelJobs/{}/".format(job_id)
    model1 = "57e27abc8e43553e572f8df7"
    model2 = "57e27abc8e43553e572f8df8"
    responses.add(
        responses.POST,
        "https://host_name.com/projects/p-id/blenderModels/",
        status=202,
        body="",
        adding_headers={"Location": location},
    )
    model_job_url = "https://host_name.com/projects/p-id/modelJobs/{}/".format(job_id)
    model_job_data = {
        "status": "inprogress",
        "processes": [],
        "projectId": "p-id",
        "samplePct": 28.349,
        "modelType": "Naive Bayes combiner classifier",
        "featurelistId": "56d8620bccf94e26f37af0a3",
        "modelCategory": "model",
        "blueprintId": "2a1b9ae97fe61880332e196c770c1f9f",
        "isBlocked": False,
        "id": job_id,
    }
    responses.add(
        responses.GET,
        model_job_url,
        status=200,
        body=json.dumps(model_job_data),
        content_type="application/json",
    )
    result = Project("p-id").blend([model1, model2], "AVG")
    assert isinstance(result, ModelJob)
    assert result.id == job_id


@responses.activate
def test_check_blend(project, project_url):
    model1 = "1234deadbeefdeadbeef4321"
    model2 = "feeddeadcafebeef43211234"
    url = "{}blenderModels/blendCheck/".format(project_url)
    response_body = {"blendable": False, "reason": "because I say so"}
    responses.add(responses.POST, url, json=response_body, content_type="application/json")
    result = project.check_blendable([model1, model2], BLENDER_METHOD.AVERAGE)
    assert result.supported is False
    assert result.reason == response_body["reason"]
    assert all(
        substring in result.context
        for substring in ["blendability", model1, model2, BLENDER_METHOD.AVERAGE]
    )


@responses.activate
def test_get_blenders_return_valid_objects(blenders_list_response_json):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/blenderModels/",
        body=blenders_list_response_json,
        status=200,
        content_type="application/json",
    )
    blenders = Project("p-id").get_blenders()
    assert all(isinstance(blender, BlenderModel) for blender in blenders)

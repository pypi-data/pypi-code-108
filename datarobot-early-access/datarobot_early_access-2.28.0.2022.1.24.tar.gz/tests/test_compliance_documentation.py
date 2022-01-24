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
import os

import responses

from datarobot.models import ComplianceDocumentation


@responses.activate
def test_generate(project_id, one_model, job_id):
    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/models/{}/complianceDocs/".format(
            project_id, one_model.id
        ),
        status=202,
        adding_headers={
            "Location": "https://host_name.com/projects/{}/jobs/{}/".format(project_id, job_id),
        },
    )
    stub_job_data = {
        "status": "inprogress",
        "url": "https://host_name.com/projects/{}/modelJobs/{}/".format(project_id, job_id),
        "id": job_id,
        "jobType": "model",
        "isBlocked": False,
        "projectId": project_id,
    }
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/jobs/{}/".format(project_id, job_id),
        status=200,
        body=json.dumps(stub_job_data),
        content_type="application/json",
    )
    doc = ComplianceDocumentation(project_id, one_model.id)
    job = doc.generate()

    assert job.id == int(job_id)
    assert len(responses.calls) == 2
    post_call, get_call = responses.calls
    assert post_call.request.body is None
    assert get_call.request.url.endswith("{}/".format(job_id))


@responses.activate
def test_download(project_id, one_model, tmpdir):
    url = "https://host_name.com/projects/{}/models/{}/complianceDocs/".format(
        project_id, one_model.id
    )
    responses.add(responses.GET, url, body="bytes and shit", status=200, match_querystring=True)
    doc = ComplianceDocumentation(project_id, one_model.id)
    localpath = tmpdir.join("temp.docx")
    doc.download(localpath.strpath)
    assert os.path.isfile(localpath.strpath)
    with open(localpath.strpath) as f:
        contents = f.read()
        assert contents == "bytes and shit"

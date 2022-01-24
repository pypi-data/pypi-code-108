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

from datarobot import enums
from datarobot.models.ruleset import Ruleset


def test_future_proof(ruleset_with_model_server_data):
    Ruleset.from_server_data(dict(ruleset_with_model_server_data, future="new"))


def test_instantiate_with_model(ruleset_with_model_server_data):
    ruleset = Ruleset.from_server_data(ruleset_with_model_server_data)
    assert ruleset.id == ruleset_with_model_server_data["rulesetId"]
    assert ruleset.rule_count == ruleset_with_model_server_data["ruleCount"]
    assert ruleset.score == ruleset_with_model_server_data["score"]
    assert ruleset.project_id == ruleset_with_model_server_data["projectId"]
    assert ruleset.parent_model_id == ruleset_with_model_server_data["parentModelId"]
    assert ruleset.model_id == ruleset_with_model_server_data["modelId"]


def test_instantiate_without_model(ruleset_without_model_server_data):
    ruleset = Ruleset.from_server_data(ruleset_without_model_server_data)
    assert ruleset.id == ruleset_without_model_server_data["rulesetId"]
    assert ruleset.rule_count == ruleset_without_model_server_data["ruleCount"]
    assert ruleset.score == ruleset_without_model_server_data["score"]
    assert ruleset.project_id == ruleset_without_model_server_data["projectId"]
    assert ruleset.parent_model_id == ruleset_without_model_server_data["parentModelId"]
    assert ruleset.model_id is None


@responses.activate
@pytest.mark.usefixtures("prime_model_job_creation_response")
def test_request_model(ruleset_without_model, job_url, prime_model_job_running_server_data):
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(prime_model_job_running_server_data),
        content_type="application/json",
    )
    prime_model_job = ruleset_without_model.request_model()
    assert prime_model_job.job_type == enums.JOB_TYPE.PRIME_MODEL


@responses.activate
@pytest.mark.usefixtures("prime_model_job_creation_response", "prime_model_job_completed_response")
def test_retrieve_request_model_result(ruleset_without_model):
    prime_model_job = ruleset_without_model.request_model()
    prime_model = prime_model_job.get_result_when_complete()
    assert prime_model.parent_model_id == ruleset_without_model.parent_model_id
    assert prime_model.ruleset.model_id == prime_model.id


def test_request_model_already_run(ruleset_with_model):
    with pytest.raises(ValueError):
        ruleset_with_model.request_model()

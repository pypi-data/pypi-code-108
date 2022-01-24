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

from datarobot import Model
from datarobot.errors import ClientError
from datarobot.models.pareto_front import ParetoFront, Solution


@pytest.fixture
def pareto_front_data(project_id):
    return {
        "project_id": project_id,
        "error_metric": "Log Loss Error",
        "hyperparameters": {},
        "target_type": "Binary",
        "solutions": [
            {
                "eureqa_solution_id": "5b2940f202d5abf17ddca9f8",
                "complexity": 1,
                "error": 0.6568885703145153,
                "expression": "target = 0",
                "expression_annotated": "target = 0",
                "best_model": False,
            },
            {
                "eureqa_solution_id": "5b2940f202d5abf17ddca9f9",
                "complexity": 2,
                "error": 0.6463236186153043,
                "expression": "target = 0",
                "expression_annotated": "target = 0",
                "best_model": False,
            },
            {
                "eureqa_solution_id": "5b2940f202d5abf17ddca9fa",
                "complexity": 3,
                "error": None,
                "expression": "target = 0",
                "expression_annotated": "target = 0",
                "best_model": False,
            },
            {
                "eureqa_solution_id": "5b2940f202d5abf17ddca9fb",
                "complexity": 4,
                "error": 0.6341910672553971,
                "expression": "target = 0",
                "expression_annotated": "target = 0",
                "best_model": False,
            },
            {
                "eureqa_solution_id": "5b29406c6523cd0665685a8d",
                "complexity": 5,
                "error": 0.6327990044770845,
                "expression": "target = 0",
                "expression_annotated": "target = 0",
                "best_model": True,
            },
        ],
    }


@pytest.fixture
def server_pareto_front_data(project_id):
    return {
        "projectId": project_id,
        "errorMetric": "Log Loss Error",
        "hyperparameters": {"random stuff": True, "other random stuff": "look ma, no trafaret!"},
        "targetType": "Binary",
        "solutions": [
            {
                "eureqaSolutionId": "5b2940f202d5abf17ddca9f8",
                "complexity": 1,
                "error": 0.6568885703145153,
                "expression": "target = 0",
                "expressionAnnotated": "target = 0",
                "bestModel": False,
            },
            {
                "eureqaSolutionId": "5b2940f202d5abf17ddca9f9",
                "complexity": 2,
                "error": 0.6463236186153043,
                "expression": "target = 0",
                "expressionAnnotated": "target = 0",
                "bestModel": False,
            },
            {
                "eureqaSolutionId": "5b2940f202d5abf17ddca9fa",
                "complexity": 3,
                "error": None,
                "expression": "target = 0",
                "expressionAnnotated": "target = 0",
                "bestModel": False,
            },
            {
                "eureqaSolutionId": "5b2940f202d5abf17ddca9fb",
                "complexity": 4,
                "error": 0.6341910672553971,
                "expression": "target = 0",
                "expressionAnnotated": "target = 0",
                "bestModel": False,
            },
            {
                "eureqaSolutionId": "5b29406c6523cd0665685a8d",
                "complexity": 5,
                "error": 0.6327990044770845,
                "expression": "target = 0",
                "expressionAnnotated": "target = 0",
                "bestModel": True,
            },
        ],
    }


def test_instantiation(server_pareto_front_data, project_id):
    pareto_front = ParetoFront.from_server_data(server_pareto_front_data)

    assert pareto_front.project_id == project_id
    assert pareto_front.error_metric == "Log Loss Error"
    assert pareto_front.hyperparameters == {
        "random stuff": True,
        "other random stuff": "look ma, no trafaret!",
    }
    assert pareto_front.target_type == "Binary"


def test_future_proof(server_pareto_front_data, project_id):
    data_with_future_keys = dict(server_pareto_front_data, new_key="amazing new key")
    data_with_future_keys["solutions"][0]["new_key"] = "amazing new key"
    pareto_front = ParetoFront.from_server_data(data_with_future_keys)

    assert pareto_front.project_id == project_id
    assert pareto_front.error_metric == "Log Loss Error"
    assert pareto_front.hyperparameters == {
        "random stuff": True,
        "other random stuff": "look ma, no trafaret!",
    }
    assert pareto_front.target_type == "Binary"


@pytest.fixture
def pareto_front_data_url(project_id, model_id):
    return "https://host_name.com/projects/{}/eureqaModels/{}/".format(project_id, model_id)


@responses.activate
def test_get_pareto_front(
    server_pareto_front_data, pareto_front_data, pareto_front_data_url, project_id, model_id
):
    responses.add(
        responses.GET,
        pareto_front_data_url,
        status=200,
        content_type="application/json",
        body=json.dumps(server_pareto_front_data),
    )
    model = Model(id=model_id, project_id=project_id)
    pf = model.get_pareto_front()
    mock_data = pareto_front_data

    assert pf.project_id == project_id
    assert pf.error_metric == "Log Loss Error"
    assert pf.hyperparameters == {
        "random stuff": True,
        "other random stuff": "look ma, no trafaret!",
    }
    assert pf.target_type == "Binary"

    for i in range(0, 5):
        assert (
            pf.solutions[i].__dict__
            == Solution(project_id=project_id, **mock_data["solutions"][i]).__dict__
        )


@responses.activate
def test_non_eureqa_model(pareto_front_data_url, project_id, model_id):
    responses.add(
        responses.GET,
        pareto_front_data_url,
        status=404,
        content_type="application/json",
        body=json.dumps({}),
    )
    model = Model(id=model_id, project_id=project_id)

    with pytest.raises(ClientError):
        model.get_pareto_front()

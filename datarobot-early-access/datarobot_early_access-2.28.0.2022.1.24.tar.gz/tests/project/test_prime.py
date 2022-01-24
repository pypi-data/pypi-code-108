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

from datarobot.models.model import Model
from datarobot.models.ruleset import Ruleset


@responses.activate
def test_list_prime_models(
    project_url, project, prime_model_server_data, ruleset_with_model_server_data
):
    response_data = {"count": 1, "previous": None, "next": None, "data": [prime_model_server_data]}
    responses.add(
        responses.GET, "{}primeModels/".format(project_url), body=json.dumps(response_data)
    )

    prime_models = project.get_prime_models()

    assert len(prime_models) == 1
    expected_model = Model.from_server_data(prime_model_server_data)
    prime_model = prime_models[0]
    assert prime_model.id == expected_model.id
    assert prime_model.model_category == expected_model.model_category
    assert prime_model.model_type == expected_model.model_type

    expected_ruleset = Ruleset.from_server_data(ruleset_with_model_server_data)
    assert prime_model.ruleset.id == expected_ruleset.id
    assert prime_model.parent_model_id == expected_ruleset.parent_model_id

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

from numpy import isclose
import pytest
import responses

from datarobot import Model
from datarobot.models import ModelParameters


@pytest.fixture
def model_parameters_data():
    return {
        "parameters": [
            {"name": u"Intercept", "value": 1},
            {"name": u"Link function", "value": u"logit"},
        ],
        "derivedFeatures": [
            {
                "coefficient": -0.015,
                "originalFeature": u"A1Cresult",
                "derivedFeature": u"A1Cresult->7",
                "type": u"CAT",
                "transformations": [{"name": u"One-hot", "value": u"'>7'"}],
            },
            {
                "coefficient": 0.014,
                "originalFeature": u"A1Cresult",
                "derivedFeature": u"A1Cresult->8",
                "type": u"CAT",
                "transformations": [{"name": u"One-hot", "value": u"'>8'"}],
            },
            {
                "coefficient": -0.133,
                "originalFeature": u"A1Cresult",
                "derivedFeature": u"A1Cresult-Norm",
                "type": u"CAT",
                "transformations": [{"name": u"One-hot", "value": u"'Norm'"}],
            },
            {
                "coefficient": 0.40552547397855254,
                "type": u"NUM",
                "derivedFeature": u"STANDARDIZED_revol_util",
                "originalFeature": u"revol_util",
                "transformations": [
                    {"name": u"Missing imputation", "value": 47.6},
                    {"name": u"Standardize", "value": u"(47.781034375,27.955074618)"},
                ],
            },
        ],
    }


@pytest.fixture
def freq_sev_model_parameters_data(model_parameters_data):
    freq_sev_data = model_parameters_data.copy()
    for derived_feature in freq_sev_data["derivedFeatures"]:
        derived_feature["stageCoefficients"] = [
            {"stage": "frequency", "coefficient": 1.0},
            {"stage": "severity", "coefficient": 2.0},
        ]
    return freq_sev_data


@pytest.fixture
def broken_model_parameters_data(model_parameters_data):
    broken_data = model_parameters_data.copy()
    bad_data = {"some_broken_field": "some_broken_value"}
    broken_data["parameters"][0].update(bad_data)
    broken_data["derivedFeatures"][0].update(bad_data)
    broken_data.update(bad_data)
    return broken_data


@pytest.fixture
def model_parameters_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/parameters/".format(project_id, model_id)


@responses.activate
def test_instantiation(model_parameters_url, model_parameters_data, project_id, model_id):
    responses.add(
        responses.GET,
        model_parameters_url,
        status=200,
        content_type="application/json",
        body=json.dumps(model_parameters_data),
    )

    mp = ModelParameters.get(project_id, model_id)

    params = mp.parameters
    expected_params = model_parameters_data["parameters"]
    for i in range(len(params)):
        assert params[i]["name"] == expected_params[i]["name"]
        assert params[i]["value"] == expected_params[i]["value"]

    derived = mp.derived_features
    expected_derived = model_parameters_data["derivedFeatures"]
    for i in range(len(derived)):
        assert isclose(derived[i]["coefficient"], expected_derived[i]["coefficient"])
        assert derived[i]["original_feature"] == expected_derived[i]["originalFeature"]
        assert derived[i]["derived_feature"] == expected_derived[i]["derivedFeature"]
        assert derived[i]["type"] == expected_derived[i]["type"]
        assert derived[i]["transformations"] == expected_derived[i]["transformations"]


@responses.activate
def test_freq_sev_parameters(
    model_parameters_url, freq_sev_model_parameters_data, project_id, model_id
):
    responses.add(
        responses.GET,
        model_parameters_url,
        status=200,
        content_type="application/json",
        body=json.dumps(freq_sev_model_parameters_data),
    )

    mp = ModelParameters.get(project_id, model_id)

    derived_features = mp.derived_features
    expected_derived_features = freq_sev_model_parameters_data["derivedFeatures"]
    for i in range(len(derived_features)):
        assert len(derived_features[i]["stage_coefficients"]) == 2
        for j in range(len(derived_features[i]["stage_coefficients"])):
            assert isclose(
                derived_features[i]["stage_coefficients"][j]["coefficient"],
                expected_derived_features[i]["stageCoefficients"][j]["coefficient"],
            )


@responses.activate
def test_future_proof(model_parameters_url, broken_model_parameters_data, project_id, model_id):
    responses.add(
        responses.GET,
        model_parameters_url,
        status=200,
        content_type="application/json",
        body=json.dumps(broken_model_parameters_data),
    )

    mp = ModelParameters.get(project_id, model_id)

    assert len(mp.parameters) == 2
    for i in range(len(mp.parameters)):
        assert "some_broken_field" not in mp.parameters[i]

    assert len(mp.derived_features) == 4
    for i in range(len(mp.derived_features)):
        assert "some_broken_field" not in mp.derived_features[i]


@responses.activate
def test_get_parameters(model_parameters_url, model_parameters_data, project_id, model_id):
    responses.add(
        responses.GET,
        model_parameters_url,
        status=200,
        content_type="application/json",
        body=json.dumps(model_parameters_data),
    )

    mp = ModelParameters.get(project_id, model_id)
    model = Model(id=model_id, project_id=project_id)
    assert mp.parameters == model.get_parameters().parameters

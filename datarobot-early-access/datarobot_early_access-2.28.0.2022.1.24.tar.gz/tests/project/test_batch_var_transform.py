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
from collections import OrderedDict

import mock
import pytest
import responses

from datarobot.enums import VARIABLE_TYPE_TRANSFORM
from tests.utils import request_body_to_json


@pytest.fixture
def batch_type_transform_create_url(unittest_endpoint, project_id):
    return "{}/projects/{}/batchTypeTransformFeatures/".format(unittest_endpoint, project_id)


@pytest.fixture
def batch_type_transform_create_response(batch_type_transform_create_url, async_url):
    responses.add(
        responses.POST,
        batch_type_transform_create_url,
        status=202,
        body="",
        adding_headers={"Location": async_url},
    )
    responses.add(
        responses.GET, async_url, status=303, body="", adding_headers={"Location": "/features/"}
    )


@pytest.mark.parametrize(
    "exception, patch",
    [(TypeError, {"parent_names": []}), (ValueError, {"variable_type": "wrong"})],
)
def test_batch_var_type_transform_arguments_validation(project, exception, patch):
    args = OrderedDict(
        {
            "parent_names": ["f1"],
            "variable_type": VARIABLE_TYPE_TRANSFORM.TEXT,
            "prefix": "prefix",
            "suffix": "suffix",
        }
    )

    args.update(patch)

    with pytest.raises(exception):
        project.batch_features_type_transform(
            parent_names=args["parent_names"],
            variable_type=args["variable_type"],
            prefix=args["prefix"],
            suffix=args["suffix"],
        )


@responses.activate
@pytest.mark.usefixtures("batch_type_transform_create_response")
def test_batch_var_type_transform(project):
    args = [
        ["f1", "f2"],
        VARIABLE_TYPE_TRANSFORM.NUMERIC,
        "prefix",
    ]

    with mock.patch.object(project, "get_features") as get_features_mock:
        features = project.batch_features_type_transform(*args)
        assert get_features_mock.called_once
        assert get_features_mock.return_value is features

    payload = request_body_to_json(responses.calls[0].request)

    assert payload["parentNames"] == ["f1", "f2"]
    assert payload["variableType"] == VARIABLE_TYPE_TRANSFORM.NUMERIC
    assert payload["prefix"] == "prefix"

    assert "suffix" not in payload


@responses.activate
@pytest.mark.usefixtures("batch_type_transform_create_response")
@pytest.mark.usefixtures("known_warning")
def test_batch_var_type_transform_categorical(project):
    args = [
        ["f1", "f2"],
        VARIABLE_TYPE_TRANSFORM.CATEGORICAL,
        "prefix",
    ]

    with mock.patch.object(project, "get_features") as get_features_mock:
        features = project.batch_features_type_transform(*args)
        assert get_features_mock.called_once
        assert get_features_mock.return_value is features

    payload = request_body_to_json(responses.calls[0].request)

    assert payload["parentNames"] == ["f1", "f2"]
    assert payload["variableType"] == VARIABLE_TYPE_TRANSFORM.CATEGORICAL
    assert payload["prefix"] == "prefix"

    assert "suffix" not in payload

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
from tempfile import NamedTemporaryFile

import pytest
import responses
import six.moves.urllib.parse as urlparse

from datarobot import Deployment
from tests.utils import request_body_to_json


@pytest.fixture
def scoring_code_data(deployment_data):
    return b"scoring_code_jar_file_data"


@pytest.fixture
def scoring_code_retrieve_response(unittest_endpoint, deployment_data, scoring_code_data):
    url = "{}/deployments/{}/scoringCode/".format(unittest_endpoint, deployment_data["id"])
    responses.add(
        responses.GET,
        url,
        status=200,
        content_type="application/java-archive",
        body=scoring_code_data,
    )


@pytest.fixture
def scoring_code_build_response(unittest_endpoint, deployment_data):
    status_url = "{}/status_url".format(unittest_endpoint)
    scoring_code_build_url = "{}/deployments/{}/scoringCodeBuilds/".format(
        unittest_endpoint, deployment_data["id"]
    )
    scoring_code_retrieve_url = "{}/deployments/{}/scoringCode/".format(
        unittest_endpoint, deployment_data["id"]
    )

    responses.add(
        responses.GET, status_url, headers={"Location": scoring_code_retrieve_url}, status=303
    )
    responses.add(
        responses.POST, scoring_code_build_url, headers={"Location": status_url}, status=202
    )


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "scoring_code_retrieve_response")
@pytest.mark.parametrize(
    "source_code, include_agent, include_prediction_explanations",
    [(True, False, False), (False, False, False)],
)
def test_download_scoring_code_without_build(
    deployment_data, scoring_code_data, source_code, include_agent, include_prediction_explanations
):
    """Test download_scoring_code that does not require building."""

    with NamedTemporaryFile() as file:
        deployment = Deployment.get(deployment_data["id"])
        deployment.download_scoring_code(
            file.name,
            source_code=source_code,
            include_agent=include_agent,
            include_prediction_explanations=include_prediction_explanations,
        )
        params_dict = dict(
            urlparse.parse_qsl(urlparse.urlsplit(responses.calls[1].request.path_url).query)
        )
        assert file.read() == scoring_code_data
        assert params_dict["sourceCode"] == str(source_code)
        assert params_dict["includeAgent"] == str(include_agent)
        assert params_dict["includePredictionExplanations"] == str(include_prediction_explanations)


@responses.activate
@pytest.mark.usefixtures(
    "deployment_get_response", "scoring_code_build_response", "scoring_code_retrieve_response"
)
@pytest.mark.parametrize(
    "include_agent, include_prediction_explanations", [(True, True), (False, True), (True, False)],
)
def test_download_scoring_code_with_build(
    deployment_data, scoring_code_data, include_agent, include_prediction_explanations
):
    """Test download_scoring_code that requires building first."""

    with NamedTemporaryFile() as file:
        deployment = Deployment.get(deployment_data["id"])
        deployment.download_scoring_code(
            file.name,
            include_agent=include_agent,
            include_prediction_explanations=include_prediction_explanations,
        )
        response = request_body_to_json(responses.calls[1].request)
        assert file.read() == scoring_code_data
        assert response["includeAgent"] == include_agent
        assert response["includePredictionExplanations"] == include_prediction_explanations

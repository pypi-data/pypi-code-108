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
import os

import pytest
import responses

from datarobot import Model
from datarobot.errors import ClientError


@pytest.fixture
def scoring_code_file_contents():
    # Just huge string bigger then 1MB chunk size
    return "some_random_file_contents" * 1000000


@pytest.fixture
def local_jar_filename(tmpdir):
    return str(tmpdir.join("temp.jar"))


@responses.activate
def test_positive_case(project_id, model_id, scoring_code_file_contents, local_jar_filename):
    url = "https://host_name.com/projects/{}/models/{}/scoringCode/?sourceCode=false".format(
        project_id, model_id
    )
    responses.add(
        responses.GET, url, body=scoring_code_file_contents, status=200, match_querystring=True
    )
    model = Model(project_id=project_id, id=model_id)
    model.download_scoring_code(local_jar_filename)
    assert os.path.isfile(local_jar_filename)
    with open(local_jar_filename) as f:
        contents = f.read()
        assert contents == scoring_code_file_contents
    os.unlink(local_jar_filename)
    assert not os.path.isfile(local_jar_filename)


@responses.activate
def test_negative_case(project_id, model_id, local_jar_filename):
    url = "https://host_name.com/projects/{}/models/{}/scoringCode/?sourceCode=false".format(
        project_id, model_id
    )
    error_message = "some error"
    responses.add(
        responses.GET, url, json={"message": error_message}, status=404, match_querystring=True
    )
    model = Model(project_id=project_id, id=model_id)
    with pytest.raises(ClientError) as exc_info:
        model.download_scoring_code(local_jar_filename)
    assert not os.path.isfile(local_jar_filename)
    assert error_message in str(exc_info.value)

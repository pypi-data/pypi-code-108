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

from datarobot.models.prime_file import PrimeFile


@pytest.fixture
def downloaded_code():
    return "Copyright DataRobot Code\ndef do_a_thing():\n    return"


@pytest.fixture
def download_response(project_url, prime_file, downloaded_code):
    url = "{}primeFiles/{}/download/".format(project_url, prime_file.id)
    responses.add(responses.GET, url, body=downloaded_code)


def test_future_proof(prime_file_server_data):
    PrimeFile.from_server_data(dict(prime_file_server_data, future="new"))


@responses.activate
def test_get_prime_file(project_url, project_id, prime_file_server_data):
    url = "{}primeFiles/{}/".format(project_url, prime_file_server_data["id"])
    responses.add(
        responses.GET, url, body=json.dumps(prime_file_server_data), content_type="application/json"
    )
    prime_file = PrimeFile.get(project_id, prime_file_server_data["id"])
    assert prime_file.id == prime_file_server_data["id"]
    assert prime_file.project_id == project_id
    assert prime_file.parent_model_id == prime_file_server_data["parentModelId"]
    assert prime_file.model_id == prime_file_server_data["modelId"]
    assert prime_file.ruleset_id == prime_file_server_data["rulesetId"]
    assert prime_file.language == prime_file_server_data["language"]
    assert prime_file.is_valid == prime_file_server_data["isValid"]


@responses.activate
@pytest.mark.usefixtures("download_response")
def test_download(temporary_file, prime_file, downloaded_code):
    prime_file.download(temporary_file)
    with open(temporary_file) as in_f:
        saved_code = in_f.read()
    assert saved_code == downloaded_code

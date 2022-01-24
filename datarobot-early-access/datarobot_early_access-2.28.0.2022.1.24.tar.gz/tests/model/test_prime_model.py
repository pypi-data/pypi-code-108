# coding: utf-8
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
from datetime import datetime
import json

import dateutil
import pytest
import responses

from datarobot.enums import JOB_TYPE
from datarobot.models.model import PrimeModel
from datarobot.models.prime_file import PrimeFile
from datarobot.models.ruleset import Ruleset
from tests.utils import assert_equal_py2, assert_equal_py3


@responses.activate
def test_get_prime_model(
    project_url, project_id, prime_model_id, prime_model_server_data, ruleset_with_model_server_data
):
    responses.add(
        responses.GET,
        "{}primeModels/{}/".format(project_url, prime_model_id),
        body=json.dumps(prime_model_server_data),
    )
    prime_model = PrimeModel.get(project_id, prime_model_id)

    assert prime_model.id == prime_model_server_data["id"]
    assert prime_model.model_type == prime_model_server_data["modelType"]
    assert prime_model.parent_model_id == ruleset_with_model_server_data["parentModelId"]
    assert prime_model.ruleset.score == ruleset_with_model_server_data["score"]


@responses.activate
@pytest.mark.usefixtures("client", "approximate_job_creation_response")
def test_approximate(one_model, job_url, approximate_job_running_server_data):
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(approximate_job_running_server_data),
        content_type="application/json",
    )
    approx_job = one_model.request_approximation()
    assert approx_job.job_type == JOB_TYPE.PRIME_RULESETS


@pytest.fixture
def datetime_prime_data(datetime_model_data, prime_data):
    modified_data = dict(prime_data)
    modified_data.update(datetime_model_data)
    modified_data.pop("sample_pct")
    return modified_data


def test_datetime_prime_model(datetime_prime_data):
    mod = PrimeModel.from_data(datetime_prime_data)
    dt = mod.training_start_date
    assert dt.tzinfo == dateutil.tz.tzutc()
    assert isinstance(mod.training_end_date, datetime)
    assert mod.training_row_count is None
    assert mod.training_duration is None


@responses.activate
@pytest.mark.usefixtures(
    "client", "approximate_job_creation_response", "approximate_completed_response"
)
def test_retrieve_approximate_result(one_model, prime_model_id):
    approx_job = one_model.request_approximation()
    rulesets = approx_job.get_result_when_complete()
    assert rulesets
    assert {prime_model_id, None} == {ruleset.model_id for ruleset in rulesets}
    for ruleset in rulesets:
        assert isinstance(ruleset, Ruleset)
        assert ruleset.parent_model_id == one_model.id


@responses.activate
def test_check_primeable(project_url, one_model):
    response_data = {"canMakePrime": True, "message": "OK", "messageId": 0}
    url = "{}models/{}/primeInfo/".format(project_url, one_model.id)
    responses.add(
        responses.GET, url, body=json.dumps(response_data), content_type="application/json"
    )
    eligibility = one_model.get_prime_eligibility()
    assert eligibility == {"can_make_prime": True, "message": "OK"}


@responses.activate
def test_check_primeable_future_proof(project_url, one_model):
    response_data = {"canMakePrime": True, "message": "OK", "messageId": 0, "future": "new"}
    url = "{}models/{}/primeInfo/".format(project_url, one_model.id)
    responses.add(
        responses.GET, url, body=json.dumps(response_data), content_type="application/json"
    )
    eligibility = one_model.get_prime_eligibility()
    assert eligibility == {"can_make_prime": True, "message": "OK"}


@responses.activate
def test_list_rulesets(
    project_url,
    model_id,
    prime_model_id,
    one_model,
    ruleset_with_model_server_data,
    ruleset_without_model_server_data,
):
    response_data = [ruleset_with_model_server_data, ruleset_without_model_server_data]
    responses.add(
        responses.GET,
        "{}models/{}/primeRulesets/".format(project_url, model_id),
        body=json.dumps(response_data),
    )
    rulesets = one_model.get_rulesets()

    assert len(rulesets) == 2
    ruleset_models = {ruleset.model_id for ruleset in rulesets}
    assert {prime_model_id, None} == ruleset_models


def test_future_proof(prime_model_server_data):
    future_data = dict(prime_model_server_data, future="new")
    PrimeModel.from_server_data(future_data)


@responses.activate
@pytest.mark.usefixtures("client", "prime_validation_job_creation_response")
def test_validate(prime_model, job_url, prime_validation_job_running_server_data):
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(prime_validation_job_running_server_data),
        content_type="application/json",
    )
    validate_job = prime_model.request_download_validation("Python")
    assert validate_job.job_type == JOB_TYPE.PRIME_VALIDATION


@responses.activate
@pytest.mark.usefixtures(
    "client", "prime_validation_job_creation_response", "prime_validation_job_completed_response"
)
def test_retrieve_validate_result(prime_model):
    validate_job = prime_model.request_download_validation("Python")
    prime_file = validate_job.get_result_when_complete()
    assert isinstance(prime_file, PrimeFile)
    assert prime_file.parent_model_id == prime_model.parent_model_id
    assert prime_file.language == "Python"


class TestRepr(object):
    """Tests of method PrimeModel.__repr__"""

    @pytest.fixture
    def kwargs(self):
        """Required parameters of PrimeModel that don't affect the tests"""
        return {
            "ruleset_id": 1,
            "rule_count": 1,
            "score": 1.0,
            "parent_model_id": "58668f2fbf36cd0183a0617a",
            "project_id": "58668f44bf36cd0183a0617b",
        }

    def test_model_type_str(self, kwargs):
        # when both model_type and id are set
        frozen_model = PrimeModel(id="58668cb5bf36cd77a5d8056c", model_type="model_type", **kwargs)
        # then repr contains only model_type
        assert repr(frozen_model) == "PrimeModel('model_type')"

    def test_model_type_unicode(self, kwargs):
        # when both model_type and id are set
        # and model_type contains non-ascii characters
        frozen_model = PrimeModel(id="58668cb5bf36cd77a5d8056c", model_type=u"тайп", **kwargs)
        # then repr is an ascii string containing only model_type
        assert_equal_py2(repr(frozen_model), "PrimeModel(u'\\u0442\\u0430\\u0439\\u043f')")
        assert_equal_py3(repr(frozen_model), "PrimeModel('тайп')")

    def test_id(self, kwargs):
        # when id is set and model_type is missing
        frozen_model = PrimeModel(id="58668cb5bf36cd77a5d8056c", **kwargs)
        # then repr contains id
        assert repr(frozen_model) == "PrimeModel('58668cb5bf36cd77a5d8056c')"

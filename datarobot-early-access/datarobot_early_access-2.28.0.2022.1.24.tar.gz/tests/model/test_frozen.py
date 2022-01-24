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

import dateutil
import pytest
import responses

from datarobot import FrozenModel
from tests.utils import assert_equal_py2, assert_equal_py3


@responses.activate
def test_frozen_model_get_returns_valid_data(frozen_json, one_frozen):
    url = "https://host_name.com/projects/p-id/frozenModels/{}/".format(one_frozen.id)
    responses.add(responses.GET, url, body=frozen_json, status=200, content_type="application/json")
    frozen = FrozenModel.get("p-id", one_frozen.id)
    assert isinstance(frozen, FrozenModel)
    assert frozen.id == one_frozen.id
    assert frozen.parent_model_id == one_frozen.parent_model_id
    assert isinstance(frozen.model_number, int)


@responses.activate
@pytest.mark.parametrize(
    "sample_pct,training_row_count", [(None, None), (98.98, None), (None, 1000)]
)
def test_request_frozen_model(
    one_model, project_url, frozen_model_job_completed_server_data, sample_pct, training_row_count
):
    frozen_models_url = "{}frozenModels/".format(project_url)
    job_url = "{}modelJobs/{}/".format(project_url, frozen_model_job_completed_server_data["id"])
    finished_freeze_url = "{}/12344321beefcafe43211234/".format(frozen_models_url)

    responses.add(
        responses.POST,
        frozen_models_url,
        body="",
        status=202,
        content_type="application/json",
        adding_headers={"Location": job_url},
    )
    responses.add(
        responses.GET,
        job_url,
        json=frozen_model_job_completed_server_data,
        status=303,
        adding_headers={"Location": finished_freeze_url},
    )
    if sample_pct:
        model_job = one_model.request_frozen_model(sample_pct=sample_pct)
    elif training_row_count:
        model_job = one_model.request_frozen_model(training_row_count=training_row_count)
    else:
        model_job = one_model.request_frozen_model()
    assert model_job.id == int(frozen_model_job_completed_server_data["id"])


@pytest.fixture
def datetime_frozen_data(datetime_model_data, frozen_data):
    modified_data = dict(frozen_data)
    modified_data.update(datetime_model_data)
    modified_data.pop("sample_pct")
    return modified_data


def test_datetime_frozen_model(datetime_frozen_data):
    mod = FrozenModel.from_data(datetime_frozen_data)
    dt = mod.training_start_date
    assert dt.tzinfo == dateutil.tz.tzutc()
    assert isinstance(mod.training_end_date, datetime)
    assert mod.training_row_count is None
    assert mod.training_duration is None


class TestRepr(object):
    """Tests of method FrozenModel.__repr__"""

    def test_model_type_str(self):
        # when both model_type and id are set
        frozen_model = FrozenModel(id="id", model_type="model_type")
        # then repr contains only model_type
        assert repr(frozen_model) == "FrozenModel('model_type')"

    def test_model_type_unicode(self):
        # when model_type contains non-ascii characters
        frozen_model = FrozenModel(model_type=u"тайп")
        # then repr is an ascii string
        assert_equal_py2(repr(frozen_model), "FrozenModel(u'\\u0442\\u0430\\u0439\\u043f')")
        assert_equal_py3(repr(frozen_model), "FrozenModel('тайп')")

    def test_id(self):
        # when id is set and model_type is missing
        frozen_model = FrozenModel(id="58668cb5bf36cd77a5d8056c")
        # then repr contains id
        assert repr(frozen_model) == "FrozenModel('58668cb5bf36cd77a5d8056c')"

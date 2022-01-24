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

from datarobot import BlenderModel


@responses.activate
def test_blender_model_get_return_valid_data(blender_json, one_blender):
    url = "https://host_name.com/projects/p-id/blenderModels/{}/".format(one_blender.id)
    responses.add(
        responses.GET, url, body=blender_json, status=200, content_type="application/json"
    )
    blender = BlenderModel.get("p-id", one_blender.id)
    assert isinstance(blender, BlenderModel)
    assert blender.id == one_blender.id
    assert blender.model_ids == one_blender.model_ids
    assert blender.blender_method == one_blender.blender_method
    assert isinstance(blender.model_number, int)


@pytest.fixture
def datetime_blender_data(datetime_model_data, blender_data):
    modified_data = dict(blender_data)
    modified_data.update(datetime_model_data)
    modified_data.pop("sample_pct")
    return modified_data


def test_datetime_blender_model(datetime_blender_data):
    mod = BlenderModel.from_data(datetime_blender_data)
    dt = mod.training_start_date
    assert dt.tzinfo == dateutil.tz.tzutc()
    assert isinstance(mod.training_end_date, datetime)
    assert mod.training_row_count is None
    assert mod.training_duration is None

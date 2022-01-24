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
import json

import pytest
import responses

from datarobot.errors import ClientError
from datarobot.helpers import DatetimePartitioning
from datarobot.helpers.partitioning_methods import Backtest
from datarobot.models import ExternalBaselineValidationInfo


@pytest.fixture()
def get_validation_info_url(project):
    return (
        "https://host_name.com/projects/{pid}/externalTimeSeriesBaselineDataValidationJobs/1234/"
    ).format(pid=project.id)


@pytest.fixture
def datetime_partitioning(project):
    return DatetimePartitioning(
        project_id=project.id,
        datetime_partition_column="Date",
        multiseries_id_columns=["Store"],
        forecast_window_start=1,
        forecast_window_end=7,
        holdout_start_date="2014-04-09 00:00:00",
        holdout_end_date="2014-06-15 00:00:00",
        backtests=[
            Backtest(
                validation_start_date="2014-02-01 00:00:00",
                validation_end_date="2014-04-09 00:00:00",
            ),
            Backtest(
                validation_start_date="2013-11-26 00:00:00",
                validation_end_date="2014-02-01 00:00:00",
            ),
        ],
    )


@pytest.fixture
def validate_baseline_payload(datetime_partitioning):
    catalog_version_id = "611c774a36e4bc0388355c03"
    target = "Sales"
    backtests = datetime_partitioning.backtests
    return {
        "catalog_version_id": catalog_version_id,
        "target": target,
        "datetime_partition_column": datetime_partitioning.datetime_partition_column,
        "forecast_window_start": datetime_partitioning.forecast_window_start,
        "forecast_window_end": datetime_partitioning.forecast_window_end,
        "holdout_start_date": datetime_partitioning.holdout_start_date,
        "holdout_end_date": datetime_partitioning.holdout_end_date,
        "backtests": [
            {
                "validation_start_date": backtests[0].validation_start_date,
                "validation_end_date": backtests[0].validation_end_date,
            },
            {
                "validation_start_date": backtests[1].validation_start_date,
                "validation_end_date": backtests[1].validation_end_date,
            },
        ],
        "multiseries_id_columns": datetime_partitioning.multiseries_id_columns,
    }


@pytest.fixture
def validate_external_time_series_baseline_response(
    project, validate_baseline_payload, get_validation_info_url
):
    post_url = (
        "https://host_name.com/projects/{pid}/externalTimeSeriesBaselineDataValidationJobs/"
    ).format(pid=project.id)
    async_url = "https://host_name.com/status/status-id/"

    get_body = validate_baseline_payload.copy()
    get_body.update(
        {
            "project_id": project.id,
            "baseline_validation_job_id": "1234",
            "is_external_baseline_dataset_valid": True,
        }
    )

    responses.add(
        responses.POST,
        post_url,
        body=json.dumps(validate_baseline_payload),
        status=202,
        adding_headers={"Location": async_url},
    )
    responses.add(
        responses.GET,
        async_url,
        status=303,
        body="",
        content_type="application/json",
        adding_headers={"Location": get_validation_info_url},
    )
    responses.add(
        responses.GET,
        get_validation_info_url,
        status=200,
        body=json.dumps(get_body),
        content_type="application/json",
    )


@pytest.fixture()
def validation_info_not_found_response(get_validation_info_url):
    responses.add(
        responses.GET,
        get_validation_info_url,
        status=404,
        content_type="application/json",
        body=json.dumps({"message": "External time series validation job not found."}),
    )


@responses.activate
@pytest.mark.usefixtures("validation_info_not_found_response")
def test_retrieve_validation_info_not_found(project):
    with pytest.raises(ClientError):
        ExternalBaselineValidationInfo.get(project.id, validation_job_id="1234")


@responses.activate
@pytest.mark.usefixtures("validate_external_time_series_baseline_response")
def test_project_validate_external_time_series_baseline(
    project, datetime_partitioning, validate_baseline_payload
):
    validation_info = project.validate_external_time_series_baseline(
        catalog_version_id=validate_baseline_payload["catalog_version_id"],
        target=validate_baseline_payload["target"],
        datetime_partitioning=datetime_partitioning,
    )
    assert validation_info.baseline_validation_job_id == "1234"
    assert validation_info.project_id == project.id
    assert validation_info.is_external_baseline_dataset_valid is True
    assert validation_info.message is None

    keys_to_check = [
        "catalog_version_id",
        "target",
        "datetime_partition_column",
        "multiseries_id_columns",
        "holdout_start_date",
        "holdout_end_date",
        "backtests",
        "forecast_window_start",
        "forecast_window_end",
    ]
    for key in keys_to_check:
        assert getattr(validation_info, key) == validate_baseline_payload[key]

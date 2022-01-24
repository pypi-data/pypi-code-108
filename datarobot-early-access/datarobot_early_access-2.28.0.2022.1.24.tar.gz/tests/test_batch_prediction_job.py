# -*- encoding: utf-8 -*-
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
import datetime
import io
import json
import threading
import time

import dateutil
import mock
import pandas as pd
import pytest
import responses
import trafaret as t

from datarobot import BatchPredictionJob, Credential
from datarobot.models import Dataset


@pytest.fixture
def batch_prediction_jobs_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "count": 4,
            "previous": None,
            "next": None,
            "data": [
                {
                    "status": "INITIALIZING",
                    "percentageCompleted": 0,
                    "elapsedTimeSec": 7747,
                    "links": {
                        "self": (
                            "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
                        ),
                        "csvUpload": (
                            "https://host_name.com/batchPredictions/"
                            "5ce1204b962d741661907ea0/csvUpload/"
                        ),
                    },
                    "jobSpec": {
                        "numConcurrent": 1,
                        "chunkSize": "auto",
                        "thresholdHigh": None,
                        "thresholdLow": None,
                        "filename": "",
                        "deploymentId": "5ce1138c962d7415e076d8c6",
                        "passthroughColumns": [],
                        "passthroughColumnsSet": None,
                        "maxExplanations": None,
                    },
                    "statusDetails": "Job submitted at 2019-05-19 09:22:19.779000",
                },
                {
                    "id": "5ce1204b962d741661907ea0",
                    "status": "INITIALIZING",
                    "percentageCompleted": 0,
                    "elapsedTimeSec": 7220,
                    "links": {
                        "self": (
                            "https://host_name.com/batchPredictions/5ce1225a962d741661907eb3/",
                        )
                    },
                    "jobSpec": {
                        "numConcurrent": 1,
                        "thresholdHigh": None,
                        "thresholdLow": None,
                        "filename": "",
                        "deploymentId": "5ce1138c962d7415e076d8c6",
                        "passthroughColumns": [],
                        "passthroughColumnsSet": None,
                        "maxExplanations": None,
                    },
                    "statusDetails": "Job submitted at 2019-05-19 09:31:06.724000",
                },
            ],
        }
    )


@pytest.fixture
def batch_prediction_job_initializing_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "status": "INITIALIZING",
            "percentageCompleted": 0,
            "elapsedTimeSec": 7747,
            "links": {
                "self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
                "csvUpload": (
                    "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/csvUpload/"
                ),
            },
            "jobSpec": {
                "numConcurrent": 1,
                "chunkSize": "auto",
                "thresholdHigh": None,
                "thresholdLow": None,
                "filename": "",
                "deploymentId": "5ce1138c962d7415e076d8c6",
                "passthroughColumns": [],
                "passthroughColumnsSet": None,
                "maxExplanations": None,
            },
            "statusDetails": "Job submitted at 2019-05-19 09:22:19.779000",
        }
    )


@pytest.fixture
def batch_prediction_job_s3_initializing_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "status": "INITIALIZING",
            "percentageCompleted": 0,
            "elapsedTimeSec": 7747,
            "links": {"self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
            "jobSpec": {
                "numConcurrent": 1,
                "chunkSize": "fixed",
                "thresholdHigh": None,
                "thresholdLow": None,
                "filename": "",
                "deploymentId": "5ce1138c962d7415e076d8c6",
                "passthroughColumns": [],
                "passthroughColumnsSet": None,
                "maxExplanations": None,
                "intake_settings": {"type": "s3", "url": "s3://bucket/source_key"},
                "output_settings": {"type": "s3", "url": "s3://bucket/target_key"},
            },
            "statusDetails": "Job submitted at 2019-05-19 09:22:19.779000",
        }
    )


@pytest.fixture
def batch_prediction_job_azure_initializing_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "status": "INITIALIZING",
            "percentageCompleted": 0,
            "elapsedTimeSec": 7747,
            "links": {"self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
            "jobSpec": {
                "numConcurrent": 1,
                "chunkSize": "dynamic",
                "thresholdHigh": None,
                "thresholdLow": None,
                "filename": "",
                "deploymentId": "5ce1138c962d7415e076d8c6",
                "passthroughColumns": [],
                "passthroughColumnsSet": None,
                "maxExplanations": None,
                "intake_settings": {
                    "type": "azure",
                    "url": "https://storage_account.blob.endpoint/container/source_key",
                },
                "output_settings": {
                    "type": "azure",
                    "url": "https://storage_account.blob.endpoint/container/target_key",
                },
            },
            "statusDetails": "Job submitted at 2019-05-19 09:22:19.779000",
        }
    )


@pytest.fixture
def batch_prediction_job_gcp_initializing_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "status": "INITIALIZING",
            "percentageCompleted": 0,
            "elapsedTimeSec": 7747,
            "links": {"self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
            "jobSpec": {
                "numConcurrent": 1,
                "chunkSize": 4096,
                "thresholdHigh": None,
                "thresholdLow": None,
                "filename": "",
                "deploymentId": "5ce1138c962d7415e076d8c6",
                "passthroughColumns": [],
                "passthroughColumnsSet": None,
                "maxExplanations": None,
                "intake_settings": {
                    "type": "gcp",
                    "url": "https://storage.googleapis.com/bucket/source_key",
                },
                "output_settings": {
                    "type": "gcp",
                    "url": "https://storage.googleapis.com/bucket/target_key",
                },
            },
            "statusDetails": "Job submitted at 2019-05-19 09:22:19.779000",
        }
    )


@pytest.fixture
def batch_prediction_job_running_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "status": "RUNNING",
            "scored_rows": 400,
            "failed_rows": 0,
            "percentageCompleted": 40,
            "elapsedTimeSec": 7747,
            "links": {
                "download": (
                    "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/"
                ),
                "self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
            },
            "jobSpec": {
                "numConcurrent": 1,
                "chunkSize": "auto",
                "thresholdHigh": None,
                "thresholdLow": None,
                "filename": "",
                "deploymentId": "5ce1138c962d7415e076d8c6",
                "passthroughColumns": [],
                "passthroughColumnsSet": None,
                "maxExplanations": None,
            },
            "statusDetails": "Job submitted at 2019-05-19 09:22:19.779000",
        }
    )


@pytest.fixture
def batch_prediction_job_completed_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "status": "COMPLETED",
            "scored_rows": 400,
            "failed_rows": 0,
            "percentageCompleted": 100,
            "elapsedTimeSec": 7747,
            "links": {
                "download": (
                    "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/"
                ),
                "self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
            },
            "jobSpec": {
                "numConcurrent": 1,
                "chunkSize": "fixed",
                "thresholdHigh": None,
                "thresholdLow": None,
                "filename": "",
                "deploymentId": "5ce1138c962d7415e076d8c6",
                "passthroughColumns": [],
                "passthroughColumnsSet": None,
                "maxExplanations": None,
            },
            "statusDetails": "Job submitted at 2019-05-19 09:22:19.779000",
        }
    )


@pytest.fixture
def batch_prediction_job_aborted_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "status": "ABORTED",
            "scored_rows": 400,
            "failed_rows": 800,
            "percentageCompleted": 100,
            "elapsedTimeSec": 7747,
            "links": {
                "download": (
                    "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/"
                ),
                "self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
            },
            "jobSpec": {
                "numConcurrent": 1,
                "chunkSize": "fixed",
                "thresholdHigh": None,
                "thresholdLow": None,
                "filename": "",
                "deploymentId": "5ce1138c962d7415e076d8c6",
                "passthroughColumns": [],
                "passthroughColumnsSet": None,
                "maxExplanations": None,
            },
            "statusDetails": "Aborted at 2019-05-19 09:22:19.779000",
        }
    )


@pytest.fixture
def batch_prediction_job_failed_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "status": "FAILED",
            "scored_rows": 0,
            "failed_rows": 0,
            "percentageCompleted": 0,
            "elapsedTimeSec": 1,
            "links": {
                "download": (
                    "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/"
                ),
                "self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
            },
            "jobSpec": {
                "numConcurrent": 1,
                "chunkSize": "fixed",
                "thresholdHigh": None,
                "thresholdLow": None,
                "filename": "",
                "deploymentId": "5ce1138c962d7415e076d8c6",
                "passthroughColumns": [],
                "passthroughColumnsSet": None,
                "maxExplanations": None,
            },
            "statusDetails": "Failed at 2019-05-19 09:22:19.779000",
        }
    )


@pytest.fixture
def batch_prediction_job_completed_passthrough_columns_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "status": "COMPLETED",
            "scored_rows": 400,
            "failed_rows": 0,
            "percentageCompleted": 100,
            "elapsedTimeSec": 7747,
            "links": {
                "download": (
                    "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/"
                ),
                "self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
            },
            "jobSpec": {
                "numConcurrent": 1,
                "chunkSize": "fixed",
                "thresholdHigh": None,
                "thresholdLow": None,
                "filename": "",
                "deploymentId": "5ce1138c962d7415e076d8c6",
                "passthroughColumns": ["a", "b"],
                "passthroughColumnsSet": None,
                "maxExplanations": None,
            },
            "statusDetails": "Job submitted at 2019-05-19 09:22:19.779000",
        }
    )


@pytest.fixture
def batch_prediction_job_completed_passthrough_columns_set_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "status": "COMPLETED",
            "scored_rows": 400,
            "failed_rows": 0,
            "percentageCompleted": 100,
            "elapsedTimeSec": 7747,
            "links": {
                "download": (
                    "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/"
                ),
                "self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
            },
            "jobSpec": {
                "numConcurrent": 1,
                "chunkSize": "dynamic",
                "thresholdHigh": None,
                "thresholdLow": None,
                "filename": "",
                "deploymentId": "5ce1138c962d7415e076d8c6",
                "passthroughColumns": [],
                "passthroughColumnsSet": "all",
                "maxExplanations": None,
            },
            "statusDetails": "Job submitted at 2019-05-19 09:22:19.779000",
        }
    )


@pytest.fixture
def batch_prediction_job_s3_completed_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "status": "COMPLETED",
            "scored_rows": 400,
            "failed_rows": 0,
            "percentageCompleted": 100,
            "elapsedTimeSec": 7747,
            "links": {"self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
            "jobSpec": {
                "numConcurrent": 1,
                "chunkSize": 2048,
                "thresholdHigh": None,
                "thresholdLow": None,
                "filename": "",
                "deploymentId": "5ce1138c962d7415e076d8c6",
                "passthroughColumns": [],
                "passthroughColumnsSet": None,
                "maxExplanations": None,
                "intake_settings": {"type": "s3", "url": "s3://bucket/source_key"},
                "output_settings": {"type": "s3", "url": "s3://bucket/target_key"},
            },
            "statusDetails": "Job submitted at 2019-05-19 09:22:19.779000",
        }
    )


@pytest.fixture
def batch_prediction_job_azure_completed_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "status": "COMPLETED",
            "scored_rows": 300,
            "failed_rows": 0,
            "percentageCompleted": 100,
            "elapsedTimeSec": 5561,
            "links": {"self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
            "jobSpec": {
                "numConcurrent": 1,
                "chunkSize": "auto",
                "thresholdHigh": None,
                "thresholdLow": None,
                "filename": "",
                "deploymentId": "5ce1138c962d7415e076d8c6",
                "passthroughColumns": [],
                "passthroughColumnsSet": None,
                "maxExplanations": None,
                "intake_settings": {
                    "type": "azure",
                    "url": "https://storage_account.blob.endpoint/container/source_key",
                },
                "output_settings": {
                    "type": "azure",
                    "url": "https://storage_account.blob.endpoint/container/target_key",
                },
            },
            "statusDetails": "Job submitted at 2019-05-19 09:22:19.779000",
        }
    )


@pytest.fixture
def batch_prediction_job_gcp_completed_json():
    return json.dumps(
        {
            "id": "5ce1204b962d741661907ea0",
            "status": "COMPLETED",
            "scored_rows": 500,
            "failed_rows": 0,
            "percentageCompleted": 100,
            "elapsedTimeSec": 1451,
            "links": {"self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
            "jobSpec": {
                "numConcurrent": 1,
                "chunkSize": "fixed",
                "thresholdHigh": None,
                "thresholdLow": None,
                "filename": "",
                "deploymentId": "5ce1138c962d7415e076d8c6",
                "passthroughColumns": [],
                "passthroughColumnsSet": None,
                "maxExplanations": None,
                "intake_settings": {
                    "type": "gcp",
                    "url": "https://storage.googleapis.com/bucket/source_key",
                },
                "output_settings": {
                    "type": "gcp",
                    "url": "https://storage.googleapis.com/bucket/target_key",
                },
            },
            "statusDetails": "Job submitted at 2019-05-19 09:22:19.779000",
        }
    )


@pytest.fixture
def batch_prediction_job_data_csv():
    return b"""readmitted_1.0_PREDICTION,readmitted_0.0_PREDICTION,readmitted_PREDICTION,THRESHOLD,POSITIVE_CLASS,prediction_status
0.219181314111,0.780818685889,0.0,0.5,1.0,OK
0.341459780931,0.658540219069,0.0,0.5,1.0,OK
0.420107662678,0.579892337322,0.0,0.5,1.0,OK"""


@pytest.fixture
def batch_prediction_job_data_csv_with_index():
    return b"""readmitted_1.0_PREDICTION,readmitted_0.0_PREDICTION,readmitted_PREDICTION,THRESHOLD,POSITIVE_CLASS,prediction_status,__DR_index__
0.219181314111,0.780818685889,0.0,0.5,1.0,OK,0
0.341459780931,0.658540219069,0.0,0.5,1.0,OK,1
0.420107662678,0.579892337322,0.0,0.5,1.0,OK,2"""


@responses.activate
@pytest.mark.usefixtures("client")
def test_list_batch_prediction_jobs_by_status(batch_prediction_jobs_json):
    responses.add(
        responses.GET, "https://host_name.com/batchPredictions/", body=batch_prediction_jobs_json
    )

    job_statuses = BatchPredictionJob.list_by_status()

    assert 2 == len(job_statuses)


@responses.activate
@pytest.mark.usefixtures("client")
@pytest.mark.parametrize(
    ["job_fixture", "expected_status", "expected_percentage_completed"],
    [
        pytest.param("batch_prediction_job_initializing_json", "INITIALIZING", 0),
        pytest.param("batch_prediction_job_completed_passthrough_columns_json", "COMPLETED", 100),
        pytest.param(
            "batch_prediction_job_completed_passthrough_columns_set_json", "COMPLETED", 100,
        ),
        pytest.param("batch_prediction_job_s3_completed_json", "COMPLETED", 100),
    ],
)
def test_get_batch_prediction_job_status(
    request, job_fixture, expected_status, expected_percentage_completed
):

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=request.getfixturevalue(job_fixture),
    )

    job = BatchPredictionJob.get("5ce1204b962d741661907ea0")
    job_status = job.get_status()

    assert job_status["status"] == expected_status
    assert job_status["percentage_completed"] == expected_percentage_completed


@responses.activate
@pytest.mark.usefixtures("client")
def test_get_result_when_done(
    batch_prediction_job_initializing_json,
    batch_prediction_job_running_json,
    batch_prediction_job_completed_json,
    batch_prediction_job_data_csv,
):

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_initializing_json,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_running_json,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_completed_json,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/",
        body=batch_prediction_job_data_csv,
    )

    job = BatchPredictionJob.get("5ce1204b962d741661907ea0")

    assert job.get_result_when_complete() == batch_prediction_job_data_csv


@responses.activate
@pytest.mark.usefixtures("client")
@pytest.mark.parametrize(
    ["kwargs", "expected_read_timeout"],
    [
        pytest.param({}, 660, id="default-timeout"),
        pytest.param({"download_read_timeout": 200}, 200, id="override-timeout"),
    ],
)
def test_score_to_file(
    tmpdir,
    kwargs,
    expected_read_timeout,
    batch_prediction_job_initializing_json,
    batch_prediction_job_completed_json,
    batch_prediction_job_data_csv,
):

    responses.add(
        responses.POST,
        "https://host_name.com/batchPredictions/",
        body=batch_prediction_job_initializing_json,
        headers={"Location": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/",
        body=batch_prediction_job_data_csv,
    )

    responses.add(
        responses.PUT,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/csvUpload/",
        body="",
        status=202,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_completed_json,
    )

    output_file = str(tmpdir.mkdir("sub").join("scored.csv"))
    thread_count_before = threading.activeCount()

    with mock.patch.object(
        BatchPredictionJob._client, "get", wraps=BatchPredictionJob._client.get
    ) as download_spy:

        BatchPredictionJob.score_to_file(
            "5ce1138c962d7415e076d8c6", io.BytesIO(b"foo\nbar"), output_file, **kwargs
        )

        download_spy.assert_any_call(
            "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/",
            stream=True,
            timeout=expected_read_timeout,
        )

    assert open(output_file, "rb").read() == batch_prediction_job_data_csv
    assert thread_count_before == threading.activeCount(), "Thread leak"


@responses.activate
@pytest.mark.usefixtures("client")
def test_score_to_file_timeout(
    tmpdir,
    batch_prediction_job_initializing_json,
    batch_prediction_job_completed_json,
    batch_prediction_job_data_csv,
):

    responses.add(
        responses.POST,
        "https://host_name.com/batchPredictions/",
        body=batch_prediction_job_initializing_json,
        headers={"Location": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
    )

    responses.add(
        responses.PUT,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/csvUpload/",
        body="",
        status=202,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_initializing_json,
    )

    responses.add(
        responses.DELETE,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body="",
        status=202,
    )

    output_file = str(tmpdir.mkdir("sub").join("scored.csv"))

    thread_count_before = threading.activeCount()

    with pytest.raises(RuntimeError):
        BatchPredictionJob.score_to_file(
            "5ce1138c962d7415e076d8c6", io.BytesIO(b"foo\nbar"), output_file, download_timeout=1,
        )

    assert open(output_file, "r").read() == ""
    assert thread_count_before == threading.activeCount(), "Thread leak"

    # Job should abort after timeout
    last_request = responses.calls[-1].request
    assert last_request.method == "DELETE"
    assert last_request.url == "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"


@responses.activate
@pytest.mark.usefixtures("client")
@mock.patch("requests.sessions.Session.put")
def test_score_to_file_race_condition(
    put_mock,
    tmpdir,
    batch_prediction_job_initializing_json,
    batch_prediction_job_completed_json,
    batch_prediction_job_data_csv,
):
    responses.add(
        responses.POST,
        "https://host_name.com/batchPredictions/",
        body=batch_prediction_job_initializing_json,
        headers={"Location": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/",
        body=batch_prediction_job_data_csv,
    )

    responses.add(
        responses.PUT,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/csvUpload/",
        body="",
        status=202,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_completed_json,
    )

    output_file = str(tmpdir.mkdir("sub").join("scored.csv"))

    thread_count_before = threading.activeCount()

    # It is not possible to slow down the PUT request itself, as the bug this test fixes
    # was related to a passed argument, which is already sent on the stack at this point.
    # Therefore, we slow down the seek(0) operation happening immediately before, triggering
    # the race condition.
    def slow_seek(*args):
        time.sleep(1)
        return

    mock_file_object = mock.MagicMock()
    mock_file_object.seek.side_effect = slow_seek

    BatchPredictionJob.score_to_file(
        "5ce1138c962d7415e076d8c6", mock_file_object, output_file,
    )

    put_mock.assert_called_once()
    assert open(output_file, "rb").read() == batch_prediction_job_data_csv
    assert thread_count_before == threading.activeCount(), "Thread leak"


@responses.activate
@pytest.mark.usefixtures("client")
def test_score_to_file_aborted_during_download_raises_exception(
    tmpdir,
    batch_prediction_job_initializing_json,
    batch_prediction_job_running_json,
    batch_prediction_job_aborted_json,
):

    responses.add(
        responses.POST,
        "https://host_name.com/batchPredictions/",
        body=batch_prediction_job_initializing_json,
        headers={"Location": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
    )

    responses.add(
        responses.PUT,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/csvUpload/",
        body="",
        status=202,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_running_json,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_running_json,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/",
        body="a,b,c\n1,2,3",
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_aborted_json,
    )

    output_file = str(tmpdir.mkdir("sub").join("scored.csv"))

    with pytest.raises(RuntimeError, match=r"Job 5ce1204b962d741661907ea0 was aborted"):
        BatchPredictionJob.score_to_file(
            "5ce1138c962d7415e076d8c6", io.BytesIO(b"foo\nbar"), output_file
        )


@responses.activate
@pytest.mark.usefixtures("client")
def test_score_to_file_failed_before_download_raises_exception(
    tmpdir, batch_prediction_job_initializing_json, batch_prediction_job_failed_json,
):

    responses.add(
        responses.POST,
        "https://host_name.com/batchPredictions/",
        body=batch_prediction_job_initializing_json,
        headers={"Location": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
    )

    responses.add(
        responses.PUT,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/csvUpload/",
        body="",
        status=202,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_failed_json,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/",
        body="a,b,c\n1,2,3",
    )

    output_file = str(tmpdir.mkdir("sub").join("scored.csv"))

    with pytest.raises(RuntimeError, match=r"Job 5ce1204b962d741661907ea0 was aborted"):
        BatchPredictionJob.score_to_file(
            "5ce1138c962d7415e076d8c6", io.BytesIO(b"foo\nbar"), output_file
        )


@responses.activate
@pytest.mark.usefixtures("client")
@pytest.mark.parametrize(
    ["name", "scoring_function", "source_url", "destination_url"],
    [
        pytest.param(
            "s3",
            BatchPredictionJob.score_s3,
            "s3://bucket/source_key",
            "s3://bucket/target_key",
            id="s3",
        ),
        pytest.param(
            "azure",
            BatchPredictionJob.score_azure,
            "https://storage_account.blob.endpoint/container/source_key",
            "https://storage_account.blob.endpoint/container/target_key",
            id="azure",
        ),
        pytest.param(
            "gcp",
            BatchPredictionJob.score_gcp,
            "https://storage.googleapis.com/bucket/source_key",
            "https://storage.googleapis.com/bucket/target_key",
            id="gcp",
        ),
    ],
)
def test_score_cloud(request, name, scoring_function, source_url, destination_url):
    responses.add(
        responses.POST,
        "https://host_name.com/batchPredictions/",
        body=request.getfixturevalue(
            "batch_prediction_job_{name}_initializing_json".format(name=name)
        ),
        headers={"Location": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=request.getfixturevalue(
            "batch_prediction_job_{name}_completed_json".format(name=name)
        ),
    )

    job = scoring_function(
        deployment="5ce1138c962d7415e076d8c6",
        source_url=source_url,
        destination_url=destination_url,
        credential=Credential("key_id"),
    )

    job.wait_for_completion()
    job_status = job.get_status()

    assert job_status["job_spec"]["intake_settings"]["type"] == name
    assert job_status["job_spec"]["output_settings"]["type"] == name
    assert job_status["job_spec"]["intake_settings"]["url"] == source_url
    assert job_status["job_spec"]["output_settings"]["url"] == destination_url


@responses.activate
@pytest.mark.usefixtures("client")
def test_score_from_existing(batch_prediction_job_s3_completed_json):

    responses.add(
        responses.POST,
        "https://host_name.com/batchPredictions/fromExisting/",
        headers={"Location": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_s3_completed_json,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea1/",
        body=batch_prediction_job_s3_completed_json,
    )

    job = BatchPredictionJob.score_from_existing(
        batch_prediction_job_id="5ce1204b962d741661907ea1",
    )

    job.wait_for_completion()


@pytest.mark.usefixtures("client")
@pytest.mark.parametrize(
    ["score_args", "expected_exception", "expected_message"],
    [
        pytest.param(
            {"deployment": "foo", "intake_settings": {"type": "unknown"}},
            ValueError,
            "Unsupported type parameter for intake_settings",
            id="unsupported-intake-option",
        ),
        pytest.param(
            {"deployment": "foo"}, ValueError, "Missing source data", id="missing-source-data",
        ),
        pytest.param(
            {"deployment": "foo", "intake_settings": {"type": "s3"}},
            t.DataError,
            None,
            id="missing-s3-intake-configuration",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "s3", "url": "s3://bucket/source_key"},
                "output_settings": {"type": "s3"},
            },
            t.DataError,
            None,
            id="missing-s3-output-configuration",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "local_file"},
                "output_settings": {"type": "local_file"},
                "timeseries_settings": {"type": "unknown"},
            },
            t.DataError,
            None,
            id="unknown-ts-prediction-type",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "local_file"},
                "output_settings": {"type": "local_file"},
                "timeseries_settings": {
                    "type": "historical",
                    "forecast_point": "2020-05-16T17:42:12+00:00",
                },
            },
            t.DataError,
            None,
            id="forecast-point-for-ts-historical-predictions",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "local_file"},
                "output_settings": {"type": "local_file"},
                "timeseries_settings": {
                    "type": "forecast",
                    "predictions_start_date": "2020-05-16T17:42:12+00:00",
                },
            },
            t.DataError,
            None,
            id="predictions-start-date-for-ts-forecast-predictions",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "timeseries_settings": {
                    "type": "historical",
                    "predictions_start_date": "2020-05-16T17:42:13+00:00",
                },
            },
            ValueError,
            None,
            id="predictions-start-date-without-end-date-for-ts-historical-predictions",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "timeseries_settings": {
                    "type": "historical",
                    "predictions_start_date": "2020-05-17T17:42:13+00:00",
                    "predictions_end_date": "2020-05-16T17:42:13+00:00",
                },
            },
            ValueError,
            None,
            id="predictions-start-date-after-end-date-for-ts-historical-predictions",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "timeseries_settings": {"type": "forecast", "forecast_point": "foo"},
            },
            ValueError,
            None,
            id="forecast-point-with-wrong-format-for-ts-forecast-predictions",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "timeseries_settings": {
                    "type": "historical",
                    "predictions_start_date": "foo",
                    "predictions_end_date": "2020-05-17T17:42:13+00:00",
                },
            },
            ValueError,
            None,
            id="predictions-start-date-with-wrong-format-for-ts-historical-predictions",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "timeseries_settings": {
                    "type": "historical",
                    "predictions_start_date": "2020-05-16T17:42:13+00:00",
                    "predictions_end_date": "foo",
                },
            },
            ValueError,
            None,
            id="predictions-end-date-with-wrong-format-for-ts-historical-predictions",
        ),
    ],
)
def test_score_errors(score_args, expected_exception, expected_message):
    with pytest.raises(expected_exception, match=expected_message):
        BatchPredictionJob.score(**score_args)


@pytest.mark.parametrize(
    ["score_args", "expected_job_data"],
    [
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
            },
            id="deployment-id",
        ),
        pytest.param(
            {
                "deployment": mock.MagicMock(id="bar"),
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
            },
            {
                "deploymentId": "bar",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
            },
            id="deployment",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "s3", "url": "s3://bucket/source_key"},
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "s3", "url": "s3://bucket/source_key"},
                "outputSettings": {"type": "localFile"},
            },
            id="s3-intake-settings",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "s3", "url": "s3://bucket/source_key"},
                "output_settings": {"type": "s3", "url": "s3://bucket/target_key"},
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "s3", "url": "s3://bucket/source_key"},
                "outputSettings": {"type": "s3", "url": "s3://bucket/target_key"},
            },
            id="s3-intake-output-settings",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {
                    "type": "s3",
                    "url": "s3://bucket/source_key",
                    "credential_id": "key_id",
                },
                "output_settings": {
                    "type": "s3",
                    "url": "s3://bucket/target_key",
                    "credential_id": "key_id",
                },
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {
                    "type": "s3",
                    "url": "s3://bucket/source_key",
                    "credentialId": "key_id",
                },
                "outputSettings": {
                    "type": "s3",
                    "url": "s3://bucket/target_key",
                    "credentialId": "key_id",
                },
            },
            id="full-s3-intake-output-settings",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "threshold_high": 0.95,
                "threshold_low": 0.05,
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "thresholdHigh": 0.95,
                "thresholdLow": 0.05,
            },
            id="thresholds",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "passthrough_columns": ["a", "b", "c"],
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "passthroughColumns": ["a", "b", "c"],
            },
            id="passthrough-columns",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "passthrough_columns_set": "all",
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "passthroughColumnsSet": "all",
            },
            id="passthrough-columns-set-all",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "passthrough_columns": ["a", "b", "c"],
                "passthrough_columns_set": "all",
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "passthroughColumnsSet": "all",
            },
            id="passthrough-columns-set-override",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "num_concurrent": 10,
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "numConcurrent": 10,
            },
            id="num-concurrent",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "chunk_size": "fixed",
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "chunkSize": "fixed",
            },
            id="chunk-size",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "max_explanations": 10,
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "maxExplanations": 10,
            },
            id="max-explanations",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "prediction_warning_enabled": True,
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "predictionWarningEnabled": True,
            },
            id="prediction-warning-enabled",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {
                    "type": "dataset",
                    "dataset": Dataset(
                        dataset_id="foo",
                        version_id="dont_display",
                        name="name",
                        categories=["categories"],
                        created_at="created_at",
                        created_by="created_by",
                        is_data_engine_eligible=False,
                        is_latest_version=True,
                        is_snapshot=True,
                        processing_state="processing_state",
                    ),
                    "dataset_version_id": "version_id_explicit",
                },
                "output_settings": {"type": "localFile"},
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {
                    "type": "dataset",
                    "datasetId": "foo",
                    "datasetVersionId": "version_id_explicit",
                },
                "outputSettings": {"type": "localFile"},
            },
            id="dataset-intake-with-version-id-localfile-output",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {
                    "type": "dataset",
                    "dataset": Dataset(
                        dataset_id="foo",
                        version_id="version_id_from_client",
                        name="name",
                        categories=["categories"],
                        created_at="created_at",
                        created_by="created_by",
                        is_data_engine_eligible=False,
                        is_latest_version=True,
                        is_snapshot=True,
                        processing_state="processing_state",
                    ),
                },
                "output_settings": {"type": "localFile"},
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {
                    "type": "dataset",
                    "datasetId": "foo",
                    "datasetVersionId": "version_id_from_client",
                },
                "outputSettings": {"type": "localFile"},
            },
            id="dataset-intake-without-version-id-localfile-output",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {
                    "type": "jdbc",
                    "table": "test",
                    "schema": "public",
                    "data_store_id": "abcd1234",
                    "credential_id": "key_id",
                },
                "output_settings": {
                    "type": "jdbc",
                    "table": "test2",
                    "schema": "public",
                    "statement_type": "insert",
                    "data_store_id": "abcd1234",
                    "credential_id": "key_id",
                },
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {
                    "type": "jdbc",
                    "table": "test",
                    "schema": "public",
                    "dataStoreId": "abcd1234",
                    "credentialId": "key_id",
                },
                "outputSettings": {
                    "type": "jdbc",
                    "table": "test2",
                    "schema": "public",
                    "statementType": "insert",
                    "dataStoreId": "abcd1234",
                    "credentialId": "key_id",
                },
            },
            id="full-jdbc-intake-output-settings",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {
                    "type": "snowflake",
                    "table": "test",
                    "schema": "public",
                    "external_stage": "s3_stage",
                    "data_store_id": "abcd1234",
                    "credential_id": "key_id",
                    "cloud_storage_credential_id": "cloud_storage_key_id",
                    "cloud_storage_type": "s3",
                },
                "output_settings": {
                    "type": "snowflake",
                    "table": "test2",
                    "schema": "public",
                    "external_stage": "s3_stage",
                    "statement_type": "insert",
                    "data_store_id": "abcd1234",
                    "credential_id": "key_id",
                    "cloud_storage_credential_id": "cloud_storage_key_id",
                    "cloud_storage_type": "s3",
                },
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {
                    "type": "snowflake",
                    "table": "test",
                    "schema": "public",
                    "externalStage": "s3_stage",
                    "dataStoreId": "abcd1234",
                    "credentialId": "key_id",
                    "cloudStorageCredentialId": "cloud_storage_key_id",
                    "cloudStorageType": "s3",
                },
                "outputSettings": {
                    "type": "snowflake",
                    "table": "test2",
                    "schema": "public",
                    "statementType": "insert",
                    "externalStage": "s3_stage",
                    "dataStoreId": "abcd1234",
                    "credentialId": "key_id",
                    "cloudStorageCredentialId": "cloud_storage_key_id",
                    "cloudStorageType": "s3",
                },
            },
            id="full-snowflake-intake-output-settings",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {
                    "type": "synapse",
                    "table": "test",
                    "schema": "public",
                    "external_data_source": "my_data_source",
                    "data_store_id": "abcd1234",
                    "credential_id": "key_id",
                    "cloud_storage_credential_id": "cloud_storage_key_id",
                },
                "output_settings": {
                    "type": "synapse",
                    "table": "test2",
                    "schema": "public",
                    "external_data_source": "my_data_source",
                    "statement_type": "insert",
                    "data_store_id": "abcd1234",
                    "credential_id": "key_id",
                    "cloud_storage_credential_id": "cloud_storage_key_id",
                },
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {
                    "type": "synapse",
                    "table": "test",
                    "schema": "public",
                    "externalDataSource": "my_data_source",
                    "dataStoreId": "abcd1234",
                    "credentialId": "key_id",
                    "cloudStorageCredentialId": "cloud_storage_key_id",
                },
                "outputSettings": {
                    "type": "synapse",
                    "table": "test2",
                    "schema": "public",
                    "statementType": "insert",
                    "externalDataSource": "my_data_source",
                    "dataStoreId": "abcd1234",
                    "credentialId": "key_id",
                    "cloudStorageCredentialId": "cloud_storage_key_id",
                },
            },
            id="full-synapse-intake-output-settings",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "timeseries_settings": {"type": "forecast"},
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "timeseriesSettings": {"type": "forecast"},
            },
            id="ts-forecast-default-forecast-point",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "timeseries_settings": {"type": "forecast"},
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "timeseriesSettings": {"type": "forecast"},
            },
            id="ts-forecast-default-forecast-point",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "timeseries_settings": {
                    "type": "forecast",
                    "forecast_point": "2020-05-16T17:42:13+00:00",
                },
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "timeseriesSettings": {
                    "type": "forecast",
                    "forecastPoint": "2020-05-16T17:42:13+00:00",
                },
            },
            id="ts-forecast-string-forecast-point",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "timeseries_settings": {
                    "type": "forecast",
                    "forecast_point": datetime.datetime(
                        2020, 5, 16, 17, 42, 13, tzinfo=dateutil.tz.tzutc()
                    ),
                },
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "timeseriesSettings": {
                    "type": "forecast",
                    "forecastPoint": "2020-05-16T17:42:13+00:00",
                },
            },
            id="ts-forecast-datetime-forecast-point",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "timeseries_settings": {"type": "historical"},
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "timeseriesSettings": {"type": "historical"},
            },
            id="ts-historical-default",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "timeseries_settings": {
                    "type": "historical",
                    "predictions_start_date": "2020-05-16T17:42:13+00:00",
                    "predictions_end_date": "2020-05-17T17:42:13+00:00",
                },
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "timeseriesSettings": {
                    "type": "historical",
                    "predictionsStartDate": "2020-05-16T17:42:13+00:00",
                    "predictionsEndDate": "2020-05-17T17:42:13+00:00",
                },
            },
            id="ts-historical-string-prediction-interval",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "timeseries_settings": {
                    "type": "historical",
                    "predictions_start_date": datetime.datetime(
                        2020, 5, 16, 17, 42, 13, tzinfo=dateutil.tz.tzutc()
                    ),
                    "predictions_end_date": datetime.datetime(
                        2020, 5, 17, 17, 42, 13, tzinfo=dateutil.tz.tzutc()
                    ),
                },
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "timeseriesSettings": {
                    "type": "historical",
                    "predictionsStartDate": "2020-05-16T17:42:13+00:00",
                    "predictionsEndDate": "2020-05-17T17:42:13+00:00",
                },
            },
            id="ts-historical-datetime-prediction-interval",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "timeseries_settings": {
                    "type": "historical",
                    "relax_known_in_advance_features_check": True,
                },
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "timeseriesSettings": {
                    "type": "historical",
                    "relaxKnownInAdvanceFeaturesCheck": True,
                },
            },
            id="ts-historical-default-relax-kia",
        ),
        pytest.param(
            {
                "deployment": "foo",
                "intake_settings": {"type": "localFile", "file": io.BytesIO(b"foo\nbar")},
                "prediction_instance": {
                    "hostName": "192.0.2.4",
                    "sslEnabled": False,
                    "apiKey": "NWUQ9w21UhGgerBtOC4ahN0aqjbjZ0NMhL1e5cSt4ZHIBn2w",
                    "datarobotKey": "154a8abb-cbde-4e73-ab3b-a46c389c337b",
                },
            },
            {
                "deploymentId": "foo",
                "intakeSettings": {"type": "localFile"},
                "outputSettings": {"type": "localFile"},
                "predictionInstance": {
                    "hostName": "192.0.2.4",
                    "sslEnabled": False,
                    "apiKey": "NWUQ9w21UhGgerBtOC4ahN0aqjbjZ0NMhL1e5cSt4ZHIBn2w",
                    "datarobotKey": "154a8abb-cbde-4e73-ab3b-a46c389c337b",
                },
            },
            id="prediction-instance",
        ),
    ],
)
@mock.patch("datarobot.BatchPredictionJob._client")
def test_score_job_data(mock_client, score_args, expected_job_data):

    # Using an exception to short-circuit the score function and test
    # the contents of the job data without proceeding with the rest
    # of the function

    mock_client.post.side_effect = RuntimeError("short-circuit")

    with pytest.raises(RuntimeError, match="short-circuit"):
        BatchPredictionJob.score(**score_args)

    mock_client.post.assert_called_once_with(
        url=BatchPredictionJob._jobs_path(), json=expected_job_data,
    )


@pytest.mark.parametrize(
    ["download_kwargs", "expected_read_timeout"],
    [
        pytest.param({}, 660, id="default-timeout"),
        pytest.param({"read_timeout": 200}, 200, id="override-timeout"),
    ],
)
@responses.activate
def test_download_read_timeout(
    batch_prediction_job_completed_json,
    batch_prediction_job_data_csv,
    download_kwargs,
    expected_read_timeout,
):

    job_id = "5ce1204b962d741661907ea0"

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_completed_json,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/",
        body=batch_prediction_job_data_csv,
    )

    job = BatchPredictionJob.get(job_id)
    buf = io.BytesIO()

    with mock.patch.object(
        BatchPredictionJob._client, "get", wraps=BatchPredictionJob._client.get
    ) as download_spy:

        job.download(buf, **download_kwargs)

        download_spy.assert_any_call(
            "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/",
            stream=True,
            timeout=expected_read_timeout,
        )


@responses.activate
def test_exception_during_cleanup(batch_prediction_job_initializing_json):

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_initializing_json,
    )

    responses.add(
        responses.DELETE,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body="{'message': 'not found'}",
        status=404,
    )

    job = BatchPredictionJob.get("5ce1204b962d741661907ea0")

    with pytest.raises(RuntimeError, match=r"Timed out waiting for download to become available"):
        job.download(io.BytesIO(), timeout=1)


@responses.activate
@pytest.mark.usefixtures("client")
def test_score_pandas(
    batch_prediction_job_initializing_json,
    batch_prediction_job_completed_json,
    batch_prediction_job_data_csv_with_index,
):

    responses.add(
        responses.POST,
        "https://host_name.com/batchPredictions/",
        body=batch_prediction_job_initializing_json,
        headers={"Location": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/",
        body=batch_prediction_job_data_csv_with_index,
        stream=True,
    )

    responses.add(
        responses.PUT,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/csvUpload/",
        body="",
        status=202,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_completed_json,
    )

    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

    job, df = BatchPredictionJob.score_pandas("5ce1138c962d7415e076d8c6", df)

    assert df.shape == (3, 8)

    assert set(df.columns) == {
        "a",
        "b",
        "readmitted_1.0_PREDICTION",
        "readmitted_0.0_PREDICTION",
        "readmitted_PREDICTION",
        "THRESHOLD",
        "POSITIVE_CLASS",
        "prediction_status",
    }


@pytest.mark.parametrize(
    ["intake_settings", "output_settings"],
    [
        pytest.param(
            {"type": "s3", "url": "s3://bucket/source_key", "credential_id": "key_id"},
            {"type": "s3", "url": "s3://bucket/target_key", "credential_id": "key_id"},
            id="s3-keys",
        ),
        pytest.param(
            {
                "type": "dataset",
                "dataset": Dataset(
                    dataset_id="foo",
                    version_id="dont_display",
                    name="name",
                    categories=["categories"],
                    created_at="created_at",
                    created_by="created_by",
                    is_data_engine_eligible=False,
                    is_latest_version=True,
                    is_snapshot=True,
                    processing_state="processing_state",
                ),
                "dataset_version_id": "version_id_explicit",
            },
            {"type": "localFile"},
        ),
        pytest.param(
            {
                "type": "jdbc",
                "table": "test",
                "schema": "public",
                "catalog": "cat",
                "data_store_id": "abcd1234",
                "credential_id": "key_id",
            },
            {
                "type": "jdbc",
                "table": "test2",
                "schema": "public",
                "catalog": "cat",
                "statement_type": "insert",
                "data_store_id": "abcd1234",
                "credential_id": "key_id",
                "create_table_if_not_exists": True,
            },
            id="jdbc-keys",
        ),
        pytest.param(
            {
                "type": "snowflake",
                "table": "test",
                "schema": "public",
                "external_stage": "s3_stage",
                "data_store_id": "abcd1234",
                "credential_id": "key_id",
                "cloud_storage_credential_id": "cloud_storage_key_id",
                "cloud_storage_type": "s3",
            },
            {
                "type": "snowflake",
                "table": "test2",
                "schema": "public",
                "external_stage": "s3_stage",
                "statement_type": "insert",
                "data_store_id": "abcd1234",
                "credential_id": "key_id",
                "cloud_storage_credential_id": "cloud_storage_key_id",
                "cloud_storage_type": "s3",
                "create_table_if_not_exists": True,
            },
            id="snowflake-keys",
        ),
        pytest.param(
            {
                "type": "synapse",
                "table": "test",
                "schema": "public",
                "catalog": "cat",
                "external_data_source": "my_data_source",
                "data_store_id": "abcd1234",
                "credential_id": "key_id",
                "cloud_storage_credential_id": "cloud_storage_key_id",
            },
            {
                "type": "synapse",
                "table": "test2",
                "schema": "public",
                "catalog": "cat",
                "external_data_source": "my_data_source",
                "statement_type": "insert",
                "data_store_id": "abcd1234",
                "credential_id": "key_id",
                "cloud_storage_credential_id": "cloud_storage_key_id",
                "create_table_if_not_exists": True,
            },
            id="synapse-keys",
        ),
    ],
)
@responses.activate
@pytest.mark.usefixtures("client")
def test_score_does_not_mutate_input_output_settings(
    batch_prediction_job_initializing_json,
    batch_prediction_job_completed_json,
    batch_prediction_job_data_csv_with_index,
    intake_settings,
    output_settings,
):
    # PRED-6420 reported that the .score() function mutated intake_settings
    # by removing keys such as type. Therefore this test checks that all keys
    # which are passed in, still exist after calling .score()

    responses.add(
        responses.POST,
        "https://host_name.com/batchPredictions/",
        body=batch_prediction_job_initializing_json,
        headers={"Location": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/"},
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/download/",
        body=batch_prediction_job_data_csv_with_index,
        stream=True,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        body=batch_prediction_job_completed_json,
    )

    # setup expected values
    input_before_scoring = dict(intake_settings)
    num_input_keys_before_scoring = len(intake_settings.keys())

    output_before_scoring = dict(output_settings)
    num_output_keys_before_scoring = len(output_settings.keys())

    BatchPredictionJob.score("5ce1138c962d7415e076d8c6", intake_settings, output_settings)

    assert len(intake_settings.keys()) == num_input_keys_before_scoring
    assert len(output_settings.keys()) == num_output_keys_before_scoring
    assert intake_settings == input_before_scoring
    assert output_settings == output_before_scoring

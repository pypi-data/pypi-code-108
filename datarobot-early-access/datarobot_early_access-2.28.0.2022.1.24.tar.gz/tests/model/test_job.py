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
import pytest

from datarobot import Job


@pytest.mark.parametrize("is_blocked", [False, True])
def test_job_initialization_with_is_blocked(is_blocked):
    job = Job(
        {
            "status": "queue",
            "url": "https://host_name.com/projects/p-id/modelJobs/1/",
            "id": "1",
            "jobType": "model",
            "projectId": "p-id",
            "isBlocked": is_blocked,
        }
    )

    assert job.id == 1
    assert job.status == "queue"
    assert job.job_type == "model"
    assert job.project_id == "p-id"
    assert job.is_blocked is is_blocked

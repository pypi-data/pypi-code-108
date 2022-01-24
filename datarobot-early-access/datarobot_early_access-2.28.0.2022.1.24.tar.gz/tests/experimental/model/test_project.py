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
import mock

from datarobot._experimental.models.project import Project

_project_id = "projectId"


@mock.patch("datarobot._experimental.models.project.get_id_from_response")
@mock.patch("datarobot._experimental.models.project.ModelJob")
def test_project_train_datetime_can_send_n_clusters(mock_model_job, mock_get_id_from_reponse):
    mock_client_post = mock.MagicMock(return_value=mock.Mock(headers={"Location": None}))
    project = Project(id=_project_id)
    project._client.post = mock_client_post

    project.train_datetime(
        blueprint_id="blueprint-id", n_clusters=3,
    )
    assert mock_client_post.call_count == 1
    actual_calls = mock_client_post.call_args
    assert actual_calls[0][0] == "projects/projectId/datetimeModels/"
    assert actual_calls[1]["data"] == {
        "blueprint_id": "blueprint-id",
        "n_clusters": 3,
    }

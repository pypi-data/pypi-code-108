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
import pytest
import responses

from datarobot.models.model import CombinedModel
from datarobot.models.project import Project
from tests.utils import add_response

_base_url = "https://host_name.com/"
_project_id = "projectId"
_project_a_id = "projectA"
_project_b_id = "projectB"
_combined_model_id = "combinedModelId"

project_a_json = {
    "id": "projectA",
    "projectName": "projectA",
    "unsupervisedMode": True,
}
project_b_json = {
    "id": "projectB",
    "projectName": "projectB",
    "unsupervisedMode": True,
}


@responses.activate
def test_get_segments_models_with_combined_model_id():
    add_response(
        "https://host_name.com/projects/projectA/", project_a_json, method=responses.GET,
    )
    add_response(
        "https://host_name.com/projects/projectB/", project_b_json, method=responses.GET,
    )

    with mock.patch.object(CombinedModel, "get") as mock_combined_model_get:
        with mock.patch.object(Project, "get_models") as mock_project_get_models:
            mock_combined_model_get.return_value = mock.Mock(
                get_segments_info=mock.MagicMock(
                    return_value=[
                        mock.Mock(segment="segment_a", project_id="projectA"),
                        mock.Mock(segment="segment_b", project_id="projectB"),
                    ]
                ),
                id="combinedModelId",
            )
            mock_project_get_models.return_value = ["model"]

            project = Project(id=_project_id)

            # Test with segment keys
            expected_segments_models = [
                {
                    "segment": "segment_a",
                    "project_id": "projectA",
                    "parent_project_id": "projectId",
                    "combined_model_id": "combinedModelId",
                    "models": ["model"],
                },
                {
                    "segment": "segment_b",
                    "project_id": "projectB",
                    "parent_project_id": "projectId",
                    "combined_model_id": "combinedModelId",
                    "models": ["model"],
                },
            ]
            segments_models = project.get_segments_models(_combined_model_id)
            assert segments_models == expected_segments_models


@responses.activate
def test_get_segments_models_without_combined_model_id():
    add_response(
        "https://host_name.com/projects/projectA/", project_a_json, method=responses.GET,
    )
    add_response(
        "https://host_name.com/projects/projectB/", project_b_json, method=responses.GET,
    )

    mock_combined_model = mock.Mock(
        get_segments_info=mock.MagicMock(
            return_value=[
                mock.Mock(segment="segment_a", project_id="projectA"),
                mock.Mock(segment="segment_b", project_id="projectB"),
            ]
        ),
        id="combinedModelId",
    )

    with mock.patch.object(Project, "get_models") as mock_project_get_models:
        mock_project_get_models.return_value = ["model"]

        project = Project(id=_project_id)
        project.get_combined_models = mock.MagicMock(return_value=[mock_combined_model])

        # Test with segment keys
        expected_segments_models = [
            {
                "segment": "segment_a",
                "project_id": "projectA",
                "parent_project_id": "projectId",
                "combined_model_id": "combinedModelId",
                "models": ["model"],
            },
            {
                "segment": "segment_b",
                "project_id": "projectB",
                "parent_project_id": "projectId",
                "combined_model_id": "combinedModelId",
                "models": ["model"],
            },
        ]
        segments_models = project.get_segments_models()
        assert segments_models == expected_segments_models


def test_get_segments_models_without_combined_model_id_fails_with_more_than_one():
    project = Project(id=_project_id)
    project.get_combined_models = mock.MagicMock(return_value=["combined-1", "combined-2"])

    # Test with segment keys
    err = "More than 1 combined_model_id was found, please specify the id that you wish to use."
    with pytest.raises(ValueError, match=err):
        project.get_segments_models()

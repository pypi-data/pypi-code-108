import os
from unittest.mock import ANY, Mock, mock_open, patch

import pytest

from anyscale.client.openapi_client.models.project import Project
from anyscale.client.openapi_client.models.project_response import ProjectResponse
from anyscale.client.openapi_client.models.session import Session
from anyscale.client.openapi_client.models.session_list_response import (
    SessionListResponse,
)
from anyscale.project import (
    create_new_proj_def,
    get_proj_id_from_name,
    get_proj_name_from_id,
    get_project_session,
    get_project_sessions,
    ProjectDefinition,
    register_or_attach_to_project,
)


def test_get_project_sessions(session_test_data: Session) -> None:
    mock_api_client = Mock()
    mock_api_client.list_sessions_api_v2_sessions_get.return_value = SessionListResponse(
        results=[session_test_data]
    )

    sessions = get_project_sessions(session_test_data.project_id, None, mock_api_client)

    assert sessions == [session_test_data]
    mock_api_client.list_sessions_api_v2_sessions_get.assert_called_once_with(
        project_id=session_test_data.project_id,
        name=None,
        state_filter=["AwaitingFileMounts", "Running"],
        _request_timeout=ANY,
    )

    sessions = get_project_sessions(
        session_test_data.project_id, None, mock_api_client, all_active_states=True
    )

    assert sessions == [session_test_data]
    mock_api_client.list_sessions_api_v2_sessions_get.assert_called_with(
        project_id=session_test_data.project_id,
        name=None,
        active_only=True,
        _request_timeout=ANY,
    )


def test_get_project_session(session_test_data: Session) -> None:
    mock_api_client = Mock()
    mock_api_client.list_sessions_api_v2_sessions_get.return_value = SessionListResponse(
        results=[session_test_data]
    )

    session = get_project_session(session_test_data.project_id, None, mock_api_client)

    assert session == session_test_data
    mock_api_client.list_sessions_api_v2_sessions_get.assert_called_once_with(
        project_id=session_test_data.project_id,
        name=None,
        state_filter=["AwaitingFileMounts", "Running"],
        _request_timeout=ANY,
    )


def test_get_proj_name_from_id(project_test_data: Project) -> None:
    mock_api_client = Mock()
    mock_api_client.get_project_api_v2_projects_project_id_get.return_value = ProjectResponse(
        result=project_test_data
    )
    project_name = get_proj_name_from_id(project_test_data.id, mock_api_client)

    assert project_name == project_test_data.name
    mock_api_client.get_project_api_v2_projects_project_id_get.assert_called_once_with(
        project_id=project_test_data.id, _request_timeout=ANY,
    )


@pytest.mark.parametrize("owner", [None, "owner"])
def test_get_proj_id_from_name(project_test_data: Project, owner: str) -> None:
    mock_api_client = Mock()
    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.return_value.results = [
        project_test_data
    ]
    project_id = get_proj_id_from_name(project_test_data.name, mock_api_client)

    assert project_id == project_test_data.id
    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.assert_called_once_with(
        name=project_test_data.name, _request_timeout=ANY, owner=None
    )


def test_create_new_proj_def(project_test_data: Project) -> None:
    mock_api_client = Mock()

    project_name, project_definition = create_new_proj_def(
        project_test_data.name, api_client=mock_api_client,
    )

    assert project_name == project_test_data.name
    assert os.path.normpath(project_definition.root) == os.getcwd()


def test_register_project(project_test_data: Project) -> None:
    mock_api_client = Mock()
    # Mock no existing project
    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.return_value.results = (
        []
    )
    mock_api_client.create_project_api_v2_projects_post.return_value.result.id = (
        project_test_data.id
    )

    project_definition = ProjectDefinition(os.getcwd())
    project_definition.config["name"] = project_test_data.name

    with patch("builtins.open", new_callable=mock_open()), patch(
        "yaml.dump"
    ) as mock_dump:
        register_or_attach_to_project(project_definition, mock_api_client)

        mock_dump.assert_called_once_with({"project_id": project_test_data.id}, ANY)

    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.assert_called_once_with(
        project_test_data.name
    )
    mock_api_client.create_project_api_v2_projects_post.assert_called_once_with(
        write_project={
            "name": project_test_data.name,
            "description": "",
            "initial_cluster_config": None,
        }
    )


def test_register_or_attach_to_project_attach_to_existing(
    project_test_data: Project,
) -> None:
    mock_api_client = Mock()
    # Mock project already exists
    mock_project = Mock()
    mock_project.id = "prj_10"
    mock_project.name = project_test_data.name
    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.return_value.results = [
        mock_project
    ]
    mock_api_client.create_project_api_v2_projects_post.return_value.result.id = (
        project_test_data.id
    )
    project_definition = ProjectDefinition(os.getcwd())
    project_definition.config["name"] = project_test_data.name

    with patch("builtins.open", new_callable=mock_open()), patch(
        "yaml.dump"
    ) as mock_dump:
        register_or_attach_to_project(project_definition, mock_api_client)

        mock_dump.assert_called_once_with({"project_id": "prj_10"}, ANY)

    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.assert_called_once_with(
        project_test_data.name
    )
    mock_api_client.create_project_api_v2_projects_post.assert_not_called()

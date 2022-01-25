import os
from typing import Optional
from unittest.mock import ANY, Mock, mock_open as mock_open_factory, patch

import pytest

from anyscale.client.openapi_client import Project, UserInfo
from anyscale.client.openapi_client.models.project_list_response import (
    ProjectListResponse,
)
from anyscale.controllers.project_controller import (
    COMPUTE_CONFIG_FILENAME,
    ProjectController,
)
from anyscale.project import ProjectDefinition


@pytest.fixture()
def mock_api_client(project_test_data: Project) -> Mock:
    mock_api_client = Mock()

    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.return_value = ProjectListResponse(
        results=[project_test_data]
    )
    mock_api_client.list_sessions_api_v2_sessions_get.return_value.results = []
    mock_api_client.get_project_latest_cluster_config_api_v2_projects_project_id_latest_cluster_config_get.return_value.result.config = (
        ""
    )

    return mock_api_client


@pytest.fixture()
def mock_auth_api_client(mock_api_client: Mock, base_mock_anyscale_api_client: Mock):
    mock_auth_api_client = Mock(
        api_client=mock_api_client, anyscale_api_client=base_mock_anyscale_api_client,
    )
    with patch.multiple(
        "anyscale.controllers.base_controller",
        get_auth_api_client=Mock(return_value=mock_auth_api_client),
    ):
        yield


@pytest.mark.parametrize("owner", [None, "owner"])
def test_clone_project(
    project_test_data: Project, owner: Optional[str], mock_auth_api_client
) -> None:
    project_controller = ProjectController()
    project_controller._write_sample_compute_config = Mock()  # type: ignore

    os_makedirs_mock = Mock(return_value=None)
    mock_write_project_file_to_disk = Mock(return_value=None)
    with patch.multiple("os", makedirs=os_makedirs_mock), patch(
        "anyscale.controllers.project_controller._write_project_file_to_disk"
    ) as mock_write_project_file_to_disk:
        project_controller.clone(project_name=project_test_data.name, owner=owner)

    project_controller.api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.assert_called_once_with(
        name=project_test_data.name, _request_timeout=ANY, owner=owner
    )
    os_makedirs_mock.assert_called_once_with(project_test_data.name)
    mock_write_project_file_to_disk.assert_called_once_with(
        project_test_data.id, project_test_data.name
    )

    project_controller._write_sample_compute_config.assert_called_once_with(
        filepath=os.path.join(project_test_data.name, COMPUTE_CONFIG_FILENAME),
        project_id=project_test_data.id,
    )


def test_init_project(project_test_data: Project, mock_auth_api_client) -> None:
    project_controller = ProjectController()
    project_controller._write_sample_compute_config = Mock()  # type: ignore
    project_definition = ProjectDefinition(os.getcwd())
    project_definition.config["name"] = project_test_data.name
    mock_create_new_proj_def = Mock(
        return_value=(project_test_data.name, project_definition)
    )
    mock_register_project = Mock()
    os_path_exists_mock = Mock(return_value=False)

    with patch.multiple(
        "anyscale.controllers.project_controller",
        create_new_proj_def=mock_create_new_proj_def,
        register_or_attach_to_project=mock_register_project,
    ), patch.multiple("os.path", exists=os_path_exists_mock):
        project_controller.init(project_id=None, name=project_test_data.name)

    mock_create_new_proj_def.assert_called_once_with(
        project_test_data.name, api_client=project_controller.api_client,
    )
    mock_register_project.assert_called_once_with(
        project_definition, project_controller.api_client
    )


def test_init_project_with_id(project_test_data: Project, mock_auth_api_client) -> None:
    project_controller = ProjectController()
    project_controller._write_sample_compute_config = Mock()  # type: ignore
    project_definition = ProjectDefinition(os.getcwd())
    project_definition.config["name"] = project_test_data.name
    mock_create_new_proj_def = Mock(
        return_value=(project_test_data.name, project_definition)
    )
    mock_register_project = Mock()
    mock_attach_to_project_with_id = Mock()
    os_path_exists_mock = Mock(return_value=False)

    with patch.multiple(
        "anyscale.controllers.project_controller",
        create_new_proj_def=mock_create_new_proj_def,
        register_or_attach_to_project=mock_register_project,
        attach_to_project_with_id=mock_attach_to_project_with_id,
    ), patch.multiple("os.path", exists=os_path_exists_mock):
        project_controller.init(project_id=project_test_data.id, name=None)

    mock_create_new_proj_def.assert_not_called()
    mock_attach_to_project_with_id.assert_called_once_with(
        project_test_data.id, project_controller.api_client
    )
    mock_register_project.assert_not_called()


@pytest.mark.parametrize("project_id", [None, "mock-project-id"])
@pytest.mark.parametrize("project_last_cloud_id", [None, "mock-project-cloud-id"])
@pytest.mark.parametrize("org_default_cloud", [None, "mock-default-cloud-id"])
def test_write_sample_compute_config(
    mock_auth_api_client,
    project_id: Optional[str],
    project_last_cloud_id: Optional[str],
    org_default_cloud: Optional[str],
    userinfo_test_data: UserInfo,
) -> None:
    project_controller = ProjectController()

    # Set up mocks.
    project_controller.anyscale_api_client.get_project.return_value.result.last_used_cloud_id = (
        project_last_cloud_id
    )
    first_mock_cloud_record = Mock()
    first_mock_cloud_record.id = "first-mock-cloud-id"
    last_mock_cloud_record = Mock()
    last_mock_cloud_record.id = "last-mock-cloud-id"
    project_controller.api_client.list_clouds_api_v2_clouds_get.return_value.results = [
        first_mock_cloud_record,
        last_mock_cloud_record,
    ]
    mock_config = Mock()
    mock_config.to_dict = Mock(return_value={"mock-config-key": "mock-config-value"})
    project_controller.api_client.get_default_compute_config_api_v2_compute_templates_default_cloud_id_get.return_value.result = (
        mock_config
    )

    userinfo_test_data.organizations[0].default_cloud_id = org_default_cloud
    project_controller.api_client.get_user_info_api_v2_userinfo_get.return_value.result = (
        userinfo_test_data
    )

    # Run the test.
    with patch("builtins.open", mock_open_factory()) as mock_open, patch(
        "anyscale.controllers.project_controller.get_cloud_id_and_name", Mock()
    ) as mock_get_cloud_id:

        # write_sample_compute_config with default cloud.
        if org_default_cloud:
            project_controller._write_sample_compute_config(filepath="mock-fp")
            project_controller.api_client.get_default_compute_config_api_v2_compute_templates_default_cloud_id_get.assert_called_once_with(
                cloud_id=org_default_cloud
            )
            mock_get_cloud_id.assert_called_once_with(
                project_controller.api_client, cloud_id=org_default_cloud
            )
            mock_open.assert_called_once_with("mock-fp", "w")
        # write_sample_compute_config with no project ID.
        elif not project_id:
            project_controller._write_sample_compute_config(filepath="mock-fp")

            project_controller.anyscale_api_client.get_project.assert_not_called()
            project_controller.api_client.list_clouds_api_v2_clouds_get.assert_called_once_with()
            project_controller.api_client.get_default_compute_config_api_v2_compute_templates_default_cloud_id_get.assert_called_once_with(
                cloud_id=last_mock_cloud_record.id
            )
            mock_open.assert_called_once_with("mock-fp", "w")

        # write_sample_compute_config
        # with project ID, but no default cloud there.
        elif not project_last_cloud_id:
            project_controller._write_sample_compute_config(
                filepath="mock-fp", project_id=project_id
            )

            project_controller.anyscale_api_client.get_project.assert_called_once_with(
                project_id
            )
            project_controller.api_client.list_clouds_api_v2_clouds_get.assert_called_once_with()
            project_controller.api_client.get_default_compute_config_api_v2_compute_templates_default_cloud_id_get.assert_called_once_with(
                cloud_id=last_mock_cloud_record.id
            )
            mock_open.assert_called_once_with("mock-fp", "w")

        # write_sample_compute_config
        # with project ID, and with a default cloud there.
        else:
            project_controller._write_sample_compute_config(
                filepath="mock-fp", project_id=project_id
            )

            project_controller.anyscale_api_client.get_project.assert_called_once_with(
                project_id
            )
            project_controller.api_client.list_clouds_api_v2_clouds_get.assert_not_called()
            project_controller.api_client.get_default_compute_config_api_v2_compute_templates_default_cloud_id_get.assert_called_once_with(
                cloud_id=project_last_cloud_id
            )
            mock_open.assert_called_once_with("mock-fp", "w")


@pytest.mark.parametrize("name", ["", "project_a"])
@pytest.mark.parametrize("json_format", [True, False])
@pytest.mark.parametrize("any_creator", [True, False])
def test_list(mock_auth_api_client, name: str, json_format: bool, any_creator: bool):

    project_controller = ProjectController()
    mock_creator_id = "usr_abc"
    mock_userinfo_response = Mock()
    mock_userinfo_response_result = Mock()
    mock_userinfo_response.result = mock_userinfo_response_result
    mock_userinfo_response_result.id = mock_creator_id
    mock_get_user_info_api_v2_userinfo_get = Mock(return_value=mock_userinfo_response)

    project_controller.api_client.get_user_info_api_v2_userinfo_get = (
        mock_get_user_info_api_v2_userinfo_get
    )

    mock_paging_token = None
    mock_metadata = Mock()
    mock_metadata.next_paging_token = mock_paging_token

    mock_project_a = Mock()
    mock_project_a.id = "prj_a"
    mock_project_a.name = "project_a"
    mock_project_a.description = "description for project a"

    mock_project_b = Mock()
    mock_project_b.id = "prj_b"
    mock_project_b.name = "project_b"
    mock_project_b.description = "description for project b"

    mock_response = Mock()
    mock_response.metadata = mock_metadata
    mock_response.results = [mock_project_a, mock_project_b]

    # self.anyscale_api_client.search_projects(project_query)
    mock_search_projects = Mock(return_value=mock_response)
    project_controller.anyscale_api_client.search_projects = mock_search_projects

    project_controller.list(name, json_format, any_creator, max_items=20)

    if any_creator:
        project_controller.api_client.get_user_info_api_v2_userinfo_get.assert_not_called()
    else:
        project_controller.api_client.get_user_info_api_v2_userinfo_get.assert_called_once_with()

    project_controller.anyscale_api_client.search_projects.assert_called_once()
    (
        projects_query,
    ) = project_controller.anyscale_api_client.search_projects.call_args[0]
    if name:
        assert projects_query.name.equals == name
    else:
        assert projects_query.name is None
    if any_creator:
        assert projects_query.creator_id is None
    else:
        assert projects_query.creator_id.equals == mock_creator_id
    assert projects_query.paging.count == 20
    assert projects_query.paging.paging_token is None

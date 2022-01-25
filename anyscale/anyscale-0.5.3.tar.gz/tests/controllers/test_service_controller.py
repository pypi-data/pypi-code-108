import json
from unittest.mock import Mock, mock_open, patch

import pytest

from anyscale.client.openapi_client import CreateProductionService, ProductionJobConfig
from anyscale.controllers.service_controller import ServiceController


@pytest.mark.parametrize("use_default_project", [True, False])
def test_submit_service(mock_auth_api_client, use_default_project: bool,) -> None:
    config_dict = {
        "entrypoint": "mock_entrypoint",
        "build_id": "mock_build_id",
        "compute_config_id": "mock_compute_config_id",
        "healthcheck_url": "mock_healthcheck_url",
    }
    service_controller = ServiceController()
    mock_project_definition = Mock()
    mock_project_definition.root = "/some/directory"
    if use_default_project:
        mock_find_project_root = Mock(return_value=None)
        service_controller.anyscale_api_client.get_default_project = Mock(
            return_value=Mock(result=Mock(id="mock_default_project_id"))
        )
    else:
        mock_find_project_root = Mock(return_value="root_path")

    mock_get_project_id = Mock(return_value="mock_project_id")

    mock_validate_successful_build = Mock()

    with patch(
        "builtins.open", mock_open(read_data=json.dumps(config_dict))
    ), patch.multiple(
        "anyscale.controllers.service_controller",
        find_project_root=mock_find_project_root,
        get_project_id=mock_get_project_id,
    ), patch.multiple(
        "anyscale.controllers.job_controller",
        validate_successful_build=mock_validate_successful_build,
    ), patch.multiple(
        "os.path", exists=Mock(return_value=True)
    ):
        service_controller.deploy(
            "mock_config_file", name="mock_name", description="mock_description"
        )
    if use_default_project:
        service_controller.anyscale_api_client.get_default_project.assert_called_once_with()
    service_controller.api_client.create_service_api_v2_decorated_ha_jobs_create_service_post.assert_called_once_with(
        CreateProductionService(
            name="mock_name",
            description="mock_description",
            project_id="mock_default_project_id"
            if use_default_project
            else "mock_project_id",
            config=ProductionJobConfig(
                **{
                    "entrypoint": "mock_entrypoint",
                    "build_id": "mock_build_id",
                    "compute_config_id": "mock_compute_config_id",
                }
            ),
            healthcheck_url="mock_healthcheck_url",
        )
    )

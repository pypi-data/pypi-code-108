from datetime import datetime
import os
from typing import Optional

import click
from pydantic import Field
import yaml

from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client import CreateProductionService, ProductionJobConfig
from anyscale.controllers.base_controller import BaseController
from anyscale.controllers.job_controller import JobConfig, JobController
from anyscale.project import find_project_root, get_project_id, ProjectDefinition
from anyscale.util import get_endpoint


class ServiceConfig(JobConfig):
    healthcheck_url: str = Field(..., description="Healthcheck url for service.")


class ServiceController(BaseController):
    def __init__(
        self, log: BlockLogger = BlockLogger(), initialize_auth_api_client: bool = True
    ):
        super().__init__(initialize_auth_api_client=initialize_auth_api_client)
        self.log = log
        self.job_controller = JobController(
            initialize_auth_api_client=initialize_auth_api_client
        )

    def deploy(
        self, service_config_file: str, name: Optional[str], description: Optional[str]
    ) -> None:
        # Check directory of .anyscale.yaml to decide whether to use default project.
        root_dir = find_project_root(os.getcwd())
        if root_dir is not None:
            project_definition = ProjectDefinition(root_dir)
            project_id = get_project_id(project_definition.root)
        else:
            default_project = self.anyscale_api_client.get_default_project().result
            project_id = default_project.id
            self.log.info(
                f"No project context detected, so using default project {project_id}."
            )

        if not os.path.exists(service_config_file):
            raise click.ClickException(f"Config file {service_config_file} not found.")

        with open(service_config_file, "r") as f:
            config_dict = yaml.safe_load(f)

        service_config = ServiceConfig.parse_obj(config_dict)
        config_object = ProductionJobConfig(
            entrypoint=service_config.entrypoint,
            runtime_env=service_config.runtime_env,
            build_id=service_config.build_id,
            compute_config_id=service_config.compute_config_id,
            max_retries=service_config.max_retries,
        )

        service = self.api_client.create_service_api_v2_decorated_ha_jobs_create_service_post(
            CreateProductionService(
                name=name
                or service_config.name
                or "cli-job-{}".format(datetime.now().isoformat()),
                description=description
                or service_config.description
                or "Service deployed from CLI",
                project_id=project_id,
                config=config_object,
                healthcheck_url=service_config.healthcheck_url,
            )
        ).result

        self.log.info(
            f"Service {service.id} has been deployed. Current state of service: {service.state.current_state}."
        )
        self.log.info(
            f"Query the status of the service with `anyscale service list --service-id {service.id}`."
        )
        self.log.info(
            f'View the service in the UI at {get_endpoint(f"/services/{service.id}")}.'
        )

    def list(
        self,
        include_all_users: bool,
        name: Optional[str],
        service_id: Optional[str],
        project_id: Optional[str],
        max_items: int,
    ) -> None:
        self.job_controller.list(
            include_all_users,
            name,
            service_id,
            project_id,
            max_items=max_items,
            is_service=True,
        )

    def terminate(self, service_id: Optional[str], service_name: Optional[str]) -> None:
        self.job_controller.terminate(service_id, service_name, is_service=True)

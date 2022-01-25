import os
from typing import Optional, Tuple

import click
import yaml

import anyscale
from anyscale.authenticate import get_auth_api_client
from anyscale.cli_logger import BlockLogger
import anyscale.conf
from anyscale.utils.connect_helpers import find_project_id


class ProjectBlock:
    """
    Class to determine which project ray.client uses. This class should never be
    instantiated directly. Instead call `get_project_block` to ensure a new
    ProjectBlock object is correctly created.
    """

    def __init__(
        self, project_dir: Optional[str] = None, project_name: Optional[str] = None,
    ):
        """
        If project_dir is passed or exists in the directory structure: ensure the project_dir
            is correctly set up. Otherwise use the default project.
        Create an ProjectBlock object with the following properties that are useful
        externally: project_id, project_name, project_dir.

        Arguments:
            project_dir (Optional[str]): Project directory location. This doesn't need to contain
                a .anyscale.yaml file.
            project_name (Optional[str]): Project name if it is necessary to register the project
                with Anyscale. This will not be used if a registered project already exists
                in the project_dir.
        """
        self.log = BlockLogger()
        auth_api_client = get_auth_api_client()
        self.api_client = auth_api_client.api_client
        self.anyscale_api_client = auth_api_client.anyscale_api_client
        self.project_dir = (
            os.path.abspath(os.path.expanduser(project_dir)) if project_dir else None
        )

        self.block_label = "Project"
        self.log.open_block(self.block_label, block_title="Choosing a project")

        if self.project_dir is None:
            self.project_dir = anyscale.project.find_project_root(os.getcwd())
        if self.project_dir:
            self.project_id, self.project_name = self._ensure_project_setup_at_dir(
                self.project_dir, project_name
            )
            left_pad = " " * 2
            self.log.info(
                f"{left_pad}{'name:': <20}{self.project_name}",
                block_label=self.block_label,
            )
            self.log.info(
                f"{left_pad}{'project id:': <20}{self.project_id}",
                block_label=self.block_label,
            )
            self.log.info(
                f"{left_pad}{'project directory:': <20}{self.project_dir}",
                block_label=self.block_label,
            )
        else:
            self.project_id, self.project_name = self._get_default_project()
        self.log.close_block(self.block_label)

    def _get_default_project(self) -> Tuple[str, str]:
        """
        Get default project id and name.

        Returns:
        The project id and project name of the project being used.
        """
        default_project = self.anyscale_api_client.get_default_project().result
        project_id = default_project.id
        project_name = default_project.name
        self.log.info(
            "No project defined. Continuing without a project.",
            block_label=self.block_label,
        )
        return project_id, project_name

    def _ensure_project_setup_at_dir(
        self, project_dir: str, project_name: Optional[str]
    ) -> Tuple[str, str]:
        """
        Get or create an Anyscale project rooted at the given dir. If .anyscale.yaml
        exists in the given project dir and that project is registered with Anyscale,
        return information about that project. Otherwise, create a project with this
        project_dir and project_name (use default if not provided).

        Returns:
        The project id and project name of the project being used.
        """
        os.makedirs(project_dir, exist_ok=True)
        if project_name is None:
            project_name = os.path.basename(project_dir)

        # If the project yaml exists, assume we're already setup.
        project_yaml = os.path.join(project_dir, ".anyscale.yaml")
        if os.path.exists(project_yaml):
            proj_def = anyscale.project.ProjectDefinition(project_dir)
            project_id: Optional[str] = anyscale.project.get_project_id(proj_def.root)
            if not project_id:
                raise click.ClickException(
                    f"{project_yaml} is not correctly formatted. Please attach to a different "
                    "project using `anyscale project init`."
                )
            try:
                project_response = self.anyscale_api_client.get_project(project_id)
            except click.ClickException:
                raise click.ClickException(
                    f"Unable to get project with id {project_id} from Anyscale. Please attach to "
                    "a different project using `anyscale project init`."
                )
            self.log.info(
                f"Using the project defined in {project_yaml}:",
                block_label=self.block_label,
            )
            return project_id, project_response.result.name

        project_id = find_project_id(self.anyscale_api_client, project_name)
        if project_id is None:
            self.log.info(
                f"Creating new project named {BlockLogger.highlight(project_name)} for local dir {project_dir}",
                block_label=self.block_label,
            )
            self.log.info(
                f"Using the project {BlockLogger.highlight(project_name)}:",
                block_label=self.block_label,
            )
            project_response = self.anyscale_api_client.create_project(
                {
                    "name": project_name,
                    "description": "Automatically created by Anyscale Connect",
                }
            )
            project_id = project_response.result.id
        else:
            self.log.info(
                f"Connecting local directory {project_dir} to project {BlockLogger.highlight(project_name)}",
                block_label=self.block_label,
            )
            self.log.info(
                f"Using the project {BlockLogger.highlight(project_name)}:",
                block_label=self.block_label,
            )

        if not os.path.exists(project_yaml):
            with open(project_yaml, "w+") as f:
                f.write(yaml.dump({"project_id": project_id}))

        return project_id, project_name


def create_project_block(
    project_dir: Optional[str] = None, project_name: Optional[str] = None
):
    """
    Function to create new ProjectBlock object. The ProjectBlock object
    is not a global variable an will be reinstantiated on each call to
    get_project_block.
    """
    return ProjectBlock(project_dir=project_dir, project_name=project_name)

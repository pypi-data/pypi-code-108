import os
from typing import Any, Optional, Tuple

import click
from click import ClickException
import yaml

import anyscale
from anyscale.authenticate import get_auth_api_client
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client import Project
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.shared_anyscale_utils.util import slugify
from anyscale.util import get_endpoint, send_json_request


ANYSCALE_PROJECT_FILE = ".anyscale.yaml"
log = BlockLogger()


def find_project_root(directory: str) -> Optional[str]:
    """Find root directory of the project.
    Args:
        directory (str): Directory to start the search in.
    Returns:
        Path of the parent directory containing the project
        or None if no such project is found.
    """
    prev, directory = None, os.path.abspath(directory)
    while prev != directory:
        if os.path.exists(os.path.join(directory, ANYSCALE_PROJECT_FILE)):
            return directory
        prev, directory = directory, os.path.abspath(os.path.join(directory, os.pardir))
    return None


class ProjectDefinition(object):
    def __init__(self, root_dir: str):
        self.root = os.path.join(root_dir, "")
        anyscale_yaml = os.path.join(root_dir, ANYSCALE_PROJECT_FILE)
        if os.path.exists(anyscale_yaml):
            with open(anyscale_yaml) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}


def load_project_or_throw() -> ProjectDefinition:
    # First check if there is a .anyscale.yaml.
    root_dir = find_project_root(os.getcwd())
    if not root_dir:
        raise ClickException("No project directory found")
    return ProjectDefinition(root_dir)


def get_project_id(project_dir: str) -> str:
    """
    Args:
        project_dir: Project root directory.
    Returns:
        The ID of the associated Project in the database.
    Raises:
        ValueError: If the current project directory does
            not contain a project ID.
    """
    project_filename = os.path.join(project_dir, ANYSCALE_PROJECT_FILE)
    if os.path.isfile(project_filename):
        with open(project_filename) as f:
            config = yaml.safe_load(f)
            project_id = config["project_id"]
    else:
        # TODO(pcm): Consider doing this for the user and retrying the command
        # they were trying to run.
        raise ClickException(
            "Ray project in {} not registered yet. "
            "Did you run 'anyscale project init'?".format(project_dir)
        )
    try:
        result = str(project_id)
    except ValueError:
        # TODO(pcm): Tell the user what to do here.
        raise ClickException(
            "{} does not contain a valid project ID".format(project_filename)
        )
    return result


def validate_project_name(project_name: str) -> bool:
    return " " not in project_name.strip()


def get_project_sessions(
    project_id: str,
    session_name: Optional[str],
    api_client: DefaultApi = None,
    all_active_states: bool = False,
) -> Any:
    """
    Returns active project clusters. If `all_active_states` is set, returns clusters with
        the following states: StartingUp, _StartingUp, StartupErrored, Running, Updating,
        UpdatingErrored, AwaitingFileMounts. Otherwise, only return clusters in the
        Running and AwaitingFileMounts state.
    """
    if api_client is None:
        return _get_project_sessions(project_id, session_name)

    if all_active_states:
        response = api_client.list_sessions_api_v2_sessions_get(
            project_id=project_id,
            name=session_name,
            active_only=True,
            _request_timeout=30,
        )
    else:
        response = api_client.list_sessions_api_v2_sessions_get(
            project_id=project_id,
            name=session_name,
            state_filter=["AwaitingFileMounts", "Running"],
            _request_timeout=30,
        )
    sessions = response.results
    if len(sessions) == 0:
        raise ClickException(
            "No active cluster matching pattern {} found".format(session_name)
        )
    return sessions


# TODO (jbai): DEPRECATED - will be removed when OpenApi migration is completed
def _get_project_sessions(project_id: str, session_name: Optional[str]) -> Any:
    response = send_json_request(
        "/api/v2/sessions/",
        {"project_id": project_id, "name_match": session_name, "active_only": True},
    )
    sessions = response["results"]
    if len(sessions) == 0:
        raise ClickException(
            "No active cluster matching pattern {} found".format(session_name)
        )
    return sessions


def get_project_session(
    project_id: str, session_name: Optional[str], api_client: DefaultApi = None
) -> Any:
    if api_client is None:
        return _get_project_session(project_id, session_name)

    sessions = get_project_sessions(project_id, session_name, api_client)
    if len(sessions) > 1:
        raise ClickException(
            "Multiple active clusters: {}\n"
            "Please specify the one you want to refer to.".format(
                [session.name for session in sessions]
            )
        )
    return sessions[0]


# TODO (jbai): DEPRECATED - will be removed when OpenApi migration is completed
def _get_project_session(project_id: str, session_name: Optional[str]) -> Any:
    sessions = get_project_sessions(project_id, session_name)
    if len(sessions) > 1:
        raise ClickException(
            "Multiple active clusters: {}\n"
            "Please specify the one you want to refer to.".format(
                [session["name"] for session in sessions]
            )
        )
    return sessions[0]


def get_proj_name_from_id(project_id: str, api_client: DefaultApi) -> str:
    resp = api_client.get_project_api_v2_projects_project_id_get(
        project_id=project_id, _request_timeout=30
    )

    if resp is None:
        raise ClickException(
            "This local project is not registered with anyscale. Please re-run `anyscale project init`."
        )
    else:
        return str(resp.result.name)


def get_proj_id_from_name(
    project_name: str,
    api_client: Optional[DefaultApi] = None,
    owner: Optional[str] = None,  # this can be the email or the username of the owner
) -> str:
    if api_client is None:
        api_client = get_auth_api_client().api_client

    resp = api_client.find_project_by_project_name_api_v2_projects_find_by_name_get(
        name=project_name, _request_timeout=30, owner=owner
    )

    if not resp.results:
        raise ClickException(
            f"There is no project '{project_name}' that is registered with Anyscale. "
            "View the registered projects with `anyscale project list`."
        )

    projects = resp.results
    my_projects = [x for x in projects if x.is_owner]

    selected_project = None

    # If there is more than one result, choose the one that you own
    # If there is one project, select it
    if len(projects) == 1:
        selected_project = projects[0]

    # Only one of the projects is mine. Let's select this one
    elif len(my_projects) == 1:
        selected_project = my_projects[0]

    # We know there is at least one element. If none of the projects are mine
    # then we don't know which one to select
    else:
        raise ClickException(
            f"There are multiple projects '{project_name}' registered with Anyscale. "
            "View the registered projects with `anyscale project list`."
            "Please specify the --owner flag to specify an alternate owner"
        )

    # Return the id of this project
    return str(selected_project.id)


def _write_project_file_to_disk(project_id: str, directory: str) -> None:
    with open(os.path.join(directory, ANYSCALE_PROJECT_FILE), "w") as f:
        f.write("{}".format("project_id: {}".format(project_id)))


def create_new_proj_def(
    name: str, api_client: DefaultApi = None,
) -> Tuple[str, ProjectDefinition]:
    if slugify(name) != name:
        name = slugify(name)
        log.info("Normalized project name to {}".format(name))

    project_definition = anyscale.project.ProjectDefinition(os.getcwd())
    project_definition.config["name"] = name
    return name, project_definition


def _do_attach(project_id: str, is_create_project: bool) -> None:
    with open(anyscale.project.ANYSCALE_PROJECT_FILE, "w") as f:
        yaml.dump(
            {"project_id": project_id}, f,
        )

    # Print success message
    url = get_endpoint(f"/projects/{project_id}")
    if is_create_project:
        log.info(f"Project {project_id} created. View at {url}")
    else:
        log.info(f"Attached to project {project_id}. View at {url}")


def register_or_attach_to_project(
    project_definition: ProjectDefinition, api_client: DefaultApi
) -> None:

    project_name = project_definition.config["name"]
    description = project_definition.config.get("description", "")

    # Find if project with name already exists
    existing_projects = api_client.find_project_by_project_name_api_v2_projects_find_by_name_get(
        project_name
    )
    existing_project = None
    if existing_projects:
        if len(existing_projects.results) == 1:
            existing_project = existing_projects.results[0]
        elif len(existing_projects.results) > 1:
            try:
                user_info = api_client.get_user_info_api_v2_userinfo_get()
            except Exception:
                raise ClickException(
                    f"More than one project with name {project_name} was found. Please connect to this project using --project-id parameter"
                )

            for project in existing_projects.results:
                if project.creator_id == user_info.result.id:
                    existing_project = project

            if not existing_project:
                raise ClickException(
                    f"More than one project with name {project_name} was found. Please connect to this project using --project-id parameter"
                )
            else:
                log.info(
                    f"Multiple projects with name {project_name} was found. Connecting to the one created by you."
                )

    if not existing_project:
        # Add a database entry for the new Project.
        resp = api_client.create_project_api_v2_projects_post(
            write_project={
                "name": project_name,
                "description": description,
                "initial_cluster_config": None,
            }
        )
        result = resp.result
        project_id = result.id
    else:
        project_id = existing_project.id

    _do_attach(project_id, not existing_project)


def attach_to_project_with_id(project_id: str, api_client: DefaultApi) -> None:
    validate_project_id(project_id, api_client)

    _do_attach(project_id, False)


def validate_project_id(project_id, api_client: DefaultApi) -> Project:
    # Find if project with name already exists
    try:
        resp = api_client.get_project_api_v2_projects_project_id_get(project_id)
    except Exception:
        resp = None

    if not resp:
        raise click.ClickException(
            f"Project with id {project_id} does not exist. Instead, you can provide a name to anyscale project init to create a new project."
        )

    return resp.result

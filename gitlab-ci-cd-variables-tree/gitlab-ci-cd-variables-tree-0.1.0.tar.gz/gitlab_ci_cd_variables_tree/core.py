import logging
import sys

from gitlab import Gitlab
from rich import print
from rich.text import Text
from rich.tree import Tree

from .styles import styles

logger = logging.getLogger(__name__)


def show_variables_as_tree(
    gitlab_url: str, gitlab_token: str, gitlab_group_id: str
) -> None:
    try:
        gl = Gitlab(gitlab_url, private_token=gitlab_token)
        gl.auth()
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    else:
        tree = walk_gitlab(gl, gitlab_group_id, None, initial_group=True)
        print(tree)


def walk_gitlab(gl: Gitlab, group_id: int, tree: Tree, initial_group=False) -> None:
    logger.info(f"InitialGroup: {initial_group}")

    group = gl.groups.get(group_id)
    if tree is None:
        tree = Tree(
            create_group_text(group_name=group.name, group_web_url=group.web_url),
            guide_style="bold bright_blue",
        )

    logger.info(f"Group_Id: {group_id}, Group_Name: {group.name}")

    # Group Variables
    for variable in group.variables.list():
        variable_text = create_variable_text(variable.key, variable.variable_type)
        tree.add(variable_text)

    # Projects Variables
    for g_project in group.projects.list():
        project_id = g_project.id

        project = gl.projects.get(project_id)
        logger.info(f"Project_Id: {project_id}, Project_Name: {project.name}")

        project_variables = project.variables.list()

        if len(project_variables) == 0:
            continue

        project_text = create_project_text(
            project_name=project.name, project_web_url=project.web_url
        )
        project_tree = tree.add(project_text)
        for variable in project_variables:
            variable_text = create_variable_text(variable.key, variable.variable_type)
            project_tree.add(variable_text)

    # Subgroups
    for subgroup in group.subgroups.list():
        subgroup_tree = tree.add(
            create_group_text(group_name=subgroup.name, group_web_url=subgroup.web_url),
        )
        logger.info(f"Subgroup_Id: {subgroup.id}")
        walk_gitlab(gl, subgroup.id, subgroup_tree)

    if initial_group:
        logger.info("Return initial group")
        return tree


def create_project_text(project_name: str, project_web_url: str) -> str:
    return f"{styles['project']['icon']} [link={project_web_url}/-/settings/ci_cd]{project_name}"


def create_variable_text(variable_name: str, variable_type: str) -> Text:
    text = Text(variable_name, "green")

    text.append(
        f" ({variable_type})", styles["variable"]["type"].get(variable_type, "white")
    )

    return Text(styles["variable"]["icon"]) + text


def create_group_text(group_name, group_web_url) -> str:
    return (
        f"{styles['group']['icon']} [link={group_web_url}/-/settings/ci_cd]{group_name}"
    )

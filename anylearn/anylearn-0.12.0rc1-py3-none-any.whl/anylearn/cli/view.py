import click

from anylearn.cli.anylearn_cli_config import AnylearnCliConfig
from anylearn.cli.utils import (
    check_connection,
    cmd_confirm_or_abort,
    option_force,
    check_config,
    cmd_error,
    cmd_info,
    cmd_success,
    cmd_warning,
    get_cmd_command,
)
from anylearn.interfaces import Project, TrainTask


@click.group("view")
def commands():
    """
    Show Web UI on specific objects.
    """
    pass


@check_config()
@check_connection()
def __host__():
    config = AnylearnCliConfig.load()
    return config.remote['host']


@commands.command()
@get_cmd_command()
def ui():
    click.launch(__host__())


@commands.command()
@click.argument('project_id')
@get_cmd_command()
def project(project_id):
    host = __host__()
    try:
        Project(id=project_id, load_detail=True)
        click.launch(f"{host}/project/{project_id}/detail")
    except:
        cmd_error(msg=f"Failed to fetch project {project_id}.")
        raise click.Abort


@commands.command()
@click.argument('task_id')
@get_cmd_command()
def task(task_id: str):
    host = __host__()
    task = TrainTask(id=task_id, load_detail=True)
    click.launch(f"{host}/project/{task.project_id}/traintask/{task.id}/detail")

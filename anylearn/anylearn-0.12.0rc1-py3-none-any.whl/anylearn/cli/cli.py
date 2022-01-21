from anylearn.interfaces.train_task import TrainTask
import os
from typing import Optional

import click

import anylearn.cli.add
import anylearn.cli.config
import anylearn.cli.download
import anylearn.cli.push
import anylearn.cli.quota
import anylearn.cli.rm
import anylearn.cli.run
from anylearn.cli.run import (
    _check_algorithm_name,
    _check_project,
    _do_train,
    _load_training_config,
)
import anylearn.cli.task
import anylearn.cli.view
from anylearn.cli.anylearn_cli_config import AnylearnCliConfig
from anylearn.cli.utils import (
    check_config,
    get_history_file_path,
    get_cmd_command,
    cmd_error,
    cmd_info,
    cmd_success,
    cmd_warning,
    check_connection,
    do_login,
    do_logout,
)
from anylearn.interfaces import Project


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
@get_cmd_command()
@click.option(
    '-n', '--project-name',
    default=os.path.basename(os.getcwd()),
    help="Project name.",
)
@click.option(
    '-d', '--project-description',
    default=None,
    help="Project description.",
)
@click.option(
    '--login',
    is_flag=True,
    default=False,
    help="Prompt login in the meantime.",
)
def init(
    project_name: str=os.path.basename(os.getcwd()),
    project_description: str=None,
    login: bool=False,
):
    """
    Create an empty Anylearn project.
    """
    if login:
        do_login(show_success=True)
    config = AnylearnCliConfig.load()
    if config.project and config.project.name:
        cmd_warning(msg=(
            "Project ("
            f"ID={config.project.id}, "
            f"name={config.project.name}, "
            f"description={config.project.description}, "
            ") "
            "has already been initialized in current directory.\n"
            "Call `anyctl push project` to synchronize local project "
            "or `anyctl reset` to reset.\n"
            "Aborted!"
        ))
        return
    config.project = Project(
        name=project_name,
        description=project_description,
    )
    AnylearnCliConfig.update(config)
    cmd_success(msg="Initialized Anylearn project:")
    cmd_info(msg=str(config))


@cli.command()
@check_config()
@get_cmd_command()
def reset():
    """
    Reset current Anylearn project.
    """
    cmd_warning(msg="Project in current directory will be reverted.")
    if click.confirm("Are you sure you want to proceed?"):
        AnylearnCliConfig.get_config_path().unlink()
        cmd_success(msg=(
            "Local project has been reverted.\n"
            "However, runtime files such as <hyperparams>.json are kept. "
            "You can still make use of them in other projects, "
            "or remove them manually when no longer needed."
        ))


@cli.command()
@check_config()
@get_cmd_command()
def login():
    do_login(show_success=True)


@cli.command()
@check_config()
@get_cmd_command()
def logout():
    do_logout()


@cli.command()
@click.option(
    '-f', '--file',
    default="AnylearnTraining.yaml",
    help="""
    Path of training configuration file 
    (default is './AnylearnTraining.yaml')
    .
    """
)
@check_config()
@check_connection()
def train(file: str="AnylearnTraining.yaml"):
    """
    Run training task based on configuration file.
    """
    config = AnylearnCliConfig.load()
    _check_project(config)
    training_config = _load_training_config(file)
    _check_algorithm_name(config, training_config['algorithm_name'])
    task = _do_train(config=config, **training_config)
    cmd_success(msg=f"CREATED {task.id}")


@cli.command()
@click.option(
    '-i', '--task-id',
    type=str,
    help="""
    ID of a certain task to fetch logs.
    If not specified, the last training task's ID will be used.
    """
)
@click.option(
    '-l', '--limit',
    type=int,
    default=100,
    show_default=True,
    help="""
    Max number of lines of logs to fetch.
    """
)
@click.option(
    '-f', '--follow',
    is_flag=True,
    default=False,
    help="""
    Whether the logs should be streamed and printed as they grow.
    """
)
@click.option(
    '--full-export',
    is_flag=True,
    default=False,
    help="""
    Fetch and save full logs into file.
    """
)
@check_config()
@check_connection()
def log(task_id: Optional[str]=None,
        limit: int=100,
        follow: bool=False,
        full_export: bool=False):
    """
    Show or export logs of training task.
    """
    config = AnylearnCliConfig.load()
    _check_project(config)
    if not task_id:
        tasks = config.project.get_train_tasks()
        if not tasks:
            cmd_error(msg=f"No launched training tasks in current project.")
            raise click.Abort
        task_id = sorted(tasks, key=lambda t: t.create_time)[0].id
    if not task_id.startswith('TRAI'):
        cmd_error(msg=f"Command `log` supports training tasks only.")
        raise click.Abort
    task = TrainTask(id=task_id)
    if full_export:
        logs = "\r\n".join(task.get_full_log())
        filename = f"{task_id}.log"
        with open(filename, 'w') as f:
            f.write(logs)
        cmd_success(msg=(
            f"Full log of task {task_id} "
            f"is exported to file {filename}."
        ))
    elif follow:
        for line in task.stream_log(init_limit=limit):
            cmd_info(msg=line)
    else:
        cmd_info(msg="\r\n".join(task.get_last_log(limit=limit)))


@cli.command()
@click.option(
    '-t', '--type',
    type=click.Choice(["get", "clean"]),
    default="get",
    help="""
    Actions on history, default "get".
    """
)
def history(type: str):
    """
    Show project's task history.
    """
    if type == "clean":
        if click.confirm("All cmd history will be cleared, continue?"):
            get_history_file_path().unlink()
            cmd_info(msg="History has been cleared")
        else:
            cmd_info(msg="Cancel clean")
    else:
        with open(get_history_file_path(), 'r') as f:
            command = f.read()
        cmd_info(msg=command)


cli.add_command(anylearn.cli.add.commands)
cli.add_command(anylearn.cli.config.commands)
cli.add_command(anylearn.cli.download.commands)
cli.add_command(anylearn.cli.push.commands)
cli.add_command(anylearn.cli.quota.commands)
cli.add_command(anylearn.cli.rm.commands)
cli.add_command(anylearn.cli.run.commands)
cli.add_command(anylearn.cli.task.commands)
cli.add_command(anylearn.cli.view.commands)


if __name__ == '__main__':
    cli()

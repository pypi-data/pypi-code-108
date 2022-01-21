import json

import click

from anylearn.cli.anylearn_cli_config import AnylearnCliConfig
from anylearn.cli.utils import (
    cmd_confirm_or_abort,
    check_config,
    check_connection,
    cmd_error,
    cmd_info,
    cmd_success,
    cmd_warning,
    get_cmd_command,
)
from anylearn.interfaces import TrainTask


@click.group("task")
def commands():
    """
    Show tasks created within local Anylearn project.
    """
    pass


@commands.command()
@check_config()
@check_connection()
@get_cmd_command()
def ls():
    """
    List all tasks.
    """
    config = AnylearnCliConfig.load()
    if not config.project or not config.project.id:
        cmd_error(msg=(
            "Local project is broken or has not been published to Anylearn remote.\n"
            "Call `anyctl reset` then `anyctl init` if project configuration is corrupted, "
            f"or call `anyctl push project` to publish local project."
        ))
        raise click.Abort
    tasks = config.project.get_train_tasks(load_detail=True)
    algos = []
    for t in tasks:
        try:
            algos.append(next(
                k
                for k, v in config.algorithms.items()
                if v.id == t.algorithm_id
            ))
        except StopIteration:
            algos.append(t.algorithm_id)
    msgs = [
        f"{click.style(t.id, fg='yellow')} <{t.create_time}> <{a}>"
        for t, a in zip(tasks, algos)
    ]
    cmd_info(msg="\n".join(msgs))


@commands.command()
@click.argument('task_id')
@check_config()
@check_connection()
@get_cmd_command()
def get(task_id: str):
    """
    Get task detail.
    """
    config = AnylearnCliConfig.load()
    try:
        task = TrainTask(id=task_id, load_detail=True)
    except:
        cmd_error(msg=f"Failed to get task {task_id}")
        raise click.Abort
    states = {
        '-3': 'Aborted',
        '-2': 'Failed',
        '-1': 'Deleted',
        '0': 'Created',
        '1': 'Running',
        '2': 'Succeeded',
        '3': 'Pending',
        '4': 'Retrying',
        '5': 'Locked',
    }
    cmd_info(msg=(
        f"ID : {task.id}\n"
        f"Name : {task.name}\n"
        f"Description : {task.description}\n"
        f"State : {states.get(str(task.state), 'Unknown')}\n"
        f"Algorithm ID : {task.algorithm_id}\n"
        f"hyperparameters : {task.train_params}\n"
        f"datasets/models : {task.files}\n"
        f"create_time : {task.create_time}\n"
        f"finish_time : {task.finish_time}\n"
        f"final_metric : {task.final_metric}\n"
    ))

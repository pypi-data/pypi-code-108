import click
from requests.models import HTTPError

from anylearn.cli.utils import (
    check_config,
    check_connection,
    cmd_error,
    cmd_info,
    cmd_success,
    get_cmd_command,
)
from anylearn.interfaces.train_task import TrainTask


_option_async_download = click.option(
    '--async-download',
    is_flag=True,
    default=False,
    help="Download in asynchronous mode."
)


@click.group("download")
def commands():
    """
    Download remote task results of training, evaluation or serving.
    """
    pass


@commands.command()
@_option_async_download
@check_config()
@check_connection()
@get_cmd_command()
@click.argument('task_id')
@click.option(
    '-s', '--save-path',
    prompt=True,
    help="Save path of task result download (absolute path)."
)
def training(task_id: str, save_path: str, async_download: bool=False):
    """
    Get training task's results.
    """
    try:
        train_task = TrainTask(id=task_id, load_detail=True)
        cmd_info(msg="DOWNLOADING...")
        res = train_task.download_results(save_path=save_path, async_download=async_download)
    except Exception as e:
        cmd_error(msg=f"{e}")
        cmd_info(msg="STOP DOWNLOAD")
        return
    cmd_success(msg=f"DOWNLOAD! {save_path}\\{res}")


@commands.command()
def evaluation():
    """
    Get evaluation task's results.
    """
    pass


@commands.command()
def serving():
    """
    Get serving task's results.
    """
    pass

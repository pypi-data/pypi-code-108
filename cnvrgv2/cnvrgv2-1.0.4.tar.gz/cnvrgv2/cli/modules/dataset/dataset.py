import os
import click

from cnvrgv2.cli.utils import messages
from cnvrgv2.cli.utils.decorators import prepare_command

from cnvrgv2.config import CONFIG_FOLDER_NAME


@click.group(name='dataset')
def dataset_group():
    pass


@dataset_group.command()
@click.option('-n', '--name', prompt=messages.DATASET_PROMPT_CLONE, help=messages.DATASET_HELP_CLONE)
@click.option('-o', '--override', is_flag=True, default=False, help=messages.DATASET_HELP_CLONE_OVERRIDE)
@prepare_command()
def clone(cnvrg, logger, name, override):
    """
    Clones the given dataset to local folder
    """
    dataset = cnvrg.datasets.get(name)
    logger.info(messages.LOG_CLONING_DATASET.format(name))
    if os.path.exists(dataset.slug + '/' + CONFIG_FOLDER_NAME) and not override:
        logger.log_and_echo(messages.DATASET_CLONE_SKIP.format(name))
        return
    dataset.clone(progress_bar_enabled=True, override=override)
    success_message = messages.DATASET_CLONE_SUCCESS.format(name)
    logger.log_and_echo(success_message)


@dataset_group.command()
@click.option('-n', '--name', prompt=messages.DATASET_PROMPT_NAME, help=messages.DATASET_HELP_NAME)
@click.option('-f', '--files', prompt=messages.DATASET_PUT_PROMPT_FILES, help=messages.DATASET_PUT_HELP_FILES)
@click.option('-g', '--git-diff', is_flag=True, help=messages.DATA_UPLOAD_HELP_GIT_DIFF)
@prepare_command()
def put(cnvrg, logger, name, files, git_diff):
    """
    Uploads the given files to the given dataset
    """
    dataset = cnvrg.datasets.get(name)
    file_paths = files.split(",")
    dataset.put_files(paths=file_paths, progress_bar_enabled=True, git_diff=git_diff)
    logger.log_and_echo(messages.DATA_UPLOAD_SUCCESS)


@dataset_group.command()
@click.option('-g', '--git-diff', is_flag=True, help=messages.DATA_UPLOAD_HELP_GIT_DIFF)
@prepare_command()
def upload(dataset, logger, git_diff):
    """
    Uploads updated files from the current dataset folder
    """
    dataset.upload(progress_bar_enabled=True, git_diff=git_diff)
    logger.log_and_echo(messages.DATA_UPLOAD_SUCCESS)


@dataset_group.command()
@prepare_command()
def download(dataset, logger):
    """
    Downloads updated files to the current dataset folder
    """
    dataset.download(progress_bar_enabled=True)
    logger.log_and_echo(messages.DATA_DOWNLOAD_SUCCESS)


@dataset_group.command()
@click.option('-n', '--name', prompt=messages.DATASET_PROMPT_NAME, help=messages.DATASET_HELP_NAME)
@click.option('-f', '--files', prompt=messages.DATASET_REMOVE_PROMPT_FILES, help=messages.DATASET_REMOVE_HELP_FILES)
@click.option('-m', '--message', help=messages.DATA_COMMIT_MESSAGE, default="")
@prepare_command()
def remove(cnvrg, logger, name, files, message):
    """
    Removes the given files remotely
    """
    dataset = cnvrg.datasets.get(name)
    file_paths = files.split(",")
    dataset.remove_files(paths=file_paths, message=message, progress_bar_enabled=True)
    logger.log_and_echo(messages.DATASET_REMOVE_SUCCESS)

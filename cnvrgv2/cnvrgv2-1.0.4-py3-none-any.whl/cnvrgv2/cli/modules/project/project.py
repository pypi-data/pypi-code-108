import os
import click

from cnvrgv2.cli.utils import messages
from cnvrgv2.config import error_messages
from cnvrgv2.cli.utils.decorators import prepare_command
from cnvrgv2.config import Config, CONFIG_FOLDER_NAME


@click.group(name='project')
def project_group():
    pass


@project_group.command()
@click.option('-n', '--name', prompt=messages.PROJECT_PROMPT_CREATE, help=messages.PROJECT_HELP_CREATE)
@prepare_command()
def create(cnvrg, logger, name):
    """
    Creates a new project, and associates the current folder with the created project.
    It is recommended to create a new project in an empty folder.
    To create a project from a folder that contains content please refer to project link command.
    """
    if os.listdir():
        click.confirm(messages.PROJECT_CREATE_FOLDER_NOT_EMPTY, default=False, abort=True)

    logger.log_and_echo(messages.PROJECT_CREATING_PROJECT.format(name))
    new_project = cnvrg.projects.create(name)

    logger.log_and_echo(messages.PROJECT_CONFIGURING_FOLDER)

    new_project.save_config()

    logger.log_and_echo(messages.PROJECT_CREATE_SUCCESS.format(new_project.title))


@project_group.command()
@click.option('-n', '--name', prompt=messages.PROJECT_PROMPT_CLONE, help=messages.PROJECT_PROMPT_CLONE)
@click.option('-o', '--override', is_flag=True, default=False, help=messages.PROJECT_HELP_CLONE_OVERRIDE)
@prepare_command()
def clone(cnvrg, logger, name, override):
    """
    Clones the given project to local folder
    """
    project = cnvrg.projects.get(name)
    logger.info(messages.LOG_CLONING_PROJECT.format(name))
    if os.path.exists(project.slug + '/' + CONFIG_FOLDER_NAME) and not override:
        logger.log_and_echo(messages.PROJECT_CLONE_SKIP.format(name))
        return
    project.clone(progress_bar_enabled=True, override=override)
    success_message = messages.PROJECT_CLONE_SUCCESS.format(name)
    logger.log_and_echo(success_message)


@project_group.command()
@click.option('-g', '--git-diff', is_flag=True, help=messages.DATA_UPLOAD_HELP_GIT_DIFF)
@prepare_command()
def upload(project, logger, git_diff):
    """
    Uploads updated files from the current project folder
    """
    project.upload(progress_bar_enabled=True, git_diff=git_diff)
    logger.log_and_echo(messages.DATA_UPLOAD_SUCCESS)


@project_group.command()
@click.option('-c', '--commit', default=None, help=messages.PROJECT_DOWNLOAD_HELP_COMMIT)
@prepare_command()
def download(project, logger, commit):
    """
    Downloads updated files to the current project folder
    """
    project.download(progress_bar_enabled=True, commit_sha1=commit)
    logger.log_and_echo(messages.DATA_DOWNLOAD_SUCCESS)


@project_group.command()
@click.option('-n', '--name', prompt=messages.PROJECT_LINK_PROMPT_NAME, help=messages.PROJECT_LINK_HELP_NAME)
@prepare_command()
def link(cnvrg, logger, name):
    """
    Links the current directory with a new project.
    This command will create a new project and upload the current folder content to the newly created project.
    """
    curr_dir_project_name = Config().data_owner_slug
    if curr_dir_project_name:
        error_message = error_messages.DIRECTORY_ALREADY_LINKED.format(curr_dir_project_name)
        logger.log_and_echo(error_message, error=True)

    logger.log_and_echo(messages.PROJECT_CREATE_NEW.format(name))
    new_project = cnvrg.projects.create(name=name)

    logger.log_and_echo(messages.PROJECT_CONFIGURING_FOLDER)
    new_project.save_config()

    logger.log_and_echo(messages.PROJECT_UPLOAD)
    new_project.upload(progress_bar_enabled=True)

    success_message = messages.PROJECT_LINK_SUCCESS.format(new_project.title)
    logger.log_and_echo(success_message)


@project_group.command()
@click.option('-n', '--name', prompt=messages.PROJECT_LINK_GIT_PROMPT_NAME, help=messages.PROJECT_LINK_GIT_HELP_NAME)
@prepare_command()
def link_git(cnvrg, logger, name):
    """
     Links the current directory, which is expected to be a git directory, with an existing cnvrg project
     that is configured to be a git project.
    """
    git_proj = cnvrg.projects.get(name)
    if not git_proj.git:
        error_message = error_messages.NOT_A_GIT_PROJECT.format(git_proj.title)
        logger.log_and_echo(error_message, error=True)

    logger.log_and_echo(messages.PROJECT_CONFIGURING_FOLDER)
    git_proj.save_config()

    success_message = messages.PROJECT_LINK_SUCCESS.format(git_proj.title)
    logger.log_and_echo(success_message)

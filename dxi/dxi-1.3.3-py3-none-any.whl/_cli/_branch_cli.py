#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

import click
from dxi._lib.util import boolean_based_system_exit
from dxi.branch.dxi_branch import DXIBranch
from dxi.branch.dxi_branch import DXIBranchConstants


@click.group(
    short_help="\b\nPerform Delphix Self-Service Branch Operations.\n"
               "[create | activate | delete | list] "
)
def branch():
    """
    Self-Service Branch operations
    """
    pass


@branch.command()
@click.option(
    "--branch-name", required=True, help="Name of the self-service branch."
)
@click.option(
    "--engine",
    default=DXIBranchConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIBranchConstants.SINGLE_THREAD),
    default=DXIBranchConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIBranchConstants.POLL),
    default=DXIBranchConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIBranchConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIBranchConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIBranchConstants.LOG_FILE_PATH,
)
def delete(
    engine, single_thread, parallel, poll, config, log_file_path, branch_name
):
    """
    Delete a self-service branch.
    """
    env_obj = DXIBranch(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config_file=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
    )
    boolean_based_system_exit(env_obj.delete(branch_name=branch_name))


@branch.command()
@click.option(
    "--branch-name", required=True, help="Name of the self-service branch."
)
@click.option(
    "--container-name",
    required=True,
    help="Name of the parent self-service container for the branch.",
)
@click.option(
    "--engine",
    default=DXIBranchConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIBranchConstants.SINGLE_THREAD),
    default=DXIBranchConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIBranchConstants.POLL),
    default=DXIBranchConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIBranchConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIBranchConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIBranchConstants.LOG_FILE_PATH,
)
def activate(
    engine,
    single_thread,
    parallel,
    poll,
    config,
    log_file_path,
    branch_name,
    container_name,
):
    """
    Activate a self-service branch.
    """
    env_obj = DXIBranch(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config_file=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
    )
    boolean_based_system_exit(
        env_obj.activate(
            branch_name=branch_name, container_name=container_name
        )
    )


@branch.command()
@click.option(
    "--engine",
    default=DXIBranchConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIBranchConstants.SINGLE_THREAD),
    default=DXIBranchConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIBranchConstants.POLL),
    default=DXIBranchConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIBranchConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIBranchConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIBranchConstants.LOG_FILE_PATH,
)
def list(engine, single_thread, parallel, poll, config, log_file_path):
    """
    List all self-service branches on an engine
    """
    env_obj = DXIBranch(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config_file=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
    )
    boolean_based_system_exit(env_obj.list())


@branch.command()
@click.option(
    "--branch-name",
    default=None,
    required=True,
    help="Name of the self-service branch.",
)
@click.option(
    "--container-name",
    default=None,
    required=True,
    help="Name of the parent self-service container.",
)
@click.option(
    "--template-name",
    default=None,
    help="Name of the parent self-service template.",
)
@click.option(
    "--bookmark-name",
    default=None,
    help="Name of the self-service bookmark to create the branch.",
)
@click.option(
    "--timestamp",
    default=None,
    help="Timestamp from the container's timeline to create the branch",
)
@click.option(
    "--engine",
    default=DXIBranchConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIBranchConstants.SINGLE_THREAD),
    default=DXIBranchConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIBranchConstants.POLL),
    default=DXIBranchConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIBranchConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIBranchConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIBranchConstants.LOG_FILE_PATH,
)
def create(
    branch_name,
    container_name,
    template_name,
    bookmark_name,
    timestamp,
    engine,
    single_thread,
    parallel,
    poll,
    config,
    log_file_path,
):
    """
    Create a new self-service branch.
    """
    env_obj = DXIBranch(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config_file=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
    )
    boolean_based_system_exit(
        env_obj.create(
            branch_name=branch_name,
            container_name=container_name,
            template_name=template_name,
            bookmark_name=bookmark_name,
            timestamp=timestamp,
        )
    )


if __name__ == "__main__":
    activate()

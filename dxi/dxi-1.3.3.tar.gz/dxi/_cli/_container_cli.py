#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

import click
from dxi._lib.util import boolean_based_system_exit
from dxi.container.dxi_container import DXIContainer
from dxi.container.dxi_container import DXIContainerConstants
from dxi._lib.dlpx_exceptions import DXIException
import sys


@click.group(
    short_help="\b\nPerform Delphix Self-Service Container Operations.\n"
               "[create | refresh | reset | restore | delete | "
               "add-owner \nremove-owner | connection-info | enable | list]"
)
def container():
    """
    Self-Service Container operations
    """
    pass


# List Command
@container.command()
@click.option(
    "--engine",
    default=DXIContainerConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIContainerConstants.SINGLE_THREAD),
    default=DXIContainerConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file with filename.",
    default=DXIContainerConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path to the logs folder.",
    default=DXIContainerConstants.LOG_FILE_PATH,
)
@click.option(
    "--poll",
    help="The number of seconds to wait between job polls.",
    default=DXIContainerConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def list(engine, single_thread, config, log_file_path, poll, debug):
    """
    List all self-service containers on a given engine
    """
    try:
        ss_container = DXIContainer(
            engine=engine,
            single_thread=single_thread,
            config=config,
            log_file_path=log_file_path,
            poll=poll,
            debug=debug
        )
        boolean_based_system_exit(ss_container.list())
    except DXIException as err:
        print(err)
        sys.exit(1)


# Create Container Command
@container.command()
@click.option(
    "--container-name",
    required=True,
    help="Name of the self-service container.",
)
@click.option(
    "--db-name",
    required=True,
    help="\b\nName of the datasets to create the self-service container.\n"
    "If the container should contain multiple datasets,\n"
    "separate the names with colon (:).\n"
    "Sample: db1:db2:db3",
)
@click.option(
    "--template-name",
    required=True,
    help="Name of the parent self-service template for the container.",
)
@click.option(
    "--engine",
    default=DXIContainerConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file with filename.",
    default=DXIContainerConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path to the logs folder.",
    default=DXIContainerConstants.LOG_FILE_PATH,
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIContainerConstants.SINGLE_THREAD),
    default=DXIContainerConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIContainerConstants.POLL),
    default=DXIContainerConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def create(
    container_name,
    template_name,
    db_name,
    engine,
    single_thread,
    config,
    log_file_path,
    poll,
    debug
):
    """
    Create a self-service container.
    """
    try:
        ss_container = DXIContainer(
            engine=engine,
            single_thread=single_thread,
            config=config,
            log_file_path=log_file_path,
            poll=poll,
            debug=debug
        )
        boolean_based_system_exit(
            ss_container.create(container_name, template_name, db_name=db_name)
        )
    except DXIException as err:
        print(err)
        sys.exit(1)


# Delete Container Command
@container.command()
@click.option(
    "--container-name",
    required=True,
    help="Name of the self-service container.",
)
@click.option(
    "--delete-vdbs",
    help="\b\nIf set, deleting the container will also delete \n"
         "the underlying virtual dataset(s)\n"
         "[Default: False]",
    default=False,
    is_flag=True,
)
@click.option(
    "--keep-vdbs",
    help="\b\n[DEPRECATION: This option will be deprecated with dxi-1.3.4 release]\n"
        "If set, deleting the container will not remove \n"
        "the underlying virtual dataset(s)\n"
        "[Default: True]",
    default=True,
    is_flag=True,
)

@click.option(
    "--engine",
    default=DXIContainerConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file with filename.",
    default=DXIContainerConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path to the logs folder.",
    default=DXIContainerConstants.LOG_FILE_PATH,
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIContainerConstants.SINGLE_THREAD),
    default=DXIContainerConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIContainerConstants.POLL),
    default=DXIContainerConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def delete(
    container_name,
    delete_vdbs,
    keep_vdbs,
    engine,
    single_thread,
    config,
    log_file_path,
    poll,
    debug
):
    """
    Delete a self-service container
    """
    try:
        ss_container = DXIContainer(
            engine=engine,
            single_thread=single_thread,
            config=config,
            log_file_path=log_file_path,
            poll=poll,
            debug=debug
        )
        boolean_based_system_exit(
            ss_container.delete(container_name, delete_vdbs, keep_vdbs=keep_vdbs)
        )
    except DXIException as err:
        print(err)
        sys.exit(1)


# Reset Container Command
@container.command()
@click.option(
    "--container-name",
    required=True,
    help="Name of the self-service container.",
)
@click.option(
    "--engine",
    default=DXIContainerConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file with filename.",
    default=DXIContainerConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path to the logs folder.",
    default=DXIContainerConstants.LOG_FILE_PATH,
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIContainerConstants.SINGLE_THREAD),
    default=DXIContainerConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIContainerConstants.POLL),
    default=DXIContainerConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def reset(container_name, engine, single_thread, config, log_file_path, poll, debug):
    """
    Undo the last refresh or restore operation on a self-service container.
    """
    try:
        ss_container = DXIContainer(
            engine=engine,
            single_thread=single_thread,
            config=config,
            log_file_path=log_file_path,
            poll=poll,
            debug=debug
        )
        boolean_based_system_exit(ss_container.reset(container_name))
    except DXIException as err:
        print(err)
        sys.exit(1)

# Refresh Container Command
@container.command()
@click.option(
    "--container-name",
    required=True,
    help="Name of the self-service container.",
)
@click.option(
    "--engine",
    default=DXIContainerConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file with filename.",
    default=DXIContainerConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path to the logs folder.",
    default=DXIContainerConstants.LOG_FILE_PATH,
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIContainerConstants.SINGLE_THREAD),
    default=DXIContainerConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIContainerConstants.POLL),
    default=DXIContainerConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def refresh(
    container_name, engine, single_thread, config, log_file_path, poll, debug
):
    """
    Refresh a self-service container.
    """
    try:
        ss_container = DXIContainer(
            engine=engine,
            single_thread=single_thread,
            config=config,
            log_file_path=log_file_path,
            poll=poll,
            debug=debug
        )
        boolean_based_system_exit(ss_container.refresh(container_name))
    except DXIException as err:
        print(err)
        sys.exit(1)

# Restore Container Command
@container.command()
@click.option(
    "--bookmark-name",
    required=True,
    help="Name of the self-service bookmark to restore the container",
)
@click.option(
    "--container-name",
    required=True,
    help="Name of the self-service container.",
)
@click.option(
    "--engine",
    default=DXIContainerConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file with filename.",
    default=DXIContainerConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path to the logs folder.",
    default=DXIContainerConstants.LOG_FILE_PATH,
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIContainerConstants.SINGLE_THREAD),
    default=DXIContainerConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIContainerConstants.POLL),
    default=DXIContainerConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def restore(
    container_name,
    bookmark_name,
    engine,
    single_thread,
    config,
    log_file_path,
    poll,
    debug
):
    """
    Restore a self-service container to a specific self-service bookmark.
    """
    try:
        ss_container = DXIContainer(
            engine=engine,
            single_thread=single_thread,
            config=config,
            log_file_path=log_file_path,
            poll=poll,
            debug=debug
        )
        boolean_based_system_exit(
            ss_container.restore(container_name, bookmark_name)
        )
    except DXIException as err:
        print(err)
        sys.exit(1)

# Lists hierarchy Command
@container.command()
@click.option(
    "--container-name",
    required=True,
    help="Name of the self-service container.",
)
@click.option(
    "--engine",
    default=DXIContainerConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file with filename.",
    default=DXIContainerConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path to the logs folder.",
    default=DXIContainerConstants.LOG_FILE_PATH,
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIContainerConstants.SINGLE_THREAD),
    default=DXIContainerConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIContainerConstants.POLL),
    default=DXIContainerConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def connection_info(
    container_name, engine, single_thread, config, log_file_path, poll, debug
):
    """
    List connection information for a self-service container.
    """
    try:
        ss_container = DXIContainer(
            engine=engine,
            single_thread=single_thread,
            config=config,
            log_file_path=log_file_path,
            poll=poll,
            debug=debug
        )
        boolean_based_system_exit(ss_container.connection_info(container_name))
    except DXIException as err:
        print(err)
        sys.exit(1)

# Add owner Command
@container.command()
@click.option(
    "--container-name",
    required=True,
    help="Name of the self-service container.",
)
@click.option(
    "--owner-name",
    required=True,
    help="Name of the owner user for the container",
)
@click.option(
    "--engine",
    default=DXIContainerConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file with filename.",
    default=DXIContainerConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path to the logs folder.",
    default=DXIContainerConstants.LOG_FILE_PATH,
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIContainerConstants.SINGLE_THREAD),
    default=DXIContainerConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIContainerConstants.POLL),
    default=DXIContainerConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def add_owner(
    owner_name,
    container_name,
    engine,
    single_thread,
    config,
    log_file_path,
    poll,
    debug
):
    """
    Add an owner to a self-service container.
    """
    # print(owner_name, container_name)
    try:
        ss_container = DXIContainer(
            engine=engine,
            single_thread=single_thread,
            config=config,
            log_file_path=log_file_path,
            poll=poll,
            debug=debug
        )
        boolean_based_system_exit(
            ss_container.add_owner(container_name, owner_name)
        )
    except DXIException as err:
        print(err)
        sys.exit(1)

# Delete owner Command
@container.command()
@click.option(
    "--container-name",
    required=True,
    help="Name of the self-service container.",
)
@click.option(
    "--owner-name",
    required=True,
    help="Name of the owner user for the container",
)
@click.option(
    "--engine",
    default=DXIContainerConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file with filename.",
    default=DXIContainerConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path to the logs folder.",
    default=DXIContainerConstants.LOG_FILE_PATH,
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIContainerConstants.SINGLE_THREAD),
    default=DXIContainerConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIContainerConstants.POLL),
    default=DXIContainerConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def remove_owner(
    container_name,
    owner_name,
    engine,
    single_thread,
    config,
    log_file_path,
    poll,
    debug
):
    """
    Remove an owner from a self-service container.
    """
    try:
        ss_container = DXIContainer(
            engine=engine,
            single_thread=single_thread,
            config=config,
            log_file_path=log_file_path,
            poll=poll,
            debug=debug
        )
        boolean_based_system_exit(
            ss_container.remove_owner(container_name, owner_name)
        )
    except DXIException as err:
        print(err)
        sys.exit(1)


# Enable Container Command
@click.option(
    "--container-name",
    required=True,
    help="Name of the self-service container.",
)
@click.option(
    "--engine",
    default=DXIContainerConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file with filename.",
    default=DXIContainerConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path to the logs folder.",
    default=DXIContainerConstants.LOG_FILE_PATH,
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIContainerConstants.SINGLE_THREAD),
    default=DXIContainerConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIContainerConstants.POLL),
    default=DXIContainerConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
@container.command()
def enable(
    container_name,
    engine,
    single_thread,
    config,
    log_file_path,
    poll,
    debug
):
    """
    Enable a self-service container
    """
    try:
        ss_container = DXIContainer(
            engine=engine,
            single_thread=single_thread,
            config=config,
            log_file_path=log_file_path,
            poll=poll,
            debug=debug
        )
        boolean_based_system_exit(
            ss_container.enable(container_name)
        )
    except DXIException as err:
        print(err)
        sys.exit(1)

# disable Container Command
@click.option(
    "--container-name",
    required=True,
    help="Name of the self-service container.",
)
@click.option(
    "--engine",
    default=DXIContainerConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file with filename.",
    default=DXIContainerConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path to the logs folder.",
    default=DXIContainerConstants.LOG_FILE_PATH,
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIContainerConstants.SINGLE_THREAD),
    default=DXIContainerConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIContainerConstants.POLL),
    default=DXIContainerConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
@container.command()
def disable(
    container_name,
    engine,
    single_thread,
    config,
    log_file_path,
    poll,
    debug
):
    """
    Disable a self-service container
    """
    try:
        ss_container = DXIContainer(
            engine=engine,
            single_thread=single_thread,
            config=config,
            log_file_path=log_file_path,
            poll=poll,
            debug=debug
        )
        boolean_based_system_exit(
            ss_container.disable(container_name)
        )
    except DXIException as err:
        print(err)
        sys.exit(1)


if __name__ == "__main__":
    delete()

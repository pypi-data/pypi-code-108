#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

import click
from dxi._lib.util import boolean_based_system_exit
from dxi.group.dxi_group import DXIGroupConstants
from dxi.group.dxi_group import DXIGroup

@click.group(
    short_help="\b\nPerform Dataset Group Operations.\n"
               "[create | update | delete | list] "
)
def group():
    """
    Delphix group operations
    """
    pass


# List Command
@group.command()
@click.option(
    "--engine",
    default=DXIGroupConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIGroupConstants.SINGLE_THREAD),
    default=DXIGroupConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=DXIGroupConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=DXIGroupConstants.LOG_FILE_PATH,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIGroupConstants.POLL),
    default=DXIGroupConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def list(engine, single_thread, config, log_file_path, poll, debug):
    """
    List all groups on a given engine.
    """
    temp_obj = DXIGroup(
        engine=engine,
        single_thread=single_thread,
        config=config,
        log_file_path=log_file_path,
        poll=poll,
        debug=debug
    )
    boolean_based_system_exit(temp_obj.list())


# Create Group Command
@group.command()
@click.option(
    "--group-name", required=True, help=" Name of the group to create."
)
@click.option(
    "--description", help="Description for the group."
)
@click.option(
    "--engine",
    default=DXIGroupConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIGroupConstants.SINGLE_THREAD),
    default=DXIGroupConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=DXIGroupConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=DXIGroupConstants.LOG_FILE_PATH,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIGroupConstants.POLL),
    default=DXIGroupConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging.",
    is_flag=True,
    default=False,
)
def create(
    group_name, description, engine, single_thread, config, log_file_path, poll, debug
):
    """
    Create a group in Delphix Engine.
    """
    temp_obj = DXIGroup(
        engine=engine,
        single_thread=single_thread,
        config=config,
        log_file_path=log_file_path,
        poll=poll,
        debug=debug
    )
    boolean_based_system_exit(
        temp_obj.create(
            group_name=group_name,
            description=description
        )
    )


# Delete Group Command
@group.command()
@click.option(
    "--group-name", required=True, help="Name of the group to create."
)
@click.option(
    "--engine",
    default=DXIGroupConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
         "[Default: {}]".format(DXIGroupConstants.SINGLE_THREAD),
    default=DXIGroupConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=DXIGroupConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=DXIGroupConstants.LOG_FILE_PATH,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIGroupConstants.POLL),
    default=DXIGroupConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging.",
    is_flag=True,
    default=False,
)
def delete(
        group_name, engine, single_thread, config, log_file_path, poll, debug
):
    """
    Delete a dataset group.
    """
    temp_obj = DXIGroup(
        engine=engine,
        single_thread=single_thread,
        config=config,
        log_file_path=log_file_path,
        poll=poll,
        debug=debug
    )
    boolean_based_system_exit(
        temp_obj.delete(group_name=group_name)
    )


# Update Group Command
@group.command()
@click.option(
    "--group-name", required=True, help=" Name of the group to update."
)
@click.option(
    "--new-name", required=True, help=" New name for the group."
)
@click.option(
    "--new-description", help=" Name description for the group."
)
@click.option(
    "--engine",
    default=DXIGroupConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIGroupConstants.SINGLE_THREAD),
    default=DXIGroupConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=DXIGroupConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=DXIGroupConstants.LOG_FILE_PATH,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIGroupConstants.POLL),
    default=DXIGroupConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging.",
    is_flag=True,
    default=False,
)
def update(
        group_name, new_name, new_description, engine, single_thread, config, log_file_path, poll, debug
):
    """
    Update a group in Delphix Engine.
    """
    temp_obj = DXIGroup(
        engine=engine,
        single_thread=single_thread,
        config=config,
        log_file_path=log_file_path,
        poll=poll,
        debug=debug
    )
    boolean_based_system_exit(
        temp_obj.update(
            group_name=group_name,
            new_name = new_name,
            new_description = new_description
        )
    )


if __name__ == "__main__":
    update()

#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

import click
from dxi._lib.util import boolean_based_system_exit
from dxi.user.dxi_user import DXIUserConstants
from dxi.user.dxi_user import DXIUser

@click.group(
    short_help="\b\nPerform Delphix Virtualization Engine User Operations.\n"
               "[create | update | delete | list] "
)
def user():
    """
    Delphix Virtualization User operations.
    """
    pass


# List Command
@user.command()
@click.option(
    "--engine",
    default=DXIUserConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXIUserConstants.SINGLE_THREAD),
    default=DXIUserConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=DXIUserConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=DXIUserConstants.LOG_FILE_PATH,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXIUserConstants.POLL),
    default=DXIUserConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def list(engine, single_thread, config, log_file_path, poll, debug):
    """
    List all users on a Delphix engine.
    Returns:
    """
    temp_obj = DXIUser(
        engine=engine,
        single_thread=single_thread,
        config=config,
        log_file_path=log_file_path,
        poll=poll,
        debug=debug
    )
    boolean_based_system_exit(temp_obj.list())


# Create User Command
@user.command()
@click.option(
    "--user-name", required=True, help=" New user's name."
)
@click.option(
    "--user-password", required=True, help="New user's password."
)
@click.option(
    "--email-address", required=True, help="New user's email address."
)
@click.option(
    "--first-name", required=True, help="New user's first name."
)
@click.option(
    "--last-name", required=True, help="New user's last name."
)
@click.option(
    "--engine",
    default=DXIUserConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIUserConstants.SINGLE_THREAD),
    default=DXIUserConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=DXIUserConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=DXIUserConstants.LOG_FILE_PATH,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIUserConstants.POLL),
    default=DXIUserConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging.",
    is_flag=True,
    default=False,
)
def create(
        user_name,
        user_password,
        email_address,
        first_name,
        last_name,
        engine,
        single_thread,
        config,
        log_file_path,
        poll,
        debug
):
    """
    Create a user in Delphix Engine.
    """
    temp_obj = DXIUser(
        engine=engine,
        single_thread=single_thread,
        config=config,
        log_file_path=log_file_path,
        poll=poll,
        debug=debug
    )
    boolean_based_system_exit(
        temp_obj.create(
            user_name=user_name,
            user_password = user_password,
            email_address=email_address,
            first_name = first_name,
            last_name = last_name
        )
    )


# Delete user Command
@user.command()
@click.option(
    "--user-name", required=True, help="Name of the user to delete."
)
@click.option(
    "--engine",
    default=DXIUserConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
         "[Default: {}]".format(DXIUserConstants.SINGLE_THREAD),
    default=DXIUserConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=DXIUserConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=DXIUserConstants.LOG_FILE_PATH,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIUserConstants.POLL),
    default=DXIUserConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging.",
    is_flag=True,
    default=False,
)
def delete(
        user_name, engine, single_thread, config, log_file_path, poll, debug
):
    """
    Delete a user from Delphix Engine.
    """
    temp_obj = DXIUser(
        engine=engine,
        single_thread=single_thread,
        config=config,
        log_file_path=log_file_path,
        poll=poll,
        debug=debug
    )
    boolean_based_system_exit(
        temp_obj.delete(user_name=user_name)
    )


# Update User Command
@user.command()
@click.option(
    "--user-name", required=True, help="Name of the user to update."
)
@click.option(
    "--current-password",
    help="\b\nCurrent password for the user.\n"
            "[ required if changing password.]"
)
@click.option(
    "--new-password",
    help="\b\nNew password for the user.\n"
         "[ required if changing password. ]"
)
@click.option(
    "--first-name", help="New First name of the user."
)
@click.option(
    "--last-name", help="Last name of the user."
)
@click.option(
    "--email-address", help="Email address for the user."
)
@click.option(
    "--engine",
    default=DXIUserConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIUserConstants.SINGLE_THREAD),
    default=DXIUserConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=DXIUserConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=DXIUserConstants.LOG_FILE_PATH,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIUserConstants.POLL),
    default=DXIUserConstants.POLL,
)
@click.option(
    "--debug",
    help="Enable debug logging.",
    is_flag=True,
    default=False,
)
def update(
        user_name,
        current_password,
        new_password,
        first_name,
        last_name,
        email_address,
        engine,
        single_thread,
        config,
        log_file_path,
        poll,
        debug
):
    """
    Update a user in Delphix Engine.
    """
    temp_obj = DXIUser(
        engine=engine,
        single_thread=single_thread,
        config=config,
        log_file_path=log_file_path,
        poll=poll,
        debug=debug
    )
    boolean_based_system_exit(
        temp_obj.update(
            user_name=user_name,
            current_password = current_password,
            new_password = new_password,
            first_name = first_name,
            last_name=last_name,
            email_address=email_address,
        )
    )

if __name__ == "__main__":
    create()

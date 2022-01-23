#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

import click
from dxi._lib.util import boolean_based_system_exit
from dxi.config.dxi_config import DXIConfig
from dxi.config.dxi_config import DXIConfigConstants


@click.group(
    short_help="\b\nInitialize and Configure dxi.\n"
               "[init | encrypt]"
)
def config():
    """
    DXI Config related operations.
    """
    pass


# encrypt
@config.command()
@click.option(
    "--config-file",
    help="\b\nPath of the config file (including filename) \n"
    "that contains engine information",
    default=DXIConfigConstants.CONFIG,
)
@click.option(
    "--log-dir",
    help="\b Path to the log directory",
    default=DXIConfigConstants.LOG_DIR,
)
def encrypt(config_file, log_dir):
    """
    Encrypts username and password fields in config file.
    """
    temp_obj = DXIConfig(config=config_file, log_dir=log_dir)
    boolean_based_system_exit(temp_obj.encrypt())


# init
@config.command()
@click.option(
    "--config-file",
    help="\b\n Path to dxi config directory",
    default=DXIConfigConstants.CONFIG,
)
@click.option(
    "--log-dir",
    help="\b Path to the dxi log directory",
    default=DXIConfigConstants.LOG_DIR,
)
def init(config_file, log_dir):
    """
    Creates config and log directories.
    Adds sample dxtools.conf file into the config directory.
    """
    temp_obj = DXIConfig(config_file, log_dir)
    boolean_based_system_exit(temp_obj.init())


if __name__ == "__main__":
    encrypt()

#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

import click
from dxi._lib.util import boolean_based_system_exit
from dxi.template.dxi_template import DXITemplate
from dxi.template.dxi_template import DXITemplateConstants


@click.group(
    short_help="\b\nPerform Delphix Self-Service Template Operations.\n"
               "[create | delete | list] "
)
def template():
    """
    Self-Service Template operations
    """
    pass


# List Command
@template.command()
@click.option(
    "--engine",
    default=DXITemplateConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXITemplateConstants.SINGLE_THREAD),
    default=DXITemplateConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=DXITemplateConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=DXITemplateConstants.LOG_FILE_PATH,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXITemplateConstants.POLL),
    default=DXITemplateConstants.POLL,
)
def list(engine, single_thread, config, log_file_path, poll):
    """
    List all self-service templates on a given engine.
    """
    temp_obj = DXITemplate(
        engine=engine,
        single_thread=single_thread,
        config=config,
        log_file_path=log_file_path,
        poll=poll,
    )
    boolean_based_system_exit(temp_obj.list())


# Create Template Command
@template.command()
@click.option(
    "--template-name", required=True, help=" Name of the template to create"
)
@click.option(
    "--db-name",
    required=True,
    help="\b\nList of data sources to add to the new template.\n"
    "If the template should contain multiple data source,\n"
    "separate the names with colon (:).\n"
    "Sample: db1:db2:db3",
)
@click.option(
    "--engine",
    default=DXITemplateConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXITemplateConstants.SINGLE_THREAD),
    default=DXITemplateConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=DXITemplateConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=DXITemplateConstants.LOG_FILE_PATH,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXITemplateConstants.POLL),
    default=DXITemplateConstants.POLL,
)
def create(
    template_name, db_name, engine, single_thread, config, log_file_path, poll
):
    """
    Create a self-service template.
    """
    temp_obj = DXITemplate(
        engine=engine,
        single_thread=single_thread,
        config=config,
        log_file_path=log_file_path,
        poll=poll,
    )
    boolean_based_system_exit(
        temp_obj.create(template_name=template_name, dbnames=db_name)
    )


# Delete Template Command
@template.command()
@click.option(
    "--template-name", required=True, help="Name of self-service template."
)
@click.option(
    "--engine",
    default=DXITemplateConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(DXITemplateConstants.SINGLE_THREAD),
    default=DXITemplateConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=DXITemplateConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=DXITemplateConstants.LOG_FILE_PATH,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(DXITemplateConstants.POLL),
    default=DXITemplateConstants.POLL,
)
def delete(template_name, engine, single_thread, config, log_file_path, poll):
    """
    Delete a self-service template.
    """
    ss_container = DXITemplate(
        engine=engine,
        single_thread=single_thread,
        config=config,
        log_file_path=log_file_path,
        poll=poll,
    )
    boolean_based_system_exit(ss_container.delete(template_name=template_name))


if __name__ == "__main__":
    list()

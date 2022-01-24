#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

import click
from dxi._lib import click_util
from dxi._lib.util import boolean_based_system_exit
from dxi.bookmark.dxi_bookmark import BookmarkConstants
from dxi.bookmark.dxi_bookmark import DXIBookmark


@click.group(
    short_help="\b\nPerform Delphix Self-Service Boomark Operations.\n"
               "[create | delete | update | "
               "share | unshare | list]"
)
def bookmark():
    """
    Self-Service Bookmark operations
    """
    pass


# list
@bookmark.command()
@click.option("--tags", default=None, help="Tags to filter the bookmark names")
@click.option(
    "--engine",
    default=BookmarkConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
    "[Default: {}]".format(BookmarkConstants.SINGLE_THREAD),
    default=BookmarkConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(BookmarkConstants.POLL),
    default=BookmarkConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=BookmarkConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=BookmarkConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=BookmarkConstants.LOG_FILE_PATH,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def list(engine, single_thread, parallel, poll, config, log_file_path, tags, debug):
    """
    List all self-service bookmarks on an engine.
    """
    bmk_obj = DXIBookmark(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
        debug=debug
    )
    boolean_based_system_exit(bmk_obj.list(tags=tags))


# share
@bookmark.command()
@click.option(
    "--bookmark-name",
    default=None,
    required=True,
    help="Name of the self-service bookmark.",
)
@click.option(
    "--engine",
    default=BookmarkConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
    "[Default: {}]".format(BookmarkConstants.SINGLE_THREAD),
    default=BookmarkConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(BookmarkConstants.POLL),
    default=BookmarkConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=BookmarkConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=BookmarkConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=BookmarkConstants.LOG_FILE_PATH,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def share(
    bookmark_name, engine, single_thread, parallel, poll, config, log_file_path, debug
):
    """
    Share a self-service bookmark.
    """
    bmk_obj = DXIBookmark(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
        debug=debug
    )
    boolean_based_system_exit(bmk_obj.share(bookmark_name=bookmark_name))


# unshare
@bookmark.command()
@click.option(
    "--bookmark-name",
    default=None,
    required=True,
    help="Name of the self-service bookmark.",
)
@click.option(
    "--engine",
    default=BookmarkConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
    "[Default: {}]".format(BookmarkConstants.SINGLE_THREAD),
    default=BookmarkConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(BookmarkConstants.POLL),
    default=BookmarkConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=BookmarkConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=BookmarkConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=BookmarkConstants.LOG_FILE_PATH,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def unshare(
    bookmark_name, engine, single_thread, parallel, poll, config, log_file_path, debug
):
    """
    Unshare a self-service bookmark.
    """
    bmk_obj = DXIBookmark(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
        debug=debug
    )
    boolean_based_system_exit(bmk_obj.unshare(bookmark_name=bookmark_name))


# delete
@bookmark.command()
@click.option(
    "--bookmark-name",
    default=None,
    required=True,
    help="Name of the self-service bookmark.",
)
@click.option(
    "--engine",
    default=BookmarkConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
    "[Default: {}]".format(BookmarkConstants.SINGLE_THREAD),
    default=BookmarkConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(BookmarkConstants.POLL),
    default=BookmarkConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=BookmarkConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=BookmarkConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=BookmarkConstants.LOG_FILE_PATH,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def delete(
    bookmark_name, engine, single_thread, parallel, poll, config, log_file_path, debug
):
    """
    Delete a self-service bookmark.
    """
    bmk_obj = DXIBookmark(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
        debug=debug
    )
    boolean_based_system_exit(bmk_obj.delete(bookmark_name=bookmark_name))


# update
@bookmark.command()
@click.option(
    "--bookmark-name",
    default=None,
    required=True,
    help="Name of the self-service bookmark.",
)
@click.option(
    "--new-name",
    default=None,
    help="If updating bookmark name, provide the new name.",
)
@click.option(
    "--tags",
    default=None,
    help="\b\nIf updating tags, provide new tags.\n"
    "All existing tags on the bookmark will be \n"
    "replaced with new tags provided.",
)
@click.option(
    "--description",
    default=None,
    help="If updating bookmark description, provide the new description.",
)
@click.option(
    "--expires",
    default=None,
    help="If updating bookmark expiration, provide new expiration date-time."
    'Format: "%Y-%m-%dT%H:%M:%S" ',
)
@click.option(
    "--engine",
    default=BookmarkConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
    "[Default: {}]".format(BookmarkConstants.SINGLE_THREAD),
    default=BookmarkConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(BookmarkConstants.POLL),
    default=BookmarkConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=BookmarkConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=BookmarkConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=BookmarkConstants.LOG_FILE_PATH,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def update(
    bookmark_name,
    new_name,
    tags,
    description,
    expires,
    engine,
    single_thread,
    parallel,
    poll,
    config,
    log_file_path,
    debug
):
    """
    Update a self-service bookmark.
    """
    bmk_obj = DXIBookmark(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
        debug=debug
    )
    boolean_based_system_exit(
        bmk_obj.update(
            bookmark_name=bookmark_name,
            new_bookmark_name=new_name,
            tags=tags,
            description=description,
            expires=expires,
        )
    )


# create
@bookmark.command()
@click.option(
    "--bookmark-name",
    default=None,
    required=True,
    help="Name of the self-service bookmark.",
)
@click.option(
    "--container-name",
    cls=click_util.MutuallyExclusiveOption,
    mutually_exclusive=["template-name"],
    default=None,
    help="\b\nName of the parent self-service container for the bookmark.\n"
    "[required: If bookmark is being created on a self-service container]",
)
@click.option(
    "--template-name",
    cls=click_util.MutuallyExclusiveOption,
    mutually_exclusive=["containername"],
    default=None,
    help="\b\nName of the self-service parent template for the bookmark.\n"
    "[required: If bookmark is being created on a self-service template]",
)
@click.option(
    "--branch-name",
    default=None,
    help="\b\nIf self-service bookmark is not unique in a container,\n"
    "specify a branch name to create the bookmark from,",
)
@click.option(
    "--timestamp",
    default=None,
    help="\b\nTimestamp to create the self-service bookmark. \n"
    "Timestamp should be in the same timezone as the Delphix Engine.\n"
    'Format: "%Y-%m-%dT%H:%M:%S" | latest \n'
    "[Example: 2021-12-21T16:22:77]",
)
@click.option(
    "--expires",
    default=None,
    help="\b\nSet self-service bookmark expiration time. \n"
    "Expiration time should be in the same timezone as the Delphix Engine.\n"
    'Format: "%Y-%m-%dT%H:%M:%S" | latest \n'
    "[Example: 2021-12-21T16:22:77]",
)
@click.option(
    "--tags", default=None, help="Tags to set on the self-service bookmark."
)
@click.option(
    "--description",
    default=None,
    help="Description for the self-service bookmark.",
)
@click.option(
    "--engine",
    default=BookmarkConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
    "[Default: {}]".format(BookmarkConstants.SINGLE_THREAD),
    default=BookmarkConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(BookmarkConstants.POLL),
    default=BookmarkConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=BookmarkConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=BookmarkConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=BookmarkConstants.LOG_FILE_PATH,
)
@click.option(
    "--debug",
    help="Enable debug logging",
    is_flag=True,
    default=False,
)
def create(
    bookmark_name,
    container_name,
    template_name,
    branch_name,
    timestamp,
    expires,
    tags,
    description,
    engine,
    single_thread,
    parallel,
    poll,
    config,
    log_file_path,
    debug
):
    """
    Create a new self-service bookmark.
    """
    bmk_obj = DXIBookmark(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
        debug=debug
    )
    boolean_based_system_exit(
        bmk_obj.create(
            bookmark_name=bookmark_name,
            container_name=container_name,
            template_name=template_name,
            branch_name=branch_name,
            timestamp=timestamp,
            expires=expires,
            tags=tags,
            description=description,
        )
    )


if __name__ == "__main__":
    create()

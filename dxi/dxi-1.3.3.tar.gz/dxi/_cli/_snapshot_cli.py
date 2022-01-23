#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

import click
from dxi._lib import click_util
from dxi._lib.util import boolean_based_system_exit
from dxi.snapshot.dxi_snapshot import DXISnapshot
from dxi.snapshot.dxi_snapshot import SnapshotConstants


@click.group(
    short_help="\b\nPerform Snapshot Operations.\n"
               "[create]"
)
def snapshot():
    """
    Dsource, VDB and vFile Snapshot operations
    """
    pass


@snapshot.command()
@click.option(
    "--db-name",
    cls=click_util.MutuallyExclusiveOption,
    default=SnapshotConstants.NAME,
    mutually_exclusive=["group", "all_dbs"],
    help="\b\nName of the dataset to create the snapshot.\n"
    "[Required if taking snapshot of a single database]",
)
@click.option(
    "--group",
    cls=click_util.MutuallyExclusiveOption,
    mutually_exclusive=["name", "all_dbs"],
    default=SnapshotConstants.GROUP,
    help="\b\nName of group in Delphix to refresh against.\n"
    "If provided, Delphix will take snapshots of \n"
    "all datasets in this group.\n"
    "[Required if taking snapshot of a all databases in a group]",
)
@click.option(
    "--all-dbs",
    cls=click_util.MutuallyExclusiveOption,
    mutually_exclusive=["name", "group"],
    is_flag=True,
    default=SnapshotConstants.ALL_DBS,
    help="\b\nTake a snapshot of all datasets on an engine.\n"
    "[Required if taking snapshot of a all databases on an engine.]",
)
@click.option(
    "--use-recent-backup",
    help="\b\nSnapshot using the most recent available backup.\n"
    "MSSQL and ASE Only.",
    default=SnapshotConstants.USE_BACKUP,
    is_flag=True,
)
@click.option(
    "--create-backup",
    help="\b\nTake a new backup to create a snapshot\n"
    "Full Backup for ASE OR Copy-Only Backup for MSSQL.",
    default=SnapshotConstants.CREATE_BACKUP,
    is_flag=True,
)
@click.option(
    "--backup-file",
    help="\b\nName of a specific backup to use for snapshot.\n"
    "For ASE, provide backup file(s) name.\n"
    "For MSSQL, provide backup uuid.",
    default=SnapshotConstants.BCK_FILE,
)
@click.option(
    "--engine",
    default=SnapshotConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(SnapshotConstants.SINGLE_THREAD),
    default=SnapshotConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=SnapshotConstants.PARALLEL,
)
@click.option(
    "--poll",
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(SnapshotConstants.POLL),
    default=SnapshotConstants.POLL,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file with filename.",
    default=SnapshotConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path to the logs folder.",
    default=SnapshotConstants.LOG_FILE_PATH,
)
def create(
    group,
    db_name,
    all_dbs,
    engine,
    single_thread,
    backup_file,
    use_recent_backup,
    create_backup,
    parallel,
    poll,
    config,
    log_file_path,
):
    """
    Snapshot a Delphix dSource, VDB or vFile.
    """
    snapshot_obj = DXISnapshot(
        engine=engine,
        group=group,
        db_name=db_name,
        all_dbs=all_dbs,
        parallel=parallel,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
    )
    boolean_based_system_exit(
        snapshot_obj.create_snapshot(
            use_recent_backup=use_recent_backup,
            create_backup=create_backup,
            backup_file=backup_file,
        )
    )


if __name__ == "__main__":
    create()

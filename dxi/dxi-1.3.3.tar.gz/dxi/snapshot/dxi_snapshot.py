#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

from os.path import basename

from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2.web import database
from delphixpy.v1_10_2.web import source
from delphixpy.v1_10_2.web import vo
from dxi._lib import dlpx_exceptions
from dxi._lib import dx_logging
from dxi._lib import get_references
from dxi._lib import run_job
from dxi._lib.run_async import run_async
from dxi._lib.util import DXIConfigConstantsHelper
from dxi.dxi_tool_base import DXIBase


class SnapshotConstants(object):
    """
    Define constants for Snapshot class and CLI usage
    """

    ALL_DBS = False
    SINGLE_THREAD = False
    POLL = 20
    CONFIG = DXIConfigConstantsHelper().get_config()
    LOG_FILE_PATH = DXIConfigConstantsHelper().get_logdir()
    BCK_FILE = None
    USE_BACKUP = False
    CREATE_BACKUP = False
    ENGINE_ID = "default"
    NAME = None
    GROUP = None
    PARALLEL = 5


class DXISnapshot(DXIBase):
    """
    Create a snapshot a dSource or VDB
    """

    def __init__(
        self,
        db_name=SnapshotConstants.NAME,
        group=SnapshotConstants.GROUP,
        parallel=SnapshotConstants.PARALLEL,
        engine=SnapshotConstants.ENGINE_ID,
        poll=SnapshotConstants.POLL,
        config=SnapshotConstants.CONFIG,
        log_file_path=SnapshotConstants.LOG_FILE_PATH,
        all_dbs=SnapshotConstants.ALL_DBS,
        single_thread=SnapshotConstants.SINGLE_THREAD,
    ):
        """
        :param name: Name of object in Delphix to snapshot against
        :type name: `str`
        :param group: Name of group in Delphix to snapshot against.
        :type group: `str`
        :param parallel: Limit number of jobs to maxjob
        :type parallel: `int`
        :param engine: Alt Identifier of Delphix engine in dxtools.conf.
        :type engine: `str`
        :param poll: The number of seconds to wait between job polls
        :type poll: `int`
        :param config: The path to the dxtools.conf file
        :type config: `str`
        :param log_file_path: The path to the logfile you want to use.
        :type log_file_path: `str`
        :param all_dbs: Run against all database objects
        :type all_dbs: `bool`
        :param single_thread: Run as a single thread.
            False if running multiple threads.
        :type single_thread: `bool`
        """
        super().__init__(
            parallel=parallel,
            poll=poll,
            config=config,
            log_file_path=log_file_path,
            single_thread=single_thread,
            engine=engine,
            module_name=__name__,
        )
        self.all_dbs = all_dbs
        self.name = db_name
        self.group = group
        self.use_backup = SnapshotConstants.USE_BACKUP
        self.create_bckup = SnapshotConstants.CREATE_BACKUP
        self.bck_file = SnapshotConstants.BCK_FILE
        self.display_choices(self)
        self._validate_input()

    def _validate_input(self):
        if not (self.group or self.name or self.all_dbs):
            dx_logging.print_exception(
                "Invalid parameter is provided."
                " Select at least one option (GROUP|NAME|ALL_DBS)"
            )
            raise
        if (
            (self.group and self.name)
            or (self.name and self.all_dbs)
            or (self.name and self.all_dbs)
        ):
            dx_logging.print_exception(
                "Invalid parameter is provided. "
                "Please choose only single option in (GROUP|NAME|ALL_DBS)"
            )
            raise

    def create_snapshot(
        self, use_recent_backup=False, create_backup=False, backup_file=None
    ):
        """
        :param use_recent_backup: Snapshot using "Most Recent backup".
        :type use_recent_backup: `bool`
        :param create_backup:
            Create and ingest a new Sybase backup or copy-only MS SQL backup
        :type create_backup: `bool`
        :param backup_file: Name of the specific ASE Sybase backup file(s)
        :type backup_file: `str`
        :returns: Snapshot creation status
        :rtype: `bool`
        """
        self.use_backup = use_recent_backup
        self.create_bckup = create_backup
        self.bck_file = backup_file
        try:
            self._execute_operation(self._create_snapshot_helper)
            return True
        except Exception as err:
            dx_logging.print_exception(
                "Snapshot operation failed. {err}".format(err=str(err))
            )
            return False

    def _run_snapshot(self, dlpx_obj, datasets=None):
        """
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        :param datasets: Run against database objects
        :type datasets: `list`
        """
        sync_params = None

        for db_sync in datasets:
            try:
                db_source_info = get_references.find_obj_by_name(
                    dlpx_obj.server_session, source, db_sync
                )
                container_obj_ref = get_references.find_obj_by_name(
                    dlpx_obj.server_session, database, db_sync
                ).reference
            except dlpx_exceptions.DlpxObjectNotFound as err:
                raise err
            if db_source_info.staging:
                raise dlpx_exceptions.DlpxException(
                    f"{db_sync} is a staging " f"database. Cannot Sync.\n"
                )
            if db_source_info.runtime.enabled != "ENABLED":
                raise dlpx_exceptions.DlpxException(
                    f"{db_sync} is not enabled " f"database. Cannot Sync.\n"
                )
            if db_source_info.runtime.enabled == "ENABLED":
                # If the database is a dSource and a MSSQL type,
                # we need to tell Delphix how we want to sync the database.
                # Delphix will just ignore the extra parameters if it is a VDB,
                # so we will omit any extra code to check
                if db_source_info.type == "MSSqlLinkedSource":
                    if self.create_bckup:
                        sync_params = (
                            vo.MSSqlNewCopyOnlyFullBackupSyncParameters()
                        )
                        sync_params.compression_enabled = False
                    elif self.use_backup is True:
                        if self.bck_file:
                            sync_params = (
                                vo.MSSqlExistingSpecificBackupSyncParameters()
                            )
                            sync_params.backup_uuid = self.bck_file
                        else:
                            sync_params = (
                                vo.MSSqlExistingMostRecentBackupSyncParameters()  # noqa
                            )
                # Else if the database is a dSource and a ASE type,
                # we need also to tell Delphix how we want to sync the database
                # Delphix will just ignore the extra parameters if it is a VDB,
                # so we will omit any extra code to check
                elif db_source_info.type == "ASELinkedSource":
                    if self.use_backup is True:
                        sync_params = vo.ASELatestBackupSyncParameters()
                    elif self.bck_file:
                        sync_params = vo.ASESpecificBackupSyncParameters()
                        sync_params.backup_files = self.bck_file.split(" ")
                    elif self.create_bckup:
                        sync_params = vo.ASENewBackupSyncParameters()
                    else:
                        sync_params = vo.ASENewBackupSyncParameters()

                if sync_params:
                    database.sync(
                        dlpx_obj.server_session, container_obj_ref, sync_params
                    )
                else:
                    database.sync(dlpx_obj.server_session, container_obj_ref)
                # Add the job into the jobs dictionary so we can track
                # its progress
                self._add_last_job_to_track(dlpx_obj)

    def _get_db_list(self, dlpx_obj):
        """
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        """
        if self.name:
            self._run_snapshot(dlpx_obj, datasets=[self.name])
        else:
            databases = []
            if self.group:
                databases = get_references.find_all_databases_by_group(
                    dlpx_obj.server_session, self.group
                )
            elif self.all_dbs:
                # Grab all databases
                databases = database.get_all(
                    dlpx_obj.server_session, no_js_data_source=False
                )
            database_lst = [db_name.name for db_name in databases]

            self._run_snapshot(dlpx_obj, datasets=database_lst)

    @run_async
    def _create_snapshot_helper(self, engine, dlpx_obj, single_thread):
        """
        This function is where we create our main workflow.
        Use the @run_async decorator to run this function asynchronously.
        The @run_async decorator allows us to run against multiple
        Delphix Engine simultaneously
        :param engine: Dictionary of engines
        :type engine: `dict`
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        :param single_thread: True - run single threaded, False -
            run multi-thread
        :type single_thread: `bool`
        """
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine)
        try:
            with dlpx_obj.job_mode(single_thread):
                self._get_db_list(dlpx_obj)
                run_job.track_running_jobs(
                    engine, dlpx_obj, poll=self.poll, failures=self.failures
                )
        except (
            dlpx_exceptions.DlpxObjectNotFound,
            exceptions.RequestError,
            exceptions.JobError,
            exceptions.HttpError,
        ) as err:
            dx_logging.print_exception(
                f'Error in {basename(__file__)}: {engine["hostname"]}\n{err}'
            )
            self.failures[0] = True

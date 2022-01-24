#
# Copyright (c) 2021 by Delphix. All rights reserved.
#
from os.path import basename

from delphixpy.v1_10_2 import exceptions
from dxi._lib import dlpx_exceptions as dxe
from dxi._lib import dx_logging as log
from dxi._lib import run_job
from dxi._lib import util
from dxi._lib.run_async import run_async
from dxi._lib.util import DXIConfigConstantsHelper
from dxi.database._internal_lib._mixins._dxi_delete import _DeleteMixin
from dxi.database._internal_lib._mixins._dxi_provision_vdb import (
    _ProvisionVDBMixin,
)
from dxi.database._internal_lib._mixins._dxi_refresh import _RefreshMixin
from dxi.database._internal_lib._mixins._dxi_rewind import _RewindMixin
from dxi.dxi_tool_base import DXIBase


class DXIVdbConstants(object):
    """
    Define constants for DXIVDB class
    """

    SINGLE_THREAD = False
    POLL = 20
    CONFIG = DXIConfigConstantsHelper().get_config()
    LOG_FILE_PATH = DXIConfigConstantsHelper().get_logdir()
    ENGINE_ID = "default"
    TIME_STAMP_TYPE = "SNAPSHOT"
    TIME_STAMP = "LATEST"
    TIME_FLOW = None
    PARALLEL = 5
    FORCE = False
    TYPE = "vdb"
    DB_TYPE = None


class DXIVdb(
    DXIBase, _RefreshMixin, _DeleteMixin, _RewindMixin, _ProvisionVDBMixin
):
    """
    Implement operations for vdb datasets
    """

    def __init__(
        self,
        engine=DXIVdbConstants.ENGINE_ID,
        single_thread=DXIVdbConstants.SINGLE_THREAD,
        poll=DXIVdbConstants.POLL,
        config=DXIVdbConstants.CONFIG,
        log_file_path=DXIVdbConstants.LOG_FILE_PATH,
        parallel=DXIVdbConstants.PARALLEL,
        module_name=__name__,
    ):
        """
          :param engine: An Identifier of Delphix engine in dxtools.conf.
          :type engine: `str`
          :param single_thread: Run as a single thread.
                 False if running multiple threads.
          :type single_thread: `bool`
          :param poll: The number of seconds to wait between job polls
          :type poll: `int`
          :param config: The path to the dxtools.conf file
          :type config: `str`
          :param log_file_path: The path to the logfile you want to use.
          :type log_file_path: `str`
          :param all_dbs: Run against all database objects
          :type all_dbs: `bool`
        """
        super().__init__(
            poll=poll,
            config=config,
            log_file_path=log_file_path,
            single_thread=single_thread,
            engine=engine,
            module_name=module_name,
            parallel=parallel,
        )
        self.vdb = ""
        self.time_stamp_type = ""
        self.time_stamp = ""
        self.time_flow = ""
        self.name = ""
        self.force = ""
        self.type = ""
        self.source_db = ""
        self.group = ""
        self.db_type = ""
        self.env_name = ""
        self.mntpoint = ""
        self.timestamp = ""
        self.timestamp_type = ""
        self.pre_refresh = ""
        self.post_refresh = ""
        self.pre_rollback = ""
        self.post_rollback = ""
        self.configure_clone = ""
        self.envinst = ""
        self.action = ""
        self.no_truncate_log = ""
        self.port_num = ""
        self.cdb_name = ""
        self.nodes = ""
        self.logsync = ""

    def refresh(
        self,
        name,
        time_stamp_type=DXIVdbConstants.TIME_STAMP_TYPE,
        time_stamp=DXIVdbConstants.TIME_STAMP,
        time_flow=DXIVdbConstants.TIME_FLOW,
    ):
        """
        Refresh a Delphix VDB or vFile.
        :param name: VDBs name
        :type name: `str`
        :param time_stamp_type: Either SNAPSHOT or TIME
        :type time_stamp_type: `str`
        :param time_stamp: The Delphix semantic for the point in time on
            the source from which you want to refresh your VDB.
        :type time_stamp: `str`
        :param time_flow: Name of the timeflow to refresh a VDB
        """
        try:
            self.vdb = name
            self.time_stamp_type = time_stamp_type
            self.time_stamp = time_stamp
            self.time_flow = time_flow
            self._execute_operation(self._refresh_helper)
            return True
        except (Exception, BaseException):
            return False

    def delete(self, name, db_type="vdb", force=False):
        """
        Deletes a VDB or a list of VDBs from an engine

        :param name: Colon[:] separated names of the VDBs/dSources to delete.
        :type name: `str`
        :param db_type: Type of object being deleted. vdb | dsource
        :type db_type: `str`
        :param force: To force delete the objects
        :type force: `bool`
        """
        try:
            self.name = name
            self.force = force
            self.db_type = db_type
            self._execute_operation(self._delete_main_workflow)
            return True
        except (Exception, BaseException):
            return False

    def rewind(
        self,
        name,
        time_stamp_type=DXIVdbConstants.TIME_STAMP_TYPE,
        time_stamp=DXIVdbConstants.TIME_STAMP,
        database_type=None,
    ):
        """
        Rewind the given vdb

        :param name: VDBs name
        :type name: `str`
        :param time_stamp_type: Either SNAPSHOT or TIME
        :type time_stamp_type: `str`
        :param time_stamp: The Delphix semantic for the point in time on
                the source from which you want to refresh your VDB.
          :type time_stamp: `str`
          :param database_type: Type of database: oracle, mssql, ase, vfiles
          :type database_type: `str`
        """
        self.vdb = name
        self.time_stamp_type = time_stamp_type
        self.time_stamp = time_stamp
        self.db_type = database_type
        try:
            self._execute_operation(self._rewind_helper)
            return True
        except Exception:
            return False

    def provision_postgres(
        self,
        target_grp,
        source_db,
        db,
        env_name,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=5432,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/provision",
        envinst=None,
    ):
        self.source_db = source_db
        self.name = db
        self.group = target_grp
        self.env_name = env_name
        self.mntpoint = mntpoint
        self.timestamp = timestamp
        self.timestamp_type = timestamp_type
        self.pre_refresh = prerefresh
        self.post_refresh = postrefresh
        self.pre_rollback = prerollback
        self.post_rollback = postrollback
        self.configure_clone = configure_clone
        self.envinst = envinst
        self.port_num = port_num
        try:
            self._execute_operation(
                self._provision_vdb_helper, self._provision_postgres_vdb
            )
            return True
        except Exception:
            return False

    def provision_vfiles(
        self,
        target_grp,
        source_db,
        db,
        env_name,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=5432,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/provision",
        envinst=None,
    ):
        self.source_db = source_db
        self.name = db
        self.group = target_grp
        self.env_name = env_name
        self.mntpoint = mntpoint
        self.timestamp = timestamp
        self.timestamp_type = timestamp_type
        self.pre_refresh = prerefresh
        self.post_refresh = postrefresh
        self.pre_rollback = prerollback
        self.post_rollback = postrollback
        self.configure_clone = configure_clone
        self.envinst = envinst
        self.port_num = port_num
        try:
            self._execute_operation(
                self._provision_vdb_helper, self._provision_vfiles_vdb
            )
            return True
        except Exception:
            return False

    def provision_ase(
        self,
        target_grp,
        source_db,
        db,
        env_name,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=5432,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/provision",
        envinst=None,
        no_truncate_log=False,
    ):
        self.source_db = source_db
        self.name = db
        self.group = target_grp
        self.env_name = env_name
        self.mntpoint = mntpoint
        self.timestamp = timestamp
        self.timestamp_type = timestamp_type
        self.pre_refresh = prerefresh
        self.post_refresh = postrefresh
        self.pre_rollback = prerollback
        self.post_rollback = postrollback
        self.configure_clone = configure_clone
        self.envinst = envinst
        self.port_num = port_num
        self.no_truncate_log = no_truncate_log
        try:
            self._execute_operation(
                self._provision_vdb_helper, self._provision_ase_vdb
            )
            return True
        except Exception:
            return False

    def provision_mssql(
        self,
        target_grp,
        source_db,
        db,
        env_name,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=5432,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/provision",
        envinst=None,
    ):
        self.source_db = source_db
        self.name = db
        self.group = target_grp
        self.env_name = env_name
        self.mntpoint = mntpoint
        self.timestamp = timestamp
        self.timestamp_type = timestamp_type
        self.pre_refresh = prerefresh
        self.post_refresh = postrefresh
        self.pre_rollback = prerollback
        self.post_rollback = postrollback
        self.configure_clone = configure_clone
        self.envinst = envinst
        self.port_num = port_num
        try:
            self._execute_operation(
                self._provision_vdb_helper, self._provision_mssql_vdb
            )
            return True
        except Exception:
            return False

    def provision_oracle_mt(
        self,
        target_grp,
        source_db,
        db,
        env_name,
        cdb_name,
        logsync,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=1521,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/provision",
        envinst=None,
    ):
        self.source_db = source_db
        self.name = db
        self.group = target_grp
        self.env_name = env_name
        self.cdb_name = cdb_name
        self.mntpoint = mntpoint
        self.timestamp = timestamp
        self.timestamp_type = timestamp_type
        self.pre_refresh = prerefresh
        self.post_refresh = postrefresh
        self.pre_rollback = prerollback
        self.post_rollback = postrollback
        self.configure_clone = configure_clone
        self.envinst = envinst
        self.port_num = port_num
        self.logsync = logsync
        try:
            self._execute_operation(
                self._provision_vdb_helper, self._provision_oracle_mt_vdb
            )
            return True
        except Exception:
            return False

    def provision_oracle_si(
        self,
        target_grp,
        source_db,
        db,
        env_name,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=5432,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/provision",
        envinst=None,
    ):
        self.source_db = source_db
        self.name = db
        self.group = target_grp
        self.env_name = env_name
        self.mntpoint = mntpoint
        self.timestamp = timestamp
        self.timestamp_type = timestamp_type
        self.pre_refresh = prerefresh
        self.post_refresh = postrefresh
        self.pre_rollback = prerollback
        self.post_rollback = postrollback
        self.configure_clone = configure_clone
        self.envinst = envinst
        self.port_num = port_num

        try:
            self._execute_operation(
                self._provision_vdb_helper, self._provision_oracle_si_vdb
            )
            return True
        except Exception:
            return False

    def provision_oracle_rac(
        self,
        target_grp,
        source_db,
        db,
        env_name,
        nodes,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=1521,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/provision",
        envinst=None,
    ):
        self.source_db = source_db
        self.name = db
        self.group = target_grp
        self.env_name = env_name
        self.mntpoint = mntpoint
        self.timestamp = timestamp
        self.timestamp_type = timestamp_type
        self.pre_refresh = prerefresh
        self.post_refresh = postrefresh
        self.pre_rollback = prerollback
        self.post_rollback = postrollback
        self.configure_clone = configure_clone
        self.envinst = envinst
        self.port_num = port_num
        self.nodes = nodes

        try:
            self._execute_operation(
                self._provision_vdb_helper, self._provision_oracle_rac_vdb
            )
            return True
        except Exception:
            return False

    def provision_oracle_mt_rac(
        self,
        target_grp,
        source_db,
        db,
        env_name,
        cdb_name,
        nodes,
        logsync,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=1521,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/provision",
        envinst=None,
    ):
        self.source_db = source_db
        self.name = db
        self.group = target_grp
        self.env_name = env_name
        self.mntpoint = mntpoint
        self.cdb_name = cdb_name
        self.nodes = nodes
        self.timestamp = timestamp
        self.timestamp_type = timestamp_type
        self.pre_refresh = prerefresh
        self.post_refresh = postrefresh
        self.pre_rollback = prerollback
        self.post_rollback = postrollback
        self.configure_clone = configure_clone
        self.envinst = envinst
        self.port_num = port_num
        self.logsync = logsync

        try:
            self._execute_operation(
                self._provision_vdb_helper, self._provision_oracle_mt_rac_vdb
            )
            return True
        except Exception:
            return False

    @run_async
    def _provision_vdb_helper(
        self, engine, dlpx_obj, single_thread, function_ref=None
    ):
        """
        This function is where we create our main workflow.
        Use the @run_async decorator to run this function asynchronously.
        The @run_async decorator to run multithreaded on Delphix Engines
        simultaneously
        :param engine: Dictionary of engines
        :type engine: dictionary
        :param single_thread: True - run single threaded,
                               False - run multi-thread
        :type single_thread: bool
        """
        if not function_ref:
            self.failures = [True]
            raise Exception("Worker method is not defined for this operation")
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine)
        if dlpx_obj.server_session:
            try:
                with dlpx_obj.job_mode(single_thread):
                    function_ref(dlpx_obj)
                    run_job.track_running_jobs(engine, dlpx_obj, self.poll)
            except (
                dxe.DlpxException,
                exceptions.RequestError,
                exceptions.JobError,
                exceptions.HttpError,
            ) as err:
                e = util.format_err_msg(
                    err, operation="provision", engine_name=engine["hostname"]
                )
                log.print_exception(f"Error in {basename(__file__)}\n" f"{e}")
                self.failures = [True]
                # raise err
            except (dxe.DlpxObjectExists) as err:
                e = util.format_err_msg(
                    err.message,
                    operation="VDB/Vfile Provision",
                    engine_name=engine["hostname"],
                )
                log.print_exception(f"Error in {basename(__file__)}\n" f"{e}")
                self.failures = [True]
                # raise err

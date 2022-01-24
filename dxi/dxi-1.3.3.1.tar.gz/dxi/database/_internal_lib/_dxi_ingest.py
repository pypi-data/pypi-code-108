#
# Copyright (c) 2021 by Delphix. All rights reserved.
#
"""
Create and sync a dSource
"""
from os.path import basename

from delphixpy.v1_10_2 import exceptions
from dxi._lib import dlpx_exceptions as dxe
from dxi._lib import dx_logging as log
from dxi._lib import run_job
from dxi._lib import util
from dxi._lib.run_async import run_async
from dxi._lib.util import DXIConfigConstantsHelper
from dxi.database._internal_lib._ingest_lib import dsource_link_ase
from dxi.database._internal_lib._ingest_lib import dsource_link_mssql
from dxi.database._internal_lib._ingest_lib import dsource_link_oracle
from dxi.database._internal_lib._ingest_lib import dsource_link_oraclemt
from dxi.dxi_tool_base import DXIBase


class DXIProvisionDsourceConstants(object):
    """
    Class of common constants used by Provision dSource
    """

    SINGLE_THREAD = False
    POLL = 10
    CONFIG = DXIConfigConstantsHelper().get_config()
    LOG_FILE_PATH = DXIConfigConstantsHelper().get_logdir()
    ENGINE_ID = "default"
    PARALLEL = 5
    ACTION = None
    MODULE_NAME = __name__
    VDB_LIST_HEADER = []
    FORCE = False


class DXIDsource(DXIBase):
    def __init__(
        self,
        engine=None,
        log_file_path=DXIProvisionDsourceConstants.LOG_FILE_PATH,
        config=DXIProvisionDsourceConstants.CONFIG,
        poll=DXIProvisionDsourceConstants.POLL,
        single_thread=DXIProvisionDsourceConstants.SINGLE_THREAD,
        parallel=DXIProvisionDsourceConstants.PARALLEL,
        action=DXIProvisionDsourceConstants.ACTION,
        module_name=DXIProvisionDsourceConstants.MODULE_NAME,
    ):
        super().__init__(
            parallel=parallel,
            poll=poll,
            config=config,
            log_file_path=log_file_path,
            single_thread=single_thread,
            engine=engine,
            module_name=module_name,
        )
        self.dsource_name = ""
        self.db_passwd = ""
        self.db_user = ""
        self.dx_group = ""
        self.env_name = ""
        self.envinst = ""
        self.ip_addr = ""
        self.db_type = ""
        self.logsync_mode = ""
        self.port_num = ""
        self.num_connections = ""
        self.files_per_set = ""
        self.rman_channels = ""
        self.create_bckup = ""
        self.bck_file = ""
        self.db_install_path = ""
        self.backup_loc_passwd = ""
        self.backup_loc_user = ""
        self.load_from_backup = ""
        self.ase_passwd = ""
        self.ase_user = ""
        self.backup_path = ""
        self.sync_mode = ""
        self.source_user = ""
        self.stage_user = ""
        self.stage_repo = ""
        self.stage_instance = ""
        self.validated_sync_mode = ""
        self.logsync = True
        self.stage_env = ""
        self.initial_load_type = ""
        self.delphix_managed = ""
        self.source_env = ""
        self.action = action

    def ingest_mssql(
        self,
        dsource_name,
        db_passwd,
        db_user,
        dx_group,
        logsync,
        validated_sync_mode,
        initial_load_type,
        delphix_managed,
        stage_env,
        stage_instance,
        backup_path,
        backup_loc_passwd,
        backup_loc_user,
        source_env
    ):
        self.dsource_name = dsource_name
        self.db_passwd = db_passwd
        self.db_user = db_user
        self.dx_group = dx_group
        self.logsync = logsync
        self.validated_sync_mode = validated_sync_mode
        self.initial_load_type = initial_load_type
        self.delphix_managed = delphix_managed
        self.stage_env = stage_env
        self.stage_instance = stage_instance
        self.backup_path = backup_path
        self.backup_loc_passwd = backup_loc_passwd
        self.backup_loc_user = backup_loc_user
        self.source_env = source_env
        try:
            self._execute_operation(self.__ingest_mssql_helper)
            return True
        except Exception:
            return False

    @run_async
    def __ingest_mssql_helper(self, engine, dlpx_obj, single_thread):
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine)
        if dlpx_obj.server_session:
            try:
                with dlpx_obj.job_mode(single_thread):
                    mssql_obj = dsource_link_mssql.DsourceLinkMssql(
                        dlpx_obj,
                        self.dsource_name,
                        self.db_passwd,
                        self.db_user,
                        self.dx_group,
                        self.logsync,
                        self.stage_env,
                        self.validated_sync_mode,
                        self.initial_load_type,
                        self.delphix_managed,
                    )

                    mssql_obj.link_mssql_dsource(
                        self.source_env,
                        self.stage_env,
                        self.stage_instance,
                        self.backup_path,
                        self.backup_loc_passwd,
                        self.backup_loc_user,
                        uuid="Any",
                    )
                    self._add_last_job_to_track(dlpx_obj)
                    run_job.track_running_jobs(engine, dlpx_obj, self.poll)
            except (
                dxe.DlpxException,
                exceptions.RequestError,
                exceptions.JobError,
                exceptions.HttpError,
            ) as err:
                log.print_exception(
                    f"Error in {basename(__file__)}:"
                    f'{engine["hostname"]}\n ERROR: {err}'
                )
                raise err
        self._remove_session(dlpx_obj.server_session)

    def ingest_sybase(
        self,
        source_name,
        db_user,
        db_password,
        group,
        source_env,
        env_name,
        stage_repo,
        backup_path,
        backup_files,
        logsync,
        create_bckup,
    ):
        self.dsource_name = source_name
        self.db_passwd = db_password
        self.db_user = db_user
        self.dx_group = group
        self.logsync = logsync
        self.stage_repo = stage_repo
        self.backup_path = backup_path
        self.bck_file = backup_files
        self.create_bckup = create_bckup
        self.env_name = env_name
        self.source_env = source_env
        try:
            self._execute_operation(self.__ingest_sybase_helper)
            return True
        except Exception:
            return False

    @run_async
    def __ingest_sybase_helper(self, engine, dlpx_obj, single_thread):
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine)
        if dlpx_obj.server_session:
            try:
                with dlpx_obj.job_mode(single_thread):
                    ase_obj = dsource_link_ase.DsourceLinkASE(
                        dlpx_obj,
                        self.dsource_name,
                        self.db_passwd,
                        self.db_user,
                        self.dx_group,
                        self.logsync,
                        self.stage_repo,

                    )
                    ase_obj.link_ase_dsource(
                        self.backup_path,
                        self.bck_file,
                        self.create_bckup,
                        self.env_name,
                        self.source_env
                    )
                    self._add_last_job_to_track(dlpx_obj)
                    run_job.track_running_jobs(engine, dlpx_obj, self.poll)
            except (
                dxe.DlpxException,
                exceptions.RequestError,
                exceptions.JobError,
                exceptions.HttpError,
            ) as err:
                log.print_exception(
                    f"Error in {basename(__file__)}:"
                    f'{engine["hostname"]}\n ERROR: {err}'
                )
                raise err
        self._remove_session(dlpx_obj.server_session)

    def ingest_oracle(
        self,
        dsource_name,
        db_passwd,
        db_user,
        dx_group,
        logsync,
        env_name,
        db_install_path,
        ip_addr,
        port_num,
        rman_channels,
        files_per_set,
        num_connections,
    ):
        self.dsource_name = dsource_name
        self.db_passwd = db_passwd
        self.db_user = db_user
        self.dx_group = dx_group
        self.logsync = logsync
        self.env_name = env_name
        self.db_install_path = db_install_path
        self.ip_addr = ip_addr
        self.port_num = int(port_num)
        self.rman_channels = rman_channels
        self.files_per_set = files_per_set
        self.num_connections = num_connections
        try:
            self._execute_operation(self._ingest_oracle_helper)
            return True
        except Exception:
            return False

    def ingest_oracle_mt_rac(
        self,
        dsource_name,
        db_passwd,
        db_user,
        dx_group,
        logsync,
        env_name,
        db_install_path,
        rman_channels,
        files_per_set,
        num_connections,
    ):
        self.dsource_name = dsource_name
        self.db_passwd = db_passwd
        self.db_user = db_user
        self.dx_group = dx_group
        self.logsync = logsync
        self.env_name = env_name
        self.db_install_path = db_install_path
        self.rman_channels = rman_channels
        self.files_per_set = files_per_set
        self.num_connections = num_connections
        try:
            self._execute_operation(self._ingest_oracle_mt_helper)
            return True
        except Exception:
            return False

    @run_async
    def _ingest_oracle_helper(self, engine, dlpx_obj, single_thread):
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine)
        if dlpx_obj.server_session:
            try:
                with dlpx_obj.job_mode(single_thread):
                    linked_ora = dsource_link_oracle.DsourceLinkOracle(
                        dlpx_obj=dlpx_obj,
                        dsource_name=self.dsource_name,
                        db_passwd=self.db_passwd,
                        db_user=self.db_user,
                        dx_group=self.dx_group,
                        logsync=self.logsync,
                        num_connections=self.num_connections,
                        files_per_set=self.files_per_set,
                        rman_channels=self.rman_channels,
                    )
                    linked_ora.get_or_create_ora_sourcecfg(
                        self.env_name,
                        self.db_install_path,
                        self.ip_addr,
                        port_num=int(self.port_num),
                    )
                    self._add_last_job_to_track(dlpx_obj)
                    run_job.track_running_jobs(engine, dlpx_obj, self.poll)
            except (
                dxe.DlpxException,
                exceptions.RequestError,
                exceptions.JobError,
                exceptions.HttpError,
            ) as err:
                e = util.format_err_msg(
                    err,
                    operation="Dsource Ingestion",
                    engine_name=engine["hostname"],
                )
                log.print_exception(f"Error in {basename(__file__)}" f"{e}")
                # raise err
                self.failures = [True]
        self._remove_session(dlpx_obj.server_session)

    @run_async
    def _ingest_oracle_mt_helper(self, engine, dlpx_obj, single_thread):
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine)
        if dlpx_obj.server_session:
            try:
                with dlpx_obj.job_mode(single_thread):
                    linked_ora = dsource_link_oraclemt.DsourceLinkOracleMT(
                        dlpx_obj=dlpx_obj,
                        dsource_name=self.dsource_name,
                        db_passwd=self.db_passwd,
                        db_user=self.db_user,
                        dx_group=self.dx_group,
                        logsync=self.logsync,
                        num_connections=self.num_connections,
                        files_per_set=self.files_per_set,
                        rman_channels=self.rman_channels,
                    )
                    linked_ora.get_or_create_ora_sourcecfg(
                        self.env_name,
                        self.db_install_path,
                    )
                    self._add_last_job_to_track(dlpx_obj)
                    run_job.track_running_jobs(engine, dlpx_obj, self.poll)
            except (
                dxe.DlpxException,
                exceptions.RequestError,
                exceptions.JobError,
                exceptions.HttpError,
            ) as err:
                e = util.format_err_msg(
                    err,
                    operation="Dsource Ingestion",
                    engine_name=engine["hostname"],
                )
                log.print_exception(f"Error in {basename(__file__)}" f"{e}")
                # raise err
                self.failures = [True]
        self._remove_session(dlpx_obj.server_session)


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
from dxi._lib.run_async import run_async
from dxi.database._internal_lib._ingest_lib import dsource_link_ase
from dxi.database._internal_lib._ingest_lib import dsource_link_mssql
from dxi.database._internal_lib._ingest_lib import dsource_link_oracle


class _ProvisionDsourceMixin(object):
    def _provision_dsource_helper(self, dlpx_obj):
        if self.db_type.lower() == "oracle":
            linked_ora = dsource_link_oracle.DsourceLinkOracle(
                dlpx_obj,
                self.dsource_name,
                self.db_passwd,
                self.db_user,
                self.dx_group,
                self.logsync,
                self.logsync_mode,
                self.db_type,
            )
            linked_ora.get_or_create_ora_sourcecfg(
                self.env_name,
                self.db_install_path,
                self.ip_addr,
                self.port_num,
            )
        elif self.db_type.lower() == "sybase":
            ase_obj = dsource_link_ase.DsourceLinkASE(
                dlpx_obj,
                self.dsource_name,
                self.db_passwd,
                self.db_user,
                self.dx_group,
                self.logsync,
                self.stage_repo,
                self.db_type,
            )
            ase_obj.link_ase_dsource(
                self.backup_path,
                self.bck_file,
                self.create_bckup,
                self.env_name,
            )
        elif self.db_type.lower() == "mssql":
            mssql_obj = dsource_link_mssql.DsourceLinkMssql(
                dlpx_obj,
                self.dsource_name,
                self.db_passwd,
                self.db_user,
                self.dx_group,
                self.db_type,
                self.logsync,
                self.validated_sync_mode,
                self.initial_load_type,
                self.delphix_managed,
            )
            mssql_obj.link_mssql_dsource(
                self.stage_env,
                self.stage_instance,
                self.backup_path,
                self.backup_loc_passwd,
                self.backup_loc_user,
                uuid="Any",
            )

    @run_async
    def _provision_dsource_runner(self, engine, dlpx_obj, single_thread):
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
        err = None
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine)
        if dlpx_obj.server_session:
            try:
                with dlpx_obj.job_mode(single_thread):
                    self._provision_dsource_helper(dlpx_obj)
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

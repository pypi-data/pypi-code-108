#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

from os.path import basename

from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2.web import source
from delphixpy.v1_10_2.web.capacity import consumer
from delphixpy.v1_10_2.web.vo import SourceDisableParameters
from dxi._lib import dlpx_exceptions as dxe
from dxi._lib import dx_logging as log
from dxi._lib import get_references as ref
from dxi._lib import run_job
from dxi._lib.dxi_constants import VirtualOps
from dxi._lib.run_async import run_async
from dxi._lib.util import DXIConfigConstantsHelper
from dxi.dxi_tool_base import DXIBase


class DXIDbConstants(object):
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


class DXIDb(DXIBase):
    """
    Implement operations for vdb datasets
    """

    def __init__(
        self,
        engine=DXIDbConstants.ENGINE_ID,
        single_thread=DXIDbConstants.SINGLE_THREAD,
        poll=DXIDbConstants.POLL,
        config=DXIDbConstants.CONFIG,
        log_file_path=DXIDbConstants.LOG_FILE_PATH,
        parallel=DXIDbConstants.PARALLEL,
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
        self.db_type = ""
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
        self.port_num = ""
        if not self.name or self.group:
            raise dxe.DXIException("DB operations require --db-name, --group"
                                   "or both arguments.")

    def list(self):
        """
        List datasets on an engine
        """
        self.action = VirtualOps.LIST
        self.db_list = []
        try:
            self._execute_operation(self._db_operation_helper)
            log.print_debug("End of Execution")
            return self.db_list
        except Exception as err:
            log.print_exception(
                f"An Error was encountered while "
                f"listing the datasets: {repr(err)}"
            )
            return False

    def start(self, name, group=None):
        """
        Start a Virtual dataset by name
        """
        self.action = VirtualOps.START
        self.name = name
        self.group = group
        if not self.name and not self.group:
            raise dxe.DXIException("Start requires --db-name, --group "
                                   "or both arguments.")
        try:
            self._execute_operation(self._db_operation_helper)
            log.print_debug("End of Execution")
            return True
        except Exception as err:
            log.print_exception(
                f"An Error was encountered while "
                f"starting the virtual dataset: {repr(err)}"
            )
            return False

    def stop(self, name, group=None):
        """
        Stop a Virtual dataset by name
        """
        self.action = VirtualOps.STOP
        self.name = name
        self.group = group
        if not self.name and not self.group:
            raise dxe.DXIException("Stop requires --db-name, --group "
                                   "or both arguments.")
        try:
            self._execute_operation(self._db_operation_helper)
            log.print_debug("End of Execution")
            return True
        except Exception as err:
            log.print_exception(
                f"An Error was encountered while "
                f"stopping the virtual dataset: {repr(err)}"
            )
            return False

    def enable(self, name, group=None):
        """
        Enable a Virtual dataset by name
        """
        self.action = VirtualOps.ENABLE
        self.name = name
        self.group = group
        if not self.name and not self.group:
            raise dxe.DXIException("Enable requires --db-name, --group "
                                   "or both arguments.")
        try:
            self._execute_operation(self._db_operation_helper)
            log.print_debug("End of Execution")
            return True
        except Exception as err:
            log.print_exception(
                f"An Error was encountered while "
                f"enabling the virtual dataset: {repr(err)}"
            )
            return False

    def disable(self, name, group=None, force=False):
        """
        Disable a Virtual dataset by name
        """
        self.action = VirtualOps.DISABLE
        self.name = name
        self.group = group
        self.force = force
        if not self.name and not self.group:
            raise dxe.DXIException("Disable requires --db-name, --group "
                                   "or both arguments.")
        try:
            self._execute_operation(self._db_operation_helper)
            log.print_debug("End of Execution")
            return True
        except Exception as err:
            log.print_exception(
                f"An Error was encountered while "
                f"disabling the virtual dataset: {repr(err)}"
            )
            return False

    def _start(self, dlpx_obj):
        """
        Starts a dataset
        :return:
        """
        svr_session = dlpx_obj.server_session
        try:
            if self.group and self.name:
                vdb_container_obj = ref.find_db_by_name_and_group(
                    svr_session, self.group, self.name
                )
                vdb_obj = ref.find_source_obj_by_containerref(
                    svr_session, source, vdb_container_obj.reference
                )
                source.start(svr_session, vdb_obj.reference)
                self._add_last_job_to_track(dlpx_obj)
            if self.group and not self.name:
                group_dbs = ref.find_all_databases_by_group(svr_session,
                                                            self.group
                                                            )
                for db in group_dbs:
                    source_db = ref.find_source_by_db_name(svr_session,
                                                           db.name
                                                           )
                    if source_db.virtual is True:
                        source.start(svr_session, source_db.reference)
                        self._add_last_job_to_track(dlpx_obj)
            elif self.name and not self.group:
                vdb_obj = ref.find_obj_by_name(svr_session, source, self.name)
                source.start(svr_session, vdb_obj.reference)
                self._add_last_job_to_track(dlpx_obj)
        except (
            exceptions.RequestError,
            exceptions.JobError,
            AttributeError,
        ) as err:
            log.print_exception(
                f"An error occurred while starting dataset {self.name}: {err}"
            )
            self.failures[0] = True

    def _stop(self, dlpx_obj):
        """
        Stops a dataset
        :return:
        """
        svr_session = dlpx_obj.server_session
        try:
            if self.group and self.name:
                vdb_container_obj = ref.find_db_by_name_and_group(
                    svr_session, self.group, self.name
                )
                vdb_obj = ref.find_source_obj_by_containerref(
                    svr_session, source, vdb_container_obj.reference
                )
                source.stop(svr_session, vdb_obj.reference)
                self._add_last_job_to_track(dlpx_obj)
            if self.group and not self.name:
                group_dbs = ref.find_all_databases_by_group(svr_session,
                                                            self.group
                                                            )
                for db in group_dbs:
                    source_db = ref.find_source_by_db_name(svr_session,
                                                           db.name
                                                           )
                    if source_db.virtual is True:
                        source.stop(svr_session, source_db.reference)
                        self._add_last_job_to_track(dlpx_obj)

            elif self.name and not self.group:
                vdb_obj = ref.find_obj_by_name(svr_session, source, self.name)
                source.stop(svr_session, vdb_obj.reference)
                self._add_last_job_to_track(dlpx_obj)

        except (
            exceptions.RequestError,
            exceptions.JobError,
            AttributeError,
        ) as err:
            log.print_exception(
                f"An error occurred while stopping dataset {self.name}: {err}"
            )
            self.failures[0] = True

    def _enable(self, dlpx_obj):
        """
        Enables a dataset
        :return:
        """
        svr_session = dlpx_obj.server_session
        try:
            if self.group and self.name:
                vdb_container_obj = ref.find_db_by_name_and_group(
                    svr_session, self.group, self.name
                )
                vdb_obj = ref.find_source_obj_by_containerref(
                    svr_session, source, vdb_container_obj.reference
                )
                source.enable(svr_session, vdb_obj.reference)
                self._add_last_job_to_track(dlpx_obj)
            if self.group and not self.name:
                group_dbs = ref.find_all_databases_by_group(svr_session,
                                                            self.group
                                                            )
                for db in group_dbs:
                    source_db = ref.find_source_by_db_name(svr_session,
                                                           db.name
                                                           )
                    if source_db.virtual is True:
                        source.enable(svr_session, source_db.reference)
                        self._add_last_job_to_track(dlpx_obj)
            elif self.name and not self.group:
                vdb_obj = ref.find_obj_by_name(svr_session, source, self.name)
                source.enable(svr_session, vdb_obj.reference)
                self._add_last_job_to_track(dlpx_obj)
        except (
            exceptions.RequestError,
            exceptions.JobError,
            AttributeError,
        ) as err:
            log.print_exception(
                f"An error occurred while enabling dataset {self.name}: {err}"
            )
            self.failures[0] = True

    def _disable(self, dlpx_obj):
        """
        Disables a dataset
        :return:
        """
        svr_session = dlpx_obj.server_session
        disable_params = SourceDisableParameters()
        try:
            if self.group and self.name:
                vdb_container_obj = ref.find_db_by_name_and_group(
                    svr_session, self.group, self.name
                )
                vdb_obj = ref.find_source_obj_by_containerref(
                    svr_session, source, vdb_container_obj.reference
                )
                source.disable(svr_session, vdb_obj.reference)
                self._add_last_job_to_track(dlpx_obj)
            if self.group and not self.name:
                group_dbs = ref.find_all_databases_by_group(svr_session,
                                                            self.group
                                                            )
                for db in group_dbs:
                    source_db = ref.find_source_by_db_name(svr_session,
                                                           db.name
                                                           )
                    if source_db.virtual is True:
                        source.disable(svr_session, source_db.reference)
                        self._add_last_job_to_track(dlpx_obj)
            elif self.name and not self.group:
                vdb_obj = ref.find_obj_by_name(svr_session, source, self.name)
                if self.force:
                    disable_params.attempt_cleanup = False
                    source.disable(svr_session, vdb_obj.reference, disable_params)
                else:
                    source.disable(svr_session, vdb_obj.reference)
                self._add_last_job_to_track(dlpx_obj)
        except (
            exceptions.RequestError,
            exceptions.JobError,
            AttributeError,
        ) as err:
            log.print_exception(
                f"An error occurred while disabling dataset {self.name}: {err}"
            )
            self.failures[0] = True

    def _list(self, dlpx_obj):
        """
        Lists all databases with stats for an engine
        """
        svr_session = dlpx_obj.server_session
        db_size = None
        active_space = None
        sync_space = None
        log_space = None
        try:
            all_source_objs = source.get_all(svr_session)
            all_consumer_objs = consumer.get_all(svr_session)
            for db_stats in all_consumer_objs:
                source_stats = ref.find_obj_list_by_containername(
                    all_source_objs, db_stats.container
                )
                if source_stats is not None:
                    active_space = (
                        db_stats.breakdown.active_space / 1024 / 1024 / 1024
                    )
                    sync_space = (
                        db_stats.breakdown.sync_space / 1024 / 1024 / 1024
                    )
                    log_space = db_stats.breakdown.log_space / 1024 / 1024
                    db_size = (
                        source_stats.runtime.database_size / 1024 / 1024 / 1024
                    )
                if source_stats.virtual is False:
                    print(
                        f"name: {db_stats.name}, ingest container:"
                        f" {db_stats.parent}, disk usage: {db_size:.2f}GB,"
                        f"Size of Snapshots: {active_space:.2f}GB, "
                        f"dSource Size: {sync_space:.2f}GB, "
                        f"Log Size: {log_space:.2f}MB,"
                        f"Enabled: {source_stats.runtime.enabled},"
                        f"Status: {source_stats.runtime.status}"
                    )
                    self.db_list.append(
                        f"name: {db_stats.name}, ingest container:"
                        f" {db_stats.parent}, disk usage: {db_size:.2f}GB,"
                        f"Size of Snapshots: {active_space:.2f}GB, "
                        f"dSource Size: {sync_space:.2f}GB, "
                        f"Log Size: {log_space:.2f}MB,"
                        f"Enabled: {source_stats.runtime.enabled},"
                        f"Status: {source_stats.runtime.status}"
                    )
                elif source_stats.virtual is True:
                    print(
                        f"name: {db_stats.name}, ingest container: "
                        f"{db_stats.parent}, disk usage: "
                        f"{active_space:.2f}GB, Size of Snapshots: "
                        f"{sync_space:.2f}GB"
                        f"Log Size: {log_space:.2f}MB, Enabled: "
                        f"{source_stats.runtime.enabled}, "
                        f"Status: {source_stats.runtime.status}"
                    )
                    self.db_list.append(
                        f"name: {db_stats.name}, ingest container: "
                        f"{db_stats.parent}, disk usage: "
                        f"{active_space:.2f}GB, Size of Snapshots: "
                        f"{sync_space:.2f}GB"
                        f"Log Size: {log_space:.2f}MB, Enabled: "
                        f"{source_stats.runtime.enabled}, "
                        f"Status: {source_stats.runtime.status}"
                    )
                elif source_stats is None:
                    print(
                        f"name: {db_stats.name},ingest container: "
                        f"{db_stats.parent}, database disk usage: "
                        f"{db_size:.2f}GB,"
                        f"Size of Snapshots: {active_space:.2f}GB,"
                        "Could not find source information. This could be a "
                        "result of an unlinked object"
                    )
                    self.db_list.append(
                        f"name: {db_stats.name},ingest container: "
                        f"{db_stats.parent}, database disk usage: "
                        f"{db_size:.2f}GB,"
                        f"Size of Snapshots: {active_space:.2f}GB,"
                        "Could not find source information. This could be a "
                        "result of an unlinked object"
                    )
        except (
            exceptions.RequestError,
            AttributeError,
            dxe.DlpxException,
        ) as err:
            log.print_exception(
                f"An error occurred while listing databases: {err}"
            )
            self.failures[0] = True
        except Exception as err:
            log.print_exception(
                f"An error occurred while listing databases: {err}"
            )
            self.failures[0] = True

    @run_async
    def _db_operation_helper(self, engine, dlpx_obj, single_thread):
        """
        This function is where we create our main workflow.
        Use the @run_async decorator to run this function asynchronously.
        The @run_async decorator to run multithreaded on Delphix Engines
        simultaneously
        :param engine: Dictionary of engines
        :type engine: dictionary
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        :param single_thread: True - run single threaded,
                               False - run multi-thread
        :type single_thread: bool
        """
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine)
        if dlpx_obj.server_session:
            try:
                with dlpx_obj.job_mode(single_thread):
                    if self.action == VirtualOps.START:
                        self._start(dlpx_obj)
                    elif self.action == VirtualOps.STOP:
                        self._stop(dlpx_obj)
                    elif self.action == VirtualOps.ENABLE:
                        self._enable(dlpx_obj)
                    elif self.action == VirtualOps.DISABLE:
                        self._disable(dlpx_obj)
                    elif self.action == VirtualOps.LIST:
                        self._list(dlpx_obj)
                    run_job.track_running_jobs(
                        engine,
                        dlpx_obj,
                        poll=self.poll,
                        failures=self.failures,
                    )
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
                # raise err
                self.failures[0] = True

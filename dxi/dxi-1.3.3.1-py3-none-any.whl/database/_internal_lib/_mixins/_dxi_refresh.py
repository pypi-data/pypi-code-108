#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2.web import database
from delphixpy.v1_10_2.web import vo
from dxi._lib import dlpx_exceptions
from dxi._lib import dx_logging
from dxi._lib import dx_timeflow
from dxi._lib import get_references
from dxi._lib import run_job
from dxi._lib import util
from dxi._lib.run_async import run_async


class _RefreshMixin(object):
    def _run_refresh_for_vdb(self, dlpx_obj):
        """
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        """
        for vdb_name in self.vdb.split(":"):
            dx_timeflow_obj = dx_timeflow.DxTimeflow(dlpx_obj.server_session)
            dx_logging.print_debug(f" Refreshing {vdb_name}")
            container_obj = get_references.find_obj_by_name(
                dlpx_obj.server_session, database, vdb_name
            )
            source_obj = get_references.find_source_by_db_name(
                dlpx_obj.server_session, vdb_name
            )
            # Sanity check to make sure our container object has a reference
            if container_obj.reference:
                try:
                    if (
                        source_obj.virtual is not True
                        or source_obj.staging is True
                    ):
                        dx_logging.print_exception(
                            f"{self.vdb} is not a virtual object.\n"
                        )
                    elif source_obj.runtime.enabled == "ENABLED":
                        dx_logging.print_debug(
                            f"INFO: Refreshing {self.vdb} "
                            f"to {self.time_stamp}\n"
                        )
                # This exception is raised if refreshing a vFiles VDB since
                # AppDataContainer does not have virtual,
                # staging or enabled attributes
                except AttributeError:
                    pass
            if source_obj.reference:
                try:
                    source_db = database.get(
                        dlpx_obj.server_session,
                        container_obj.provision_container,
                    )
                except (exceptions.RequestError, exceptions.JobError) as err:
                    raise dlpx_exceptions.DlpxException(
                        f"Encountered error while refreshing:"
                        f"{vdb_name}:\n{err}"
                    )

                if str(container_obj.reference).startswith("ORACLE"):
                    refresh_params = vo.OracleRefreshParameters()
                else:
                    refresh_params = vo.RefreshParameters()

                refresh_params.timeflow_point_parameters = dx_timeflow_obj.set_timeflow_point(  # noqa
                    source_db,
                    timestamp_type=self.time_stamp_type,
                    timestamp=self.time_stamp,
                    engine_session_ref=dlpx_obj.server_session,
                )
                try:
                    database.refresh(
                        dlpx_obj.server_session,
                        container_obj.reference,
                        refresh_params,
                    )
                    self._add_last_job_to_track(dlpx_obj)
                except (
                    dlpx_exceptions.DlpxException,
                    exceptions.RequestError,
                ) as err:
                    dx_logging.print_exception(
                        f"ERROR: Could not set timeflow point:{err}"
                    )
                    raise dlpx_exceptions.DlpxException(
                        f"ERROR: Could not set time flow point:{err}"
                    )
            # Don't do anything if the database is disabled
            else:
                dx_logging.print_debug(
                    f"INFO: {container_obj.name} is not enabled."
                    f" Refresh will not continue.\n"
                )

    def _refresh_validate_data(self):
        self.display_choices(self)
        dx_logging.print_debug("Validating inputs for refresh operation")
        if self.vdb and self.group:
            raise Exception("Name and Group both cannot be passed together.")
        if not (self.vdb or self.group):
            raise Exception("Either vdb name or group must be defined")

        if self.time_stamp_type.upper() not in ["TIME", "SNAPSHOT"]:
            raise Exception(
                "Possible values for Time stamp type: TIME|SNAPSHOT "
            )

    @run_async
    def _refresh_helper(self, engine, dlpx_obj, single_thread):
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
        self._refresh_validate_data()
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine)
        try:
            with dlpx_obj.job_mode(single_thread):
                self._run_refresh_for_vdb(dlpx_obj)
                dx_logging.print_debug(f"All refreshes must be running now")
                run_job.track_running_jobs(
                    engine, dlpx_obj, poll=self.poll, failures=self.failures
                )
        except (Exception, BaseException) as err:
            e = util.format_err_msg(
                err,
                engine_name=engine["hostname"],
                operation="VDB/Vfile Refresh",
            )
            dx_logging.print_exception(f"Error in dxi_refresh\n" f"{e}")
            self.failures[0] = True

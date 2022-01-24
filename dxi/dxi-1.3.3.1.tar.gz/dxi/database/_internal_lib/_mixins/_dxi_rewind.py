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
from dxi._lib.run_async import run_async


class _RewindMixin(object):
    """
    Refresh a Delphix VDB
    """

    def _rewind_validate_data(self):
        dx_logging.print_debug("Validating inputs for rewind operation")
        if not self.vdb:
            raise Exception("Invalid VDB name")

        if self.time_stamp_type not in ["TIME", "SNAPSHOT"]:
            raise Exception("Either vdb name or group must be defined")

    @run_async
    def _rewind_helper(self, engine, dlpx_obj, single_thread):
        """
        This function is where we create our main workflow.
        Use the @run_async decorator to run this function asynchronously.
        The @run_async decorator allows us to run against multiple
        Delphix Engine simultaneously
        :param engine: Dictionary of engines
        :type engine: dictionary
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        :param single_thread: True - run single threaded, False -
            run multi-thread
        :type single_thread: bool
        """
        func_ref = "_RewindMixin._rewind_helper()"
        self._rewind_validate_data()
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine)
        try:
            dx_timeflow_obj = dx_timeflow.DxTimeflow(dlpx_obj.server_session)
            container_obj = get_references.find_obj_by_name(
                dlpx_obj.server_session, database, self.vdb
            )
            with dlpx_obj.job_mode(single_thread):
                dx_logging.print_debug(f" Rewinding {self.vdb}")
                container_obj = get_references.find_obj_by_name(
                    dlpx_obj.server_session, database, self.vdb
                )
                # Make sure our container object has a reference
                if container_obj.reference:
                    try:
                        if container_obj.runtime.enabled == "ENABLED":
                            dx_logging.print_debug(
                                f"INFO: {engine['hostname']} Rewinding "
                                f"{container_obj.name} to {self.time_stamp}\n"
                            )
                        elif (
                            container_obj.virtual is not True
                            or container_obj.staging is True
                        ):
                            raise dlpx_exceptions.DlpxException(
                                f"{container_obj.name} on "
                                f"Delphix Engine:{engine['hostname']} "
                                f"is not a virtual object. "
                                f"Rewind operation cannot continue.\n"
                            )
                    # This exception is raised if rewinding a vFiles VDB since
                    # AppDataContainer does not have virtual,
                    # staging or enabled attributes
                    except AttributeError:
                        pass
                    # If the vdb is a Oracle type, we need to use a
                    # OracleRollbackParameters
                    if str(container_obj.reference).startswith("ORACLE"):
                        rewind_params = vo.OracleRollbackParameters()
                    else:
                        rewind_params = vo.RollbackParameters()
                    rewind_params.timeflow_point_parameters = dx_timeflow_obj.set_timeflow_point(  # noqa
                        container_obj,
                        timestamp_type=self.time_stamp_type,
                        timestamp=self.time_stamp,
                        engine_session_ref=dlpx_obj.server_session,
                    )
                    try:
                        # Rewind the VDB
                        database.rollback(
                            dlpx_obj.server_session,
                            container_obj.reference,
                            rewind_params,
                        )
                    except (
                        exceptions.RequestError,
                        exceptions.HttpError,
                        exceptions.JobError,
                    ) as err:
                        raise dlpx_exceptions.DlpxException(
                            f"ERROR: {engine['hostname']} encountered "
                            f"an error on {container_obj.name} "
                            f"during the rewind process:\n{str(err)}",
                            func_ref,
                        )
                    self._add_last_job_to_track(dlpx_obj)
                # Don't do anything if the database is disabled
                else:
                    dx_logging.print_info(
                        f"{engine['hostname']}: {container_obj.name} is not "
                        f"enabled. Skipping sync."
                    )
                run_job.track_running_jobs(
                    engine, dlpx_obj, poll=self.poll, failures=self.failures
                )
        except (
            dlpx_exceptions.DlpxException,
            BaseException,
            Exception,
        ) as err:
            dx_logging.print_exception(err, func_ref)
            self.failures[0] = True
